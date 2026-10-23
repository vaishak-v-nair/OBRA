param([ValidateSet('Core','Full')][string]$Scope = 'Core')
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($Scope -eq 'Full') {
    Write-Output 'Full is not an implicit combined gate. Run Gate A, then scripts/verify-orchestration-local.ps1 for independent local Gate B. Stage05A makes no model requests.'
    exit 2
}
& uv run --directory apps/api python -m scripts.orchestration_verification A
$gateExit = $LASTEXITCODE
exit $gateExit
