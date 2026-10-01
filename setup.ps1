param(
    [switch]$DashboardOnly
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = 'py'
    $PythonPrefix = @('-3')
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCommand = 'python'
    $PythonPrefix = @()
} else {
    throw 'Chua tim thay Python. Cai Python 3.11+ roi chay lai setup.ps1.'
}

$VersionText = & $PythonCommand @PythonPrefix -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
if ($LASTEXITCODE -ne 0) { throw 'Khong the chay Python. Hay kiem tra lai cai dat Python.' }
$Version = [version]$VersionText
if ($Version -lt [version]'3.11') { throw "Can Python 3.11 tro len; hien tai la $VersionText." }

$VenvPython = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $VenvPython)) {
    Write-Host "Tao moi truong Python voi Python $VersionText..."
    & $PythonCommand @PythonPrefix -m venv (Join-Path $ProjectRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Tao moi truong Python that bai.' }
}

$Requirements = if ($DashboardOnly) { 'requirements-dashboard.txt' } else { 'requirements.txt' }
Write-Host "Cai thu vien tu $Requirements..."
& $VenvPython -m pip install -r (Join-Path $ProjectRoot $Requirements)
if ($LASTEXITCODE -ne 0) { throw 'Cai thu vien that bai. Kiem tra ket noi Internet va chay lai setup.ps1.' }

Write-Host ''
Write-Host 'Cai dat xong.'
if ($DashboardOnly) {
    Write-Host 'Chay dashboard: .\.venv\Scripts\python.exe dashboard_server.py'
    Write-Host 'Che do nay khong bao gom tra cuu Loan ID neu chua co Parquet loan-level.'
} else {
    Write-Host 'Dashboard: .\.venv\Scripts\python.exe dashboard_server.py'
    Write-Host 'Pipeline:  .\.venv\Scripts\python.exe run_backend.py all'
    Write-Host 'Hay chuan bi du lieu dau vao trong data/ truoc khi chay pipeline.'
}
