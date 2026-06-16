# Start all Eventrio services as Docker containers (shows in Docker Desktop)
# Usage: .\scripts\docker-up.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path (Join-Path $Root ".env"))) {
    Write-Error ".env not found. Copy .env.example to .env and add your credentials."
}

# Stop any locally running Maven/Java instances from start-all.ps1
Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "Stopped any local Java processes (old start-all.ps1 runs)."
Write-Host ""

Write-Host "Building and starting all containers..."
Write-Host "This may take several minutes on first run."
Write-Host ""

docker compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "All services are running in Docker Desktop."
    Write-Host "Open: http://localhost:8080"
    Write-Host ""
    Write-Host "View status:  docker compose ps"
    Write-Host "View logs:    docker compose logs -f eventrio-gateway"
    Write-Host "Stop all:     .\scripts\docker-down.ps1"
}
