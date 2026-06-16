# Start all Eventrio microservices in the background (Windows) - LOCAL Maven mode.
# For Docker Desktop (recommended):  .\scripts\docker-up.ps1
#
# Usage: .\scripts\start-all.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        Write-Warning ".env not found at $Path - using defaults only."
        return
    }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        if ($line -match '^\s*([^#=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($value.Length -ge 2) {
                if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                    ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
            }
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Host "Loaded environment from .env"
    if ($env:MONGO_URI -match "mongodb\+srv") {
        Write-Host "MongoDB: Atlas (online)"
    } else {
        Write-Host "MongoDB: $($env:MONGO_URI)"
    }
}

Import-DotEnv (Join-Path $Root ".env")

$LogDir = Join-Path $Root "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-Host "LOCAL mode: services run as Java processes (not visible in Docker Desktop)."
Write-Host "For Docker containers use: .\scripts\docker-up.ps1"
Write-Host "Ensure Redis is running: docker compose up -d redis"
Write-Host ""

$Services = @(
    @{ Module = "eventrio-user-service";            Port = 8082 },
    @{ Module = "eventrio-organization-service";   Port = 8083 },
    @{ Module = "eventrio-event-service";           Port = 8084 },
    @{ Module = "eventrio-collaboration-service";   Port = 8085 },
    @{ Module = "eventrio-ticketing-service";       Port = 8086 },
    @{ Module = "eventrio-payment-service";         Port = 8087 },
    @{ Module = "eventrio-notification-service";    Port = 8088 },
    @{ Module = "eventrio-ai-orchestrator-service"; Port = 8089 },
    @{ Module = "eventrio-web-service";             Port = 8090 },
    @{ Module = "eventrio-gateway";                 Port = 8080 }
)

Write-Host "Starting Eventrio microservices from $Root ..."
Write-Host "Logs directory: $LogDir"
Write-Host ""

foreach ($svc in $Services) {
    $logFile = Join-Path $LogDir "$($svc.Module).log"
    $errFile = Join-Path $LogDir "$($svc.Module).err.log"

    $proc = Start-Process -FilePath "mvn" `
        -ArgumentList "spring-boot:run", "-pl", $svc.Module, "-q" `
        -WorkingDirectory $Root `
        -RedirectStandardOutput $logFile `
        -RedirectStandardError $errFile `
        -PassThru `
        -WindowStyle Hidden

    Write-Host ("  [{0,4}] {1,-40} PID {2}" -f $svc.Port, $svc.Module, $proc.Id)
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "All services launched. Open: http://localhost:8080"
Write-Host 'Tail logs:  Get-Content logs\eventrio-gateway.log -Wait -Tail 50'
Write-Host 'Stop all:   Get-Process java -ErrorAction SilentlyContinue | Stop-Process'
