param([switch]$AllowPaid)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location (Split-Path $PSScriptRoot -Parent)
$gateArgs = @('run','--directory','apps/api','python','-m','scripts.verification','B')
if ($AllowPaid) { $gateArgs += '--allow-paid' }
& uv @gateArgs
$gateExit = $LASTEXITCODE
exit $gateExit
