# /save — Save the Session and Consolidate Memory

Saves the session to the vault and automatically consolidates durable decisions, insights and conventions. Use it when you finish or pause work.

Run both phases in order. Phase 2 only writes when there is durable knowledge. When in doubt, don't write: the session log already preserves the context, and the user can pin something later with /memorize.

## Vault detection (same rule as /resume)
Run this block (one Bash call) and use the printed `vault=` as `<vault>`, `project=` as `<project>`, `project_dir=` as `<vault>/<project>` and `logs=` as the log folder:
```bash
setopt nullglob 2>/dev/null  # zsh aborts on unmatched globs; no-op in bash
vault=${VAULT_DIR:-$HOME/vault}
root=$(git rev-parse --show-toplevel 2>/dev/null); root=${root:-$PWD}
project=$(basename "$root")
if [ -d "$vault/$project" ]; then pdir="$vault/$project"; logs="$pdir/logs"; else pdir=""; logs="$vault/logs"; fi
echo "vault=$vault project=$project project_dir=${pdir:-NONE} logs=$logs"
```
- The vault is `$VAULT_DIR` (default `~/vault`). The project is the basename of the git top-level folder, or of the current directory outside git.
- `project_dir=NONE`: logs go to `<vault>/logs/` and decisions stay in the log only. Don't create a project folder in the vault.

## Phase 1: Session log (always)

1. Read `<vault>/CLAUDE.md` before writing. Review the whole conversation of this session.
2. Create `<logs>/YYYY-MM-DD-short-description.md` (kebab-case, no accents). Never overwrite an existing log: if the name already exists, add `HHMM` after the date. Frontmatter:
```yaml
---
title: "Descriptive session title"
tags: [session-log, <project>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: completed
type: log
---
```
3. Sections:
   - `## What was done`
   - `## Decisions made` (if none, "No new decisions.")
   - `## Pending`
   - `## State for resume`: task (or `none`), branch, pending acceptance criteria, tests run and result, blockers, exact next action
   - `## Files modified` (`path` — what changed)
   - `## Notes created or updated` (filled at the end of Phase 2)
4. Follow the rules in `<vault>/CLAUDE.md`: at least 2 wikilinks, complete frontmatter.
5. Never include the raw log of the whole conversation. If an existing vault note became outdated and is not handled in Phase 2, tell the user.

## Phase 2: Memory consolidation (conditional)

### 2.1 Identify candidates

Review the whole session. A candidate must meet at least one criterion:

- Technical or architectural decision with a rationale (alternatives were considered)
- Insight reusable outside this project: pattern, pitfall, non-obvious bug root cause, discovered behavior of a tool or library
- Project convention created or changed (naming, structure, workflow, code rule)
- Durable project fact: schema, structure, pipeline, path, known bug with an identified cause
- Correction of something already memorized that turned out wrong or outdated

Not candidates:
- Progress, completed tasks, pending items (already in the log)
- Investigations without a conclusion
- Implementation details that don't generalize
- Items already memorized with no change

If there are no candidates, skip to 2.5.

### 2.2 Check for duplicates

For each candidate, before writing:
- `grep -ril "<key-term>" <vault>/permanent/`
- `grep -i "<key-term>" <vault>/<project>/architecture/decisions.md`
- `grep -ril "<key-term>" <vault>/<project>/CLAUDE.md <vault>/<project>/data <vault>/<project>/architecture <vault>/<project>/features <vault>/<project>/pipeline 2>/dev/null`
- `grep -i "<key-term>" ./CLAUDE.md`

If an equivalent note exists: update it (the `updated` field and the content). Never create a duplicate.
If it exists but the session contradicts it: update it and record the change in the note body ("Updated on YYYY-MM-DD: ...").

### 2.3 Write by destination

- **Project decision:** append to the end of `<vault>/<project>/architecture/decisions.md` an entry `## YYYY-MM-DD — short title` with the fields Context, Alternatives, Decision and Rationale as bullets (/resume reads the file by its last `## ` headings). Create the file with frontmatter (`type: decision`) if it doesn't exist. Without a project folder: the decision stays in the log only.
- **Reusable insight:** create `<vault>/permanent/<kebab-case>.md` with complete frontmatter (title, tags, created, updated, status: permanent, type: concept), 1 concept per note, at least 2 wikilinks to existing notes (list `permanent/` first to link real names). Then append to `## Permanent facts` (see below) a line `- [[note-name]]: one-line summary`. Only the pointer, never the content; when updating a note that already has a pointer, don't duplicate the line.
- **Durable project fact:** if a matching note exists under `<vault>/<project>/` (schema → `data/`, component or structure → `architecture/`, feature → `features/`, pipeline → `pipeline/`), update that note (content and `updated` field). If not, append a line `- fact in one line` to `## Permanent facts`. Never write a secret, only the config name.
- **Project convention:** PROPOSE the line to add to the "## Conventions" section of the project's `CLAUDE.md` and ask for confirmation (y/n) before writing. It is the only destination that needs confirmation, because it changes the agent's behavior in the project. Ask only after finishing the other writes and the report, and record the proposal under `## Pending` in the log so it isn't lost if no answer comes.

`## Permanent facts` lives in `<vault>/<project>/CLAUDE.md`, the file /resume reads as the project's memory. Create the section at the end of the file if it doesn't exist; if the file doesn't exist, create it with frontmatter (title, tags, created, updated) and the section. The file and the section are only created at the moment a line is written to them; a /save that ends in "nothing to consolidate" neither creates nor changes `<vault>/<project>/CLAUDE.md`. With `project_dir=NONE` there is no pointer: the fact stays in the log and the note in `permanent/` is enough.

Auto-archive: if `<vault>/<project>/CLAUDE.md` grows past 300 lines, move the oldest sections to `<vault>/<project>/architecture/claude-archive.md`, keep the essentials in CLAUDE.md (stack, rules, active conventions, pointers) and add "Full history in [[claude-archive]]".

### 2.4 Link

Add [[wikilinks]] to every note created or updated in the "Notes created or updated" section of the Phase 1 session log.

### 2.5 Report

Always finish with:

```
Session log: <path>
Memory:
- created: <path> (reason in one line)
- updated: <path> (reason in one line)
```
or
```
Session log: <path>
Memory: nothing to consolidate this session
```
