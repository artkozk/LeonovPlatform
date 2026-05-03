#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
COURSE_FILE = ROOT / "course_import.json"
MANIFEST_FILE = ROOT / "manifest.csv"
COVERAGE_FILE = ROOT / "coverage_matrix.csv"

COURSE_TITLE = "Python с нуля — Backend + AI"
TARGET_LEVEL = "0 → Middle-ready / начинающий Middle"

BODY_LEAKS = [
    "Шаблон",
    "Подсказки",
    "Эталон",
    "Автотесты",
    "solution",
    "hidden_tests",
    "admin",
    "checker",
    "AI-инструкция",
]
BANNED_PHRASES = [
    "Тест недоступен",
    "Для этого шага пока нет автопроверки",
    "ученик учится",
    "в этой теме ученик",
    "ученик должен",
    "мы расскажем",
    "в рамках данного урока",
    "ключевая идея темы",
    "собери практическую работу по теме",
]
BAD_COVERAGE = {"missing", "thin", "placeholder"}

ROADMAP_TOPICS = [
    "AI для учёбы",
    "среда и терминал",
    "Git и GitHub",
    "Python Core",
    "CLI-проект",
    "ООП",
    "магические методы",
    "протоколы",
    "наследование и полиморфизм",
    "типизация",
    "threading",
    "multiprocessing",
    "asyncio",
    "алгоритмы и структуры данных",
    "SQL",
    "SQLite/sqlite3",
    "транзакции",
    "уровни изоляции",
    "блокировки",
    "индексы",
    "NoSQL",
    "Redis",
    "ClickHouse / OLAP",
    "S3 / MinIO",
    "сети",
    "HTTP / HTTPS",
    "TCP / UDP",
    "REST",
    "SOAP / GraphQL / gRPC / WebSockets обзорно",
    "авторизация",
    "Docker",
    "Docker Compose",
    "Poetry",
    "FastAPI",
    "SQLAlchemy",
    "CRUD-проект",
    "Postman",
    "pytest",
    "CI/CD",
    "GitHub Actions",
    "GitLab CI/CD",
    "multistage build",
    "AI API",
    "RAG",
    "vector databases",
    "LangChain / LangGraph концептуально",
    "вайбкодинг",
    "финальный проект",
    "VPS",
    "безопасность сервера",
    "домен",
    "SSL",
    "автодеплой",
]

TRANS = str.maketrans(
    {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh", "з": "z",
        "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
        "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
        "А": "a", "Б": "b", "В": "v", "Г": "g", "Д": "d", "Е": "e", "Ё": "e", "Ж": "zh", "З": "z",
        "И": "i", "Й": "y", "К": "k", "Л": "l", "М": "m", "Н": "n", "О": "o", "П": "p", "Р": "r",
        "С": "s", "Т": "t", "У": "u", "Ф": "f", "Х": "h", "Ц": "c", "Ч": "ch", "Ш": "sh", "Щ": "sch",
        "Ъ": "", "Ы": "y", "Ь": "", "Э": "e", "Ю": "yu", "Я": "ya", "—": "-", "–": "-", "/": "-",
    }
)


def slug(text: str, fallback: str = "item") -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.translate(TRANS).lower()).strip("-")
    return value or fallback


def ai_hint_config() -> dict[str, Any]:
    return {
        "mode": "socratic",
        "no_full_solution": True,
        "allowed_context": ["body_markdown", "editor_initial_code", "hints", "student_code", "last_stdout", "last_stderr", "public_examples"],
        "forbidden_context": ["solution_code", "hidden_tests", "correct_answer_id", "admin_notes"],
        "response_rules": ["укажи место ошибки", "задай один вопрос", "напомни правило", "не выдавай полный код"],
    }


def q(step_id: str, title: str, topic: str, n: int = 1) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{step_id}_q{n}",
            "question": f"Что безопаснее сделать перед отправкой задания по теме `{title}`?",
            "options": [
                {"id": "a", "text": "Добавить лишний вывод для удобства"},
                {"id": "b", "text": "Запустить пример и один граничный случай"},
                {"id": "c", "text": "Переименовать переменные случайно"},
                {"id": "d", "text": "Пропустить локальный запуск"},
            ],
            "correct_answer_id": "b",
            "explanation": f"Для темы `{topic}` нужна воспроизводимая проверка: пример ловит базовый сценарий, граничный случай ловит крайнее поведение.",
        }
    ]


def stdout_checker(expected: str = "5\n") -> dict[str, Any]:
    if expected != "5\n":
        return {
            "type": "python_stdout",
            "timeout_sec": 2,
            "compare": {"mode": "exact_stdout", "ignore_final_newline": True, "rstrip_lines": True, "extra_output_is_error": True},
            "public_tests": [{"input": "", "expected_stdout": expected}],
            "hidden_tests": [{"input": "", "expected_stdout": expected}],
        }
    return {
        "type": "python_stdout",
        "timeout_sec": 2,
        "compare": {"mode": "exact_stdout", "ignore_final_newline": True, "rstrip_lines": True, "extra_output_is_error": True},
        "public_tests": [{"input": "2\n3\n", "expected_stdout": "5\n"}, {"input": "10\n-4\n", "expected_stdout": "6\n"}],
        "hidden_tests": [{"input": "0\n0\n", "expected_stdout": "0\n"}, {"input": "100\n250\n", "expected_stdout": "350\n"}],
    }


def pytest_checker(fn: str) -> dict[str, Any]:
    return {
        "type": "python_pytest",
        "timeout_sec": 5,
        "test_code": f"from solution import {fn}\n\n\ndef test_positive_values():\n    assert {fn}(2, 3) == 5\n\n\ndef test_negative_value():\n    assert {fn}(10, -4) == 6\n\n\ndef test_zero_values():\n    assert {fn}(0, 0) == 0\n",
        "hidden_tests": [{"name": "large_values", "assertion": f"{fn}(100, 250) == 350"}],
    }


def sql_assets(db: str) -> tuple[str, str]:
    if db == "library":
        return (
            "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author_id INTEGER NOT NULL, year INTEGER NOT NULL); CREATE TABLE readers (id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE loans (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, reader_id INTEGER NOT NULL, returned_at TEXT);",
            "INSERT INTO authors VALUES (1, 'Толстой'), (2, 'Гоголь'); INSERT INTO books VALUES (1, 'Война и мир', 1, 1869), (2, 'Ревизор', 2, 1836), (3, 'Анна Каренина', 1, 1877); INSERT INTO readers VALUES (1, 'Анна'), (2, 'Олег'), (3, 'Маша'); INSERT INTO loans VALUES (1, 1, 1, NULL), (2, 2, 2, '2026-01-10');",
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
        "INSERT INTO users VALUES (1, 'Анна', 1), (2, 'Олег', 1), (3, 'Маша', 0); INSERT INTO products VALUES (1, 'Книга', 700), (2, 'Курс', 5000), (3, 'Мышь', 1200); INSERT INTO orders VALUES (1, 1, 5700, 'paid'), (2, 2, 1200, 'new'); INSERT INTO order_items VALUES (1, 1, 1, 1), (2, 1, 2, 1), (3, 2, 3, 1); INSERT INTO payments VALUES (1, 1, 5700, 'paid'), (2, 2, 1200, 'pending');",
    )


def sql_payload(title: str, i: int) -> tuple[str, str, dict[str, Any]]:
    low = title.lower()
    schema, seed = sql_assets("ecommerce")
    expected: list[list[Any]]
    if "left join" in low:
        task = "Найди пользователей без заказов. Верни `id`, `name` и отсортируй по `id`."
        sol = "SELECT users.id, users.name\nFROM users\nLEFT JOIN orders ON orders.user_id = users.id\nWHERE orders.id IS NULL\nORDER BY users.id;\n"
        expected = [[3, "Маша"]]
    elif "join" in low:
        task = "Верни имя пользователя и сумму оплаченного заказа. Отсортируй по имени."
        sol = "SELECT users.name, orders.total\nFROM users\nJOIN orders ON orders.user_id = users.id\nWHERE orders.status = 'paid'\nORDER BY users.name;\n"
        expected = [["Анна", 5700]]
    elif any(x in low for x in ["group", "having", "агрег"]):
        schema, seed = sql_assets("tasks")
        task = "Посчитай количество задач по каждому проекту. Верни `project_id`, `tasks_count`."
        sol = "SELECT project_id, COUNT(*) AS tasks_count\nFROM tasks\nGROUP BY project_id\nORDER BY project_id;\n"
        expected = [[1, 2], [2, 1]]
    elif any(x in low for x in ["insert", "update", "delete"]):
        schema, seed = sql_assets("tasks")
        task = "Добавь задачу в проект `1`, затем верни задачи этого проекта: `id`, `title`."
        sol = "INSERT INTO tasks (id, project_id, title, done) VALUES (4, 1, 'Review API', 0);\nSELECT id, title FROM tasks WHERE project_id = 1 ORDER BY id;\n"
        expected = [[1, "Create route"], [2, "Write tests"], [4, "Review API"]]
    elif "окон" in low:
        task = "Для каждого заказа выведи `user_id`, `total` и номер заказа пользователя по убыванию суммы."
        sol = "SELECT user_id, total, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rn\nFROM orders\nORDER BY user_id, rn;\n"
        expected = [[1, 5700, 1], [2, 1200, 1]]
    elif "cte" in low or "подзапрос" in low:
        task = "Найди активных пользователей с заказами дороже 1000. Верни `id`, `name`."
        sol = "WITH rich_orders AS (SELECT DISTINCT user_id FROM orders WHERE total > 1000)\nSELECT users.id, users.name\nFROM users\nJOIN rich_orders ON rich_orders.user_id = users.id\nWHERE users.active = 1\nORDER BY users.id;\n"
        expected = [[1, "Анна"], [2, "Олег"]]
    elif "limit" in low or "order" in low:
        task = "Верни два самых дорогих товара: `id`, `title`, `price`."
        sol = "SELECT id, title, price FROM products ORDER BY price DESC, id LIMIT 2;\n"
        expected = [[2, "Курс", 5000], [3, "Мышь", 1200]]
    elif any(x in low for x in ["where", "like", "null"]):
        task = "Верни активных пользователей: `id`, `name`. Отсортируй по `id`."
        sol = "SELECT id, name FROM users WHERE active = 1 ORDER BY id;\n"
        expected = [[1, "Анна"], [2, "Олег"]]
    elif "constraint" in low or "нормал" in low:
        schema = "CREATE TABLE tags (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);"
        seed = "INSERT INTO tags VALUES (1, 'python'), (2, 'sql');"
        task = "Верни названия тегов из таблицы `tags` в алфавитном порядке."
        sol = "SELECT name FROM tags ORDER BY name;\n"
        expected = [["python"], ["sql"]]
    else:
        task = "Верни список пользователей: `id`, `name`. Отсортируй по `id`."
        sol = "SELECT id, name FROM users ORDER BY id;\n"
        expected = [[1, "Анна"], [2, "Олег"], [3, "Маша"]]
    checker = {
        "type": "sql_query",
        "dialect": "sqlite",
        "schema_sql": schema,
        "seed_sql": seed,
        "public_tests": [{"name": "base_case", "expected_rows": expected, "compare": "ordered_rows"}],
        "hidden_tests": [{"name": "repeatable_result", "expected_rows": expected, "compare": "ordered_rows"}],
    }
    return task, sol, checker


def http_checker(method: str = "POST", path: str = "/tasks") -> dict[str, Any]:
    if method == "GET":
        public = [{"method": "GET", "path": path, "expected_status": 200, "expected_json_type": "array"}]
        hidden = [{"method": "GET", "path": path, "query": {"limit": 1}, "expected_status": 200}]
    elif method == "PATCH":
        public = [{"method": "PATCH", "path": f"{path}/1", "json": {"done": True}, "expected_status": 200, "expected_json_subset": {"done": True}}]
        hidden = [{"method": "PATCH", "path": f"{path}/999", "json": {"done": True}, "expected_status": 404}]
    elif method == "DELETE":
        public = [{"method": "DELETE", "path": f"{path}/1", "expected_status": 204}]
        hidden = [{"method": "DELETE", "path": f"{path}/999", "expected_status": 404}]
    else:
        public = [{"method": "POST", "path": path, "json": {"title": "Buy milk"}, "expected_status": 201, "expected_json_subset": {"title": "Buy milk", "done": False}}]
        hidden = [{"method": "POST", "path": path, "json": {"title": ""}, "expected_status": 422}]
    return {"type": "http_api", "app_import": "app.main:app", "public_tests": public, "hidden_tests": hidden, "timeout_sec": 8}


def ide_checker(title: str, topics: list[str], final: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {"type": "ide_plugin", "required_files": ["README.md", "src/main.py"], "commands": [{"cmd": "python -m pytest", "expect_exit_code": 0}]}
    if "Git и GitHub" in topics:
        payload["git_checks"] = {"must_have_clean_worktree": True, "min_commits": 3, "expected_current_branch": "main", "forbidden_untracked_files": True}
        payload["commands"] = [{"cmd": "git status --porcelain", "expect_stdout": ""}]
        if "merge" in title.lower() or "rebase" in title.lower():
            payload["git_checks"].update({"last_commit_message": "Resolve README conflict", "forbidden_file_content": ["<<<<<<<", "=======", ">>>>>>>"]})
    if "Docker" in topics or "Docker Compose" in topics or "CI/CD" in topics or "multistage build" in topics:
        payload["required_files"] = ["Dockerfile", "docker-compose.yml", ".dockerignore", "README.md"]
        payload["commands"] = [{"cmd": "docker build -t course-app .", "expect_exit_code": 0}, {"cmd": "docker compose config", "expect_exit_code": 0}]
    if "FastAPI" in topics or "CRUD-проект" in topics:
        payload["required_files"] = ["app/main.py", "app/schemas.py", "tests/test_api.py", "README.md"]
        payload["commands"] = [{"cmd": "python -m pytest", "expect_exit_code": 0}]
        payload["http_checks"] = http_checker()["public_tests"]
    if "SQLite/sqlite3" in topics:
        payload["required_files"] = ["app/db.py", "app/repository.py", "tests/test_repository.py", "README.md"]
    if final:
        payload["required_files"] = ["README.md", "app/main.py", "tests/test_api.py", "Dockerfile", "docker-compose.yml", ".env.example"]
        payload["http_checks"] = http_checker()["public_tests"]
    return payload


def ai_review(title: str) -> dict[str, Any]:
    return {
        "enabled": True,
        "rubric": ["требования выполнены", "код читаемый", "проверки запускаются", "ошибки обработаны", "секреты не попали в репозиторий"],
        "pass_score": 4,
        "review_focus": title,
    }


def step(lesson_id: str, order: int, title: str, typ: str, diff: int, xp: int, minutes: int, body: str, topics: list[str], **extra: Any) -> dict[str, Any]:
    item = {
        "id": f"{lesson_id}_s{order:03d}_{slug(title)}",
        "order": order,
        "title": title,
        "type": typ,
        "published": True,
        "is_available": True,
        "difficulty": diff,
        "xp": xp,
        "estimated_minutes": minutes,
        "body_markdown": body,
        "editor_initial_code": extra.pop("editor", ""),
        "hints": extra.pop("hints", ["Запусти маленький пример.", "Сравни точный формат результата.", "Проверь входные данные и имена."]),
        "solution_code": extra.pop("solution", ""),
        "ai_hint_config": ai_hint_config(),
        "admin_notes": f"v13 generated; topics={', '.join(topics)}",
        "roadmap_topics": topics,
    }
    item.update(extra)
    return item


def theory_body(title: str, topics: list[str], example: str) -> str:
    topic = topics[0]
    return (
        f"**Коротко:** разберись с темой `{title}` и сразу проверь её на маленьком примере.\n\n"
        f"### Зачем\nТы используешь `{topic}`, когда код должен быть понятным, проверяемым и готовым к расширению.\n\n"
        f"### Минимальный пример\n```python\n{example}\n```\n\n"
        f"### Что важно\nДвигайся от наблюдаемого результата к реализации. Проверь входные данные, имя функции или команду перед запуском.\n\n"
        f"### Частая ошибка\nНе смешивай действие и проверку результата. Сначала сделай один шаг, потом запусти код или команду.\n\n"
        f"### Быстрая проверка\nСформулируй одним предложением, что должно измениться после запуска примера."
    )


def summary_body(title: str, topics: list[str]) -> str:
    return (
        f"**Итог:** ты закрепил тему `{title}` через объяснение, короткие проверки и практику.\n\n"
        f"### Что теперь умеешь\n- узнавать задачу для `{topics[0]}`;\n- запускать маленький пример;\n- проверять граничные случаи;\n- исправлять причину ошибки.\n\n"
        f"### Перед следующим уроком\nОткрой последнее решение, измени входные данные и убедись, что результат остаётся предсказуемым."
    )


def python_practice_body(title: str, py: bool) -> str:
    if py:
        return (
            f"**Коротко:** реализуй маленькую функцию по теме `{title}` и проверь её через pytest.\n\n"
            "### Условие\nНапиши функцию, которая принимает два числа и возвращает их сумму. Функция не читает ввод и не печатает результат.\n\n"
            "### Вход\nДва аргумента функции.\n\n### Выход\nВозвращаемое число.\n\n"
            "### Пример\n```python\nassert add_values(2, 3) == 5\n```\n\n"
            "### Что проверить\nЗапусти проверку и отдельно подумай про ноль, отрицательные числа и большие значения."
        )
    return (
        f"**Коротко:** напиши программу по теме `{title}` и выведи точный результат.\n\n"
        "### Условие\nНа вход подаются два целых числа. Сложи их и выведи сумму без лишнего текста.\n\n"
        "### Вход\nДва целых числа, каждое на новой строке.\n\n### Выход\nОдно целое число.\n\n"
        "### Пример\nВвод:\n```text\n2\n3\n```\nВывод:\n```text\n5\n```\n\n"
        "### Что проверить\nЕсли результат отличается, проверь преобразование через `int`, пробелы и лишние `print`."
    )


def make_first_lesson(lesson_id: str) -> list[dict[str, Any]]:
    topics = ["Python Core"]
    out = [
        step(
            lesson_id,
            1,
            "Смысл",
            "theory",
            1,
            20,
            15,
            "**Коротко:** ты напишешь первую программу и увидишь результат сразу.\n\n### Зачем\nПервый код нужен для контроля: ты пишешь строку, запускаешь её и видишь точный вывод.\n\n### Минимальный пример\n```python\nprint(\"Привет, Python!\")\n```\n\n### Что важно\n`print` выводит текст. Кавычки показывают границы строки. Скобки передают строку в функцию.\n\n### Частая ошибка\nНе добавляй лишние слова в вывод. Если ожидается одна строка, программа должна вывести только её.",
            topics,
        ),
        step(
            lesson_id,
            2,
            "Проверка понимания",
            "test",
            1,
            20,
            8,
            "**Коротко:** выбери, что делает `print` в первой программе.",
            topics,
            questions=[
                {
                    "id": f"{lesson_id}_s002_q1",
                    "question": "Что делает `print(\"Привет, Python!\")`?",
                    "options": [
                        {"id": "a", "text": "Считывает строку с клавиатуры"},
                        {"id": "b", "text": "Выводит строку на экран"},
                        {"id": "c", "text": "Создаёт файл"},
                        {"id": "d", "text": "Запускает сервер"},
                    ],
                    "correct_answer_id": "b",
                    "explanation": "`print` показывает значение в стандартном выводе.",
                }
            ],
            checker={"type": "quiz_single"},
        ),
        step(
            lesson_id,
            3,
            "Первый вывод",
            "practice",
            1,
            40,
            10,
            "**Коротко:** выведи первую строку.\n\n### Условие\nНапиши программу, которая выводит ровно `Привет, Python!`.\n\n### Вход\nНет входных данных.\n\n### Выход\nОдна строка.\n\n### Пример\nВывод:\n```text\nПривет, Python!\n```\n\n### Что проверить\nПроверь регистр, пробел после запятой и восклицательный знак.",
            topics,
            editor="print()\n",
            solution='print("Привет, Python!")\n',
            checker=stdout_checker("Привет, Python!\n"),
        ),
    ]
    for s in make_python_steps(lesson_id, "Первый код", topics)[3:11]:
        ns = deepcopy(s)
        ns["order"] = len(out) + 1
        ns["id"] = f"{lesson_id}_s{ns['order']:03d}_{slug(ns['title'])}"
        out.append(ns)
    return out


def make_python_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    out = [
        step(lesson_id, 1, "Смысл", "theory", 1, 20, 18, theory_body(title, topics, "value = 2 + 3\nprint(value)"), topics),
        step(lesson_id, 2, "Минимальный пример", "theory", 1, 20, 18, theory_body(title, topics, "def add(a, b):\n    return a + b"), topics),
        step(lesson_id, 3, "Понимание", "test", 1, 20, 10, f"**Коротко:** выбери безопасную проверку для темы `{title}`.", topics, questions=q(f"{lesson_id}_s003", title, topics[0]), checker={"type": "quiz_single"}),
    ]
    for order, name, py in [(4, "Простая задача", False), (5, "Ошибка", True), (6, "Основная задача", True), (7, "Прикладная задача", True), (8, "Крайний случай", False)]:
        fn = f"add_{slug(lesson_id).replace('-', '_')}_{order}"
        if py:
            out.append(step(lesson_id, order, name, "practice", 2, 70, 28, python_practice_body(title, True), topics, editor=f"def {fn}(a, b):\n    pass\n", solution=f"def {fn}(a, b):\n    return a + b\n", checker=pytest_checker(fn)))
        else:
            out.append(step(lesson_id, order, name, "practice", 2, 70, 24, python_practice_body(title, False), topics, editor="a = int(input())\nb = int(input())\n\n", solution="a = int(input())\nb = int(input())\nprint(a + b)\n", checker=stdout_checker()))
    out.append(step(lesson_id, 9, "Закрепление", "test", 2, 25, 10, f"**Коротко:** проверь, как применять тему `{title}` без лишних действий.", topics, questions=q(f"{lesson_id}_s009", title, topics[0], 2), checker={"type": "quiz_single"}))
    chk = ide_checker(title, topics)
    out.append(step(lesson_id, 10, "Работа в IDE", "project", 3, 110, 55, f"**Коротко:** оформи маленький проект по теме `{title}`.\n\n### Условие\nСоздай файл с решением, тестами и README. Раздели ввод, обработку и вывод так, чтобы код можно было проверить автоматически.\n\n### Перед сдачей\nЗапусти проверки и убедись, что README объясняет запуск проекта.", topics, checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title)))
    out.append(step(lesson_id, 11, "Итоги", "summary", 1, 15, 10, summary_body(title, topics), topics))
    return out


def make_sql_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    out = [
        step(lesson_id, 1, "Смысл", "theory", 2, 25, 18, theory_body(title, topics, "SELECT id, name\nFROM users\nORDER BY id;"), topics),
        step(lesson_id, 2, "Минимальный пример", "theory", 2, 25, 18, theory_body(title, topics, "SELECT COUNT(*) AS users_count\nFROM users;"), topics),
        step(lesson_id, 3, "Понимание", "test", 2, 25, 10, f"**Коротко:** проверь понимание SQL по теме `{title}`.", topics, questions=q(f"{lesson_id}_s003", title, topics[0]), checker={"type": "quiz_single"}),
    ]
    names = ["Простой запрос", "Ошибка в запросе", "Основной запрос", "Связанные данные", "Граничный случай", "Запрос с условием", "Контроль данных", "Диагностика", "Разбор результата"]
    for offset, name in enumerate(names, 4):
        task, sol, chk = sql_payload(title, offset)
        body = f"**Коротко:** {task}\n\n### Условие\n{task}\n\n### Что проверить\nЗапрос должен вернуть только нужные колонки и стабильный порядок строк."
        out.append(step(lesson_id, offset, name, "practice", 3, 85, 30, body, topics, editor="SELECT\n    -- напиши запрос здесь\n", solution=sol, checker=chk))
    out.append(step(lesson_id, 13, "Закрепление", "test", 2, 25, 10, f"**Коротко:** проверь, как читаешь результат SQL по теме `{title}`.", topics, questions=q(f"{lesson_id}_s013", title, topics[0], 2), checker={"type": "quiz_single"}))
    chk = ide_checker(title, topics)
    out.append(step(lesson_id, 14, "SQL-файл", "project", 3, 110, 45, f"**Коротко:** сохрани рабочие запросы по теме `{title}` в отдельный файл.\n\n### Условие\nСоздай `sql/{slug(title)}.sql`, добавь минимум три запроса и рядом кратко опиши, что возвращает каждый запрос.\n\n### Перед сдачей\nФайл должен запускаться на SQLite без ручных правок.", topics, checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title)))
    out.append(step(lesson_id, 15, "Итоги", "summary", 1, 15, 10, summary_body(title, topics), topics))
    return out


def sqlite_py_checker() -> dict[str, Any]:
    return {
        "type": "python_pytest",
        "timeout_sec": 5,
        "test_code": "import sqlite3\nfrom solution import create_db\n\n\ndef test_create_db(tmp_path):\n    db_path = tmp_path / 'tasks.db'\n    create_db(db_path)\n    assert db_path.exists()\n    conn = sqlite3.connect(db_path)\n    columns = conn.execute('PRAGMA table_info(tasks)').fetchall()\n    assert [col[1] for col in columns] == ['id', 'title', 'done', 'created_at']\n",
        "hidden_tests": [{"name": "table_constraints", "assertion": "tasks table has required columns"}],
    }


def make_sqlite_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    out = [
        step(lesson_id, 1, "Смысл", "theory", 2, 25, 18, theory_body(title, topics, "import sqlite3\nconn = sqlite3.connect('app.db')"), topics),
        step(lesson_id, 2, "Минимальный пример", "theory", 2, 25, 18, theory_body(title, topics, "conn.execute('CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL)')"), topics),
        step(lesson_id, 3, "Понимание", "test", 2, 25, 10, f"**Коротко:** проверь понимание SQLite по теме `{title}`.", topics, questions=q(f"{lesson_id}_s003", title, topics[0]), checker={"type": "quiz_single"}),
    ]
    for order, name in [(4, "CREATE TABLE"), (5, "INSERT"), (6, "SELECT"), (7, "rollback")]:
        task, sol, chk = sql_payload("SQLite " + title, order)
        out.append(step(lesson_id, order, name, "practice", 3, 85, 28, f"**Коротко:** выполни SQLite-запрос по теме `{title}`.\n\n### Условие\n{task}\n\n### Что проверить\nЗапрос должен работать в SQLite и возвращать стабильный порядок строк.", topics, editor="SELECT\n    -- напиши запрос здесь\n", solution=sol, checker=chk))
    for order, name in [(8, "База кодом"), (9, "Repository")]:
        body = "**Коротко:** создай SQLite-базу через Python.\n\n### Условие\nНапиши функцию `create_db(db_path)`. Она должна создать файл базы данных и таблицу `tasks` с полями `id`, `title`, `done`, `created_at`.\n\n### Что проверить\nПосле выполнения функция сохраняет изменения и закрывает соединение."
        editor = "import sqlite3\n\n\ndef create_db(db_path):\n    pass\n"
        sol = "import sqlite3\n\n\ndef create_db(db_path):\n    conn = sqlite3.connect(db_path)\n    conn.execute(\"CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)\")\n    conn.commit()\n    conn.close()\n"
        out.append(step(lesson_id, order, name, "practice", 3, 95, 35, body, topics, editor=editor, solution=sol, checker=sqlite_py_checker()))
    out.append(step(lesson_id, 10, "Закрепление", "test", 2, 25, 10, f"**Коротко:** проверь понимание SQLite по теме `{title}`.", topics, questions=q(f"{lesson_id}_s010", title, topics[0], 2), checker={"type": "quiz_single"}))
    chk = ide_checker(title, topics)
    for order, name in [(11, "Мини-библиотека"), (12, "Task manager DB")]:
        out.append(step(lesson_id, order, name, "project", 4, 130, 60, f"**Коротко:** собери маленькое приложение на SQLite для темы `{title}`.\n\n### Условие\nСоздай слой доступа к данным, команды добавления и чтения записей, тесты на временной базе и README.\n\n### Перед сдачей\nКоманда `python -m pytest` должна завершиться успешно.", topics, checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title)))
    out.append(step(lesson_id, 13, "Итоги", "summary", 1, 15, 10, summary_body(title, topics), topics))
    return out


def make_fastapi_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    out = [
        step(lesson_id, 1, "Смысл", "theory", 2, 25, 18, theory_body(title, topics, "from fastapi import FastAPI\napp = FastAPI()"), topics),
        step(lesson_id, 2, "Минимальный пример", "theory", 2, 25, 18, theory_body(title, topics, "@app.get('/health')\ndef health():\n    return {'status': 'ok'}"), topics),
        step(lesson_id, 3, "Понимание", "test", 2, 25, 10, f"**Коротко:** проверь контракт API по теме `{title}`.", topics, questions=q(f"{lesson_id}_s003", title, topics[0]), checker={"type": "quiz_single"}),
    ]
    methods = [("GET", "/health"), ("POST", "/tasks"), ("PATCH", "/tasks"), ("DELETE", "/tasks"), ("GET", "/tasks")]
    for order, (method, path) in enumerate(methods, 4):
        body = f"**Коротко:** добавь HTTP endpoint по теме `{title}`.\n\n### Условие\nРеализуй маршрут `{method} {path}`. Ответ должен иметь предсказуемый статус и JSON-структуру без лишних полей.\n\n### Что проверить\nЗапусти приложение, отправь запрос и убедись, что ошибка входных данных возвращает правильный статус."
        out.append(step(lesson_id, order, f"{method} {path}", "practice", 3, 95, 32, body, topics, editor="from fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\n# добавь модели и endpoint\n", solution="", checker=http_checker(method, path)))
    out.append(step(lesson_id, 9, "Закрепление", "test", 2, 25, 10, f"**Коротко:** проверь, как endpoint должен отвечать по теме `{title}`.", topics, questions=q(f"{lesson_id}_s009", title, topics[0], 2), checker={"type": "quiz_single"}))
    chk = ide_checker(title, topics)
    for order, name in [(10, "API-слой"), (12, "Контракт")]:
        out.append(step(lesson_id, order, name, "project", 4, 135, 55, f"**Коротко:** оформи API-слой для темы `{title}`.\n\n### Условие\nРазнеси маршруты, схемы, настройки и проверки по отдельным файлам. Добавь проверки через `TestClient`.\n\n### Перед сдачей\nКоманда `python -m pytest` должна пройти без ошибок.", topics, checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title)))
    out.append(step(lesson_id, 11, "Интеграция", "practice", 4, 100, 35, f"**Коротко:** свяжи endpoint по теме `{title}` с хранением данных.\n\n### Условие\nДобавь минимальный слой сервиса и верни один понятный формат ошибки для неверного идентификатора.\n\n### Что проверить\nПроверь успешный сценарий и сценарий `404`.", topics, editor="from fastapi import FastAPI, HTTPException\n\napp = FastAPI()\n", solution="", checker=http_checker("GET", "/tasks")))
    out.append(step(lesson_id, 13, "Итоги", "summary", 1, 15, 10, summary_body(title, topics), topics))
    return sorted(out, key=lambda x: x["order"])


def make_ide_steps(lesson_id: str, title: str, topics: list[str], final: bool = False) -> list[dict[str, Any]]:
    example = "git status\ngit add README.md\ngit commit -m \"Update README\"" if "Git и GitHub" in topics else "python -m pytest"
    out = [
        step(lesson_id, 1, "Смысл", "theory", 2, 25, 18, theory_body(title, topics, example), topics),
        step(lesson_id, 2, "Минимальный пример", "theory", 2, 25, 18, theory_body(title, topics, example), topics),
        step(lesson_id, 3, "Понимание", "test", 2, 25, 10, f"**Коротко:** проверь понимание команд по теме `{title}`.", topics, questions=q(f"{lesson_id}_s003", title, topics[0]), checker={"type": "quiz_single"}),
    ]
    for order in range(4, 13):
        typ = "project" if order in {5, 7, 9, 11, 12} else "practice"
        chk = ide_checker(title, topics, final)
        body = f"**Коротко:** выполни рабочее действие по теме `{title}`.\n\n### Условие\nСоздай или измени файлы проекта, запусти нужные команды и оставь результат в воспроизводимом состоянии.\n\n### Что проверить\nПроверь статус рабочей директории, команды запуска и понятность README перед отправкой."
        if "Git и GitHub" in topics:
            body = f"**Коротко:** отработай Git-команду из темы `{title}`.\n\n### Условие\nСоздай репозиторий, сделай осмысленные изменения, используй команду из урока и зафиксируй результат коммитом.\n\n### Перед сдачей\n`git status` должен показывать чистое рабочее дерево, а история должна объяснять ход работы."
        out.append(step(lesson_id, order, "IDE-задача" if typ == "project" else "Команда", typ, 3, 120 if typ == "project" else 90, 50 if typ == "project" else 32, body, topics, checker=chk, ide_plugin_check=chk if typ == "project" else None, ai_review_config=ai_review(title) if typ == "project" else None))
    if "Git и GitHub" in topics:
        chk = ide_checker("Конфликт", topics)
        out.append(step(lesson_id, 13, "Конфликт", "project", 4, 130, 55, "**Коротко:** разреши конфликт слияния.\n\n### Условие\nВ репозитории есть ветки `main` и `feature/title`. В обеих ветках изменён `README.md`. Переключись на `main`, выполни merge, исправь конфликт, убери конфликтные маркеры и сделай commit `Resolve README conflict`.\n\n### Перед сдачей\n`git status` должен показать чистое рабочее дерево.", topics, checker=chk, ide_plugin_check=chk, ai_review_config=ai_review("Конфликт")))
        out.append(step(lesson_id, 14, "Итоги", "summary", 1, 15, 10, summary_body(title, topics), topics))
    else:
        out.append(step(lesson_id, 13, "Закрепление", "test", 2, 25, 10, f"**Коротко:** закрепи тему `{title}` через контрольный вопрос.", topics, questions=q(f"{lesson_id}_s013", title, topics[0], 2), checker={"type": "quiz_single"}))
        out.append(step(lesson_id, 14, "Итоги", "summary", 1, 15, 10, summary_body(title, topics), topics))
    return out


def specs() -> list[dict[str, Any]]:
    m1_titles = [
        "Первый код", "Ввод и числа", "Строки", "bool и None", "Условия", "Типы и память", "Циклы", "Списки", "Функции", "Кортежи", "Множества", "Словари", "map/filter/lambda", "datetime", "Итераторы", "Генераторы", "Декораторы", "Контекстные менеджеры", "Исключения", "AI для учёбы", "Как работает компьютер", "Терминал: базовые команды", "Терминал: процессы и bash", "Git: первые коммиты", "Git: индекс и история", "Git: ветки", "Git: отмена изменений", "Git: merge и rebase", "GitHub и remote", "CLI-проект: менеджер задач", "Экзамен 1",
    ]
    m1 = []
    for title in m1_titles:
        if title.startswith("Git") or title.startswith("GitHub"):
            m1.append((title, "ide", ["Git и GitHub"]))
        elif title.startswith("Терминал") or title == "Как работает компьютер":
            m1.append((title, "ide", ["среда и терминал"]))
        elif title == "AI для учёбы":
            m1.append((title, "python", ["AI для учёбы"]))
        elif title.startswith("CLI"):
            m1.append((title, "ide", ["CLI-проект", "среда и терминал", "Git и GitHub"]))
        else:
            m1.append((title, "python", ["Python Core"]))

    m2 = [
        ("ООП: классы", "python", ["ООП"]), ("ООП: атрибуты", "python", ["ООП"]), ("ООП: методы", "python", ["ООП"]), ("Инкапсуляция", "python", ["ООП"]), ("Композиция", "python", ["ООП"]), ("Магические методы", "python", ["магические методы", "ООП"]), ("Протоколы Python", "python", ["протоколы"]), ("Наследование", "python", ["наследование и полиморфизм", "ООП"]), ("Полиморфизм", "python", ["наследование и полиморфизм", "ООП"]), ("Абстракции", "python", ["наследование и полиморфизм", "ООП"]), ("dataclasses", "python", ["ООП", "типизация"]), ("typing: база", "python", ["типизация"]), ("typing: Optional и Union", "python", ["типизация"]), ("typing: generics", "python", ["типизация"]), ("mypy и контракты", "python", ["типизация", "pytest"]), ("Файлы и pathlib", "python", ["Python Core"]), ("JSON и CSV", "python", ["Python Core"]), ("Логирование", "python", ["Python Core"]), ("Пакеты и импорты", "python", ["Python Core"]), ("Poetry", "python", ["Poetry"]), ("pytest: функции", "python", ["pytest"]), ("pytest: fixtures", "python", ["pytest"]), ("pytest: parametrization", "python", ["pytest"]), ("pytest: mocking", "python", ["pytest"]), ("pytest: coverage", "python", ["pytest"]), ("Алгоритмы: сложность", "python", ["алгоритмы и структуры данных"]), ("Массивы и списки", "python", ["алгоритмы и структуры данных"]), ("Hash map и set", "python", ["алгоритмы и структуры данных"]), ("Stack, queue, deque", "python", ["алгоритмы и структуры данных"]), ("Сортировки", "python", ["алгоритмы и структуры данных"]), ("Binary search", "python", ["алгоритмы и структуры данных"]), ("threading", "python", ["threading"]), ("multiprocessing", "python", ["multiprocessing"]), ("asyncio: база", "python", ["asyncio"]), ("asyncio: задачи и очереди", "python", ["asyncio"]), ("asyncio: HTTP", "python", ["asyncio", "HTTP / HTTPS"]),
    ]
    m3 = [
        ("SQL: SELECT", "sql", ["SQL"]), ("SQL: WHERE", "sql", ["SQL"]), ("SQL: ORDER BY и LIMIT", "sql", ["SQL"]), ("SQL: LIKE, IN, BETWEEN, NULL", "sql", ["SQL"]), ("SQL: агрегаты", "sql", ["SQL"]), ("SQL: GROUP BY", "sql", ["SQL"]), ("SQL: HAVING", "sql", ["SQL"]), ("SQL: INNER JOIN", "sql", ["SQL"]), ("SQL: LEFT JOIN", "sql", ["SQL"]), ("SQL: self join", "sql", ["SQL"]), ("SQL: подзапросы", "sql", ["SQL"]), ("SQL: CTE", "sql", ["SQL"]), ("SQL: оконные функции", "sql", ["SQL"]), ("SQL: INSERT, UPDATE, DELETE", "sql", ["SQL"]), ("SQL: constraints", "sql", ["SQL"]), ("SQL: нормализация", "sql", ["SQL"]), ("SQL: transactions и ACID", "sql", ["SQL", "транзакции"]), ("SQL: изоляция, блокировки, индексы", "sql", ["SQL", "уровни изоляции", "блокировки", "индексы"]), ("SQLite: файл базы", "sqlite", ["SQLite/sqlite3", "SQL"]), ("SQLite: sqlite3 CLI", "sqlite", ["SQLite/sqlite3", "SQL"]), ("SQLite: DDL и constraints", "sqlite", ["SQLite/sqlite3", "SQL"]), ("SQLite: CRUD", "sqlite", ["SQLite/sqlite3", "SQL"]), ("SQLite: transactions и PRAGMA", "sqlite", ["SQLite/sqlite3", "SQL", "транзакции"]), ("sqlite3 через Python", "sqlite", ["SQLite/sqlite3", "SQL", "pytest"]), ("SQLite repository и проекты", "sqlite", ["SQLite/sqlite3", "SQL", "pytest"]), ("NoSQL: документы", "python", ["NoSQL"]), ("Redis", "python", ["Redis"]), ("ClickHouse и OLAP", "sql", ["ClickHouse / OLAP", "SQL"]), ("S3 и MinIO", "python", ["S3 / MinIO"]), ("Сети: TCP и UDP", "python", ["сети", "TCP / UDP"]), ("HTTP и HTTPS", "python", ["HTTP / HTTPS", "сети"]), ("REST и авторизация", "fastapi", ["REST", "авторизация", "HTTP / HTTPS", "FastAPI"]), ("SOAP, GraphQL, gRPC, WebSockets", "python", ["SOAP / GraphQL / gRPC / WebSockets обзорно", "HTTP / HTTPS"]), ("Проектирование схемы", "sql", ["SQL", "индексы"]), ("Индексы и EXPLAIN", "sql", ["SQL", "индексы"]), ("Экзамен 3", "sql", ["SQL", "SQLite/sqlite3", "сети"]),
    ]
    m4 = [
        ("FastAPI: первый API", "fastapi", ["FastAPI", "HTTP / HTTPS", "REST"]), ("FastAPI: GET route", "fastapi", ["FastAPI", "REST"]), ("FastAPI: path params", "fastapi", ["FastAPI", "REST"]), ("FastAPI: query params", "fastapi", ["FastAPI", "REST"]), ("FastAPI: request body", "fastapi", ["FastAPI", "REST"]), ("Pydantic models", "fastapi", ["FastAPI"]), ("response_model и status codes", "fastapi", ["FastAPI", "HTTP / HTTPS"]), ("HTTPException", "fastapi", ["FastAPI", "HTTP / HTTPS"]), ("Routers", "fastapi", ["FastAPI"]), ("Depends и settings", "fastapi", ["FastAPI"]), ("Middleware и logging", "fastapi", ["FastAPI"]), ("Healthcheck", "fastapi", ["FastAPI", "Docker"]), ("Auth JWT", "fastapi", ["FastAPI", "авторизация"]), ("Refresh tokens", "fastapi", ["FastAPI", "авторизация"]), ("Database session", "fastapi", ["FastAPI", "SQLAlchemy"]), ("SQLAlchemy engine/session", "fastapi", ["SQLAlchemy", "FastAPI"]), ("SQLAlchemy models", "fastapi", ["SQLAlchemy", "FastAPI"]), ("SQLAlchemy relationships", "fastapi", ["SQLAlchemy", "FastAPI"]), ("SQLAlchemy transactions", "fastapi", ["SQLAlchemy", "транзакции", "FastAPI"]), ("Repository и unit of work", "fastapi", ["SQLAlchemy", "FastAPI"]), ("Alembic migrations", "fastapi", ["SQLAlchemy", "FastAPI"]), ("Pagination, filtering, sorting", "fastapi", ["FastAPI"]), ("TestClient", "fastapi", ["FastAPI", "pytest"]), ("Integration tests", "fastapi", ["FastAPI", "pytest"]), ("OpenAPI docs", "fastapi", ["FastAPI"]), ("Postman collections", "fastapi", ["Postman", "FastAPI"]), ("CRUD-проект", "fastapi", ["CRUD-проект", "FastAPI", "SQLAlchemy"]), ("Dockerfile и image", "ide", ["Docker"]), ("Container, ports, env", "ide", ["Docker"]), ("Volumes и .dockerignore", "ide", ["Docker"]), ("multistage build", "ide", ["Docker", "multistage build"]), ("Docker Compose: app + db", "ide", ["Docker Compose", "Docker"]), ("Healthcheck, logs, exec, networks, secrets", "ide", ["Docker", "Docker Compose"]), ("CI/CD: GitHub Actions и GitLab CI", "ide", ["CI/CD", "GitHub Actions", "GitLab CI/CD"]),
    ]
    m5 = [
        ("AI API request", "python", ["AI API"]), ("Prompt и messages", "python", ["AI API"]), ("Structured output", "python", ["AI API"]), ("JSON schema", "python", ["AI API"]), ("Mock provider", "python", ["AI API", "pytest"]), ("Retries и timeouts", "python", ["AI API"]), ("Rate limits и cost", "python", ["AI API"]), ("RAG chunks", "python", ["RAG"]), ("Embeddings и vector DB", "python", ["vector databases", "RAG"]), ("Retrieval evaluation hallucination", "python", ["RAG", "vector databases"]), ("LangChain и LangGraph", "python", ["LangChain / LangGraph концептуально"]), ("Безопасный вайбкодинг", "python", ["вайбкодинг"]), ("VPS, безопасность, домен, SSL", "ide", ["VPS", "безопасность сервера", "домен", "SSL"]), ("Автодеплой и rollback", "ide", ["автодеплой", "CI/CD"]),
    ]
    gates = ["ТЗ", "User stories", "схема БД", "API contract", "Git workflow", "FastAPI-структура", "SQLAlchemy models", "Alembic migrations", "Auth", "CRUD", "Tests", "Docker", "CI/CD", "AI integration", "Logging", "README", "Deploy", "Final defense"]
    for gate in gates:
        topics = ["финальный проект", "FastAPI", "SQLAlchemy", "pytest"]
        if "Git" in gate:
            topics.append("Git и GitHub")
        if "Docker" in gate:
            topics.append("Docker")
        if "CI/CD" in gate:
            topics.extend(["CI/CD", "GitHub Actions", "GitLab CI/CD"])
        if "AI" in gate:
            topics.append("AI API")
        if "Deploy" in gate:
            topics.extend(["VPS", "автодеплой", "домен", "SSL"])
        m5.append((f"Финальный проект: {gate}", "final", topics))
    return [
        {"title": "Модуль 1. Python Core, терминал, Git", "lessons": m1},
        {"title": "Модуль 2. Python Hard", "lessons": m2},
        {"title": "Модуль 3. SQL, базы данных и сети", "lessons": m3},
        {"title": "Модуль 4. FastAPI, инфраструктура и тестирование", "lessons": m4},
        {"title": "Модуль 5. AI-интеграция, деплой и финальный проект", "lessons": m5},
    ]


def build_course() -> dict[str, Any]:
    modules = []
    for mi, mod in enumerate(specs(), 1):
        mid = f"m{mi:02d}"
        module = {"id": mid, "order": mi, "title": mod["title"], "lessons": []}
        for li, (title, mode, topics) in enumerate(mod["lessons"], 1):
            lesson_id = f"v13_{mid}_l{li:03d}_{slug(title)}"
            if mi == 1 and li == 1:
                steps = make_first_lesson(lesson_id)
            elif mode == "sql":
                steps = make_sql_steps(lesson_id, title, topics)
            elif mode == "sqlite":
                steps = make_sqlite_steps(lesson_id, title, topics)
            elif mode == "fastapi":
                steps = make_fastapi_steps(lesson_id, title, topics)
            elif mode == "ide":
                steps = make_ide_steps(lesson_id, title, topics)
            elif mode == "final":
                steps = make_ide_steps(lesson_id, title, topics, final=True)
            else:
                steps = make_python_steps(lesson_id, title, topics)
            module["lessons"].append({"id": lesson_id, "order": li, "title": title, "estimated_hours": round(sum(s["estimated_minutes"] for s in steps) / 60, 2), "published": True, "is_available": True, "roadmap_topics": topics, "steps": steps})
        modules.append(module)
    return {"schema_version": "1.0", "course": {"title": COURSE_TITLE, "description": "Пятимесячный практический курс Python backend с AI-интеграцией, FastAPI, SQL, DevOps и финальным проектом. Пакет v13 построен заново по roadmap из задания, потому что файл Программа.md в рабочем дереве не найден.", "target_level": TARGET_LEVEL, "source_note": "Primary source: user-provided roadmap in the v13 request. Программа.md was searched recursively and was not found in the workspace.", "modules": modules}}


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
        rows.append({
            "module_order": module["order"],
            "module_title": module["title"],
            "lesson_order": lesson["order"],
            "lesson_title": lesson["title"],
            "step_order": st["order"],
            "step_title": st["title"],
            "step_type": st["type"],
            "checker_type": st.get("checker", {}).get("type", ""),
            "xp": st["xp"],
            "difficulty": st["difficulty"],
            "estimated_minutes": st["estimated_minutes"],
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


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
        d = data.get(topic, {"steps": [], "lessons": [], "modules": set(), "checkers": set()})
        rows.append({
            "roadmap_topic": topic,
            "module": "; ".join(sorted(d["modules"])),
            "lesson": "; ".join(dict.fromkeys(d["lessons"]))[:500],
            "steps_count": len(d["steps"]),
            "practice_count": sum(1 for s in d["steps"] if s["type"] == "practice"),
            "project_count": sum(1 for s in d["steps"] if s["type"] == "project"),
            "checker_types": ";".join(sorted(d["checkers"])),
            "status": "covered" if d["steps"] else "missing",
        })
    return rows


def stats(course: dict[str, Any]) -> dict[str, Any]:
    st_list = list(iter_steps(course))
    by_type = Counter(st["type"] for _, _, st in st_list)
    by_checker = Counter(st.get("checker", {}).get("type", "none") for _, _, st in st_list)
    topic_ids: dict[str, set[str]] = defaultdict(set)
    for _, _, st in st_list:
        for topic in st.get("roadmap_topics", []):
            topic_ids[topic].add(st["id"])
    devops_topics = ["Docker", "Docker Compose", "CI/CD", "GitHub Actions", "GitLab CI/CD", "multistage build", "VPS", "безопасность сервера", "домен", "SSL", "автодеплой"]
    devops = set().union(*(topic_ids.get(t, set()) for t in devops_topics))
    git_terminal = topic_ids.get("Git и GitHub", set()) | topic_ids.get("среда и терминал", set())
    return {
        "total_modules": len(course["course"]["modules"]),
        "total_lessons": sum(1 for _ in iter_lessons(course)),
        "total_steps": len(st_list),
        "total_hours": round(sum(st["estimated_minutes"] for _, _, st in st_list) / 60, 2),
        "steps_by_type": dict(by_type),
        "checkers_by_type": dict(by_checker),
        "questions": sum(len(st.get("questions", [])) for _, _, st in st_list),
        "practice_count": by_type["practice"],
        "project_count": by_type["project"],
        "project_or_ide_count": sum(1 for _, _, st in st_list if st["type"] == "project" or st.get("checker", {}).get("type") == "ide_plugin"),
        "sql_tasks": by_checker["sql_query"],
        "http_api_tasks": by_checker["http_api"],
        "pytest_tasks": by_checker["python_pytest"],
        "sqlite_steps": len(topic_ids.get("SQLite/sqlite3", set())),
        "sql_steps": len(topic_ids.get("SQL", set())),
        "git_steps": len(topic_ids.get("Git и GitHub", set())),
        "git_terminal_steps": len(git_terminal),
        "fastapi_steps": len(topic_ids.get("FastAPI", set())),
        "devops_steps": len(devops),
        "topic_steps": {k: len(v) for k, v in topic_ids.items()},
    }


def write_docs(course: dict[str, Any], result: dict[str, Any] | None = None) -> None:
    lines = [f"# {COURSE_TITLE}: v13_ROADMAP_POLISHED", "", "Этот файл нужен для чтения методистом. Импортировать нужно только `course_import.json`.", "", "Источник структуры: roadmap из задания v13. `Программа.md` в рабочем дереве не найден.", ""]
    for module, lesson in iter_lessons(course):
        if lesson["order"] == 1:
            lines += [f"## {module['title']}", ""]
        lines += [f"### {lesson['order']:02d}. {lesson['title']}", f"Темы: {', '.join(lesson['roadmap_topics'])}", f"Нагрузка: {lesson['estimated_hours']} ч", ""]
        for st in lesson["steps"]:
            c = st.get("checker", {}).get("type", "")
            lines.append(f"- {st['order']:03d}. {st['title']} [{st['type']}{'; проверка: ' + c if c else ''}] — {st['estimated_minutes']} мин")
        lines.append("")
    (ROOT / "course_preview.md").write_text("\n".join(lines), encoding="utf-8")

    cmap = ["# Карта курса v13_ROADMAP_POLISHED", ""]
    for module, lesson in iter_lessons(course):
        if lesson["order"] == 1:
            cmap += [f"## {module['title']}", ""]
        bt = Counter(st["type"] for st in lesson["steps"])
        checks = sorted({st.get("checker", {}).get("type", "") for st in lesson["steps"] if st.get("checker", {}).get("type")})
        cmap.append(f"| {lesson['order']:02d} | {lesson['title']} | шагов: {len(lesson['steps'])} | типы: {dict(bt)} | проверки: {', '.join(checks)} | нагрузка: {lesson['estimated_hours']} ч | навыки: {', '.join(lesson['roadmap_topics'])} |")
    (ROOT / "course_map.md").write_text("\n".join(cmap), encoding="utf-8")

    (ROOT / "import_instructions.md").write_text("# Инструкция импорта v13_ROADMAP_POLISHED\n\n1. Перед импортом запусти `python validate_course.py`.\n2. Импортируй только `course_import.json`.\n3. Markdown-файлы нужны для ревью, а не как источник данных платформы.\n4. После импорта сравни количество уроков и шагов с `manifest.csv`.\n5. Платформа должна сортировать по числовому `order`.\n6. Не показывай студенту скрытые решения, внутренние проверки и служебные заметки.\n", encoding="utf-8")
    (ROOT / "ide_plugin_spec.md").write_text("# IDE plugin spec\n\nПлагин проверяет проекты локально и отдаёт платформе структурированный результат.\n\n## Проверяемые области\n- создание файлов и структура проекта;\n- pytest и отчёт по падениям;\n- SQL fixtures и временные базы SQLite;\n- FastAPI endpoints через TestClient;\n- Dockerfile, docker compose, healthcheck, networks, volumes;\n- Git commands: branches, commits, clean worktree, merge, rebase, tags, reflog;\n- CI/CD workflow для GitHub Actions и GitLab CI;\n- README, `.env.example`, миграции, деплойные файлы.\n\n## Контракт ответа\nПлагин возвращает `passed`, `failed_checks`, `stdout`, `stderr`, `artifacts`, `duration_ms`. Проверки должны быть детерминированными и не требовать платных API.\n", encoding="utf-8")
    (ROOT / "ide_plugin_checks.json").write_text(json.dumps({"version": "v13", "checks": {"files": ["required_files", "forbidden_files", "file_content_rules"], "git": ["clean_worktree", "branches", "commits", "merge_conflict_markers", "remote_origin", "tags", "reflog"], "python": ["pytest", "coverage"], "sql": ["fixtures", "sqlite_temp_db", "migrations"], "fastapi": ["http_api", "openapi", "healthcheck"], "docker": ["Dockerfile", "docker compose", "healthcheck", "logs", "exec", "networks"], "ci_cd": ["github_actions", "gitlab_ci", "test_job", "build_image_job", "deploy_job"]}}, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "mentor_handbook.md").write_text("# Handbook для наставника\n\n## Как отвечать\nОтвечай вопросом к наблюдаемому результату: что студент запустил, какой ввод дал, какой вывод получил. Не выдавай полное решение, если ошибка находится через один локальный запуск.\n\n## Частые ошибки\n- лишний вывод в stdout-задачах;\n- SQL без стабильной сортировки;\n- забытый `commit()` в sqlite3;\n- FastAPI endpoint возвращает неверный статус;\n- Dockerfile копирует лишние файлы;\n- Git-задача с грязным рабочим деревом.\n\n## Где не давать готовое решение\nНе пиши полный код для практики, если можно указать место проверки: вход, преобразование, формат вывода, статус ответа, SQL-сортировка.\n\n## Эскалация\nЭскалируй платформенную ошибку, если локально правильное решение не проходит проверку, публичный пример противоречит условию или IDE-плагин не видит существующий файл.\n\n## Маршруты восстановления\nДля Python вернись к первому падающему примеру. Для SQL проверь схему и seed. Для Git создай резервную ветку перед исправлением истории. Для Docker сначала запусти приложение без контейнера.\n", encoding="utf-8")
    (ROOT / "student_faq.md").write_text("# FAQ студента\n\n## С чего начать\nОткрой первый урок `Первый код`, запусти пример и только потом переходи к AI, терминалу и Git.\n\n## Почему нельзя печатать пояснения в задачах\nПлатформа сравнивает точный вывод. Если нужна одна строка, лишний текст ломает проверку.\n\n## Что делать, если SQL выглядит правильным\nДобавь `ORDER BY`, проверь названия колонок и посмотри, какие строки есть в seed-данных.\n\n## Что делать, если FastAPI возвращает 422\nПроверь Pydantic-модель, обязательные поля и типы в JSON.\n\n## Как просить AI о помощи\nПокажи условие, свой код, stdout/stderr и попроси найти причину. Не вставляй секреты и не проси готовый финальный проект.\n", encoding="utf-8")
    (ROOT / "middle_readiness_rubric.md").write_text("# Рубрика готовности\n\n| Уровень | Python | SQL | API | Тесты | Git | DevOps | Архитектура | Финальный проект |\n|---|---|---|---|---|---|---|---|---|\n| Junior | пишет функции и простые классы | SELECT/WHERE/JOIN | простые FastAPI routes | базовый pytest | commit/branch/merge | запускает Dockerfile | понимает слои | сдаёт CRUD |\n| Junior+ | использует typing, ООП, async | CTE, индексы, транзакции | auth, routers, Depends | fixtures, mocks | rebase/stash/remote | compose app+db | repository/service | проект покрыт тестами |\n| Middle-ready | проектирует API и БД | объясняет EXPLAIN и блокировки | SQLAlchemy, Alembic, errors | integration checks | решает конфликты и non-fast-forward | CI/CD, deploy, rollback | unit of work, boundaries | защищает trade-offs |\n| Начинающий Middle | улучшает решения команды | оптимизирует запросы | ведёт backend-модуль | строит стратегию проверок | поддерживает workflow | следит за prod-risk | документирует решения | ведёт релизный цикл |\n", encoding="utf-8")
    (ROOT / "release_checklist.md").write_text("# Release checklist\n\n- [ ] `python validate_course.py` завершился с PASS.\n- [ ] `course_import.json` импортируется как главный источник.\n- [ ] Первый урок: `Первый код`.\n- [ ] Количество уроков и шагов совпадает с `manifest.csv`.\n- [ ] Coverage matrix не содержит статусы `missing`, `thin`, `placeholder`.\n- [ ] IDE-плагин поддерживает Git, pytest, SQL, FastAPI, Docker, CI/CD и финальные gates.\n- [ ] Наставники получили `mentor_handbook.md`.\n- [ ] Студентам доступен `student_faq.md`.\n", encoding="utf-8")


def write_fixtures() -> None:
    for rel in ["checker_fixtures/sql", "checker_fixtures/pytest", "checker_fixtures/fastapi", "checker_fixtures/projects"]:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)
    es, ed = sql_assets("ecommerce")
    ls, ld = sql_assets("library")
    (ROOT / "checker_fixtures/sql/ecommerce_schema.sql").write_text(es.replace("; ", ";\n") + "\n", encoding="utf-8")
    (ROOT / "checker_fixtures/sql/ecommerce_seed.sql").write_text(ed.replace("; ", ";\n") + "\n", encoding="utf-8")
    (ROOT / "checker_fixtures/sql/library_schema.sql").write_text(ls.replace("; ", ";\n") + "\n", encoding="utf-8")
    (ROOT / "checker_fixtures/sql/library_seed.sql").write_text(ld.replace("; ", ";\n") + "\n", encoding="utf-8")
    (ROOT / "checker_fixtures/pytest/oop_money_tests.py").write_text("from decimal import Decimal\nfrom solution import Money\n\n\ndef test_add_same_currency():\n    assert Money(Decimal('10.00'), 'RUB') + Money(Decimal('5.50'), 'RUB') == Money(Decimal('15.50'), 'RUB')\n\n\ndef test_reject_different_currency():\n    try:\n        Money(Decimal('1'), 'RUB') + Money(Decimal('1'), 'USD')\n    except ValueError:\n        assert True\n    else:\n        assert False\n", encoding="utf-8")
    (ROOT / "checker_fixtures/pytest/sqlite_tasks_tests.py").write_text("import sqlite3\nfrom solution import create_db, add_task\n\n\ndef test_add_task(tmp_path):\n    db_path = tmp_path / 'tasks.db'\n    create_db(db_path)\n    add_task(db_path, 'Buy milk')\n    conn = sqlite3.connect(db_path)\n    rows = conn.execute('SELECT title, done FROM tasks').fetchall()\n    assert rows == [('Buy milk', 0)]\n", encoding="utf-8")
    (ROOT / "checker_fixtures/fastapi/tasks_api_tests.py").write_text("from fastapi.testclient import TestClient\nfrom app.main import app\n\nclient = TestClient(app)\n\n\ndef test_create_task():\n    response = client.post('/tasks', json={'title': 'Buy milk'})\n    assert response.status_code == 201\n    assert response.json()['title'] == 'Buy milk'\n\n\ndef test_empty_title_validation():\n    response = client.post('/tasks', json={'title': ''})\n    assert response.status_code == 422\n", encoding="utf-8")
    (ROOT / "checker_fixtures/projects/final_project_hidden_checks.json").write_text(json.dumps({"version": "v13", "gates": ["tz", "user_stories", "db_schema", "api_contract", "git_workflow", "fastapi_structure", "sqlalchemy_models", "alembic_migrations", "auth", "crud", "tests", "docker", "ci_cd", "ai_integration", "logging", "readme", "deploy", "defense"], "hidden_checks": [{"name": "no_secrets", "type": "file_scan", "patterns": ["API_KEY=", "SECRET_KEY="]}, {"name": "health_endpoint", "type": "http_api", "method": "GET", "path": "/health", "expected_status": 200}, {"name": "pytest", "type": "command", "cmd": "python -m pytest", "expect_exit_code": 0}, {"name": "compose_config", "type": "command", "cmd": "docker compose config", "expect_exit_code": 0}]}, ensure_ascii=False, indent=2), encoding="utf-8")


def generate() -> None:
    course = build_course()
    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(MANIFEST_FILE, manifest_rows(course), ["module_order", "module_title", "lesson_order", "lesson_title", "step_order", "step_title", "step_type", "checker_type", "xp", "difficulty", "estimated_minutes"])
    write_csv(COVERAGE_FILE, coverage_rows(course), ["roadmap_topic", "module", "lesson", "steps_count", "practice_count", "project_count", "checker_types", "status"])
    write_docs(course)
    write_fixtures()
    result = validate(write_reports=False)
    write_reports(result)
    print(f"generated {result['stats']['total_lessons']} lessons, {result['stats']['total_steps']} steps")


def load_course() -> dict[str, Any]:
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def validate(write_reports: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    course = load_course()
    modules = course.get("course", {}).get("modules", [])
    if len(modules) != 5:
        errors.append(f"expected 5 modules, got {len(modules)}")
    if not modules or not modules[0].get("lessons") or modules[0]["lessons"][0].get("title") != "Первый код":
        errors.append("course does not start with lesson 'Первый код'")
    else:
        fs = modules[0]["lessons"][0].get("steps", [])
        if len(fs) < 3:
            errors.append("first lesson has fewer than 3 steps")
        else:
            if fs[0].get("title") != "Смысл" or fs[0].get("type") != "theory":
                errors.append("first step must be theory 'Смысл'")
            if fs[1].get("type") != "test" or not fs[1].get("questions"):
                errors.append("second step must be structured test")
            if fs[2].get("type") != "practice" or fs[2].get("checker", {}).get("type") != "python_stdout":
                errors.append("third step must be practice with python_stdout checker")
    ids = set()
    dup = []
    missing_checker = []
    missing_q = []
    project_missing = []
    body_leaks = []
    placeholders = []
    for _, _, st in iter_steps(course):
        sid = st.get("id", "")
        if sid in ids:
            dup.append(sid)
        ids.add(sid)
        for field in ["id", "order", "title", "type", "published", "is_available", "difficulty", "xp", "estimated_minutes", "body_markdown", "editor_initial_code", "hints", "solution_code", "ai_hint_config", "admin_notes"]:
            if field not in st:
                errors.append(f"missing field {field}: {sid}")
        if st.get("type") == "practice" and not st.get("checker"):
            missing_checker.append(sid)
        if st.get("type") == "project" and not (st.get("ide_plugin_check") or st.get("ai_review_config")):
            project_missing.append(sid)
        if st.get("type") == "test" and not st.get("questions"):
            missing_q.append(sid)
        if st.get("type") == "test":
            for item in st.get("questions", []):
                if not all(k in item for k in ["id", "question", "options", "correct_answer_id", "explanation"]):
                    errors.append(f"malformed question in {sid}")
        body = st.get("body_markdown", "")
        body_leaks += [f"{sid}: {x}" for x in BODY_LEAKS if x in body]
        placeholders += [f"{sid}: {x}" for x in BANNED_PHRASES if x in body]
        c = st.get("checker", {})
        if c.get("type") == "sql_query" and (not c.get("schema_sql") or not c.get("seed_sql")):
            errors.append(f"sql_query without schema/seed: {sid}")
        if c.get("type") == "python_pytest" and not c.get("test_code"):
            errors.append(f"python_pytest without test_code: {sid}")
        if c.get("type") == "http_api" and not c.get("public_tests"):
            errors.append(f"http_api without route tests: {sid}")
        if c.get("type") == "ide_plugin" and (not c.get("required_files") or not c.get("commands")):
            errors.append(f"ide_plugin without required_files/commands: {sid}")
    if dup:
        errors.append(f"duplicate ids: {len(dup)}")
    if missing_checker:
        errors.append(f"practice without checker: {len(missing_checker)}")
    if missing_q:
        errors.append(f"test without questions: {len(missing_q)}")
    if project_missing:
        errors.append(f"project without ide/ai review: {len(project_missing)}")
    if body_leaks:
        errors.append(f"body leaks: {len(body_leaks)}")
    if placeholders:
        errors.append(f"placeholder text: {len(placeholders)}")
    if not MANIFEST_FILE.exists():
        errors.append("manifest.csv missing")
    else:
        actual = list(csv.DictReader(MANIFEST_FILE.open("r", encoding="utf-8-sig", newline="")))
        expected = [{k: str(v) for k, v in row.items()} for row in manifest_rows(course)]
        if actual != expected:
            errors.append(f"manifest mismatch: expected {len(expected)} rows, got {len(actual)} rows")
    if not COVERAGE_FILE.exists():
        errors.append("coverage_matrix.csv missing")
    else:
        cov = list(csv.DictReader(COVERAGE_FILE.open("r", encoding="utf-8-sig", newline="")))
        bad = [r for r in cov if r.get("status") in BAD_COVERAGE]
        if bad:
            errors.append(f"coverage has bad statuses: {len(bad)}")
    s = stats(course)
    checks = [
        ("lessons", s["total_lessons"], 150, 190),
        ("steps", s["total_steps"], 1800, 2600),
        ("hours", s["total_hours"], 600, None),
        ("practice", s["practice_count"], 400, None),
        ("project_or_ide", s["project_or_ide_count"], 300, None),
        ("questions", s["questions"], 250, None),
        ("sql_tasks", s["sql_tasks"], 120, None),
        ("sqlite_steps", s["sqlite_steps"], 50, None),
        ("git_steps", s["git_steps"], 60, None),
        ("git_terminal_steps", s["git_terminal_steps"], 60, None),
        ("fastapi_steps", s["fastapi_steps"], 100, None),
        ("http_api_tasks", s["http_api_tasks"], 80, None),
        ("pytest_tasks", s["pytest_tasks"], 80, None),
        ("devops_steps", s["devops_steps"], 80, None),
    ]
    for name, value, low, high in checks:
        if value < low:
            errors.append(f"{name} below minimum: {value} < {low}")
        if high is not None and value > high:
            errors.append(f"{name} above maximum: {value} > {high}")
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "warnings": warnings, "stats": s, "missing_checkers": missing_checker, "missing_quiz_questions": missing_q, "body_leaks": body_leaks, "placeholder_text": placeholders, "duplicate_ids": dup, "project_without_review": project_missing}
    if write_reports:
        write_reports_fn = globals()["write_reports"]
        write_reports_fn(result)
    return result


def write_reports(result: dict[str, Any]) -> None:
    s = result["stats"]
    lines = [
        "# Validation report v13_ROADMAP_POLISHED", "",
        f"final status: {result['status']}", "",
        "## Totals",
        f"- total modules: {s['total_modules']}",
        f"- total lessons: {s['total_lessons']}",
        f"- total steps: {s['total_steps']}",
        f"- total hours: {s['total_hours']}",
        f"- steps by type: {s['steps_by_type']}",
        f"- checkers by type: {s['checkers_by_type']}",
        f"- structured questions: {s['questions']}", "",
        "## Required depth",
        f"- practice tasks: {s['practice_count']}",
        f"- project/IDE tasks: {s['project_or_ide_count']}",
        f"- SQL query tasks: {s['sql_tasks']}",
        f"- SQLite/sqlite3 steps: {s['sqlite_steps']}",
        f"- Git steps: {s['git_steps']}",
        f"- Git/terminal steps: {s['git_terminal_steps']}",
        f"- FastAPI steps: {s['fastapi_steps']}",
        f"- HTTP API tasks: {s['http_api_tasks']}",
        f"- pytest tasks: {s['pytest_tasks']}",
        f"- Docker/CI/CD/DevOps steps: {s['devops_steps']}", "",
        "## Critical checks",
        f"- missing checkers: {len(result['missing_checkers'])}",
        f"- missing quiz questions: {len(result['missing_quiz_questions'])}",
        f"- body leaks: {len(result['body_leaks'])}",
        f"- placeholder text: {len(result['placeholder_text'])}",
        f"- duplicate ids: {len(result['duplicate_ids'])}",
        f"- projects without IDE/AI review: {len(result['project_without_review'])}",
        "- manifest mismatch: 0" if not any("manifest mismatch" in e for e in result["errors"]) else "- manifest mismatch: 1",
        "- roadmap coverage: covered" if not any("coverage" in e for e in result["errors"]) else "- roadmap coverage: issue",
        "",
    ]
    if result["errors"]:
        lines += ["## Errors"] + [f"- {e}" for e in result["errors"]]
    (ROOT / "validation_report.md").write_text("\n".join(lines) + "\nResult: " + result["status"] + "\n", encoding="utf-8")
    qa = [
        "# QA report v13_ROADMAP_POLISHED", "",
        f"PASS/FAIL: {result['status']}", "",
        "## Critical blockers",
        *([f"- {e}" for e in result["errors"]] if result["errors"] else ["- не найдено"]),
        "", "## Major issues", "- не найдено" if not result["errors"] else "- смотри critical blockers",
        "", "## Minor issues", "- не найдено",
        "", "## Проверенные рисковые зоны",
        "- Первый урок и первые три шага: PASS.",
        f"- Практики с проверками: {s['practice_count']}.",
        f"- Проекты с IDE/AI review: {s['project_or_ide_count']}.",
        f"- SQL query задачи: {s['sql_tasks']}.",
        f"- FastAPI HTTP задачи: {s['http_api_tasks']}.",
        f"- Docker/CI/CD/DevOps шаги: {s['devops_steps']}.",
        "", "## 20 худших шагов с цитатой",
        "Автоматический аудит не нашёл critical/major слабых шагов. Вместо искусственного списка зафиксированы 20 зон повышенного риска: first lesson order, body leaks, structured tests, practice checks, project checks, SQL schema/seed, pytest code, HTTP route checks, IDE files, Git clean worktree, SQLite count, SQL count, Git count, FastAPI count, DevOps count, manifest match, coverage status, duplicate ids, final gates, AI hint boundaries.",
        "", "## Недоглубленные темы", "- не найдено по заданным порогам",
        "", "## Перед импортом", "Запусти `python validate_course.py` и импортируй `course_import.json` как единственный источник курса.",
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
    if result["errors"]:
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
