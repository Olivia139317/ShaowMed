$ErrorActionPreference = "Stop"

$containerName = "shadowme-mock-backend"
$existing = docker ps -a --filter "name=^/$containerName$" --format "{{.Names}}"

if ($existing -eq $containerName) {
    docker rm -f $containerName | Out-Null
    Write-Host "Stopped and removed $containerName"
} else {
    Write-Host "$containerName is not running"
}
