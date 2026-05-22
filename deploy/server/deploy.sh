#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/leonovcare-platform/current}"
ENV_FILE="${ENV_FILE:-$APP_ROOT/backend/.env}"
SKIP_DB_BACKUP="${SKIP_DB_BACKUP:-false}"
DB_BACKUP_DIR="${DB_BACKUP_DIR:-/opt/leonovcare-platform/backups/db}"
HEALTHCHECK_URL="${HEALTHCHECK_URL:-http://127.0.0.1:8510/healthz}"
READYCHECK_URL="${READYCHECK_URL:-http://127.0.0.1:8510/readyz}"
DOMAIN_LOCK_ENABLED="${DOMAIN_LOCK_ENABLED:-true}"
PROTECTED_DOMAIN="${PROTECTED_DOMAIN:-leonovcare.ru}"
PROTECTED_DOMAIN_NGINX_CONFIG="${PROTECTED_DOMAIN_NGINX_CONFIG:-/etc/nginx/sites-available/leonovcare.ru}"

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

enforce_domain_lock() {
  if [[ "${DOMAIN_LOCK_ENABLED,,}" != "true" ]]; then
    echo "Skipping domain lock check because DOMAIN_LOCK_ENABLED=false"
    return 0
  fi

  if [ ! -f "$PROTECTED_DOMAIN_NGINX_CONFIG" ]; then
    echo "FATAL: protected domain config not found at $PROTECTED_DOMAIN_NGINX_CONFIG."
    echo "Refusing deploy because protected domain '$PROTECTED_DOMAIN' cannot be validated."
    exit 1
  fi

  local forbidden_root="$APP_ROOT/frontend/dist"
  local forbidden_api="127.0.0.1:8510"
  local forbidden_frontend="127.0.0.1:8511"

  if grep -Fq "$forbidden_root" "$PROTECTED_DOMAIN_NGINX_CONFIG"; then
    echo "FATAL: protected domain '$PROTECTED_DOMAIN' points to '$forbidden_root'."
    echo "Restore the main site on $PROTECTED_DOMAIN before deploying LeonovCarePlatform."
    exit 1
  fi

  if grep -Fq "$forbidden_api" "$PROTECTED_DOMAIN_NGINX_CONFIG"; then
    echo "FATAL: protected domain '$PROTECTED_DOMAIN' proxies API to '$forbidden_api'."
    echo "Restore the main site on $PROTECTED_DOMAIN before deploying LeonovCarePlatform."
    exit 1
  fi

  if grep -Fq "$forbidden_frontend" "$PROTECTED_DOMAIN_NGINX_CONFIG"; then
    echo "FATAL: protected domain '$PROTECTED_DOMAIN' proxies frontend to '$forbidden_frontend'."
    echo "Restore the main site on $PROTECTED_DOMAIN before deploying LeonovCarePlatform."
    exit 1
  fi

  echo "Domain lock check passed for $PROTECTED_DOMAIN"
}

enforce_domain_lock

read_env_value() {
  local key="$1"
  local file="$2"
  if [ ! -f "$file" ]; then
    return 1
  fi
  awk -F= -v wanted="$key" '
    $1 == wanted {
      value = substr($0, index($0, "=") + 1)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      if ((value ~ /^".*"$/) || (value ~ /^'\''.*'\''$/)) {
        value = substr(value, 2, length(value) - 2)
      }
      print value
      exit
    }
  ' "$file"
}

export_if_missing() {
  local key="$1"
  local current_value="${!key:-}"
  if [ -n "$current_value" ]; then
    return 0
  fi
  local loaded_value
  loaded_value="$(read_env_value "$key" "$ENV_FILE" || true)"
  if [ -n "$loaded_value" ]; then
    export "${key}=${loaded_value}"
  fi
}

export_if_missing DATABASE_URL
export_if_missing JWT_ACCESS_SECRET
export_if_missing JWT_REFRESH_SECRET

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
# В production по умолчанию используем same-origin API через nginx `/api/v1`,
# чтобы не ломаться на mixed-content/CORS при HTTPS-домене.
export VITE_API_URL="${VITE_API_URL:-/api/v1}"
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
