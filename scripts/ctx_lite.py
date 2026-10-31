#!/usr/bin/env python3
"""Tier 2 prompt hook for a Claude Home workspace. Advisory only; never blocks, never raises.

Installed at <home>/tools/ctx_lite.py and wired to Claude Code's UserPromptSubmit hook. Reads the hook JSON on stdin,
finds a project under <home>/projects whose folder name or CONTEXT.md aliases appear in the prompt, and prints a short
brief (path, read order, open bullets from PROGRESS.md) once per project per session. Prints nothing when no project
matches, when the project was already briefed this session, or on any error. Exit code is always 0.

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
    projects = home / "projects"
    if not projects.is_dir():
        return

    best, best_len = None, 0
    for pdir in sorted(projects.iterdir()):
        if not pdir.is_dir():
            continue
        names = [pdir.name, pdir.name.replace("-", " ")] + read_aliases(pdir / "CONTEXT.md")
        for n in names:
            n_l = n.lower()
            if n_l and re.search(r"(?<![a-z0-9])" + re.escape(n_l) + r"(?![a-z0-9])", prompt) and len(n_l) > best_len:
                best, best_len = pdir, len(n_l)
    if best is None:
        return

    state_dir = home / ".state"
    state_file = state_dir / f"{sid}.json"
    briefed = []
    try:
        if state_file.exists():
            briefed = json.loads(state_file.read_text(encoding="utf-8")).get("briefed", [])
    except (OSError, json.JSONDecodeError):
        briefed = []
    if best.name in briefed:
        return

    lines = [f"[ctx-lite] {best.name}",
             f"project: {best.as_posix()}",
             f"read first: {(best / 'CONTEXT.md').as_posix()} then {(best / 'PROGRESS.md').as_posix()}"]
    bullets = state_bullets(best / "PROGRESS.md")
    text = "\n".join(lines + bullets)
    while len(text.encode("utf-8")) > CAP_BYTES and bullets:
        bullets.pop()
        text = "\n".join(lines + bullets + ["(more in PROGRESS.md)"])
    print(text)

    try:
        state_dir.mkdir(exist_ok=True)
        state_file.write_text(json.dumps({"briefed": briefed + [best.name]}), encoding="utf-8")
    except OSError:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:          # a hook must never break the user's turn
        pass
    sys.exit(0)
