<!--- Human readable documentation for the skill. Save as README.md for your project -->
### UserContextHarness
**WHat it does**: Sets up a small, visible home base and plain-language house rules for someone new to Claude Code who is not fluent with folders, so files land where they can find them and context survives between sessions

**Covers**:

- [ Six-question plain-language intake adapted from the ctx handoff, with environment detection instead of jargon questions ]
- [ Tier 1 scaffold: a chosen home folder (Documents or user folder, offered every time), one folder per project with CONTEXT.md and PROGRESS.md, a user-level CLAUDE.md, an inbox, and never-overwrite creation with an undo log ]
- [ Tier 2 optional advisory prompt hook (ctx_lite.py) that briefs Claude on the named project, installed only with Python verified and an explicit yes; existing files move only after a listed, per-file approval and every move is logged ]

**Trigger patterns**: "I'm new to Claude Code, how do I set this up", "help me get organized / where should my files go", "Claude keeps forgetting what we did", "I can't find the file you made", "everything is in my Downloads folder", "set up a workspace for me"
