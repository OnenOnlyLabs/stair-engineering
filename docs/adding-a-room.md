# Adding a Layer 2 room — three steps

1. **Create the file** in `stairs/layer2/` named `<number>-<topic>.md`, e.g. `203-design.md`. Numbers group topics (200s = one domain, 300s = another); the topic word is what people will call it. Write it in sections with `## ` headings — sections are how the loader hands out just one piece.

2. **Generate the table of contents**: `python3 tools/stair_toc.py toc --apply`. Idempotent; run it every time you edit the file. The TOC block at the top is the "corridor" agents read before opening a section.

3. **Route to it** — twice, on purpose:
   - one line in `stairs/layer1/MEMORY.md` under Rooms: `Room 203 — design → layer2/203-design.md`
   - one line in `stairs/routes.txt`: `203-design.md | design, layout, banner, 시안`
   Then `python3 tools/stair_toc.py check` — it must not say UNROUTED.

Rules of thumb: one topic per room, sections named the way people ask ("Indexing", not "Section 3.2"), no room for one-off notes (append to an existing room instead).
