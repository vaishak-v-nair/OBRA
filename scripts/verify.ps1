$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot
New-Item -ItemType Directory -Force docs/evidence | Out-Null
Start-Transcript -Path docs/evidence/verification-transcript.txt -Force
function Run-Check([string]$Executable, [string[]]$Arguments) {
    Write-Output "COMMAND: $Executable $($Arguments -join ' ')"
    & $Executable @Arguments 2>&1 | ForEach-Object { Write-Output "$_" }
    $commandExit = $LASTEXITCODE
    Write-Output "EXIT: $commandExit"
    if ($commandExit -ne 0) { throw "Check failed with exit $commandExit" }
}
try {
    Run-Check docker @('compose','-f','infra/compose.yaml','--profile','test','up','-d','--wait')
    Run-Check uv @('sync','--locked','--directory','apps/api')
    Run-Check npm @('exec','--yes','--package=pnpm@12.14.0','--','pnpm','install','--frozen-lockfile')
    Run-Check npm @('exec','--yes','--package=pnpm@12.14.0','--','pnpm','peers','check')
    Run-Check uv @('run','--directory','apps/api','alembic','upgrade','head')
    Run-Check uv @('run','--directory','apps/api','alembic','check')
    Run-Check uv @('run','--directory','apps/api','pytest','-q')
    Run-Check uv @('run','--directory','apps/api','ruff','check','.')
    Run-Check uv @('run','--directory','apps/api','ruff','format','--check','.')
    foreach ($task in @('typecheck','lint','build','test:e2e')) {
        Run-Check npm @('exec','--yes','--package=pnpm@12.14.0','--','pnpm',$task)
    }
} finally {
    Stop-Transcript
}
