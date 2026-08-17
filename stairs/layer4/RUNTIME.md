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

Three more failures show up the moment you build this, and none of them raise anything:
- **Bound the block by time, not by count.** A count-based window keeps delivering last week once the
  log goes quiet. After three idle days, three-day-old work arrives labelled *recent* — and a stale
  block is worse than an empty one, because it reads as current.
- **When a record is too long to keep whole, keep the tail.** Answers carry their framing at the front
  and their decision at the end; truncate from the front and every entry becomes a preamble.
- **Log what the agent was asked, not the envelope it arrived in.** Recipient lists and routing headers
  are prepended by your dispatcher, so a head-truncated record can preserve the wrapper and lose the
  entire question.

Layer 4 fails quietly by nature. The block still renders; only its contents go stale. Nothing throws,
so nothing appears in the logs — which is why the checks belong in a tool, not in a page of advice.

The generator is code, not a floor. What it prints is Layer 4; the rule that the block must appear belongs
on Layer 1; how to run it belongs in a Layer 2 room.

**Recent actions — what this agent actually ran.**
Only if it uses tools, and only if you check where they are logged. The conversation and the tool calls
usually live in different stores, and injecting just the conversation gives you an agent that remembers
every word and none of its own work — it re-runs finished commands and retries failed approaches. Collapse
consecutive repeats to one line and keep it to about six.

Two things decide whether this block helps or hurts, and both are about *what* you put in it.

A command log records that a call was **made**, not that it **worked**. An agent that reads "submitted
the render job" with no outcome attached will report the job as done more confidently than if it had
read nothing at all — you strengthen the confabulation instead of correcting it. So log outcomes:
a success flag, the artifact path, the exit code. You can drop the successes entirely, since the
artifact is already the evidence, and keep only what failed.

A command log is also a cache with no invalidation. "Read that file twenty minutes ago" is offered as
history and taken as current state, and in the meantime the file changed. Prefer **state changes**
("config rewritten at 10:20") over **actions** ("listed the directory"): a state change has a long
useful life and costs real work to re-verify, while re-running a cheap read costs nothing. Anything
cheap to redo does not need to be in the block at all.

Other things worth injecting here rather than hard-coding: the current branch, whether the working tree is
dirty, and which environment the agent is pointed at. All situational, all cheap, all wrong to memorize.

## Close with a condition, not a prohibition

The last line of the block is an instruction, and its shape matters more than its content.

    ✗  Do not repeat anything listed above.
    ✓  Before running anything listed above, check its recorded result first.

A bare prohibition gives the model nothing to evaluate: it has to decide what counts as "the same"
on every turn, and that judgement drifts. A condition names a check it can actually perform. Several
of our agents also report that naming a forbidden action tends to raise it rather than suppress it —
that one is an observation from their own logs, not something we have isolated with a control, so
treat it as a reason to prefer the conditional form rather than as a finding about negation.
