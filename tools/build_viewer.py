#!/usr/bin/env python3
"""build_viewer — turn your stairs/ folder into ONE self-contained index.html you can double-click.

Why this exists: the whole point of the stairs is that a human can see what the agent reads.
A terminal tool does not do that for someone who does not live in terminals.
This writes a single HTML file with your floors embedded — no server, no build, no network.

    python3 tools/build_viewer.py            # writes stairs.html next to your stairs/ folder
    python3 tools/build_viewer.py --out ~/Desktop/stairs.html

It only reads stairs/. Nothing is uploaded anywhere.
"""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAIRS = ROOT / "stairs"


def sections(text):
    out, cur, buf = [], "", []
    for ln in text.split("\n"):
        m = re.match(r"^## +(.+?)\s*$", ln)
        if m:
            out.append((cur, "\n".join(buf).strip()))
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(ln)
    out.append((cur, "\n".join(buf).strip()))
    return [(t, b) for t, b in out if t or b]


def collect():
    data = {"floors": []}
    notes = [q for q in sorted((STAIRS / "layer0").glob("*.md")) if q.name != "README.md"] \
        if (STAIRS / "layer0").is_dir() else []
    if notes:
        data["floors"].append({
            "id": "0F", "name": "this chat only", "sub": "one file per chat · never auto-loaded",
            "accent": "quiet", "bytes": sum(q.stat().st_size for q in notes),
            "items": [{"title": q.stem, "sections": [{"title": s or "(top)", "body": b}
                                                     for s, b in sections(q.read_text(encoding="utf-8"))]}
                      for q in notes],
        })
    l1 = STAIRS / "layer1" / "MEMORY.md"
    if l1.exists():
        t = l1.read_text(encoding="utf-8")
        data["floors"].append({
            "id": "1F", "name": "one page", "sub": "always loaded · every call",
            "accent": "hot", "bytes": l1.stat().st_size,
            "items": [{"title": l1.name, "sections": [{"title": s or "(top)", "body": b} for s, b in sections(t)]}],
        })
    rooms = sorted((STAIRS / "layer2").glob("*.md")) if (STAIRS / "layer2").is_dir() else []
    if rooms:
        data["floors"].append({
            "id": "2F", "name": "knowledge", "sub": "opened by address · one section at a time",
            "accent": "cool", "bytes": sum(p.stat().st_size for p in rooms),
            "items": [{"title": p.stem, "sections": [{"title": s or "(top)", "body": b}
                                                     for s, b in sections(p.read_text(encoding="utf-8"))]}
                      for p in rooms],
        })
    cards = sorted((STAIRS / "layer3").glob("*.md")) if (STAIRS / "layer3").is_dir() else []
    if cards:
        data["floors"].append({
            "id": "3F", "name": "identity", "sub": "one card per agent",
            "accent": "plain", "bytes": sum(p.stat().st_size for p in cards),
            "items": [{"title": p.stem, "sections": [{"title": s or "(top)", "body": b}
                                                     for s, b in sections(p.read_text(encoding="utf-8"))]}
                      for p in cards],
        })
    rt = STAIRS / "layer4" / "RUNTIME.md"
    if rt.exists():
        data["floors"].append({
            "id": "4F", "name": "runtime", "sub": "what your code adds every call",
            "accent": "dashed", "bytes": rt.stat().st_size,
            "items": [{"title": rt.name, "sections": [{"title": s or "(top)", "body": b}
                                                      for s, b in sections(rt.read_text(encoding="utf-8"))]}],
        })
    data["floors"].reverse()   # top floor first on screen
    return data


TEMPLATE = """<!doctype html>
<meta charset="utf-8"><title>Stairs</title>
<style>
 :root{--bg:#0b1220;--panel:#121c30;--line:#24344f;--ink:#e8eefa;--dim:#8496b3;
       --hot:#f6a94b;--cool:#4aa8c6;--plain:#5f7fae;--dash:#8a7ab0}
 *{box-sizing:border-box}
 body{margin:0;background:linear-gradient(160deg,#101a2b,#070b13);color:var(--ink);
      font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Apple SD Gothic Neo",sans-serif}
 header{padding:26px 30px 6px}
 h1{margin:0;font-size:23px;letter-spacing:-.3px}
 header p{margin:6px 0 0;color:var(--dim);font-size:14px}
 .wrap{display:grid;grid-template-columns:minmax(340px,1fr) minmax(360px,1.1fr);gap:22px;padding:18px 30px 40px}
 @media (max-width:900px){.wrap{grid-template-columns:1fr}}
 .floor{border:1px solid var(--line);border-radius:8px;background:var(--panel);margin:0 0 12px;overflow:hidden}
 .floor.hot{border-color:var(--hot)} .floor.cool{border-color:var(--cool)}
 .floor.dashed{border-style:dashed;border-color:var(--dash)}
 .floor.quiet{border-color:#33465f;opacity:.72}
 .fhead{display:flex;align-items:baseline;gap:12px;padding:14px 16px}
 .fid{color:var(--dim);letter-spacing:3px;font-size:12px}
 .fname{font-size:18px;font-weight:650}
 .fsub{color:var(--dim);font-size:13px;margin-left:auto;text-align:right}
 .items{display:flex;flex-wrap:wrap;gap:8px;padding:0 16px 14px}
 button.item{cursor:pointer;border:1px solid var(--line);background:#0d1626;color:#cfe0f5;
   border-radius:6px;padding:7px 11px;font-size:13px;font-family:inherit}
 button.item:hover{border-color:var(--cool);color:#fff}
 button.item.on{border-color:var(--hot);color:#ffe6c2}
 .pane{border:1px solid var(--line);border-radius:8px;background:#0c1424;padding:0;min-height:320px}
 .ptitle{padding:14px 16px;border-bottom:1px solid var(--line);color:var(--dim);font-size:13px}
 .secs{display:flex;flex-wrap:wrap;gap:6px;padding:12px 16px;border-bottom:1px solid var(--line)}
 .secs button{cursor:pointer;border:1px solid transparent;background:#111c31;color:#a9bdd8;
   border-radius:999px;padding:5px 11px;font-size:12.5px;font-family:inherit}
 .secs button.on{background:#1a2942;color:#fff;border-color:var(--cool)}
 pre{margin:0;padding:16px 18px;white-space:pre-wrap;word-break:break-word;color:#d7e2f2;font-size:13.5px;
     font-family:ui-monospace,SFMono-Regular,Menlo,monospace;line-height:1.62}
 footer{padding:0 30px 30px;color:#54637d;font-size:12.5px}
</style>
<header>
  <h1>Stairs</h1>
  <p>Everything your agent reads, by floor. Click a file, then a section — that is exactly how the loader hands it over.</p>
</header>
<div class="wrap"><div id="floors"></div>
  <div class="pane"><div class="ptitle" id="ptitle">pick a file on the left</div>
  <div class="secs" id="secs"></div><pre id="body"></pre></div></div>
<footer>Generated from your own <code>stairs/</code> folder. No network, no tracking. Re-run the builder after you edit.</footer>
<script>
const DATA = __DATA__;
const floors = document.getElementById('floors');
const ptitle = document.getElementById('ptitle');
const secsEl = document.getElementById('secs');
const bodyEl = document.getElementById('body');
let cur = null;

function kb(n){ return n >= 1024 ? (n/1024).toFixed(1)+' KB' : n+' B'; }

DATA.floors.forEach(f => {
  const d = document.createElement('div');
  d.className = 'floor ' + f.accent;
  d.innerHTML = `<div class="fhead"><span class="fid">${f.id}</span>
    <span class="fname">${f.name}</span><span class="fsub">${f.sub} · ${kb(f.bytes)}</span></div>`;
  const box = document.createElement('div'); box.className = 'items';
  f.items.forEach(it => {
    const b = document.createElement('button');
    b.className = 'item'; b.textContent = it.title;
    b.onclick = () => { document.querySelectorAll('button.item').forEach(x=>x.classList.remove('on'));
                        b.classList.add('on'); open(f, it); };
    box.appendChild(b);
  });
  d.appendChild(box); floors.appendChild(d);
});

function open(f, item){
  cur = item;
  ptitle.textContent = f.id + ' · ' + item.title + ' — ' + item.sections.length + ' section(s)';
  secsEl.innerHTML = '';
  item.sections.forEach((s, i) => {
    const b = document.createElement('button');
    b.textContent = s.title;
    b.onclick = () => { [...secsEl.children].forEach(x=>x.classList.remove('on'));
                        b.classList.add('on'); bodyEl.textContent = s.body || '(empty)'; };
    secsEl.appendChild(b);
    if (i === 0) b.click();
  });
}
const first = DATA.floors.find(f => f.id === '1F') || DATA.floors[0];
if (first) { open(first, first.items[0]); document.querySelector('button.item')?.classList.add('on'); }
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "stairs.html"))
    a = ap.parse_args()
    if not STAIRS.is_dir():
        raise SystemExit(f"no stairs/ folder at {STAIRS}")
    data = collect()
    if not data["floors"]:
        raise SystemExit("stairs/ has no layer0..layer4 content yet")
    out = Path(a.out)
    out.write_text(TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    total = sum(f["bytes"] for f in data["floors"])
    print(f"wrote {out} — {len(data['floors'])} floors, {total} B of content embedded")
    print("open it by double-clicking. re-run this after you edit stairs/.")


if __name__ == "__main__":
    main()
