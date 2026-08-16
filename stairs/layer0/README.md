# Layer 0 — one file per chat

You have more than one chat open with your agent. One is refactoring auth, one is writing docs,
one is chasing a bug. Each of those threads has state that belongs to it and to nothing else:
what was decided, what was ruled out, where it stopped.

That state does not belong in Layer 1 — every other chat would read it on every call.
It is not knowledge either — it expires the day the task ships.

So give each chat its own file here: `stairs/layer0/<chat-name>.md`.

Rules that make it work:

- **Never auto-loaded.** No tool injects Layer 0. You paste it into the one chat it belongs to,
  or your wrapper loads it for that session only.
- **One file per chat, named after the work** — `auth-refactor.md`, not `chat-3.md`.
- **Write the state, not the transcript.** Decisions, dead ends, the next step. Not what was said.
- **When it stops being about this chat, promote it.** A fact you will need again belongs in a
  Layer 2 room. A rule you will always need belongs in Layer 1. Layer 0 is where things
  pass through, not where they live.
- **Delete it when the work ships.** A folder of stale Layer 0 files is worse than none.

`python tools/stair_toc.py check` counts these files and warns when one grows past 8 KB —
at that size it is usually holding something that should have moved upstairs.
