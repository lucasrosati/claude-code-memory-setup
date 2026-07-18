# Scripts

Helper scripts for the Claude Code + Obsidian + Graphify setup.

## Files

| File | Purpose |
|------|---------|
| `claude_to_obsidian.py` | Process exported Claude chats and import them into your Obsidian vault with frontmatter, auto-tags, and wikilinks |
| `sync_claude_obsidian.sh` | Automation wrapper: exports Claude Code chats and runs the processor |

## Setup

1. **Copy both files to `~/scripts/`:**

   ```bash
   mkdir -p ~/scripts
   cp claude_to_obsidian.py ~/scripts/
   cp sync_claude_obsidian.sh ~/scripts/
   chmod +x ~/scripts/sync_claude_obsidian.sh
   ```

2. **Install the Claude Code extractor:**

   ```bash
   pipx install claude-conversation-extractor
   ```

When you have any errors, follow official instalation guide <https://github.com/ZeroSumQuant/claude-conversation-extractor/blob/main/docs/user/INSTALL.md>

3. **Edit `sync_claude_obsidian.sh`:**

   Open the file and change `VAULT_DIR` to point to your Obsidian vault:

   ```bash
   VAULT_DIR="$HOME/YourVaultName"
   ```

4. **Customize tags (optional):**

   Open `claude_to_obsidian.py` and edit the `KEYWORD_TAG_MAP` dictionary at the top. Add keywords specific to your stack and projects:

   ```python
   KEYWORD_TAG_MAP = {
       "my-project": "my-project",
       "client-name": "client-work",
       # ... your keywords
   }
   ```

5. **Test manually:**

   ```bash
   ~/scripts/sync_claude_obsidian.sh
   ```

   Check the log:
   ```bash
   tail -f ~/scripts/claude_obsidian_sync.log
   ```

6. **Schedule via cron (daily at 10pm):**

   ```bash
   (crontab -l 2>/dev/null; echo "0 22 * * * $HOME/scripts/sync_claude_obsidian.sh") | crontab -
   ```

7. **For Claude Web chats:**

Install the **"Export Claude Chat to Markdown"** browser extension for Chrome/Edge. Do periodic bulk exports, save the `.md` files to `~/claude-exports/web/`, and the cron job handles the rest.

## How it works

1. `sync_claude_obsidian.sh` runs `claude-extract` to export all Claude Code conversations as `.md` files into `~/claude-exports/code/`
2. `claude_to_obsidian.py` processes each `.md`:
   - Detects origin (Code vs Web)
   - Generates auto-tags via keyword matching
   - Adds standardized YAML frontmatter
   - Inserts `[[wikilinks]]` for notes that already exist in your vault
4. Files are moved (with `--move` flag) into `<vault>/chats/code/` or `<vault>/chats/web/`

## CLI options

```bash
python3 claude_to_obsidian.py \
    --export-dir ~/claude-exports \
    --vault-dir ~/ObsidianVault \
    --move
```

| Flag | Description |
|------|-------------|
| `--export-dir` | Directory containing exported `.md` files (required) |
| `--vault-dir` | Path to your Obsidian vault (required) |
| `--dry-run` | Preview what would happen without modifying anything |
| `--move` | Delete originals after copying (default: copy only) |
| `--origin` | Force origin: `code`, `web`, or `auto` (default: `auto`) |
| `--no-wikilinks` | Disable wikilink insertion |

## Filter in Obsidian Graph View

After import, use these filters:

- `tag:chat-import` → only imported chats
- `path:chats` → all chats by folder
- `-path:chats` → hide all chats
- `tag:python tag:chat-import` → Python-related chats only

## Troubleshooting

**`claude-extract` not found:**
Install with `pip install claude-conversation-extractor`. If still not found, check that pip's bin directory is in your `$PATH`.

**Cron job doesn't run on macOS:**
Grant Full Disk Access to `cron` in System Preferences → Privacy & Security → Full Disk Access.

**No tags being generated:**
Check that `KEYWORD_TAG_MAP` in `claude_to_obsidian.py` contains keywords actually present in your chats. Run with `--dry-run` to debug.

**Wikilinks not inserted:**
The script only inserts wikilinks for notes that already exist in your vault. Make sure your `--vault-dir` points to a vault with notes (not an empty folder).
