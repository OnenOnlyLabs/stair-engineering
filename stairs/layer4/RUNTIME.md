# Layer 4 — Runtime injection (what the code adds every call)

Not a file the agent reads. This is the list of things your harness silently prepends to every request.
Write them down here anyway: what you cannot see, you cannot trim.

Layer 4 has two halves. Most people only do the first: **count it**, so you know your real cost.
The second is **fill it** — this is the only layer that can hand the agent something which is neither an
always-true rule nor a room it knows to open.

## Typical items
- current date and time (agents guess the year wrong without it)
- the tool list / schema your harness advertises
- the last N turns of conversation
- file context the editor attaches (open buffers, selection, diffs)
- system reminders the harness adds on its own

## Rules
- Measure it once. Print the exact prompt your harness sends and count the bytes. That number is your real Layer 1 cost.
- Anything here that never changes belongs in Layer 1 instead — put it in the file you control.
- Anything here that is situational (time, current file) is correct to inject; leave it.
- When you shrink Layer 1 and nothing gets faster, the reason is almost always this layer.

## What to deliberately inject

**Recent work — what this agent changed in the last day or two.**
Not a rule, so it does not belong on Layer 1. The agent has no reason to go looking for it, so Layer 2
never reaches it. Unfilled, the symptom is specific: the agent cannot recall work it did hours ago, and
nobody can see why, because a long session compacts itself without anyone pressing anything.

Deliver it at the two moments the agent goes blank: **session start** and **compaction**.

```bash
python3 tools/recent_work.py --ledger CHANGELOG.md
```

```
🧠 [last 36h you touched — most recent first]
  src/auth/session.ts · src/auth/tokens.ts · tests/auth.spec.ts
  📒 2026-03-04 — rotate refresh tokens on reuse
```

Four rules, each of which was a bug first:
- **Read, don't store.** Generate from version control at call time. Nothing accumulates, and the record
  is complete without anyone's discipline.
- **Most-recent-first, not most-frequent.** Frequency puts your changelog at the top and pushes the file
  you just edited off the list.
- **Widen when empty, not when old.** Below a handful of hits, reach back further. A blank block reads as
  "nothing happened" — straight back to the original failure.
- **Fixed read cost.** A bounded window, so the block stays ~12 lines however long history grows.

The generator is code, not a floor. What it prints is Layer 4; the rule that the block must appear belongs
on Layer 1; how to run it belongs in a Layer 2 room.

Other things worth injecting here rather than hard-coding: the current branch, whether the working tree is
dirty, and which environment the agent is pointed at. All situational, all cheap, all wrong to memorize.
