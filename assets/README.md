<!--- Human readable documentation for the skill. Save as README.md for your project -->
### UserContextHarness
**What it does**: Sets someone up to work efficiently with Claude Code from the first session: installs the tools Claude works best with through a route their machine allows, tells Claude which tools exist, then adds plain-language house rules and a small map of their projects so context survives between sessions

**Covers**:

- [ Toolchain first: `toolcheck.py` detects git, Python, Node.js, ripgrep, jq, GitHub CLI (plus fd, uv, pandoc and role tools such as Azure CLI or a JDK), picks an install route that works without admin on a locked-down work laptop (Scoop, winget user scope), or produces an IT request list when nothing may be installed ]
- [ A "Tools on this machine" block written into `~/.claude/CLAUDE.md` between markers, so every session uses the tools without probing; refreshed by re-running the check ]
- [ Six-question intake adapted from the ctx handoff; a workspace folder that maps each project to where its files really live (repo, shared drive, email) with CONTEXT.md and PROGRESS.md; never-overwrite creation with an undo log; per-file approval for moves ]
- [ Optional read-only permission allow list and an optional advisory prompt hook (ctx_lite.py), each behind its own yes and never on a managed machine's policy-controlled settings ]

**Trigger patterns**: "I'm new to Claude Code, how do I set this up", "set up Claude on my work laptop", "what should I install for Claude", "Claude keeps forgetting what we did", "I can't find the file you made", "help me get organized"
