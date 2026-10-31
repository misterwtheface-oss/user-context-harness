---
name: user-context-harness
description: "Sets up a tidy, persistent home base for a person who is new to Claude Code and not fluent with their computer's folders: a plain-language intake, a visible workspace with one folder per project, a user-level CLAUDE.md of house rules, memory that survives between sessions, and an optional one-hook automation tier. Use this whenever someone is new to Claude Code, asks how to get organized or set up, says Claude keeps forgetting things, cannot find files Claude made, keeps everything in Downloads or Desktop, or asks where files should go. Trigger even when they do not use the words workspace, harness, or onboarding."
---

# User Context Harness

## Overview
Many people reach Claude Code having never built a folder tree on purpose. Their computer is Downloads, Desktop,
Documents, and whatever an app saved somewhere. Claude then creates files in the current directory, which they cannot
find, and forgets everything by the next session, which they experience as the tool being unreliable. Neither is their
fault. Both are fixed by giving them a small, visible home for Claude work and a short set of written rules that Claude
follows every session.

This skill runs that setup as a guided conversation. It adapts the intake, brownfield, and local-vs-shared ideas from the
`ctx` handoff (see `references/intake-questions.md`) to one person on one machine, and scales the deterministic layer to
what they can actually run: Tier 1 is folders plus rules plus memory and needs nothing installed; Tier 2 adds one advisory
prompt hook, only when Python is present and they say yes.

The user never sees "registry", "hook", or "post-flight". They see a folder they can open, a README that explains it, and
a Claude that remembers where things are.

## Trigger Patterns
Intent phrases that should activate this skill:
- "I'm new to Claude Code, how do I set this up"
- "help me get organized" / "where should I put my files"
- "Claude keeps forgetting what we did last time"
- "I can't find the file you made"
- "everything is in my Downloads folder"
- "set up a workspace for me" / "set up my context"
- A first session where the working directory is Downloads, Desktop, or the home folder and the person sounds unsure

## Context Mode
- What "mode" the agent enters when this skill activates:
- **Mode Name**: "Onboarding Guide Mode"
- **Elevated Permissions**: Create folders and files inside one chosen home folder; write `~/.claude/CLAUDE.md`; with
  explicit opt-in, edit `~/.claude/settings.json` to add one hook; move the user's existing files only after listing them
  and receiving a yes for that list
- **Safety Level**: Medium

## Prerequisites
- Claude Code (CLI or desktop) with file access to the user's home directory
- A shell: PowerShell on Windows, zsh or bash on Mac and Linux
- Python 3 is needed only for `scripts/scaffold_workspace.py` and for Tier 2; both have a no-Python path
- Read `references/novice-guidance.md` before the first message to the user. It sets the voice for the whole session

## Strict Protocol

### Step 1: Pre-Flight Checks
**MUST** actions before any execution:
- [ ] Read `references/novice-guidance.md`. It explains how to describe a path, when to open a folder on screen, and why
      one idea per message matters for this audience
- [ ] Detect the environment without asking: OS, home directory, whether `python` or `py -3` runs, whether
      `~/.claude/CLAUDE.md` and `~/.claude/settings.json` already exist, and what the current working directory is. Open
      `references/optional-hooks.md` only when Python is present
- [ ] Look for an existing home. If a folder already contains a `README.md` that mentions this skill, or `~/.claude/CLAUDE.md`
      names a home path, this is a repeat visit: read that README and skip to the part of the intake that is missing
- [ ] Run the intake from `references/intake-questions.md`. Ask in plain words, two or three questions per message at most,
      and take the user's own words for each body of work as the project names. Record the answers; they become the
      "Why this is set up this way" section of the workspace README

### Step 2: Verification
**MUST** get confirmation before proceeding:
- [ ] Offer the home location as a choice every time, both options spelled out with the full path: a visible folder under
      Documents (what most novices can find again) or a folder directly in their user folder (shorter paths, matches
      developer habits). Recommend Documents unless they already work from their user folder. See
      `references/workspace-layout.md` for the exact names per OS
- [ ] Show the tree that will be created, as an indented list, with one plain sentence per folder. Keep it to the layout
      in `references/workspace-layout.md`; do not invent extra folders on the first pass
- [ ] Show the house rules that will go into `~/.claude/CLAUDE.md` (from `assets/templates/CLAUDE.md`) and ask whether
      any rule is wrong for them
- [ ] If any of their existing files came up in intake, present the candidate moves as a list: file name, where it is
      now, where it would go, why. Nothing moves until they say yes to that list. "Move only with per-file approval" is
      the rule; a sweep is never offered
- [ ] If Python is present, describe Tier 2 in one paragraph and ask yes or no. Default is no
- [ ] Ask: "Should I go ahead and create this?" and wait for an explicit yes

### Step 3: Execution
Only after confirmation:
- [ ] Create the tree. Prefer `python scripts/scaffold_workspace.py --home "<path>" --project "<name>" ...` because it never
      overwrites, fills the templates, and writes `.setup-log.json` for rollback. Without Python, create the same files by
      hand from `assets/templates/`, filling the placeholders, and write the log yourself
- [ ] Write `~/.claude/CLAUDE.md`. If one exists, append a clearly titled section rather than replacing it, and say so
- [ ] Perform any approved moves, one list at a time, and append each move to `<home>/inbox/MOVED.md` so the person can
      trace where a file went. Never delete
- [ ] If Tier 2 was approved, follow `references/optional-hooks.md`: back up `settings.json`, add the single hook, run the
      activation test with hook-shaped JSON on stdin, and remove the hook again if the test fails
- [ ] Open the new home folder on screen (`explorer.exe` on Windows, `open` on Mac, `xdg-open` on Linux) and ask the
      person to confirm they can see it. This is the moment the structure becomes real for them
- [ ] Fill the first project's `PROGRESS.md` with what was decided today, in their words, so the next session has
      something to recall

### Step 4: Post-Flight
After execution completes:
- [ ] Walk the person through the README in two or three messages: what each folder is for, how to pin the home in
      Explorer or Finder, how to read `PROGRESS.md` themselves
- [ ] Verify by re-reading what was written: every path in the README exists, `CLAUDE.md` names the right home, nothing
      new was left in Downloads or the previous working directory
- [ ] Tell them the one habit that matters: when they start the next session, name the project, and Claude will open its
      `CONTEXT.md` and `PROGRESS.md` first. Suggest they try it tomorrow
- [ ] Leave Onboarding Guide Mode. From here on the house rules in `CLAUDE.md` carry the behaviour

## Safety Rules
Non-negotiable constraints while this skill is active:
1. **One home, chosen by them**: Everything this skill creates lives inside the home folder they picked, plus the two
   user-level Claude files. No files appear anywhere else, because "where did it go" is the problem being solved
2. **Existing files move only after a listed yes**: Present each proposed move as a list and wait. Never sweep, never
   delete, always log the move. People trust a tool that touches their files exactly as much as it promised to
3. **Never overwrite**: The scaffolder skips existing files and reports them. An existing `CLAUDE.md` or `settings.json`
   is appended to or backed up, never replaced
4. **Plain language, one idea per message**: No jargon without a one-line explanation. Describe every path twice, once as
   a full path in a code block and once as a click path in words. See `references/novice-guidance.md`
5. **Tier 2 is opt-in and advisory**: Hooks never block anything for a novice, and the skill never installs one without
   Python verified and a clear yes
6. **Their words are the vocabulary**: Project folder names and aliases come from how the person described their work,
   not from what Claude would call it. A folder they would not recognise is a folder they will not open

## Rollback Procedures
If something goes wrong:
1. Read `<home>/.setup-log.json`. It lists every file and folder the scaffolder created, with timestamps
2. Remove only entries that are still unchanged since creation; leave anything the person has edited and say so
3. Restore `~/.claude/settings.json` from the dated backup made before the Tier 2 edit, and remove the appended section
   from `~/.claude/CLAUDE.md` if it was added this session
4. Reverse any moves using `<home>/inbox/MOVED.md`, which records source and destination for each file
5. Tell the person in one message what was undone and what was left in place

## Related Rules
- [Novice guidance](references/novice-guidance.md): Voice, path description, and pacing rules for this audience
- [Workspace layout](references/workspace-layout.md): The folder skeleton, naming rules, and what goes where

## Related Workflows
- [Intake questions](references/intake-questions.md): The plain-language interview and how each answer changes the build
- [Optional hooks](references/optional-hooks.md): Tier 2 install, activation test, and removal

## Example Implementation

```markdown
User: i just installed claude code and honestly i dont know where anything is. all my stuff is in downloads.
      i want help with my team's weekly report and also planning a kitchen remodel

Claude (intake, two questions): Happy to set this up. Two quick things first. For the weekly report, is
      that a file you get sent, or something you write from scratch? And is this your only computer, or do
      you also use a work laptop?

User: i get a spreadsheet emailed every monday and turn it into a summary. just this computer.

Claude (home choice): I'll make one folder for all Claude work so you always know where to look. Two
      options:
      1. Documents > Claude Home   (C:\Users\sam\Documents\Claude Home)   - easiest to find again
      2. Your user folder > claude_workspace   (C:\Users\sam\claude_workspace)   - shorter paths
      I'd suggest the first. Which do you prefer?

User: documents

Claude (verification): Here is what I'll create ... [tree with one sentence each] ... and these house rules
      go in a file Claude reads every time it starts ... [rules]. The Monday spreadsheets can stay in
      Downloads, or I can list them and move them into the weekly-report project if you say yes to the list.
      Should I go ahead and create this?

User: yes, and move the spreadsheets

Claude: lists the 4 spreadsheets with current and proposed location, waits for yes, runs the scaffolder,
      moves and logs them, opens the folder on screen, fills PROGRESS.md, walks through the README.
```

## Notes
- This skill is about the person's first week with Claude Code, not about any one project. Project-specific skills
  should build on the home it creates rather than on Downloads
- The handoff documents this adapts (`ADOPTION.md`, `PORTING.md`) assume an owner who can answer twelve intake
  questions and run a Python toolkit. This skill asks six and runs zero by default. Expand toward the full framework only
  when the person has used the home for a while and asks for more automation
- Repeat visits are normal. The pre-flight check for an existing home exists so the skill extends rather than restarts
