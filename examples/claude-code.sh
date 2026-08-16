#!/usr/bin/env bash
# Generate a CLAUDE.md for Claude Code from the stairs (Layer 1 + the builder card).
# Re-run whenever you edit stairs/. Rooms are opened on demand by asking Claude to run the loader.
set -e
cd "$(dirname "$0")/.."
python3 tools/stair_load.py --agent builder --out CLAUDE.md
printf '\n\n# When a task needs domain knowledge\nRun `python3 tools/stair_load.py --route "<the request>"` and read the section it returns before answering.\n' >> CLAUDE.md
echo "wrote CLAUDE.md ($(wc -c < CLAUDE.md) bytes)"
