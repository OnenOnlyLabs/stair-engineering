# Layer 4 — Runtime injection (what the code adds every call)

Not a file the agent reads. This is the list of things your harness silently prepends to every request.
Write them down here anyway: what you cannot see, you cannot trim.

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
