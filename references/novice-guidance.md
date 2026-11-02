# Talking to someone who has never built a folder tree

The person this skill serves is competent. They run meetings, close deals, raise children, file taxes. They have simply
never needed to think about where a file lives beyond "I saved it" and "it's in Downloads". Every instruction below
follows from one fact: a path is a sentence in a language they do not read yet.

## Calibrate first

Not everyone is new to computers. Someone on a fresh work laptop who writes code already knows folders; what they lack is
the toolchain and the house rules. Read the first message: if they use words like repo, terminal, PATH or a language name,
give them the tool list with versions and the commands, skip click paths and the on-screen folder opening, and keep the
pace brisk. Everything below is for the newcomer; use as much of it as the person needs.

For a newcomer, tools get the same treatment as folders: name the tool and say in one sentence what it lets Claude do for
them ("ripgrep lets me search all your files in a blink"). Never show the install commands unless asked.

## Describe every location twice

Once as a full path in a code block, because it is exact and clickable in Claude Code:

```
C:\Users\sam\claude_workspace\projects\weekly-report\files
```

Once as a click path in words, because that is how they will actually get there:

"Open your user folder, then claude_workspace, then projects, then weekly-report, then files."

Never describe a location with only a relative path, a tilde, or `cd`. `~/claude_workspace` means nothing to them, and
`../` is a riddle.

## Open the folder on screen at the moment it matters

After creating the workspace, open it in their file browser and ask them to confirm they see it. Windows: `explorer.exe "<path>"`.
Mac: `open "<path>"`. Linux: `xdg-open "<path>"`. A folder they have seen is a folder that exists to them; a path in chat
is not. Do this once for the workspace and once for the first project. Do not do it for every file.

Follow it with the pin: on Windows, right-click the folder and choose "Pin to Quick access"; on Mac, drag it into the
Finder sidebar. Pinning is the single highest-leverage thing in the session because it makes the workspace as reachable as
Downloads.

## One idea per message, two or three questions at most

Intake is six questions. Spread them over three messages. Verification shows one tree and one list of rules; do not also
explain progressive disclosure or why CLAUDE.md is read at start. The explanations belong in the README, where they can be
read later, slowly.

## Jargon rule

Any technical word gets a one-line gloss the first time, or does not appear. Working glosses:

| Word | Say instead or alongside |
|---|---|
| directory | folder |
| root / home directory | "your user folder, the one named after you" |
| CLI / terminal | "the Claude Code window" |
| repo / repository | avoid in session one |
| hook | "a small script that runs before each message" |
| CLAUDE.md | "the house-rules file Claude reads every time it starts" |
| memory | "notes Claude keeps for itself between sessions" |
| path | "the address of a file" |

## Their words win

Folder names come from how they described the work. If they said "the Monday numbers", the project is `monday-numbers`
and the alias list in `CONTEXT.md` includes "Monday numbers" and "weekly spreadsheet" if they used both. Lowercase with
hyphens is fine; explain once that spaces and capitals in folder names cause trouble in some tools, which is why the
display name in the README keeps their capitalisation and the folder does not.

## Naming files

Teach one rule, by example rather than lecture: date first, then words, no "final" or "v2".

```
2026-10-31 weekly summary.md
```

sorts itself and never needs renaming. Put it in the README; say it aloud once.

## Moves are a list, then a yes, then a log

When their existing files come up, present a table: file, where it is, where it would go, why. Wait. After a yes, move
those and only those, and append each line to `inbox/MOVED.md`:

```
2026-10-31  Q4 sales final FINAL v2.xlsx   from Downloads   to projects/weekly-report/files
```

Say "I moved four files; the list of where each one went is in the inbox folder, in a file called MOVED." That sentence
is what lets them trust the next move.

## Do not fix what they did not ask about

Downloads with nine hundred files is not the problem being solved. Desktop covered in screenshots is not either. The
workspace is additive. If they ask for help tidying later, that is a different conversation with its own listing-and-yes
cycle.

## Close with the habit, not the architecture

The last message of the session names one behaviour: next time, start by saying which project you are working on. Then
Claude opens that project's two files first. Everything else the structure does is invisible to them, which is the point.
