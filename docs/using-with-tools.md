# Using the stairs with your tool

The loader prints plain text. Put it where your tool reads instructions.

**Windows:** always write with `--out FILE`. PowerShell's `>` redirection saves UTF-16 with a BOM, which breaks every UTF-8 reader downstream. `python` not `python3`. See `examples/*.ps1` and `examples/*.bat`.

## Claude Code
```bash
python3 tools/stair_load.py --agent builder --out CLAUDE.md
```
When a task needs a room, ask Claude to run `python3 tools/stair_load.py --room 201 --section indexing` and read the output. Or add one line to CLAUDE.md: "Before domain work, run the loader with --route and read the section it returns."

## Codex CLI / AGENTS.md
```bash
python3 tools/stair_load.py --agent builder --out AGENTS.md
```

## Cursor / VS Code agent rules
```bash
python3 tools/stair_load.py --out .cursorrules
```

## Gemini CLI / Antigravity
Write the loader output into the context file your tool reads at start (for example `GEMINI.md`).

## Ollama
```bash
python3 tools/stair_load.py --agent researcher --out /tmp/system.txt
# Modelfile
FROM llama3
SYSTEM """$(cat /tmp/system.txt)"""
```
Keep Layer 1 short for local models — under ~3 KB is a good target.

## LM Studio / any raw API
Send the loader output as the `system` message. When the user's request matches a room, append `--route "<request>"` output to the same system message for that turn only.

## An agent that cannot run commands (chat UI)
Paste Layer 1 once as custom instructions. When the task needs a room, paste that room's TOC, then the one section the agent asks for. Do not paste whole rooms.

## Several agents, several machines
Pick one machine as the owner of `stairs/`. Push copies from there (rsync/scp) and verify by file count after each push. Restart agent processes after a push — a file arriving is not a process reloading it.
