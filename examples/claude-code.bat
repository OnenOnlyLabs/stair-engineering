@echo off
REM Generate CLAUDE.md for Claude Code from the stairs (Windows cmd).
cd /d "%~dp0\.."
python tools\stair_load.py --agent builder --out CLAUDE.md
echo wrote CLAUDE.md
