#!/usr/bin/env bash
# Generate AGENTS.md from the stairs (Layer 1 + the builder card). Re-run after editing stairs/.
set -e
cd "$(dirname "$0")/.."
python3 tools/stair_load.py --agent builder --out AGENTS.md
printf '\n\n# When a task needs domain knowledge\nRun `python3 tools/stair_load.py --route "<the request>"` and read the section it returns before answering.\n' >> AGENTS.md
echo "wrote AGENTS.md ($(wc -c < AGENTS.md) bytes)"
