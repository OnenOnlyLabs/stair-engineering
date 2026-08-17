#!/usr/bin/env python3
"""stair_load — print what an agent should read *right now*, and nothing more.

Stair Engineering in one sentence: what you always read must be thin; deep knowledge lives up the stairs.

    Layer 1  (always)      stairs/layer1/MEMORY.md         one page, injected on every call
    Layer 2  (on demand)   stairs/layer2/<room>.md          knowledge files, opened by "room" address
    Layer 3  (identity)    stairs/layer3/<agent>.md         persona / role card, per agent

Usage
    python3 tools/stair_load.py                      # Layer 1 only  (paste into your system prompt)
    python3 tools/stair_load.py --agent researcher   # Layer 1 + that agent's Layer 3 card
    python3 tools/stair_load.py --room 201           # Layer 1 + the TOC of room 201 (not the body)
    python3 tools/stair_load.py --room 201 --section "indexing"   # + only that section's body
    python3 tools/stair_load.py --route "check the ad ranking"    # pick rooms by keyword routing
    python3 tools/stair_load.py --agent builder --out CLAUDE.md   # write a UTF-8 file (Windows: always use --out, not >)

The output is plain text. Pipe it wherever your tool takes a system prompt / context file:
    Claude Code / Codex / Cursor / Gemini CLI  → write to CLAUDE.md, AGENTS.md, .cursorrules, or a context file
    Ollama / LM Studio / any raw API           → put it in the system message

No network, no dependencies. Python 3.8+.
"""
import argparse
import re
import sys
from pathlib import Path

# Windows consoles default to a legacy code page (e.g. cp949 on Korean Windows) and Python then
# dies on the first non-ASCII character it prints. Force UTF-8 on the way out; reading already is.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
L1 = ROOT / "stairs" / "layer1" / "MEMORY.md"
L0 = ROOT / "stairs" / "layer0"
L2 = ROOT / "stairs" / "layer2"
L3 = ROOT / "stairs" / "layer3"
ROUTES = ROOT / "stairs" / "routes.txt"

_H2 = re.compile(r"^## +(.+?)\s*$")


def sections(text):
    """[(title, body)] split on '## ' headings. The pre-heading part comes back with title ''."""
    out, cur, buf = [], "", []
    for ln in text.split("\n"):
        m = _H2.match(ln)
        if m:
            out.append((cur, "\n".join(buf).strip()))
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(ln)
    out.append((cur, "\n".join(buf).strip()))
    return out


def toc(text):
    """The file's own <!-- toc --> block if present, else a bare list of section titles."""
    m = re.search(r"<!-- toc -->\n(.*?)<!-- /toc -->", text, re.S)
    if m:
        return m.group(1).strip()
    return "\n".join("- " + t for t, _ in sections(text) if t)


def pick_section(text, want):
    w = want.strip().lower()
    for t, body in sections(text):
        if t and (w in t.lower() or t.lower() in w):
            return f"## {t}\n{body}"
    return None


def room_file(room):
    """Accept '201', '201-ads', 'ads', or 'ads.md'."""
    room = str(room).strip()
    cands = sorted(L2.glob("*.md"))
    for p in cands:
        if p.stem == room or p.name == room:
            return p
    for p in cands:
        if p.stem.startswith(room + "-") or p.stem.split("-", 1)[-1] == room:
            return p
    return None


def route(query):
    """routes.txt lines look like:  201-ads.md | ranking, index, keyword
    Return the files whose keywords appear in the query (best matches first, max 2)."""
    if not ROUTES.exists():
        return []
    q = query.lower()
    scored = []
    for ln in ROUTES.read_text(encoding="utf-8").splitlines():
        if "|" not in ln or ln.strip().startswith("#"):
            continue
        fn, kws = [x.strip() for x in ln.split("|", 1)]
        hits = sum(1 for k in kws.split(",") if k.strip() and k.strip().lower() in q)
        if hits:
            scored.append((hits, fn))
    return [fn for _, fn in sorted(scored, reverse=True)[:2]]




# The file each tool reads on every call. Different name, same job.
# If your tool is not here, --install still takes an explicit path.
KNOWN_TARGETS = [
    ("CLAUDE.md",       "Claude Code"),
    ("AGENTS.md",       "Codex CLI / OpenAI agents"),
    ("GEMINI.md",       "Gemini CLI"),
    ("AGENT.md",        "Antigravity / generic"),
    (".cursorrules",    "Cursor"),
    (".clinerules",     "Cline"),
    (".windsurfrules",  "Windsurf"),
    (".github/copilot-instructions.md", "GitHub Copilot"),
    ("GROK.md",         "Grok Build"),
    (".rules",          "generic rules file"),
]

# Tools with no project file — the block goes in their system-prompt box.
PROMPT_ONLY = ["Ollama", "LM Studio", "raw API / any chat UI"]


# ── --install ────────────────────────────────────────────────────────────────
# Why this exists: the loader could always write Layer 1 with `--out CLAUDE.md`,
# but that OVERWRITES the file. Nobody runs that on a CLAUDE.md they already have,
# so in practice the stair never reaches the one file the agent actually reads
# every call — and the agent keeps working from memory. That happened to us.
# `--install` appends a managed block instead, and re-running replaces just that
# block. Your own rules above and below it are never touched.
BEGIN = "<!-- STAIR:BEGIN — managed by tools/stair_load.py --install; edit stairs/, not here -->"
END = "<!-- STAIR:END -->"


def install_block(layer1_text, root):
    """The block we keep in the agent's always-read file."""
    return "\n".join([
        BEGIN,
        "## Stair — read this first",
        "",
        "This project keeps the agent's context on a staircase. You are holding Layer 1 only.",
        "Everything else is opened **by address**, when you need it — never by scrolling.",
        "",
        "```",
        "Layer 4  runtime    what the harness injects every call (date, tools, recent turns)",
        "Layer 3  identity   one card per role — who you are, how you speak",
        "Layer 2  knowledge  rooms by address (201, 202 …) — open one section at a time",
        "Layer 1  memory     this page — always loaded",
        "Layer 0  this chat  what THIS thread is doing — never auto-loaded",
        "```",
        "",
        "**When you need something that is not on this page, run the loader — do not guess:**",
        "",
        "```bash",
        f"python3 {root}/tools/stair_load.py --route \"<what you need, in your own words>\"",
        f"python3 {root}/tools/stair_load.py --room 201 --section indexing",
        f"python3 {root}/tools/stair_load.py --agent builder      # an identity card (Layer 3)",
        "```",
        "",
        "Identity lives in Layer 3, not here. This page holds only what every role shares.",
        "",
        "### Layer 1",
        "",
        layer1_text.strip(),
        END,
    ])


def install_targets(explicit):
    """Which files to write. With no --install value, every known file that exists."""
    if explicit and explicit != "auto":
        return [Path(explicit)]
    found = [Path(n) for n, _ in KNOWN_TARGETS if Path(n).exists()]
    return found


def do_install(target, layer1_text, root, dry_run=False):
    block = install_block(layer1_text, root)
    p = Path(target)
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    if BEGIN in old and END in old:
        head, rest = old.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        new = head + block + tail
        action = "updated"
    else:
        sep = "" if not old or old.endswith("\n\n") else ("\n" if old.endswith("\n") else "\n\n")
        new = old + sep + block + "\n"
        action = "added"
    if dry_run:
        print(f"[dry-run] would have {action} the stair block in {p} "
              f"({len(block)} chars; your other {len(old)} chars are kept)")
        return 0
    p.write_text(new, encoding="utf-8")
    print(f"{action} the stair block in {p} ({len(block)} chars kept in sync with stairs/layer1)")
    print("re-run this after you edit Layer 1; your own text outside the markers is never touched")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chat", help="Layer 0 note for THIS chat only (file stem under stairs/layer0/) — never loaded unless you ask")
    ap.add_argument("--agent", help="Layer 3 card to include (file stem under stairs/layer3/)")
    ap.add_argument("--room", help="Layer 2 room to open (number, stem or filename)")
    ap.add_argument("--section", help="only this section of the room (title substring)")
    ap.add_argument("--route", help="pick rooms by keywords in this text")
    ap.add_argument("--full", action="store_true", help="with --room: print the whole file, not just the TOC")
    ap.add_argument("--install", metavar="FILE", nargs="?", const="auto",
                    help="put Layer 1 + the routing rules into the file your agent reads every call. "
                         "With no FILE: every known agent file present here (CLAUDE.md, AGENTS.md, GEMINI.md, "
                         ".cursorrules, .clinerules, .windsurfrules, copilot-instructions.md, GROK.md). "
                         "Appends a managed block — your own text is kept. Re-run to refresh it.")
    ap.add_argument("--dry-run", action="store_true", help="with --install: show what would change, write nothing")
    ap.add_argument("--out", help="write the result to this file as UTF-8 (use this on Windows: PowerShell's > redirection saves UTF-16)")
    a = ap.parse_args()

    rc = 0
    parts = []
    if not L1.exists():
        sys.exit(f"missing {L1} — Layer 1 is the one file you must have")
    l1_text = L1.read_text(encoding="utf-8").strip()
    if a.install is not None:
        try:
            root = ROOT.relative_to(Path.cwd())
        except Exception:
            root = ROOT
        targets = install_targets(a.install)
        if not targets:
            print("no agent file found in this folder. Either name one:")
            for n, tool in KNOWN_TARGETS:
                print(f"    python3 tools/stair_load.py --install {n:<34} # {tool}")
            print("\nor, for tools with no project file " + ", ".join(PROMPT_ONLY) + ":")
            print("    python3 tools/stair_load.py            # print Layer 1 and paste it into the system prompt box")
            sys.exit(1)
        rc2 = 0
        for tp in targets:
            rc2 |= do_install(str(tp), l1_text, root, a.dry_run)
        sys.exit(rc2)
    parts.append(l1_text)

    if a.chat:
        p = L0 / f"{a.chat}.md"
        if p.exists():
            parts.append(f"[Layer 0 · this chat only — not shared with your other chats]\n"
                         + p.read_text(encoding="utf-8").strip())
        else:
            parts.append(f"[stair] no Layer 0 note for '{a.chat}' (looked for {p})")
            rc = 2

    if a.agent:
        p = L3 / f"{a.agent}.md"
        if p.exists():
            parts.append(p.read_text(encoding="utf-8").strip())
        else:
            parts.append(f"[stair] no Layer 3 card for '{a.agent}' (looked for {p})")

    rooms = []
    if a.room:
        rooms.append(a.room)
    if a.route:
        hit = route(a.route)
        if not hit:
            kws = [ln.strip() for ln in ROUTES.read_text(encoding="utf-8").splitlines()
                   if "|" in ln and not ln.strip().startswith("#")] if ROUTES.exists() else []
            print(f"[stair] --route matched no room for: {a.route!r}. Known routes:\n  " + "\n  ".join(kws), file=sys.stderr)
            rc = 2
        rooms += hit
    if (a.section or a.full) and not rooms:
        print("[stair] --section/--full need a room: add --room <id> or --route <text>", file=sys.stderr)
        rc = 2
    for r in rooms:
        p = room_file(r)
        if not p:
            parts.append(f"[stair] no Layer 2 room matches '{r}'. Rooms: " + ", ".join(x.stem for x in sorted(L2.glob("*.md"))))
            continue
        text = p.read_text(encoding="utf-8")
        if a.section:
            body = pick_section(text, a.section)
            parts.append(body if body else f"[stair] room {p.stem} has no section like '{a.section}'. TOC:\n{toc(text)}")
        elif a.full:
            parts.append(text.strip())
        else:
            parts.append(f"[Layer 2 · {p.stem} — table of contents; open a section with --section]\n{toc(text)}")

    out = "\n\n---\n\n".join(parts)
    if a.out:
        data = out + "\n"
        # newline="\n": keep LF on Windows too (matches .gitattributes eol=lf) and make the reported size exact
        Path(a.out).write_text(data, encoding="utf-8", newline="\n")
        print(f"[stair] wrote {a.out} ({len(data.encode('utf-8'))} bytes, UTF-8, LF)")
    else:
        print(out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
