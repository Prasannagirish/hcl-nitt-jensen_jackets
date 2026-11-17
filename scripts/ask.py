"""Ask one question from the command line and print the cited answer.

Usage: uv run python scripts/ask.py "your question" [--per-paper]
"""

import json
import sys

from app.answer import answer, default_snapshot


def main() -> None:
    """Run answer() on the question and print the result as JSON."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    result = answer(" ".join(args), default_snapshot(), per_paper="--per-paper" in sys.argv)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
