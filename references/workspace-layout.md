# Workspace layout

The home is deliberately small: five things at the top level, two files per project. The handoff's greenfield skeleton has
a router, a state doc, decisions, changelog, session log, and archive per project. For a novice, the router and state doc
are enough; decisions and the session log fold into `PROGRESS.md` as sections, and the changelog is dropped. Grow it when
they ask why something was decided, not before.

## Home location, offered every time

| Option | Windows | Mac | Linux | Suits |
|---|---|---|---|---|
| Under Documents | `C:\Users\<name>\Documents\Claude Home` | `/Users/<name>/Documents/Claude Home` | `/home/<name>/Documents/Claude Home` | anyone who finds files through Documents today; recommended default |
| User folder | `C:\Users\<name>\claude_workspace` | `/Users/<name>/claude_workspace` | `/home/<name>/claude_workspace` | people who already open their user folder, or want short paths |

Spell both out with the person's actual user name, recommend the first unless intake said otherwise, and let them choose.
If Documents is cloud-synced (OneDrive, iCloud) and intake raised privacy, mention that the first option will sync and offer
the second.

## The tree

```
Claude Home/
  README.md            the map: what each folder is for, how to find this again, why it is set up this way
  CLAUDE.md            workspace rules Claude reads when working inside this folder
  inbox/               drop anything here for Claude to look at; MOVED.md records files moved in from elsewhere
  projects/
    <project-name>/
      CONTEXT.md       what this project is, the words you use for it, where its files are, what to read first
      PROGRESS.md      where things stand, what Claude is waiting on you for, open items, a line per session
      files/           working files for this project
      archive/         old items moved out of PROGRESS.md, dated
  archive/             whole projects that are finished
  .setup-log.json      what the scaffolder created and when (for undo); hidden, not mentioned unless needed
```

Tier 2 adds `tools/ctx_lite.py` and `.state/` at the top level. Neither appears in the README's main list; a one-line
"Automation" note at the end covers them.

## What goes where, and why

- **README.md** is written for the person, not for Claude. It opens with the click path to this folder, lists the folders
  with one sentence each, states the two habits (name the project at session start; date-first file names), and ends with
  the dated "Why this is set up this way" section from intake.
- **CLAUDE.md in the home** carries rules that apply when Claude is working inside the home: files go in the active
  project's `files/`, `PROGRESS.md` is updated before the session ends, moves are listed first. It is read by Claude Code
  automatically when the working directory is inside the home.
- **`~/.claude/CLAUDE.md`** (user level, outside the home) carries the rules that must hold even when Claude is started
  from Downloads or the Desktop: where the home is, that new files go there, that locations are reported in plain words.
  This is the file that stops the original problem from recurring.
- **CONTEXT.md** is the router. Aliases first, so a prompt-matching hook or a reading Claude can resolve "the Monday
  numbers" to this folder. Then where the real files live (which may be an email inbox or a shared drive, not this folder).
  Then read order: PROGRESS.md, then whatever else matters.
- **PROGRESS.md** is the state. Bullets under headings so a hook or a human can pull them. The template has "Where things
  stand", "Waiting on you", "Open items", "Decisions", and "Session log". Add headings only if intake asked for them.
- **files/** holds what Claude produces and what the person moves in. It is the answer to "where did it go".
- **archive/** at both levels exists so nothing is deleted. Old PROGRESS items move to `project/archive/<date>.md`;
  finished projects move whole to `Claude Home/archive/`.

## Naming rules

- Folder names: lowercase, hyphens, from the person's own phrase. `weekly-report`, `kitchen-remodel`, `mom-medical`.
- Display names in README and CONTEXT keep their capitalisation: "Weekly Report".
- Files: `YYYY-MM-DD short description.ext`. No `final`, no `v2`; the date is the version.
- Never rename a file the person brought in. Log it as-is in `MOVED.md`.

## Templates and placeholders

`assets/templates/` holds `CLAUDE.md` (user level), `HOME_CLAUDE.md` (inside the home), `README.md`, `CONTEXT.md`, and
`PROGRESS.md`. Placeholders the scaffolder fills, and that must be filled by hand when Python is absent:

| Placeholder | Value |
|---|---|
| `{{HOME}}` | full path to the home |
| `{{HOME_CLICK_PATH}}` | click path in words, e.g. "your user folder, then Documents, then Claude Home" |
| `{{USER}}` | the person's user folder name |
| `{{DATE}}` | today, `YYYY-MM-DD` |
| `{{PROJECT}}` | folder name of this project |
| `{{PROJECT_DISPLAY}}` | display name |
| `{{PROJECT_ALIASES}}` | comma-separated phrases from intake |
| `{{PROJECT_SOURCES}}` | where the real files live today, one bullet per line |
| `{{INTAKE_NOTES}}` | the six answers, one bullet each |
| `{{PROJECT_LIST}}` | README bullet list of projects |

## Repeat visits

Adding a project later means one `projects/<name>/` folder from the two templates and one new bullet in the README. The
scaffolder does this with `--home <existing> --project <new>`; it skips everything that already exists and reports it.
Because the README is skipped on a repeat visit, add the new project's bullet to the existing README by hand.
