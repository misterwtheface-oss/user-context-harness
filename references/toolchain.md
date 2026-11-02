# Toolchain: what Claude needs on the machine, and how to get it there

A fresh machine makes Claude slow in ways the person reads as "Claude is bad at this". Without ripgrep it searches by
reading files one at a time. Without Python it does data work by hand in the shell and gets quoting wrong. Without git a
bad edit cannot be undone. Without jq it reads a whole JSON file to find one value. Installing six small tools in the first
session fixes all of that. Do it before building any folder structure, because the person feels the difference on their
first real task.

The list lives in `assets/toolchain.json` (one entry per tool: tier, why, install ids per package manager, and the hint
line Claude gets). `scripts/toolcheck.py` reads it. Edit the JSON to add a tool; do not repeat the list anywhere else.

## Tiers

| Tier | Tools | When to offer |
|---|---|---|
| essential | git, Python 3, Node.js LTS, ripgrep, jq, GitHub CLI | always, as one list, missing ones only |
| recommended | fd, uv, pandoc | in the same message, as a second short list the person can skip |
| role | Azure CLI, AWS CLI, Docker, .NET SDK, JDK | only when intake question 1 names that kind of work (`--roles azure,java`) |

Skip `gh` from the offer when intake says they never touch GitHub; skip `pandoc` when they never handle Word files. Their
work decides, not the list.

## Run order

1. `python scripts/toolcheck.py [--roles ...]`. If Python itself is missing, see "No Python yet" below.
2. Show the person the MISSING rows: tool name and the one-sentence why from the output. Not the commands; they read
   outcomes. Ask one yes for the list. They can strike items.
3. Run the install commands the script printed, one tool at a time, and report each result in a word (installed / failed
   and why).
4. Tell them a new Claude Code session is needed for new tools to be found (the running session keeps the old PATH). If
   they want to stay in this session, check a new tool by its full install path instead.
5. In the new session: re-run `toolcheck.py`, then `toolcheck.py --write-claude-md`. This writes a short "Tools on this
   machine" block into `~/.claude/CLAUDE.md` between markers, so every later session knows which tools exist without
   probing. Only the marked block is replaced on later runs; a dated backup is made the first time each day.

## Install routes, by machine

The script picks the route; this is what it does and why.

| Machine | Route | Admin needed |
|---|---|---|
| Windows, admin | winget | sometimes (it asks) |
| Windows, no admin (typical work laptop) | Scoop if present, else winget with `--scope user` | no |
| Windows, no admin, winget off by policy | set up Scoop first (user folder only) | no |
| Mac | Homebrew (installing brew itself needs admin once) | once |
| Linux | apt or dnf | yes (sudo) |
| none of the above work | IT request list | n/a |

On a work machine with winget `--scope user`, some packages (Node.js, GitHub CLI) only install machine-wide and Windows
asks for admin. If that prompt appears, cancel it and use Scoop for that tool. Scoop setup is one PowerShell line (the
script prints it) and installs nothing outside the user folder.

## Work machines: stay inside the rules

- Ask intake question 3 first. If they say installing software is not allowed at all, skip installs and print the IT
  request list (`toolcheck.py` shows it when no route exists; it is also the MISSING rows with their why lines).
- Never work around a block: no disabling security software, no elevation tricks, no portable binaries dropped into
  system folders, no changing execution policy beyond `CurrentUser` and only for Scoop with their yes.
- A tool the company already ships (a managed Git, a company Python) counts as present. Do not install a second copy.
- If a corporate proxy breaks installs (timeouts, certificate errors), stop and say so; that is an IT ticket, not a fix.

## No Python yet

The checker needs Python, so on a bare machine install Python through the route first, then run the script. To see what
exists before that, one line per OS:

```
# Windows (PowerShell)
'git','python','py','node','rg','jq','gh' | % { "{0,-7} {1}" -f $_, (Get-Command $_ -ErrorAction SilentlyContinue).Source }
# Mac / Linux
for t in git python3 node rg jq gh; do printf '%-8s %s\n' "$t" "$(command -v $t)"; done
```

On Windows, a `python` path under `WindowsApps` is the Microsoft Store shortcut, not Python: treat it as missing (the
script already does).

## Optional: fewer permission prompts

Once tools are in, Claude Code still asks before every shell command. Offer, as a separate yes, to add read-only commands
to the allow list in `~/.claude/settings.json` (back it up first; merge, never replace):

```json
{ "permissions": { "allow": ["Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(rg:*)", "Bash(fd:*)",
  "Bash(jq:*)", "Bash(gh pr view:*)", "Bash(gh pr list:*)"] } }
```

Read-only only; nothing that writes, pushes or deletes. On a managed machine where settings are policy-controlled, skip
it and say why in one sentence.
