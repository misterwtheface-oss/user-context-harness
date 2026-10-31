# Intake questions

The `ctx` handoff lists twelve intake inputs an owner must answer before a context framework is built: session topology,
consumers, vocabulary, context inventory, intent layers, existing checks, boundaries, harness policy, what "done" means,
size budgets, risk posture, and repositories. Most of those collapse for one person on one machine who has never written a
check script. Six plain-language questions cover what still matters. Detect the rest.

Ask two or three per message, never all six at once. Let the person answer in their own words and keep those words.

## Detect, do not ask

| What | How | Feeds |
|---|---|---|
| Operating system and home directory | shell, `$HOME` / `$env:USERPROFILE` | path style in every message, folder names |
| Python available | `python --version`, then `py -3 --version` on Windows | whether the scaffolder runs, whether Tier 2 is offered |
| Existing `~/.claude/CLAUDE.md` or `settings.json` | file exists | append vs create; backup before edit |
| Existing home from an earlier visit | README mentioning this skill, CLAUDE.md naming a home | skip to what is missing |
| Current working directory | `pwd` | if it is Downloads, Desktop, or home root, the problem statement is confirmed |
| Cloud-synced Documents | path contains OneDrive, iCloud, Dropbox | warn once that the home will sync too; usually fine, sometimes unwanted |

## The six questions

### 1. "What do you want Claude to help you with? Name the two or three things you'd actually use it for."
Handoff inputs covered: vocabulary (#3), bodies of work. The answers become the project folder names, in their words.
"my team's weekly report" becomes `weekly-report`, not `reporting-pipeline`. Write both the folder name and the phrase
they used into `CONTEXT.md` under aliases, because the phrase is what they will type next session.

If they name only one thing, create one project. Do not pad the tree with "example" projects; empty folders are clutter to
someone who did not ask for them.

### 2. "Where do the files for that live right now?"
Handoff input: context inventory (#4). Expect Downloads, Desktop, email attachments, a shared drive, a phone. Record each
place. These are candidate sources for per-file moves later, and for the inbox habit. If a place is a shared drive or
email, the file stays there and `CONTEXT.md` simply points to it; the home is a map, not a copy.

### 3. "Is this your only computer? Is it a work machine with rules about what you can install?"
Handoff inputs: session topology (#1), harness policy (#8). One personal machine means absolute paths are fine and Tier 2
is possible. A managed work machine means: do not offer Tier 2, do not edit `settings.json`, keep everything to files and
CLAUDE.md, and say why in one sentence. Two machines means the home should sit in a synced folder if they have one, and
`CLAUDE.md` should avoid machine-specific paths where it can.

### 4. "Is any of this private or confidential? Client data, finances, health, other people's information?"
Handoff input: boundaries (#7). A yes creates a `private/` folder inside the relevant project with a one-line README
saying Claude reads it only when asked, and adds a house rule not to summarise its contents into other documents. If the
home is in a cloud-synced folder and they say yes, raise that in the same breath and offer the user-folder location
instead.

### 5. "When you come back tomorrow, what would you want Claude to already know?"
Handoff input: what "done" means (#9). The answer shapes the `PROGRESS.md` headings and the wrap-up habit. Common answers:
"where we left off" (the default state section), "what I still have to do" (open items), "what I decided" (a decisions
list). Add a heading only for what they said; the template has the first two and a session log.

### 6. "Do you want Claude to check things automatically, or just follow written rules for now?"
Handoff input: risk posture (#11). Ask this only when Python is present and the machine is theirs. Explain Tier 2 in one
paragraph: a small script runs before each message you send, notices which project you named, and shows Claude that
project's open items without anyone opening a file. It never blocks anything. Default to "written rules for now" if they
hesitate. The hook can be added in a later session; removing one that confused them costs more trust than it saved.

## Inputs this skill deliberately drops

- Consumers other than Claude Code (#2): one person, one tool. Mention `AGENTS.md` only if they say they also use Codex.
- Existing deterministic checks (#6): a novice has none. Tier 2's hook is the first and only one.
- Size budgets (#10): PROGRESS.md gets a soft note in the template ("if this gets long, move old items to archive").
  No enforcement.
- Repositories (#12): no git in the first session unless they already have a repo. Introducing version control to someone
  learning folders is two lessons at once.

## Recording the answers

Write a short section titled "Why this is set up this way" at the bottom of the workspace README: one line per question,
dated. This is the novice-sized equivalent of the handoff's "Intake, <date>" entry in `DESIGN.md`. It lets the next
session, or a helper looking over their shoulder, understand the choices without redoing the interview.
