#!/usr/bin/env python3
"""
session_autosave.py — SessionEnd hook for Claude Code.

Automatically writes a minimal session log to your Obsidian vault when a
Claude Code session ends (exit, /clear, logout). Zero LLM calls: everything
is extracted mechanically from the session transcript.

This is a safety net, not a replacement for /save. The manual /save command
produces rich logs (decisions, pending items, wikilinks). This hook
guarantees that even forgotten sessions leave a trace.

Install:
    1. Copy to ~/scripts/session_autosave.py
    2. Add the hook to ~/.claude/settings.json (see README)
    3. Set VAULT_DIR env var or edit DEFAULT_VAULT below

The hook receives JSON on stdin from Claude Code:
    { "session_id": "...", "transcript_path": "...", "cwd": "...",
      "hook_event_name": "SessionEnd", "reason": "exit|clear|logout|..." }
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_VAULT = Path(os.environ.get("VAULT_DIR", str(Path.home() / "ObsidianVault")))

# Skip sessions with fewer user messages than this (avoids noise from
# trivial "open and close" sessions)
MIN_USER_MESSAGES = 2

# Max items to include in each section
MAX_FILES = 20
MAX_COMMANDS = 10
FIRST_PROMPT_MAX_CHARS = 300

LOG_FILE = Path.home() / "scripts" / "autosave.log"

# ============================================================================


def log(msg: str) -> None:
    """Append to the debug log. Never raise."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass


def parse_transcript(transcript_path: Path) -> dict:
    """Extract session facts from the JSONL transcript. Defensive parsing:
    format may vary between Claude Code versions, so every access is guarded."""
    first_prompt = None
    user_messages = 0
    files_touched: list[str] = []
    commands: list[str] = []
    first_ts = None
    last_ts = None

    seen_files: set[str] = set()

    with transcript_path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = entry.get("timestamp")
            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            msg = entry.get("message") or {}
            role = msg.get("role") or entry.get("type")
            content = msg.get("content")

            # User messages
            if role == "user" and content:
                # content can be a string or a list of blocks
                text = None
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text")
                            break
                # Skip tool results masquerading as user turns
                if text and not text.startswith("<"):
                    user_messages += 1
                    if first_prompt is None:
                        first_prompt = text.strip()

            # Assistant tool calls
            if role == "assistant" and isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    tool = block.get("name", "")
                    tool_input = block.get("input") or {}

                    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit",
                                "str_replace", "create_file", "str_replace_editor"):
                        fp = tool_input.get("file_path") or tool_input.get("path")
                        if fp and fp not in seen_files:
                            seen_files.add(fp)
                            files_touched.append(fp)

                    elif tool in ("Bash", "bash", "bash_tool"):
                        cmd = tool_input.get("command")
                        if cmd:
                            # Keep only the first line of multi-line commands
                            commands.append(cmd.split("\n")[0][:120])

    return {
        "first_prompt": first_prompt,
        "user_messages": user_messages,
        "files_touched": files_touched,
        "commands": commands,
        "first_ts": first_ts,
        "last_ts": last_ts,
    }


def fmt_time(iso_ts) -> str:
    if not iso_ts:
        return "?"
    try:
        return datetime.fromisoformat(iso_ts.replace("Z", "+00:00")).astimezone().strftime("%H:%M")
    except Exception:
        return "?"


def resolve_logs_dir(vault: Path, project: str) -> Path:
    """Prefer <vault>/<project>/logs/ if the project folder exists in the
    vault; fall back to <vault>/logs/."""
    project_dir = vault / project
    if project_dir.is_dir():
        return project_dir / "logs"
    return vault / "logs"


def build_note(project: str, facts: dict, session_id: str, reason: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    now_hm = datetime.now().strftime("%H:%M")

    prompt = (facts["first_prompt"] or "(no prompt captured)")
    if len(prompt) > FIRST_PROMPT_MAX_CHARS:
        prompt = prompt[:FIRST_PROMPT_MAX_CHARS] + "..."
    prompt = prompt.replace("\n", " ")

    files_section = "\n".join(
        f"- `{fp}`" for fp in facts["files_touched"][:MAX_FILES]
    ) or "- (no file edits)"
    if len(facts["files_touched"]) > MAX_FILES:
        files_section += f"\n- ... and {len(facts['files_touched']) - MAX_FILES} more"

    commands_section = "\n".join(
        f"- `{c}`" for c in facts["commands"][:MAX_COMMANDS]
    ) or "- (no commands)"

    return f"""---
title: "Auto session log — {project} — {today} {now_hm}"
tags:
  - session-log
  - auto-log
  - {project}
created: {today}
updated: {today}
status: imported
type: log
session_id: {session_id}
end_reason: {reason}
---

# Auto session log — {project}

## Objective (first prompt)
> {prompt}

## Files touched
{files_section}

## Commands executed (sample)
{commands_section}

## Stats
- User turns: {facts["user_messages"]}
- Files edited: {len(facts["files_touched"])}
- Start: {fmt_time(facts["first_ts"])} / End: {fmt_time(facts["last_ts"])}

_Generated automatically by the SessionEnd hook. For a rich log with
decisions and pending items, run /save before closing the session._
"""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        log(f"ERROR: could not parse stdin: {e}")
        return

    transcript_path = payload.get("transcript_path")
    cwd = payload.get("cwd") or os.getcwd()
    session_id = payload.get("session_id", "unknown")
    reason = payload.get("reason", "unknown")

    if not transcript_path or not Path(transcript_path).exists():
        log(f"SKIP: transcript not found ({transcript_path})")
        return

    try:
        facts = parse_transcript(Path(transcript_path))
    except Exception as e:
        log(f"ERROR: transcript parse failed: {e}")
        return

    if facts["user_messages"] < MIN_USER_MESSAGES:
        log(f"SKIP: trivial session ({facts['user_messages']} user messages) in {cwd}")
        return

    vault = DEFAULT_VAULT
    if not vault.is_dir():
        log(f"SKIP: vault not found at {vault}")
        return

    project = Path(cwd).name
    logs_dir = resolve_logs_dir(vault, project)

    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        dest = logs_dir / f"{stamp}-auto-session.md"
        # Avoid clobbering if two sessions end in the same minute
        counter = 1
        while dest.exists():
            dest = logs_dir / f"{stamp}-auto-session-{counter}.md"
            counter += 1
        dest.write_text(build_note(project, facts, session_id, reason), encoding="utf-8")
        log(f"OK: wrote {dest}")
    except Exception as e:
        log(f"ERROR: could not write log: {e}")


if __name__ == "__main__":
    main()
