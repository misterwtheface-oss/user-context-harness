# Workspace layout

The workspace is deliberately small: five things at the top level, two files per project. The handoff's greenfield skeleton has
a router, a state doc, decisions, changelog, session log, and archive per project. For a novice, the router and state doc
are enough; decisions and the session log fold into `PROGRESS.md` as sections, and the changelog is dropped. Grow it when
they ask why something was decided, not before.

## A map, not a container

The workspace holds notes about the work, not necessarily the work. A project whose files live in a repo, a shared drive
or an email thread keeps them there; its `CONTEXT.md` points at that place and Claude works in it. Only projects with no
home of their own (a kitchen remodel, a one-off report) use the project's `files/` folder. Never move a repo or a shared
drive's files into the workspace, and never add personal notes files inside a team repo.

## Where it goes

Propose one location in a single line rather than making it a decision:

| Default | Windows | Mac | Linux |
|---|---|---|---|
| User folder | `C:\Users\<name>\claude_workspace` | `/Users/<name>/claude_workspace` | `/home/<name>/claude_workspace` |

Short paths, not cloud-synced, and on a work laptop not inside a OneDrive-redirected Documents folder. Offer
`Documents\Claude workspace` instead only when the person says they find everything through Documents; if that folder is
cloud-synced and intake raised privacy, say it will sync. If they already keep a folder for this kind of thing, use it.

## The tree

```
claude_workspace/
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
- **CLAUDE.md in the workspace** carries rules that apply when Claude is working inside it: work happens where the
  project's `CONTEXT.md` says, `PROGRESS.md` is updated before the session ends, moves are listed first. Claude Code reads
  it automatically when the working directory is inside the workspace.
- **`~/.claude/CLAUDE.md`** (user level, outside the workspace) carries what must hold wherever Claude is started (a repo,
  Downloads, the Desktop): the toolbox block from `toolcheck.py`, where the workspace is, where new files go, that
  locations are reported in plain words.
  This is the file that stops the original problem from recurring.
- **CONTEXT.md** is the router. Aliases first, so a prompt-matching hook or a reading Claude can resolve "the Monday
  numbers" to this folder. Then where the real files live (which may be an email inbox or a shared drive, not this folder).
  Then read order: PROGRESS.md, then whatever else matters.
- **PROGRESS.md** is the state. Bullets under headings so a hook or a human can pull them. The template has "Where things
  stand", "Waiting on you", "Open items", "Decisions", and "Session log". Add headings only if intake asked for them.
- **files/** holds what Claude produces for projects with no home of their own, and what the person moves in.
- **archive/** at both levels exists so nothing is deleted. Old PROGRESS items move to `project/archive/<date>.md`;
  finished projects move whole to the workspace's `archive/`.

## Naming rules

- Folder names: lowercase, hyphens, from the person's own phrase. `weekly-report`, `kitchen-remodel`, `mom-medical`.
- Display names in README and CONTEXT keep their capitalisation: "Weekly Report".
- Files: `YYYY-MM-DD short description.ext`. No `final`, no `v2`; the date is the version.
- Never rename a file the person brought in. Log it as-is in `MOVED.md`.

## Templates and placeholders

`assets/templates/` holds `CLAUDE.md` (user level), `HOME_CLAUDE.md` (inside the workspace), `README.md`, `CONTEXT.md`, and
`PROGRESS.md`. Placeholders the scaffolder fills, and that must be filled by hand when Python is absent:

| Placeholder | Value |
|---|---|
| `{{HOME}}` | full path to the workspace |
| `{{HOME_CLICK_PATH}}` | click path in words, e.g. "your user folder, then claude_workspace" |
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
