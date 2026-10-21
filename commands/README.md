# Session commands

Ready-to-install slash commands for the vault workflow described in the [main guide](../README.md).

| Command | What it does |
|---------|--------------|
| [`/save`](./save.md) | Writes the session log and consolidates durable decisions, insights and conventions into memory. |
| [`/memorize`](./memorize.md) | Explicit mid-session trigger: pins one item (or runs the consolidation) right now, without a session log. |
| [`/commit`](./commit.md) | Commits and pushes the changes, then runs `/save`. |
| [`/resume`](./resume.md) | Loads the project memory, recent decisions and the last session logs. |

## Install

```bash
cp commands/*.md ~/.claude/commands/
rm ~/.claude/commands/README.md
```

Restart Claude Code so the commands are registered. `/memorize` and `/commit` read `~/.claude/commands/save.md` at run time, so keep that file name (or update the reference if you rename it).

## Vault location

The commands use `$VAULT_DIR`, defaulting to `~/vault`. The project is the basename of the git top-level folder (or of the current directory outside git). Logs go to `<vault>/<project>/logs/` when `<vault>/<project>/` exists, otherwise to `<vault>/logs/`, the same routing as the auto-save hook.

## How Phase 2 of /save works

1. **Criteria:** only decisions with a rationale, reusable insights, project conventions, durable project facts and corrections to existing memory qualify; progress and unfinished investigations don't.
2. **Deduplication:** each candidate is grepped in `permanent/`, the project folder and the project `CLAUDE.md`; an existing note is updated, never duplicated.
3. **Destinations:** decisions → `architecture/decisions.md`, insights → `<vault>/permanent/` plus a pointer in `## Permanent facts` of `<vault>/<project>/CLAUDE.md`, facts → the matching `data/`, `architecture/`, `features/` or `pipeline/` note, or a line in `## Permanent facts`.
4. **Confirmation:** only a new project convention asks first (y/n), at the end, because it changes the agent's behavior.
5. **Report:** `Session log: <path>` followed by `Memory:` with `created:`/`updated:` lines, or `Memory: nothing to consolidate this session`.

## Auto-save hook

[`scripts/session_autosave.py`](../scripts/session_autosave.py) is mechanical: it writes a minimal log from the transcript and never runs Phase 2. Use `/save` when you want memory consolidated.
