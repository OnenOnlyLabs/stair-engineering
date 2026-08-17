#!/usr/bin/env python3
"""Layer 0 — keep each chat's own note, and keep the boring half of it automatic.

Layer 0 is the layer people need and never write: one file per chat thread, holding what THIS
thread decided, ruled out, and where it stopped. It cannot live on Layer 1 (every other thread
would read it on every call) and it is not knowledge (it expires when the task ships).

The reason it goes unwritten is not that people disagree with it — it is that writing it is a
chore at exactly the moment you are trying to finish something else. So split it in two:

    mechanical  which files this thread touched, when it was last active   <- this tool, automatic
    judgment    what was decided, what was ruled out, what is still open   <- the agent writes it

The mechanical half needs no discipline, and once the file exists and is handed back at session
start, the judgment half tends to get written — an empty heading in front of you is a much
stronger prompt than a rule you have to remember.

    python3 tools/chat_note.py --note auth-refactor --start
        create the note if needed, stamp a new session, and print it (feed this to the agent)

    python3 tools/chat_note.py --note auth-refactor --touch
        refresh the mechanical block with files changed since the last stamp. Safe to run often —
        wire it to whatever fires when a turn ends.

    python3 tools/chat_note.py --note auth-refactor --append "ruled out: session cookies, SSR breaks"
        one line of judgment, appended under Decisions.

    python3 tools/chat_note.py --list

Only the block between the AUTO markers is ever rewritten. Everything the agent or you write
outside it is left alone.

Works the same on macOS, Linux and Windows: no shell, stdlib only, output forced to UTF-8
(a Windows console defaults to a legacy code page and would otherwise drop the whole block).
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path

BEGIN = "<!-- LAYER0:AUTO:BEGIN — rewritten by tools/chat_note.py; write your own notes outside -->"
END = "<!-- LAYER0:AUTO:END -->"
STAMP = re.compile(r"^<!-- last-stamp: (.+?) -->$", re.M)

NOISE = re.compile(
    r"(^|/)(logs?|node_modules|vendor|dist|build|target|\.venv|__pycache__)/"
    r"|\.(log|jsonl|lock|pyc|min\.js|map|png|jpe?g|gif|svg|pdf|zip|tar|gz|mp4|mov|webm|mp3|wav)$"
)

SKELETON = """# {title}

{begin}
{end}

## Goal
_What this thread is for. One or two lines._

## Decisions
_What was settled, and what was ruled out and why. Ruled-out matters most — without it the next
session re-proposes the thing you already rejected._

## Open
_Where it stopped. What the next person (or the next you) picks up first._

---
When something here outlives this task, promote it: a fact to a Layer 2 room, a rule to Layer 1.
Then delete it from this file. Layer 0 is allowed to be thrown away; that is the point.
"""


def git(repo: Path, *args: str) -> str:
    try:
        # core.quotepath=false: git otherwise escapes non-ASCII paths as octal, which renders as
        # gibberish and also defeats the extension filters (the path then ends in a quote).
        r = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=false", *args],
                           capture_output=True, text=True, timeout=20)
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def changed_since(repo: Path, since: str) -> list[str]:
    """Files committed since a timestamp, most recent first."""
    out = git(repo, "log", f"--since={since}", "--name-only", "--pretty=format:")
    seen: list[str] = []
    for line in out.splitlines():
        p = line.strip()
        if p and p not in seen and not NOISE.search(p):
            seen.append(p)
    return seen


def now() -> str:
    return dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")


def note_path(root: Path, name: str) -> Path:
    safe = re.sub(r"[^\w.-]+", "-", name).strip("-") or "chat"
    return root / "stairs" / "layer0" / f"{safe}.md"


def read_stamp(text: str) -> str | None:
    m = STAMP.search(text)
    return m.group(1) if m else None


def auto_block(repo: Path, since: str | None, sessions: int) -> str:
    """The mechanical half. `since` None means 'first stamp, look back a day'."""
    files = changed_since(repo, since or "36 hours ago")
    lines = [BEGIN, f"<!-- last-stamp: {now()} -->", "",
             f"**This thread** · sessions: {sessions} · last active: {now()}"]
    if files:
        shown = files[:12]
        lines.append("**Touched since last session:** " + " · ".join(shown)
                     + (f" …and {len(files) - len(shown)} more" if len(files) > len(shown) else ""))
    else:
        lines.append("**Touched since last session:** nothing committed yet")
    lines += ["", END]
    return "\n".join(lines)


def splice(text: str, block: str) -> str:
    if BEGIN in text and END in text:
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        return head + block + tail
    return block + "\n\n" + text


def count_sessions(text: str) -> int:
    m = re.search(r"sessions: (\d+)", text)
    return int(m.group(1)) if m else 0


def cmd_start(repo: Path, path: Path, title: str) -> str:
    fresh = not path.exists()
    if fresh:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = SKELETON.format(title=title, begin=BEGIN, end=END)
    else:
        text = path.read_text(encoding="utf-8")
    block = auto_block(repo, read_stamp(text), count_sessions(text) + 1)
    text = splice(text, block)
    path.write_text(text, encoding="utf-8")
    return text


def cmd_touch(repo: Path, path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    # Same session — keep the session count, only refresh what changed.
    text = splice(text, auto_block(repo, read_stamp(text), max(count_sessions(text), 1)))
    path.write_text(text, encoding="utf-8")
    return text


def cmd_append(path: Path, line: str) -> None:
    if not path.exists():
        raise SystemExit(f"no note yet: {path} — run --start first")
    text = path.read_text(encoding="utf-8")
    stamp = dt.datetime.now().astimezone().strftime("%m-%d %H:%M")
    if "\n## Decisions\n" in text:
        head, tail = text.split("\n## Decisions\n", 1)
        text = f"{head}\n## Decisions\n- {stamp} — {line}\n{tail}"
    else:
        text = text.rstrip() + f"\n\n## Decisions\n- {stamp} — {line}\n"
    path.write_text(text, encoding="utf-8")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Layer 0: one note per chat, half of it automatic.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--note", default="", help="name of this chat thread")
    ap.add_argument("--title", default="", help="heading for a new note (defaults to --note)")
    ap.add_argument("--start", action="store_true", help="create/stamp and print the note")
    ap.add_argument("--touch", action="store_true", help="refresh the automatic block only")
    ap.add_argument("--append", default="", help="add one line under Decisions")
    ap.add_argument("--list", action="store_true", help="list existing notes")
    a = ap.parse_args()

    repo = Path(a.repo).resolve()
    if a.list:
        d = repo / "stairs" / "layer0"
        for f in sorted(d.glob("*.md")) if d.exists() else []:
            head = f.read_text(encoding="utf-8").splitlines()[:1]
            print(f"{f.stem:<28} {head[0].lstrip('# ') if head else ''}")
        return 0

    if not a.note:
        ap.error("--note is required (except with --list)")
    if not shutil.which("git"):
        print("git is not on PATH — the automatic half reads history from git", file=sys.stderr)
    path = note_path(repo, a.note)

    if a.append:
        cmd_append(path, a.append)
        print(f"appended to {path}")
        return 0
    if a.touch:
        out = cmd_touch(repo, path)
        if not out:
            print(f"no note yet: {path} — run --start first", file=sys.stderr)
            return 1
        return 0
    if a.start:
        print(cmd_start(repo, path, a.title or a.note))
        return 0

    if path.exists():
        print(path.read_text(encoding="utf-8"))
        return 0
    print(f"no note yet: {path} — run --start first", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
