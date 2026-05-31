# Claude Code + Obsidian + Graphify: The Definitive Guide to Token Savings & Persistent Memory

> **71.5x fewer tokens per session** with Graphify + **permanent memory across sessions** with Obsidian Zettelkasten.

A complete setup to turn Claude Code into an agent with long-term memory and full codebase awareness — without wasting tokens re-reading files.

🇧🇷 [Leia em Português](./README.pt-BR.md)

---

## Table of Contents

1. [The Problem](#the-problem)
2. [The Solution (Overview)](#the-solution-overview)
3. [Part 1 — Obsidian as Persistent Memory](#part-1--obsidian-as-persistent-memory)
4. [Part 2 — Chat Import Pipeline](#part-2--chat-import-pipeline)
5. [Part 3 — Graphify (Codebase Knowledge Graph)](#part-3--graphify-codebase-knowledge-graph)
6. [Part 4 — Complete Workflow](#part-4--complete-workflow)
7. [Real Results](#real-results)
8. [Troubleshooting](#troubleshooting)

---

## The Problem

When working with Claude Code, two problems silently eat your tokens:

**Problem 1 — Amnesia between sessions.** Every time you open a new session, you have to re-explain your project: stack, past decisions, current bugs, what's left to do. Claude Code remembers nothing from the previous session.

**Problem 2 — Codebase re-reading.** Claude Code re-reads all your project files every session to understand the structure. A project with ~40 files burns ~20,000 tokens just for Claude to orient itself — before you even ask a question. If you run 10 sessions a day, that's **200,000 wasted tokens**.

---

## The Solution (Overview)

Two complementary systems, each solving a different problem:

| Layer | Tool | Problem Solved | Cost |
|-------|------|---------------|------|
| Project memory | Obsidian Zettelkasten | Amnesia between sessions | Free |
| Code map | Graphify | Codebase re-reading | Free (AST mode) |
| Conversation history | Import pipeline | Lost chat insights | Free |
| Continuity | `/resume` and `/save` commands | Picking up where you left off | Free |

Obsidian handles **what was decided** (declarative memory). Graphify handles **how the code is structured** (structural map). Together, Claude Code starts every session knowing everything — without re-reading anything.

---

## Part 1 — Obsidian as Persistent Memory

### Concept

A single, centralized Obsidian vault acts as Claude Code's "second brain." It stores decisions, context, progress, and knowledge for all your projects. Notes follow the Zettelkasten method: atomic (one idea per note), densely interlinked, with standardized metadata.

Claude Code accesses the vault through `CLAUDE.md` and custom skills.

### Recommended Structure

```
~/vault/                              # SINGLE vault for all projects
├── CLAUDE.md                         # global instructions for Claude Code
├── permanent/                        # consolidated atomic notes
├── inbox/                            # raw capture (ideas, drafts)
├── fleeting/                         # quick temporary notes
├── templates/                        # note templates
├── logs/                             # global session logs
├── references/                       # reference material
├── my-project/                       # MOCs and notes for project X
│   ├── architecture/                 #   architecture, decisions, conventions
│   ├── pipeline/                     #   data flows, APIs
│   ├── data/                         #   schema, data model
│   ├── features/                     #   planned/implemented features
│   └── logs/                         #   project session logs
├── another-project/                  # MOCs and notes for project Y
│   └── ...
├── chats/                            # imported Claude chats
│   ├── code/                         #   from Claude Code
│   └── web/                          #   from Claude Web/App
└── graphify/                         # codebase knowledge graphs
    ├── my-project/                   #   graph notes for project X
    └── another-project/              #   graph notes for project Y
```

> **Why a single vault?** Having one vault per project fragments knowledge. With a single vault, a note about "Supabase Auth" links to both project A and B. The graph view reveals cross-project connections you didn't expect.

### Step-by-Step Setup

**Prerequisites:**
- Claude Code installed and authenticated
- Obsidian installed (free: [obsidian.md](https://obsidian.md))

**1. Create the vault:**

Obsidian → "Create new vault" → choose a name and location.

**2. Create the folder structure:**

```bash
cd ~/vault  # adjust to your path
mkdir -p permanent inbox fleeting templates logs references
mkdir -p my-project/{architecture,pipeline,data,features,logs}
```

**3. Create the CLAUDE.md:**

This is the file Claude Code reads automatically. Create `CLAUDE.md` at the vault root:

```markdown
# Vault — Instructions for Claude Code

## What is this vault
Centralized knowledge base for all projects.
Persistent memory across sessions.

## Project stacks
- Project X: React + Supabase
- Project Y: Python + FastAPI
(adapt to your projects)

## Zettelkasten Rules

### Note creation
- Use wikilinks: [[note-name]] (not markdown links)
- Mandatory YAML frontmatter on every note
- Filenames in kebab-case: `auth-flow.md`, not `Auth Flow.md`
- 1 concept per permanent note (atomicity)
- Minimum 2 wikilinks per note (dense linking)

### Standard frontmatter
---
title: Note Name
tags: [project, topic]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
type: permanent
---

### Never do
- Don't delete notes without asking
- Don't use markdown links for internal notes (use wikilinks)
- Don't create notes without frontmatter
- Don't change folder structure without documenting it

## Session Commands

### /resume
When you receive this command:
1. Read the 3 most recent session logs in logs/
2. Read architecture/decisions.md for the current project
3. Summarize current state and what's left to do

### /save
When you receive this command:
1. Create a session log in logs/YYYY-MM-DD-description.md
2. Record: what was done, decisions made, pending items
3. Add wikilinks to created/modified notes
4. Run git commit + push if in a repository
```

**4. Create a note template:**

```bash
cat > templates/default-note.md << 'EOF'
---
title: {{title}}
tags: []
created: {{date}}
updated: {{date}}
status: draft
type: permanent
---

# {{title}}

## Context

## Details

## Related links
EOF
```

**5. Recommended Obsidian plugins:**

| Plugin | Purpose | Install method |
|--------|---------|----------------|
| BRAT | Install beta plugins | Community Plugins → Browse |
| 3D Graph | 3D vault visualization | Via BRAT (v2.4.1) |
| Folders to Graph | Folders as graph nodes | Community Plugins → Browse |
| Calendar | Daily note navigation | Community Plugins → Browse |

---

## Part 2 — Chat Import Pipeline

### Concept

Your Claude chats (both Code and Web) contain valuable decisions, insights, and context that get lost in the history. This pipeline exports, processes, and imports those conversations as vault notes — with frontmatter, automatic tags, and wikilinks to existing notes.

### Components

```
~/scripts/
├── claude_to_obsidian.py          # processor (frontmatter, tags, wikilinks)
└── sync_claude_obsidian.sh        # automation (export + process)

~/claude-exports/                   # temporary staging area (outside vault)
├── code/                           # Claude Code exports
└── web/                            # Claude Web exports
```

### Setup

**1. Install the Claude Code extractor:**

```bash
pip install claude-conversation-extractor
```

**2. Create staging directories:**

```bash
mkdir -p ~/claude-exports/code ~/claude-exports/web
```

**3. Create the post-processing script (`~/scripts/claude_to_obsidian.py`):**

The script should:
- Read each exported `.md` file
- Detect origin (Code vs Web)
- Generate automatic tags based on content keywords
- Add standardized YAML frontmatter
- Insert `[[wikilinks]]` for notes that already exist in the vault
- Copy to `chats/code/` or `chats/web/` inside the vault

Example keyword-to-tag mapping:

```python
KEYWORD_TAG_MAP = {
    "python": "python",
    "react": "react",
    "supabase": "supabase",
    "deploy": "deploy",
    "bug": "debugging",
    "refactor": "refactoring",
    # add your own
}
```

**4. Create the automation script (`~/scripts/sync_claude_obsidian.sh`):**

```bash
#!/bin/bash
EXPORT_DIR="$HOME/claude-exports"
VAULT_DIR="$HOME/vault"  # adjust to your path
SCRIPT_DIR="$HOME/scripts"
LOG="$SCRIPT_DIR/sync.log"

echo "[$(date)] Sync started" >> "$LOG"

# Export Claude Code chats
claude-extract --all --output "$EXPORT_DIR/code" 2>> "$LOG"

# Process and send to vault
python3 "$SCRIPT_DIR/claude_to_obsidian.py" \
    --export-dir "$EXPORT_DIR" \
    --vault-dir "$VAULT_DIR" \
    --move 2>> "$LOG"

echo "[$(date)] Sync completed" >> "$LOG"
```

**5. Schedule automatic execution:**

```bash
chmod +x ~/scripts/sync_claude_obsidian.sh

# Run daily at 10 PM
(crontab -l 2>/dev/null; echo "0 22 * * * $HOME/scripts/sync_claude_obsidian.sh") | crontab -
```

**6. For Claude Web chats:**

Install the **"Export Claude Chat to Markdown"** browser extension for Chrome/Edge. Do periodic bulk exports, save the `.md` files to `~/claude-exports/web/`, and the cron job handles the rest.

**7. Add a section to the vault's CLAUDE.md:**

```markdown
## Chat Import Pipeline

### Structure
- `chats/code/` → imported Claude Code conversations
- `chats/web/` → imported Claude Web/App conversations
- All chats get frontmatter with `type: chat` and `chat-import` tag

### Filter in Graph View
- `tag:chat-import` → chats only
- `-path:chats` → hide chats
```

---

## Part 3 — Graphify (Codebase Knowledge Graph)

### Concept

[Graphify](https://github.com/safishamsi/graphify) transforms your codebase into a queryable knowledge graph. Instead of Claude Code re-reading every file, it queries the graph — which is persistent across sessions and costs a fraction of the tokens.

- **Code:** processed 100% locally via tree-sitter AST. No code content leaves your machine.
- **Cache:** SHA256 — re-runs only process modified files.
- **Cost:** 0 tokens in default mode (pure AST). `--deep` mode uses LLM for semantic edges.
- **Languages:** Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby, C#, Kotlin, Scala, PHP, Swift, Lua, Zig, and more (20 languages via tree-sitter).

### Setup

**1. Install:**

```bash
pip install graphifyy
graphify install --platform claude
```

`graphify install --platform claude` creates the skill at `~/.claude/skills/graphify/SKILL.md`. Other platforms are also supported (`cursor`, `codex`, `opencode`, etc.).

**1.5. Set up API key (required for semantic extraction):**

Graphify needs an LLM API key from Anthropic or Moonshot (Kimi) for semantic extraction. Export one before running:

```bash
export ANTHROPIC_API_KEY="your-key-here"
# or
export MOONSHOT_API_KEY="your-key-here"
```

If you want to skip LLM costs entirely, use AST-only mode:

```bash
graphify extract . --out ./graphify-out --no-cluster
```

This generates a structural graph without semantic edges.

**2. Generate the graph:**

Graphify has two execution paths and the original `--obsidian*` flags only work on one of them. Pick the form that matches how you're invoking it:

**A. Inside Claude Code (skill — recommended for this guide):**

```
/graphify . --obsidian --obsidian-dir ~/vault/graphify/project-name
```

This runs the `/graphify` slash command, which the skill at `~/.claude/skills/graphify/SKILL.md` parses. The skill calls `graphify.export.to_obsidian()` in Python directly, so `--obsidian` and `--obsidian-dir` are recognized here — they're not part of the headless shell parser.

**B. From the terminal / CI (headless CLI):**

```bash
graphify extract . --out ./graphify-out
```

The headless CLI uses subcommands (`extract`, `update`, `watch`, `tree`) and does **not** expose `--obsidian` / `--obsidian-dir` / `--wiki` / `--mode deep`. If you want Obsidian integration from the terminal, symlink the output directory into your vault after extraction:

```bash
ln -s $(pwd)/graphify-out ~/vault/graphify/project-name/graphify-out
```

Generated output (varies by path and flags):

```
your-project/
└── graphify-out/
    ├── graph.json          # queryable graph (always)
    ├── graph.html          # interactive viz (skill auto-generates; headless: see step 3)
    ├── GRAPH_REPORT.md     # god nodes, connections, metrics (always)
    ├── wiki/               # Wikipedia-style articles (skill form with --wiki only)
    └── cache/              # SHA256 cache

~/vault/graphify/project-name/    # only when skill form was given --obsidian
    └── (Obsidian notes)          # one note per function/module
```

**3. Generate interactive visualization (headless only):**

The skill auto-generates `graph.html` during extraction. For the headless path, run the visualization as a separate step:

```bash
graphify tree --graph ./graphify-out/graph.json --output ./graphify-out/GRAPH_TREE.html
```

Open the HTML file in a browser to explore the graph interactively.

**4. Update .gitignore:**

```gitignore
# Graphify
graphify-out/cache/
```

Keep `graph.json` and `GRAPH_REPORT.md` versioned — they're useful for the team.

**5. Add to the project's CLAUDE.md:**

Append to the CLAUDE.md at the repository root:

```markdown
## Context Navigation (Graphify)

### 3-Layer Query Rule
1. **First:** query `graphify-out/graph.json` or `graphify-out/wiki/index.md`
   to understand code structure and connections
2. **Second:** query the Obsidian vault for decisions, progress, and project context
3. **Third:** only read raw code files when editing
   or when the first two layers don't have the answer

### When to rebuild the graph
- After structural changes (new modules, major refactors)
- Headless: `graphify update .` (only processes modified files)
- Skill: `/graphify . --update` (same behavior, runs through the skill — also accepts `--obsidian` to refresh the vault)
- The graph is persistent — NO need to rebuild every session

### Do NOT
- Don't manually modify files inside `graphify-out/`
- Don't re-read the entire codebase if the graph already has the information
```

**6. Add to the vault's CLAUDE.md:**

```markdown
## Graphify (Codebase Maps)

### Structure
- `graphify/project-x/` → knowledge graph for project X
- Future projects get their own subfolders
- Notes are auto-generated — do NOT edit manually

### In Graph View
- Filter by `path:graphify` to see only code nodes
- Filter by `-path:graphify` to hide code nodes
```

**7. Git Hook (optional):**

Automatically rebuilds the graph on every commit:

```bash
graphify hook install
```

**8. Watch Mode (optional):**

Auto-rebuild on file save. Pick the form that matches how you invoke graphify.

Headless (separate terminal):

```bash
graphify watch .
```

Skill (inside Claude Code):

```
/graphify . --watch
```

### Useful Commands

The table below lists the **headless CLI** subcommands you'd run in a terminal. Inside Claude Code, the same operations are available via the `/graphify` slash form documented in `~/.claude/skills/graphify/SKILL.md` — that form additionally supports `--obsidian`, `--obsidian-dir`, `--wiki`, and `--mode deep` (which the headless parser doesn't expose).

| Command | Description |
|---------|-------------|
| `graphify extract .` | Full extraction on current directory |
| `graphify extract ./src` | Scan specific folder |
| `graphify update .` | Only process modified files |
| `graphify watch .` | Auto-rebuild on save |
| `graphify query "question"` | Query the graph directly |
| `graphify explain "NodeName"` | Plain-language explanation of a node |
| `graphify path "A" "B"` | Shortest path between two nodes |
| `graphify tree --graph ./graphify-out/graph.json --output ./graphify-out/GRAPH_TREE.html` | Generate interactive visualization |
| `open graphify-out/graph.html` | Open interactive visualization (skill-generated) or `GRAPH_TREE.html` (headless) |

### Adding New Projects

With a centralized vault, each project is just a subfolder. Same two paths as the initial setup.

Skill (inside Claude Code):

```
/graphify ~/another-project --obsidian --obsidian-dir ~/vault/graphify/another-project
```

Headless (terminal):

```bash
cd ~/another-project
graphify extract . --out ./graphify-out
ln -s $(pwd)/graphify-out ~/vault/graphify/another-project/graphify-out
```

Drop the `ln -s` line if you don't need Obsidian to pick up the graph. Notes appear in Obsidian's graph view alongside everything else.

---

## Part 4 — Complete Workflow

### Typical session

```
Open Claude Code session
    │
    ├── /resume                      ← loads vault context
    │                                   (recent logs, decisions, progress)
    │
    ├── Claude queries graph.json     ← understands code structure
    │                                   without re-reading all files
    │
    ├── Work on code                  ← features, bugs, refactors
    │
    ├── /save                        ← generates session log in vault
    │
    └── git commit                   ← hook rebuilds graph automatically
```

### Savings per layer

| Layer | Without it | With it |
|-------|-----------|---------|
| `/resume` | Re-explain project every session | Claude already knows the context |
| Graphify | Re-read ~40 files (~20k tokens) | Query 1 graph (~280 tokens) |
| Chat pipeline | Insights lost in chat history | Everything indexed and searchable |
| `/save` + logs | Forget what was done | Complete history with wikilinks |

### Graph View Filters

| Filter | What it shows |
|--------|--------------|
| `path:permanent` | Only permanent notes (consolidated knowledge) |
| `path:graphify` | Only codebase nodes (functions, modules, imports) |
| `tag:chat-import` | Only imported chats |
| `-path:graphify -path:chats` | Only manual notes (pure vault) |

---

## Real Results

Tested on a React + Supabase project with 126 TypeScript files:

| Metric | Value |
|--------|-------|
| Graph nodes | 332 |
| Edges (connections) | 258 |
| Communities detected | 124 |
| graph.json size | 172 KB |
| Obsidian notes generated | 456 |
| Token reduction per query | **499x** |
| LLM cost for generation | **0 tokens** (AST mode) |
| Imported chats in vault | 137 |
| Accumulated permanent notes | 65+ |
| Total vault notes | 780+ |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (single)                   │
│                                                             │
│  permanent/  ← consolidated knowledge (Zettelkasten)        │
│  logs/       ← session logs (/save)                         │
│  chats/      ← imported conversations (cron pipeline)       │
│  graphify/   ← codebase knowledge graphs                    │
│  project-x/  ← MOCs, decisions, architecture                │
│                                                             │
│  CLAUDE.md   ← global instructions for Claude Code          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                    Claude Code reads/writes
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                   PROJECT REPOSITORY                         │
│                                                             │
│  src/            ← source code                              │
│  CLAUDE.md       ← project instructions + Context Nav       │
│  graphify-out/   ← graph.json, graph.html, report           │
│  .git/hooks/     ← post-commit rebuilds the graph           │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

**Graphify notes don't appear in Obsidian:**
Confirm the notes are inside the actual vault directory. Obsidian doesn't always point where you think — create a note in Obsidian and run `find ~ -name "note-name.md"` to discover the real path. Then move the notes there and Cmd+Q / reopen.

**Graph view empty with filter applied:**
Disable "Orphans" and "Existing files only" in the graph filters. Cmd+Q and reopen Obsidian to force reindexing.

**Claude Code doesn't query the graph:**
Check that the project's CLAUDE.md has the "Context Navigation" section and that `graphify-out/graph.json` exists at the repo root.

**Cron doesn't run (macOS):**
Grant Full Disk Access to your terminal in System Preferences → Privacy & Security.

**Graphify doesn't generate wiki:**
The `wiki/` folder is only produced by the **skill form with `--wiki`** (`/graphify . --wiki` inside Claude Code). The headless `graphify extract` subcommand doesn't expose `--wiki`. From the terminal, use `graphify query "question"` against `graph.json` instead, or run the skill form if you need the Wikipedia-style articles.

**Files with parentheses in name:**
Graphify generates notes like `myFunction().md`. Obsidian may struggle indexing files with `()` in the name. If needed, batch rename:
```bash
cd ~/vault/graphify/project
for f in *"("*; do mv "$f" "$(echo "$f" | sed 's/[()]//g')"; done
```
**Unknown Command error in graphify:**
If `graphify .` errors with `unknown command '.'`, you're running the **headless CLI** — which requires a subcommand (`extract`, `update`, `watch`, etc.) before the path. Either use the headless form:
```bash
graphify extract . --out ./graphify-out
# or, to refresh an existing graph:
graphify update .
```
Or, inside Claude Code, use the **skill form** with the leading slash — which routes through the `/graphify` skill rather than the shell parser and supports the full flag set (`--obsidian`, `--obsidian-dir`, `--wiki`, `--mode deep`, etc.):
```
/graphify . --obsidian --obsidian-dir ~/vault/graphify/project-name
```

---

## Credits & Links

- [Graphify](https://github.com/safishamsi/graphify) — codebase knowledge graphs (MIT)
- [Obsidian](https://obsidian.md) — PKM and second brain (free)
- [Claude Code](https://docs.anthropic.com) — Anthropic's coding agent
- Inspired by Andrej Karpathy's system and the r/ClaudeAI community

---

**If this guide helped you, give the repo a ⭐ and share it with other devs using Claude Code.**
