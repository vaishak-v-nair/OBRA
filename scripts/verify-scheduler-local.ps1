$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location (Split-Path $PSScriptRoot -Parent)
& uv run --directory apps/api python -m scripts.scheduler_verification B
exit $LASTEXITCODE
