# Room 204 — How this system is wired

<!-- toc -->
Sections (5) — read only what you need:
- Layers — Layer 1 (stairs/layer1/MEMORY.md) is loaded on every call. L…
- Loading — tools/stairload.py prints exactly what to inject. Layer 1 al…
- Keeping it honest — tools/stairtoc.py check finds rooms nothing points to, route…
- Recent work and chat notes — Two layers are generated rather than written, and both have …
- Changes
<!-- /toc -->

## Layers
Layer 1 (`stairs/layer1/MEMORY.md`) is loaded on every call. Layer 2 (`stairs/layer2/`) is opened by room address only when needed. Layer 3 (`stairs/layer3/`) is one identity card per agent.

## Loading
`tools/stair_load.py` prints exactly what to inject. Layer 1 always; a Layer 3 card with `--agent`; a room's TOC with `--room`; one section with `--section`; keyword routing with `--route`.

## Keeping it honest
`tools/stair_toc.py check` finds rooms nothing points to, routes that point at nothing, and prints the Layer 1 size so you notice when it grows.

## Recent work and chat notes

Two layers are generated rather than written, and both have a tool:

`tools/recent_work.py` — Layer 4. What you changed in the last day or two, read from git at call
time. Wire it to whatever runs at session start; on Claude Code that is the `SessionStart` hook,
which also fires on compaction. If the block ever stops appearing, the delivery broke — fix the
wiring rather than working from memory.

```bash
python3 tools/recent_work.py --ledger CHANGELOG.md
python3 tools/recent_work.py --hours 72 --full     # wider, with commit subjects
```

`tools/chat_note.py` — Layer 0. One note per chat thread. It keeps the mechanical half current
(files touched, sessions, last active) and leaves the judgment half — goal, decisions, what was
ruled out, where it stopped — for you to write. Only the block between the AUTO markers is
rewritten, so your prose is never clobbered.

```bash
python3 tools/chat_note.py --note auth-refactor --start    # print at session start
python3 tools/chat_note.py --note auth-refactor --touch    # after a turn; cheap, run it often
python3 tools/chat_note.py --note auth-refactor --append "ruled out: session cookies, SSR breaks"
```

Write the ruled-out decisions especially. Without them the next session proposes the thing you
already rejected, and you spend the same hour twice.

Both are stdlib-only and behave the same on macOS, Linux and Windows. On Windows call them with
`python` rather than `python3`; they force UTF-8 output so a legacy console code page cannot
silently swallow the block.

## Changes
- (add one line here every time you change the wiring — who, what, why)
