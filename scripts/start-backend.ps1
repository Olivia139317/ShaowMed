param(
  [int]$Port = 5000
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "mock-backend"
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Write-Host "Starting ShadowMe mock backend on http://localhost:$Port"
Write-Host "Backend directory: $BackendDir"

Push-Location $BackendDir
try {
  if (-not (Test-Path $VenvPython)) {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
      throw "Python is not available on PATH."
    }

    Write-Host "Creating project virtual environment..."
    python -m venv (Join-Path $RepoRoot ".venv")
  }

  if (-not (Test-Path $VenvPython)) {
    throw "Python is not available on PATH."
  }

  & $VenvPython -m pip install -r requirements.txt
  $env:PORT = "$Port"
  & $VenvPython server.py
}
finally {
  Pop-Location
}
