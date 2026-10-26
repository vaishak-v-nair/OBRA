param([ValidateSet('Core','Full')][string]$Scope = 'Core')
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($Scope -eq 'Full') {
    Write-Output 'Run Gate A, then scripts/verify-scheduler-local.ps1 for independent Stage05B local Gate B. Neither gate calls a model or executes engineering tasks.'
    exit 2
}
& uv run --directory apps/api python -m scripts.scheduler_verification A
$gateExit = $LASTEXITCODE
exit $gateExit
