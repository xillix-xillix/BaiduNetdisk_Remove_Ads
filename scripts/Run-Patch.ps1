param([ValidateSet('apply','restore')][string]$Mode)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$localPath=Join-Path $root 'install-path.local.txt'
try {
    if(Test-Path -LiteralPath $localPath){
        $installPath=(Get-Content -LiteralPath $localPath -Raw).Trim().Trim('"')
    } else {
        $installPath=(Read-Host 'Enter BaiduNetdisk installation folder (without quotes)').Trim().Trim('"')
    }
    if(-not (Test-Path -LiteralPath (Join-Path $installPath 'module\BrowserEngine\resources\core.asar'))){throw 'core.asar not found under that installation folder.'}
    $python=Get-Command python -ErrorAction Stop
    $log=Join-Path $root 'last-run.log'
    Push-Location $PSScriptRoot
    try {
        & $python.Source (Join-Path $PSScriptRoot 'clean_netdisk.py') $Mode --path $installPath 2>&1 | Tee-Object -FilePath $log
        $result=$LASTEXITCODE
    } finally {Pop-Location}
    Write-Host "Exit code: $result"
    Write-Host "Log: $log"
    exit $result
} catch {Write-Host ('ERROR: '+$_.Exception.Message);exit 1}
