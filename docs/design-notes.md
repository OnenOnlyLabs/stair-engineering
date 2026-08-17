# Design notes — why each rule exists

**One page, always.** Tools truncate. Models skim. A rule that lives at line 400 of a 21 KB file is a rule that will be lost. One page is the largest thing you can trust to be read whole.

**Addresses, not search.** "Room 201, section Indexing" can be said out loud, written in a chat, and checked by a human in seconds. A vector hit cannot.

**TOC first, section second.** Cost is paid per token, and a room is 5–10× a page. Reading the corridor before the room keeps the staircase thin all the way up.

**Routes are plain text.** A keyword table you can read beats a ranker you cannot debug at 2 a.m.

**The tool prints the size.** Nobody keeps a page thin by willpower. Show the number every time.

**Change log inside the system.** Chat scrolls away. Room 204's "Changes" list is the memory of the memory.

**One owner, many copies, verify by count.** Distributed copies drift silently. Count files after every push and treat a mismatch as an alarm, not a note.

## Why the checker runs the Layer 4 generator instead of describing it

Layers 1 through 3 are files. If one is wrong you can open it and see that it is wrong. Layer 4 is
produced at call time, and its failures are silent by construction: the block still renders, the
harness still injects it, nothing raises. A window that quietly returns last week's work looks exactly
like a window that is working. So the rule about Layer 4 is enforced by `stair_toc.py check`, which
runs the generator and fails when there is history to show and the block comes back empty. A caution
in a document gets read once; a check runs every time.

## Do not ask the agent what is in its prompt

The obvious way to find out whether an injected block arrived is to ask the agent. It is also the way
that produces false answers, in both directions.

Asking a model to quote its own system prompt is a disclosure request, and many models answer it with
silence or a refusal that your harness records as an empty completion — which looks identical to a
crash in the injection code. In the other direction, a model that cannot see a block will often
reconstruct a plausible one rather than say it is missing.

Dump the bytes you actually transmit to a file and read them yourself. The agent's self-report is
testimony, not evidence, and the two diverge exactly when you most need the truth.

A related trap: when several agents independently offer the same explanation for a failure, that is
several agents reading the same visible clues, not corroboration. Treat unanimity as one hypothesis
worth testing rather than as a result — and prefer the cheapest experiment that separates it from the
alternative, changing one variable at a time. A rollback that also changes the question tells you
nothing about either.
