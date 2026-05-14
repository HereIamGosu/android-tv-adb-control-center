# build.ps1
# Run from repo root in an activated venv:
#   .\.venv\Scripts\Activate.ps1
#   .\build.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Installing PyInstaller..."
python -m pip install -r requirements-build.txt --quiet

Write-Host "Running PyInstaller..."
pyinstaller pyinstaller.spec --clean --noconfirm

$exe = "dist\AndroidTVADBControlCenter.exe"
if (Test-Path $exe) {
    $size = (Get-Item $exe).Length
    Write-Host "Build succeeded: $exe ($size bytes)"
} else {
    Write-Error "Build failed: $exe not found"
    exit 1
}
