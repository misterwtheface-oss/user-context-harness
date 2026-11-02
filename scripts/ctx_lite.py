#!/usr/bin/env python3
"""Tier 2 prompt hook for a Claude workspace. Advisory only; never blocks, never raises.

Installed at <home>/tools/ctx_lite.py and wired to Claude Code's UserPromptSubmit hook. Reads the hook JSON on stdin,
finds a project under <home>/projects whose folder name or CONTEXT.md aliases appear in the prompt, and prints a short
brief (path, read order, open bullets from PROGRESS.md) once per project per session. Prints nothing when no project
matches, when the project was already briefed this session, or on any error. Exit code is always 0.

Skill vault (optional): skills kept in <home>/skill_vault/<skill>/SKILL.md are not loaded by Claude Code at startup. When a
prompt names a vaulted skill or enough of its `keywords:` (frontmatter), the hook prints a pointer to that SKILL.md, once
per skill per session, at most MAX_SKILLS per prompt. A keyword hit scores its word count; the threshold is SKILL_THRESHOLD.

Test by hand:
  echo '{"session_id":"t1","prompt":"lets do the weekly report"}' | python ctx_lite.py
"""
import json
import re
import sys
from pathlib import Path

CAP_BYTES = 3 * 1024          # brief stays small so it never crowds the prompt
MAX_BULLETS = 12
STATE_HEADINGS = ("waiting on you", "open items")
SKILL_THRESHOLD = 2       # one two-word phrase, or two single words, or the skill name
MAX_SKILLS = 3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def read_aliases(ctx: Path) -> list:
    try:
        for line in ctx.read_text(encoding="utf-8", errors="replace").splitlines()[:15]:
            if line.lower().startswith("aliases:"):
                return [a.strip() for a in line.split(":", 1)[1].split(",") if a.strip()]
    except OSError:
        pass
    return []


def state_bullets(progress: Path) -> list:
    out = []
    try:
        lines = progress.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out
    active = False
    for line in lines:
        if line.startswith("#"):
            active = line.lstrip("#").strip().lower() in STATE_HEADINGS
            if active:
                out.append(line.strip())
            continue
        if active and line.lstrip().startswith(("-", "*")):
            out.append(line.rstrip())
            if sum(1 for l in out if not l.startswith("#")) >= MAX_BULLETS:
                break
    return out


def phrase_in(phrase: str, prompt: str) -> bool:
    body = re.escape(phrase.lower()).replace(" ", r"[\s_-]+")
    return bool(phrase) and re.search(r"(?<![a-z0-9])" + body + r"(?![a-z0-9])", prompt) is not None


def skill_frontmatter(path: Path) -> dict:
    fm = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return fm
    if not lines or lines[0].strip() != "---":
        return fm
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip().lower()] = v.strip().strip('"\'')
    return fm


def skill_hits(home: Path, prompt: str, shown: list) -> list:
    vault = home / "skill_vault"
    hits = []
    if not vault.is_dir():
        return hits
    for sk in sorted(vault.glob("*/SKILL.md")):
        fm = skill_frontmatter(sk)
        name = fm.get("name") or sk.parent.name
        if name in shown:
            continue
        kws = [k.strip().strip('"\'') for k in fm.get("keywords", "").strip("[]").split(",") if k.strip()]
        score = sum(max(1, len(k.split())) for k in kws if not k.endswith("!") and phrase_in(k, prompt))
        if any(phrase_in(k.rstrip("!"), prompt) for k in kws if k.endswith("!")):
            score = max(score, SKILL_THRESHOLD)   # "word!" = strong keyword, enough on its own
        if phrase_in(name, prompt) or phrase_in(name.replace("-", " "), prompt):
            score = max(score, SKILL_THRESHOLD)
        if score >= SKILL_THRESHOLD:
            desc = re.split(r"(?<=[.!?])\s", fm.get("description", ""), maxsplit=1)[0][:160]
            hits.append((score, name, sk.as_posix(), desc))
    hits.sort(key=lambda h: (-h[0], h[1]))
    return hits[:MAX_SKILLS]


def project_brief(home: Path, prompt: str, briefed: list):
    projects = home / "projects"
    if not projects.is_dir():
        return None, None
    best, best_len = None, 0
    for pdir in sorted(projects.iterdir()):
        if not pdir.is_dir():
            continue
        names = [pdir.name, pdir.name.replace("-", " ")] + read_aliases(pdir / "CONTEXT.md")
        for n in names:
            n_l = n.lower()
            if n_l and re.search(r"(?<![a-z0-9])" + re.escape(n_l) + r"(?![a-z0-9])", prompt) and len(n_l) > best_len:
                best, best_len = pdir, len(n_l)
    if best is None or best.name in briefed:
        return None, None
    lines = [f"[ctx-lite] {best.name}",
             f"project: {best.as_posix()}",
             f"read first: {(best / 'CONTEXT.md').as_posix()} then {(best / 'PROGRESS.md').as_posix()}"]
    bullets = state_bullets(best / "PROGRESS.md")
    text = "\n".join(lines + bullets)
    while len(text.encode("utf-8")) > CAP_BYTES and bullets:
        bullets.pop()
        text = "\n".join(lines + bullets + ["(more in PROGRESS.md)"])
    return best.name, text


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return
    prompt = str(payload.get("prompt", "")).lower()
    sid = re.sub(r"[^A-Za-z0-9_-]", "_", str(payload.get("session_id", "nosession")))
    if not prompt.strip():
        return

    home = Path(__file__).resolve().parent.parent      # tools/ sits directly under the home
    state_dir = home / ".state"
    state_file = state_dir / f"{sid}.json"
    state = {}
    try:
        if state_file.exists():
            state = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    briefed, shown = state.get("briefed", []), state.get("skills_shown", [])

    out = []
    name, text = project_brief(home, prompt, briefed)
    if name:
        out.append(text)
        briefed.append(name)
    hits = skill_hits(home, prompt, shown)
    if hits:
        out.append("[ctx-lite] skill vault match (not loaded at startup; read the SKILL.md first and follow it):")
        out += [f"- {n} (score {s}): {p} - {d}" for s, n, p, d in hits]
        shown += [n for _, n, _, _ in hits]
    if not out:
        return
    print("\n".join(out))
    try:
        state_dir.mkdir(exist_ok=True)
        state_file.write_text(json.dumps({"briefed": briefed, "skills_shown": shown}), encoding="utf-8")
    except OSError:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:          # a hook must never break the user's turn
        pass
    sys.exit(0)
