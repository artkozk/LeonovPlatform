#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8510/api/v1}"
EMAIL="student-$(date +%s)@demo.local"
NICKNAME="student$(date +%s)"
FIRST_NAME="Smoke"
LAST_NAME="Tester"
PASSWORD="StrongPassword123!"

echo "Health check"
curl -fsS "${API_URL%/api/v1}/healthz" >/dev/null

echo "Register"
REGISTER_PAYLOAD=$(FIRST_NAME="$FIRST_NAME" LAST_NAME="$LAST_NAME" NICKNAME="$NICKNAME" EMAIL="$EMAIL" PASSWORD="$PASSWORD" python3 - <<'PY'
import json
import os
print(json.dumps({
    "firstName": os.environ["FIRST_NAME"],
    "lastName": os.environ["LAST_NAME"],
    "nickname": os.environ["NICKNAME"],
    "email": os.environ["EMAIL"],
    "password": os.environ["PASSWORD"],
}))
PY
)
REGISTER=$(curl -fsS -X POST "$API_URL/auth/register" -H "Content-Type: application/json" -d "$REGISTER_PAYLOAD")
REGISTER_TOKEN=$(echo "$REGISTER" | python3 -c 'import sys,json;print(json.load(sys.stdin)["tokens"]["accessToken"])')
if [ -z "$REGISTER_TOKEN" ]; then
  echo "Register did not return access token" >&2
  exit 1
fi

echo "Login"
LOGIN=$(curl -fsS -X POST "$API_URL/auth/login" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
TOKEN=$(echo "$LOGIN" | python3 -c 'import sys,json;print(json.load(sys.stdin)["accessToken"])')
if [ -z "$TOKEN" ]; then
  echo "Login did not return access token" >&2
  exit 1
fi

echo "Get courses"
COURSES=$(curl -fsS "$API_URL/courses" -H "Authorization: Bearer $TOKEN")
COURSE_ID=$(echo "$COURSES" | python3 -c 'import sys,json;items=json.load(sys.stdin)["items"];print(items[0]["id"] if items else "")')

if [ -z "$COURSE_ID" ]; then
  echo "No course found" >&2
  exit 1
fi

echo "Get tasks catalog"
CATALOG=$(curl -fsS "$API_URL/courses/$COURSE_ID/tasks-catalog" -H "Authorization: Bearer $TOKEN")
TASK_ID=$(echo "$CATALOG" | python3 -c 'import sys,json;items=json.load(sys.stdin)["items"];first=items[0] if items else {};print(first.get("taskId") or first.get("id") or "")')
if [ -z "$TASK_ID" ]; then
  echo "No task found in tasks-catalog" >&2
  exit 1
fi

echo "Get task details"
TASK=$(curl -fsS "$API_URL/tasks/$TASK_ID" -H "Authorization: Bearer $TOKEN")
SUBMIT_PAYLOAD=$(TASK_JSON="$TASK" python3 - <<'PY'
import json
import os

task = json.loads(os.environ["TASK_JSON"]).get("task", {})
language = str(task.get("language", "")).strip().lower()
source = str(task.get("starterCode", "")).strip()
if not source:
    if language == "sql":
        source = "SELECT 1;"
    elif language in {"python", "python3", "py"}:
        source = 'print("smoke")'
    else:
        source = 'public class Main { public static void main(String[] args) { System.out.println("smoke"); } }'
print(json.dumps({"sourceCode": source}))
PY
)

echo "Create submission"
SUBMISSION=$(curl -fsS -X POST "$API_URL/tasks/$TASK_ID/submissions" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$SUBMIT_PAYLOAD")
SUBMISSION_ID=$(echo "$SUBMISSION" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("submissionId",""))')
if [ -z "$SUBMISSION_ID" ]; then
  echo "Submission did not return submissionId" >&2
  exit 1
fi

echo "Smoke OK"
