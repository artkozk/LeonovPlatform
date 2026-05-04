#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/leonovcare-platform/current"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required but not found in PATH"
  exit 1
fi

NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
NODE_MINOR="$(node -p 'process.versions.node.split(".")[1]')"
if [ "$NODE_MAJOR" -lt 20 ] || { [ "$NODE_MAJOR" -eq 20 ] && [ "$NODE_MINOR" -lt 19 ]; }; then
  echo "Node.js >= 20.19.0 is required for frontend dependencies. Current: $(node -v)"
  exit 1
fi

cd "$APP_ROOT/backend"
go mod tidy
go test ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker

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

echo "Deployment completed"
