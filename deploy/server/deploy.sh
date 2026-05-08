#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/leonovcare-platform/current}"
SKIP_DB_BACKUP="${SKIP_DB_BACKUP:-false}"
DB_BACKUP_DIR="${DB_BACKUP_DIR:-/opt/leonovcare-platform/backups/db}"
HEALTHCHECK_URL="${HEALTHCHECK_URL:-http://127.0.0.1:8510/healthz}"
READYCHECK_URL="${READYCHECK_URL:-http://127.0.0.1:8510/readyz}"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd is required but not found in PATH"
    exit 1
  fi
}

require_cmd node
require_cmd npm
require_cmd go
require_cmd pm2
require_cmd curl

NODE_MAJOR="$(node -p "process.versions.node.split('.')[0]")"
NODE_MINOR="$(node -p "process.versions.node.split('.')[1]")"
if [ "$NODE_MAJOR" -lt 20 ] || { [ "$NODE_MAJOR" -eq 20 ] && [ "$NODE_MINOR" -lt 19 ]; }; then
  echo "Node.js >= 20.19.0 is required for frontend dependencies. Current: $(node -v)"
  exit 1
fi

if [[ "${SKIP_DB_BACKUP,,}" != "true" ]]; then
  echo "Running pre-deploy DB backup..."
  DB_BACKUP_DIR="$DB_BACKUP_DIR" bash "$APP_ROOT/deploy/server/backup-db.sh"
else
  echo "Skipping DB backup because SKIP_DB_BACKUP=true"
fi

cd "$APP_ROOT/backend"
go mod tidy
go test ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker
go build -o bin/leonovcare-migrator ./cmd/migrator

echo "Applying migrations via migrator..."
./bin/leonovcare-migrator

cd "$APP_ROOT/frontend"
npm ci
npm run test
export VITE_API_URL="${VITE_API_URL:-http://85.198.82.221:8510/api/v1}"
export VITE_GOOGLE_CLIENT_ID="${VITE_GOOGLE_CLIENT_ID:-${GOOGLE_CLIENT_ID:-}}"
npm run build

cd "$APP_ROOT"
pm2 delete leonovcare-api leonovcare-worker leonovcare-frontend >/dev/null 2>&1 || true
pm2 start deploy/server/ecosystem.config.cjs
pm2 save

echo "Running post-deploy health checks..."
curl -fsS "$HEALTHCHECK_URL" >/dev/null
curl -fsS "$READYCHECK_URL" >/dev/null

echo "Deployment completed and health checks passed"
