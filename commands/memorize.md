# /memorize — Update Permanent Memory

Pins a decision, insight or convention to the vault right away. /save already does this automatically at the end of the session; use this command only when you want to write something now, mid-session.

When you receive this command, do the following:

1. Read `~/.claude/commands/save.md`. Run the "Vault detection" block to get `<vault>` and `<project>`.
2. **With an argument** (the item to memorize): run steps 2.2 to 2.5 of Phase 2 for the given item. If the item meets none of the 2.1 criteria, say why and don't write.
3. **Without an argument:** run the whole Phase 2, starting at 2.1, over the current session. Items that a /save in this session already wrote count as "already memorized with no change".
4. Don't create a session log: step 2.4 only applies if a log for this session already exists (from an earlier /save); in that case, update its "Notes created or updated" section.
5. In the 2.5 report, omit the "Session log" line if none was touched.
6. If nothing was written, don't write any file and end the reply with this exact line:
   `Memory: nothing new to memorize.`
