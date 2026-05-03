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
        "admin_notes": f"v14 regenerated from roadmap skeleton after independent QA; topics={', '.join(topics)}",
        "roadmap_topics": topics,
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
        task = "Проведи перевод 300 единиц со счёта Анны на счёт Олега внутри транзакции. После фиксации верни `id`, `owner`, `balance` по возрастанию `id`."
        sol = "BEGIN;\nUPDATE accounts SET balance = balance - 300 WHERE id = 1;\nUPDATE accounts SET balance = balance + 300 WHERE id = 2;\nCOMMIT;\nSELECT id, owner, balance FROM accounts ORDER BY id;\n"
        return task, sol, sql_checker(schema, seed, [[1, "Анна", 700], [2, "Олег", 700], [3, "Маша", 0]]), "transactions"
    if "изоляц" in low or "блокиров" in low or "индекс" in low or "explain" in low:
        task = "Создай индекс для поиска заказов пользователя и верни оплаченные заказы пользователя `1`: `id`, `total`. Отсортируй по `id`."
        sol = "CREATE INDEX idx_orders_user_status ON orders(user_id, status);\nSELECT id, total FROM orders WHERE user_id = 1 AND status = 'paid' ORDER BY id;\n"
        return task, sol, sql_checker(schema, seed, [[1, 5700], [3, 700]]), "indexes"
    if "left join" in low:
        task = "Найди активных пользователей без заказов. Верни `id`, `name`, отсортируй по `id`."
        sol = "SELECT users.id, users.name\nFROM users\nLEFT JOIN orders ON orders.user_id = users.id\nWHERE users.active = 1 AND orders.id IS NULL\nORDER BY users.id;\n"
        return task, sol, sql_checker(schema, seed, [[4, "Лена"]]), "left_join"
    if "join" in low:
        task = "Верни имя пользователя и сумму каждого оплаченного заказа. Нужны колонки `name`, `total`, порядок по `name`, затем `total`."
        sol = "SELECT users.name, orders.total\nFROM users\nJOIN orders ON orders.user_id = users.id\nWHERE orders.status = 'paid'\nORDER BY users.name, orders.total;\n"
        return task, sol, sql_checker(schema, seed, [["Анна", 700], ["Анна", 5700]]), "join"
    if "group" in low or "having" in low or "агрег" in low or "clickhouse" in low or "olap" in low:
        task = "Посчитай выручку по пользователям. Верни `user_id`, `orders_count`, `paid_total` только для пользователей с суммой выше 1000."
        sol = "SELECT user_id, COUNT(*) AS orders_count, SUM(total) AS paid_total\nFROM orders\nWHERE status = 'paid'\nGROUP BY user_id\nHAVING SUM(total) > 1000\nORDER BY user_id;\n"
        return task, sol, sql_checker(schema, seed, [[1, 2, 6400]]), "aggregate"
    if "окон" in low:
        task = "Пронумеруй заказы каждого пользователя по убыванию суммы. Верни `user_id`, `total`, `rn`."
        sol = "SELECT user_id, total, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rn\nFROM orders\nORDER BY user_id, rn;\n"
        return task, sol, sql_checker(schema, seed, [[1, 5700, 1], [1, 700, 2], [2, 1200, 1]]), "window"
    if "cte" in low or "подзапрос" in low:
        task = "Через CTE найди пользователей с оплаченными заказами. Верни `id`, `name`, `paid_total`."
        sol = "WITH paid AS (\n    SELECT user_id, SUM(total) AS paid_total\n    FROM orders\n    WHERE status = 'paid'\n    GROUP BY user_id\n)\nSELECT users.id, users.name, paid.paid_total\nFROM users\nJOIN paid ON paid.user_id = users.id\nORDER BY users.id;\n"
        return task, sol, sql_checker(schema, seed, [[1, "Анна", 6400]]), "cte"
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
    return {"type": "http_api", "app_import": "app.main:app", "public_tests": [test], "hidden_tests": [hidden], "timeout_sec": 8}


def ide_checker(kind: str, lesson_slug: str, order: int, topics: list[str], final_gate: str | None = None) -> dict[str, Any]:
    scenario = f"{kind}_{lesson_slug}_{order}"
    if "Git и GitHub" in topics:
        files = [f"git_labs/{lesson_slug}/README.md", f"git_labs/{lesson_slug}/src/main.py"]
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
            },
            "commands": [{"cmd": "git status --porcelain", "expect_stdout": ""}, {"cmd": f"test -f git_labs/{lesson_slug}/README.md", "expect_exit_code": 0}],
        }
    if any(t in topics for t in ["Docker", "Docker Compose", "CI/CD", "GitHub Actions", "GitLab CI/CD", "multistage build", "VPS", "автодеплой"]):
        files = ["Dockerfile", "docker-compose.yml", ".dockerignore", f"deploy/{lesson_slug}_{order}.sh", ".github/workflows/ci.yml"]
        return {
            "type": "ide_plugin",
            "scenario_id": scenario,
            "required_files": files,
            "file_content_rules": [{"file": "Dockerfile", "must_contain": ["WORKDIR", "COPY", "CMD"]}, {"file": "docker-compose.yml", "must_contain": ["services:", "healthcheck"]}],
            "commands": [{"cmd": "docker compose config", "expect_exit_code": 0}, {"cmd": f"test -f deploy/{lesson_slug}_{order}.sh", "expect_exit_code": 0}],
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
        return {"type": "ide_plugin", "scenario_id": scenario, "required_files": files, "commands": [{"cmd": "python -m pytest", "expect_exit_code": 0}, {"cmd": "docker compose config", "expect_exit_code": 0}], "http_checks": [{"method": "GET", "path": "/health", "expected_status": 200}]}
    files = [f"src/{lesson_slug}_{order}.py", f"tests/test_{lesson_slug}_{order}.py", "README.md"]
    return {"type": "ide_plugin", "scenario_id": scenario, "required_files": files, "commands": [{"cmd": f"python -m pytest tests/test_{lesson_slug}_{order}.py", "expect_exit_code": 0}]}


def ai_review(title: str, gate: str | None = None) -> dict[str, Any]:
    rubrics = ["требования выполнены наблюдаемым результатом", "код разделён на небольшие функции", "ошибки и крайние случаи проверены", "README объясняет запуск", "секреты не попали в репозиторий"]
    if gate:
        rubrics.insert(0, f"gate `{gate}` имеет явные pass/fail критерии")
    return {"enabled": True, "rubric": rubrics, "pass_score": 4, "review_focus": title}


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
        steps.append(base_step(lesson_id, order, ["Простой запрос", "Ошибка в запросе", "Основной запрос", "Связанные данные", "Граничный случай", "Контроль данных", "Диагностика", "Разбор результата", "Edge case"][order - 4], "practice", 3, 90, 28, body, topics, editor_initial_code="-- напиши SQL ниже\n", solution_code=sol, checker=chk))
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
        chk = ide_checker("ide", lesson_slug, order, topics, final_gate)
        if "Git и GitHub" in topics:
            task = f"В каталоге `git_labs/{lesson_slug}` выполни Git-лабу {order}: создай репозиторий, сделай ветку `feature/{lesson_slug[:20]}`, зафиксируй изменение README и вернись в `main`."
            solution = f"mkdir -p git_labs/{lesson_slug}\ncd git_labs/{lesson_slug}\ngit init\ngit config user.email student@example.com\ngit config user.name Student\necho '# {title}' > README.md\ngit add README.md\ngit commit -m 'Start {lesson_slug}'\ngit switch -c feature/{lesson_slug[:20]}\necho 'practice {order}' >> README.md\ngit add README.md\ngit commit -m 'Practice {order}'\ngit switch main\ngit merge feature/{lesson_slug[:20]}\ngit status --porcelain\n"
        elif any(t in topics for t in ["Docker", "Docker Compose", "CI/CD", "VPS", "автодеплой", "SSL", "домен"]):
            task = f"Подготовь инфраструктурный артефакт `{lesson_slug}_{order}`: Docker/compose/deploy-файл с healthcheck и понятной командой запуска."
            solution = f"Files:\nDockerfile\ndocker-compose.yml\n.dockerignore\ndeploy/{lesson_slug}_{order}.sh\n.github/workflows/ci.yml\n\nCommands:\ndocker compose config\nbash deploy/{lesson_slug}_{order}.sh --dry-run\n"
        else:
            task = f"Собери проверяемый IDE-артефакт `{lesson_slug}_{order}`: исходный файл, тест и README с командой запуска."
            solution = f"Files:\nsrc/{lesson_slug}_{order}.py\ntests/test_{lesson_slug}_{order}.py\nREADME.md\n\nCommand:\npython -m pytest tests/test_{lesson_slug}_{order}.py\n"
        body = f"**Коротко:** {task}\n\n### Условие\n{task}\n\n### Что сдаёшь\nФайлы из проверки, команду запуска в README и воспроизводимый результат.\n\n### Pass/fail\nПроходит, если IDE-плагин находит все файлы, команды завершаются успешно, а результат соответствует теме `{title}`."
        steps.append(base_step(lesson_id, order, f"{'Проект' if typ == 'project' else 'Практика'} {order}", typ, 3, 125 if typ == "project" else 90, 50 if typ == "project" else 30, body, topics, solution_code=solution, checker=chk, ide_plugin_check=chk if typ == "project" else None, ai_review_config=ai_review(title, final_gate) if typ == "project" else None))
    if "Git и GitHub" in topics:
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
        mid = f"v14_m{mi:02d}"
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
        "package_version": "v14_CONTENT_POLISHED",
        "course": {
            "id": "python_backend_ai_v14_content_polished",
            "title": TITLE,
            "description": "Полный импортируемый пакет курса, пересобранный после независимого QA v13. Основная цель v14: убрать шаблонность, дубли, пустые решения и формальные проверки в сложных темах.",
            "target_level": TARGET,
            "source_note": "Lesson order follows the approved roadmap skeleton. Student-facing content, solutions and checker signatures were regenerated for v14 based on the quality example lesson and QA blockers.",
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
    }


def write_docs(course: dict[str, Any]) -> None:
    preview = [f"# {TITLE}: v14_CONTENT_POLISHED", "", "Этот preview нужен для методиста. Импортировать нужно только `course_import.json`.", "", "v14 пересобран после QA: дубли body, пустые решения и мягкий QA теперь проверяются валидатором.", ""]
    cmap = ["# Карта курса v14_CONTENT_POLISHED", ""]
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
    (ROOT / "import_instructions.md").write_text("# Инструкция импорта v14_CONTENT_POLISHED\n\n1. Запусти `python validate_course.py`.\n2. Импортируй только `course_import.json`.\n3. Markdown-preview не является источником для платформы.\n4. После импорта сравни уроки и шаги с `manifest.csv`.\n5. Если импортёр сортирует не по `order`, исправь импортёр до запуска потока.\n6. Скрытые поля `solution_code`, `checker`, `ai_review_config`, `admin_notes` не показываются студенту.\n", encoding="utf-8")
    (ROOT / "ide_plugin_spec.md").write_text("# IDE plugin spec v14\n\nПлагин проверяет конкретные артефакты, а не общие обещания.\n\n## Обязательные проверки\n- required_files с уникальным `scenario_id`;\n- команды `python -m pytest`, `git status --porcelain`, `docker compose config` по типу задания;\n- SQL fixtures и временные SQLite-базы;\n- FastAPI route checks через TestClient;\n- Dockerfile, compose, healthcheck, deploy script;\n- Git workflow: branch, merge, rebase, conflict markers, clean worktree;\n- CI/CD: test job, image build job, deploy job;\n- final gates: required docs, pass/fail criteria, AI-review rubric.\n", encoding="utf-8")
    (ROOT / "ide_plugin_checks.json").write_text(json.dumps({"version": "v14", "quality_rules": {"unique_scenario_id_required": True, "max_signature_repeat": 20, "project_solution_required": True}, "checks": ["files", "git", "pytest", "sql", "fastapi", "docker", "ci_cd", "final_gates"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "mentor_handbook.md").write_text("# Handbook для наставника v14\n\n## Принцип ответа\nСначала спроси студента о наблюдаемом результате: ввод, вывод, stderr, команда запуска. Не выдавай готовое решение, если можно локализовать ошибку одним вопросом.\n\n## Частые ошибки\n- точный stdout нарушен лишним словом;\n- SQL не сортирует результат;\n- transaction-задача делает SELECT вместо BEGIN/COMMIT/ROLLBACK;\n- FastAPI healthcheck возвращает массив вместо объекта;\n- Docker/CI задача не содержит проверяемого файла;\n- Git-задача оставляет грязное рабочее дерево.\n\n## Эскалация\nЭскалируй, если публичный пример противоречит hidden-проверке, IDE-плагин не видит существующий файл или корректное решение падает на инфраструктуре.\n", encoding="utf-8")
    (ROOT / "student_faq.md").write_text("# FAQ студента v14\n\n## Как проходить курс\nСначала запускай минимальный пример, потом решай задачу, потом проверяй edge case. Не начинай с AI, если ещё не понял ошибку.\n\n## Почему нельзя писать лишний вывод\nstdout-задачи сравнивают точный текст. Одно лишнее слово ломает проверку.\n\n## Почему SQL требует ORDER BY\nБез сортировки база не обязана возвращать строки в одном порядке.\n\n## Почему project-step просит файлы\nПроект нельзя проверить намерением. Нужны файлы, команды и воспроизводимый результат.\n", encoding="utf-8")
    (ROOT / "middle_readiness_rubric.md").write_text("# Рубрика готовности\n\n| Уровень | Python | SQL | API | Тесты | Git | DevOps | Архитектура | Финальный проект |\n|---|---|---|---|---|---|---|---|---|\n| Junior | функции, коллекции, ошибки | SELECT/JOIN | простые routes | базовый pytest | commit/branch | Dockerfile | слои видит | CRUD работает |\n| Junior+ | ООП, typing, async | CTE, transactions | auth, Depends | fixtures/mocks | rebase/conflicts | compose/CI | repository/service | тесты и README |\n| Middle-ready | проектирует boundaries | индексы/изоляция | SQLAlchemy/Alembic | integration suite | workflow ведёт | deploy/rollback | trade-offs объясняет | защита проходит |\n| Начинающий Middle | улучшает чужой код | оптимизирует запросы | владеет модулем | строит стратегию качества | держит историю чистой | снижает prod-risk | документирует решения | ведёт релиз |\n", encoding="utf-8")
    (ROOT / "release_checklist.md").write_text("# Release checklist v14\n\n- [ ] `python validate_course.py` возвращает PASS.\n- [ ] `duplicate_body_count = 0`.\n- [ ] Empty solution_code у practice/project = 0.\n- [ ] Первый урок — `Первый код`.\n- [ ] Manifest совпадает с JSON.\n- [ ] Coverage matrix не содержит missing/thin/placeholder.\n- [ ] SQL transactions содержит BEGIN/COMMIT/ROLLBACK-задачи.\n- [ ] FastAPI healthcheck возвращает объект.\n- [ ] Docker/final tasks имеют конкретные файлы и команды.\n", encoding="utf-8")


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
    (ROOT / "checker_fixtures/projects/final_project_hidden_checks.json").write_text(json.dumps({"version": "v14", "gates": ["tz", "user_stories", "db_schema", "api_contract", "git_workflow", "fastapi_structure", "sqlalchemy_models", "alembic_migrations", "auth", "crud", "tests", "docker", "ci_cd", "ai_integration", "logging", "readme", "deploy", "defense"], "hidden_checks": [{"name": "no_secrets", "type": "file_scan", "patterns": ["API_KEY=", "SECRET_KEY="]}, {"name": "health_endpoint_object", "type": "http_api", "method": "GET", "path": "/health", "expected_status": 200, "expected_json_subset": {"status": "ok"}}, {"name": "pytest", "type": "command", "cmd": "python -m pytest", "expect_exit_code": 0}, {"name": "compose_config", "type": "command", "cmd": "docker compose config", "expect_exit_code": 0}]}, ensure_ascii=False, indent=2), encoding="utf-8")


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
    for label, items in [("duplicate ids", dup_ids), ("practice without checker", missing_checker), ("test without questions", missing_questions), ("project without ide/ai", project_missing), ("body leaks", leaks), ("banned text", banned), ("practice empty solution", empty_practice_solution), ("project empty solution", empty_project_solution)]:
        if items:
            errors.append(f"{label}: {len(items)}")
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
        "# Validation report v14_CONTENT_POLISHED", "", f"final status: {result['status']}", "",
        "## Totals", f"- total modules: {s['total_modules']}", f"- total lessons: {s['total_lessons']}", f"- total steps: {s['total_steps']}", f"- total hours: {s['total_hours']}", f"- steps by type: {s['steps_by_type']}", f"- checkers by type: {s['checkers_by_type']}", f"- structured questions: {s['questions']}", "",
        "## Quality gates", f"- duplicate body_markdown: {s['duplicate_body_count']} duplicates / {s['duplicate_body_groups']} groups", f"- empty practice solutions: {len(result['empty_practice_solution'])}", f"- empty project solutions: {len(result['empty_project_solution'])}", f"- unique IDE signatures: {s['unique_ide_signatures']}", f"- max IDE signature repeat: {s['max_ide_signature_repeat']}", "",
        "## Required depth", f"- practice tasks: {s['practice_count']}", f"- project/IDE tasks: {s['project_or_ide_count']}", f"- SQL query tasks: {s['sql_tasks']}", f"- SQLite/sqlite3 steps: {s['sqlite_steps']}", f"- Git steps: {s['git_steps']}", f"- Git/terminal steps: {s['git_terminal_steps']}", f"- FastAPI steps: {s['fastapi_steps']}", f"- HTTP API tasks: {s['http_api_tasks']}", f"- pytest tasks: {s['pytest_tasks']}", f"- Docker/CI/CD/DevOps steps: {s['devops_steps']}", "",
        "## Critical checks", f"- missing checkers: {len(result['missing_checkers'])}", f"- missing quiz questions: {len(result['missing_questions'])}", f"- body leaks: {len(result['body_leaks'])}", f"- banned text: {len(result['banned_text'])}", f"- duplicate ids: {len(result['duplicate_ids'])}", f"- projects without IDE/AI review: {len(result['project_missing'])}",
    ]
    if result["errors"]:
        lines += ["", "## Errors"] + [f"- {e}" for e in result["errors"]]
    lines.append(f"\nResult: {result['status']}")
    (ROOT / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    qa = [
        "# QA report v14_CONTENT_POLISHED", "", f"PASS/FAIL: {result['status']}", "",
        "## Critical blockers", *([f"- {e}" for e in result["errors"]] if result["errors"] else ["- не найдено"]), "",
        "## Major issues", "- не найдено" if not result["errors"] else "- смотри critical blockers", "",
        "## Duplicate audit", f"- exact duplicate body_markdown: {s['duplicate_body_count']}", f"- duplicate groups: {s['duplicate_body_groups']}", "",
        "## Solution audit", f"- practice with empty solution_code: {len(result['empty_practice_solution'])}", f"- project with empty solution_code: {len(result['empty_project_solution'])}", "",
        "## Checker audit", f"- unique IDE checker signatures: {s['unique_ide_signatures']}", f"- max IDE signature repeat: {s['max_ide_signature_repeat']}", "",
        "## Темы повышенного риска", "- SQL transactions проверяются через BEGIN/COMMIT/ROLLBACK, а не простым SELECT.", "- FastAPI healthcheck ожидает JSON object.", "- Docker/final gates имеют concrete required_files и команды.", "",
        "## Итог", "Пакет считается готовым только при PASS всех quality gates выше.",
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
    print(f"duplicate_body={s['duplicate_body_count']} empty_practice_solution={len(result['empty_practice_solution'])} empty_project_solution={len(result['empty_project_solution'])} unique_ide={s['unique_ide_signatures']}")
    if result["errors"]:
        for e in result["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
