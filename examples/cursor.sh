#!/usr/bin/env bash
# Generate .cursorrules from the stairs (Layer 1 + the builder card). Re-run after editing stairs/.
set -e
cd "$(dirname "$0")/.."
python3 tools/stair_load.py --agent builder --out .cursorrules
printf '\n\n# When a task needs domain knowledge\nRun `python3 tools/stair_load.py --route "<the request>"` and read the section it returns before answering.\n' >> .cursorrules
echo "wrote .cursorrules ($(wc -c < .cursorrules) bytes)"
