# /commit — Commit + Push + Auto-save

When you receive this command, do the following:

## 1. Analyze changes
- Run `git status` and `git diff --stat` to see what changed
- Read the modified files to understand the context

## 2. Generate the commit message
- Write a concise, descriptive commit message
- Format: "type: short description" (e.g. "feat: leitner flashcards", "fix: auth redirect loop", "refactor: componentized sidebar")
- If there are several changes, use the most significant one as the main message

## 3. Execute
- `git add .`
- `git commit -m "generated message"`
- `git push`

## 4. Auto-save (session log + memory)
After the commit and the push, read `~/.claude/commands/save.md` and run Phases 1 and 2 in full, adding this section to the session log:
```markdown
## Commit
- Short hash, message, files changed
```

## Rules
- Never commit without showing `git status` first
- Always show the generated commit message before executing
- If there are files that shouldn't be committed (env, node_modules, etc.), warn the user
- Wait for the user's confirmation before running the commit
