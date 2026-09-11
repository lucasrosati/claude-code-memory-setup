#!/usr/bin/env python3
"""Validate every ```json fenced block in the given markdown files.

The guide ships copy-pasteable config (e.g. ~/.claude/settings.json hooks).
A block that does not parse is a real bug for whoever copies it.

Blocks that are intentionally partial are skipped: anything containing an
ellipsis ("..." / "…") or a comment line ("//", "/*", "#").

Usage:  python .github/scripts/check_json_blocks.py FILE.md [FILE.md ...]
Exit code 1 if any block fails to parse.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

OPEN_RE = re.compile(r"^\s*(```|~~~)\s*json\b", re.IGNORECASE)
CLOSE_RE = re.compile(r"^\s*(```|~~~)\s*$")
COMMENT_RE = re.compile(r"^\s*(//|/\*|#)")


def partial(block: str) -> bool:
    if "..." in block or "…" in block:
        return True
    return any(COMMENT_RE.match(line) for line in block.splitlines())


def blocks_in(path: Path):
    """Yield (start_line, text) for each ```json block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        if OPEN_RE.match(lines[i]):
            start = i + 1
            body: list[str] = []
            i += 1
            while i < len(lines) and not CLOSE_RE.match(lines[i]):
                body.append(lines[i])
                i += 1
            yield start, "\n".join(body)
        i += 1


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv[1:]] or [Path("README.md")]
    checked = skipped = failed = 0
    for path in files:
        if not path.is_file():
            print(f"::warning::{path} not found, skipping")
            continue
        for line, text in blocks_in(path):
            if partial(text):
                skipped += 1
                print(f"skip  {path}:{line} (partial snippet)")
                continue
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                failed += 1
                print(
                    f"::error file={path},line={line + e.lineno - 1}::"
                    f"invalid JSON block starting at {path}:{line}: {e.msg} "
                    f"(line {e.lineno}, col {e.colno} of the block)"
                )
            else:
                checked += 1
                print(f"ok    {path}:{line}")
    print(f"\n{checked} valid, {skipped} skipped (partial), {failed} invalid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
