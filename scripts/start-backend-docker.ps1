$ErrorActionPreference = "Stop"

$imageName = "shadowme-mock-backend:latest"
$containerName = "shadowme-mock-backend"
$root = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $root "mock-backend"

$existing = docker ps -a --filter "name=^/$containerName$" --format "{{.Names}}"
if ($existing -eq $containerName) {
    docker rm -f $containerName | Out-Null
}

$portOpen = Test-NetConnection -ComputerName 127.0.0.1 -Port 5000 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($portOpen) {
    Write-Host "Port 5000 is already in use. Stop the local backend or other service before starting Docker backend."
    exit 1
}

docker build -t $imageName $backendDir
docker run -d --name $containerName -p 5000:5000 --restart unless-stopped $imageName | Out-Null

Start-Sleep -Seconds 2
$health = Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 http://localhost:5000/health
Write-Host $health.Content
