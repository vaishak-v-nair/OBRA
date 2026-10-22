param([switch]$AllowPaid)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not $AllowPaid) {
    Write-Output 'BLOCKED: fresh owner authorization and -AllowPaid are required. No generation request was sent.'
    exit 2
}
$env:PYTHONIOENCODING = 'utf-8'
$env:ORBA_ARCHITECT_LIVE_OPT_IN = '1'
& uv run --directory apps/api python -m scripts.architect_verification B --allow-paid
$gateExit = $LASTEXITCODE
if ($gateExit -eq 0) {
    & uv run --directory apps/api python -m scripts.architect_verification summary
    exit $LASTEXITCODE
}
exit $gateExit
