# Creating your own Layer 1

The example `stairs/layer1/MEMORY.md` is for a four-agent team. Yours will be smaller. Keep it to one page.

## What goes in
- Who is on the team (one line each: `@name  what they do`). For a solo agent, one line.
- How to talk (only if there is more than one agent).
- How to work — the 5–8 rules you keep repeating in chat. Those are the ones.
- Safety — the three or four things that must never happen.
- Rooms — the list of Layer 2 files with a one-phrase "when to open this".

## What stays out
- Anything an agent needs *sometimes*. That is a room.
- Anything longer than two lines. Move it to a room, leave one line pointing there.
- Secrets, keys, private hostnames, customer names. Never.
- Version history and changelogs. Room 204 has a "Changes" list.

## Format rules (they matter)
- One rule per line. No tables, no nested bullets. If a tool squashes newlines, the meaning must survive.
- Say the rule, not the story behind it. The story can live in a room.
- No numbers that go stale ("we are 12 agents") — write the list, not the count.

## Size
Run `python3 tools/stair_toc.py check`. It prints the byte size. Local models: aim under ~3 KB. Cloud models: under ~10 KB is comfortable. When it grows, move a section into a room.
