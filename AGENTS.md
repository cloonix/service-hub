# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Commit all changes** - This is MANDATORY:
   ```bash
   git add -A
   git commit -m "descriptive message"
   bd sync
   git status  # MUST show "nothing to commit, working tree clean"
   ```
5. **Clean up** - Clear stashes if any
6. **Verify** - All changes committed (but NOT pushed)
7. **Hand off** - Provide summary for next session

**CRITICAL RULES:**
- NEVER push to remote - user will push when ready
- ALWAYS commit locally so work is not lost
- Work is complete when committed locally and beads are synced
- NEVER use git push under any circumstances
- If user says "continue until finished", commit but do NOT push

