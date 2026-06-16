#!/usr/bin/env bash
# Start all Eventrio services as Docker containers
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: .env not found. Copy .env.example to .env first."
  exit 1
fi

pkill -f "spring-boot:run" 2>/dev/null || true

echo "Building and starting all containers..."
docker compose up -d --build

echo ""
echo "All services running in Docker. Open http://localhost:8080"
echo "docker compose ps"
echo "docker compose logs -f eventrio-gateway"
echo "docker compose down"
