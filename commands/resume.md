# /resume — Load Context from the Previous Session

When you receive this command, do the following:

## Vault detection (by project, never by a fixed path)
1. Run this block (one Bash call) and use the printed `vault=` as `<vault>`, `project=` as `<project>`, `project_dir=` as `<vault>/<project>` and `logs=` as the log folder for the rest of the command:
   ```bash
   setopt nullglob 2>/dev/null  # zsh aborts on unmatched globs; no-op in bash
   vault=${VAULT_DIR:-$HOME/vault}
   root=$(git rev-parse --show-toplevel 2>/dev/null); root=${root:-$PWD}
   project=$(basename "$root")
   if [ -d "$vault/$project" ]; then pdir="$vault/$project"; logs="$pdir/logs"; else pdir=""; logs="$vault/logs"; fi
   echo "vault=$vault project=$project project_dir=${pdir:-NONE} logs=$logs"
   ```
   - The vault is `$VAULT_DIR` (default `~/vault`). The project is the basename of the git top-level folder, or of the current directory outside git.
   - `project_dir=NONE`: say so, suggest creating `<vault>/<project>/` (Part 1 of the guide), and load only the logs from `<vault>/logs/`. Don't create a vault folder.
2. Also read the general rules in `<vault>/CLAUDE.md` and, if it exists, `<vault>/<project>/_moc.md`.

## Load context
1. Read `<vault>/<project>/CLAUDE.md` if it exists (the project's permanent memory, including `## Permanent facts`).
2. Split the logs in `<logs>`, newest first, into **rich** (written by `/save`) and **automatic** (stub from the SessionEnd hook, with `auto-log` in the tags):
   ```bash
   cd "<logs>" && for f in $(ls -t); do grep -qx '  - auto-log' "$f" && echo "auto $f" || echo "rich $f"; done | head -20
   ```
3. Read the last 3 **rich** logs (or the requested number). From the automatic logs newer than the last rich one, read only the frontmatter and `## Stats`: they go in one line ("since then: N short sessions, no rich log").
4. Read the most recent entries of `<vault>/<project>/architecture/decisions.md` (the file can have thousands of lines: read from the end, starting at the last `## ` headings, not the whole file).
5. A pending item in a log is a snapshot of the past. A deadline quoted in memory ("by 10/10") counts as pending only if the date hasn't passed.

## Variants
- `/resume` → loads the last 3 session logs
- `/resume 5` → loads the last 5 session logs
- `/resume batch` → loads the last 3 logs + searches "batch" across all logs
- `/resume 5 auth` → loads the last 5 + searches "auth"

## Output
Present a compact summary:
- **Vault:** the resolved path (and the project)
- **Last session:** date + what was done
- **Recent decisions:** last 3 decisions from architecture/decisions.md
- **Pending tasks:** the `- [ ]` items from recent logs, already checked in step 5
- **State for resume:** the "State for resume" section of the latest rich log
- **Active context:** which part of the project was being worked on

End with: "Context loaded. What are we working on today?"
