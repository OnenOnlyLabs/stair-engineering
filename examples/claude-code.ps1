# Generate CLAUDE.md for Claude Code from the stairs (Windows PowerShell).
# --out writes UTF-8 directly; do NOT use '>' in PowerShell (it saves UTF-16).
Set-Location (Join-Path $PSScriptRoot "..")
python tools/stair_load.py --agent builder --out CLAUDE.md
Add-Content -Path CLAUDE.md -Encoding utf8 -Value "`n`n# When a task needs domain knowledge`nRun ``python tools/stair_load.py --route `"<the request>`"`` and read the section it returns before answering."
Write-Output ("wrote CLAUDE.md (" + (Get-Item CLAUDE.md).Length + " bytes)")
