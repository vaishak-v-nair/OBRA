param([ValidateSet('Core','Full')][string]$Scope = 'Core')
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($Scope -eq 'Full') {
    Write-Output 'Full does not dispatch paid requests. Run Gate A; Architect live verification requires fresh owner authorization for scripts/verify-architect-live.ps1 -AllowPaid.'
    exit 2
}
& uv run --directory apps/api python -m scripts.architect_verification A
$gateExit = $LASTEXITCODE
exit $gateExit
