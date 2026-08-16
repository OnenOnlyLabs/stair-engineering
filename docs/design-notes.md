# Design notes — why each rule exists

**One page, always.** Tools truncate. Models skim. A rule that lives at line 400 of a 21 KB file is a rule that will be lost. One page is the largest thing you can trust to be read whole.

**Addresses, not search.** "Room 201, section Indexing" can be said out loud, written in a chat, and checked by a human in seconds. A vector hit cannot.

**TOC first, section second.** Cost is paid per token, and a room is 5–10× a page. Reading the corridor before the room keeps the staircase thin all the way up.

**Routes are plain text.** A keyword table you can read beats a ranker you cannot debug at 2 a.m.

**The tool prints the size.** Nobody keeps a page thin by willpower. Show the number every time.

**Change log inside the system.** Chat scrolls away. Room 204's "Changes" list is the memory of the memory.

**One owner, many copies, verify by count.** Distributed copies drift silently. Count files after every push and treat a mismatch as an alarm, not a note.
