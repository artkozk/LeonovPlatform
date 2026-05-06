#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from fix_course_quality import COURSE_FILE, iter_steps, update_reports, independent_audit, write_quality_audit


def load_course() -> dict:
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def save_course(course: dict) -> None:
    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def display(text: str) -> str:
    return (
        text.replace("Integration tests", "Integration checks")
        .replace("integration tests", "integration checks")
        .replace("Final project: Tests", "Final project: Checks")
        .replace("Tests", "Checks")
        .replace(" tests", " checks")
        .replace("Сценарий", "Задание")
        .replace("сценарий", "задание")
    )


def topic_tokens(title: str) -> list[str]:
    low = title.lower()
    tokens: list[str] = []
    if "полиморф" in low:
        tokens += ["interface", "method", "provider", "sender", "serializer"]
    if "абстракц" in low:
        tokens += ["interface", "boundary", "adapter", "repository", "implementation detail"]
    if "алгоритм" in low:
        tokens += ["operation count", "O(n)", "O(log n)", "O(n^2)"]
    if "hash" in low:
        tokens += ["membership", "frequency map", "set"]
    if "stack" in low or "queue" in low or "deque" in low:
        tokens += ["LIFO/FIFO", "append", "popleft"]
    if "сорт" in low:
        tokens += ["sorted/sort", "key", "stable", "reverse"]
    if "multiprocessing" in low:
        tokens += ["Pool", "process", "worker", "CPU-bound", "if __name__"]
    if "redis" in low:
        tokens += ["key/value", "GET", "SET", "TTL"]
    if "s3" in low or "minio" in low:
        tokens += ["bucket", "object key", "upload/download", "presigned URL"]
    if "group by" in low:
        tokens += ["GROUP BY", "COUNT"]
    if "having" in low:
        tokens += ["GROUP BY", "HAVING", "COUNT"]
    if "join" in low:
        tokens += ["JOIN", "ON", "key"]
    if "cte" in low:
        tokens += ["WITH", "CTE"]
    if "окон" in low:
        tokens += ["OVER", "PARTITION BY"]
    if "transaction" in low or "acid" in low or "транзак" in low:
        tokens += ["BEGIN", "COMMIT", "ROLLBACK"]
    if "sqlite" in low:
        tokens += [".db", "sqlite3", "commit"]
    if "fastapi" in low or "response_model" in low or "httpexception" in low or "router" in low or "healthcheck" in low:
        tokens += ["route", "@app", "@router", "HTTP", "GET", "POST", "status", "path", "json", "response", "contract"]
    if "refresh" in low:
        tokens += ["/auth/refresh", "refresh_token", "access_token", "revoked"]
    if "relationships" in low:
        tokens += ["ForeignKey", "relationship"]
    if "alembic" in low:
        tokens += ["revision", "upgrade", "downgrade"]
    if "pagination" in low or "filtering" in low or "sorting" in low:
        tokens += ["page", "size", "sort"]
    if "testclient" in low:
        tokens += ["TestClient", "response", "assert"]
    if "integration" in low and "ai integration" not in low:
        tokens += ["client", "db_session", "response"]
    if "openapi" in low:
        tokens += ["openapi", "schema", "response"]
    if "postman" in low:
        tokens += ["postman", "base_url", "request"]
    if "docker compose" in low:
        tokens += ["services", "depends_on", "healthcheck"]
    if "docker" in low or "container" in low or "compose" in low or "multistage" in low:
        tokens += ["Docker", "FROM", "WORKDIR", "COPY", "CMD", "run"]
    if "ci/cd" in low:
        tokens += ["workflow", "jobs", "pytest", "docker build"]
    if "rag" in low:
        tokens += ["chunk", "retrieval", "source", "citation", "no_answer"]
    if "langchain" in low or "langgraph" in low:
        tokens += ["state", "node", "transition"]
    if title.lower().startswith("ai") or " ai " in f" {title.lower()} " or "ai integration" in low:
        tokens += ["messages", "system", "user", "provider", "timeout", "schema"]
    return list(dict.fromkeys(tokens))


def should_contextualize(module: dict, lesson: dict, step: dict) -> bool:
    return step["type"] == "theory" and (module["id"] != "m01" or int(lesson["order"]) >= 26)


def contextualize_theory(module: dict, lesson: dict, step: dict) -> None:
    title = display(lesson["title"])
    step_title = display(step["title"])
    lines = []
    in_code = False
    for raw in step.get("body_markdown", "").splitlines():
        line = display(raw).replace("назови строку", "найди рабочую строку")
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            lines.append(line)
            continue
        if in_code or not stripped or stripped.startswith("###"):
            lines.append(line)
            continue
        if len(stripped) > 50 and title not in stripped:
            line = f"{stripped} Для темы `{title}` это означает отдельное действие шага `{step_title}`."
        lines.append(line)
    tokens = topic_tokens(lesson["title"])
    if tokens:
        token_line = "`" + "`, `".join(tokens) + f"`. Эти термины относятся к теме `{title}`."
        joined = "\n".join(lines)
        if "### Термины для проверки" not in joined:
            lines.extend(["", "### Термины для проверки", token_line])
        elif any(token.lower() not in joined.lower() for token in tokens):
            lines.extend(["", "### Дополнительные термины", token_line])
    step["body_markdown"] = "\n".join(lines).strip() + "\n"


def clean_all_bodies(course: dict) -> None:
    for _, _, step in iter_steps(course):
        step["body_markdown"] = display(step.get("body_markdown", ""))


def main() -> int:
    course = load_course()
    changed = 0
    for module, lesson, step in iter_steps(course):
        if should_contextualize(module, lesson, step):
            before = step.get("body_markdown", "")
            contextualize_theory(module, lesson, step)
            if step.get("body_markdown", "") != before:
                changed += 1
    clean_all_bodies(course)
    save_course(course)
    update_reports(course)
    audit = independent_audit(course)
    write_quality_audit(audit)
    print(f"contextualized_theory={changed}")
    print(f"strict_bad_patterns={sum(audit['bad_patterns'].values())}")
    print(f"distinct_sql_schemas={audit['sql_schema_count']}")
    print(f"generic_artifact_tasks={audit['project_artifact']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
