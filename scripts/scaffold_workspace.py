#!/usr/bin/env python3
"""Create (or extend) a Claude workspace from the templates in ../assets/templates.

Stdlib only. Never overwrites: an existing file or folder is reported as SKIP and left alone.
Everything created is appended to <home>/.setup-log.json so a setup can be undone precisely.

Usage
  python scaffold_workspace.py --home "C:/Users/sam/claude_workspace" \
      --project "weekly-report:Weekly Report:the Monday numbers,weekly spreadsheet" \
      --project "kitchen-remodel:Kitchen Remodel:the kitchen,remodel" \
      --source "weekly-report=Emailed every Monday as an .xlsx attachment" \
      --intake "Use: weekly report summary; kitchen remodel planning" \
      --intake "Files today: Downloads and email" \
      --user-claude-md

  --project   folder-name[:Display Name[:alias1,alias2]]  (repeatable)
  --source    folder-name=where the real files live       (repeatable; one line each)
  --intake    one plain-language line from the interview  (repeatable; becomes the README's "why" section)
  --user-claude-md   also write ~/.claude/CLAUDE.md (appends a titled section if the file exists)
  --dry-run   print what would happen, touch nothing
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # console default is cp1252
    except AttributeError:
        pass

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "assets" / "templates"
TODAY = dt.date.today().isoformat()
FOLDER_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
USER_SECTION_TITLE = "# House rules for Claude"


def click_path(home: Path) -> str:
    """'C:/Users/sam/claude_workspace' -> 'your user folder, then claude_workspace'."""
    try:
        rel = home.relative_to(Path.home()).parts
    except ValueError:
        rel = home.parts[1:]
    if not rel:
        return "your user folder"
    return "your user folder, then " + ", then ".join(rel)


def parse_project(spec: str):
    bits = spec.split(":", 2)
    name = bits[0].strip()
    if not FOLDER_RE.match(name):
        sys.exit(f"ERROR project folder name '{name}' must be lowercase letters, digits and hyphens")
    display = bits[1].strip() if len(bits) > 1 and bits[1].strip() else name.replace("-", " ").title()
    aliases = [a.strip() for a in bits[2].split(",")] if len(bits) > 2 else []
    aliases = [a for a in aliases if a]
    if display.lower() not in [a.lower() for a in aliases]:
        aliases.insert(0, display)
    return name, display, aliases


def fill(template: str, values: dict) -> str:
    out = template
    for k, v in values.items():
        out = out.replace("{{" + k + "}}", v)
    left = re.findall(r"{{([A-Z_]+)}}", out)
    if left:
        sys.exit(f"ERROR unfilled placeholders {sorted(set(left))}; the template and the script disagree")
    return out


class Scaffolder:
    def __init__(self, home: Path, dry: bool):
        self.home = home
        self.dry = dry
        self.created = []
        self.skipped = []

    def mkdir(self, p: Path):
        if p.exists():
            self.skipped.append(str(p))
            return
        if not self.dry:
            p.mkdir(parents=True)
        self.created.append({"path": str(p), "kind": "dir", "ts": TODAY})

    def write(self, p: Path, text: str):
        if p.exists():
            self.skipped.append(str(p))
            return
        if not self.dry:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8", newline="\n")
        self.created.append({"path": str(p), "kind": "file", "ts": TODAY})

    def append_section(self, p: Path, text: str, title: str):
        """For ~/.claude/CLAUDE.md: append a titled section if the file exists and lacks it."""
        if p.exists():
            existing = p.read_text(encoding="utf-8", errors="replace")
            if title in existing:
                self.skipped.append(str(p) + " (section already present)")
                return
            if not self.dry:
                with p.open("a", encoding="utf-8", newline="\n") as fh:
                    fh.write("\n\n" + text)
            self.created.append({"path": str(p), "kind": "appended-section", "title": title, "ts": TODAY})
        else:
            self.write(p, text)

    def save_log(self):
        if self.dry or not self.created:
            return
        log = self.home / ".setup-log.json"
        entries = []
        if log.exists():
            try:
                entries = json.loads(log.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                entries = []
        entries.extend(self.created)
        log.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", required=True)
    ap.add_argument("--project", action="append", default=[])
    ap.add_argument("--source", action="append", default=[])
    ap.add_argument("--intake", action="append", default=[])
    ap.add_argument("--user-claude-md", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not TEMPLATES.is_dir():
        sys.exit(f"ERROR templates folder not found at {TEMPLATES}")
    home = Path(a.home).expanduser().resolve()
    sc = Scaffolder(home, a.dry_run)

    sources = {}
    for s in a.source:
        if "=" not in s:
            sys.exit(f"ERROR --source needs folder-name=text, got '{s}'")
        k, v = s.split("=", 1)
        sources.setdefault(k.strip(), []).append(v.strip())

    projects = [parse_project(p) for p in a.project]
    base = {
        "HOME": home.as_posix(),
        "HOME_CLICK_PATH": click_path(home),
        "USER": Path.home().name,
        "DATE": TODAY,
    }

    # top level
    sc.mkdir(home)
    for d in ("inbox", "projects", "archive"):
        sc.mkdir(home / d)
    sc.write(home / "inbox" / "MOVED.md",
             "# Files moved into this workspace\n\nDate, file, where it came from, where it went. Newest at the bottom.\n")
    sc.write(home / "CLAUDE.md", fill((TEMPLATES / "HOME_CLAUDE.md").read_text(encoding="utf-8"), base))

    # projects
    bullets = []
    for name, display, aliases in projects:
        pdir = home / "projects" / name
        for d in ("files", "archive"):
            sc.mkdir(pdir / d)
        src_lines = sources.get(name) or ["(where the existing files live; edit this line)"]
        src_lines = [l if l.startswith("-") else "- " + l for l in src_lines]
        vals = dict(base, PROJECT=name, PROJECT_DISPLAY=display,
                    PROJECT_ALIASES=", ".join(aliases), PROJECT_SOURCES="\n".join(src_lines))
        sc.write(pdir / "CONTEXT.md", fill((TEMPLATES / "CONTEXT.md").read_text(encoding="utf-8"), vals))
        sc.write(pdir / "PROGRESS.md", fill((TEMPLATES / "PROGRESS.md").read_text(encoding="utf-8"), vals))
        bullets.append(f"- **{display}** : `projects/{name}/` (you call it: {', '.join(aliases)})")

    # README: existing project folders not passed this run still get listed, so a first README is complete
    if (home / "projects").is_dir():
        known = {n for n, _, _ in projects}
        for p in sorted((home / "projects").iterdir()):
            if p.is_dir() and p.name not in known and (p / "CONTEXT.md").exists():
                bullets.append(f"- **{p.name.replace('-', ' ').title()}** : `projects/{p.name}/`")
    intake = "\n".join("- " + l for l in a.intake) if a.intake else "- (intake notes go here)"
    readme_vals = dict(base, PROJECT_LIST="\n".join(bullets) or "- (none yet)", INTAKE_NOTES=intake)
    sc.write(home / "README.md", fill((TEMPLATES / "README.md").read_text(encoding="utf-8"), readme_vals))

    # user-level CLAUDE.md
    if a.user_claude_md:
        text = fill((TEMPLATES / "CLAUDE.md").read_text(encoding="utf-8"), base)
        sc.append_section(Path.home() / ".claude" / "CLAUDE.md", text, USER_SECTION_TITLE)

    sc.save_log()

    verb = "Would create" if a.dry_run else "Created"
    print(f"{verb} {len(sc.created)} item(s) under {home}")
    for c in sc.created:
        print(f"  NEW   {c['path']}" + (f"  [{c['title']}]" if c.get("title") else ""))
    for s in sc.skipped:
        print(f"  SKIP  {s}  (already there, left alone)")
    if not a.dry_run and sc.created:
        print(f"Log: {home / '.setup-log.json'}")
    if projects and (home / "README.md") in [Path(s) for s in sc.skipped]:
        print("\nNote: README.md already existed, so add the new project bullet(s) to it by hand.")
    if bullets and not a.dry_run:
        print("\nNext: open the folder on screen and walk through README.md with the person.")


if __name__ == "__main__":
    main()
