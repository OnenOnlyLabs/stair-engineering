#!/usr/bin/env python3
"""stair_toc — put a section table-of-contents at the top of every Layer 2 file, and check the stairs.

Why: a Layer 2 file can be 25 KB. Opening it whole costs as much as six Layer 1 pages.
With a TOC at the top an agent reads the "corridor" first and opens only the section it needs.

    python3 tools/stair_toc.py toc            # preview
    python3 tools/stair_toc.py toc --apply    # write <!-- toc --> blocks (idempotent)
    python3 tools/stair_toc.py check          # stairs sanity: unrouted rooms, dead routes, missing files
"""
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
L2 = ROOT / "stairs" / "layer2"
ROUTES = ROOT / "stairs" / "routes.txt"
A, B = "<!-- toc -->", "<!-- /toc -->"
_H2 = re.compile(r"^## +(.+?)\s*$")


def first_sentence(lines, start):
    for ln in lines[start + 1:start + 12]:
        s = ln.strip()
        if not s or s.startswith(("#", "<!--", "|", "```", "-", "*", ">")):
            continue
        s = re.sub(r"[`*_\[\]]", "", s)
        return (s[:60] + "…") if len(s) > 60 else s
    return ""


def build(text):
    lines = text.split("\n")
    heads = [(i, m.group(1)) for i, ln in enumerate(lines) if (m := _H2.match(ln))]
    if len(heads) < 3:
        return None
    rows = [f"- {h} — {first_sentence(lines, i)}".rstrip(" —") for i, h in heads]
    return "\n".join([A, f"Sections ({len(heads)}) — read only what you need:", *rows, B])


def strip(text):
    return re.sub(re.escape(A) + r".*?" + re.escape(B) + r"\n?", "", text, flags=re.S)


def apply(path, write):
    text = path.read_text(encoding="utf-8")
    body = strip(text)
    t = build(body)
    if not t:
        return "skip (fewer than 3 sections)"
    lines = body.split("\n")
    at = next((i + 1 for i, ln in enumerate(lines[:5]) if ln.startswith("# ")), 0)
    # deterministic: title, blank, toc, blank, then the rest with leading blanks trimmed → idempotent
    rest = lines[at:]
    while rest and not rest[0].strip():
        rest.pop(0)
    new = "\n".join(lines[:at] + ["", t, ""] + rest)
    if new == text:
        return "unchanged"
    if write:
        path.write_text(new, encoding="utf-8")
    return ("wrote" if write else "would write") + f" ({t.count(chr(10)) - 1} sections)"


def check():
    bad = 0
    l1 = L1.read_text(encoding="utf-8") if L1.exists() else ""
    routed = set(re.findall(r"layer2/([A-Za-z0-9_\-]+\.md)", l1))
    if ROUTES.exists():
        for ln in ROUTES.read_text(encoding="utf-8").splitlines():
            if "|" in ln and not ln.strip().startswith("#"):
                routed.add(ln.split("|", 1)[0].strip())
    for p in sorted(L2.glob("*.md")):
        if p.name not in routed:
            print(f"UNROUTED  {p.name} — nothing points here; agents cannot find it")
            bad += 1
    for fn in sorted(routed):
        if not (L2 / fn).exists():
            print(f"DEAD ROUTE  {fn} — referenced but the file does not exist")
            bad += 1
    if L1.exists():
        n = L1.stat().st_size
        hint = "" if n < 3000 else ("  (over ~3 KB — too big for most local models; move a section into a room)" if n < 10000
                                    else "  (over ~10 KB — even cloud models skim at this size; move sections into rooms)")
        print(f"layer1: {n} bytes{hint}")
    l0 = ROOT / "stairs" / "layer0"
    if l0.exists():
        notes = [p for p in sorted(l0.glob("*.md")) if p.name != "README.md"]
        for p in notes:
            n = p.stat().st_size
            if n > 8000:
                print(f"FAT NOTE  layer0/{p.name} — {n} bytes; promote what is durable to a room")
                bad += 1
        print(f"layer0: {len(notes)} chat note(s)")
    print("check:", "ok" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        return check()
    if cmd == "toc":
        write = "--apply" in sys.argv
        for p in sorted(L2.glob("*.md")):
            print(f"  {p.name:<28} {apply(p, write)}")
        print("(preview — use --apply to write)" if not write else "done")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
