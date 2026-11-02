#!/usr/bin/env python3
"""Check which tools Claude Code works best with are on this machine, and print an install plan for the missing ones.

Stdlib only. Reads ../assets/toolchain.json. Never installs anything itself: it prints the exact commands so Claude can
show the list and run them after a yes. Re-run after installing to confirm and to refresh the CLAUDE.md toolbox block.

Usage
  python toolcheck.py                      report + install plan (essential and recommended tiers)
  python toolcheck.py --roles azure,java   also check role tools whose roles match intake (see toolchain.json)
  python toolcheck.py --json               machine-readable result
  python toolcheck.py --claude-md          print the "Tools on this machine" block for ~/.claude/CLAUDE.md
  python toolcheck.py --write-claude-md    write that block into ~/.claude/CLAUDE.md between markers (backup first);
                                           only the marked block is ever replaced, the rest of the file is untouched
Exit code: 0 when every essential tool is present, 1 otherwise.
"""
import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # console default is cp1252
    except AttributeError:
        pass

HERE = Path(__file__).resolve().parent
MANIFEST = HERE.parent / "assets" / "toolchain.json"
BEGIN = "<!-- toolbox:begin (written by user-context-harness toolcheck.py; re-run it to refresh) -->"
END = "<!-- toolbox:end -->"


def os_key():
    s = platform.system().lower()
    return "windows" if s == "windows" else "mac" if s == "darwin" else "linux"


def is_admin():
    try:
        if os_key() == "windows":
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        if os.geteuid() == 0:
            return True
        return subprocess.run(["sudo", "-n", "true"], capture_output=True, timeout=5).returncode == 0
    except Exception:
        return False


def winget_blocked():
    """Group policy can switch winget off on managed machines."""
    if os_key() != "windows":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\AppInstaller") as k:
            return winreg.QueryValueEx(k, "EnableAppInstaller")[0] == 0
    except OSError:
        return False


def probe(tool):
    """First binary that exists AND answers its version flag. The Windows Store 'python' stub exists but does not answer."""
    for b in tool["bins"]:
        path = shutil.which(b)
        if not path:
            continue
        try:
            r = subprocess.run([path] + tool["version"], capture_output=True, text=True, timeout=15,
                               encoding="utf-8", errors="replace")
        except (OSError, subprocess.TimeoutExpired):
            continue
        out = (r.stdout or r.stderr or "").strip().splitlines()
        if r.returncode == 0 and out:
            return {"bin": b, "path": path, "version": out[0][:80]}
    return None


def environment(manifest):
    osk = os_key()
    managers = [m for m, spec in manifest["managers"].items() if spec["os"] == osk and shutil.which(m)]
    if "winget" in managers and winget_blocked():
        managers.remove("winget")
    return {
        "os": osk,
        "admin": is_admin(),
        "work_domain": os.environ.get("USERDNSDOMAIN") or None,  # set on domain-joined (usually work) Windows machines
        "managers": managers,
        "winget_blocked_by_policy": winget_blocked(),
    }


def pick_route(env, manifest):
    """Which package manager to use. No admin -> a route that never needs it."""
    order = {"windows": ["winget", "scoop", "choco"] if env["admin"] else ["scoop", "winget"],
             "mac": ["brew"], "linux": ["apt", "dnf"] if env["admin"] else []}[env["os"]]
    for m in order:
        if m in env["managers"]:
            return m
    if env["os"] == "windows":
        return "scoop-bootstrap"  # scoop installs without admin; offer to set it up first
    if env["os"] == "mac":
        return "brew-bootstrap"
    return None


def install_cmd(manager, pkg, manifest, env):
    spec = manifest["managers"][manager]
    cmd = spec["cmd"].format(id=pkg)
    if manager == "winget" and not env["admin"]:
        cmd += " " + spec["user_scope"]
    if manager == "scoop" and "/" in pkg:
        cmd = f"scoop bucket add {pkg.split('/')[0]}; " + cmd
    return cmd


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roles", default="", help="comma-separated roles from intake, e.g. azure,java")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--claude-md", action="store_true")
    ap.add_argument("--write-claude-md", action="store_true")
    a = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    roles = {r.strip().lower() for r in a.roles.split(",") if r.strip()}
    tools = [t for t in manifest["tools"]
             if t["tier"] != "role" or roles & set(t.get("roles", []))]
    env = environment(manifest)
    route = pick_route(env, manifest)
    mgr = route if route in manifest["managers"] else ("scoop" if route == "scoop-bootstrap" else
                                                        "brew" if route == "brew-bootstrap" else None)

    rows = []
    for t in tools:
        hit = probe(t)
        pkg = t["install"].get(mgr) if mgr else None
        rows.append({"key": t["key"], "name": t["name"], "tier": t["tier"], "why": t["why"],
                     "found": hit, "package": pkg,
                     "install": install_cmd(mgr, pkg, manifest, env) if (not hit and pkg) else None,
                     "hint": t["claude_hint"].replace("{bin}", hit["bin"]) if hit else None})

    missing_essential = [r for r in rows if not r["found"] and r["tier"] == "essential"]

    if a.claude_md or a.write_claude_md:
        block = render_block(rows, env)
        if a.write_claude_md:
            write_block(block)
        else:
            print(block)
        return 0 if not missing_essential else 1

    if a.json:
        print(json.dumps({"env": env, "route": route, "tools": rows}, indent=2))
        return 0 if not missing_essential else 1

    print(f"Machine: {env['os']}, admin rights: {'yes' if env['admin'] else 'no'}"
          + (f", work domain: {env['work_domain']}" if env["work_domain"] else "")
          + f", package managers: {', '.join(env['managers']) or 'none'}"
          + (" (winget switched off by policy)" if env["winget_blocked_by_policy"] else ""))
    print()
    for r in rows:
        state = "OK     " if r["found"] else "MISSING"
        detail = f"{r['found']['version']}" if r["found"] else r["why"]
        print(f"  {state} {r['name']:<16} [{r['tier']}] {detail}")

    todo = [r for r in rows if not r["found"]]
    if not todo:
        print("\nEverything is in place.")
        return 0
    print()
    if route == "scoop-bootstrap":
        print("Route: Scoop (installs into your user folder, no admin needed). Set it up first, in PowerShell:")
        print("  " + manifest["managers"]["scoop"]["bootstrap"])
    elif route == "brew-bootstrap":
        print("Route: Homebrew is not installed; installing it needs admin once (https://brew.sh).")
    elif route:
        spec = manifest["managers"][route]
        print(f"Route: {route} ({spec['note']})")
    else:
        print("Route: none without admin rights on this machine. Send the IT request list below.")
    for r in todo:
        if r["install"]:
            print(f"  {r['name']:<16} {r['install']}")
    no_pkg = [r for r in todo if not r["install"]]
    if no_pkg or not route:
        print("\nIT request list (tool, why it is needed):")
        for r in (todo if not route else no_pkg):
            print(f"  - {r['name']}: {r['why']}")
    print("\nAfter installing: start a new Claude Code session so the new tools are on its PATH, then re-run this check.")
    return 0 if not missing_essential else 1


def render_block(rows, env):
    have = [r for r in rows if r["found"]]
    lacking = [r["name"] for r in rows if not r["found"]]
    lines = [BEGIN, f"## Tools on this machine (checked {dt.date.today().isoformat()}, {env['os']})", ""]
    lines += [f"- {r['hint']}" for r in have]
    if lacking:
        lines.append(f"- Not installed: {', '.join(lacking)}. Do not assume them; say so if one would help.")
    lines.append(END)
    return "\n".join(lines)


def write_block(block):
    p = Path.home() / ".claude" / "CLAUDE.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    if old:
        bak = p.with_name(f"CLAUDE.md.bak-{dt.date.today().isoformat()}")
        if not bak.exists():
            bak.write_text(old, encoding="utf-8")
    if BEGIN in old and END in old:
        head, rest = old.split(BEGIN, 1)
        new = head + block + rest.split(END, 1)[1]
    else:
        new = (old.rstrip() + "\n\n" if old.strip() else "") + block + "\n"
    p.write_text(new, encoding="utf-8", newline="\n")
    print(f"Wrote the toolbox block to {p}")


if __name__ == "__main__":
    sys.exit(main())
