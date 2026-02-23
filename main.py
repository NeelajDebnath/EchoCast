"""
EchoCast 2 — CLI Entry-point
Usage:
    python main.py "Your podcast topic here"
"""

import sys
from echocast.orchestrator import run


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:  python main.py \"Your podcast topic\"")
        print("Example:  python main.py \"The future of solid-state batteries\"")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    try:
        output_path = run(topic)
        print(f"\n✅  Done! Your podcast is at: {output_path}")
    except Exception as e:
        print(f"\n❌  Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
