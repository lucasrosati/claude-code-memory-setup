#!/usr/bin/env python3
"""Structural parity check between README.md and README.pt-BR.md.

Compares *structure only* (never translated text):

  - level-2 headings ("## ") outside fenced code blocks -> count must match (error)
  - fenced code blocks (``` / ~~~)                       -> warn if they differ by > 2

Headings that appear inside fenced code blocks (the READMEs embed example
markdown notes) are ignored, otherwise an edit to an example would look like a
missing section.

Usage:  python .github/scripts/check_parity.py [EN_FILE PT_FILE]
Exit code 1 on error, 0 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FENCE_RE = re.compile(r"^\s*(```|~~~)")
H2_RE = re.compile(r"^## +(.*\S)\s*$")
WARN_BLOCK_DELTA = 2


def scan(path: Path) -> tuple[list[str], int]:
    """Return (h2 headings outside code fences, number of fenced code blocks)."""
    headings: list[str] = []
    blocks = 0
    in_fence = False
    fence_marker = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if not in_fence:
                in_fence, fence_marker = True, marker
                blocks += 1
            elif marker == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue
        h = H2_RE.match(line)
        if h:
            headings.append(h.group(1))
    return headings, blocks


def main(argv: list[str]) -> int:
    en = Path(argv[1]) if len(argv) > 2 else Path("README.md")
    pt = Path(argv[2]) if len(argv) > 2 else Path("README.pt-BR.md")
    for p in (en, pt):
        if not p.is_file():
            print(f"::error::{p} not found")
            return 1

    en_heads, en_blocks = scan(en)
    pt_heads, pt_blocks = scan(pt)

    print(f"{en}: {len(en_heads)} sections, {en_blocks} code blocks")
    print(f"{pt}: {len(pt_heads)} sections, {pt_blocks} code blocks")

    status = 0

    if len(en_heads) != len(pt_heads):
        status = 1
        if len(en_heads) > len(pt_heads):
            missing_in = pt.name
        else:
            missing_in = en.name
        msg = (
            f"{en.name} has {len(en_heads)} sections, {pt.name} has {len(pt_heads)}. "
            f"{missing_in} is missing {abs(len(en_heads) - len(pt_heads))} section(s)."
        )
        print(f"::error::{msg}")
        print()
        print("Sections are compared by position (titles are translated, so they differ):")
        width = max(len(h) for h in en_heads + pt_heads) if en_heads + pt_heads else 10
        for i in range(max(len(en_heads), len(pt_heads))):
            left = en_heads[i] if i < len(en_heads) else "<missing>"
            right = pt_heads[i] if i < len(pt_heads) else "<missing>"
            mark = " " if i < len(en_heads) and i < len(pt_heads) else "!"
            print(f"  {mark} {i + 1:2d}. {left:<{width}}  |  {right}")
        print()
        print(f"Sections in {en.name}: {en_heads}")
        print(f"Sections in {pt.name}: {pt_heads}")
    else:
        print("OK: section count matches")

    delta = abs(en_blocks - pt_blocks)
    if delta > WARN_BLOCK_DELTA:
        print(
            f"::warning::Code block count differs by {delta} "
            f"({en.name}: {en_blocks}, {pt.name}: {pt_blocks}). "
            "A code example may have been added to only one README."
        )
    else:
        print(f"OK: code block counts within tolerance (delta {delta})")

    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
