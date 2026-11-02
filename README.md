# user-context-harness

A Claude Code skill that sets a person up to work efficiently from their first session.

- **Tools first.** Checks the machine for the tools Claude works best with (git, Python, Node.js, ripgrep, jq, GitHub CLI;
  fd, uv, pandoc; Azure / AWS CLI, Docker, .NET, Java when the work calls for them) and installs the missing ones through a
  route the machine allows: Scoop or winget user scope on a locked-down work laptop, Homebrew on Mac, apt / dnf on Linux,
  or an IT request list when nothing may be installed. Then writes a short "Tools on this machine" block into
  `~/.claude/CLAUDE.md` so every session uses them without probing.
- **Context that survives sessions.** Plain-language house rules in `~/.claude/CLAUDE.md`, and a small workspace that maps
  each project to where its files already live (a repo, a shared drive, email) with a `CONTEXT.md` and a `PROGRESS.md`.
- **Skill vault, for heavy skill users.** Every installed skill costs its description in every session. With dozens or
  hundreds of skills, the vault keeps them out of the startup list and an optional prompt hook surfaces only the ones whose
  keywords match the prompt.
- **Safe by default.** Nothing is installed, moved or written without a listed yes; nothing is overwritten; every step has
  an undo.

## Install

Claude Code reads skills from `~/.claude/skills/`. Clone straight into it.

Windows (PowerShell):

```powershell
git clone https://github.com/misterwtheface-oss/user-context-harness "$env:USERPROFILE\.claude\skills\user-context-harness"
```

Mac / Linux:

```bash
git clone https://github.com/misterwtheface-oss/user-context-harness ~/.claude/skills/user-context-harness
```

No git? Download the ZIP from the green "Code" button, unzip, and rename the folder to `user-context-harness` inside
`~/.claude/skills/`. Update later with `git pull` in that folder.

Then start Claude Code and say something like "set up Claude on this laptop" or "I'm new to Claude Code, help me get set up".

## What is inside

| Path | What it is |
|---|---|
| `SKILL.md` | the protocol Claude follows |
| `scripts/toolcheck.py` | detects tools, admin rights and package managers; prints an install plan; writes the toolbox block |
| `assets/toolchain.json` | the tool list: tiers, why each matters, package ids per manager (edit to add tools) |
| `scripts/scaffold_workspace.py` | creates the workspace from templates; never overwrites; logs for undo |
| `scripts/ctx_lite.py` | optional advisory prompt hook: project briefs and skill-vault routing |
| `references/` | toolchain, intake questions, voice, workspace layout, hooks, skill vault |
| `evals/evals.json` | test prompts with expected behaviour |

Python 3 (stdlib only) runs the scripts; on a bare machine the skill installs Python first.

## Source

Developed in [misterwtheface-oss/skill-vault](https://github.com/misterwtheface-oss/skill-vault) and published here with
`git subtree`; changes land there first.
