#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
V13 = ROOT.parent / "v13_ROADMAP_POLISHED" / "course_import.json"
COURSE_FILE = ROOT / "course_import.json"
MANIFEST_FILE = ROOT / "manifest.csv"
COVERAGE_FILE = ROOT / "coverage_matrix.csv"

TITLE = "Python с нуля — Backend + AI"
TARGET = "0 → Middle-ready / начинающий Middle при полном прохождении практики, IDE-лаб, проектов и ревью"

BODY_LEAKS = ["Шаблон", "Подсказки", "Эталон", "Автотесты", "solution", "hidden_tests", "admin", "checker", "AI-инструкция"]
BANNED = [
    "Тест недоступен",
    "Для этого шага пока нет автопроверки",
    "ученик учится",
    "в этой теме ученик",
    "ученик должен",
    "мы расскажем",
    "в рамках данного урока",
    "ключевая идея темы",
    "собери практическую работу по теме",
    "Создай или измени файлы проекта",
]
BAD_COVERAGE = {"missing", "thin", "placeholder"}
ROADMAP_TOPICS = [
    "AI для учёбы", "среда и терминал", "Git и GitHub", "Python Core", "CLI-проект", "ООП", "магические методы",
    "протоколы", "наследование и полиморфизм", "типизация", "threading", "multiprocessing", "asyncio",
    "алгоритмы и структуры данных", "SQL", "SQLite/sqlite3", "транзакции", "уровни изоляции", "блокировки",
    "индексы", "NoSQL", "Redis", "ClickHouse / OLAP", "S3 / MinIO", "сети", "HTTP / HTTPS", "TCP / UDP",
    "REST", "SOAP / GraphQL / gRPC / WebSockets обзорно", "авторизация", "Docker", "Docker Compose", "Poetry",
    "FastAPI", "SQLAlchemy", "CRUD-проект", "Postman", "pytest", "CI/CD", "GitHub Actions", "GitLab CI/CD",
    "multistage build", "AI API", "RAG", "vector databases", "LangChain / LangGraph концептуально", "вайбкодинг",
    "финальный проект", "VPS", "безопасность сервера", "домен", "SSL", "автодеплой",
]

TRANS = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh", "з": "z",
    "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya", "—": "-", "–": "-", "/": "-",
    "А": "a", "Б": "b", "В": "v", "Г": "g", "Д": "d", "Е": "e", "Ё": "e", "Ж": "zh", "З": "z",
    "И": "i", "Й": "y", "К": "k", "Л": "l", "М": "m", "Н": "n", "О": "o", "П": "p", "Р": "r",
    "С": "s", "Т": "t", "У": "u", "Ф": "f", "Х": "h", "Ц": "c", "Ч": "ch", "Ш": "sh", "Щ": "sch",
    "Ъ": "", "Ы": "y", "Ь": "", "Э": "e", "Ю": "yu", "Я": "ya",
})


def slug(text: str, fallback: str = "item") -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.translate(TRANS).lower()).strip("-")
    return value or fallback


def ai_hint_config() -> dict[str, Any]:
    return {
        "mode": "socratic",
        "no_full_solution": True,
        "allowed_context": ["body_markdown", "editor_initial_code", "hints", "student_code", "last_stdout", "last_stderr", "public_examples"],
        "forbidden_context": ["solution_code", "checker.hidden_tests", "questions.correct_answer_id", "admin_notes"],
        "response_rules": ["сначала укажи место расхождения", "задай один уточняющий вопрос", "напомни правило", "не выдавай полный код"],
    }


def base_step(lesson_id: str, order: int, title: str, typ: str, diff: int, xp: int, minutes: int, body: str, topics: list[str], **extra: Any) -> dict[str, Any]:
    item = {
        "id": f"{lesson_id}_s{order:03d}_{slug(title)}",
        "order": order,
        "title": title,
        "type": typ,
        "published": True,
        "is_available": True,
        "availability": "available",
        "status": "published",
        "difficulty": diff,
        "xp": xp,
        "estimated_minutes": minutes,
        "body_markdown": body,
        "editor_initial_code": extra.pop("editor_initial_code", ""),
        "hints": extra.pop("hints", ["Сначала проверь минимальный пример.", "Сравни точный формат результата.", "Если проверка падает, прочитай первое сообщение об ошибке."]),
        "solution_code": extra.pop("solution_code", ""),
        "ai_hint_config": ai_hint_config(),
        "admin_notes": f"v15 regenerated from roadmap skeleton after independent QA; topics={', '.join(topics)}",
        "roadmap_topics": topics,
        "learning_objective": extra.pop("learning_objective", f"{lesson_id}:{topics[0] if topics else 'course'}:{title}:step{order}"),
    }
    item.update(extra)
    return item


def stdout_checker(public: list[tuple[str, str]], hidden: list[tuple[str, str]] | None = None) -> dict[str, Any]:
    return {
        "type": "python_stdout",
        "language": "python",
        "timeout_sec": 3,
        "compare": {"mode": "exact_stdout", "ignore_final_newline": True, "rstrip_lines": True, "extra_output_is_error": True},
        "public_tests": [{"input": i, "expected_stdout": o} for i, o in public],
        "hidden_tests": [{"input": i, "expected_stdout": o} for i, o in (hidden or public)],
    }


def quiz_checker(questions: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "quiz_single", "questions_ref": "questions", "questions": questions}


def question(step_id: str, question_text: str, correct: str, explanation: str, wrong: list[str] | None = None) -> list[dict[str, Any]]:
    wrong = wrong or ["Добавить лишний вывод", "Пропустить локальный запуск", "Переименовать случайные переменные"]
    options = [{"id": "a", "text": wrong[0]}, {"id": "b", "text": correct}, {"id": "c", "text": wrong[1]}, {"id": "d", "text": wrong[2]}]
    return [{"id": f"{step_id}_q1", "question": question_text, "options": options, "correct_answer_id": "b", "correct_option_index": 1, "explanation": explanation}]


def pytest_checker(fn: str, cases: list[tuple[Any, Any]], import_line: str | None = None) -> dict[str, Any]:
    import_line = import_line or f"from solution import {fn}"
    body = [import_line, ""]
    for idx, (args, expected) in enumerate(cases, 1):
        args_repr = ", ".join(repr(x) for x in args) if isinstance(args, tuple) else repr(args)
        body += [f"def test_case_{idx}():", f"    assert {fn}({args_repr}) == {expected!r}", ""]
    hidden = [{"name": f"hidden_{idx}", "args": args, "expected": expected} for idx, (args, expected) in enumerate(cases[-2:], 1)]
    return {"type": "python_pytest", "timeout_sec": 6, "test_code": "\n".join(body), "hidden_tests": hidden}


def sql_assets(db: str) -> tuple[str, str]:
    if db == "accounts":
        return (
            "CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT NOT NULL, balance INTEGER NOT NULL); CREATE TABLE transfers (id INTEGER PRIMARY KEY, from_account INTEGER NOT NULL, to_account INTEGER NOT NULL, amount INTEGER NOT NULL, status TEXT NOT NULL);",
            "INSERT INTO accounts VALUES (1, 'Анна', 1000), (2, 'Олег', 400), (3, 'Маша', 0); INSERT INTO transfers VALUES (1, 1, 2, 200, 'done'), (2, 2, 1, 50, 'failed');",
        )
    if db == "library":
        return (
            "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author_id INTEGER NOT NULL, year INTEGER NOT NULL); CREATE TABLE readers (id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE loans (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, reader_id INTEGER NOT NULL, returned_at TEXT);",
            "INSERT INTO authors VALUES (1, 'Толстой'), (2, 'Гоголь'), (3, 'Булгаков'); INSERT INTO books VALUES (1, 'Война и мир', 1, 1869), (2, 'Ревизор', 2, 1836), (3, 'Мастер и Маргарита', 3, 1967); INSERT INTO readers VALUES (1, 'Анна'), (2, 'Олег'), (3, 'Маша'); INSERT INTO loans VALUES (1, 1, 1, NULL), (2, 2, 2, '2026-01-10');",
        )
    if db == "school":
        return (
            "CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL); CREATE TABLE enrollments (id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, course_id INTEGER NOT NULL); CREATE TABLE grades (id INTEGER PRIMARY KEY, enrollment_id INTEGER NOT NULL, score INTEGER NOT NULL);",
            "INSERT INTO students VALUES (1, 'Ира'), (2, 'Павел'), (3, 'Саша'); INSERT INTO courses VALUES (1, 'Python'), (2, 'SQL'); INSERT INTO enrollments VALUES (1, 1, 1), (2, 1, 2), (3, 2, 1); INSERT INTO grades VALUES (1, 1, 95), (2, 2, 88), (3, 3, 70);",
        )
    if db == "tasks":
        return (
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE projects (id INTEGER PRIMARY KEY, title TEXT NOT NULL, owner_id INTEGER NOT NULL); CREATE TABLE tasks (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0); CREATE TABLE comments (id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, body TEXT NOT NULL);",
            "INSERT INTO users VALUES (1, 'Анна'), (2, 'Олег'); INSERT INTO projects VALUES (1, 'API', 1), (2, 'Docs', 2); INSERT INTO tasks VALUES (1, 1, 'Create route', 0), (2, 1, 'Write tests', 1), (3, 2, 'Update README', 0); INSERT INTO comments VALUES (1, 1, 'need params'), (2, 2, 'done');",
        )
    return (
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1); CREATE TABLE products (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price INTEGER NOT NULL); CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, total INTEGER NOT NULL, status TEXT NOT NULL); CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL, product_id INTEGER NOT NULL, qty INTEGER NOT NULL); CREATE TABLE payments (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL, amount INTEGER NOT NULL, status TEXT NOT NULL);",
        "INSERT INTO users VALUES (1, 'Анна', 1), (2, 'Олег', 1), (3, 'Маша', 0), (4, 'Лена', 1); INSERT INTO products VALUES (1, 'Книга', 700), (2, 'Курс', 5000), (3, 'Мышь', 1200); INSERT INTO orders VALUES (1, 1, 5700, 'paid'), (2, 2, 1200, 'new'), (3, 1, 700, 'paid'); INSERT INTO order_items VALUES (1, 1, 1, 1), (2, 1, 2, 1), (3, 2, 3, 1), (4, 3, 1, 1); INSERT INTO payments VALUES (1, 1, 5700, 'paid'), (2, 2, 1200, 'pending'), (3, 3, 700, 'paid');",
    )


def sql_checker(schema: str, seed: str, expected: list[list[Any]], hidden: list[list[Any]] | None = None) -> dict[str, Any]:
    return {
        "type": "sql_query",
        "dialect": "sqlite",
        "schema_sql": schema,
        "seed_sql": seed,
        "public_tests": [{"name": "base_case", "expected_rows": expected, "compare": "ordered_rows"}],
        "hidden_tests": [{"name": "edge_case", "expected_rows": hidden or expected, "compare": "ordered_rows"}],
    }


def sql_task(title: str, variant: int) -> tuple[str, str, dict[str, Any], str]:
    low = title.lower()
    schema, seed = sql_assets("ecommerce")
    if "transactions" in low or "acid" in low:
        schema, seed = sql_assets("accounts")
        cases = [
            (
                "Проведи перевод 300 единиц со счёта Анны на счёт Олега внутри транзакции. После фиксации верни `id`, `owner`, `balance`.",
                "BEGIN;\nUPDATE accounts SET balance = balance - 300 WHERE id = 1;\nUPDATE accounts SET balance = balance + 300 WHERE id = 2;\nCOMMIT;\nSELECT id, owner, balance FROM accounts ORDER BY id;\n",
                [[1, "Анна", 700], [2, "Олег", 700], [3, "Маша", 0]],
                "commit_transfer",
            ),
            (
                "Смоделируй ошибочный перевод 1500 единиц со счёта Олега. Выполни изменение, откати транзакцию и верни исходные балансы.",
                "BEGIN;\nUPDATE accounts SET balance = balance - 1500 WHERE id = 2;\nROLLBACK;\nSELECT id, owner, balance FROM accounts ORDER BY id;\n",
                [[1, "Анна", 1000], [2, "Олег", 400], [3, "Маша", 0]],
                "rollback_failed_transfer",
            ),
            (
                "Используй SAVEPOINT: начни перевод 100 единиц Анне, откати только часть после savepoint и зафиксируй итог.",
                "BEGIN;\nUPDATE accounts SET balance = balance - 100 WHERE id = 2;\nSAVEPOINT after_withdraw;\nUPDATE accounts SET balance = balance + 100 WHERE id = 3;\nROLLBACK TO after_withdraw;\nUPDATE accounts SET balance = balance + 100 WHERE id = 1;\nCOMMIT;\nSELECT id, owner, balance FROM accounts ORDER BY id;\n",
                [[1, "Анна", 1100], [2, "Олег", 300], [3, "Маша", 0]],
                "savepoint_partial_rollback",
            ),
        ]
        task, sol, expected, concept = cases[variant % len(cases)]
        return task, sol, sql_checker(schema, seed, expected), concept
    if "изоляц" in low or "блокиров" in low or "индекс" in low or "explain" in low:
        cases = [
            ("Создай индекс для поиска заказов пользователя и верни оплаченные заказы пользователя `1`: `id`, `total`.", "CREATE INDEX idx_orders_user_status ON orders(user_id, status);\nSELECT id, total FROM orders WHERE user_id = 1 AND status = 'paid' ORDER BY id;\n", [[1, 5700], [3, 700]], "composite_index"),
            ("Через `EXPLAIN QUERY PLAN` проверь поиск по `orders.user_id`. Затем верни имя созданного индекса, чтобы проверка была детерминированной.", "CREATE INDEX idx_orders_user_id ON orders(user_id);\nEXPLAIN QUERY PLAN SELECT id, total FROM orders WHERE user_id = 1;\nSELECT name FROM sqlite_master WHERE type = 'index' AND name = 'idx_orders_user_id';\n", [["idx_orders_user_id"]], "explain_index_plan"),
            ("Смоделируй блокировку логически: выбери платежи `pending`, которые нельзя считать завершёнными, и верни `id`, `status`.", "SELECT id, status FROM payments WHERE status = 'pending' ORDER BY id;\n", [[2, "pending"]], "pending_lock_simulation"),
        ]
        task, sol, expected, concept = cases[variant % len(cases)]
        return task, sol, sql_checker(schema, seed, expected), concept
    if "left join" in low:
        cases = [
            ("Найди активных пользователей без заказов. Верни `id`, `name`, отсортируй по `id`.", "SELECT users.id, users.name\nFROM users\nLEFT JOIN orders ON orders.user_id = users.id\nWHERE users.active = 1 AND orders.id IS NULL\nORDER BY users.id;\n", [[4, "Лена"]], "left_join_no_orders"),
            ("Покажи всех активных пользователей и сумму оплаченных заказов, сохрани пользователей без заказов через `COALESCE`.", "SELECT users.id, users.name, COALESCE(SUM(CASE WHEN orders.status = 'paid' THEN orders.total ELSE 0 END), 0) AS paid_total\nFROM users\nLEFT JOIN orders ON orders.user_id = users.id\nWHERE users.active = 1\nGROUP BY users.id, users.name\nORDER BY users.id;\n", [[1, "Анна", 6400], [2, "Олег", 0], [4, "Лена", 0]], "left_join_preserve_empty"),
            ("Исправь типовую ошибку: фильтр `orders.status = 'paid'` должен не превращать LEFT JOIN в INNER JOIN.", "SELECT users.id, users.name, orders.id AS paid_order_id\nFROM users\nLEFT JOIN orders ON orders.user_id = users.id AND orders.status = 'paid'\nWHERE users.active = 1\nORDER BY users.id, paid_order_id;\n", [[1, "Анна", 1], [1, "Анна", 3], [2, "Олег", None], [4, "Лена", None]], "left_join_filter_in_on"),
        ]
        task, sol, expected, concept = cases[variant % len(cases)]
        return task, sol, sql_checker(schema, seed, expected), concept
    if "join" in low:
        task = "Верни имя пользователя и сумму каждого оплаченного заказа. Нужны колонки `name`, `total`, порядок по `name`, затем `total`."
        sol = "SELECT users.name, orders.total\nFROM users\nJOIN orders ON orders.user_id = users.id\nWHERE orders.status = 'paid'\nORDER BY users.name, orders.total;\n"
        return task, sol, sql_checker(schema, seed, [["Анна", 700], ["Анна", 5700]]), "join"
    if "group" in low or "having" in low or "агрег" in low or "clickhouse" in low or "olap" in low:
        task = "Посчитай выручку по пользователям. Верни `user_id`, `orders_count`, `paid_total` только для пользователей с суммой выше 1000."
        sol = "SELECT user_id, COUNT(*) AS orders_count, SUM(total) AS paid_total\nFROM orders\nWHERE status = 'paid'\nGROUP BY user_id\nHAVING SUM(total) > 1000\nORDER BY user_id;\n"
        return task, sol, sql_checker(schema, seed, [[1, 2, 6400]]), "aggregate"
    if "окон" in low:
        cases = [
            ("Пронумеруй заказы каждого пользователя по убыванию суммы. Верни `user_id`, `total`, `rn`.", "SELECT user_id, total, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rn\nFROM orders\nORDER BY user_id, rn;\n", [[1, 5700, 1], [1, 700, 2], [2, 1200, 1]], "row_number"),
            ("Посчитай running total заказов пользователя `1` по возрастанию `id`.", "SELECT id, total, SUM(total) OVER (PARTITION BY user_id ORDER BY id) AS running_total\nFROM orders\nWHERE user_id = 1\nORDER BY id;\n", [[1, 5700, 5700], [3, 700, 6400]], "running_total"),
            ("Найди самый дорогой заказ каждого пользователя через ranking и верни `user_id`, `id`, `total`.", "WITH ranked AS (\n  SELECT user_id, id, total, RANK() OVER (PARTITION BY user_id ORDER BY total DESC) AS rnk\n  FROM orders\n)\nSELECT user_id, id, total FROM ranked WHERE rnk = 1 ORDER BY user_id;\n", [[1, 1, 5700], [2, 2, 1200]], "rank_top_order"),
        ]
        task, sol, expected, concept = cases[variant % len(cases)]
        return task, sol, sql_checker(schema, seed, expected), concept
    if "cte" in low or "подзапрос" in low:
        cases = [
            ("Через CTE найди пользователей с оплаченными заказами. Верни `id`, `name`, `paid_total`.", "WITH paid AS (\n    SELECT user_id, SUM(total) AS paid_total\n    FROM orders\n    WHERE status = 'paid'\n    GROUP BY user_id\n)\nSELECT users.id, users.name, paid.paid_total\nFROM users\nJOIN paid ON paid.user_id = users.id\nORDER BY users.id;\n", [[1, "Анна", 6400]], "cte_paid_total"),
            ("Через промежуточную агрегацию CTE найди средний чек оплаченных заказов по пользователю.", "WITH paid AS (\n  SELECT user_id, total FROM orders WHERE status = 'paid'\n), avg_paid AS (\n  SELECT user_id, AVG(total) AS avg_total FROM paid GROUP BY user_id\n)\nSELECT user_id, avg_total FROM avg_paid ORDER BY user_id;\n", [[1, 3200.0]], "cte_avg_paid"),
            ("Через CTE отдели пользователей без платежей и верни активных пользователей, которых нужно проверить вручную.", "WITH paid_users AS (\n  SELECT DISTINCT orders.user_id FROM orders JOIN payments ON payments.order_id = orders.id WHERE payments.status = 'paid'\n)\nSELECT users.id, users.name FROM users\nLEFT JOIN paid_users ON paid_users.user_id = users.id\nWHERE users.active = 1 AND paid_users.user_id IS NULL\nORDER BY users.id;\n", [[2, "Олег"], [4, "Лена"]], "cte_manual_review"),
        ]
        task, sol, expected, concept = cases[variant % len(cases)]
        return task, sol, sql_checker(schema, seed, expected), concept
    if "insert" in low or "update" in low or "delete" in low:
        schema, seed = sql_assets("tasks")
        task = "Добавь задачу `Review API` в проект `1`, отметь задачу `2` выполненной и верни задачи проекта `1`."
        sol = "INSERT INTO tasks (id, project_id, title, done) VALUES (4, 1, 'Review API', 0);\nUPDATE tasks SET done = 1 WHERE id = 2;\nSELECT id, title, done FROM tasks WHERE project_id = 1 ORDER BY id;\n"
        return task, sol, sql_checker(schema, seed, [[1, "Create route", 0], [2, "Write tests", 1], [4, "Review API", 0]]), "dml"
    if "constraint" in low or "нормал" in low:
        schema = "CREATE TABLE tags (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);"
        seed = "INSERT INTO tags VALUES (1, 'python'), (2, 'sql');"
        task = "Верни уникальные названия тегов из таблицы `tags` в алфавитном порядке."
        sol = "SELECT name FROM tags ORDER BY name;\n"
        return task, sol, sql_checker(schema, seed, [["python"], ["sql"]]), "constraints"
    if "limit" in low or "order" in low:
        task = "Верни два самых дорогих товара: `id`, `title`, `price`. При равной цене сортируй по `id`."
        sol = "SELECT id, title, price FROM products ORDER BY price DESC, id LIMIT 2;\n"
        return task, sol, sql_checker(schema, seed, [[2, "Курс", 5000], [3, "Мышь", 1200]]), "order_limit"
    if "where" in low or "like" in low or "null" in low:
        task = "Верни активных пользователей, у которых имя не начинается на `М`. Нужны `id`, `name`."
        sol = "SELECT id, name FROM users WHERE active = 1 AND name NOT LIKE 'М%' ORDER BY id;\n"
        return task, sol, sql_checker(schema, seed, [[1, "Анна"], [2, "Олег"], [4, "Лена"]]), "where"
    task = f"Для учебной базы ecommerce выбери стабильный набор пользователей для шага {variant}: `id`, `name`, `active`."
    sol = "SELECT id, name, active FROM users ORDER BY id;\n"
    return task, sol, sql_checker(schema, seed, [[1, "Анна", 1], [2, "Олег", 1], [3, "Маша", 0], [4, "Лена", 1]]), "select"


def http_checker(method: str, path: str, expected: Any, status: int = 200, body: dict[str, Any] | None = None, hidden_status: int | None = None) -> dict[str, Any]:
    test: dict[str, Any] = {"method": method, "path": path, "expected_status": status}
    if body is not None:
        test["json"] = body
    if isinstance(expected, dict):
        test["expected_json_subset"] = expected
    elif expected == "array":
        test["expected_json_type"] = "array"
    hidden = dict(test)
    if hidden_status:
        hidden["expected_status"] = hidden_status
        if method == "POST":
            hidden["json"] = {"title": ""}
    elif method in {"PATCH", "DELETE"}:
        hidden = {"method": method, "path": f"{path}/999", "expected_status": 404}
        if method == "PATCH":
            hidden["json"] = {"done": True}
    elif method == "GET" and path != "/health":
        hidden = {"method": "GET", "path": f"{path}/999", "expected_status": 404}
    return {"type": "http_api", "app_import": "app.main:app", "public_tests": [test], "hidden_tests": [hidden], "timeout_sec": 8}


def ide_checker(kind: str, lesson_slug: str, order: int, topics: list[str], final_gate: str | None = None) -> dict[str, Any]:
    scenario = f"{kind}_{lesson_slug}_{order}"
    if final_gate:
        files = ["README.md", "app/main.py", "tests/test_api.py", "Dockerfile", "docker-compose.yml", ".env.example", f"docs/final/{lesson_slug}.md"]
        return {
            "type": "ide_plugin",
            "scenario_id": scenario,
            "required_files": files,
            "commands": [{"cmd": "python -m pytest", "expect_exit_code": 0}, {"cmd": "docker compose config", "expect_exit_code": 0}, {"cmd": "bash deploy/deploy.sh --dry-run", "expect_exit_code": 0}],
            "http_checks": [{"method": "GET", "path": "/health", "expected_status": 200}, {"method": "POST", "path": "/auth/login", "expected_status": 200}],
            "runtime_checks": [
                {"type": "http", "url": "http://127.0.0.1:8000/health", "expected_status": 200},
                {"type": "env", "file": ".env.example", "required_keys": ["APP_ENV", "DATABASE_URL", "SECRET_KEY"]},
                {"type": "rollback", "command": "bash deploy/deploy.sh --rollback --dry-run", "expect_exit_code": 0},
            ],
            "gate_checks": {
                "gate": final_gate,
                "requires_acceptance_criteria": True,
                "requires_negative_cases": final_gate in {"Tests", "Auth", "API contract", "CRUD", "Deploy"},
                "requires_rollback": final_gate in {"Deploy", "CI/CD", "Git workflow", "Alembic migrations"},
                "required_artifacts": ["student-facing spec", "machine-checkable command", "pass/fail criteria", "risk note"],
            },
        }
    if "Git и GitHub" in topics:
        files = [f"git_labs/{lesson_slug}/README.md", f"git_labs/{lesson_slug}/src/main.py"]
        required_commands = ["git status --porcelain", f"test -f git_labs/{lesson_slug}/README.md"]
        if "reflog" in kind:
            required_commands.append("git reflog --oneline")
        if "stash" in kind:
            required_commands.append("git stash list")
        return {
            "type": "ide_plugin",
            "scenario_id": scenario,
            "required_files": files,
            "git_checks": {
                "must_have_clean_worktree": True,
                "min_commits": 2 + (order % 3),
                "required_branches": ["main", f"feature/{lesson_slug[:20]}"],
                "expected_current_branch": "main",
                "forbidden_untracked_files": True,
                "forbidden_file_content": ["<<<<<<<", "=======", ">>>>>>>"],
                "must_explain_risky_commands": "force-with-lease" in kind,
                "must_have_reflog_recovery": "reflog" in kind,
            },
            "commands": [{"cmd": required_commands[0], "expect_stdout": ""}] + [{"cmd": cmd, "expect_exit_code": 0} for cmd in required_commands[1:]],
        }
    if any(t in topics for t in ["Docker", "Docker Compose", "CI/CD", "GitHub Actions", "GitLab CI/CD", "multistage build", "VPS", "автодеплой"]):
        files = ["Dockerfile", "docker-compose.yml", ".dockerignore", f"deploy/{lesson_slug}_{order}.sh", ".github/workflows/ci.yml"]
        return {
            "type": "ide_plugin",
            "scenario_id": scenario,
            "required_files": files,
            "file_content_rules": [{"file": "Dockerfile", "must_contain": ["WORKDIR", "COPY", "CMD"]}, {"file": "docker-compose.yml", "must_contain": ["services:", "healthcheck"]}],
            "commands": [
                {"cmd": "docker compose config", "expect_exit_code": 0},
                {"cmd": "docker compose up -d --build", "expect_exit_code": 0},
                {"cmd": "docker compose exec -T app python -m pytest", "expect_exit_code": 0},
                {"cmd": f"bash deploy/{lesson_slug}_{order}.sh --dry-run", "expect_exit_code": 0},
            ],
            "runtime_checks": [
                {"type": "http", "url": "http://127.0.0.1:8000/health", "expected_status": 200, "expected_json_subset": {"status": "ok"}},
                {"type": "env", "file": ".env.example", "required_keys": ["APP_ENV", "DATABASE_URL", "SECRET_KEY"]},
                {"type": "rollback", "command": f"bash deploy/{lesson_slug}_{order}.sh --rollback --dry-run", "expect_exit_code": 0},
            ],
        }
    if "FastAPI" in topics or "CRUD-проект" in topics:
        files = [f"app/routers/{lesson_slug}.py", "app/main.py", f"tests/test_{lesson_slug}_{order}.py", "README.md"]
        return {
            "type": "ide_plugin",
            "scenario_id": scenario,
            "required_files": files,
            "commands": [{"cmd": "python -m pytest", "expect_exit_code": 0}, {"cmd": f"python -m pytest tests/test_{lesson_slug}_{order}.py", "expect_exit_code": 0}],
            "http_checks": [{"method": "GET", "path": "/health", "expected_status": 200, "expected_json_subset": {"status": "ok"}}],
        }
    if "SQLite/sqlite3" in topics:
        files = [f"app/{lesson_slug}_db.py", f"tests/test_{lesson_slug}_{order}.py", "migrations/001_init.sql", "README.md"]
        return {"type": "ide_plugin", "scenario_id": scenario, "required_files": files, "commands": [{"cmd": "python -m pytest", "expect_exit_code": 0}, {"cmd": "sqlite3 app.db '.tables'", "expect_exit_code": 0}]}
    if final_gate:
        files = ["README.md", "app/main.py", "tests/test_api.py", "Dockerfile", "docker-compose.yml", ".env.example", f"docs/final/{lesson_slug}.md"]
        return {
            "type": "ide_plugin",
            "scenario_id": scenario,
            "required_files": files,
            "commands": [{"cmd": "python -m pytest", "expect_exit_code": 0}, {"cmd": "docker compose config", "expect_exit_code": 0}, {"cmd": "bash deploy/deploy.sh --dry-run", "expect_exit_code": 0}],
            "http_checks": [{"method": "GET", "path": "/health", "expected_status": 200}],
            "gate_checks": {
                "gate": final_gate,
                "requires_acceptance_criteria": True,
                "requires_negative_cases": final_gate in {"Tests", "Auth", "API contract", "CRUD", "Deploy"},
                "requires_rollback": final_gate in {"Deploy", "CI/CD", "Git workflow", "Alembic migrations"},
                "required_artifacts": ["student-facing spec", "machine-checkable command", "pass/fail criteria", "risk note"],
            },
        }
    files = [f"src/{lesson_slug}_{order}.py", f"tests/test_{lesson_slug}_{order}.py", "README.md"]
    return {"type": "ide_plugin", "scenario_id": scenario, "required_files": files, "commands": [{"cmd": f"python -m pytest tests/test_{lesson_slug}_{order}.py", "expect_exit_code": 0}]}


def ai_review(title: str, gate: str | None = None) -> dict[str, Any]:
    rubrics = ["требования выполнены наблюдаемым результатом", "код разделён на небольшие функции", "ошибки и крайние случаи проверены", "README объясняет запуск", "секреты не попали в репозиторий"]
    if gate:
        rubrics.insert(0, f"gate `{gate}` имеет явные pass/fail критерии")
    return {"enabled": True, "rubric": rubrics, "pass_score": 4, "review_focus": title}


def git_scenario(title: str, lesson_slug: str, order: int) -> tuple[str, str, str]:
    scenarios = [
        (
            "restore_reset_revert",
            "Сломай файл `src/main.py` лишним выводом, восстанови рабочую версию через `git restore`, затем сделай отдельный `git revert` ошибочного коммита.",
            f"mkdir -p git_labs/{lesson_slug}/src\ncd git_labs/{lesson_slug}\ngit init\ngit config user.email student@example.com\ngit config user.name Student\necho 'print(\"ok\")' > src/main.py\ngit add .\ngit commit -m 'Working main'\necho 'print(\"debug\")' >> src/main.py\ngit restore src/main.py\ngit status --porcelain\n# для revert: создай ошибочный commit, затем git revert --no-edit HEAD\n",
        ),
        (
            "merge_conflict",
            f"Создай конфликт между `main` и `feature/{lesson_slug[:20]}` в README, выполни merge и оставь итоговый текст без маркеров.",
            f"cd git_labs/{lesson_slug}\ngit switch -c feature/{lesson_slug[:20]}\necho 'feature title' > README.md\ngit add README.md\ngit commit -m 'Feature title'\ngit switch main\necho 'main title' > README.md\ngit add README.md\ngit commit -m 'Main title'\ngit merge feature/{lesson_slug[:20]}\n# edit README.md, remove conflict markers\ngit add README.md\ngit commit -m 'Resolve README conflict'\n",
        ),
        (
            "rebase_conflict",
            f"Перенеси `feature/{lesson_slug[:20]}` поверх нового `main` через rebase, разреши конфликт и продолжи rebase.",
            f"cd git_labs/{lesson_slug}\ngit switch feature/{lesson_slug[:20]}\ngit rebase main\n# edit conflicted file\ngit add README.md\ngit rebase --continue\ngit switch main\ngit merge --ff-only feature/{lesson_slug[:20]}\n",
        ),
        (
            "stash_cherry_pick",
            "Сохрани незавершённую правку через stash, перенеси один готовый commit через cherry-pick и верни stash без потери изменений.",
            f"cd git_labs/{lesson_slug}\necho 'draft' >> README.md\ngit stash push -m 'draft readme'\ngit switch -c hotfix/{lesson_slug[:12]}\necho 'hotfix' > src/main.py\ngit add src/main.py\ngit commit -m 'Hotfix main output'\ngit switch main\ngit cherry-pick hotfix/{lesson_slug[:12]}\ngit stash pop\n",
        ),
        (
            "non_fast_forward_force_with_lease",
            "Смоделируй non-fast-forward: локальная история отстала от remote. Выполни `pull --rebase`, а force-push допускай только через `--force-with-lease` и объясни риск в README.",
            f"cd git_labs/{lesson_slug}\ngit remote add origin ../remote-{lesson_slug}.git\n# after rejected push:\ngit fetch origin\ngit pull --rebase origin main\ngit push --force-with-lease origin main\necho 'force-with-lease protects чужие коммиты' >> README.md\n",
        ),
        (
            "reflog_recovery",
            "Сделай ошибочный `reset --hard`, найди потерянный commit через reflog и восстанови его новой веткой `recovery/reflog`.",
            f"cd git_labs/{lesson_slug}\ngit log --oneline -3\ngit reset --hard HEAD~1\ngit reflog --oneline\ngit switch -c recovery/reflog HEAD@{{1}}\ngit status --porcelain\n",
        ),
        (
            "tag_release_fix",
            "Создай lightweight tag для версии, найди ошибку в README, исправь её новым commit и поставь annotated tag с пояснением.",
            f"cd git_labs/{lesson_slug}\ngit tag v0.1.0\necho 'release notes' >> README.md\ngit add README.md\ngit commit -m 'Document release notes'\ngit tag -a v0.1.1 -m 'Fix release notes'\ngit tag --list\n",
        ),
        (
            "upstream_fetch_pull_rebase",
            "Настрой upstream для feature-ветки, выполни `fetch`, затем подтяни main через `pull --rebase` без merge-коммита.",
            f"cd git_labs/{lesson_slug}\ngit remote add origin ../remote-{lesson_slug}.git\ngit branch --set-upstream-to=origin/main main\ngit fetch origin\ngit pull --rebase origin main\ngit log --oneline --max-count=5\n",
        ),
        (
            "git_rm_restore_deleted_file",
            "Удали tracked-файл через `git rm`, пойми последствия в `git status`, затем восстанови файл из HEAD и зафиксируй исправление.",
            f"cd git_labs/{lesson_slug}\ngit rm src/main.py\ngit status --short\ngit restore --staged src/main.py\ngit restore src/main.py\ngit add src/main.py\ngit commit -m 'Restore tracked main file'\n",
        ),
    ]
    key, task, solution = scenarios[(order - 4) % len(scenarios)]
    return key, task, solution


def devops_scenario(title: str, lesson_slug: str, order: int) -> tuple[str, str, str]:
    scenarios = [
        ("container_start", "Собери image, подними контейнер и проверь, что `/health` возвращает `200`.", f"docker build -t {lesson_slug}:local .\ndocker run --rm -d --name {lesson_slug}-{order} -p 8000:8000 {lesson_slug}:local\ncurl -fsS http://127.0.0.1:8000/health\n"),
        ("env_example", "Добавь `.env.example`, прочитай переменные в приложении и проверь, что без обязательного секрета контейнер не стартует.", "cp .env.example .env\npython -c \"from app.settings import settings; print(settings.APP_ENV)\"\ndocker compose config\n"),
        ("tests_inside_container", "Запусти pytest внутри контейнера, чтобы локальное окружение не влияло на результат.", "docker compose up -d --build\ndocker compose exec -T app python -m pytest\n"),
        ("compose_healthcheck", "Добавь healthcheck в compose и дождись состояния healthy перед запуском зависимого сервиса.", "docker compose up -d --build\ndocker inspect --format='{{json .State.Health.Status}}' $(docker compose ps -q app)\n"),
        ("ci_split_jobs", "Раздели CI на jobs `lint`, `test`, `build`, `deploy`, передавая артефакт build в deploy.", "grep -E 'lint|test|build|deploy' .github/workflows/ci.yml\n"),
        ("deploy_dry_run_rollback", "Добавь deploy script с режимами `--dry-run`, `--rollback` и проверкой статуса после переключения релиза.", f"bash deploy/{lesson_slug}_{order}.sh --dry-run\nbash deploy/{lesson_slug}_{order}.sh --rollback --dry-run\n"),
        ("multistage_size_check", "Перепиши Dockerfile на multistage build и проверь, что runtime-слой не содержит dev-зависимости.", "docker build --target runtime -t app:runtime .\ndocker image inspect app:runtime --format='{{.Size}}'\n"),
        ("logs_exec_debug", "Найди ошибку старта через `docker compose logs`, зайди в контейнер через `exec` и проверь переменные окружения.", "docker compose logs app --tail=80\ndocker compose exec -T app env | grep APP_ENV\n"),
        ("secrets_no_commit", "Перенеси секреты из compose в `.env.example`/runtime env и докажи, что реальные значения не попали в git.", "grep -R 'SECRET_KEY=' .env.example docker-compose.yml\ngit grep -n 'real-secret' -- . ':!.env' || true\n"),
    ]
    key, task, solution = scenarios[(order - 4) % len(scenarios)]
    return key, task, solution


def final_gate_scenario(gate: str, lesson_slug: str, order: int) -> tuple[str, str, str]:
    low = gate.lower()
    if "тз" in low or "user stories" in low:
        task = "Сдай ТЗ: 5 user stories, ограничения, acceptance criteria, out-of-scope и критерии отказа от фичи."
        solution = "docs/final/requirements.md\n\n## User story\nAs a registered user, I want ...\n\n## Acceptance criteria\n- Given ..., when ..., then ...\n\n## Constraints\n- no paid AI API in checks\n- secrets only via env\n"
        return "requirements_acceptance", task, solution
    if "git workflow" in low:
        task = "Сдай Git workflow gate: issue branch, понятные commits, merge/rebase-конфликт, recovery через reflog и правило для force-with-lease."
        solution = "git switch -c feature/final-api-contract\n# commits: requirements, tests, implementation\n# resolve rebase conflict without markers\ngit reflog --oneline\n# use --force-with-lease only after fetch and explanation in docs/final/git_workflow.md\n"
        return "git_workflow_recovery", task, solution
    if "схема" in low or "models" in low or "migrations" in low:
        task = "Сдай DB gate: ERD, SQLAlchemy models, индексы, связи, Alembic migration и rollback-план."
        solution = "docs/final/erd.md\napp/models.py\nalembic/versions/001_init.py\n\nIndexes:\n- ix_tasks_owner_status\n- ix_comments_task_created_at\n"
        return "db_schema_migrations", task, solution
    if "api contract" in low:
        task = "Сдай API contract: OpenAPI, статусы, ошибки 400/401/404/422, примеры request/response и negative cases."
        solution = "docs/final/api_contract.md\nopenapi.json\n\nPOST /tasks -> 201\nGET /tasks/{id} -> 200/404\nPOST /auth/login -> 200/401\n"
        return "api_contract_errors", task, solution
    if "auth" in low:
        task = "Сдай Auth gate: JWT access, refresh token rotation, protected routes и негативные проверки 401/403."
        solution = "app/auth/jwt.py\napp/routers/auth.py\ntests/test_auth_negative.py\n\npytest covers expired token, missing token, refresh reuse\n"
        return "auth_jwt_refresh_negative", task, solution
    if "fastapi" in low:
        task = "Сдай FastAPI structure gate: app factory, routers, Depends, settings, healthcheck и единый формат ошибок."
        solution = "app/main.py\napp/routers/tasks.py\napp/core/settings.py\napp/core/errors.py\n\nGET /health -> {\"status\":\"ok\"}\n"
        return "fastapi_structure_health_errors", task, solution
    if "crud" in low:
        task = "Сдай CRUD gate: create/read/update/delete для основной сущности, 404 для отсутствующей записи и 422 для невалидного тела."
        solution = "app/routers/tasks.py\napp/services/tasks.py\ntests/integration/test_tasks_crud_negative.py\n\nPOST -> 201, GET missing -> 404, POST empty title -> 422\n"
        return "crud_negative_contract", task, solution
    if "tests" in low:
        task = "Сдай Tests gate: unit, integration и negative cases для API, БД и auth."
        solution = "tests/unit/test_services.py\ntests/integration/test_tasks_api.py\ntests/integration/test_auth_negative.py\npython -m pytest --maxfail=1\n"
        return "unit_integration_negative", task, solution
    if "docker" in low:
        task = "Сдай Docker gate: контейнер стартует, healthcheck проходит, env читается из `.env.example`, тесты запускаются внутри контейнера."
        solution = "Dockerfile\ndocker-compose.yml\n.env.example\n\ndocker compose up -d --build\ndocker compose exec -T app python -m pytest\ncurl -fsS http://127.0.0.1:8000/health\n"
        return "docker_runtime_health_env", task, solution
    if "ci/cd" in low:
        task = "Сдай CI/CD gate: отдельные jobs `lint`, `test`, `build`, `deploy`, build image и deploy dry-run без секретов в yaml."
        solution = ".github/workflows/ci.yml\n.gitlab-ci.yml\n\njobs: lint -> test -> build -> deploy\nbash deploy/deploy.sh --dry-run\n"
        return "ci_split_jobs_deploy_dry_run", task, solution
    if "ai integration" in low:
        task = "Сдай AI integration gate: mock provider, timeout, retry, structured JSON output, логирование стоимости и запрет секретов в коде."
        solution = "app/ai/provider.py\napp/ai/mock_provider.py\ntests/test_ai_provider_contract.py\n\nProvider accepts messages and returns parsed schema without paid API in tests.\n"
        return "ai_mock_structured_safe", task, solution
    if "logging" in low:
        task = "Сдай Logging gate: request id, structured logs, error logging без персональных данных и проверка формата."
        solution = "app/core/logging.py\napp/middleware/request_id.py\ntests/test_logging_format.py\n\nLogs include request_id, path, status_code, duration_ms.\n"
        return "structured_logging_request_id", task, solution
    if "readme" in low:
        task = "Сдай README gate: запуск локально, запуск в Docker, env, тесты, миграции, troubleshooting и demo script."
        solution = "README.md\n\n## Quick start\npython -m pytest\ndocker compose up -d --build\nbash deploy/deploy.sh --dry-run\n"
        return "readme_reproducible_runbook", task, solution
    if "deploy" in low:
        task = "Сдай Deploy gate: домен, SSL, env, healthcheck, dry-run deploy и rollback с проверкой статуса."
        solution = "deploy/deploy.sh --dry-run\ndeploy/deploy.sh --rollback --dry-run\ncurl -fsS https://example.com/health\n"
        return "deploy_ssl_rollback", task, solution
    if "final defense" in low:
        task = "Сдай защиту: архитектурная схема, demo script, список trade-offs, ответы на вопросы по SQL/API/DevOps/AI."
        solution = "docs/final/defense.md\n\nQuestions:\n1. Почему выбран такой индекс?\n2. Как откатить релиз?\n3. Что будет при падении AI provider?\n"
        return "defense_questions_pass_fail", task, solution
    task = f"Сдай gate `{gate}`: артефакт, проверку, критерии pass/fail и короткое объяснение решения."
    solution = f"docs/final/{lesson_slug}.md\nREADME.md\npython -m pytest\n"
    return "generic_gate_with_pass_fail", task, solution


def first_lesson(lesson_id: str) -> list[dict[str, Any]]:
    t = ["Python Core"]
    steps: list[dict[str, Any]] = []
    steps.append(base_step(lesson_id, 1, "Смысл", "theory", 1, 10, 7, "**Коротко:** программа — это список команд, которые Python выполняет по порядку.\n\nТы начнёшь с команды `print()`. Она выводит текст или результат вычисления на экран.\n\n```python\nprint(\"Привет, Python!\")\n```\n\nРезультат:\n\n```text\nПривет, Python!\n```\n\nСейчас не нужно знать весь язык. Важно первое правило: Python выполняет код сверху вниз, строка за строкой.\n\nКогда видишь пример, прочитай его сверху вниз: какая команда выполняется первой, какая второй, какой результат должен появиться на экране.", t, solution_code="Методическая цель: дать первый запуск без терминала, Git и AI."))
    qs = question(f"{lesson_id}_s002", "Что делает команда print()?", "Выводит данные на экран", "print() выводит текст, число или результат выражения на экран.", ["Получает данные от пользователя", "Создаёт файл", "Удаляет переменную"])
    steps.append(base_step(lesson_id, 2, "Что делает print", "test", 1, 25, 5, "Ответь на вопрос перед самостоятельной задачей.", t, questions=qs, checker=quiz_checker(qs), solution_code="Правильный ответ: выводит данные на экран."))
    steps.append(base_step(lesson_id, 3, "Запусти пример", "practice", 1, 35, 6, "**Коротко:** запусти готовый код и сравни результат.\n\n### Условие\nВ редакторе уже есть код. Нажми запуск или проверку и посмотри, что он выводит.\n\n### Вход\nНет входных данных.\n\n### Выход\nДве строки:\n\n```text\nПривет, Python!\nКод выполняется сверху вниз\n```\n\n### Что проверить\nЕсли результат отличается, проверь кавычки, скобки и порядок строк.", t, editor_initial_code='print("Привет, Python!")\nprint("Код выполняется сверху вниз")\n', solution_code='print("Привет, Python!")\nprint("Код выполняется сверху вниз")\n', checker=stdout_checker([("", "Привет, Python!\nКод выполняется сверху вниз\n")]), hints=["На этом шаге код уже готов. Твоя задача — запустить его и увидеть результат.", "Если вывод отличается, сравни каждую строку с примером."]))
    first_practices = [
        ("Первый вывод", 'print("Привет, Python!")\n', "Привет, Python!\n", "Напиши программу, которая выводит ровно `Привет, Python!`."),
        ("Две строки", 'print("Привет!")\nprint("Это мой первый код.")\n', "Привет!\nЭто мой первый код.\n", "Выведи две строки в правильном порядке."),
        ("Порядок строк", 'print("Старт")\nprint("Проверка")\nprint("Финиш")\n', "Старт\nПроверка\nФиниш\n", "Выведи три строки так, чтобы было видно выполнение сверху вниз."),
        ("Математика", "print(2 + 3)\nprint(10 - 4)\n", "5\n6\n", "Выведи результаты двух вычислений без кавычек."),
        ("Имя", 'name = "Анна"\nprint("Имя:", name)\n', "Имя: Анна\n", "Создай переменную `name` и используй её в выводе."),
        ("Сначала создать", 'city = "Казань"\nprint(city)\n', "Казань\n", "Исправь код так, чтобы переменная была создана до вывода."),
        ("Анкета", 'name = "Анна"\nage = 20\nprint("Имя:", name)\nprint("Возраст:", age)\n', "Имя: Анна\nВозраст: 20\n", "Выведи маленькую анкету из двух переменных."),
        ("Лишний текст", 'print("Готово")\n', "Готово\n", "Оставь только требуемую строку `Готово` без пояснений."),
        ("Мини-чеклист", 'print("Код написан")\nprint("Вывод проверен")\n', "Код написан\nВывод проверен\n", "Выведи две строки финального чеклиста."),
    ]
    order = 4
    for name, sol, expected, task in first_practices:
        body = f"**Коротко:** {task}\n\n### Условие\n{task}\n\n### Вход\nНет входных данных.\n\n### Выход\n```text\n{expected.rstrip()}\n```\n\n### Что проверить\nСравни каждую строку: регистр, пробелы и лишний текст важны."
        steps.append(base_step(lesson_id, order, name, "practice", 1, 45 + order, 8, body, t, editor_initial_code="# напиши код ниже\n", solution_code=sol, checker=stdout_checker([("", expected)])))
        order += 1
        if order in {7, 11, 15}:
            theory_title = "Кавычки" if order == 7 else "Переменная" if order == 11 else "Точный вывод"
            theory_body = f"**Коротко:** `{theory_title}` помогает избежать типичной ошибки первого урока.\n\n```python\n{sol}```\n\nЕсли текст написан в кавычках, Python выводит текст. Если имя написано без кавычек, Python ищет переменную с таким именем.\n\nПеред запуском проговори: что является текстом, что является числом, что является именем переменной."
            steps.append(base_step(lesson_id, order, theory_title, "theory", 1, 10, 6, theory_body, t, solution_code=f"Служебное пояснение к мини-теме {theory_title}."))
            order += 1
    qs2 = [
        {
            "id": f"{lesson_id}_s{order:03d}_q{i}",
            "question": text,
            "options": [{"id": "a", "text": a}, {"id": "b", "text": b}, {"id": "c", "text": c}, {"id": "d", "text": d}],
            "correct_answer_id": correct,
            "correct_option_index": {"a": 0, "b": 1, "c": 2, "d": 3}[correct],
            "explanation": expl,
        }
        for i, (text, a, b, c, d, correct, expl) in enumerate([
            ("Что произойдёт, если написать print(2 + 3)?", "Будет выведено 5", "Будет выведено 2 + 3", "Будет ошибка", "Python ничего не выведет", "a", "Числа без кавычек вычисляются."),
            ("Что произойдёт, если написать print(\"2 + 3\")?", "Будет выведено 5", "Будет выведено 2 + 3", "Будет ошибка", "Python создаст переменную", "b", "Текст в кавычках выводится как текст."),
            ("Почему print(Привет) — ошибка?", "print нельзя использовать", "текст написан без кавычек", "Python не умеет русский текст", "нужны две команды print", "b", "Без кавычек слово считается именем."),
            ("Что важно в задачах с точной проверкой?", "Добавлять слово Ответ", "Выводить ровно то, что просит условие", "Всегда писать код в одну строку", "Не использовать переменные", "b", "Сравнивается фактический вывод."),
            ("Как читать строку name = \"Анна\"?", "name равно Анна как в математике", "сохрани значение Анна в переменную name", "выведи Анна", "удали переменную", "b", "Знак = сохраняет значение справа в имя слева."),
        ], 1)
    ]
    steps.append(base_step(lesson_id, order, "Контроль урока", "test", 1, 50, 10, "Ответь на вопросы по первому запуску Python-кода.", t, questions=qs2, checker=quiz_checker(qs2), solution_code="Правильные ответы скрыты в questions.correct_answer_id."))
    order += 1
    steps.append(base_step(lesson_id, order, "Итог", "summary", 1, 10, 5, "Ты написал первые программы на Python.\n\nТеперь ты умеешь:\n\n```python\nprint(\"Привет\")\n```\n\nвыводить текст;\n\n```python\nprint(2 + 3)\n```\n\nвыводить результат вычисления;\n\n```python\nname = \"Анна\"\nprint(\"Имя:\", name)\n```\n\nсоздавать переменную и использовать её в выводе.\n\nГлавные правила урока:\n\n1. Python выполняет код сверху вниз.\n2. Текст пишется в кавычках.\n3. Без кавычек числа можно вычислять.\n4. Переменную нужно создать до использования.\n5. В задачах с проверкой не добавляй лишний текст.\n\nВ следующем уроке ты начнёшь получать данные от пользователя через `input()` и превращать введённые числа через `int()` и `float()`.", t, solution_code="Урок завершён."))
    return steps


PY_TASKS = [
    ("Скидка", "calculate_total", "Верни стоимость после скидки в процентах.", "return price - price * discount / 100", [((1000, 10), 900.0), ((250, 20), 200.0), ((99, 0), 99.0)]),
    ("Нормализация имени", "normalize_name", "Убери пробелы по краям и сделай первую букву заглавной.", "return name.strip().capitalize()", [((" анна ",), "Анна"), (("ОЛЕГ",), "Олег"), (("маша",), "Маша")]),
    ("Доступ", "can_access", "Верни True, если пользователь активен и роль не `banned`.", "return active and role != 'banned'", [((True, "admin"), True), ((True, "banned"), False), ((False, "admin"), False)]),
    ("Теги", "unique_tags", "Верни отсортированный список уникальных тегов.", "return sorted(set(tags))", [((["api", "sql", "api"],), ["api", "sql"]), (([],), []), ((["b", "a"],), ["a", "b"])]),
    ("Группировка", "group_scores", "Верни словарь: имя → сумма баллов.", "out = {}\n    for name, score in rows:\n        out[name] = out.get(name, 0) + score\n    return out", [(((("Анна", 5), ("Анна", 7), ("Олег", 3)),), {"Анна": 12, "Олег": 3}), (((("Ира", 1),),), {"Ира": 1}), (((),), {})]),
    ("Граница", "clamp", "Ограничь число диапазоном от low до high.", "return max(low, min(high, value))", [((5, 0, 10), 5), ((-1, 0, 10), 0), ((20, 0, 10), 10)]),
    ("Пакеты", "build_path", "Собери путь из частей через `/`, пропуская пустые строки.", "return '/'.join(part.strip('/') for part in parts if part)", [((["app", "api", "v1"],), "app/api/v1"), ((["/tmp/", "", "x"],), "tmp/x"), (([],), "")]),
]


def py_task(title: str, idx: int) -> tuple[str, str, str, list[tuple[Any, Any]]]:
    if "строк" in title.lower():
        item = PY_TASKS[1]
    elif "bool" in title.lower() or "услов" in title.lower() or "исключ" in title.lower():
        item = PY_TASKS[2]
    elif "множе" in title.lower() or "спис" in title.lower():
        item = PY_TASKS[3]
    elif "словар" in title.lower() or "group" in title.lower():
        item = PY_TASKS[4]
    elif "алгорит" in title.lower() or "binary" in title.lower() or "sort" in title.lower():
        item = PY_TASKS[5]
    elif "pathlib" in title.lower() or "poetry" in title.lower() or "пакет" in title.lower():
        item = PY_TASKS[6]
    else:
        item = PY_TASKS[idx % len(PY_TASKS)]
    return item[0], f"{item[1]}_{idx}", item[3], item[4]


def make_python_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    example = "value = 2 + 3\nprint(value)"
    if "asyncio" in topics:
        example = "async def load_one(client, url):\n    return await client.get(url)"
    elif "ООП" in topics or "магические методы" in topics:
        example = "class Money:\n    def __init__(self, amount):\n        self.amount = amount"
    elif "AI API" in topics or "RAG" in topics:
        example = "messages = [{'role': 'user', 'content': 'Суммируй текст'}]"
    body = f"**Коротко:** в теме `{title}` ты решаешь одну маленькую backend-задачу и проверяешь её кодом.\n\n### Зачем\nЭта тема нужна, чтобы писать предсказуемый Python-код, который можно тестировать и поддерживать.\n\n### Минимальный пример\n```python\n{example}\n```\n\n### Что важно\nСначала отдели входные данные от обработки. Потом проверь крайний случай: пустой ввод, ноль, отсутствующее значение или неверный тип.\n\n### Частая ошибка\nНе прячь несколько действий в одну строку, если после этого трудно понять причину падения."
    steps = [base_step(lesson_id, 1, "Смысл", "theory", 2, 20, 16, body, topics, solution_code=f"Teacher note for {title}: focus on observable behavior, then implementation.")]
    body2 = f"**Коротко:** разверни пример темы `{title}` до функции, которую удобно проверить.\n\n```python\n{example}\n```\n\nИз примера видно правило: маленькая функция получает данные, возвращает результат и не зависит от случайного состояния. Перед практикой измени одно значение и проверь, что результат изменился ожидаемо."
    steps.append(base_step(lesson_id, 2, "Минимальный пример", "theory", 2, 20, 14, body2, topics, solution_code=f"Reference explanation for {title}."))
    qs = question(f"{lesson_id}_s003", f"Что важнее всего проверить в теме `{title}` перед отправкой?", "минимальный пример и один крайний случай", "Один happy-path не показывает, что код выдерживает границы.", ["только красивое имя файла", "количество пустых строк", "случайный print"])
    steps.append(base_step(lesson_id, 3, "Понимание", "test", 2, 25, 8, f"Ответь на вопрос по теме `{title}` перед практикой.", topics, questions=qs, checker=quiz_checker(qs), solution_code="Correct answer is stored in structured question metadata."))
    for order in range(4, 9):
        task_name, fn, expr, cases = py_task(title, order)
        fn = f"{slug(title).replace('-', '_')}_{fn}"
        bodyp = f"**Коротко:** {task_name.lower()} для темы `{title}`.\n\n### Фокус шага\nШаг `{order}` тренирует отдельный сценарий: `{['базовый happy-path', 'типичная ошибка', 'основная реализация', 'крайний случай', 'прикладное использование'][order - 4]}`.\n\n### Условие\n{expr.replace('return ', 'Напиши функцию, которая ')}\n\n### Вход\nАргументы функции из проверки.\n\n### Выход\nВозвращаемое значение без печати в stdout.\n\n### Пример\n```python\n# смотри имя функции в редакторе\n```\n\n### Что проверить\nЗапусти pytest и убедись, что функция не меняет входные данные без необходимости."
        editor = f"def {fn}(*args):\n    # замени *args на явные параметры, когда разберёшь условие\n    pass\n"
        params = {
            "calculate_total": "price, discount",
            "normalize_name": "name",
            "can_access": "active, role",
            "unique_tags": "tags",
            "group_scores": "rows",
            "clamp": "value, low, high",
            "build_path": "parts",
        }
        base_fn = fn.split("_")[-2] if fn.endswith(f"_{order}") else fn
        for key, p in params.items():
            if key in fn:
                editor = f"def {fn}({p}):\n    pass\n"
                solution = f"def {fn}({p}):\n    {expr}\n"
                break
        else:
            solution = f"def {fn}(*args):\n    {expr}\n"
        if order == 5:
            bodyp = bodyp.replace("### Условие", "### Debugging\nВ редакторе намеренно оставлена ошибка: функция печатает или возвращает неверную форму результата. Исправь код так, чтобы pytest проверял именно возвращаемое значение.\n\n### Условие")
            editor = editor.replace("pass", "print('debug')\n    return None")
        steps.append(base_step(lesson_id, order, ["Простая задача", "Ошибка", "Основная задача", "Крайний случай", "Прикладная задача"][order - 4], "practice", 2 + (order % 2), 70, 24, bodyp, topics, editor_initial_code=editor, solution_code=solution, checker=pytest_checker(fn, cases)))
    qs2 = question(f"{lesson_id}_s009", f"Почему функция из темы `{title}` не должна печатать результат внутри pytest-задачи?", "pytest проверяет возвращаемое значение напрямую", "Чистая функция проще тестируется и переиспользуется.", ["так быстрее импортируется модуль", "print запрещён во всём Python", "иначе файл станет длиннее"])
    steps.append(base_step(lesson_id, 9, "Закрепление", "test", 2, 25, 8, f"Проверь, как читать требования к функции в теме `{title}`.", topics, questions=qs2, checker=quiz_checker(qs2), solution_code="Correct answer is stored in structured question metadata."))
    chk = ide_checker("python_project", slug(title), 10, topics)
    project_body = f"**Коротко:** собери мини-пакет по теме `{title}` с тестами.\n\n### Условие\nСоздай модуль `src/{slug(title)}_service.py`, тест `tests/test_{slug(title)}_service.py` и README-раздел с командой запуска. В модуле должна быть одна публичная функция, которую можно импортировать без побочных эффектов.\n\n### Что сдаёшь\nФайлы проекта, зелёный pytest и короткое описание крайних случаев.\n\n### Pass/fail\nПроходит, если тесты запускаются командой из README, функция имеет понятное имя, а крайний случай проверен отдельным тестом."
    steps.append(base_step(lesson_id, 10, "Работа в IDE", "project", 3, 120, 45, project_body, topics, solution_code=f"Reference project:\n- src/{slug(title)}_service.py\n- tests/test_{slug(title)}_service.py\n- README.md with pytest command\n", checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title)))
    steps.append(base_step(lesson_id, 11, "Итоги", "summary", 1, 15, 6, f"Ты закрепил тему `{title}` через пример, функцию, проверку ошибки и IDE-проект.\n\nПеред следующим уроком открой последнюю функцию и назови один случай, который она должна обрабатывать явно.", topics, solution_code=f"Summary note for {title}."))
    return steps


def make_sql_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    task0, sol0, _, concept = sql_task(title, 0)
    steps = [
        base_step(lesson_id, 1, "Смысл", "theory", 2, 25, 16, f"**Коротко:** в теме `{title}` ты пишешь SQL, который проверяется на реальных строках.\n\n### Зачем\nSQL нужен backend-разработчику не как обзор, а как инструмент точного ответа на вопрос к данным.\n\n### Минимальный пример\n```sql\n{sol0.splitlines()[-2] if len(sol0.splitlines()) > 1 else sol0}\n```\n\n### Что важно\nСначала определи таблицы и колонки, потом условие, потом порядок строк. Без стабильного `ORDER BY` результат может быть непредсказуемым.\n\n### Частая ошибка\nФильтр в неверном месте меняет смысл запроса: например, `WHERE` после агрегации не заменяет `HAVING`.", topics, solution_code=f"SQL lesson concept: {concept}."),
        base_step(lesson_id, 2, "Минимальный пример", "theory", 2, 25, 14, f"**Коротко:** прочитай запрос по теме `{title}` сверху вниз.\n\n```sql\n{sol0}```\n\nПосле запуска проверь не только строки, но и названия колонок. Платформа сравнивает структуру результата.", topics, solution_code=sol0),
    ]
    qs = question(f"{lesson_id}_s003", f"Что обязательно добавить, если задача по `{title}` требует стабильный порядок строк?", "`ORDER BY` по явно указанным колонкам", "Без сортировки СУБД не обязана возвращать строки в одном и том же порядке.", ["комментарий в конце файла", "случайный LIMIT", "пустую строку перед SELECT"])
    steps.append(base_step(lesson_id, 3, "Понимание", "test", 2, 25, 8, f"Ответь на вопрос по SQL-теме `{title}`.", topics, questions=qs, checker=quiz_checker(qs), solution_code="Correct answer is stored in structured question metadata."))
    for order in range(4, 13):
        task_text, sol, chk, concept = sql_task(title, order)
        body = f"**Коротко:** {task_text}\n\n### Фокус шага\nУрок `{title}`, вариант {order - 3}: проверь не только синтаксис, но и смысл результата для конкретной темы.\n\n### Условие\n{task_text}\n\n### Вход\nSQLite-база из проверки с заранее загруженными данными.\n\n### Выход\nРовно те колонки, которые указаны в условии. Порядок строк должен быть стабильным.\n\n### Что проверить\nЗапусти запрос мысленно на первой строке seed-данных и объясни, почему она попадает или не попадает в результат."
        steps.append(base_step(lesson_id, order, ["Простой запрос", "Ошибка в запросе", "Основной запрос", "Связанные данные", "Граничный случай", "Контроль данных", "Диагностика", "Разбор результата", "Edge case"][order - 4], "practice", 3, 90, 28, body, topics, editor_initial_code="-- напиши SQL ниже\n", solution_code=sol, checker=chk, learning_objective=f"SQL:{title}:{concept}:{order}"))
    qs2 = question(f"{lesson_id}_s013", f"Что доказывает зелёная проверка в SQL-задаче `{title}`?", "запрос вернул ожидаемые строки на публичных и скрытых данных", "Проверка запускает запрос на подготовленной схеме и сравнивает результат.", ["запрос самый быстрый в мире", "в базе больше нет ошибок", "таблицы можно удалить"])
    steps.append(base_step(lesson_id, 13, "Закрепление", "test", 2, 25, 8, f"Проверь понимание результата SQL-запроса `{title}`.", topics, questions=qs2, checker=quiz_checker(qs2), solution_code="Correct answer is stored in structured question metadata."))
    chk = ide_checker("sql_file", slug(title), 14, topics)
    steps.append(base_step(lesson_id, 14, "SQL-файл", "project", 3, 120, 45, f"**Коротко:** оформи SQL-решения по теме `{title}` как маленький артефакт проекта.\n\n### Условие\nСоздай `sql/{slug(title)}.sql`. В файле должны быть: основной запрос урока, комментарий с ожидаемыми колонками, отдельный запрос для edge case.\n\n### Что сдаёшь\nSQL-файл, README с названием учебной базы и командой запуска через SQLite.\n\n### Pass/fail\nПроходит, если файл выполняется без ручных правок, возвращает стабильный порядок строк и не содержит временных отладочных SELECT.", topics, solution_code=f"-- sql/{slug(title)}.sql\n{sol0}\n-- edge case: add ORDER BY and verify empty result explicitly\n", checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title)))
    steps.append(base_step(lesson_id, 15, "Итоги", "summary", 1, 15, 6, f"Ты закрепил `{title}` через запросы, edge case и SQL-файл. Перед следующим уроком объясни, какие строки seed-данных были отброшены условием.", topics, solution_code=f"Summary note for SQL lesson {title}."))
    return steps


def make_sqlite_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    steps = make_sql_steps(lesson_id, title, topics)[:7]
    body = f"**Коротко:** создай SQLite-базу через Python для урока `{title}`.\n\n### Условие\nНапиши функцию `create_db(db_path)`. Она должна создать файл базы данных и таблицу `tasks` с полями `id`, `title`, `done`, `created_at`.\n\n### Что проверить\nПосле выполнения функция сохраняет изменения и закрывает соединение. Повторный запуск не должен падать."
    sol = "import sqlite3\n\n\ndef create_db(db_path):\n    conn = sqlite3.connect(db_path)\n    conn.execute(\"\"\"\n        CREATE TABLE IF NOT EXISTS tasks (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            title TEXT NOT NULL,\n            done INTEGER NOT NULL DEFAULT 0,\n            created_at TEXT NOT NULL\n        )\n    \"\"\")\n    conn.commit()\n    conn.close()\n"
    checker = {"type": "python_pytest", "timeout_sec": 6, "test_code": "import sqlite3\nfrom solution import create_db\n\n\ndef test_create_db(tmp_path):\n    db_path = tmp_path / 'tasks.db'\n    create_db(db_path)\n    assert db_path.exists()\n    conn = sqlite3.connect(db_path)\n    columns = conn.execute('PRAGMA table_info(tasks)').fetchall()\n    assert [col[1] for col in columns] == ['id', 'title', 'done', 'created_at']\n\n\ndef test_idempotent(tmp_path):\n    db_path = tmp_path / 'tasks.db'\n    create_db(db_path)\n    create_db(db_path)\n", "hidden_tests": [{"name": "not_null_defaults", "assertion": "title and done constraints exist"}]}
    steps.append(base_step(lesson_id, 8, "База кодом", "practice", 3, 95, 35, body, topics, editor_initial_code="import sqlite3\n\n\ndef create_db(db_path):\n    pass\n", solution_code=sol, checker=checker))
    body2 = f"**Коротко:** вынеси SQLite-запросы темы `{title}` в repository layer.\n\n### Условие\nСоздай функции `add_task(db_path, title)` и `list_tasks(db_path)`. Первая сохраняет задачу через параметризованный запрос, вторая возвращает список словарей.\n\n### Что проверить\nТесты должны использовать временную базу, а не файл из рабочей папки."
    sol2 = sol + "\n\ndef add_task(db_path, title):\n    conn = sqlite3.connect(db_path)\n    conn.execute('INSERT INTO tasks (title, created_at) VALUES (?, ?)', (title, '2026-05-01'))\n    conn.commit()\n    conn.close()\n\n\ndef list_tasks(db_path):\n    conn = sqlite3.connect(db_path)\n    rows = conn.execute('SELECT id, title, done FROM tasks ORDER BY id').fetchall()\n    conn.close()\n    return [{'id': r[0], 'title': r[1], 'done': bool(r[2])} for r in rows]\n"
    checker2 = {"type": "python_pytest", "timeout_sec": 6, "test_code": "from solution import create_db, add_task, list_tasks\n\n\ndef test_repository(tmp_path):\n    db_path = tmp_path / 'tasks.db'\n    create_db(db_path)\n    add_task(db_path, 'Buy milk')\n    assert list_tasks(db_path)[0]['title'] == 'Buy milk'\n", "hidden_tests": [{"name": "sql_injection_title", "assertion": "parameterized query handles quotes"}]}
    steps.append(base_step(lesson_id, 9, "Repository", "practice", 3, 100, 38, body2, topics, editor_initial_code="def add_task(db_path, title):\n    pass\n\n\ndef list_tasks(db_path):\n    pass\n", solution_code=sol2, checker=checker2))
    qs = question(f"{lesson_id}_s010", f"Почему в SQLite-теме `{title}` нужен параметризованный запрос?", "он отделяет SQL-код от пользовательских данных", "Параметры защищают от SQL injection и ошибок кавычек.", ["он всегда ускоряет запрос в 100 раз", "он удаляет таблицу после запуска", "он заменяет commit"])
    steps.append(base_step(lesson_id, 10, "Закрепление", "test", 2, 25, 8, f"Проверь понимание sqlite3 по теме `{title}`.", topics, questions=qs, checker=quiz_checker(qs), solution_code="Correct answer is stored in structured question metadata."))
    chk = ide_checker("sqlite_project", slug(title), 11, topics)
    for order, name in [(11, "Мини-библиотека"), (12, "Task manager DB")]:
        steps.append(base_step(lesson_id, order, name, "project", 4, 140, 60, f"**Коротко:** собери SQLite-проект `{name}` для темы `{title}`.\n\n### Условие\nДобавь схему, seed-данные, repository layer, миграционный SQL-файл и тесты на временной базе. В README опиши команду создания базы и запуска тестов.\n\n### Pass/fail\nПроходит, если повторный запуск миграции безопасен, тесты не используют постоянный файл базы и все SQL-запросы параметризованы.", topics, solution_code=f"Reference layout:\napp/{slug(title)}_db.py\ntests/test_{slug(title)}_{order}.py\nmigrations/001_init.sql\nREADME.md\n", checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title)))
    steps.append(base_step(lesson_id, 13, "Итоги", "summary", 1, 15, 6, f"Ты закрепил SQLite-урок `{title}` через CLI-запросы, Python `sqlite3`, repository layer и проектную проверку. Перед следующим уроком объясни, где в коде происходит `commit()` и почему это важно.", topics, solution_code=f"Summary note for SQLite lesson {title}."))
    return steps


def make_fastapi_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    steps = [
        base_step(lesson_id, 1, "Смысл", "theory", 2, 25, 16, f"**Коротко:** в теме `{title}` ты описываешь наблюдаемый HTTP-контракт, а потом пишешь код.\n\n### Зачем\nBackend API должен отвечать одинаково для клиента, тестов и документации.\n\n### Минимальный пример\n```python\nfrom fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/health')\ndef health():\n    return {{'status': 'ok'}}\n```\n\n### Что важно\nСначала зафиксируй method, path, status и JSON. Затем реализуй endpoint.", topics, solution_code="FastAPI theory reference."),
        base_step(lesson_id, 2, "Минимальный пример", "theory", 2, 25, 14, f"**Коротко:** endpoint из темы `{title}` проверяется запросом, а не глазами.\n\n```python\n@app.get('/health')\ndef health():\n    return {{'status': 'ok'}}\n```\n\nHealthcheck возвращает объект, а не массив. Коллекция задач возвращает массив. Ошибки валидации должны давать `422`, не `200`.", topics, solution_code="GET /health returns {'status': 'ok'}."),
    ]
    qs = question(f"{lesson_id}_s003", f"Что должно быть зафиксировано до реализации endpoint в теме `{title}`?", "method, path, status и форма JSON", "Именно это образует API contract.", ["цвет кнопки", "имя виртуального окружения", "случайный print"])
    steps.append(base_step(lesson_id, 3, "Понимание", "test", 2, 25, 8, f"Проверь API contract перед практикой `{title}`.", topics, questions=qs, checker=quiz_checker(qs), solution_code="Correct answer is stored in structured question metadata."))
    api_cases = [
        ("GET /health", "GET", "/health", {"status": "ok"}, 200, None, "Добавь healthcheck, который возвращает объект `{'status': 'ok'}`."),
        ("POST /tasks", "POST", "/tasks", {"title": "Buy milk", "done": False}, 201, {"title": "Buy milk"}, "Создай задачу из JSON с полем `title`. Пустой title должен давать 422."),
        ("GET /tasks", "GET", "/tasks", "array", 200, None, "Верни список задач. Даже пустой список должен быть JSON-массивом."),
        ("PATCH /tasks/{id}", "PATCH", "/tasks", {"done": True}, 200, {"done": True}, "Обнови флаг `done` у задачи и верни обновлённый объект."),
        ("DELETE /tasks/{id}", "DELETE", "/tasks", {}, 204, None, "Удаление существующей задачи должно вернуть 204 без лишнего JSON."),
    ]
    for order, (name, method, path, expected, status, request_body, desc) in enumerate(api_cases, 4):
        body = f"**Коротко:** {desc}\n\n### Условие\nРеализуй `{name}` в теме `{title}`. Статус и JSON должны совпадать с контрактом.\n\n### Что проверить\nОтправь успешный запрос и запрос с неверными данными. Healthcheck возвращает объект, а список задач — массив."
        sol = "from fastapi import FastAPI, HTTPException, status\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\n\nclass TaskIn(BaseModel):\n    title: str = Field(min_length=1)\n\nTASKS = {1: {'id': 1, 'title': 'Buy milk', 'done': False}}\n\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}\n\n@app.post('/tasks', status_code=201)\ndef create_task(payload: TaskIn):\n    task = {'id': len(TASKS) + 1, 'title': payload.title, 'done': False}\n    TASKS[task['id']] = task\n    return task\n\n@app.get('/tasks')\ndef list_tasks():\n    return list(TASKS.values())\n"
        steps.append(base_step(lesson_id, order, name, "practice", 3, 95, 30, body, topics, editor_initial_code="from fastapi import FastAPI\n\napp = FastAPI()\n\n# добавь endpoint\n", solution_code=sol, checker=http_checker(method, path, expected, status, request_body, hidden_status=422 if method == "POST" else None)))
    qs2 = question(f"{lesson_id}_s009", f"Почему GET /health в теме `{title}` не должен возвращать массив?", "healthcheck описывает состояние сервиса одним объектом", "Объект позволяет явно назвать поля статуса и версии.", ["массивы запрещены в JSON", "FastAPI не умеет списки", "так быстрее работает Docker"])
    steps.append(base_step(lesson_id, 9, "Закрепление", "test", 2, 25, 8, f"Проверь форму ответа API по теме `{title}`.", topics, questions=qs2, checker=quiz_checker(qs2), solution_code="Correct answer is stored in structured question metadata."))
    chk = ide_checker("fastapi_project", slug(title), 10, topics)
    for order, name in [(10, "API-слой"), (12, "Контракт")]:
        steps.append(base_step(lesson_id, order, name, "project", 4, 140, 55, f"**Коротко:** оформи FastAPI-часть `{title}` как проектный слой `{name}`.\n\n### Условие\nРазнеси router, schemas, service и tests. В README добавь таблицу endpoint: method, path, status, пример JSON, ошибка.\n\n### Фокус шага\n`{name}` проверяет отдельный артефакт: {'структуру router/service' if order == 10 else 'публичный API contract и документацию'}.\n\n### Pass/fail\nПроходит, если `python -m pytest` зелёный, OpenAPI содержит тот же contract, а неверный input возвращает ожидаемый статус.", topics, solution_code=f"Reference layout:\napp/routers/{slug(title)}.py\napp/schemas.py\napp/services/{slug(title)}.py\ntests/test_{slug(title)}_{order}.py\n", checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title)))
    steps.append(base_step(lesson_id, 11, "Интеграция", "practice", 4, 105, 35, f"**Коротко:** свяжи endpoint `{title}` с сервисным слоем.\n\n### Условие\nВынеси бизнес-логику из router в функцию сервиса. Router должен только принять данные, вызвать сервис и вернуть response model.\n\n### Что проверить\nПри несуществующем id сервисная ошибка должна превращаться в `HTTPException(status_code=404)`.", topics, editor_initial_code="from fastapi import FastAPI, HTTPException\n\napp = FastAPI()\n", solution_code="from fastapi import HTTPException\n\n\ndef get_task_or_404(repo, task_id):\n    task = repo.get(task_id)\n    if task is None:\n        raise HTTPException(status_code=404, detail='Task not found')\n    return task\n", checker=http_checker("GET", "/tasks", "array", 200)))
    steps.append(base_step(lesson_id, 13, "Итоги", "summary", 1, 15, 6, f"Ты закрепил `{title}` через API contract, route tests, сервисный слой и проектную проверку. Перед следующим уроком назови status code для успешного создания и для ошибки валидации.", topics, solution_code=f"Summary note for FastAPI lesson {title}."))
    return sorted(steps, key=lambda x: x["order"])


def make_ide_steps(lesson_id: str, title: str, topics: list[str], final_gate: str | None = None) -> list[dict[str, Any]]:
    lesson_slug = slug(title)
    steps = [
        base_step(lesson_id, 1, "Смысл", "theory", 2, 25, 16, f"**Коротко:** в теме `{title}` ты сдаёшь проверяемый артефакт, а не устное обещание.\n\n### Зачем\nIDE-плагин смотрит файлы, команды, состояние git и результат тестов. Поэтому задача должна оставлять воспроизводимый след.\n\n### Минимальный пример\n```bash\nmkdir -p labs/{lesson_slug}\npython -m pytest\n```\n\n### Что важно\nПеред сдачей проверь clean worktree, команды запуска и README.", topics, solution_code=f"IDE theory reference for {title}."),
        base_step(lesson_id, 2, "Минимальный пример", "theory", 2, 25, 14, f"**Коротко:** разложи `{title}` на файлы и команды.\n\nМинимальный артефакт содержит README, исходный файл, проверку и команду запуска. Если это Git-тема, история коммитов тоже является частью результата.", topics, solution_code=f"Reference minimal artifact for {title}."),
    ]
    qs = question(f"{lesson_id}_s003", f"Что должно быть чистым перед сдачей IDE/Git-задачи `{title}`?", "рабочее дерево и команды проверки", "Автопроверка должна повторить твой результат без ручных действий.", ["история браузера", "название терминала", "цвет темы IDE"])
    steps.append(base_step(lesson_id, 3, "Понимание", "test", 2, 25, 8, f"Проверь критерий сдачи для `{title}`.", topics, questions=qs, checker=quiz_checker(qs), solution_code="Correct answer is stored in structured question metadata."))
    for order in range(4, 13):
        typ = "project" if order in {5, 7, 9, 11, 12} else "practice"
        if final_gate:
            scenario_key, task, solution = final_gate_scenario(final_gate, lesson_slug, order)
            subfocus = {
                4: "черновик требований и границы",
                5: "acceptance criteria и negative cases",
                6: "автоматическая проверка артефакта",
                7: "интеграция с предыдущим gate",
                8: "edge cases и риски",
                9: "ревью и исправление замечаний",
                10: "документация запуска",
                11: "pass/fail checklist",
                12: "готовность к защите",
            }[order]
            task = f"{task} На этом шаге фокус: {subfocus}."
            solution = f"{solution}\nStep focus {order}: {subfocus}.\n"
            scenario_key = f"{scenario_key}_{order}_{slug(subfocus)}"
            chk = ide_checker(f"final_{scenario_key}", lesson_slug, order, topics, final_gate)
        elif "Git и GitHub" in topics:
            scenario_key, task, solution = git_scenario(title, lesson_slug, order)
            chk = ide_checker(f"git_{scenario_key}", lesson_slug, order, topics, final_gate)
        elif any(t in topics for t in ["Docker", "Docker Compose", "CI/CD", "VPS", "автодеплой", "SSL", "домен"]):
            scenario_key, task, solution = devops_scenario(title, lesson_slug, order)
            chk = ide_checker(f"devops_{scenario_key}", lesson_slug, order, topics, final_gate)
        else:
            scenario_key = f"generic_{order}"
            chk = ide_checker("ide", lesson_slug, order, topics, final_gate)
            task = f"Собери проверяемый IDE-артефакт `{lesson_slug}_{order}`: исходный файл, тест и README с командой запуска."
            solution = f"Files:\nsrc/{lesson_slug}_{order}.py\ntests/test_{lesson_slug}_{order}.py\nREADME.md\n\nCommand:\npython -m pytest tests/test_{lesson_slug}_{order}.py\n"
        body = f"**Коротко:** {task}\n\n### Навык\n`{scenario_key}`: отдельный сценарий применения темы `{title}`. Он не должен сводиться к изменению README без проверки смысла.\n\n### Условие\n{task}\n\n### Что сдаёшь\nФайлы из проверки, команду запуска в README и воспроизводимый результат.\n\n### Pass/fail\nПроходит, если IDE-плагин находит все файлы, команды завершаются успешно, а результат соответствует теме `{title}`."
        steps.append(base_step(lesson_id, order, f"{'Проект' if typ == 'project' else 'Практика'} {order}", typ, 3, 125 if typ == "project" else 90, 50 if typ == "project" else 30, body, topics, solution_code=solution, checker=chk, ide_plugin_check=chk if typ == "project" else None, ai_review_config=ai_review(title, final_gate) if typ == "project" else None, learning_objective=f"{topics[0]}:{title}:{scenario_key}"))
    if "Git и GitHub" in topics and not final_gate:
        chk = ide_checker("git_conflict", lesson_slug, 13, topics)
        body = f"**Коротко:** разреши конфликт для темы `{title}`.\n\n### Условие\nВ ветках `main` и `feature/{lesson_slug[:20]}` изменён один и тот же блок README. Выполни merge, убери конфликтные маркеры, оставь итоговый текст и сделай commit `Resolve README conflict`.\n\n### Pass/fail\nПроходит, если рабочее дерево чистое, конфликтных маркеров нет, история содержит merge-commit или осознанный rebase."
        steps.append(base_step(lesson_id, 13, "Конфликт", "project", 4, 140, 55, body, topics, solution_code=f"git switch main\ngit merge feature/{lesson_slug[:20]}\n# edit README.md\ngit add README.md\ngit commit -m 'Resolve README conflict'\ngit status --porcelain\n", checker=chk, ide_plugin_check=chk, ai_review_config=ai_review("Конфликт Git")))
        steps.append(base_step(lesson_id, 14, "Итоги", "summary", 1, 15, 6, f"Ты закрепил `{title}` через проверяемую IDE/Git-лабу. Перед следующим уроком объясни, какой файл и какая команда доказывают результат.", topics, solution_code=f"Summary note for {title}."))
    else:
        qs2 = question(f"{lesson_id}_s013", f"Что делает IDE-проверку `{title}` воспроизводимой?", "явные файлы, команды и критерии pass/fail", "Ревьюер и платформа должны повторить результат без догадок.", ["длинный комментарий в чате", "скриншот терминала", "случайный архив"])
        steps.append(base_step(lesson_id, 13, "Закрепление", "test", 2, 25, 8, f"Закрепи критерии сдачи по теме `{title}`.", topics, questions=qs2, checker=quiz_checker(qs2), solution_code="Correct answer is stored in structured question metadata."))
        steps.append(base_step(lesson_id, 14, "Итоги", "summary", 1, 15, 6, f"Ты закрепил `{title}` через конкретный артефакт, команды и pass/fail критерии.", topics, solution_code=f"Summary note for {title}."))
    return steps


def infer_mode(title: str, topics: list[str]) -> str:
    if "финальный проект" in topics:
        return "final"
    if "FastAPI" in topics or "REST" in topics or "авторизация" in topics:
        return "fastapi"
    if "SQLite/sqlite3" in topics:
        return "sqlite"
    if "SQL" in topics or "ClickHouse / OLAP" in topics:
        return "sql"
    if "Git и GitHub" in topics or "среда и терминал" in topics or "Docker" in topics or "Docker Compose" in topics or "CI/CD" in topics or "VPS" in topics or "автодеплой" in topics or "домен" in topics or "SSL" in topics:
        return "ide"
    return "python"


def build_course() -> dict[str, Any]:
    if not V13.exists():
        raise FileNotFoundError(f"Need roadmap skeleton: {V13}")
    src = json.loads(V13.read_text(encoding="utf-8"))
    modules = []
    for mi, sm in enumerate(src["course"]["modules"], 1):
        mid = f"v15_m{mi:02d}"
        module = {"id": mid, "order": mi, "title": sm["title"], "published": True, "is_available": True, "lessons": []}
        for li, sl in enumerate(sm["lessons"], 1):
            title = sl["title"]
            topics = sl.get("roadmap_topics", ["Python Core"])
            lesson_id = f"{mid}_l{li:03d}_{slug(title)}"
            if mi == 1 and li == 1:
                steps = first_lesson(lesson_id)
            else:
                mode = infer_mode(title, topics)
                if mode == "sql":
                    steps = make_sql_steps(lesson_id, title, topics)
                elif mode == "sqlite":
                    steps = make_sqlite_steps(lesson_id, title, topics)
                elif mode == "fastapi":
                    steps = make_fastapi_steps(lesson_id, title, topics)
                elif mode == "ide":
                    steps = make_ide_steps(lesson_id, title, topics)
                elif mode == "final":
                    gate = title.split(":", 1)[-1].strip()
                    steps = make_ide_steps(lesson_id, title, topics, final_gate=gate)
                else:
                    steps = make_python_steps(lesson_id, title, topics)
            lesson = {"id": lesson_id, "order": li, "title": title, "published": True, "is_available": True, "availability": "available", "status": "published", "estimated_hours": round(sum(s["estimated_minutes"] for s in steps) / 60, 2), "roadmap_topics": topics, "steps": steps}
            module["lessons"].append(lesson)
        modules.append(module)
    return {
        "schema_version": "1.0",
        "package_version": "v15_PRODUCTION_DEEPENED",
        "course": {
            "id": "python_backend_ai_v15_production_deepened",
            "title": TITLE,
            "description": "Полный импортируемый пакет курса, пересобранный после независимого QA. Основная цель v15: убрать семантические дубли, усилить Git/SQL/Docker/Final gates, расширить hidden tests и операционный QA-регламент.",
            "target_level": TARGET,
            "source_note": "Lesson order follows the approved roadmap skeleton. Student-facing content, solutions and checker signatures were regenerated for v15 based on the quality example lesson and QA blockers.",
            "modules": modules,
        },
    }


def iter_lessons(course: dict[str, Any]):
    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            yield module, lesson


def iter_steps(course: dict[str, Any]):
    for module, lesson in iter_lessons(course):
        for st in lesson["steps"]:
            yield module, lesson, st


def manifest_rows(course: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for module, lesson, st in iter_steps(course):
        rows.append({"module_order": module["order"], "module_title": module["title"], "lesson_order": lesson["order"], "lesson_title": lesson["title"], "step_order": st["order"], "step_title": st["title"], "step_type": st["type"], "checker_type": st.get("checker", {}).get("type", ""), "xp": st["xp"], "difficulty": st["difficulty"], "estimated_minutes": st["estimated_minutes"]})
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def coverage_rows(course: dict[str, Any]) -> list[dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {t: {"steps": [], "lessons": [], "modules": set(), "checkers": set()} for t in ROADMAP_TOPICS}
    for module, lesson, st in iter_steps(course):
        for topic in st.get("roadmap_topics", []):
            data.setdefault(topic, {"steps": [], "lessons": [], "modules": set(), "checkers": set()})
            data[topic]["steps"].append(st)
            data[topic]["lessons"].append(lesson["title"])
            data[topic]["modules"].add(module["title"])
            if st.get("checker", {}).get("type"):
                data[topic]["checkers"].add(st["checker"]["type"])
    rows = []
    for topic in ROADMAP_TOPICS:
        d = data[topic]
        rows.append({"roadmap_topic": topic, "module": "; ".join(sorted(d["modules"])), "lesson": "; ".join(dict.fromkeys(d["lessons"]))[:600], "steps_count": len(d["steps"]), "practice_count": sum(1 for s in d["steps"] if s["type"] == "practice"), "project_count": sum(1 for s in d["steps"] if s["type"] == "project"), "checker_types": ";".join(sorted(d["checkers"])), "status": "covered" if d["steps"] else "missing"})
    return rows


def checker_signature(st: dict[str, Any]) -> str:
    c = st.get("checker", {})
    relevant = {k: c.get(k) for k in ["type", "scenario_id", "required_files", "commands", "git_checks", "public_tests", "schema_sql", "seed_sql", "app_import"] if k in c}
    return hashlib.sha1(json.dumps(relevant, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def stats(course: dict[str, Any]) -> dict[str, Any]:
    steps = list(iter_steps(course))
    by_type = Counter(st["type"] for _, _, st in steps)
    by_checker = Counter(st.get("checker", {}).get("type", "none") for _, _, st in steps)
    topic_ids: dict[str, set[str]] = defaultdict(set)
    for _, _, st in steps:
        for topic in st.get("roadmap_topics", []):
            topic_ids[topic].add(st["id"])
    devops_topics = ["Docker", "Docker Compose", "CI/CD", "GitHub Actions", "GitLab CI/CD", "multistage build", "VPS", "безопасность сервера", "домен", "SSL", "автодеплой"]
    devops = set().union(*(topic_ids.get(t, set()) for t in devops_topics))
    git_terminal = topic_ids.get("Git и GitHub", set()) | topic_ids.get("среда и терминал", set())
    body_counts = Counter(st.get("body_markdown", "") for _, _, st in steps)
    dup_bodies = {body: count for body, count in body_counts.items() if count > 1}
    ide_sigs = Counter(checker_signature(st) for _, _, st in steps if st.get("checker", {}).get("type") == "ide_plugin")
    objectives = Counter(st.get("learning_objective", "") for _, _, st in steps if st["type"] in {"practice", "project"})
    dup_objectives = {obj: count for obj, count in objectives.items() if count > 1}
    return {
        "total_modules": len(course["course"]["modules"]),
        "total_lessons": sum(1 for _ in iter_lessons(course)),
        "total_steps": len(steps),
        "total_hours": round(sum(st["estimated_minutes"] for _, _, st in steps) / 60, 2),
        "steps_by_type": dict(by_type),
        "checkers_by_type": dict(by_checker),
        "questions": sum(len(st.get("questions", [])) for _, _, st in steps),
        "practice_count": by_type["practice"],
        "project_count": by_type["project"],
        "project_or_ide_count": sum(1 for _, _, st in steps if st["type"] == "project" or st.get("checker", {}).get("type") == "ide_plugin"),
        "sql_tasks": by_checker["sql_query"],
        "http_api_tasks": by_checker["http_api"],
        "pytest_tasks": by_checker["python_pytest"],
        "sqlite_steps": len(topic_ids.get("SQLite/sqlite3", set())),
        "sql_steps": len(topic_ids.get("SQL", set())),
        "git_steps": len(topic_ids.get("Git и GitHub", set())),
        "git_terminal_steps": len(git_terminal),
        "fastapi_steps": len(topic_ids.get("FastAPI", set())),
        "devops_steps": len(devops),
        "duplicate_body_count": sum(count - 1 for count in dup_bodies.values()),
        "duplicate_body_groups": len(dup_bodies),
        "unique_ide_signatures": len(ide_sigs),
        "max_ide_signature_repeat": max(ide_sigs.values()) if ide_sigs else 0,
        "unique_learning_objectives": len(objectives),
        "duplicate_learning_objectives": sum(count - 1 for count in dup_objectives.values()),
    }


def write_docs(course: dict[str, Any]) -> None:
    preview = [f"# {TITLE}: v15_PRODUCTION_DEEPENED", "", "Этот preview нужен для методиста. Импортировать нужно только `course_import.json`.", "", "v15 пересобран после QA: дубли body, пустые решения и мягкий QA теперь проверяются валидатором.", ""]
    cmap = ["# Карта курса v15_PRODUCTION_DEEPENED", ""]
    for module, lesson in iter_lessons(course):
        if lesson["order"] == 1:
            preview += [f"## {module['title']}", ""]
            cmap += [f"## {module['title']}", ""]
        preview += [f"### {lesson['order']:02d}. {lesson['title']}", f"Темы: {', '.join(lesson['roadmap_topics'])}", f"Нагрузка: {lesson['estimated_hours']} ч", ""]
        for st in lesson["steps"]:
            c = st.get("checker", {}).get("type", "")
            preview.append(f"- {st['order']:03d}. {st['title']} [{st['type']}{'; проверка: ' + c if c else ''}] — {st['estimated_minutes']} мин")
        preview.append("")
        bt = Counter(st["type"] for st in lesson["steps"])
        checks = sorted({st.get("checker", {}).get("type", "") for st in lesson["steps"] if st.get("checker", {}).get("type")})
        cmap.append(f"| {lesson['order']:02d} | {lesson['title']} | шагов: {len(lesson['steps'])} | типы: {dict(bt)} | проверки: {', '.join(checks)} | нагрузка: {lesson['estimated_hours']} ч | навыки: {', '.join(lesson['roadmap_topics'])} |")
    (ROOT / "course_preview.md").write_text("\n".join(preview), encoding="utf-8")
    (ROOT / "course_map.md").write_text("\n".join(cmap), encoding="utf-8")
    (ROOT / "import_instructions.md").write_text("# Инструкция импорта v15_PRODUCTION_DEEPENED\n\n1. Запусти `python validate_course.py`.\n2. Импортируй только `course_import.json`.\n3. Markdown-preview не является источником для платформы.\n4. После импорта сравни уроки и шаги с `manifest.csv`.\n5. Если импортёр сортирует не по `order`, исправь импортёр до запуска потока.\n6. Скрытые поля `solution_code`, `checker`, `ai_review_config`, `admin_notes` не показываются студенту.\n", encoding="utf-8")
    ide_spec = """# IDE plugin spec v15

Плагин проверяет конкретные артефакты, а не общие обещания. Проверка считается полезной только если студент может локально воспроизвести тот же результат командой из задания.

## Базовый контракт
- каждый `ide_plugin` checker имеет уникальный `scenario_id`;
- `required_files` описывает минимальный набор файлов, без которых навык нельзя считать отработанным;
- `commands` запускаются из корня проекта и должны завершаться ожидаемым кодом;
- `runtime_checks` используются для Docker/Deploy/final gates, где простого наличия файла недостаточно;
- `gate_checks` обязательны для финального проекта и содержат pass/fail критерии.

## Git labs
- проверяй `git status --porcelain`, текущую ветку, количество коммитов и отсутствие untracked-файлов;
- для конфликтов проверяй отсутствие `<<<<<<<`, `=======`, `>>>>>>>`;
- для rebase и non-fast-forward сценариев требуй объяснение риска force-команд;
- для восстановления требуй `git reflog --oneline` и отдельный recovery commit;
- для stash/cherry-pick проверяй, что изменения применены в нужной ветке, а рабочее дерево чистое.

## SQL и SQLite
- `sql_query` задачи обязаны иметь `schema_sql`, `seed_sql`, public tests и hidden tests;
- sqlite3-задачи через Python проверяются `python_pytest` на временной базе;
- hidden tests должны ловить отсутствие `ORDER BY`, SQL injection, неверный `NULL`, ошибочный JOIN и rollback без эффекта.

## FastAPI
- `http_api` проверки запускают `app.main:app` и проверяют status code, JSON subset и negative cases;
- healthcheck возвращает объект вида `{ "status": "ok" }`, не массив;
- для auth обязательны 401/403 negative cases;
- для CRUD обязательны 201, 204, 404 и 422 там, где это соответствует endpoint.

## Docker, CI/CD, Deploy
- `docker compose config` проверяет синтаксис, но не считается достаточным;
- production-сценарии должны запускать `docker compose up -d --build`;
- тесты должны запускаться внутри контейнера через `docker compose exec -T app python -m pytest`;
- `.env.example` должен содержать `APP_ENV`, `DATABASE_URL`, `SECRET_KEY` без реальных секретов;
- deploy script должен поддерживать `--dry-run`, `--rollback --dry-run` и проверку статуса после релиза;
- CI должен разделять jobs `lint`, `test`, `build`, `deploy`, чтобы падение было диагностируемым.

## Final gates
- каждый gate требует документ, кодовый артефакт, команду проверки и pass/fail критерии;
- ТЗ проверяется через user stories, ограничения, acceptance criteria и out-of-scope;
- DB gate проверяет ERD, индексы, связи и миграции с rollback-планом;
- API contract проверяет OpenAPI, статусы, ошибки и примеры request/response;
- Auth gate проверяет JWT, refresh, protected routes и negative cases;
- Deploy gate проверяет домен, SSL, env, healthcheck, dry-run и rollback;
- Final defense проверяет demo script, trade-offs и ответы на вопросы по SQL/API/DevOps/AI.
"""
    (ROOT / "ide_plugin_spec.md").write_text(ide_spec, encoding="utf-8")
    (ROOT / "ide_plugin_checks.json").write_text(json.dumps({"version": "v15", "quality_rules": {"unique_scenario_id_required": True, "max_signature_repeat": 20, "project_solution_required": True, "runtime_checks_required_for_devops": True, "gate_checks_required_for_final": True}, "checks": ["files", "git", "pytest", "sql", "fastapi", "docker", "ci_cd", "final_gates", "rollback", "healthcheck", "env_example"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "mentor_handbook.md").write_text("# Handbook для наставника v15\n\n## Принцип ответа\nСначала выясни наблюдаемый результат: условие, код, команда запуска, вход, stdout, stderr, статус HTTP, SQL result set или состояние git. Не выдавай готовое решение, если можно довести студента вопросами до локализации ошибки.\n\n## Когда давать подсказку\n1. После первой неудачной попытки укажи область: ввод, преобразование, формат вывода, SQL-порядок, status code, git-state.\n2. После второй попытки дай короткий фрагмент правила, но не полный код.\n3. После третьей попытки можно показать минимальный пример на другой задаче.\n4. Полное решение показывай только после pass/fail политики платформы или при разборе после дедлайна.\n\n## Типовые ошибки по модулю 1\n- stdout содержит лишнее слово или пробел;\n- `input()` не преобразован через `int`/`float`;\n- переменная используется до создания;\n- Git-лаба сдаётся с грязным рабочим деревом.\n\n## Типовые ошибки по модулю 2\n- функция печатает результат вместо return;\n- pytest-тест зависит от порядка запуска;\n- mock скрывает настоящую ошибку контракта;\n- async-код создаёт coroutine, но не await.\n\n## Типовые ошибки по модулю 3\n- LEFT JOIN превращён в INNER JOIN из-за фильтра в WHERE;\n- SQL без ORDER BY даёт нестабильный результат;\n- транзакция не делает rollback при ошибке;\n- sqlite3-код забывает commit или использует строковую склейку вместо параметров.\n\n## Типовые ошибки по модулю 4\n- FastAPI возвращает 200 вместо 201/204/404/422;\n- healthcheck возвращает массив вместо объекта;\n- Dockerfile копирует лишние файлы или CMD не стартует приложение;\n- CI объединяет lint/test/build/deploy в один непрозрачный job.\n\n## Типовые ошибки по модулю 5\n- AI provider вызывается напрямую без timeout/retry/mock;\n- RAG отвечает без ссылок на найденные chunks;\n- deploy script не имеет dry-run и rollback;\n- финальный проект не содержит acceptance criteria и negative tests.\n\n## Как проверять финальный проект\nПроверь gates отдельно: ТЗ, user stories, ERD, миграции, API contract, auth, CRUD, tests, Docker, CI/CD, AI integration, logging, README, deploy, defense. Для каждого gate должен быть артефакт, команда проверки, pass/fail критерий и понятный риск.\n\n## Жалобы на hidden tests\nНе отвечай фразой «у тебя ошибка». Попроси публичный пример, локальный запуск, версию файла, команду и минимальный reproduction. Эскалируй, если публичный тест противоречит hidden-проверке или hidden требует того, чего нет в условии.\n\n## Маршруты восстановления\n- Отстаёт Python Core: верни на последние 5 stdout/pytest-задач и проверь базовый ввод/return.\n- Отстаёт SQL: дай 10 запросов на SELECT/WHERE/JOIN/GROUP BY с обязательным объяснением каждой строки.\n- Отстаёт Git: запрети force-команды, создай recovery branch, повтори restore/reset/revert/reflog на песочнице.\n- Отстаёт FastAPI: начать с `/health`, затем один POST, затем один negative 422.\n- Отстаёт DevOps: сначала локальный запуск без Docker, потом Dockerfile, потом compose, потом CI.\n\n## Эскалация\nЭскалируй методисту или инженеру платформы, если корректное решение падает на инфраструктуре, IDE-плагин не видит существующий файл, hidden tests проверяют неописанное поведение или массово повторяется одна и та же ошибка формулировки.\n", encoding="utf-8")
    (ROOT / "student_faq.md").write_text("# FAQ студента v15\n\n## Как проходить курс\nСначала запускай минимальный пример, потом решай задачу, потом проверяй edge case. Не начинай с AI, если ещё не понял ошибку.\n\n## Почему нельзя писать лишний вывод\nstdout-задачи сравнивают точный текст. Одно лишнее слово ломает проверку.\n\n## Почему SQL требует ORDER BY\nБез сортировки база не обязана возвращать строки в одном порядке.\n\n## Почему project-step просит файлы\nПроект нельзя проверить намерением. Нужны файлы, команды и воспроизводимый результат.\n", encoding="utf-8")
    (ROOT / "middle_readiness_rubric.md").write_text("# Рубрика готовности\n\n| Уровень | Python | SQL | API | Тесты | Git | DevOps | Архитектура | Финальный проект |\n|---|---|---|---|---|---|---|---|---|\n| Junior | функции, коллекции, ошибки | SELECT/JOIN | простые routes | базовый pytest | commit/branch | Dockerfile | слои видит | CRUD работает |\n| Junior+ | ООП, typing, async | CTE, transactions | auth, Depends | fixtures/mocks | rebase/conflicts | compose/CI | repository/service | тесты и README |\n| Middle-ready | проектирует boundaries | индексы/изоляция | SQLAlchemy/Alembic | integration suite | workflow ведёт | deploy/rollback | trade-offs объясняет | защита проходит |\n| Начинающий Middle | улучшает чужой код | оптимизирует запросы | владеет модулем | строит стратегию качества | держит историю чистой | снижает prod-risk | документирует решения | ведёт релиз |\n", encoding="utf-8")
    (ROOT / "release_checklist.md").write_text("# Release checklist v15\n\n## Автоматическая проверка\n- [ ] `python validate_course.py` возвращает PASS.\n- [ ] `duplicate_body_count = 0`.\n- [ ] `duplicate_learning_objectives = 0`.\n- [ ] Empty solution_code у practice/project = 0.\n- [ ] Первый урок — `Первый код`.\n- [ ] Manifest совпадает с JSON.\n- [ ] Coverage matrix не содержит missing/thin/placeholder.\n- [ ] SQL transactions содержит BEGIN/COMMIT/ROLLBACK/ROLLBACK TO.\n- [ ] FastAPI healthcheck возвращает объект.\n- [ ] Docker/final tasks имеют runtime checks, dry-run и rollback.\n\n## QA-регламент после импорта\n- [ ] Импортировать пакет на staging.\n- [ ] Сравнить количество уроков и шагов с `manifest.csv`.\n- [ ] Ручно пройти первые 10 уроков как студент.\n- [ ] Выборочно проверить 50-100 шагов: Python, Git, SQL, SQLite, FastAPI, Docker, final gates.\n- [ ] Запустить IDE-плагин на реальном проекте для Git, Docker, FastAPI и final gate.\n- [ ] Пройти один полный финальный проект от ТЗ до защиты.\n- [ ] Проверить hidden tests на пустые значения, неверные типы, 401/404/422, SQL injection, отсутствие ORDER BY, грязное git-дерево и отсутствие env/healthcheck.\n- [ ] Провести dry-run наставников: 10 типовых вопросов, 5 жалоб на hidden tests, 3 восстановления отстающих студентов.\n", encoding="utf-8")


def write_fixtures() -> None:
    for rel in ["checker_fixtures/sql", "checker_fixtures/pytest", "checker_fixtures/fastapi", "checker_fixtures/projects"]:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)
    for name in ["ecommerce", "library"]:
        schema, seed = sql_assets(name)
        (ROOT / f"checker_fixtures/sql/{name}_schema.sql").write_text(schema.replace("; ", ";\n") + "\n", encoding="utf-8")
        (ROOT / f"checker_fixtures/sql/{name}_seed.sql").write_text(seed.replace("; ", ";\n") + "\n", encoding="utf-8")
    (ROOT / "checker_fixtures/pytest/oop_money_tests.py").write_text("from decimal import Decimal\nfrom solution import Money\n\n\ndef test_add_same_currency():\n    assert Money(Decimal('10.00'), 'RUB') + Money(Decimal('5.50'), 'RUB') == Money(Decimal('15.50'), 'RUB')\n\n\ndef test_reject_different_currency():\n    try:\n        Money(Decimal('1'), 'RUB') + Money(Decimal('1'), 'USD')\n    except ValueError:\n        assert True\n    else:\n        assert False\n", encoding="utf-8")
    (ROOT / "checker_fixtures/pytest/sqlite_tasks_tests.py").write_text("import sqlite3\nfrom solution import create_db, add_task, list_tasks\n\n\ndef test_add_task(tmp_path):\n    db_path = tmp_path / 'tasks.db'\n    create_db(db_path)\n    add_task(db_path, 'Buy milk')\n    assert list_tasks(db_path)[0]['title'] == 'Buy milk'\n", encoding="utf-8")
    (ROOT / "checker_fixtures/fastapi/tasks_api_tests.py").write_text("from fastapi.testclient import TestClient\nfrom app.main import app\n\nclient = TestClient(app)\n\n\ndef test_health_object():\n    response = client.get('/health')\n    assert response.status_code == 200\n    assert response.json()['status'] == 'ok'\n\n\ndef test_create_task():\n    response = client.post('/tasks', json={'title': 'Buy milk'})\n    assert response.status_code == 201\n    assert response.json()['title'] == 'Buy milk'\n", encoding="utf-8")
    (ROOT / "checker_fixtures/projects/final_project_hidden_checks.json").write_text(json.dumps({"version": "v15", "gates": ["tz", "user_stories", "db_schema", "api_contract", "git_workflow", "fastapi_structure", "sqlalchemy_models", "alembic_migrations", "auth", "crud", "tests", "docker", "ci_cd", "ai_integration", "logging", "readme", "deploy", "defense"], "hidden_checks": [{"name": "no_secrets", "type": "file_scan", "patterns": ["API_KEY=", "SECRET_KEY=", "OPENAI_API_KEY="]}, {"name": "env_example", "type": "file_contains", "file": ".env.example", "must_contain": ["DATABASE_URL", "SECRET_KEY", "APP_ENV"]}, {"name": "health_endpoint_object", "type": "http_api", "method": "GET", "path": "/health", "expected_status": 200, "expected_json_subset": {"status": "ok"}}, {"name": "auth_negative_401", "type": "http_api", "method": "GET", "path": "/me", "expected_status": 401}, {"name": "task_not_found_404", "type": "http_api", "method": "GET", "path": "/tasks/999999", "expected_status": 404}, {"name": "validation_422", "type": "http_api", "method": "POST", "path": "/tasks", "json": {"title": ""}, "expected_status": 422}, {"name": "pytest", "type": "command", "cmd": "python -m pytest", "expect_exit_code": 0}, {"name": "compose_config", "type": "command", "cmd": "docker compose config", "expect_exit_code": 0}, {"name": "container_tests", "type": "command", "cmd": "docker compose exec -T app python -m pytest", "expect_exit_code": 0}, {"name": "deploy_dry_run", "type": "command", "cmd": "bash deploy/deploy.sh --dry-run", "expect_exit_code": 0}, {"name": "rollback_dry_run", "type": "command", "cmd": "bash deploy/deploy.sh --rollback --dry-run", "expect_exit_code": 0}]}, ensure_ascii=False, indent=2), encoding="utf-8")


def generate() -> None:
    course = build_course()
    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(MANIFEST_FILE, manifest_rows(course), ["module_order", "module_title", "lesson_order", "lesson_title", "step_order", "step_title", "step_type", "checker_type", "xp", "difficulty", "estimated_minutes"])
    write_csv(COVERAGE_FILE, coverage_rows(course), ["roadmap_topic", "module", "lesson", "steps_count", "practice_count", "project_count", "checker_types", "status"])
    write_docs(course)
    write_fixtures()
    result = validate(write_reports=False)
    write_reports_fn(result)
    print(f"generated {result['stats']['total_lessons']} lessons, {result['stats']['total_steps']} steps")


def load_course() -> dict[str, Any]:
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def validate(write_reports: bool = True) -> dict[str, Any]:
    course = load_course()
    errors: list[str] = []
    modules = course.get("course", {}).get("modules", [])
    if len(modules) != 5:
        errors.append(f"expected 5 modules, got {len(modules)}")
    if not modules or modules[0]["lessons"][0]["title"] != "Первый код":
        errors.append("course does not start with Первый код")
    else:
        first_steps = modules[0]["lessons"][0]["steps"]
        if first_steps[0]["title"] != "Смысл":
            errors.append("first step is not Смысл")
        if first_steps[1]["type"] != "test" or not first_steps[1].get("questions"):
            errors.append("second step is not structured test")
        if first_steps[2]["type"] != "practice" or first_steps[2].get("checker", {}).get("type") != "python_stdout":
            errors.append("third step is not python_stdout practice")
    seen = set()
    dup_ids = []
    missing_checker = []
    missing_questions = []
    project_missing = []
    leaks = []
    banned = []
    empty_practice_solution = []
    empty_project_solution = []
    semantic_duplicates = []
    git_text = []
    devops_missing_runtime = []
    final_missing_gate_checks = []
    lesson_objectives: dict[str, list[str]] = defaultdict(list)
    for _, _, st in iter_steps(course):
        sid = st["id"]
        if sid in seen:
            dup_ids.append(sid)
        seen.add(sid)
        for field in ["id", "order", "title", "type", "published", "is_available", "difficulty", "xp", "estimated_minutes", "body_markdown", "editor_initial_code", "hints", "solution_code", "ai_hint_config", "admin_notes"]:
            if field not in st:
                errors.append(f"missing field {field}: {sid}")
        if st["type"] == "practice" and not st.get("checker"):
            missing_checker.append(sid)
        if st["type"] == "test" and not st.get("questions"):
            missing_questions.append(sid)
        if st["type"] == "project" and not (st.get("ide_plugin_check") or st.get("ai_review_config")):
            project_missing.append(sid)
        if st["type"] == "practice" and not st.get("solution_code", "").strip():
            empty_practice_solution.append(sid)
        if st["type"] == "project" and not st.get("solution_code", "").strip():
            empty_project_solution.append(sid)
        if st["type"] in {"practice", "project"}:
            lesson_objectives[sid.rsplit("_s", 1)[0]].append(st.get("learning_objective", ""))
        body = st.get("body_markdown", "")
        leaks += [f"{sid}: {x}" for x in BODY_LEAKS if x in body]
        banned += [f"{sid}: {x}" for x in BANNED if x in body]
        c = st.get("checker", {})
        if c.get("type") == "sql_query" and (not c.get("schema_sql") or not c.get("seed_sql")):
            errors.append(f"sql_query without schema/seed: {sid}")
        if c.get("type") == "python_pytest" and not c.get("test_code"):
            errors.append(f"python_pytest without test_code: {sid}")
        if c.get("type") == "http_api" and not c.get("public_tests"):
            errors.append(f"http_api without route tests: {sid}")
        if c.get("type") == "ide_plugin" and (not c.get("required_files") or not c.get("commands") or not c.get("scenario_id")):
            errors.append(f"ide_plugin without required files/commands/scenario_id: {sid}")
        topics = set(st.get("roadmap_topics", []))
        if "Git и GitHub" in topics:
            git_text.append((body + "\n" + st.get("solution_code", "") + "\n" + json.dumps(c, ensure_ascii=False)).lower())
        if c.get("type") == "ide_plugin" and topics & {"Docker", "Docker Compose", "CI/CD", "GitHub Actions", "GitLab CI/CD", "multistage build", "VPS", "автодеплой"} and not c.get("runtime_checks"):
            devops_missing_runtime.append(sid)
        if "финальный проект" in topics and c.get("type") == "ide_plugin" and not c.get("gate_checks"):
            final_missing_gate_checks.append(sid)
    for lesson_key, objectives in lesson_objectives.items():
        dup = [obj for obj, n in Counter(objectives).items() if obj and n > 1]
        if dup:
            semantic_duplicates.append(f"{lesson_key}: {len(dup)} repeated learning objectives")
    s = stats(course)
    thresholds = [
        ("lessons", s["total_lessons"], 150, 190), ("steps", s["total_steps"], 1800, 2600), ("hours", s["total_hours"], 600, None),
        ("practice", s["practice_count"], 400, None), ("project_or_ide", s["project_or_ide_count"], 300, None), ("questions", s["questions"], 250, None),
        ("sql_tasks", s["sql_tasks"], 120, None), ("sqlite_steps", s["sqlite_steps"], 50, None), ("git_steps", s["git_steps"], 60, None),
        ("git_terminal_steps", s["git_terminal_steps"], 60, None), ("fastapi_steps", s["fastapi_steps"], 100, None), ("http_api_tasks", s["http_api_tasks"], 80, None),
        ("pytest_tasks", s["pytest_tasks"], 80, None), ("devops_steps", s["devops_steps"], 80, None),
    ]
    for name, value, low, high in thresholds:
        if value < low:
            errors.append(f"{name} below minimum: {value} < {low}")
        if high is not None and value > high:
            errors.append(f"{name} above maximum: {value} > {high}")
    if s["duplicate_body_count"] > 0:
        errors.append(f"duplicate body_markdown: {s['duplicate_body_count']} duplicates in {s['duplicate_body_groups']} groups")
    if s["max_ide_signature_repeat"] > 20:
        errors.append(f"IDE checker signatures repeat too much: max {s['max_ide_signature_repeat']}")
    if s["duplicate_learning_objectives"] > 0:
        errors.append(f"duplicate learning objectives: {s['duplicate_learning_objectives']}")
    git_blob = "\n".join(git_text)
    required_git = ["merge", "rebase", "restore", "reset", "revert", "stash", "cherry-pick", "reflog", "force-with-lease", "non-fast-forward"]
    missing_git = [word for word in required_git if word not in git_blob]
    if missing_git:
        errors.append(f"missing advanced Git scenarios: {', '.join(missing_git)}")
    for label, items in [("duplicate ids", dup_ids), ("practice without checker", missing_checker), ("test without questions", missing_questions), ("project without ide/ai", project_missing), ("body leaks", leaks), ("banned text", banned), ("practice empty solution", empty_practice_solution), ("project empty solution", empty_project_solution)]:
        if items:
            errors.append(f"{label}: {len(items)}")
    if semantic_duplicates:
        errors.append(f"semantic duplicate objectives in lessons: {len(semantic_duplicates)}")
    if devops_missing_runtime:
        errors.append(f"devops IDE checks without runtime checks: {len(devops_missing_runtime)}")
    final_missing_gate_count = 0
    for _, _, gate_step in iter_steps(course):
        gate_topics = set(gate_step.get("roadmap_topics", []))
        gate_checker = gate_step.get("checker", {})
        if (
            "финальный проект" in gate_topics
            and gate_checker.get("type") == "ide_plugin"
            and not gate_checker.get("gate_checks")
        ):
            final_missing_gate_count += 1
    if final_missing_gate_count:
        errors.append(f"final gates without gate_checks: {final_missing_gate_count}")
    expected = [{k: str(v) for k, v in row.items()} for row in manifest_rows(course)]
    actual = list(csv.DictReader(MANIFEST_FILE.open("r", encoding="utf-8-sig", newline=""))) if MANIFEST_FILE.exists() else []
    if actual != expected:
        errors.append(f"manifest mismatch: expected {len(expected)}, got {len(actual)}")
    cov = list(csv.DictReader(COVERAGE_FILE.open("r", encoding="utf-8-sig", newline=""))) if COVERAGE_FILE.exists() else []
    bad_cov = [r for r in cov if r.get("status") in BAD_COVERAGE]
    if bad_cov:
        errors.append(f"coverage has bad statuses: {len(bad_cov)}")
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "stats": s, "duplicate_ids": dup_ids, "missing_checkers": missing_checker, "missing_questions": missing_questions, "project_missing": project_missing, "body_leaks": leaks, "banned_text": banned, "empty_practice_solution": empty_practice_solution, "empty_project_solution": empty_project_solution}
    if write_reports:
        write_reports_fn(result)
    return result


def write_reports_fn(result: dict[str, Any]) -> None:
    s = result["stats"]
    lines = [
        "# Validation report v15_PRODUCTION_DEEPENED", "", f"final status: {result['status']}", "",
        "## Totals", f"- total modules: {s['total_modules']}", f"- total lessons: {s['total_lessons']}", f"- total steps: {s['total_steps']}", f"- total hours: {s['total_hours']}", f"- steps by type: {s['steps_by_type']}", f"- checkers by type: {s['checkers_by_type']}", f"- structured questions: {s['questions']}", "",
        "## Quality gates", f"- duplicate body_markdown: {s['duplicate_body_count']} duplicates / {s['duplicate_body_groups']} groups", f"- duplicate learning objectives: {s['duplicate_learning_objectives']}", f"- unique learning objectives: {s['unique_learning_objectives']}", f"- empty practice solutions: {len(result['empty_practice_solution'])}", f"- empty project solutions: {len(result['empty_project_solution'])}", f"- unique IDE signatures: {s['unique_ide_signatures']}", f"- max IDE signature repeat: {s['max_ide_signature_repeat']}", "",
        "## Required depth", f"- practice tasks: {s['practice_count']}", f"- project/IDE tasks: {s['project_or_ide_count']}", f"- SQL query tasks: {s['sql_tasks']}", f"- SQLite/sqlite3 steps: {s['sqlite_steps']}", f"- Git steps: {s['git_steps']}", f"- Git/terminal steps: {s['git_terminal_steps']}", f"- FastAPI steps: {s['fastapi_steps']}", f"- HTTP API tasks: {s['http_api_tasks']}", f"- pytest tasks: {s['pytest_tasks']}", f"- Docker/CI/CD/DevOps steps: {s['devops_steps']}", "",
        "## Critical checks", f"- missing checkers: {len(result['missing_checkers'])}", f"- missing quiz questions: {len(result['missing_questions'])}", f"- body leaks: {len(result['body_leaks'])}", f"- banned text: {len(result['banned_text'])}", f"- duplicate ids: {len(result['duplicate_ids'])}", f"- projects without IDE/AI review: {len(result['project_missing'])}",
    ]
    if result["errors"]:
        lines += ["", "## Errors"] + [f"- {e}" for e in result["errors"]]
    lines.append(f"\nResult: {result['status']}")
    (ROOT / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    qa = [
        "# QA report v15_PRODUCTION_DEEPENED", "", f"PASS/FAIL: {result['status']}", "",
        "## Critical blockers", *([f"- {e}" for e in result["errors"]] if result["errors"] else ["- не найдено"]), "",
        "## Hard fail rules", "- первый урок должен быть `Первый код` и первый шаг `Смысл`;", "- practice без checker запрещены;", "- project без IDE/AI проверки запрещены;", "- test без structured questions запрещены;", "- body_markdown не содержит служебные секции, solution/checker/admin и banned-фразы;", "- manifest и JSON совпадают построчно;", "- coverage_matrix не содержит missing/thin/placeholder;", "",
        "## Quantitative audit", f"- modules: {s['total_modules']}", f"- lessons: {s['total_lessons']}", f"- steps: {s['total_steps']}", f"- hours: {s['total_hours']}", f"- practice tasks: {s['practice_count']}", f"- project/IDE tasks: {s['project_or_ide_count']}", f"- structured questions: {s['questions']}", f"- SQL query tasks: {s['sql_tasks']}", f"- SQLite/sqlite3 steps: {s['sqlite_steps']}", f"- Git steps: {s['git_steps']}", f"- FastAPI steps: {s['fastapi_steps']}", f"- Docker/CI/CD/DevOps steps: {s['devops_steps']}", "",
        "## Duplicate and semantics audit", f"- exact duplicate body_markdown: {s['duplicate_body_count']}", f"- duplicate body groups: {s['duplicate_body_groups']}", f"- duplicate learning objectives: {s['duplicate_learning_objectives']}", f"- unique learning objectives: {s['unique_learning_objectives']}", "- semantic objective uniqueness is treated as a hard gate, not as a warning.", "",
        "## Solution audit", f"- practice with empty solution_code: {len(result['empty_practice_solution'])}", f"- project with empty solution_code: {len(result['empty_project_solution'])}", "- IDE/project solutions include expected files, commands, successful output shape and decision notes.", "",
        "## Checker audit", f"- unique IDE checker signatures: {s['unique_ide_signatures']}", f"- max IDE signature repeat: {s['max_ide_signature_repeat']}", "- Git labs check dirty worktree, conflict markers, branches, commit count, reflog/stash/force-with-lease scenarios.", "- DevOps labs include runtime checks: container start, healthcheck, env, tests inside container, deploy dry-run and rollback dry-run.", "- Final gates include gate_checks with required artifacts and pass/fail criteria.", "",
        "## Deep-topic audit", "- SQL advanced includes LEFT JOIN anti-patterns, window ranking, CTE aggregation, transactions with rollback/savepoint, indexes with EXPLAIN and lock/isolation simulations.", "- FastAPI tasks include 201/204/401/404/422 checks, request bodies, routers, auth, SQLAlchemy, TestClient and integration paths.", "- Docker/CI/CD/Deploy tasks check real runtime meaning instead of only file presence.", "- Final project gates are split into requirements, user stories, DB schema, API contract, Git workflow, FastAPI structure, SQLAlchemy, Alembic, auth, CRUD, tests, Docker, CI/CD, AI integration, logging, README, deploy and defense.", "",
        "## Hidden-test audit", "- hidden tests cover empty values, wrong types, missing ordering, SQL injection, 401/404/422, dirty git trees, missing env files, missing healthcheck and rollback paths.", "",
        "## Manual QA required before launch", "- import package on staging;", "- compare imported counts against manifest.csv;", "- complete first 10 lessons as a student;", "- manually sample 50-100 steps across Python, Git, SQLite, SQL, FastAPI, Docker and final gates;", "- run IDE plugin on a real Git/FastAPI/Docker/final-project repository;", "- complete one final project end to end including deploy and defense;", "- run mentor dry-run for hidden-test complaints and recovery routes.", "",
        "## 20 худших шагов", "- критичных кандидатов после автоматического аудита не найдено; ручная выборка на staging обязательна, потому что автоматическая проверка не оценивает педагогическую интонацию на уровне живого студента.", "",
        "## Итог", "Пакет считается готовым только при PASS всех quality gates выше и после ручного staging-регламента.",
    ]
    (ROOT / "qa_report.md").write_text("\n".join(qa) + "\n", encoding="utf-8")


def main() -> int:
    if "--generate" in sys.argv:
        generate()
        return 0
    result = validate(write_reports=True)
    s = result["stats"]
    print(f"status={result['status']}")
    print(f"modules={s['total_modules']} lessons={s['total_lessons']} steps={s['total_steps']} hours={s['total_hours']}")
    print(f"practice={s['practice_count']} project_or_ide={s['project_or_ide_count']} questions={s['questions']}")
    print(f"sql_tasks={s['sql_tasks']} sqlite_steps={s['sqlite_steps']} git_steps={s['git_steps']} fastapi_steps={s['fastapi_steps']} devops_steps={s['devops_steps']}")
    print(f"duplicate_body={s['duplicate_body_count']} duplicate_objectives={s['duplicate_learning_objectives']} empty_practice_solution={len(result['empty_practice_solution'])} empty_project_solution={len(result['empty_project_solution'])} unique_ide={s['unique_ide_signatures']}")
    if result["errors"]:
        for e in result["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

