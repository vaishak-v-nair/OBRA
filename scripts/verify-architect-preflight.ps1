param([ValidateSet('preflight','navigation')][string]$Mode = 'preflight')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONIOENCODING = 'utf-8'
Write-Output 'UNPAID Phase 1 only: real navigation and source approval; all model generation is denied. This does not verify live AI.'
& uv run --directory apps/api python -m scripts.architect_preflight --mode $Mode
$gateExit = $LASTEXITCODE
exit $gateExit
