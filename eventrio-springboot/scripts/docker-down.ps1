# Force-stop all Eventrio containers quickly (use when Docker Desktop delete hangs)
# Usage: .\scripts\docker-down.ps1

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Stopping Eventrio stack (force, 1s grace)..."

Get-Process docker -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

docker compose down -t 1 --remove-orphans
if ($LASTEXITCODE -ne 0) {
    Write-Host "compose down failed - killing containers..."
    $ids = docker ps -q --filter "name=eventrio" 2>$null
    if ($ids) {
        foreach ($id in $ids) {
            docker kill $id 2>$null | Out-Null
        }
    }
    docker compose down -t 0 --remove-orphans
}

Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

$remaining = docker ps -q --filter "name=eventrio" 2>$null
if ($remaining) {
    Write-Host "Some containers still running. Try restarting Docker Desktop, then run this script again."
} else {
    Write-Host "All Eventrio containers stopped."
}
