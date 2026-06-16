#!/usr/bin/env bash
# Start all Eventrio microservices in the background (Unix).
# Usage: ./scripts/start-all.sh
# Run from eventrio-springboot/ or anywhere; script resolves the project root.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Load .env if present
if [[ -f "$ROOT/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$ROOT/.env"
    set +a
    echo "Loaded environment from .env"
fi

LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

declare -a MODULES=(
    "eventrio-user-service:8082"
    "eventrio-organization-service:8083"
    "eventrio-event-service:8084"
    "eventrio-collaboration-service:8085"
    "eventrio-ticketing-service:8086"
    "eventrio-payment-service:8087"
    "eventrio-notification-service:8088"
    "eventrio-ai-orchestrator-service:8089"
    "eventrio-web-service:8090"
    "eventrio-gateway:8080"
)

echo "Starting Eventrio microservices from $ROOT ..."
echo "Logs directory: $LOG_DIR"
echo ""

PIDS_FILE="$LOG_DIR/service.pids"
: > "$PIDS_FILE"

for entry in "${MODULES[@]}"; do
    module="${entry%%:*}"
    port="${entry##*:}"
    log_file="$LOG_DIR/${module}.log"

    nohup mvn spring-boot:run -pl "$module" -q >> "$log_file" 2>&1 &
    pid=$!
    echo "$pid $module" >> "$PIDS_FILE"
    printf "  [%4s] %-40s PID %s\n" "$port" "$module" "$pid"
    sleep 4
done

echo ""
echo "All services launched. Gateway: http://localhost:8080"
echo "Tail logs:  tail -f logs/eventrio-gateway.log"
echo "Stop all:   xargs kill < logs/service.pids   # or: kill \$(cut -d' ' -f1 logs/service.pids)"
