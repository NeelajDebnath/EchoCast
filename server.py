"""
EchoCast 2 — Flask Web Server
Serves the landing page and exposes a REST API for the podcast pipeline.
Runs the pipeline in a background thread and streams status via SSE.
"""

from __future__ import annotations

import json
import queue
import sys
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

from echocast.config import OUTPUT_DIR

# ── Patch stdout to capture agent logs ────────────────────────────────────────
_status_queues: dict[str, queue.Queue] = {}


class _TeeWriter:
    """Writes to real stdout AND pushes lines to any active status queues."""

    def __init__(self, original):
        self.original = original

    def write(self, text: str):
        self.original.write(text)
        if text.strip():
            for q in list(_status_queues.values()):
                try:
                    q.put_nowait(text.strip())
                except queue.Full:
                    pass

    def flush(self):
        self.original.flush()


sys.stdout = _TeeWriter(sys.stdout)

# ── Flask app ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="frontend", static_url_path="")
_JOBS: dict[str, dict] = {}  # job_id -> {status, result, error}


@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    """Start a podcast generation job. Returns a job_id immediately."""
    data = request.get_json(force=True)
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Topic is required."}), 400

    job_id = str(uuid.uuid4())[:8]
    _JOBS[job_id] = {"status": "running", "result": None, "error": None}
    _status_queues[job_id] = queue.Queue(maxsize=500)

    def _run():
        try:
            from echocast.orchestrator import run
            output_path = run(topic)
            _JOBS[job_id]["status"] = "done"
            _JOBS[job_id]["result"] = output_path.name
        except Exception as e:
            _JOBS[job_id]["status"] = "error"
            _JOBS[job_id]["error"] = str(e)
        finally:
            # Send a final sentinel
            q = _status_queues.get(job_id)
            if q:
                q.put("__DONE__")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return jsonify({"job_id": job_id}), 202


@app.route("/api/status/<job_id>")
def status_stream(job_id: str):
    """SSE endpoint — streams real-time log lines to the client."""
    if job_id not in _JOBS:
        return jsonify({"error": "Unknown job."}), 404

    def event_stream():
        q = _status_queues.get(job_id)
        if not q:
            return
        while True:
            try:
                line = q.get(timeout=120)
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
                continue

            if line == "__DONE__":
                job = _JOBS[job_id]
                yield f"data: {json.dumps({'type': 'complete', 'status': job['status'], 'result': job.get('result'), 'error': job.get('error')})}\n\n"
                break
            else:
                yield f"data: {json.dumps({'type': 'log', 'message': line})}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/api/audio/<filename>")
def serve_audio(filename: str):
    """Serve the generated podcast MP3."""
    return send_from_directory(str(OUTPUT_DIR), filename)


if __name__ == "__main__":
    print("🚀  EchoCast 2 — Server starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
