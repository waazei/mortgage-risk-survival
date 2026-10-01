$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$ArchivePath = Join-Path $ProjectRoot "mortgage-risk-source-$Stamp.zip"

Add-Type -AssemblyName System.IO.Compression.FileSystem
$Stream = [System.IO.File]::Open($ArchivePath, [System.IO.FileMode]::CreateNew)
$Archive = [System.IO.Compression.ZipArchive]::new($Stream, [System.IO.Compression.ZipArchiveMode]::Create)

try {
    $Files = @()
    foreach ($Name in @('README.md', 'dashboard_server.py', 'run_backend.py', 'requirements.txt', 'requirements-dashboard.txt', 'setup.ps1')) {
        $Path = Join-Path $ProjectRoot $Name
        if (Test-Path $Path -PathType Leaf) { $Files += Get-Item -LiteralPath $Path }
    }
    foreach ($Folder in @('src', 'web', 'data\results')) {
        $Path = Join-Path $ProjectRoot $Folder
        if (Test-Path $Path -PathType Container) {
            $Files += Get-ChildItem -LiteralPath $Path -File -Recurse | Where-Object { $_.FullName -notmatch '[\\/]__pycache__([\\/]|$)' }
        }
    }

    foreach ($File in $Files) {
        $RelativePath = $File.FullName.Substring($ProjectRoot.TrimEnd('\').Length).TrimStart('\').Replace('\', '/')
        [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($Archive, $File.FullName, $RelativePath, [System.IO.Compression.CompressionLevel]::Optimal)
    }
} finally {
    $Archive.Dispose()
    $Stream.Dispose()
}

Write-Host "Da tao goi ma nguon: $ArchivePath"
Write-Host 'Goi nay kem data/results de mo dashboard tong hop; khong gom raw, standardized hay analysis Parquet.'
