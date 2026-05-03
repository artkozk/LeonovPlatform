#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/leonovcare-platform/current"

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
