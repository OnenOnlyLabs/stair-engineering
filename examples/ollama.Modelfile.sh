#!/usr/bin/env bash
# Build an Ollama Modelfile whose SYSTEM is Layer 1 + the researcher card.
set -e
cd "$(dirname "$0")/.."
SYS=$(python3 tools/stair_load.py --agent researcher)
cat > Modelfile <<MF
FROM llama3
SYSTEM """
$SYS
"""
MF
echo "wrote Modelfile — now: ollama create stairs-researcher -f Modelfile"
