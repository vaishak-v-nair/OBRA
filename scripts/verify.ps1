param([ValidateSet('Core','Full')][string]$Scope = 'Core')
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($Scope -eq 'Full') {
    Write-Output 'Full no longer dispatches paid requests. Run Gate A, then explicitly use scripts/verify-live.ps1 -AllowPaid.'
    exit 2
}
& uv run --directory apps/api python -m scripts.verification A
$gateExit = $LASTEXITCODE
exit $gateExit
