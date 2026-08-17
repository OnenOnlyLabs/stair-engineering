# Using the stairs with your tool

The loader prints plain text. Put it where your tool reads instructions.

**Windows:** always write with `--out FILE`. PowerShell's `>` redirection saves UTF-16 with a BOM, which breaks every UTF-8 reader downstream. `python` not `python3`. See `examples/*.ps1` and `examples/*.bat`.

## Claude Code
```bash
python3 tools/stair_load.py --install CLAUDE.md      # appends; your existing rules are kept
```
When a task needs a room, ask Claude to run `python3 tools/stair_load.py --room 201 --section indexing` and read the output. Or add one line to CLAUDE.md: "Before domain work, run the loader with --route and read the section it returns."

## Codex CLI / AGENTS.md
```bash
python3 tools/stair_load.py --install AGENTS.md      # appends; your existing rules are kept
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

## One command for all of them

```bash
python3 tools/stair_load.py --install        # finds every agent file in the folder and updates each
python3 tools/stair_load.py --install --dry-run   # show what would change, write nothing
```

Recognised: `CLAUDE.md` · `AGENTS.md` · `GEMINI.md` · `AGENT.md` · `.cursorrules` · `.clinerules` ·
`.windsurfrules` · `.github/copilot-instructions.md` · `GROK.md`. Name any other path with `--install FILE`.

`--install` writes only between the `STAIR:BEGIN` / `STAIR:END` markers, so it is safe on a file you already
have, and re-running refreshes just that block. `--out FILE` still exists and **replaces** the whole file —
use it for a new file only.

**Tools with no project file** (Ollama, LM Studio, raw API, chat UIs): run `python3 tools/stair_load.py`
and paste the output into the system-prompt box. Re-paste after you change Layer 1.

## Layer 4 — delivering recent work at session start

Layer 1 through 3 are files the agent loads. Layer 4 is what your harness *injects*, and the piece worth
injecting on purpose is what the agent changed recently — a long session compacts itself, and everything
before the fold is gone without anyone pressing anything.

Print this into the model's context at session start (and at compaction, if your tool exposes it):

```bash
python3 tools/recent_work.py --repo . --ledger CHANGELOG.md
```

**Claude Code** — a `SessionStart` hook in `.claude/settings.json`; it fires on start, resume, clear and
compact, which is exactly the set of moments the agent goes blank:

```json
{ "hooks": { "SessionStart": [ { "hooks": [ { "type": "command",
  "command": "python3 tools/recent_work.py --ledger CHANGELOG.md" } ] } ] } }
```

**Codex CLI / Cursor / Gemini CLI** — no session hook. Run the command yourself and paste the block, or
have your wrapper script prepend it to the first message of each session.

**Any harness you control** — prepend the output to the system prompt you assemble. It is ~12 lines.

Two things to check once it is wired:
- The block appears on a *resumed* session, not just a fresh one. Resuming is where the loss actually happens.
- Non-ASCII paths render as text, not octal escapes. If you wrote your own generator, pass
  `-c core.quotepath=false` to git — without it the escaped path also defeats extension filters.
