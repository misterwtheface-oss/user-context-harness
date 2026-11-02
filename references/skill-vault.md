# Skill vault: many skills without paying for them every session

## Who this is for

Offer it when any of these is true, and not otherwise:
- **Lots of skills at setup.** The pre-flight count (below) finds more than about 25 installed skills, often because a
  team or company shares a skill library.
- **Heavy skill users.** The person builds or collects skills as a habit and expects the list to keep growing.
- **The list has become unmanageable.** They say Claude picks the wrong skill, ignores one, or that the skill list is
  long. These are symptoms of too many descriptions competing in every session.

Someone with five skills gets nothing from it; leave their skills where they are.

## The problem, in one paragraph for the person

Every installed skill (a folder under `~/.claude/skills/` or a project's `.claude/skills/`) puts its name and
description into every session, used or not. That is the price of Claude knowing the skill exists. With a hundred and
fifty skills it adds up to thousands of tokens before the first message, every session, and the skills crowd each other.
The vault moves skills out of those folders so they cost nothing at startup. A small script that already runs before each
message checks the message against each vaulted skill's keywords and shows Claude only the few that match, with the path
to read. Claude then reads that skill and follows it as usual.

## How it works

- **Vault**: a folder Claude Code does not scan, holding skill folders unchanged: `<workspace>/skill_vault/<skill>/SKILL.md`.
- **Keywords**: one line added to each vaulted skill's frontmatter, in the person's words for the task:
  `keywords: [rotate api keys, key rotation, expired credentials]`. Claude Code never parses a vaulted skill, so the extra
  field is safe. A keyword hit scores its word count; the skill name always counts as a full match. A distinctive
  single word can be marked strong with a trailing `!` (`datamine!`) so it surfaces the skill on its own; use it sparingly.
- **Routing**: the prompt hook (Tier 2's `ctx_lite.py`, or the full `ctx` kit's `skillroute.py`) scores each prompt. A
  skill that reaches the threshold (2: one two-word phrase, two single words, or the name) is printed as a pointer, at
  most three per prompt, each once per session.
- **Pinned skills stay installed**: a skill used in nearly every session, or one the person starts by typing `/name`,
  stays in `~/.claude/skills/`. Vaulted skills cannot be started with a slash; the person says "use <skill name>" instead.

Because routing runs in the prompt hook, the vault needs Tier 2 (Python and a machine where the person may edit
`~/.claude/settings.json`). On a managed machine without hooks, do not vault anything: an unrouted skill is a lost skill.

## Setting it up

1. **Count.** List `~/.claude/skills/*/SKILL.md` and `<cwd>/.claude/skills/*/SKILL.md`. Report the number in one line and
   offer the vault only past the threshold or on the symptoms above.
2. **Choose what stays.** Show the list with a suggested split: pinned (daily use, slash-invoked) and vaulted (the rest).
   The person edits the split. Default to vaulting; a wrong vault costs one "use <name>", a wrong pin costs every session.
3. **Write keywords before moving.** For each skill to vault, propose a `keywords:` line from its description and its
   "Trigger Patterns" section, in plain task words the person would actually type. Show them in one table; take edits.
4. **Move, after a listed yes.** Move each folder to `<workspace>/skill_vault/`, log it in `inbox/MOVED.md`, never delete.
   Scripts inside skills that locate files relative to `SKILL.md` keep working; check any that hard-code
   `~/.claude/skills`.
5. **Test.** For three vaulted skills, feed a typical prompt to the hook as in `optional-hooks.md` and confirm the skill
   appears; feed an unrelated prompt and confirm nothing does. Then start a new session and confirm the vaulted skills are
   gone from the startup list.
6. **Record** in the workspace README which skills are pinned and that new skills go to the vault with a keywords line.

## Keeping it healthy

- A skill that never surfaces when it should has weak keywords: add the words the person actually used that time.
- A skill that surfaces on unrelated prompts has a generic keyword ("report", "data"): replace it with a phrase.
- Moving a skill back is a single folder move; nothing else references its location.
- The full `ctx` kit adds checks: `ctx.py skills` lists every vaulted skill with its keywords, flags skills still on
  derived keywords, duplicates, and skills both vaulted and installed (paid twice); `ctx.py skills match "<prompt>"` shows
  what a prompt would surface.
