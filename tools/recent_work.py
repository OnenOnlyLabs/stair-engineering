#!/usr/bin/env python3
"""Layer 4 — hand the agent back what it just did.

An agent goes blank at two moments: when a session starts, and when a long conversation is
compacted. Neither is something the user does deliberately, so the loss is invisible from the
outside — a session can fold a dozen times while its owner assumes nothing was cleared.

Recent history is the one thing neither Layer 1 nor Layer 2 can carry. It is not an always-true
rule, and the agent has no reason to go opening a room for it. So it has to be *delivered*, on
every session start and every compaction. That is Layer 4.

Wire it into whatever your harness runs at session start (a hook, a wrapper, a preamble builder)
and print the result into the model's context.

    python3 tools/recent_work.py                      # default: 36h, ~12 lines
    python3 tools/recent_work.py --hours 72 --full    # wider, with commit subjects
    python3 tools/recent_work.py --repo /path/to/repo --ledger CHANGELOG.md

Design notes — each of these was a bug first:
  * Read, don't store. Everything comes from git at call time, so nothing accumulates and the
    record is complete without anyone remembering to write it.
  * Most-recent-first, not most-frequent. Frequency ranks changelogs and notes files at the top
    and pushes the file you just edited off the list.
  * Widen when empty, not when old. A blank block reads as "nothing happened".
  * Fixed read cost. Always a bounded window, so the block stays ~12 lines forever.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Machine-written files. If these are in the list, the change you actually made is buried.
NOISE = re.compile(
    r"(^|/)(logs?|node_modules|vendor|dist|build|target|\.venv|__pycache__)/"
    r"|\.(log|jsonl|lock|pyc|min\.js|map|png|jpe?g|gif|svg|pdf|zip|tar|gz|mp4|mov|webm|mp3|wav)$"
)


def git(repo: Path, *args: str) -> str:
    try:
        # core.quotepath=false: without it git escapes non-ASCII paths as octal, which both
        # renders as gibberish and defeats the extension filters below (the path ends in a quote).
        r = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=false", *args],
                           capture_output=True, text=True, timeout=20)
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def touched(repo: Path, hours: int, skip: set[str]) -> list[str]:
    """Files changed in the window, most recently touched first."""
    out = git(repo, "log", f"--since={hours} hours ago", "--name-only", "--pretty=format:")
    seen: list[str] = []
    for line in out.splitlines():          # git log yields newest commits first
        p = line.strip()
        if p and p not in seen and p not in skip and not NOISE.search(p):
            seen.append(p)
    return seen


def ledger_tail(path: Path, n: int = 4) -> list[str]:
    """Latest headings from a changelog/decision log — the 'why' next to git's 'what'.

    Counts `##` and `###` alike: if later entries are filed one level deeper and you only count
    one of them, today's work is invisible and yesterday's looks like the newest thing you did.
    """
    try:
        heads = [ln.lstrip("#").strip() for ln in path.read_text(encoding="utf-8").splitlines()
                 if ln.startswith(("## ", "### "))]
        return heads[-n:]
    except Exception:
        return []


def pack(items: list[str], width: int = 88) -> list[str]:
    lines, cur = [], ""
    for tok in items:
        if cur and len(cur) + len(tok) + 3 > width:
            lines.append(cur)
            cur = tok
        else:
            cur = f"{cur} · {tok}" if cur else tok
    if cur:
        lines.append(cur)
    return lines


def digest(repo: Path, ledger: Path | None, hours: int = 36,
           top: int = 14, full: bool = False) -> str:
    skip = {str(ledger.relative_to(repo))} if ledger and ledger.is_relative_to(repo) else set()
    items = touched(repo, hours, skip)
    # Widen when the window comes back nearly empty — an agent returning after a break
    # would otherwise be handed a blank block, which reads as "nothing happened".
    for wider in (72, 24 * 7):
        if len(items) >= 5 or wider <= hours:
            break
        items, hours = touched(repo, wider, skip), wider
    heads = ledger_tail(ledger) if ledger else []
    if not items and not heads:
        return ""
    out = [f"🧠 [last {hours}h you touched — most recent first]"]
    out += [f"  {ln}" for ln in pack(items[:top])]
    if len(items) > top:
        out.append(f"  …and {len(items) - top} more")
    out += [f"  📒 {h}" for h in heads]
    # Make a lagging ledger visible. git gives you 'what' for free; 'why' is written by hand,
    # and an unwritten entry is silent — next session it reads as work that never happened.
    last_day = git(repo, "log", "-1", "--pretty=format:%ad", "--date=format:%Y-%m-%d").strip()
    if ledger and items and last_day and not any(last_day in h for h in heads):
        out.append(f"  ⚠ no {last_day} entry in {ledger.name} — today's changes are unrecorded")
    if full:
        out += [f"  · {t}" for t in
                git(repo, "log", f"--since={hours} hours ago",
                    "--pretty=format:%h %s").splitlines()[:40]]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Layer 4: deliver recent work back to the agent.")
    ap.add_argument("--repo", default=".", help="git repository to read (default: cwd)")
    ap.add_argument("--ledger", default="", help="changelog/decision log for the 'why' lines")
    ap.add_argument("--hours", type=int, default=36)
    ap.add_argument("--top", type=int, default=14)
    ap.add_argument("--full", action="store_true", help="also list commit subjects")
    a = ap.parse_args()

    repo = Path(a.repo).resolve()
    if not (repo / ".git").exists() and not git(repo, "rev-parse", "--git-dir"):
        print(f"not a git repository: {repo}", file=sys.stderr)
        return 1
    ledger = (repo / a.ledger).resolve() if a.ledger else None
    text = digest(repo, ledger, a.hours, a.top, a.full)
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
