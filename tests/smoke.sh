#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8510/api/v1}"
EMAIL="student-$(date +%s)@demo.local"
USERNAME="student$(date +%s)"
PASSWORD="StrongPassword123!"

echo "Health check"
curl -fsS "${API_URL%/api/v1}/healthz" >/dev/null

echo "Register"
REGISTER=$(curl -fsS -X POST "$API_URL/auth/register" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL\",\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")
TOKEN=$(echo "$REGISTER" | python3 -c 'import sys,json;print(json.load(sys.stdin)["tokens"]["accessToken"])')

echo "Get courses"
COURSES=$(curl -fsS "$API_URL/courses" -H "Authorization: Bearer $TOKEN")
COURSE_ID=$(echo "$COURSES" | python3 -c 'import sys,json;items=json.load(sys.stdin)["items"];print(items[0]["id"] if items else "")')

if [ -z "$COURSE_ID" ]; then
  echo "No course found" >&2
  exit 1
fi

echo "Smoke OK"
