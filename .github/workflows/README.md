# CI checks

`ci.yml` runs on every pull request to `main`, on pushes to `main`, and manually
(`workflow_dispatch`). It needs no secrets, finishes in under two minutes, and only
enforces things that were real bugs in past PRs. There are deliberately **no
style linters** — a good documentation PR must never be blocked by cosmetics.

| Job | What it catches |
|---|---|
| `lint-python` | Syntax errors and real mistakes in `scripts/*.py` (`py_compile` + `ruff` with only `E9,F63,F7,F82`: syntax, invalid comparisons, misplaced `break`/`return`, undefined names). No formatting or complexity rules. |
| `lint-shell` | Common shell bugs in `scripts/*.sh` (`shellcheck --severity=warning`; info/style suggestions do not fail). |
| `check-links` | Broken links (internal and external) in `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `scripts/README.md` via [lychee](https://github.com/lycheeverse/lychee). `429` is accepted (rate limit, not a broken link). Patterns in `.lycheeignore` (localhost, `example.com`, `<placeholders>`) are skipped. |
| `readme-parity` | `README.md` and `README.pt-BR.md` drifting apart. Compares the number of `##` sections (error) and fenced code blocks (warning if they differ by more than 2). Structure only — translated text is never compared. |
| `validate-hook-json` | Broken ` ```json ` examples (e.g. the `~/.claude/settings.json` hook config). Snippets containing `...` or comment lines are treated as intentionally partial and skipped. |

## Run the checks locally

From the repository root:

```bash
# lint-python
python3 -m py_compile scripts/*.py && echo "Python OK"
pip install ruff && ruff check scripts/ --select=E9,F63,F7,F82

# lint-shell  (brew install shellcheck / apt install shellcheck)
shellcheck --severity=warning scripts/*.sh

# check-links  (brew install lychee)
lychee --accept 200,204,206,429 --exclude-all-private \
  README.md README.pt-BR.md CHANGELOG.md scripts/README.md

# readme-parity
python3 .github/scripts/check_parity.py

# validate-hook-json
python3 .github/scripts/check_json_blocks.py README.md README.pt-BR.md CHANGELOG.md scripts/README.md
```

## Adding or changing a check

- Keep it secret-free and fast.
- It must catch a class of bug that actually happens here, not a style preference.
- Prefer leaving a check out over shipping one that is flaky.
