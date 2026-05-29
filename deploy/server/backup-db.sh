#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/leonovcare-platform/current}"
ENV_FILE="${ENV_FILE:-$APP_ROOT/backend/.env}"
DB_BACKUP_DIR="${DB_BACKUP_DIR:-/opt/leonovcare-platform/backups/db}"
BACKUP_PREFIX="${BACKUP_PREFIX:-leonovcare_db}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
SKIP_RETENTION="${SKIP_RETENTION:-false}"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd is required but not found in PATH"
    exit 1
  fi
}

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

require_cmd pg_dump
require_cmd gzip
require_cmd mkdir
require_cmd find

sanitize_database_url() {
  local raw="$1"
  echo "$raw" | sed -E 's/[?&]pool_[^&=]+=[^&]*//g; s/\?&/\?/g; s/[?&]$//g'
}

DATABASE_URL="${DATABASE_URL:-}"
if [ -z "$DATABASE_URL" ]; then
  DATABASE_URL="$(read_env_value "DATABASE_URL" "$ENV_FILE" || true)"
fi
if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL is required for backup and was not found in env or $ENV_FILE"
  exit 1
fi
DATABASE_URL="$(sanitize_database_url "$DATABASE_URL")"

mkdir -p "$DB_BACKUP_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_file="$DB_BACKUP_DIR/${BACKUP_PREFIX}_${timestamp}.sql.gz"

tmp_file="${backup_file}.tmp"
pg_dump "$DATABASE_URL" | gzip -9 >"$tmp_file"
mv "$tmp_file" "$backup_file"
chmod 600 "$backup_file"

if [[ "${SKIP_RETENTION,,}" != "true" ]]; then
  if [[ "$BACKUP_RETENTION_DAYS" =~ ^[0-9]+$ ]] && [ "$BACKUP_RETENTION_DAYS" -gt 0 ]; then
    find "$DB_BACKUP_DIR" -maxdepth 1 -type f -name "${BACKUP_PREFIX}_*.sql.gz" -mtime +"$BACKUP_RETENTION_DAYS" -delete
  fi
fi

echo "DB backup created: $backup_file"
