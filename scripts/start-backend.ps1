param(
  [int]$Port = 5000
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "mock-backend"

Write-Host "Starting ShadowMe mock backend on http://localhost:$Port"
Write-Host "Backend directory: $BackendDir"

Push-Location $BackendDir
try {
  if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not available on PATH."
  }

  python -m pip install -r requirements.txt
  $env:PORT = "$Port"
  python server.py
}
finally {
  Pop-Location
}
