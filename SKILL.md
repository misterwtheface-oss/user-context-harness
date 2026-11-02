---
name: user-context-harness
description: "Sets a person up to work efficiently with Claude Code from their first session: checks the machine for the tools Claude works best with (git, Python, Node.js, ripgrep, jq, GitHub CLI, plus role tools) and installs the missing ones through a route their machine allows (no-admin routes on locked-down work laptops, an IT request list when nothing is allowed), tells Claude which tools exist, then adds user-level house rules, memory that survives between sessions, and a light per-project map that points at where their work already lives. Use this whenever someone is new to Claude Code or on a new or work machine, asks how to set up or what to install, says Claude is slow, keeps forgetting things, or cannot find files it made. Trigger even when they do not say setup, toolchain, workspace or onboarding."
---

# User Context Harness

## Overview
Two things make a first week with Claude Code go badly. The machine lacks the tools Claude leans on, so it searches by
reading files one by one, does data work by hand in the shell, and cannot undo a bad edit. And nothing is written down, so
every session starts from zero. People experience both as the tool being unreliable. Neither is their fault.

This skill fixes them in that order. First the toolchain: detect what is installed, install what is missing through a route
the machine permits, and write a short "Tools on this machine" block into `~/.claude/CLAUDE.md` so Claude uses those tools
without probing. Then context: house rules in that same file, and for each body of work a `CONTEXT.md` (what it is, the
words they use for it, where its files really live) and a `PROGRESS.md` (where things stand). Those two files sit in one
small workspace folder that acts as a map. Work that already lives in a repo, a shared drive or email stays there; the map
points at it.

It adapts the intake, brownfield and local-vs-shared ideas from the `ctx` handoff (see `references/intake-questions.md`)
to one person on one machine. Tier 1 is tools, rules and the map. Tier 2 adds one advisory prompt hook, only on a machine
they control and only with a yes.

## Trigger Patterns
Intent phrases that should activate this skill:
- "I'm new to Claude Code, how do I set this up" / "set up Claude on my work laptop"
- "what should I install for Claude" / "Claude is slow at searching" / "Claude keeps saying a command is not found"
- "Claude keeps forgetting what we did last time" / "I can't find the file you made"
- "help me get organized" / "set up my context"
- A first session on a machine where `toolcheck.py` reports essential tools missing

## Context Mode
- **Mode Name**: "Setup Guide Mode"
- **Elevated Permissions**: Run package-manager installs from the printed plan after a yes, using the person's own rights;
  write `~/.claude/CLAUDE.md`; create one workspace folder; with separate opt-ins, edit `~/.claude/settings.json` (allow
  list, Tier 2 hook) and move existing files after a listed yes
- **Safety Level**: Medium

## Prerequisites
- Claude Code (CLI or desktop) with a shell: PowerShell on Windows, zsh or bash on Mac and Linux
- Python 3 runs `scripts/toolcheck.py` and `scripts/scaffold_workspace.py`. On a bare machine, Python is the first install
  (`references/toolchain.md` § No Python yet); every step also has a by-hand path
- Read `references/novice-guidance.md` before the first message. It sets the voice and how to calibrate it to the person

## Strict Protocol

### Step 1: Pre-Flight Checks
**MUST** actions before any execution:
- [ ] Read `references/novice-guidance.md` and calibrate: a developer on a new laptop wants the list and the commands; a
      newcomer wants plain words and click paths
- [ ] Detect without asking: OS, user folder, current working directory, admin rights, package managers, and the tool
      state, all in one run of `python scripts/toolcheck.py` (or the one-liner in `references/toolchain.md` without Python).
      Also check whether `~/.claude/CLAUDE.md` and `~/.claude/settings.json` exist
- [ ] Look for a previous visit: a toolbox block or a workspace path in `~/.claude/CLAUDE.md`, or a README mentioning this
      skill. If found, read it and do only what is missing (often: re-run the tool check, add a project)
- [ ] Run the intake from `references/intake-questions.md`: two or three questions per message, their words kept. Question
      1 (what work) sets the role tools; question 3 (whose machine, what is allowed) sets the install route

### Step 2: Toolchain
**MUST** happen before any folder is created. Follow `references/toolchain.md`:
- [ ] Show the missing tools as one list, name plus the one-sentence why (not the commands). Recommended tools as a second
      short list. Role tools only if intake named that work. Ask one yes; they may strike items
- [ ] If installing is not allowed at all, skip installs and hand over the IT request list instead
- [ ] Run the printed install commands one tool at a time; report each in a word. If Windows asks for admin on a no-admin
      machine, cancel and use the Scoop route for that tool
- [ ] Explain that new tools appear in a new Claude Code session. In that session, re-run `toolcheck.py`, then
      `toolcheck.py --write-claude-md` so the toolbox block is in `~/.claude/CLAUDE.md`
- [ ] Optionally, as its own yes: the read-only allow list from `references/toolchain.md` (skip on policy-managed settings)

### Step 3: Verification of the context layout
**MUST** get confirmation before proceeding:
- [ ] Propose the workspace in one line, not as a decision to labour: `<user folder>/claude_workspace` by default; under
      Documents only if they find things through Documents and it is not cloud-synced with private material. See
      `references/workspace-layout.md`
- [ ] Show the tree as an indented list, one plain sentence per folder, and for each project where its real files live
      (a repo path, a shared drive, email). Work in a repo stays in the repo; only the two notes files go in the workspace
- [ ] Show the house rules for `~/.claude/CLAUDE.md` (from `assets/templates/CLAUDE.md`) and ask whether any is wrong
- [ ] If existing files came up, list candidate moves (file, where now, where to, why). Nothing moves without a yes to that
      list. Files inside a repo or shared drive are never moved
- [ ] If the machine is theirs and Python works, describe Tier 2 in one paragraph and ask yes or no. Default is no
- [ ] Ask: "Should I go ahead and create this?" and wait for an explicit yes

### Step 4: Execution
Only after confirmation:
- [ ] Create the workspace with `python scripts/scaffold_workspace.py --home "<path>" --project "<name>" --source
      "<name>=<where files live>" ... --user-claude-md`. It never overwrites, fills the templates, and logs to
      `.setup-log.json`. Without Python, create the same files by hand from `assets/templates/`
- [ ] `~/.claude/CLAUDE.md`: house rules are appended as a titled section if the file exists; the toolbox block sits
      between its own markers and is refreshed only by `toolcheck.py`
- [ ] Perform approved moves one list at a time, appending each to `<workspace>/inbox/MOVED.md`. Never delete
- [ ] If Tier 2 was approved, follow `references/optional-hooks.md`, including the activation test and removal on failure
- [ ] For a newcomer, open the workspace on screen once (`explorer.exe`, `open`, `xdg-open`) and ask them to confirm they
      see it. A developer can skip this
- [ ] Fill each project's `PROGRESS.md` with what was decided today, including which tools were installed

### Step 5: Post-Flight
After execution completes:
- [ ] `toolcheck.py` exits 0 (every essential tool present) or the person holds an IT request list for the rest
- [ ] Re-read what was written: every path in the README and each `CONTEXT.md` exists, `~/.claude/CLAUDE.md` names the
      workspace and carries a current toolbox block, nothing new was left in Downloads or the starting directory
- [ ] Give the one habit: start each session by naming the project; Claude opens its `CONTEXT.md` and `PROGRESS.md` first
- [ ] Leave Setup Guide Mode. From here on `~/.claude/CLAUDE.md` carries the behaviour

## Safety Rules
Non-negotiable constraints while this skill is active:
1. **Installs only from the shown list, with their rights**: Nothing is installed that the person did not see by name and
   say yes to. No elevation tricks, no disabling security software, no bypassing a company policy; a blocked install
   becomes an IT request line
2. **The workspace is a map**: Notes files go in the one workspace folder; real work stays where it already lives. No files
   appear anywhere else, because "where did it go" is one of the problems being solved
3. **Existing files move only after a listed yes**: never a sweep, never a delete, every move logged
4. **Never overwrite**: the scaffolder skips existing files; `CLAUDE.md` gets an appended section or a marked block;
   `settings.json` is backed up before any edit
5. **Plain language, calibrated**: no jargon without a one-line gloss for a newcomer; full paths always
6. **Tier 2 is opt-in and advisory**: never on a managed machine, never blocking
7. **Their words are the vocabulary**: project names and aliases come from how they described the work

## Rollback Procedures
If something goes wrong:
1. Uninstall a tool installed this session with the same manager (`winget uninstall --id <id>`, `scoop uninstall <id>`,
   `brew uninstall <id>`); the ids are in `assets/toolchain.json` and the project's `PROGRESS.md` lists what was installed
2. Restore `~/.claude/CLAUDE.md` from `CLAUDE.md.bak-<date>` or delete the marked toolbox block and the appended section
3. Restore `~/.claude/settings.json` from its dated backup
4. Read `<workspace>/.setup-log.json` and remove only entries unchanged since creation; reverse moves from `inbox/MOVED.md`
5. Tell the person in one message what was undone and what was left in place

## Related Rules
- [Novice guidance](references/novice-guidance.md): voice, calibration, path description, pacing
- [Workspace layout](references/workspace-layout.md): the map folder, naming rules, what goes where

## Related Workflows
- [Toolchain](references/toolchain.md): tiers, install routes per machine, work-machine limits, the toolbox block
- [Intake questions](references/intake-questions.md): the interview and how each answer changes the build
- [Optional hooks](references/optional-hooks.md): Tier 2 install, activation test, removal

## Example Implementation

```markdown
User: just got a new work laptop, installed claude code. i mostly do python data stuff for the finance team
      and our code is in an azure devops repo. not admin on this machine.

Claude (detects, then intake): ran the tool check. You have Git and Python. Missing: ripgrep (fast search),
      jq (reads JSON), Node.js (runs add-on tools), plus uv (Python packages without admin) and the Azure CLI
      since your work is on Azure. You're not admin, so I'd install them into your user folder with Scoop,
      which needs no admin rights. Is software installation allowed on this laptop, and OK to install those?

User: yes, skip node

Claude: sets up Scoop, installs ripgrep, jq, uv, azure-cli one by one, reports each, asks for a new session.
      New session: re-runs the check (all OK), writes the toolbox block into ~/.claude/CLAUDE.md.

Claude (layout): proposes C:\Users\pat\claude_workspace with one project, finance-models, whose CONTEXT.md
      points at the repo at C:\Users\pat\source\repos\finance-models (the code stays there), shows the
      house rules, asks for a yes, scaffolds, fills PROGRESS.md, gives the habit.
```

## Notes
- This skill is about the first week, not any one project. Project skills build on the toolbox and the map it leaves
- The handoff documents this adapts (`ADOPTION.md`, `PORTING.md`) assume an owner who answers twelve intake questions and
  runs a Python toolkit. This skill asks six. Grow toward the full framework only when the person asks for more automation
- Repeat visits are normal: re-run the tool check on a new machine, add a project, refresh the toolbox block
