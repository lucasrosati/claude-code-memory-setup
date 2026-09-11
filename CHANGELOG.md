# Changelog

All notable changes to this guide are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Since this is a documentation repository, versions track meaningful changes to the
setup itself: new components, corrections that change the instructions, and new scripts.

## [1.0.0] - 2026-09-10

First tagged release. The setup is complete and covers the full memory lifecycle
for Claude Code: structural code map, curated memory, chat history, and automatic
session capture.

### Added

- **Auto-save hook (`scripts/session_autosave.py`)** — a `SessionEnd` hook that
  writes a minimal session log to the vault when a session closes. Zero LLM calls:
  facts are extracted mechanically from the JSONL transcript (objective, files
  touched, commands, stats). Acts as a safety net when `/save` is forgotten.
  Inspired by [ai-memory](https://github.com/akitaonrails/ai-memory).
- **Part 5 section** in both READMEs documenting hook installation, routing
  behavior, and Obsidian filters for auto-logs.
- **Chat import scripts** (`scripts/claude_to_obsidian.py`,
  `scripts/sync_claude_obsidian.sh`) — previously described in prose only, now
  published as runnable files with their own README.
- **Session commands as global skills** — documentation on implementing `/save`
  and `/resume` under `~/.claude/` so they register as real slash commands instead
  of living only as `CLAUDE.md` prose.
- **"Keep code out of the vault" warning** — clarifies that code repositories must
  live outside the vault to avoid Obsidian indexing `node_modules/` and build output.
- **Multi-repo guidance** — how to structure the setup when a product spans several
  repositories.

### Changed

- **Graphify commands updated for the current PyPI build.** The packaged CLI is
  subcommand-based (`graphify extract`, `graphify update`, `graphify watch`,
  `graphify tree`), so the previous `graphify . --flag` form fails from the terminal.
  Both invocation paths are now documented side by side: the skill form inside
  Claude Code (which supports `--obsidian`, `--obsidian-dir`, `--wiki`) and the
  headless form for terminal and CI.
- **`graphify install` → `graphify install --platform claude`.**
- Output tree and Useful Commands table corrected to match the current CLI surface.

### Fixed

- Added a documented LLM API key requirement for semantic extraction, plus the
  AST-only path for users who want to avoid LLM costs entirely.
- Troubleshooting entry for the `unknown command '.'` error.
- Troubleshooting entry for Obsidian failing to index notes when the vault path
  differs from the expected one.

## [0.1.0] - 2026-04-12

Initial public guide.

### Added

- **Part 1 — Obsidian as persistent memory.** Single centralized vault, Zettelkasten
  conventions, folder structure, `CLAUDE.md` rules, `/save` and `/resume` commands.
- **Part 2 — Chat import pipeline.** Exporting Claude Code and Claude Web
  conversations into the vault with frontmatter, auto-tags, and wikilinks.
- **Part 3 — Graphify.** Generating a codebase knowledge graph so Claude Code
  queries a graph instead of re-reading every file.
- **Part 4 — Complete workflow**, architecture diagram, measured results, and
  troubleshooting.
- Full Portuguese translation (`README.pt-BR.md`).
- MIT license.

[1.0.0]: https://github.com/lucasrosati/claude-code-memory-setup/releases/tag/v1.0.0
[0.1.0]: https://github.com/lucasrosati/claude-code-memory-setup/releases/tag/v0.1.0
