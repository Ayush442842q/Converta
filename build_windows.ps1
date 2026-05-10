$ErrorActionPreference = "Stop"

$Python = "python"
if (Get-Command py -ErrorAction SilentlyContinue) {
    $Python = "py -3"
}

if (-not (Test-Path ".venv")) {
    Invoke-Expression "$Python -m venv .venv"
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\pyinstaller.exe `
    --noconfirm `
    --clean `
    --windowed `
    --name Converta `
    --add-data "static;static" `
    --add-data "templates;templates" `
    desktop_app.py

Write-Host ""
Write-Host "Build complete: dist\Converta\Converta.exe"
Write-Host "For widest conversion support, install LibreOffice and Pandoc on this Windows machine."
