# Tier 2: the optional prompt hook

Tier 1 works because Claude reads `~/.claude/CLAUDE.md` at start and follows the rule "when the person names a project,
open its CONTEXT.md and PROGRESS.md first". That is a rule the model follows, which means it is probabilistic. Tier 2 makes
the first half deterministic: a script sees each prompt, resolves the project from the aliases in `CONTEXT.md`, and injects
the project path, read order, and the open-item bullets before Claude starts thinking. It is the first step of the
handoff's "minimal viable version" (registry, resolve, brief, prompt hook), with the registry replaced by the folder tree
itself so there is nothing extra to maintain.

It is advisory only. It never blocks a turn, never gates a stop, never logs the person's prompts anywhere but a per-session
state file inside the workspace. Those are the handoff's post-flight and gap-log ideas, and they are wrong for someone in their
first week.

## Offer it only when all of these hold

- Python 3 runs from the shell (`python --version` or `py -3 --version` on Windows)
- The machine is theirs (intake question 3), not a managed work laptop
- They answered "check things automatically" to intake question 6, after the one-paragraph explanation
- Tier 1 is already created and the toolbox block is written

Otherwise skip this file entirely and do not mention hooks. It can be added in any later session.

## Install

1. Copy `scripts/ctx_lite.py` to `<home>/tools/ctx_lite.py`. Keeping it inside the home means it is visible, backed up
   with everything else, and removable by deleting one folder.
2. Back up `~/.claude/settings.json` to `~/.claude/settings.json.bak-<YYYY-MM-DD>` before touching it. If the file does
   not exist, create it with just the hooks block.
3. Add one hook. Use the interpreter that worked in the detection step and the absolute path to the home, because this is
   a single-machine user-level install:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"C:/Users/sam/claude_workspace/tools/ctx_lite.py\""
          }
        ]
      }
    ]
  }
}
```

If `settings.json` already has a `hooks` block, merge the entry into the existing `UserPromptSubmit` array rather than
replacing anything. Forward slashes work on Windows inside the JSON string and avoid escaping.

4. Activation test, before telling the person it is on. Feed hook-shaped JSON on stdin exactly as Claude Code would:

```
echo '{"session_id":"test-1","prompt":"lets work on the weekly report","cwd":"C:/Users/sam"}' | python "<home>/tools/ctx_lite.py"
```

Expected: a short block beginning `[ctx-lite] weekly-report` with the project path, read order, and any bullets under
"Waiting on you" and "Open items". A second run with the same session id prints nothing (once per session per project). A
prompt that names no project prints nothing. A failure prints nothing and exits 0; the hook must never break a turn.
Delete `<home>/.state/test-1.json` after the test so the test session id does not linger.

5. If the test does not behave, remove the hook entry, restore the backup, and tell the person it is not on. Do not leave a
half-working hook; a confusing automation teaches them to distrust the whole setup.

## How the script resolves a project

- Lists `<home>/projects/*/CONTEXT.md`.
- Reads the `aliases:` line near the top of each (comma-separated phrases from intake) plus the folder name.
- Case-insensitive whole-phrase match against the prompt; longest alias wins on collision.
- Pulls bullets from `PROGRESS.md` under headings matching `Waiting on you` and `Open items`, up to 12 lines.
- Writes `<home>/.state/<session_id>.json` recording which projects have been briefed this session.
- Caps output at 3 KB. Over the cap, bullets truncate first; the path and read order always survive.

The home path is found from the script's own location (`tools/` is directly under the home), so the script has no config.

## Removal

Delete the hook entry from `~/.claude/settings.json` (or restore the dated backup), delete `<home>/tools/` and
`<home>/.state/`. Tier 1 is untouched.

## Growing toward the full framework

When the person starts asking for more (several bodies of work, a wrap-up check, rules that differ per project), the
handoff's `PORTING.md` order applies from step 2 onward: session state, then post-flight, then gap logging. Each of those
should arrive as its own conversation with its own yes.
