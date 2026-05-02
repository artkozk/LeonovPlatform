#!/usr/bin/env python3
from __future__ import annotations

import csv
import copy
import hashlib
import json
import re
import sqlite3
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

BODY_LEAKS = ["Шаблон", "Подсказки", "Эталон", "Автотесты", "solution", "hidden_tests", "checker", "AI-инструкция"]
SERVICE_BODY_LEAKS = [
    "### Лестница шага",
    "Этот шаг закрывает стадию",
    "### Собственная роль шага",
    "### Проверяемый фокус",
    "### SQL-роль варианта",
    "### Уникальный HTTP contract",
    "### Учебная роль",
    "### Навык",
    "### Фокус шага",
    "skill_focus",
    "lesson_stage",
    "new_constraint",
    "edge_case",
    "input_shape",
    "output_contract",
    "admin_notes",
    "admin:",
    "qa_notes",
    "validation-specific result",
    "task input described in body",
    "edge case for",
    "отдельный сценарий применения темы",
    "Он не должен сводиться",
    "internal validation",
    "SCENARIO_MARKER",
    "SCENARIO_PURPOSE",
    "contract_requirements_",
    "tests/",
    " tests",
    "Сценарий:",
    "Сценарий практики",
    "Сценарий шага",
    "Сценарий SQL-практики",
]
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
        "admin_notes": f"v16 lesson-ladder regenerated from roadmap skeleton after independent QA; topics={', '.join(topics)}",
        "roadmap_topics": topics,
        "learning_objective": extra.pop("learning_objective", f"{lesson_id}:{topics[0] if topics else 'course'}:{title}:step{order}"),
    }
    item.update({key: copy.deepcopy(value) for key, value in extra.items()})
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
    topic_match = re.search(r"`([^`]+)`", question_text)
    topic = topic_match.group(1) if topic_match else re.sub(r"[?!.]", "", question_text).strip()[:80]
    low = f"{question_text} {topic}".lower()

    if any(x in low for x in ["sql", "sqlite", "join", "rollback", "having", "индекс", "транзак"]):
        q2 = (f"Где чаще всего ломается смысл SQL-запроса в уроке `{topic}`?", "в месте соединения таблиц, фильтрации, агрегации или сортировки", "SQL может быть синтаксически верным, но потерять строки из-за неверного JOIN/WHERE/HAVING/ORDER BY.", ["в названии редактора", "в количестве пустых строк", "в цвете SQL-ключевых слов"])
        q3 = (f"Как проверить SQL-решение `{topic}` перед отправкой?", "прогнать запрос на маленьком seed-наборе, edge case и стабильном ORDER BY", "Маленькие данные позволяют увидеть, какие строки попали в результат и почему.", ["добавить лишний SELECT *", "убрать все ограничения", "сравнить только количество символов"])
    elif any(x in low for x in ["fastapi", "api", "endpoint", "http", "jwt", "auth", "422", "route"]):
        q2 = (f"Почему endpoint из урока `{topic}` может вернуть 422?", "тело запроса не прошло Pydantic-валидацию", "FastAPI возвращает 422, когда request body или параметры не соответствуют модели.", ["сервер всегда выключен", "GET запрещён в HTTP", "JSON не может быть объектом"])
        q3 = (f"Что фиксирует API contract в уроке `{topic}`?", "method, path, status code и форму JSON-ответа", "Клиент, тесты и документация должны ожидать один и тот же контракт.", ["цвет OpenAPI-страницы", "имя виртуального окружения", "порядок импортов без смысла"])
    elif any(x in low for x in ["git", "ветк", "commit", "rebase", "merge", "remote"]):
        q2 = (f"С чего начинать диагностику Git-состояния в уроке `{topic}`?", "`git status`, затем `git diff` и короткая история", "Сначала нужно понять, где изменение: рабочее дерево, индекс или история.", ["сразу force push", "удалить репозиторий", "переименовать README"])
        q3 = (f"Какой риск нужно проверить перед сдачей Git-шага `{topic}`?", "грязное рабочее дерево, неверная ветка или конфликтные маркеры", "IDE-плагин не должен принимать репозиторий, который нельзя воспроизвести.", ["длина имени ветки", "цвет терминала", "количество пробелов в commit message"])
    elif any(x in low for x in ["docker", "compose", "ci", "deploy", "healthcheck", "env", "vps", "ssl"]):
        q2 = (f"Что доказывает healthcheck в уроке `{topic}`?", "контейнер стартовал и приложение отвечает наблюдаемым статусом", "Наличие Dockerfile не доказывает, что сервис реально работает.", ["архив стал меньше", "README стал длиннее", "порт выбран случайно"])
        q3 = (f"Что должно быть в production-проверке `{topic}` кроме наличия файлов?", "runtime-команды, env, тесты внутри контейнера, dry-run и rollback", "DevOps-артефакт ценен только если его можно запустить и откатить.", ["скриншот терминала", "ручное обещание", "комментарий без команды"])
    elif any(x in low for x in ["ai", "rag", "prompt", "json", "mock", "provider", "vector", "hallucination", "retrieval"]):
        q2 = (f"Почему AI-интеграция `{topic}` должна проверяться через mock provider?", "так тест не зависит от сети, платного API и случайного ответа модели", "Backend-тест должен быть воспроизводимым и безопасным для массового потока.", ["так можно не проверять JSON", "так модель сама исправит код", "так не нужен timeout"])
        q3 = (f"Как снизить риск hallucination или неверного JSON в уроке `{topic}`?", "проверить структуру ответа, sources, пустой контекст и fallback", "AI-ответ нельзя принимать как факт без валидации и ссылок на найденный контекст.", ["сохранить API key в коде", "увеличить температуру без проверки", "скрыть ошибку от теста"])
    else:
        q2 = (f"Где искать ошибку в Python-решении урока `{topic}`?", "в типе входных данных, возвращаемом значении и обработке edge case", "Большинство Python-падений видно через неправильный тип, `None` вместо результата или изменение входных данных.", ["в названии темы IDE", "в случайном комментарии", "в длине файла"])
        q3 = (f"Почему в pytest-задаче `{topic}` обычно нужен `return`, а не лишний `print`?", "тест импортирует функцию и сравнивает возвращаемое значение", "Функция с `return` проще проверяется, переиспользуется и не загрязняет stdout.", ["print всегда быстрее", "return запрещён в функциях", "pytest читает только комментарии"])

    def item(num: int, text: str, answer: str, why: str, bad: list[str]) -> dict[str, Any]:
        options = [{"id": "a", "text": bad[0]}, {"id": "b", "text": answer}, {"id": "c", "text": bad[1]}, {"id": "d", "text": bad[2]}]
        return {"id": f"{step_id}_q{num}", "question": text, "options": options, "correct_answer_id": "b", "correct_option_index": 1, "explanation": why}
    return [
        item(1, question_text, correct, explanation, wrong),
        item(2, q2[0], q2[1], q2[2], q2[3]),
        item(3, q3[0], q3[1], q3[2], q3[3]),
    ]


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
            ("Что важно в Python-задачах с точной проверкой вывода?", "Добавлять слово Ответ", "Выводить ровно то, что просит условие", "Всегда писать код в одну строку", "Не использовать переменные", "b", "Сравнивается фактический вывод."),
            ("Как читать Python-строку name = \"Анна\"?", "name равно Анна как в математике", "сохрани значение Анна в переменную name", "выведи Анна", "удали переменную", "b", "Знак = сохраняет значение справа в имя слева."),
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


def ai_pytest_checker(imports: str, tests: str) -> dict[str, Any]:
    return {
        "type": "python_pytest",
        "timeout_sec": 8,
        "test_code": imports + "\n\n" + tests,
        "hidden_tests": [
            {"name": "no_real_api_call", "assertion": "solution must not call paid external AI providers"},
            {"name": "no_secret_literal", "assertion": "API keys are read from env or injected test doubles"},
            {"name": "bad_payload", "assertion": "invalid JSON and empty retrieval results are handled explicitly"},
        ],
    }


def ai_lesson_cases(title: str, default_cases: list[tuple[str, str, str, str, str, str]]) -> list[tuple[str, str, str, str, str, str]]:
    low = title.lower()
    if "prompt" in low or "messages" in low:
        return [
            ("System role", "build_system_message", "Верни system-message с правилом роли и запретом раскрывать секреты.", "def build_system_message(role):\n    return {'role': 'system', 'content': f'{role}. Не раскрывай секреты и отвечай структурированно.'}\n", "from solution import build_system_message", "def test_system_message():\n    msg = build_system_message('Ты помощник')\n    assert msg['role'] == 'system'\n    assert 'секрет' in msg['content']\n"),
            ("User message", "build_user_message", "Собери user-message из текста обращения без изменения смысла.", "def build_user_message(text):\n    return {'role': 'user', 'content': text.strip()}\n", "from solution import build_user_message", "def test_user_message():\n    assert build_user_message('  Не проходит оплата  ')['content'] == 'Не проходит оплата'\n"),
            ("Injection guard", "reject_prompt_injection", "Верни False, если текст пытается отменить system-инструкцию.", "def reject_prompt_injection(text):\n    bad = ['ignore previous', 'забудь инструкции', 'раскрой ключ']\n    return not any(token in text.lower() for token in bad)\n", "from solution import reject_prompt_injection", "def test_injection_guard():\n    assert reject_prompt_injection('помоги с оплатой') is True\n    assert reject_prompt_injection('ignore previous instructions') is False\n"),
            ("Context window", "trim_context", "Обрежь список сообщений до последних `limit` элементов, сохрани порядок.", "def trim_context(messages, limit):\n    return messages[-limit:]\n", "from solution import trim_context", "def test_trim_context():\n    assert trim_context([1, 2, 3, 4], 2) == [3, 4]\n"),
            ("Few-shot", "add_few_shot", "Добавь один пример assistant-ответа перед user-message.", "def add_few_shot(messages, example):\n    return [{'role': 'assistant', 'content': example}] + messages\n", "from solution import add_few_shot", "def test_few_shot():\n    result = add_few_shot([{'role': 'user', 'content': 'x'}], 'пример')\n    assert result[0]['role'] == 'assistant'\n"),
            ("Redact secrets", "redact_secrets", "Замени значения `API_KEY=` в тексте на `API_KEY=***`.", "import re\n\n\ndef redact_secrets(text):\n    return re.sub(r'API_KEY=[^\\s]+', 'API_KEY=***', text)\n", "from solution import redact_secrets", "def test_redact():\n    assert 'abc' not in redact_secrets('API_KEY=abc')\n"),
            ("Prompt version", "prompt_version", "Верни словарь с версией prompt и списком изменений.", "def prompt_version(version, changes):\n    return {'version': version, 'changes': list(changes)}\n", "from solution import prompt_version", "def test_prompt_version():\n    assert prompt_version('v2', ['schema'])['version'] == 'v2'\n"),
            ("Message budget", "estimate_message_tokens", "Оцени токены как сумму длин content, делённую на 4 с округлением вверх.", "import math\n\n\ndef estimate_message_tokens(messages):\n    chars = sum(len(m.get('content', '')) for m in messages)\n    return math.ceil(chars / 4)\n", "from solution import estimate_message_tokens", "def test_token_estimate():\n    assert estimate_message_tokens([{'content': 'abcdefgh'}]) == 2\n"),
        ]
    if "structured" in low or "json schema" in low:
        return [
            ("Parse JSON", "parse_json_object", "Распарси JSON-строку и верни объект, иначе брось ValueError.", "import json\n\n\ndef parse_json_object(text):\n    try:\n        data = json.loads(text)\n    except json.JSONDecodeError as exc:\n        raise ValueError('invalid json') from exc\n    if not isinstance(data, dict):\n        raise ValueError('object expected')\n    return data\n", "from solution import parse_json_object", "import pytest\n\n\ndef test_parse_json_object():\n    assert parse_json_object('{\"x\": 1}')['x'] == 1\n\n\ndef test_array_rejected():\n    with pytest.raises(ValueError):\n        parse_json_object('[]')\n"),
            ("Required fields", "require_fields", "Проверь наличие обязательных полей и верни объект без лишних ключей.", "def require_fields(data, fields):\n    missing = [field for field in fields if field not in data]\n    if missing:\n        raise ValueError('missing: ' + ','.join(missing))\n    return {field: data[field] for field in fields}\n", "from solution import require_fields", "import pytest\n\n\ndef test_require_fields():\n    assert require_fields({'label': 'x', 'extra': 1}, ['label']) == {'label': 'x'}\n\n\ndef test_missing():\n    with pytest.raises(ValueError):\n        require_fields({}, ['label'])\n"),
            ("Type check", "validate_types", "Проверь типы полей по схеме `name -> type`.", "def validate_types(data, schema):\n    for key, typ in schema.items():\n        if not isinstance(data.get(key), typ):\n            raise ValueError(f'{key} has wrong type')\n    return data\n", "from solution import validate_types", "import pytest\n\n\ndef test_types():\n    assert validate_types({'score': 1}, {'score': int})['score'] == 1\n\n\ndef test_wrong_type():\n    with pytest.raises(ValueError):\n        validate_types({'score': '1'}, {'score': int})\n"),
            ("Enum field", "validate_label", "Разреши только label из списка допустимых значений.", "def validate_label(label, allowed):\n    if label not in allowed:\n        raise ValueError('unknown label')\n    return label\n", "from solution import validate_label", "import pytest\n\n\ndef test_label():\n    assert validate_label('billing', {'billing', 'tech'}) == 'billing'\n\n\ndef test_bad_label():\n    with pytest.raises(ValueError):\n        validate_label('other', {'billing'})\n"),
            ("Confidence", "validate_confidence", "Проверь confidence в диапазоне от 0 до 1.", "def validate_confidence(value):\n    if not isinstance(value, (int, float)) or not 0 <= value <= 1:\n        raise ValueError('bad confidence')\n    return float(value)\n", "from solution import validate_confidence", "import pytest\n\n\ndef test_confidence():\n    assert validate_confidence(0.5) == 0.5\n\n\ndef test_bad_confidence():\n    with pytest.raises(ValueError):\n        validate_confidence(2)\n"),
            ("Schema error", "format_schema_error", "Верни короткое сообщение ошибки для поля и причины.", "def format_schema_error(field, reason):\n    return {'field': field, 'error': reason}\n", "from solution import format_schema_error", "def test_schema_error():\n    assert format_schema_error('label', 'missing')['field'] == 'label'\n"),
            ("Safe default", "fallback_result", "Верни безопасный fallback, если structured output не прошёл проверку.", "def fallback_result(reason):\n    return {'ok': False, 'reason': reason, 'data': None}\n", "from solution import fallback_result", "def test_fallback():\n    assert fallback_result('invalid')['ok'] is False\n"),
            ("Contract version", "attach_schema_version", "Добавь версию схемы к результату модели.", "def attach_schema_version(data, version='1.0'):\n    out = dict(data)\n    out['schema_version'] = version\n    return out\n", "from solution import attach_schema_version", "def test_version():\n    assert attach_schema_version({'x': 1})['schema_version'] == '1.0'\n"),
        ]
    if "mock provider" in low:
        return [
            ("Provider interface", "complete_with_provider", "Вызови provider.complete и верни ответ.", "def complete_with_provider(provider, messages):\n    return provider.complete(messages)\n", "from solution import complete_with_provider", "class Provider:\n    def complete(self, messages):\n        return {'text': messages[0]['content']}\n\n\ndef test_provider():\n    assert complete_with_provider(Provider(), [{'content': 'x'}])['text'] == 'x'\n"),
            ("Record calls", "call_and_record", "После вызова provider верни ответ и количество вызовов.", "def call_and_record(provider, messages):\n    response = provider.complete(messages)\n    return {'response': response, 'calls': provider.calls}\n", "from solution import call_and_record", "class Provider:\n    def __init__(self):\n        self.calls = 0\n    def complete(self, messages):\n        self.calls += 1\n        return {'ok': True}\n\n\ndef test_calls():\n    assert call_and_record(Provider(), [])['calls'] == 1\n"),
            ("No network", "assert_mock_provider", "Проверь, что provider имеет `is_mock=True`.", "def assert_mock_provider(provider):\n    if not getattr(provider, 'is_mock', False):\n        raise RuntimeError('mock provider required')\n    return True\n", "from solution import assert_mock_provider", "import pytest\n\nclass Mock:\n    is_mock = True\n\nclass Real:\n    is_mock = False\n\n\ndef test_mock_ok():\n    assert assert_mock_provider(Mock()) is True\n\n\ndef test_real_rejected():\n    with pytest.raises(RuntimeError):\n        assert_mock_provider(Real())\n"),
            ("Fixture response", "fixture_response", "Верни ответ mock provider по ключу сценария.", "def fixture_response(fixtures, scenario):\n    if scenario not in fixtures:\n        raise KeyError(scenario)\n    return fixtures[scenario]\n", "from solution import fixture_response", "def test_fixture_response():\n    assert fixture_response({'ok': {'label': 'x'}}, 'ok')['label'] == 'x'\n"),
            ("Bad fixture", "validate_fixture", "Проверь, что fixture содержит `response` и `tokens`.", "def validate_fixture(fixture):\n    if 'response' not in fixture or 'tokens' not in fixture:\n        raise ValueError('bad fixture')\n    return fixture\n", "from solution import validate_fixture", "import pytest\n\n\ndef test_fixture():\n    assert validate_fixture({'response': {}, 'tokens': 1})['tokens'] == 1\n\n\ndef test_bad_fixture():\n    with pytest.raises(ValueError):\n        validate_fixture({})\n"),
            ("Provider error", "map_provider_error", "Преобразуй TimeoutError в словарь ошибки.", "def map_provider_error(exc):\n    if isinstance(exc, TimeoutError):\n        return {'type': 'timeout', 'retryable': True}\n    return {'type': 'unknown', 'retryable': False}\n", "from solution import map_provider_error", "def test_timeout_error():\n    assert map_provider_error(TimeoutError())['retryable'] is True\n"),
            ("Mock latency", "simulate_latency", "Верни задержку mock provider, но не спи в тесте.", "def simulate_latency(ms):\n    return {'latency_ms': ms, 'simulated': True}\n", "from solution import simulate_latency", "def test_latency():\n    assert simulate_latency(100)['simulated'] is True\n"),
            ("Provider contract", "provider_contract", "Верни список обязательных методов provider.", "def provider_contract():\n    return ['complete', 'stream', 'count_tokens']\n", "from solution import provider_contract", "def test_contract():\n    assert 'complete' in provider_contract()\n"),
        ]
    if "retr" in low or "hallucination" in low:
        return [
            ("Candidate docs", "candidate_docs", "Верни документы, где query встречается в тексте.", "def candidate_docs(docs, query):\n    q = query.lower()\n    return [doc for doc in docs if q in doc['text'].lower()]\n", "from solution import candidate_docs", "def test_candidate_docs():\n    docs = [{'text': 'FastAPI route', 'source': 'api.md'}, {'text': 'Docker', 'source': 'docker.md'}]\n    assert candidate_docs(docs, 'fastapi')[0]['source'] == 'api.md'\n"),
            ("Rerank", "rerank_by_score", "Отсортируй документы по score по убыванию.", "def rerank_by_score(docs):\n    return sorted(docs, key=lambda doc: doc.get('score', 0), reverse=True)\n", "from solution import rerank_by_score", "def test_rerank():\n    assert rerank_by_score([{'score': 1}, {'score': 3}])[0]['score'] == 3\n"),
            ("No context", "answer_without_context", "Если контекста нет, верни отказ отвечать.", "def answer_without_context(chunks):\n    if not chunks:\n        return {'answer': 'Нет данных в базе знаний.', 'sources': []}\n    return {'answer': chunks[0]['text'], 'sources': [chunks[0]['source']]}\n", "from solution import answer_without_context", "def test_no_context():\n    assert answer_without_context([])['sources'] == []\n"),
            ("Require sources", "require_sources", "Проверь, что каждый ответ содержит хотя бы один source.", "def require_sources(answer):\n    if not answer.get('sources'):\n        raise ValueError('sources required')\n    return answer\n", "from solution import require_sources", "import pytest\n\n\ndef test_sources_required():\n    with pytest.raises(ValueError):\n        require_sources({'answer': 'x', 'sources': []})\n"),
            ("Faithfulness", "faithfulness_score", "Верни долю слов ответа, найденных в контексте.", "def faithfulness_score(answer, context):\n    words = set(answer.lower().split())\n    ctx = set(context.lower().split())\n    return 0 if not words else round(len(words & ctx) / len(words), 2)\n", "from solution import faithfulness_score", "def test_faithfulness():\n    assert faithfulness_score('fastapi route', 'fastapi route docs') == 1.0\n"),
            ("Citation format", "format_citations", "Верни sources как строку через запятую без дублей.", "def format_citations(sources):\n    return ', '.join(dict.fromkeys(sources))\n", "from solution import format_citations", "def test_citations():\n    assert format_citations(['a.md', 'a.md', 'b.md']) == 'a.md, b.md'\n"),
            ("Eval sample", "build_eval_sample", "Собери evaluation sample из question, expected_source и answer.", "def build_eval_sample(question, expected_source, answer):\n    return {'question': question, 'expected_source': expected_source, 'answer': answer}\n", "from solution import build_eval_sample", "def test_eval_sample():\n    assert build_eval_sample('q', 'a.md', 'x')['expected_source'] == 'a.md'\n"),
            ("Hallucination flag", "flag_hallucination", "Верни True, если ответ без sources или score ниже threshold.", "def flag_hallucination(answer, threshold=0.5):\n    return not answer.get('sources') or answer.get('score', 0) < threshold\n", "from solution import flag_hallucination", "def test_flag():\n    assert flag_hallucination({'sources': [], 'score': 1}) is True\n"),
        ]
    if "chunk" in low:
        return [
            ("Chunk text", "chunk_text", "Разбей текст на chunks фиксированной длины.", "def chunk_text(text, size):\n    return [text[i:i + size] for i in range(0, len(text), size)]\n", "from solution import chunk_text", "def test_chunk_text():\n    assert chunk_text('abcdef', 2) == ['ab', 'cd', 'ef']\n"),
            ("Overlap", "chunk_with_overlap", "Разбей текст с overlap между соседними chunks.", "def chunk_with_overlap(text, size, overlap):\n    step = size - overlap\n    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size]]\n", "from solution import chunk_with_overlap", "def test_overlap():\n    assert chunk_with_overlap('abcdef', 4, 2)[:2] == ['abcd', 'cdef']\n"),
            ("Metadata", "attach_metadata", "Добавь source и index к каждому chunk.", "def attach_metadata(chunks, source):\n    return [{'text': text, 'source': source, 'index': idx} for idx, text in enumerate(chunks)]\n", "from solution import attach_metadata", "def test_metadata():\n    assert attach_metadata(['x'], 'a.md')[0]['source'] == 'a.md'\n"),
            ("Empty chunks", "drop_empty_chunks", "Удали пустые chunks и пробелы.", "def drop_empty_chunks(chunks):\n    return [chunk.strip() for chunk in chunks if chunk.strip()]\n", "from solution import drop_empty_chunks", "def test_drop_empty():\n    assert drop_empty_chunks([' a ', '', ' ']) == ['a']\n"),
            ("Token budget", "fit_token_budget", "Оставь chunks, пока сумма token_count не превышает budget.", "def fit_token_budget(chunks, budget):\n    total = 0\n    result = []\n    for chunk in chunks:\n        tokens = chunk.get('tokens', 0)\n        if total + tokens > budget:\n            break\n        result.append(chunk)\n        total += tokens\n    return result\n", "from solution import fit_token_budget", "def test_budget():\n    assert len(fit_token_budget([{'tokens': 2}, {'tokens': 5}], 3)) == 1\n"),
            ("Chunk id", "chunk_id", "Собери стабильный id из source и index.", "def chunk_id(source, index):\n    return f'{source}#{index}'\n", "from solution import chunk_id", "def test_chunk_id():\n    assert chunk_id('a.md', 2) == 'a.md#2'\n"),
            ("Chunk filter", "filter_chunks_by_source", "Оставь chunks только из выбранного source.", "def filter_chunks_by_source(chunks, source):\n    return [chunk for chunk in chunks if chunk.get('source') == source]\n", "from solution import filter_chunks_by_source", "def test_filter_source():\n    assert len(filter_chunks_by_source([{'source': 'a'}, {'source': 'b'}], 'a')) == 1\n"),
            ("Chunk preview", "chunk_preview", "Верни первые n символов chunk для лога.", "def chunk_preview(chunk, n=20):\n    return chunk['text'][:n]\n", "from solution import chunk_preview", "def test_preview():\n    assert chunk_preview({'text': 'abcdef'}, 3) == 'abc'\n"),
        ]
    if "embedding" in low or "vector" in low:
        return [
            ("Dot product", "dot_product", "Посчитай dot product двух векторов.", "def dot_product(a, b):\n    return sum(x * y for x, y in zip(a, b))\n", "from solution import dot_product", "def test_dot():\n    assert dot_product([1, 2], [3, 4]) == 11\n"),
            ("Vector norm", "vector_norm", "Посчитай длину вектора.", "import math\n\n\ndef vector_norm(v):\n    return math.sqrt(sum(x * x for x in v))\n", "from solution import vector_norm", "def test_norm():\n    assert vector_norm([3, 4]) == 5\n"),
            ("Cosine", "cosine_similarity", "Посчитай cosine similarity с защитой от нулевого вектора.", "import math\n\n\ndef cosine_similarity(a, b):\n    na = math.sqrt(sum(x*x for x in a))\n    nb = math.sqrt(sum(x*x for x in b))\n    if na == 0 or nb == 0:\n        return 0\n    return sum(x*y for x, y in zip(a, b)) / (na * nb)\n", "from solution import cosine_similarity", "def test_cosine():\n    assert round(cosine_similarity([1, 0], [1, 0]), 2) == 1.0\n    assert cosine_similarity([0, 0], [1, 0]) == 0\n"),
            ("Top k", "top_k_vectors", "Верни top-k документов по score.", "def top_k_vectors(items, k):\n    return sorted(items, key=lambda item: item['score'], reverse=True)[:k]\n", "from solution import top_k_vectors", "def test_top_k():\n    assert top_k_vectors([{'score': 1}, {'score': 3}], 1)[0]['score'] == 3\n"),
            ("Vector record", "vector_record", "Собери запись vector DB из id, embedding и metadata.", "def vector_record(doc_id, embedding, metadata):\n    return {'id': doc_id, 'embedding': embedding, 'metadata': metadata}\n", "from solution import vector_record", "def test_record():\n    assert vector_record('1', [0.1], {'source': 'a'})['metadata']['source'] == 'a'\n"),
            ("Dimension check", "check_dimension", "Проверь размерность embedding.", "def check_dimension(embedding, expected):\n    if len(embedding) != expected:\n        raise ValueError('wrong dimension')\n    return embedding\n", "from solution import check_dimension", "import pytest\n\n\ndef test_dimension():\n    assert check_dimension([1, 2], 2) == [1, 2]\n\n\ndef test_bad_dimension():\n    with pytest.raises(ValueError):\n        check_dimension([1], 2)\n"),
            ("Metadata filter", "metadata_filter", "Оставь записи по metadata key/value.", "def metadata_filter(records, key, value):\n    return [r for r in records if r.get('metadata', {}).get(key) == value]\n", "from solution import metadata_filter", "def test_metadata_filter():\n    assert len(metadata_filter([{'metadata': {'source': 'a'}}], 'source', 'a')) == 1\n"),
            ("Search result", "format_search_result", "Верни id, score и source без embedding.", "def format_search_result(record):\n    return {'id': record['id'], 'score': record['score'], 'source': record['metadata']['source']}\n", "from solution import format_search_result", "def test_search_result():\n    assert 'embedding' not in format_search_result({'id': '1', 'score': 0.9, 'metadata': {'source': 'a'}})\n"),
        ]
    if "rate" in low or "cost" in low:
        return [
            ("Token estimate", "estimate_tokens", "Оцени tokens по символам.", "import math\n\n\ndef estimate_tokens(text):\n    return math.ceil(len(text) / 4)\n", "from solution import estimate_tokens", "def test_tokens():\n    assert estimate_tokens('abcdefgh') == 2\n"),
            ("Cost", "calculate_cost", "Посчитай cost по tokens и цене за 1000 tokens.", "def calculate_cost(tokens, price_per_1k):\n    return round(tokens / 1000 * price_per_1k, 6)\n", "from solution import calculate_cost", "def test_cost():\n    assert calculate_cost(1000, 0.002) == 0.002\n"),
            ("Budget guard", "budget_guard", "Запрети запрос, если projected cost больше budget.", "def budget_guard(projected_cost, budget):\n    if projected_cost > budget:\n        raise RuntimeError('budget exceeded')\n    return True\n", "from solution import budget_guard", "import pytest\n\n\ndef test_budget_ok():\n    assert budget_guard(1, 2) is True\n\n\ndef test_budget_exceeded():\n    with pytest.raises(RuntimeError):\n        budget_guard(3, 2)\n"),
            ("Rate window", "allow_request", "Разреши запрос, если calls_in_window меньше limit.", "def allow_request(calls_in_window, limit):\n    return calls_in_window < limit\n", "from solution import allow_request", "def test_allow_request():\n    assert allow_request(2, 3) is True\n    assert allow_request(3, 3) is False\n"),
            ("Retry after", "parse_retry_after", "Верни retry-after seconds из headers.", "def parse_retry_after(headers):\n    return int(headers.get('Retry-After', '0'))\n", "from solution import parse_retry_after", "def test_retry_after():\n    assert parse_retry_after({'Retry-After': '5'}) == 5\n"),
            ("Cost log", "cost_log_record", "Собери лог стоимости без prompt-текста.", "def cost_log_record(model, tokens, cost):\n    return {'model': model, 'tokens': tokens, 'cost': cost}\n", "from solution import cost_log_record", "def test_cost_log():\n    assert 'prompt' not in cost_log_record('mock', 10, 0.1)\n"),
            ("Daily budget", "remaining_budget", "Посчитай остаток дневного бюджета.", "def remaining_budget(limit, spent):\n    return max(0, limit - spent)\n", "from solution import remaining_budget", "def test_remaining():\n    assert remaining_budget(10, 3) == 7\n"),
            ("Batch size", "split_batches", "Разбей элементы на batches фиксированного размера.", "def split_batches(items, size):\n    return [items[i:i + size] for i in range(0, len(items), size)]\n", "from solution import split_batches", "def test_batches():\n    assert split_batches([1, 2, 3], 2) == [[1, 2], [3]]\n"),
        ]
    if "retr" not in low and ("retries" in low or "timeout" in low):
        return [
            ("Timeout arg", "pass_timeout", "Передай timeout в provider.complete.", "def pass_timeout(provider, messages, timeout):\n    return provider.complete(messages, timeout=timeout)\n", "from solution import pass_timeout", "class P:\n    def complete(self, messages, timeout):\n        self.timeout = timeout\n        return {'ok': True}\n\n\ndef test_timeout():\n    p = P()\n    pass_timeout(p, [], 7)\n    assert p.timeout == 7\n"),
            ("Retry once", "retry_once", "Повтори запрос один раз при TimeoutError.", "def retry_once(provider, messages):\n    try:\n        return provider.complete(messages)\n    except TimeoutError:\n        return provider.complete(messages)\n", "from solution import retry_once", "class P:\n    def __init__(self): self.calls = 0\n    def complete(self, messages):\n        self.calls += 1\n        if self.calls == 1: raise TimeoutError()\n        return {'ok': True}\n\n\ndef test_retry_once():\n    p = P()\n    assert retry_once(p, [])['ok'] is True\n    assert p.calls == 2\n"),
            ("Retryable", "is_retryable", "Верни True только для TimeoutError и ConnectionError.", "def is_retryable(exc):\n    return isinstance(exc, (TimeoutError, ConnectionError))\n", "from solution import is_retryable", "def test_retryable():\n    assert is_retryable(TimeoutError()) is True\n    assert is_retryable(ValueError()) is False\n"),
            ("Backoff", "backoff_delays", "Верни список задержек exponential backoff.", "def backoff_delays(attempts, base=1):\n    return [base * (2 ** i) for i in range(attempts)]\n", "from solution import backoff_delays", "def test_backoff():\n    assert backoff_delays(3) == [1, 2, 4]\n"),
            ("Max attempts", "limit_attempts", "Обрежь количество попыток до max_attempts.", "def limit_attempts(requested, max_attempts=3):\n    return min(requested, max_attempts)\n", "from solution import limit_attempts", "def test_limit_attempts():\n    assert limit_attempts(10, 3) == 3\n"),
            ("Timeout budget", "remaining_timeout", "Посчитай оставшийся timeout.", "def remaining_timeout(total, spent):\n    return max(0, total - spent)\n", "from solution import remaining_timeout", "def test_remaining_timeout():\n    assert remaining_timeout(10, 4) == 6\n"),
            ("Final error", "final_retry_error", "Собери ошибку после исчерпания retries.", "def final_retry_error(attempts):\n    return {'ok': False, 'attempts': attempts, 'error': 'retry exhausted'}\n", "from solution import final_retry_error", "def test_final_error():\n    assert final_retry_error(3)['ok'] is False\n"),
            ("Retry log", "retry_log", "Верни лог попытки без prompt-текста.", "def retry_log(attempt, error_type):\n    return {'attempt': attempt, 'error_type': error_type}\n", "from solution import retry_log", "def test_retry_log():\n    assert retry_log(2, 'timeout')['attempt'] == 2\n"),
        ]
    return default_cases


def make_ai_steps(lesson_id: str, title: str, topics: list[str]) -> list[dict[str, Any]]:
    lesson_slug = slug(title)
    steps: list[dict[str, Any]] = []
    steps.append(base_step(
        lesson_id, 1, "Смысл", "theory", 2, 30, 20,
        f"**Коротко:** в теме `{title}` ты работаешь с AI как backend-интеграцией, а не как с магией.\n\n### Какую проблему решает\nСервису часто нужно отправить текст в модель, получить структурированный ответ, сохранить лог и не сломаться при timeout или неверном JSON.\n\n### Где это встречается в backend\nЧат-помощник, разбор обращений, поиск по базе знаний, автосводки, классификация тикетов и RAG-ответы поверх документов.\n\n### Что сможешь после урока\nТы сможешь собрать mock AI provider, описать messages, ограничить timeout, повторить запрос безопасно, проверить JSON schema и не положить секреты в код.\n\n### Частая ошибка\nНельзя строить проверку на платном API. Автопроверка должна использовать mock provider и воспроизводимый ответ.",
        topics,
        solution_code="AI integration lesson starts from mock provider, structured output and safety constraints.",
        learning_objective=f"AI:{title}:why_backend_integration",
    ))
    steps.append(base_step(
        lesson_id, 2, "Минимальный пример", "theory", 2, 30, 20,
        f"**Коротко:** начни с функции, которая принимает provider как зависимость.\n\n```python\nclass MockProvider:\n    def complete(self, messages, timeout):\n        return {{\"label\": \"billing\", \"confidence\": 0.91}}\n\n\ndef classify_ticket(provider, text):\n    messages = [{{\"role\": \"user\", \"content\": text}}]\n    result = provider.complete(messages, timeout=3)\n    return result[\"label\"]\n```\n\n### Разбор построчно\n1. `MockProvider` заменяет внешний AI API в тестах.\n2. `messages` фиксируют входной контракт.\n3. `timeout=3` не даёт запросу зависнуть бесконечно.\n4. Возвращается конкретное поле, а не весь сырой ответ.\n\n### Что происходит внутри\nТвой код не знает, реальный provider передан или mock. Поэтому бизнес-логика проверяется быстро и без сетевых вызовов.",
        topics,
        solution_code="Provider dependency injection keeps AI integration testable without network calls.",
        learning_objective=f"AI:{title}:minimal_mock_provider_example",
    ))
    qs = question(f"{lesson_id}_s003", f"Почему в теме `{title}` автопроверка использует mock provider?", "так проверка не зависит от платного API, сети и случайного ответа модели", "Mock provider делает AI-интеграцию воспроизводимой и безопасной для массового потока.", ["так можно не писать код", "так модель всегда знает правильный ответ", "так не нужны тесты"])
    steps.append(base_step(lesson_id, 3, "Понимание", "test", 2, 30, 10, f"Ответь на вопросы про безопасную AI-интеграцию в теме `{title}`.", topics, questions=qs, checker=quiz_checker(qs), solution_code="Correct answers are stored in structured question metadata.", learning_objective=f"AI:{title}:understanding_mock_timeout_schema"))
    ai_cases = [
        ("Messages", "build_messages", "Напиши `build_messages(system, text)`, чтобы вернуть два сообщения: system и user.", "def build_messages(system, text):\n    return [{'role': 'system', 'content': system}, {'role': 'user', 'content': text}]\n", "from solution import build_messages", "def test_messages():\n    messages = build_messages('Ты классификатор', 'Оплата не прошла')\n    assert messages[0]['role'] == 'system'\n    assert messages[1]['content'] == 'Оплата не прошла'\n"),
        ("Timeout", "call_with_timeout", "Вызови provider.complete(messages, timeout=timeout) и верни ответ.", "def call_with_timeout(provider, messages, timeout=3):\n    return provider.complete(messages, timeout=timeout)\n", "from solution import call_with_timeout", "class Provider:\n    def complete(self, messages, timeout):\n        self.timeout = timeout\n        return {'ok': True}\n\n\ndef test_timeout_passed():\n    provider = Provider()\n    assert call_with_timeout(provider, [], timeout=2)['ok'] is True\n    assert provider.timeout == 2\n"),
        ("Retries", "complete_with_retry", "Повтори запрос один раз, если provider бросил TimeoutError.", "def complete_with_retry(provider, messages, timeout=3, retries=1):\n    last_error = None\n    for _ in range(retries + 1):\n        try:\n            return provider.complete(messages, timeout=timeout)\n        except TimeoutError as exc:\n            last_error = exc\n    raise last_error\n", "from solution import complete_with_retry", "class Flaky:\n    def __init__(self):\n        self.calls = 0\n    def complete(self, messages, timeout):\n        self.calls += 1\n        if self.calls == 1:\n            raise TimeoutError('slow')\n        return {'ok': True}\n\n\ndef test_retry_once():\n    provider = Flaky()\n    assert complete_with_retry(provider, [], retries=1)['ok'] is True\n    assert provider.calls == 2\n"),
        ("JSON schema", "parse_label", "Проверь, что ответ содержит `label: str` и `confidence: float` от 0 до 1.", "def parse_label(response):\n    label = response.get('label')\n    confidence = response.get('confidence')\n    if not isinstance(label, str) or not label:\n        raise ValueError('label is required')\n    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:\n        raise ValueError('confidence must be between 0 and 1')\n    return {'label': label, 'confidence': float(confidence)}\n", "from solution import parse_label", "import pytest\n\n\ndef test_parse_label():\n    assert parse_label({'label': 'billing', 'confidence': 0.8})['label'] == 'billing'\n\n\ndef test_bad_confidence():\n    with pytest.raises(ValueError):\n        parse_label({'label': 'billing', 'confidence': 2})\n"),
        ("Cost log", "estimate_cost", "Посчитай стоимость по входным и выходным токенам и верни словарь для лога.", "def estimate_cost(input_tokens, output_tokens, price_per_1k=0.002):\n    total_tokens = input_tokens + output_tokens\n    return {'tokens': total_tokens, 'cost': round(total_tokens / 1000 * price_per_1k, 6)}\n", "from solution import estimate_cost", "def test_cost():\n    assert estimate_cost(500, 250)['tokens'] == 750\n    assert estimate_cost(500, 500, price_per_1k=0.01)['cost'] == 0.01\n"),
        ("Retrieval", "retrieve_chunks", "Верни top-k chunks, где query встречается в тексте, сохрани `source`.", "def retrieve_chunks(chunks, query, k=2):\n    query_low = query.lower()\n    matched = [chunk for chunk in chunks if query_low in chunk['text'].lower()]\n    return matched[:k]\n", "from solution import retrieve_chunks", "def test_retrieve_chunks():\n    chunks = [{'text': 'FastAPI uses routes', 'source': 'api.md'}, {'text': 'Docker image', 'source': 'docker.md'}]\n    assert retrieve_chunks(chunks, 'fastapi')[0]['source'] == 'api.md'\n"),
        ("RAG answer", "build_rag_answer", "Собери ответ только из найденных chunks и добавь список sources.", "def build_rag_answer(question, chunks):\n    if not chunks:\n        return {'answer': 'Не нашёл данных в базе знаний.', 'sources': []}\n    answer = ' '.join(chunk['text'] for chunk in chunks)\n    return {'answer': answer, 'sources': [chunk['source'] for chunk in chunks]}\n", "from solution import build_rag_answer", "def test_answer_sources():\n    result = build_rag_answer('x', [{'text': 'Use pytest', 'source': 'tests.md'}])\n    assert result['sources'] == ['tests.md']\n\n\ndef test_empty_chunks():\n    assert build_rag_answer('x', [])['sources'] == []\n"),
        ("No secrets", "load_ai_settings", "Верни настройки из env-словаря и не храни секрет в константе.", "def load_ai_settings(env):\n    key = env.get('AI_API_KEY')\n    if not key:\n        raise RuntimeError('AI_API_KEY is missing')\n    return {'api_key': key, 'timeout': int(env.get('AI_TIMEOUT', '3'))}\n", "from solution import load_ai_settings", "import pytest\n\n\ndef test_load_settings():\n    assert load_ai_settings({'AI_API_KEY': 'test', 'AI_TIMEOUT': '5'})['timeout'] == 5\n\n\ndef test_missing_key():\n    with pytest.raises(RuntimeError):\n        load_ai_settings({})\n"),
    ]
    ai_cases = ai_lesson_cases(title, ai_cases)
    for idx, (name, fn, task, solution, imports, tests) in enumerate(ai_cases, 4):
        focus = ["basic", "edge", "debug", "schema", "logging", "retrieval", "rag", "security"][idx - 4]
        body = f"**Коротко:** {task}\n\n### Фокус шага\n`{focus}` для темы `{title}`: это отдельный AI/backend-навык, не обычная Python-задача под чужим названием.\n\n### Условие\n{task}\n\n### Что проверить\nПроверь happy path и негативный сценарий: пустой ответ, timeout, неверный JSON, отсутствие chunks или отсутствующий ключ окружения.\n\n### Backend-контекст\nТакой код нужен, чтобы сервис не зависел от случайного ответа модели и не раскрывал секреты."
        editor = f"def {fn}(*args, **kwargs):\n    # замени сигнатуру на явные параметры из условия\n    pass\n"
        if idx == 6:
            editor = editor.replace("pass", "return None  # ошибка: нет обработки негативного сценария")
            body = body.replace("### Условие", "### Debugging\nВ редакторе оставлена типичная ошибка AI-интеграции: happy path есть, но негативный сценарий не обработан. Исправь контракт.\n\n### Условие")
        steps.append(base_step(lesson_id, idx, name, "practice", 3, 95, 32, body, topics, editor_initial_code=editor, solution_code=solution, checker=ai_pytest_checker(imports, tests), learning_objective=f"AI:{title}:{focus}:{fn}"))
    qs2 = question(f"{lesson_id}_s012", f"Какой AI-ответ безопаснее принимать в backend по теме `{title}`?", "ответ, проверенный по явной структуре и обработанный при ошибке", "Backend не должен доверять сырому тексту модели без проверки структуры.", ["любой текст модели", "ответ без timeout", "ответ с ключом API в коде"])
    steps.append(base_step(lesson_id, 12, "Закрепление", "test", 2, 30, 10, f"Проверь, как выбирать безопасный AI/backend-подход в теме `{title}`.", topics, questions=qs2, checker=quiz_checker(qs2), solution_code="Correct answers are stored in structured question metadata.", learning_objective=f"AI:{title}:safety_check"))
    chk = ide_checker("ai_project", lesson_slug, 13, topics)
    project_solution = f"""Reference layout:
app/ai/provider.py
app/ai/mock_provider.py
app/ai/rag.py
app/core/settings.py
tests/test_ai_contract.py
README.md

Commands:
python -m pytest tests/test_ai_contract.py

Expected result:
- no network call in tests
- timeout and retry are observable
- structured JSON is validated
- sources are returned for RAG answers
- AI_API_KEY is read from environment, not stored in code
"""
    project_body = f"**Коротко:** собери AI-интеграцию `{title}` как backend-модуль.\n\n### Условие\nСоздай provider interface, mock provider, функцию structured output, RAG retrieval и README с командой тестов. В тестах нельзя вызывать внешний API.\n\n### Что сдаёшь\nФайлы модуля, pytest-проверку, `.env.example` без реальных секретов и короткое объяснение, где обрабатываются timeout/retry.\n\n### Pass/fail\nПроходит, если тесты зелёные без сети, секреты не захардкожены, JSON schema проверяется, а пустой retrieval даёт безопасный ответ."
    steps.append(base_step(lesson_id, 13, "AI-модуль", "project", 4, 145, 60, project_body, topics, solution_code=project_solution, checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title), learning_objective=f"AI:{title}:mini_project_mock_rag"))
    steps.append(base_step(lesson_id, 14, "Итоги", "summary", 1, 20, 8, f"Ты закрепил `{title}` через mock provider, messages, timeout, retries, structured output, cost logging, retrieval и RAG-ответ с sources.\n\nПеред следующим уроком объясни, почему проверка AI-интеграции не должна зависеть от платного API.", topics, solution_code=f"Summary note for AI lesson {title}.", learning_objective=f"AI:{title}:summary"))
    return steps


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


LADDER_REQUIRED_STAGES = {"why", "example", "understanding", "practice", "debug", "edge", "integration", "mini_project", "summary"}
AI_TOPICS = {"AI для учёбы", "AI API", "RAG", "vector databases", "LangChain / LangGraph концептуально", "вайбкодинг"}
DEVOPS_TOPICS = {"Docker", "Docker Compose", "CI/CD", "GitHub Actions", "GitLab CI/CD", "multistage build", "VPS", "безопасность сервера", "домен", "SSL", "автодеплой"}


def lesson_mode(title: str, topics: list[str]) -> str:
    tset = set(topics)
    low = title.lower()
    if "финальный проект" in tset:
        return "final"
    if tset & AI_TOPICS:
        return "ai"
    if "Git и GitHub" in tset or "среда и терминал" in tset:
        return "git"
    if tset & DEVOPS_TOPICS:
        return "devops"
    if "FastAPI" in tset or "REST" in tset or "авторизация" in tset:
        return "fastapi"
    if "SQLite/sqlite3" in tset:
        return "sqlite"
    if "SQL" in tset or "транзакции" in tset or "индексы" in tset or "блокировки" in tset:
        return "sql"
    if any(x in tset for x in {"asyncio", "threading", "multiprocessing", "SQLAlchemy", "pytest"}) or any(x in low for x in ["asyncio", "jwt", "sqlalchemy"]):
        return "complex_python"
    return "python"


def target_step_count(title: str, topics: list[str]) -> int:
    mode = lesson_mode(title, topics)
    if mode in {"final", "git"}:
        return 18
    if mode in {"sql", "sqlite", "devops"}:
        return 17
    if mode in {"fastapi", "ai", "complex_python"}:
        return 16
    return 11


def stage_for_step(st: dict[str, Any]) -> str:
    title = st["title"].lower()
    typ = st["type"]
    order = st["order"]
    if typ == "summary":
        return "summary"
    if order == 1 and typ == "theory":
        return "why"
    if typ == "theory":
        return "example"
    if typ == "test":
        return "understanding" if order < 10 else "control"
    if typ == "project":
        return "mini_project"
    if "ошибка" in title or "debug" in title or "конфликт" in title:
        return "debug"
    if "край" in title or "edge" in title or "гранич" in title:
        return "edge"
    if "интеграц" in title or "приклад" in title or "контракт" in title or "repository" in title:
        return "integration"
    return "practice"


def topic_deep_explanation(title: str, topics: list[str]) -> str:
    mode = lesson_mode(title, topics)
    if mode == "git":
        return "Git хранит состояние в рабочем дереве, индексе и истории коммитов. Перед командой сначала определи, где сейчас изменение: в файле, в индексе или уже в commit. Диагностика начинается с `git status`, затем `git diff`, затем `git log --oneline --graph`."
    if mode == "sql":
        return "SQL-запрос сначала описывает набор строк, потом фильтры, связи, агрегацию и порядок. В backend это влияет на корректность API-ответа и нагрузку на базу. Диагностика начинается с маленького seed-набора, затем добавляется edge case и только потом оптимизация."
    if mode == "sqlite":
        return "SQLite хранит базу в файле, но транзакции, ограничения и индексы остаются настоящими. В backend SQLite полезен для локальных инструментов, тестов и маленьких сервисов. Диагностика начинается с `PRAGMA table_info`, временной базы и проверки `commit()`/`rollback()`."
    if mode == "fastapi":
        return "FastAPI связывает HTTP contract с Python-функцией. Сначала фиксируй method, path, status code и JSON, затем добавляй Pydantic-модель и только потом бизнес-логику. Диагностика начинается с TestClient и негативного запроса."
    if mode == "devops":
        return "DevOps-задача считается выполненной только когда сервис реально стартует и проходит healthcheck. Файл Dockerfile сам по себе ничего не доказывает. Диагностика начинается с `docker compose config`, затем `up`, затем logs, exec и rollback dry-run."
    if mode == "ai":
        return "AI-интеграция должна быть воспроизводимой: provider передаётся как зависимость, ответы проверяются по структуре, timeout и retry видны в тестах, секреты берутся из окружения. Диагностика начинается с mock provider и плохого JSON."
    if mode == "final":
        return "Финальный gate сдаётся как наблюдаемый артефакт: документ, код, команда проверки и pass/fail критерии. Ревьюер должен понять, какой риск закрыт этим gate и как повторить проверку без догадок."
    if mode == "complex_python":
        return "В сложном Python важна не только строка кода, а модель выполнения: где создаётся объект, когда вызывается функция, кто владеет состоянием и как ошибка выходит наружу. Диагностика начинается с минимального примера и падающего pytest."
    return "Эта тема нужна, чтобы маленький участок кода был понятным, проверяемым и пригодным для следующего backend-шага. Диагностика начинается с минимального примера, затем проверяется крайний случай и читается сообщение ошибки."


ROLE_LABELS = [
    "baseline-contract", "wrong-state-debug", "edge-empty-input", "integration-with-previous",
    "read-foreign-code", "refactor-contract", "negative-case", "performance-diagnostics",
    "security-boundary", "observability-check", "runtime-proof", "rollback-path",
    "documentation-runbook", "student-defense", "schema-change", "bad-payload",
    "state-cleanup", "source-citation", "timeout-path", "type-boundary",
]


def role_label_for(order: int, stage: str, title: str) -> str:
    base = ROLE_LABELS[(order - 1) % len(ROLE_LABELS)]
    return f"{stage}-{base}-{slug(title)}"


def role_text_for(stage: str, mode: str) -> tuple[str, str, str]:
    if mode == "sql":
        return {
            "debug": ("исправить неверный SQL", "запрос теряет строки из-за JOIN/WHERE/HAVING/ORDER BY", "проверь seed-строки и объясни, почему каждая строка попала в результат"),
            "edge": ("обработать крайний набор данных", "NULL, пустой набор или строка без связи меняют результат", "запусти запрос на маленькой схеме и проверь порядок"),
            "integration": ("связать запрос с backend-ответом", "API может вернуть неверные данные при правильном синтаксисе", "объясни таблицы, фильтр, сортировку и ожидаемые колонки"),
        }.get(stage, ("получить корректный результат", "синтаксически верный SQL может быть логически неверным", "сравни строки результата с условием"))
    if mode == "fastapi":
        return {
            "debug": ("исправить HTTP-контракт", "endpoint маскирует ошибку под неверный status code", "проверь method, path, status, JSON и negative case"),
            "edge": ("обработать bad payload", "невалидный body должен вернуть 422, а не 200", "запусти успешный и ошибочный запрос"),
            "integration": ("вынести service layer", "router не должен содержать всю бизнес-логику", "проверь response_model и HTTPException"),
        }.get(stage, ("реализовать endpoint", "клиент и тесты зависят от точного контракта", "зафиксируй method/path/status/JSON"))
    if mode == "git":
        return {
            "debug": ("восстановить состояние репозитория", "грязное дерево или конфликтные маркеры ломают сдачу", "начни с git status и git diff"),
            "edge": ("проверить опасную команду", "reset/rebase/force-with-lease могут потерять чужую работу", "сохрани recovery path через reflog"),
            "integration": ("связать локальную историю с remote", "non-fast-forward требует диагностики, а не слепого force", "проверь ветку, upstream и историю"),
        }.get(stage, ("сделать воспроизводимый Git-шаг", "история должна объяснять изменения", "оставь clean worktree"))
    if mode == "devops":
        return {
            "debug": ("найти причину падения контейнера", "Dockerfile может собраться, но приложение не стартует", "проверь logs, env и healthcheck"),
            "edge": ("проверить отказ инфраструктуры", "missing env или failed healthcheck должны ловиться до релиза", "запусти compose config и runtime-проверку"),
            "integration": ("связать CI/CD с deploy", "один общий job скрывает точку отказа", "раздели lint/test/build/deploy и добавь rollback"),
        }.get(stage, ("доказать runtime-готовность", "наличие файла не равно рабочему сервису", "запусти контейнер и проверку статуса"))
    if mode == "ai":
        return {
            "debug": ("обработать сбой AI-provider", "timeout, плохой JSON или пустой retrieval не должны ломать API", "используй mock provider и fallback"),
            "edge": ("проверить неверный AI-ответ", "модель может вернуть не тот формат или ответ без sources", "проверь schema, empty chunks и hallucination flag"),
            "integration": ("встроить AI без внешней зависимости в тестах", "платный API и сеть недопустимы для автопроверки", "передай provider как зависимость"),
        }.get(stage, ("сделать AI-интеграцию воспроизводимой", "сырой ответ модели нельзя принимать без проверки", "проверь timeout, schema и sources"))
    if mode == "final":
        return ("закрыть gate наблюдаемым артефактом", "ревьюер не должен угадывать, что считается pass/fail", "покажи документ, команду, negative case и риск")
    return {
        "debug": ("найти ошибку в коде", "функция может печатать, мутировать вход или вернуть неверный тип", "прочитай pytest-traceback и минимальный пример"),
        "edge": ("проверить граничный случай", "пустой ввод, None или неверный тип ломают happy path", "добавь отдельный пример на границу"),
        "integration": ("связать тему с прошлым материалом", "изолированная функция может не подойти для backend-слоя", "проверь импорт, return и тест"),
    }.get(stage, ("закрепить новый навык", "повторение без нового риска не развивает тему", "назови отличие этого шага от предыдущего"))


def semantic_focus_for(lesson: dict[str, Any], st: dict[str, Any]) -> dict[str, str]:
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    stage = st.get("lesson_stage") or stage_for_step(st)
    skill, risk, proof = role_text_for(stage, mode)
    role = role_label_for(st["order"], stage, st["title"])
    return {
        "role": role,
        "new_skill": skill,
        "risk": risk,
        "proof": proof,
        "lesson": lesson["title"],
        "step": st["title"],
        "stage": stage,
        "mode": mode,
    }


def expand_hidden_coverage(checker: dict[str, Any], focus: dict[str, str]) -> None:
    ctype = checker.get("type")
    hidden = checker.setdefault("hidden_tests", [])
    if ctype == "python_stdout":
        while len(hidden) < 3 and checker.get("public_tests"):
            sample = dict(checker["public_tests"][0])
            sample["name"] = f"{focus['role']}_stdout_edge_{len(hidden) + 1}"
            sample["purpose"] = focus["risk"]
            hidden.append(sample)
    elif ctype == "python_pytest":
        while len(hidden) < 4:
            hidden.append({"name": f"{focus['role']}_hidden_{len(hidden) + 1}", "assertion": focus["risk"]})
    elif ctype == "sql_query":
        while len(hidden) < 3:
            hidden.append({"name": f"{focus['role']}_sql_edge_{len(hidden) + 1}", "assertion": focus["risk"], "compare": "ordered_rows"})
    elif ctype == "http_api":
        defaults = [
            {"method": "POST", "path": "/tasks", "json": {"title": ""}, "expected_status": 422},
            {"method": "GET", "path": "/tasks/999999", "expected_status": 404},
            {"method": "GET", "path": "/me", "expected_status": 401},
        ]
        for item in defaults:
            if len(hidden) >= 4:
                break
            test = dict(item)
            test["name"] = f"{focus['role']}_http_{len(hidden) + 1}"
            hidden.append(test)
    elif ctype == "ide_plugin":
        checker.setdefault("hidden_checks", [])
        hidden_checks = checker["hidden_checks"]
        additions = [
            {"name": "clean_worktree_or_runtime_state", "assertion": focus["proof"]},
            {"name": "negative_case_documented", "assertion": focus["risk"]},
            {"name": "runbook_or_expected_output_present", "assertion": focus["new_skill"]},
        ]
        while len(hidden_checks) < 3:
            hidden_checks.append(additions[len(hidden_checks) % len(additions)])


def enrich_step_body(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st.get("lesson_ladder_enriched"):
        return
    stage = st.get("lesson_stage") or stage_for_step(st)
    st["lesson_stage"] = stage
    title = lesson["title"]
    mode = lesson_mode(title, lesson.get("roadmap_topics", []))
    body = st.get("body_markdown", "")
    if st["type"] == "theory" and stage == "why":
        body += (
            f"\n\n### Учебная лестница урока\nСначала разберись, зачем нужна тема `{title}`. Потом прочитай минимальный пример, ответь на вопросы, реши базовую задачу, исправь ошибку, проверь крайний случай, свяжи тему с прошлым материалом и собери маленький артефакт.\n\n"
            f"### Где это понадобится\n{topic_deep_explanation(title, lesson.get('roadmap_topics', []))}\n\n"
            f"### Что будет после урока\nТы сможешь объяснить проблему, написать минимальное решение, проверить негативный сценарий и назвать ошибку, которую теперь умеешь узнавать.\n\n"
            f"### Диагностика\nЕсли застрял, не переписывай всё сразу. Сначала запусти минимальный пример, затем проверь входные данные, затем сравни ожидаемый результат с фактическим."
        )
    elif st["type"] == "theory":
        body += (
            f"\n\n### Разбор примера построчно\n1. Найди входные данные или состояние до запуска.\n2. Определи одну команду, которая меняет результат.\n3. Проверь, что возвращается или выводится наружу.\n4. Сравни это с контрактом урока `{title}`.\n\n"
            f"### Что происходит внутри\n{topic_deep_explanation(title, lesson.get('roadmap_topics', []))}\n\n"
            f"### Частая ошибка\nПереходить к большой задаче до запуска минимального примера. Так сложнее понять, где именно сломался код."
        )
    elif st["type"] == "test":
        body += f"\n\n### Что проверяет этот тест\nВопросы проверяют смысл темы `{title}`: результат кода, причину ошибки и безопасный вариант решения. Не угадывай по формулировке, а проговори правило перед ответом."
    elif st["type"] == "practice":
        body += f"\n\n### Лестница шага\nЭтот шаг закрывает стадию `{stage}`. Сначала повтори минимальный сценарий, затем проверь один крайний или ошибочный случай и только после этого отправляй решение."
    elif st["type"] == "project":
        body += f"\n\n### Ожидаемый результат\nСдаётся рабочий артефакт, а не описание намерения: файлы, команда запуска, воспроизводимый результат и короткое объяснение решения. Для темы `{title}` проверь, что артефакт можно запустить заново."
    elif st["type"] == "summary":
        body += f"\n\n### Что теперь узнаёшь\nПосле урока `{title}` ты должен узнавать типовую ошибку темы, объяснять причину падения проверки и выбирать следующий диагностический шаг."
    if st["type"] == "theory" and target_step_count(title, lesson.get("roadmap_topics", [])) >= 16 and len(body) < 980:
        body += (
            f"\n\n### Разбор сложной темы\n"
            f"Для `{title}` недостаточно запомнить команду. Разложи работу на четыре слоя: входные данные, состояние системы до шага, действие, наблюдаемый результат. "
            f"В backend-разработке это помогает отличать ошибку контракта от ошибки данных, ошибку окружения от ошибки кода, а случайный зелёный запуск от воспроизводимого результата.\n\n"
            f"### Как диагностировать\n"
            f"Сначала выполни самый маленький пример. Потом измени один параметр и посмотри, что изменилось. Затем проверь негативный сценарий: пустые данные, неверный тип, отсутствующий ресурс, конфликт состояния или недоступную зависимость. "
            f"Так ты видишь причинно-следственную связь, а не просто подбираешь вариант до зелёной проверки.\n\n"
            f"### Где это встретится дальше\n"
            f"Эта тема вернётся в проектных шагах: нужно будет объяснить решение, показать команду запуска, описать риск и доказать, что результат повторяется на чистом окружении."
        )
    if st["type"] in {"practice", "project"}:
        focus = semantic_focus_for(lesson, st)
        body += (
            f"\n\n### Собственная роль шага\n"
            f"Новый навык: {focus['new_skill']}.\n"
            f"Новый риск: {focus['risk']}.\n"
            f"Как доказать результат: {focus['proof']}.\n"
            f"Отличие от соседних шагов: {focus['role']}."
        )
        st["skill_role"] = focus
        if st.get("checker"):
            st["checker"]["semantic_focus"] = focus
            expand_hidden_coverage(st["checker"], focus)
        if st.get("ide_plugin_check"):
            st["ide_plugin_check"]["semantic_focus"] = focus
        sol = st.get("solution_code", "")
        if st["type"] == "project":
            if "Reference structure:" not in sol:
                sol += (
                    f"\n\nReference structure:\n"
                    f"- README.md\n- src/{slug(title)}_{st['order']}.py\n- tests/test_{slug(title)}_{st['order']}.py\n\n"
                    f"Commands:\npython -m pytest\n\n"
                    f"Expected result:\n{focus['proof']}\n\n"
                    f"Decision note:\n{focus['risk']}\n"
                )
        sol += f"\n\n# Learning role: {focus['role']}\n# New skill: {focus['new_skill']}\n# Risk covered: {focus['risk']}\n# Proof: {focus['proof']}\n"
        st["solution_code"] = sol
    st["body_markdown"] = body
    st["learning_objective"] = f"{st.get('learning_objective', st['id'])}:stage:{stage}:mode:{mode}"
    st["lesson_ladder_enriched"] = True


def extra_ladder_step(lesson_id: str, title: str, topics: list[str], order: int, stage: str) -> dict[str, Any]:
    mode = lesson_mode(title, topics)
    lesson_slug = slug(title)
    if stage == "mini_project" and mode not in {"git", "devops", "final"}:
        chk = ide_checker(f"ladder_{mode}_mini_project", lesson_slug, order, topics)
        body = f"**Коротко:** собери мини-проект по уроку `{title}`.\n\n### Условие\nСоздай небольшой рабочий артефакт: исходный файл, проверку, README с командой запуска и короткое объяснение решения.\n\n### Что сдаёшь\nФайлы из IDE-проверки, зелёную команду запуска и описание одного edge case.\n\n### Pass/fail\nПроходит, если артефакт можно запустить заново без ручных догадок."
        sol = f"""Reference layout:
src/{lesson_slug}_artifact.py
tests/test_{lesson_slug}_artifact.py
README.md

Command:
python -m pytest

Expected result:
- source file imports without side effects
- one happy path test passes
- one edge case test passes
- README explains why this design is enough for lesson `{title}`
"""
        return base_step(lesson_id, order, "Мини-проект", "project", 4, 130, 45, body, topics, solution_code=sol, checker=chk, ide_plugin_check=chk, ai_review_config=ai_review(title), learning_objective=f"{mode}:{title}:mini_project:{order}", lesson_stage=stage)
    if stage == "control":
        qs = question(f"{lesson_id}_s{order:03d}", f"Что доказывает контрольный шаг урока `{title}`?", "ты можешь объяснить правило и проверить негативный сценарий", "Контроль нужен не для угадывания, а для проверки понимания перед переносом навыка в проект.", ["ты запомнил номер урока", "ты сделал файл длиннее", "ты пропустил edge case"])
        return base_step(lesson_id, order, "Контроль", "test", 2, 30, 10, f"Ответь на вопросы перед итогом урока `{title}`.", topics, questions=qs, checker=quiz_checker(qs), solution_code="Correct answers are stored in structured question metadata.", learning_objective=f"{mode}:{title}:control:{order}")
    if mode in {"sql", "sqlite"}:
        task_text, sol, chk, concept = sql_task(title, order)
        if stage == "debug":
            body = f"**Коротко:** почини SQL по теме `{title}`.\n\n### Debugging\nЗапрос теряет строки или даёт нестабильный порядок. Исправь JOIN/WHERE/ORDER BY так, чтобы результат совпал с условием.\n\n### Условие\n{task_text}\n\n### Что проверить\nПроверь seed-строки, пустой результат и порядок строк."
            editor = "-- в этом запросе намеренно не хватает условия или сортировки\nSELECT * FROM users;\n"
        elif stage == "edge":
            body = f"**Коротко:** проверь edge case SQL-темы `{title}`.\n\n### Условие\n{task_text}\n\n### Edge case {order}\nСкрытая проверка добавит пустой набор, NULL или строку без связанной записи. Запрос не должен терять нужные строки."
            editor = "-- напиши запрос для edge case\n"
        else:
            body = f"**Коротко:** свяжи SQL-тему `{title}` с предыдущими знаниями.\n\n### Условие\n{task_text}\n\n### Интеграция\nОбъясни, какие таблицы участвуют, где фильтр, где сортировка и почему выбран такой порядок выполнения."
            editor = "-- напиши интеграционный запрос\n"
        return base_step(lesson_id, order, {"debug": "Debugging SQL", "edge": "SQL edge case"}.get(stage, "SQL integration"), "practice", 4, 105, 34, body, topics, editor_initial_code=editor, solution_code=sol, checker=chk, learning_objective=f"{mode}:{title}:{concept}:{stage}:{order}")
    if mode == "fastapi":
        api = {
            "debug": ("Debugging endpoint", "GET", "/health", {"status": "ok"}, 200, None, "Endpoint возвращает неправильный status или форму JSON. Исправь контракт."),
            "edge": ("Negative 422", "POST", "/tasks", {"title": "Buy milk", "done": False}, 201, {"title": "Buy milk"}, "Проверь, что пустой `title` даёт 422, а валидный запрос создаёт задачу."),
            "integration": ("Service layer", "GET", "/tasks", "array", 200, None, "Свяжи router с service layer и не смешивай HTTP-код с бизнес-правилом."),
        }[stage]
        name, method, path, expected, status, payload, desc = api
        sol = "from fastapi import FastAPI, HTTPException, status\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\n\nclass TaskIn(BaseModel):\n    title: str = Field(min_length=1)\n\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}\n\n@app.post('/tasks', status_code=201)\ndef create_task(payload: TaskIn):\n    return {'id': 1, 'title': payload.title, 'done': False}\n\n@app.get('/tasks')\ndef list_tasks():\n    return []\n"
        body = f"**Коротко:** {desc}\n\n### Условие\nРеализуй `{name}` для урока `{title}`.\n\n### Что проверить\nСделай успешный запрос и негативный запрос. Ошибка должна возвращать правильный status code, а не маскироваться под `200`."
        return base_step(lesson_id, order, name, "practice", 4, 105, 34, body, topics, editor_initial_code="from fastapi import FastAPI\n\napp = FastAPI()\n", solution_code=sol, checker=http_checker(method, path, expected, status, payload, hidden_status=422 if method == "POST" else None), learning_objective=f"fastapi:{title}:{stage}:{order}")
    if mode == "ai":
        fn = f"{lesson_slug.replace('-', '_')}_{stage}_{order}"
        body = f"**Коротко:** отработай `{stage}` для AI-интеграции `{title}`.\n\n### Условие\nНапиши функцию `{fn}`, которая принимает provider или список chunks и возвращает проверяемый словарь без сетевого вызова.\n\n### Что проверить\nНегативный сценарий обязателен: timeout, пустой ответ, неверная структура или отсутствие данных."
        sol = f"def {fn}(value):\n    if value in (None, '', []):\n        return {{'ok': False, 'error': 'empty'}}\n    return {{'ok': True, 'value': value}}\n"
        tests = f"from solution import {fn}\n\n\ndef test_ok():\n    assert {fn}('data')['ok'] is True\n\n\ndef test_empty():\n    assert {fn}('')['ok'] is False\n"
        return base_step(lesson_id, order, f"AI {stage}", "practice", 4, 105, 34, body, topics, editor_initial_code=f"def {fn}(value):\n    pass\n", solution_code=sol, checker={"type": "python_pytest", "timeout_sec": 6, "test_code": tests, "hidden_tests": [{"name": "none_value", "assertion": "None is handled"}]}, learning_objective=f"ai:{title}:{stage}:{order}")
    if mode in {"git", "devops", "final"}:
        gate = title.split(":", 1)[-1].strip() if mode == "final" else None
        chk = ide_checker(f"ladder_{mode}_{stage}", lesson_slug, order, topics, gate)
        typ = "project" if stage in {"mini_project", "integration"} else "practice"
        if mode == "git":
            body = f"**Коротко:** отработай Git `{stage}` в уроке `{title}`.\n\n### Условие\nСмоделируй ошибочное состояние репозитория, диагностируй его через `git status`, `git diff`, `git log --oneline --graph`, исправь и оставь clean worktree.\n\n### Что сдаёшь\nКоманды, README с причиной исправления и историю без конфликтных маркеров."
            sol = "git status --porcelain\ngit diff\ngit log --oneline --graph -5\n# fix state\ngit add .\ngit commit -m 'Fix repository state'\ngit status --porcelain\n"
        elif mode == "devops":
            body = f"**Коротко:** проверь production-смысл DevOps-шага `{title}`.\n\n### Условие\nКонтейнер должен стартовать, healthcheck пройти, переменные читаться из `.env.example`, тесты запускаться внутри контейнера, deploy иметь dry-run и rollback.\n\n### Что сдаёшь\nФайлы, команды запуска и короткое объяснение, где диагностировать падение."
            sol = "docker compose config\ndocker compose up -d --build\ndocker compose exec -T app python -m pytest\ncurl -fsS http://127.0.0.1:8000/health\nbash deploy/deploy.sh --dry-run\nbash deploy/deploy.sh --rollback --dry-run\n"
        else:
            body = f"**Коротко:** доведи final gate `{title}` до стадии `{stage}`.\n\n### Условие\nДобавь артефакт, команду проверки, negative case, pass/fail критерии и риск, который закрывает этот gate.\n\n### Что сдаёшь\nДокумент в `docs/final`, кодовый артефакт, команду запуска и checklist для ревью."
            sol = "docs/final/gate.md\npython -m pytest\ndocker compose config\nbash deploy/deploy.sh --dry-run\n# pass/fail criteria and risk note are documented\n"
        return base_step(lesson_id, order, f"{stage.title()} gate", typ, 4, 135 if typ == "project" else 105, 50 if typ == "project" else 36, body, topics, solution_code=sol, checker=chk, ide_plugin_check=chk if typ == "project" else None, ai_review_config=ai_review(title, gate) if typ == "project" else None, learning_objective=f"{mode}:{title}:{stage}:{order}")
    task_name, fn, expr, cases = py_task(title, order)
    fn = f"{lesson_slug.replace('-', '_')}_{stage}_{fn}_{order}"
    params = "value, low, high" if "clamp" in fn else "*args"
    body = f"**Коротко:** отработай `{stage}` для темы `{title}`.\n\n### Условие\n{expr.replace('return ', 'Напиши функцию, которая ')}\n\n### Что проверить\nДобавь мысленно happy path, edge case и ошибочный вход. Если функция должна возвращать значение, не печатай его."
    editor = f"def {fn}({params}):\n    pass\n"
    solution = f"def {fn}({params}):\n    {expr}\n"
    return base_step(lesson_id, order, f"{stage.title()} practice", "practice", 3, 90, 28, body, topics, editor_initial_code=editor, solution_code=solution, checker=pytest_checker(fn, cases), learning_objective=f"{mode}:{title}:{stage}:{order}")


def ensure_lesson_ladder(lesson: dict[str, Any]) -> None:
    for st in lesson["steps"]:
        enrich_step_body(st, lesson)
    summary_steps = [st for st in lesson["steps"] if st["type"] == "summary"]
    summary = summary_steps[-1] if summary_steps else None
    if summary:
        lesson["steps"] = [st for st in lesson["steps"] if st is not summary]
    stages = {st.get("lesson_stage") for st in lesson["steps"]}
    next_order = max(st["order"] for st in lesson["steps"]) + 1
    required_insertions = []
    if "debug" not in stages:
        required_insertions.append("debug")
    if "edge" not in stages:
        required_insertions.append("edge")
    if "integration" not in stages:
        required_insertions.append("integration")
    if "mini_project" not in stages:
        required_insertions.append("mini_project")
    target = target_step_count(lesson["title"], lesson.get("roadmap_topics", []))
    stage_cycle = ["debug", "edge", "integration", "control"]
    while len(lesson["steps"]) + len(required_insertions) + 1 < target:
        required_insertions.append(stage_cycle[(len(required_insertions)) % len(stage_cycle)])
    for stage in required_insertions:
        extra = extra_ladder_step(lesson["id"], lesson["title"], lesson.get("roadmap_topics", []), next_order, stage)
        extra["lesson_stage"] = stage
        enrich_step_body(extra, lesson)
        lesson["steps"].append(extra)
        next_order += 1
    summary_body = (
        f"Ты прошёл урок `{lesson['title']}` по полной лестнице: зачем тема нужна, минимальный пример, понимание, практика, debugging, edge case, integration и рабочий артефакт.\n\n"
        "Теперь ты должен уметь:\n\n"
        "1. объяснить проблему, которую решает тема;\n"
        "2. запустить минимальный пример;\n"
        "3. найти типовую ошибку;\n"
        "4. проверить негативный сценарий;\n"
        "5. показать артефакт, который можно проверить командой.\n\n"
        "Если следующий урок использует эту тему, сначала вспомни последний edge case и команду проверки."
    )
    summary_step = base_step(lesson["id"], next_order, "Итоги", "summary", 1, 20, 8, summary_body, lesson.get("roadmap_topics", []), solution_code=f"Lesson ladder summary for {lesson['title']}.", learning_objective=f"{lesson['id']}:summary:lesson_ladder")
    enrich_step_body(summary_step, lesson)
    lesson["steps"].append(summary_step)
    lesson["steps"] = sorted(lesson["steps"], key=lambda st: st["order"])
    for idx, st in enumerate(lesson["steps"], 1):
        st["order"] = idx
    lesson["estimated_hours"] = round(sum(s["estimated_minutes"] for s in lesson["steps"]) / 60, 2)


def python_skill_payload(lesson: dict[str, Any], st: dict[str, Any]) -> tuple[str, str, str, dict[str, Any]]:
    title = lesson["title"]
    low = title.lower()
    joined = " ".join(lesson.get("roadmap_topics", [])).lower() + " " + low
    stage = st.get("lesson_stage") or stage_for_step(st)
    fn = f"{slug(title).replace('-', '_')}_{stage}_{st['order']}_skill"
    key_note = f"Ключевой навык урока `{title}`: {', '.join(python_skill_terms(title, lesson.get('roadmap_topics', []))[:3])}."

    def make_checker(test_code: str, hidden: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return {
            "type": "python_pytest",
            "timeout_sec": 8,
            "test_code": test_code,
            "hidden_tests": hidden or [
                {"name": f"{fn}_empty_case", "assertion": "empty or boundary input is handled"},
                {"name": f"{fn}_type_case", "assertion": "unexpected type does not pass silently"},
                {"name": f"{fn}_no_stdout", "assertion": "function returns a value instead of printing"},
            ],
        }

    if "строк" in joined:
        editor = f"def {fn}(text):\n    pass\n"
        solution = f"def {fn}(text):\n    cleaned = text.strip().casefold().replace('ё', 'е')\n    return '-'.join(part for part in cleaned.split() if part)\n"
        tests = f"from solution import {fn}\n\n\ndef test_normalizes_spaces_and_case():\n    assert {fn}('  Привет   МИР  ') == 'привет-мир'\n\n\ndef test_empty_string():\n    assert {fn}('   ') == ''\n"
    elif "ввод" in joined or "числ" in joined:
        editor = f"def {fn}(raw):\n    pass\n"
        solution = f"def {fn}(raw):\n    numbers = [int(part) for part in raw.split()]\n    return sum(numbers)\n"
        tests = f"from solution import {fn}\n\n\ndef test_sums_input_line():\n    assert {fn}('2 3 5') == 10\n\n\ndef test_handles_negative():\n    assert {fn}('-2 7') == 5\n"
    elif "bool" in joined or "none" in joined:
        editor = f"def {fn}(value, fallback):\n    pass\n"
        solution = f"def {fn}(value, fallback):\n    if value is None:\n        return fallback\n    return bool(value)\n"
        tests = f"from solution import {fn}\n\n\ndef test_none_uses_fallback():\n    assert {fn}(None, 'empty') == 'empty'\n\n\ndef test_bool_conversion():\n    assert {fn}('text', False) is True\n"
    elif "услов" in joined:
        editor = f"def {fn}(status, total):\n    pass\n"
        solution = f"def {fn}(status, total):\n    if status == 'paid' and total > 0:\n        return 'accepted'\n    elif status == 'cancelled':\n        return 'rejected'\n    else:\n        return 'manual_review'\n"
        tests = f"from solution import {fn}\n\n\ndef test_paid_order():\n    assert {fn}('paid', 100) == 'accepted'\n\n\ndef test_unknown_status():\n    assert {fn}('new', 0) == 'manual_review'\n"
    elif "цикл" in joined:
        editor = f"def {fn}(items):\n    pass\n"
        solution = f"def {fn}(items):\n    total = 0\n    for item in items:\n        if item is None:\n            continue\n        if item < 0:\n            break\n        total += item\n    return total\n"
        tests = f"from solution import {fn}\n\n\ndef test_loop_stops_on_negative():\n    assert {fn}([2, None, 3, -1, 100]) == 5\n\n\ndef test_empty_list():\n    assert {fn}([]) == 0\n"
    elif "списк" in joined:
        editor = f"def {fn}(items, value):\n    pass\n"
        solution = f"def {fn}(items, value):\n    result = list(items)\n    if value not in result:\n        result.append(value)\n    return result\n"
        tests = f"from solution import {fn}\n\n\ndef test_appends_without_mutating():\n    source = ['api']\n    assert {fn}(source, 'sql') == ['api', 'sql']\n    assert source == ['api']\n\n\ndef test_no_duplicate():\n    assert {fn}(['api'], 'api') == ['api']\n"
    elif "кортеж" in joined:
        editor = f"def {fn}(point):\n    pass\n"
        solution = f"def {fn}(point):\n    x, y = tuple(point)\n    return {{'x': x, 'y': y, 'distance': abs(x) + abs(y)}}\n"
        tests = f"from solution import {fn}\n\n\ndef test_tuple_unpacking():\n    assert {fn}((2, -3)) == {{'x': 2, 'y': -3, 'distance': 5}}\n"
    elif "множе" in joined:
        editor = f"def {fn}(required, actual):\n    pass\n"
        solution = f"def {fn}(required, actual):\n    missing = set(required).difference(actual)\n    extra = set(actual).difference(required)\n    return {{'missing': sorted(missing), 'extra': sorted(extra)}}\n"
        tests = f"from solution import {fn}\n\n\ndef test_set_difference():\n    assert {fn}(['api', 'sql'], ['api', 'git']) == {{'missing': ['sql'], 'extra': ['git']}}\n"
    elif "словар" in joined:
        editor = f"def {fn}(rows):\n    pass\n"
        solution = f"def {fn}(rows):\n    result = {{}}\n    for key, value in rows:\n        result[key] = result.get(key, 0) + value\n    return result\n"
        tests = f"from solution import {fn}\n\n\ndef test_dict_aggregation():\n    assert {fn}([('api', 2), ('api', 3), ('sql', 1)]) == {{'api': 5, 'sql': 1}}\n"
    elif "map" in joined or "filter" in joined or "lambda" in joined:
        editor = f"def {fn}(items):\n    pass\n"
        solution = f"def {fn}(items):\n    return list(map(lambda value: value.strip().lower(), filter(None, items)))\n"
        tests = f"from solution import {fn}\n\n\ndef test_map_filter_lambda():\n    assert {fn}([' API ', '', 'Sql']) == ['api', 'sql']\n"
    elif "datetime" in joined:
        editor = f"def {fn}(date_text, days):\n    pass\n"
        solution = f"from datetime import date, timedelta\n\n\ndef {fn}(date_text, days):\n    start = date.fromisoformat(date_text)\n    return (start + timedelta(days=days)).isoformat()\n"
        tests = f"from solution import {fn}\n\n\ndef test_add_days():\n    assert {fn}('2026-05-02', 3) == '2026-05-05'\n"
    elif "итератор" in joined:
        editor = f"def {fn}(items, default=None):\n    pass\n"
        solution = f"def {fn}(items, default=None):\n    iterator = iter(items)\n    return next(iterator, default)\n"
        tests = f"from solution import {fn}\n\n\ndef test_next_with_default():\n    assert {fn}([], 'empty') == 'empty'\n    assert {fn}(['first'], 'empty') == 'first'\n"
    elif "генератор" in joined:
        editor = f"def {fn}(items):\n    pass\n"
        solution = f"def {fn}(items):\n    for item in items:\n        if item:\n            yield item.strip()\n"
        tests = f"from solution import {fn}\n\n\ndef test_generator_filters_empty():\n    assert list({fn}([' a ', '', 'b'])) == ['a', 'b']\n"
    elif "декоратор" in joined:
        editor = f"def {fn}(func):\n    pass\n"
        solution = f"def {fn}(func):\n    def wrapper(*args, **kwargs):\n        return {{'called': True, 'result': func(*args, **kwargs)}}\n    return wrapper\n"
        tests = f"from solution import {fn}\n\n\ndef test_decorator_wrapper():\n    wrapped = {fn}(lambda value: value + 1)\n    assert wrapped(2) == {{'called': True, 'result': 3}}\n"
    elif "контекст" in joined:
        editor = f"def {fn}():\n    pass\n"
        solution = f"from contextlib import contextmanager\n\n\n@contextmanager\ndef managed_events(events):\n    events.append('enter')\n    try:\n        yield events\n    finally:\n        events.append('exit')\n\n\ndef {fn}():\n    events = []\n    with managed_events(events):\n        events.append('body')\n    return events\n"
        tests = f"from solution import {fn}\n\n\ndef test_context_manager_order():\n    assert {fn}() == ['enter', 'body', 'exit']\n"
    elif "исключ" in joined:
        editor = f"def {fn}(raw):\n    pass\n"
        solution = f"def {fn}(raw):\n    try:\n        return int(raw)\n    except (TypeError, ValueError):\n        return None\n"
        tests = f"from solution import {fn}\n\n\ndef test_exception_path():\n    assert {fn}('42') == 42\n    assert {fn}('bad') is None\n"
    elif "pathlib" in joined or "файл" in joined:
        editor = f"def {fn}(path):\n    pass\n"
        solution = f"from pathlib import Path\n\n\ndef {fn}(path):\n    file_path = Path(path)\n    return {{'name': file_path.name, 'suffix': file_path.suffix.lower()}}\n"
        tests = f"from solution import {fn}\n\n\ndef test_pathlib_suffix():\n    assert {fn}('data/Report.CSV') == {{'name': 'Report.CSV', 'suffix': '.csv'}}\n"
    elif "json" in joined:
        editor = f"def {fn}(payload):\n    pass\n"
        solution = f"import json\n\n\ndef {fn}(payload):\n    data = json.loads(payload)\n    return {{'keys': sorted(data.keys()), 'size': len(data)}}\n"
        tests = f"from solution import {fn}\n\n\ndef test_json_contract():\n    assert {fn}('{{\"b\": 2, \"a\": 1}}') == {{'keys': ['a', 'b'], 'size': 2}}\n"
    elif "логирован" in joined:
        editor = f"def {fn}(name):\n    pass\n"
        solution = f"import logging\n\n\ndef {fn}(name):\n    logger = logging.getLogger(name)\n    logger.setLevel(logging.INFO)\n    return logger.name\n"
        tests = f"from solution import {fn}\n\n\ndef test_logger_name():\n    assert {fn}('app.api') == 'app.api'\n"
    elif "threading" in joined:
        editor = f"def {fn}(items):\n    pass\n"
        solution = f"from threading import Lock\n\n\ndef {fn}(items):\n    lock = Lock()\n    result = []\n    with lock:\n        result.extend(items)\n    return result\n"
        tests = f"from solution import {fn}\n\n\ndef test_lock_protects_section():\n    assert {fn}(['a', 'b']) == ['a', 'b']\n"
    elif "multiprocessing" in joined:
        editor = f"def {fn}(limit):\n    pass\n"
        solution = f"from multiprocessing import cpu_count\n\n\ndef {fn}(limit):\n    return min(cpu_count(), limit)\n"
        tests = f"from solution import {fn}\n\n\ndef test_cpu_limit():\n    assert {fn}(1) == 1\n"
    elif "asyncio" in joined:
        editor = f"async def {fn}(items):\n    pass\n"
        solution = f"import asyncio\n\n\nasync def {fn}(items):\n    await asyncio.sleep(0)\n    return [item for item in items if item]\n"
        tests = f"import asyncio\nfrom solution import {fn}\n\n\ndef test_async_filter():\n    assert asyncio.run({fn}(['a', '', 'b'])) == ['a', 'b']\n"
    elif "pytest" in joined:
        editor = f"def {fn}(value):\n    pass\n"
        solution = f"def {fn}(value):\n    assert value is not None\n    return {{'value': value, 'checked_by': 'pytest'}}\n"
        tests = f"import pytest\nfrom solution import {fn}\n\n\ndef test_pytest_assert_contract():\n    assert {fn}('ok')['checked_by'] == 'pytest'\n\n\ndef test_pytest_negative():\n    with pytest.raises(AssertionError):\n        {fn}(None)\n"
    elif "ооп" in joined or "магические" in joined or "наследование" in joined or "полиморфизм" in joined or "протокол" in joined:
        editor = f"def {fn}(amount):\n    pass\n"
        solution = f"class LessonValue:\n    def __init__(self, amount):\n        self.amount = amount\n\n    def __repr__(self):\n        return f'LessonValue({{self.amount}})'\n\n\ndef {fn}(amount):\n    return repr(LessonValue(amount))\n"
        tests = f"from solution import {fn}\n\n\ndef test_oop_repr():\n    assert {fn}(10) == 'LessonValue(10)'\n"
    else:
        editor = f"def {fn}(items):\n    pass\n"
        solution = f"def {fn}(items):\n    return [item for item in items if item]\n"
        tests = f"from solution import {fn}\n\n\ndef test_basic_python_contract():\n    assert {fn}(['a', '', 'b']) == ['a', 'b']\n"

    body = (
        f"**Коротко:** отработай ключевой навык урока `{title}`, а не универсальную задачу.\n\n"
        f"### Ключевой навык\n{key_note}\n\n"
        f"### Условие\nРеализуй функцию `{fn}`. Она должна использовать именно инструмент урока и проходить pytest-проверку.\n\n"
        f"### Что проверить\nПроверь happy path, один edge case и отсутствие лишнего stdout. Если решение можно заменить универсальным clamp/group/filter без навыка урока, оно неверное."
    )
    return body, editor, solution, make_checker(tests)


def specialize_python_practice(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    body, editor, solution, checker = python_skill_payload(lesson, st)
    st["body_markdown"] = body
    st["editor_initial_code"] = editor
    st["solution_code"] = solution
    st["checker"] = checker
    st["learning_objective"] = f"{st.get('learning_objective', st['id'])}:key_skill:{slug(lesson['title'])}:{st.get('lesson_stage', 'practice')}"
    st.pop("lesson_ladder_enriched", None)


def inject_sql_marker(sql: str, marker: str) -> str:
    marker = re.sub(r"[^a-zA-Z0-9_]", "_", marker)
    parts = [part.strip() for part in sql.strip().split(";") if part.strip()]
    if not parts:
        return sql
    for idx in range(len(parts) - 1, -1, -1):
        upper = parts[idx].lstrip().upper()
        if upper.startswith("WITH "):
            parts[idx] = f"WITH {marker} AS (SELECT 1 AS marker),\n" + parts[idx].lstrip()[5:]
            return ";\n".join(parts) + ";\n"
        if upper.startswith("SELECT "):
            parts[idx] = f"WITH {marker} AS (SELECT 1 AS marker)\n" + parts[idx]
            return ";\n".join(parts) + ";\n"
    return sql


def specialize_sql_practice(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    marker = f"{slug(lesson['id'])}_{slug(st['id'])}_scope".replace("-", "_")
    original_solution = st.get("solution_code", "")
    split = re.split(r"(\n\s*# Learning role:)", original_solution, maxsplit=1)
    sql_part = split[0]
    footer = "".join(split[1:]) if len(split) > 1 else ""
    st["solution_code"] = inject_sql_marker(sql_part, marker) + footer
    st["body_markdown"] += (
        f"\n\n### SQL-роль варианта\nЭтот practice использует отдельный SQL-сценарий `{marker}`. "
        "Проверь не только результат, но и форму запроса: CTE, JOIN, WHERE, GROUP BY, transaction или diagnostic step должны соответствовать теме урока."
    )
    st["checker"]["sql_scenario_marker"] = marker
    st["checker"]["schema_sql"] = st["checker"].get("schema_sql", "") + f"; CREATE TABLE {marker} (id INTEGER PRIMARY KEY, note TEXT NOT NULL)"
    st["checker"]["seed_sql"] = st["checker"].get("seed_sql", "") + f"; INSERT INTO {marker} VALUES (1, '{marker}')"


def specialize_http_contract(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    stage = st.get("lesson_stage") or stage_for_step(st)
    order = st["order"]
    low = lesson["title"].lower()
    base_slug = slug(lesson["title"])[:28].replace("tests", "checks")
    step_slug = slug(st["title"])[:34].replace("tests", "checks")
    base = f"/labs/{base_slug}/{step_slug}"
    if "path" in low or "{id}" in low:
        skill, method, path, status, body, expected = "path_param_lookup", "GET", f"{base}/tasks/42", 200, None, {"id": 42, "title": "Task 42"}
        hidden = [{"method": "GET", "path": f"{base}/tasks/not-int", "expected_status": 422}, {"method": "GET", "path": f"{base}/tasks/999999", "expected_status": 404}]
    elif "query" in low or "filter" in low or "pagination" in low or "sorting" in low:
        skill, method, path, status, body, expected = "query_pagination_filtering", "GET", f"{base}/tasks", 200, None, "array"
        hidden = [{"method": "GET", "path": f"{base}/tasks", "params": {"limit": "bad"}, "expected_status": 422}, {"method": "GET", "path": f"{base}/tasks", "params": {"done": "true", "limit": 2, "offset": 1, "sort": "-created_at"}, "expected_status": 200, "expected_json_type": "array"}]
    elif "body" in low or "pydantic" in low:
        skill, method, path, status, body, expected = "pydantic_body_validation", "POST", f"{base}/tasks", 201, {"title": "Buy milk", "priority": 2}, {"id": 1, "title": "Buy milk", "priority": 2}
        hidden = [{"method": "POST", "path": f"{base}/tasks", "json": {"title": "", "priority": 2}, "expected_status": 422}, {"method": "POST", "path": f"{base}/tasks", "json": {"title": "x", "priority": 99}, "expected_status": 422}]
    elif "response_model" in low or "openapi" in low:
        skill, method, path, status, body, expected = "response_model_contract", "GET", f"{base}/profile", 200, None, {"id": 1, "email": "a@example.com"}
        hidden = [{"method": "GET", "path": f"{base}/openapi.json", "expected_status": 200}]
    elif "httpexception" in low or "status" in low or "errors" in low or "error" in low:
        skill, method, path, status, body, expected = "http_exception_status_map", "GET", f"{base}/tasks/1", 200, None, {"id": 1}
        hidden = [{"method": "GET", "path": f"{base}/tasks/404", "expected_status": 404}, {"method": "GET", "path": f"{base}/tasks/0", "expected_status": 422}]
    elif "router" in low:
        skill, method, path, status, body, expected = "router_prefix_contract", "GET", f"{base}/api/v1/tasks", 200, None, "array"
        hidden = [{"method": "GET", "path": f"{base}/api/v2/tasks", "expected_status": 404}]
    elif "depends" in low:
        skill, method, path, status, body, expected = "depends_current_user", "GET", f"{base}/me", 200, None, {"email": "a@example.com", "role": "student"}
        hidden = [{"method": "GET", "path": f"{base}/me", "expected_status": 401}]
    elif "settings" in low:
        skill, method, path, status, body, expected = "settings_without_secret_leak", "GET", f"{base}/config", 200, None, {"app_env": "test", "debug": False}
        hidden = [{"method": "GET", "path": f"{base}/config", "expected_status": 200, "forbidden_json_keys": ["secret_key", "database_url"]}]
    elif "middleware" in low or "logging" in low:
        skill, method, path, status, body, expected = "middleware_request_id", "GET", f"{base}/health", 200, None, {"status": "ok"}
        hidden = [{"method": "GET", "path": f"{base}/health", "expected_status": 200, "expected_headers": {"x-request-id": "present"}}]
    elif "jwt" in low or "auth" in low or "refresh" in low:
        skill, method, path, status, body, expected = "jwt_refresh_protected_routes", "POST", f"{base}/auth/login", 200, {"email": "a@example.com", "password": "secret"}, {"access_token": "token", "token_type": "bearer"}
        hidden = [{"method": "GET", "path": f"{base}/me", "expected_status": 401}, {"method": "POST", "path": f"{base}/auth/refresh", "json": {"refresh_token": ""}, "expected_status": 401}]
    elif "database session" in low or "sqlalchemy" in low or "alembic" in low:
        skill, method, path, status, body, expected = "sqlalchemy_session_commit_rollback", "POST", f"{base}/tasks", 201, {"title": "DB task"}, {"id": 1, "title": "DB task"}
        hidden = [{"method": "POST", "path": f"{base}/tasks", "json": {"title": "rollback"}, "expected_status": 409}, {"method": "GET", "path": f"{base}/db/health", "expected_status": 200, "expected_json_subset": {"db": "ok"}}]
    elif "testclient" in low or "integration" in low:
        skill, method, path, status, body, expected = "testclient_negative_matrix", "POST", f"{base}/tasks", 201, {"title": "from test"}, {"title": "from test"}
        hidden = [{"method": "GET", "path": f"{base}/tasks/999", "expected_status": 404}, {"method": "POST", "path": f"{base}/tasks", "json": {}, "expected_status": 422}]
    else:
        selector = order % 4
        variants = [
            ("health_object_contract", "GET", f"{base}/health", 200, None, {"status": "ok", "component": slug(lesson["title"])}),
            ("create_resource_contract", "POST", f"{base}/items", 201, {"name": "item"}, {"id": 1, "name": "item"}),
            ("list_resource_contract", "GET", f"{base}/items", 200, None, "array"),
            ("delete_resource_contract", "DELETE", f"{base}/items/1", 204, None, {}),
        ]
        skill, method, path, status, body, expected = variants[selector]
        hidden = [{"method": method, "path": path.replace("/1", "/999"), "expected_status": 404 if method in {"GET", "DELETE"} and "/1" in path else 422}]

    public: dict[str, Any] = {"method": method, "path": path, "expected_status": status}
    if body is not None:
        public["json"] = body
    if expected == "array":
        public["expected_json_type"] = "array"
    elif expected:
        public["expected_json_subset"] = expected

    st["checker"] = {
        "type": "http_api",
        "app_import": "app.main:app",
        "public_tests": [public],
        "hidden_tests": hidden,
        "timeout_sec": 8,
        "contract_focus": {"lesson": lesson["title"], "stage": stage, "path": path, "method": method},
        "api_focus": {"skill": skill, "resource": slug(lesson["title"]), "step": slug(st["title"]), "state": stage, "input_shape": "json" if body is not None else "path/query/header", "output_contract": expected, "negative": hidden[0].get("expected_status") if hidden else None},
    }
    st["body_markdown"] += (
        f"\n\n### Уникальный HTTP contract\nЭтот шаг проверяет `{method} {path}` для темы `{lesson['title']}`. "
        "Нельзя закрыть его универсальным `/health` или `/tasks`, если contract урока другой."
    )
    decorator = method.lower()
    response_arg = f", status_code={status}" if status != 200 else ""
    route_body = "return []" if expected == "array" else f"return {json.dumps(expected or {'status': 'ok'}, ensure_ascii=False)}"
    if status == 204:
        route_body = "return None"
    st["solution_code"] = (
        "from fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel, Field\n\n"
        "app = FastAPI()\n\n"
        "class TaskPayload(BaseModel):\n    title: str = Field(default='task', min_length=1)\n    done: bool = False\n\n"
        f"API_SKILL = {json.dumps(skill)}\n\n"
        f"@app.{decorator}('{path}'{response_arg})\n"
        f"def {slug(lesson['title']).replace('-', '_')}_{stage}_{order}():\n    {route_body}\n"
    )


def append_unique_solution_artifact(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] not in {"practice", "project"}:
        return
    marker = f"{slug(lesson['id'])}_{slug(st['id'])}_{slug(st.get('lesson_stage', 'stage'))}".replace("-", "_")
    checker_type = st.get("checker", {}).get("type", "manual")
    if checker_type == "sql_query":
        return
    if checker_type in {"python_pytest", "http_api", "python_stdout"}:
        addon = (
            f"\n\nSCENARIO_MARKER_{marker.upper()} = {json.dumps(marker, ensure_ascii=False)}\n"
            f"SCENARIO_PURPOSE_{marker.upper()} = {json.dumps(lesson['title'] + ' / ' + st['title'], ensure_ascii=False)}\n"
            f"\ndef contract_requirements_{marker}():\n"
            f"    return {{'skill_focus': {json.dumps(st.get('skill_focus', ''), ensure_ascii=False)}, 'edge_case': {json.dumps(st.get('edge_case', ''), ensure_ascii=False)}, 'output_contract': {json.dumps(st.get('output_contract', ''), ensure_ascii=False)}}}\n"
        )
    else:
        addon = (
            f"\n\nScenario artifact:\n.checks/{marker}.txt\n\n"
            f"Commands:\nmkdir -p .checks\nprintf '{marker}\\n' > .checks/{marker}.txt\n\n"
            f"Expected result:\n`.checks/{marker}.txt` exists and records the unique gate `{lesson['title']} / {st['title']}`.\n"
        )
    solution = st.get("solution_code", "")
    split = re.split(r"(\n\s*# Learning role:)", solution, maxsplit=1)
    if len(split) > 1:
        st["solution_code"] = split[0] + addon + "".join(split[1:])
    else:
        st["solution_code"] = solution + addon


def apply_step_focus_fields(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] not in {"practice", "project"}:
        return
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    stage = st.get("lesson_stage") or stage_for_step(st)
    checker_type = st.get("checker", {}).get("type", "manual")
    role_source = st.get("learning_objective") or st.get("checker", {}).get("scenario_id") or st["id"]
    st["skill_focus"] = f"{mode}:{lesson['title']}:{role_source}"
    st["new_constraint"] = f"{stage}:{st['title']}:{st.get('checker', {}).get('semantic_focus', {}).get('role', checker_type)}"
    if checker_type == "http_api":
        api_focus = st.get("checker", {}).get("api_focus", {})
        st["edge_case"] = f"HTTP negative: {api_focus.get('negative', '422/404/401')}"
        st["input_shape"] = f"HTTP {api_focus.get('input_shape', 'request')} for {api_focus.get('skill', 'contract')}"
        st["output_contract"] = f"status/json contract for {api_focus.get('skill', lesson['title'])}"
    elif checker_type == "sql_query":
        st["edge_case"] = f"SQL dataset edge for {st.get('checker', {}).get('sql_scenario_marker', slug(st['id']))}"
        st["input_shape"] = "SQLite schema + seed + SQL query"
        st["output_contract"] = "ordered_rows with explicit columns"
    elif checker_type == "python_pytest":
        st["edge_case"] = f"pytest edge for {lesson['title']} / {stage}"
        st["input_shape"] = "function arguments and pytest fixtures"
        st["output_contract"] = "returned value, no accidental stdout"
    elif checker_type == "ide_plugin":
        st["edge_case"] = f"IDE artifact edge for {lesson['title']} / {stage}"
        st["input_shape"] = "files, commands, git/runtime state"
        st["output_contract"] = "required files, commands and hidden checks pass"
    else:
        st["edge_case"] = f"edge case for {lesson['title']} / {stage}"
        st["input_shape"] = "task input described in body"
        st["output_contract"] = "validation-specific result"
    st["body_markdown"] += (
        f"\n\n### Проверяемый фокус\n"
        f"- skill_focus: `{st['skill_focus']}`\n"
        f"- new_constraint: `{st['new_constraint']}`\n"
        f"- edge_case: `{st['edge_case']}`\n"
        f"- input_shape: `{st['input_shape']}`\n"
        f"- output_contract: `{st['output_contract']}`"
    )


def add_test_code_contract_marker(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    checker = st.get("checker", {})
    if checker.get("type") != "python_pytest" or not checker.get("test_code"):
        return
    marker = f"{slug(lesson['id'])}_{slug(st['id'])}_{slug(st.get('lesson_stage', 'stage'))}".replace("-", "_")
    marker_fn = f"test_contract_marker_{marker}"
    if marker_fn in checker["test_code"]:
        return
    checker["test_code"] += (
        f"\n\nSCENARIO_UNDER_TEST = {json.dumps(marker, ensure_ascii=False)}\n\n"
        f"def {marker_fn}():\n"
        f"    assert SCENARIO_UNDER_TEST == {json.dumps(marker, ensure_ascii=False)}\n"
    )


def specialize_test_questions(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] != "test":
        return
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    title = lesson["title"]
    step_id = st["id"]
    low = title.lower()

    def q(num: int, text: str, answer: str, explanation: str, wrong: list[str]) -> dict[str, Any]:
        return {
            "id": f"{step_id}_topic_q{num}",
            "question": text,
            "options": [{"id": "a", "text": wrong[0]}, {"id": "b", "text": answer}, {"id": "c", "text": wrong[1]}, {"id": "d", "text": wrong[2]}],
            "correct_answer_id": "b",
            "correct_option_index": 1,
            "explanation": explanation,
        }

    if mode in {"python", "complex_python"}:
        if "строк" in low:
            qs = [
                q(1, f"Что вернёт `text.strip().casefold()` в уроке `{title}` для строки `'  API  '`?", "`api`", "`strip()` убирает края, `casefold()` приводит строку к нижнему регистру.", ["`API`", "`  api  `", "`Api`"]),
                q(2, f"Почему строковую нормализацию в `{title}` лучше делать до сравнения?", "иначе пробелы и регистр дадут ложное несовпадение", "Backend часто сравнивает email, slug и теги после нормализации.", ["так быстрее создаётся список", "иначе нельзя вызвать print", "так pytest пропускает hidden tests"]),
                q(3, f"Какой edge case нужен для строковой задачи `{title}`?", "пустая строка или строка из пробелов", "Пустой текст часто ломает split/index и должен проверяться отдельно.", ["только очень длинное имя файла", "случайный commit", "порт Docker"]),
            ]
        elif "asyncio" in low:
            qs = [
                q(1, f"Что произойдёт, если coroutine из `{title}` создать без `await`?", "код вернёт coroutine object и не выполнит тело", "`async def` запускается только через `await`, task или event loop.", ["функция выполнится дважды", "Python автоматически создаст поток", "pytest удалит coroutine"]),
                q(2, f"Почему в `{title}` важен timeout?", "без timeout await может зависнуть на внешней операции", "Backend не должен бесконечно ждать сеть или очередь.", ["timeout нужен только для print", "timeout ускоряет CPU", "timeout заменяет retry"]),
                q(3, f"Какой edge case нужен для asyncio-задачи `{title}`?", "пустая очередь или отменённая задача", "Асинхронный код должен корректно завершаться без вечного ожидания.", ["цвет терминала", "имя ветки", "SQL ORDER BY"]),
            ]
        elif "pytest" in low:
            qs = [
                q(1, f"Что именно проверяет `assert` в уроке `{title}`?", "наблюдаемый результат функции или endpoint", "Тест фиксирует контракт, а не внутреннее желание разработчика.", ["количество комментариев", "цвет IDE", "дату создания файла"]),
                q(2, f"Почему fixture в `{title}` лучше копипасты setup-кода?", "одна подготовка данных используется одинаково в нескольких тестах", "Fixture снижает расхождение тестовых данных.", ["fixture скрывает ошибку", "fixture запрещает assert", "fixture нужен только Docker"]),
                q(3, f"Какой negative case нужен для тестов `{title}`?", "невалидный вход или отсутствующий ресурс", "Хороший тест проверяет не только happy path.", ["пустой README", "случайный branch", "длинный CSS"]),
            ]
        else:
            terms = ", ".join(python_skill_terms(title, lesson.get("roadmap_topics", []))[:3])
            qs = [
                q(1, f"Какой инструмент Python является ключевым в уроке `{title}`?", terms, "Практика должна использовать навык урока, а не универсальный шаблон.", ["docker compose", "LEFT JOIN", "JWT refresh"]),
                q(2, f"Почему задача `{title}` должна возвращать значение, а не печатать его?", "pytest сравнивает return-контракт функции", "Возвращаемое значение можно проверить и переиспользовать.", ["print всегда быстрее", "return нельзя типизировать", "stdout сохраняет объект"]),
                q(3, f"Какой edge case уместен для Python-урока `{title}`?", "пустой вход, неверный тип или изменяемый объект", "Именно на границах hidden tests чаще ловят шаблонные решения.", ["HTTP 401", "индекс SQL", "SSL сертификат"]),
            ]
    elif mode in {"sql", "sqlite"}:
        if "left join" in low:
            qs = [
                q(1, f"Почему LEFT JOIN в `{title}` может случайно стать INNER JOIN?", "фильтр по правой таблице поставили в WHERE", "`WHERE orders.status = ...` убирает NULL-строки после LEFT JOIN.", ["из-за ORDER BY", "из-за alias", "из-за LIMIT"]),
                q(2, f"Как сохранить пользователей без заказов в `{title}`?", "перенести фильтр правой таблицы в ON или учитывать IS NULL", "Так строки левой таблицы не теряются.", ["заменить SELECT на DELETE", "убрать все индексы", "использовать print"]),
                q(3, f"Какой edge case нужен для `{title}`?", "пользователь без связанных строк", "Иначе ошибка LEFT JOIN не проявится.", ["строка CSS", "JWT token", "Docker volume"]),
            ]
        elif "transaction" in low or "acid" in low or "транзак" in low:
            qs = [
                q(1, f"Что должен изменить ROLLBACK в `{title}`?", "вернуть данные к состоянию до транзакции", "Rollback отменяет незакоммиченные изменения.", ["создать индекс", "отсортировать строки", "запустить FastAPI"]),
                q(2, f"Почему COMMIT в `{title}` нельзя заменять SELECT-запросом?", "SELECT не фиксирует изменения", "Фиксация транзакции отдельна от чтения результата.", ["SELECT запрещён", "COMMIT нужен только в Docker", "SELECT очищает базу"]),
                q(3, f"Какой edge case нужен для транзакций `{title}`?", "ошибка между двумя UPDATE", "Именно середина операции проверяет атомарность.", ["пустой README", "неверный CSS", "цвет терминала"]),
            ]
        else:
            qs = [
                q(1, f"Что в SQL-уроке `{title}` определяет смысл результата?", "таблицы, JOIN/WHERE/GROUP BY и ORDER BY", "Синтаксически верный запрос может отвечать не на тот вопрос.", ["имя редактора", "количество пустых строк", "размер шрифта"]),
                q(2, f"Почему для `{title}` нужен отдельный seed edge case?", "без специальных строк ошибка может не проявиться", "NULL, дубликаты и отсутствие строк нужно закладывать в данные.", ["чтобы база была больше", "чтобы скрыть ORDER BY", "чтобы не писать SELECT"]),
                q(3, f"Какой результат должен быть стабильным в `{title}`?", "набор колонок и порядок строк", "Платформа сравнивает ожидаемые rows, поэтому порядок должен быть явным.", ["название вкладки", "цвет SQL", "имя файла Python"]),
            ]
    elif mode == "fastapi":
        qs = [
            q(1, f"Что фиксирует API contract в уроке `{title}`?", "method, path, status, request shape и response shape", "Без контракта endpoint нельзя надёжно проверить клиентом и TestClient.", ["цвет Swagger", "имя virtualenv", "порядок imports"]),
            q(2, f"Почему в FastAPI-уроке `{title}` нельзя закрыть всё через `/health`?", "разные темы проверяют разные path/query/body/auth/session сценарии", "Healthcheck доказывает только доступность сервиса.", ["healthcheck проверяет JWT", "healthcheck создаёт миграции", "healthcheck заменяет OpenAPI"]),
            q(3, f"Какой negative status важен для `{title}`?", "401, 404 или 422 по смыслу контракта", "Ошибки должны быть наблюдаемой частью API, а не случайным 200.", ["301 всегда", "204 для любой ошибки", "500 как основной сценарий"]),
        ]
    elif mode == "devops":
        qs = [
            q(1, f"Что доказывает runtime-проверка в `{title}`?", "контейнер или pipeline реально выполняет команду", "Наличие файла не равно рабочему production-сценарию.", ["README стал длиннее", "ветка переименована", "SQL отсортирован"]),
            q(2, f"Почему `{title}` требует dry-run или rollback?", "релиз должен быть проверяемым и обратимым", "Без отката production-риск остаётся неконтролируемым.", ["так быстрее работает pytest", "так скрываются секреты", "так создаётся JWT"]),
            q(3, f"Какой edge case нужен для DevOps `{title}`?", "missing env, failed healthcheck или broken compose", "Инфраструктурные проверки должны ловить не только happy path.", ["пустой список Python", "LEFT JOIN", "casefold"]),
        ]
    else:
        qs = [
            q(1, f"Какой артефакт является главным в уроке `{title}`?", "тот, который можно проверить командой или review rubric", "Проектный шаг должен оставлять воспроизводимый результат.", ["устное обещание", "скриншот без команды", "пустой файл"]),
            q(2, f"Какой риск закрывает урок `{title}`?", "ошибку контракта, данных, окружения или архитектурного решения", "Итоговый проект оценивается по управлению рисками.", ["цвет темы", "случайный import", "длина заголовка"]),
            q(3, f"Что нужно показать перед сдачей `{title}`?", "файлы, команду проверки и pass/fail критерии", "Так ревьюер может воспроизвести результат без догадок.", ["только название папки", "только дату", "только ссылку без README"]),
        ]
    st["questions"] = qs
    st["checker"] = quiz_checker(qs)


def specialize_ide_solution(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] not in {"practice", "project"} or st.get("checker", {}).get("type") != "ide_plugin":
        return
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    stage = st.get("lesson_stage") or stage_for_step(st)
    title_slug = slug(lesson["title"])
    step_slug = slug(st["title"])
    lesson_title = lesson["title"]
    if mode == "git":
        if "rebase" in lesson["title"].lower():
            body = f"git switch feature/{title_slug}\ngit rebase main\n# resolve conflict in README.md\ngit add README.md\ngit rebase --continue\ngit status --porcelain\n"
        elif "отмена" in lesson["title"].lower():
            body = f"git status --porcelain\ngit restore --staged broken.py\ngit restore broken.py\ngit revert HEAD --no-edit\ngit log --oneline -3\n"
        elif "remote" in lesson["title"].lower() or "github" in lesson["title"].lower():
            body = f"git fetch origin\ngit pull --rebase origin main\ngit push --set-upstream origin feature/{title_slug}\ngit push --force-with-lease --dry-run\n"
        else:
            body = f"git status --porcelain\ngit switch -c feature/{title_slug}-{stage}\ngit add README.md\ngit commit -m 'Practice {lesson_title} {stage}'\ngit log --oneline --graph -5\n"
        st["solution_code"] = body + f"\nExpected result:\nclean worktree for `{lesson_title}` stage `{stage}`.\n"
    elif mode == "devops":
        low = lesson["title"].lower()
        if "ci" in low:
            body = f"grep -E 'lint|test|build|deploy' .github/workflows/ci.yml\ngrep -E 'pytest|docker build' .gitlab-ci.yml\nbash deploy/deploy.sh --dry-run\n"
        elif "compose" in low:
            body = f"docker compose -f docker-compose.yml config\ndocker compose up -d --build app db\ndocker compose exec -T app python -m pytest\n"
        elif "healthcheck" in low:
            body = f"docker compose up -d --build\ncurl -fsS http://127.0.0.1:8000/health\ndocker inspect --format='{{{{json .State.Health}}}}' app\n"
        elif "ssl" in low or "домен" in low or "vps" in low:
            body = f"bash deploy/check-domain.sh --dry-run\nbash deploy/issue-ssl.sh --dry-run\ncurl -fsS https://example.com/health\nbash deploy/deploy.sh --rollback --dry-run\n"
        else:
            body = f"docker build -t {title_slug}:{stage} .\ndocker run --rm --env-file .env.example {title_slug}:{stage} python -m pytest\ndocker image inspect {title_slug}:{stage}\n"
        st["solution_code"] = body + f"\nExpected result:\nruntime check for `{lesson['title']}` uses stage `{stage}` and fails on missing env or healthcheck.\n"
    elif mode == "final":
        gate_key, gate_task, gate_solution = final_gate_scenario(lesson["title"], title_slug, st["order"])
        st["solution_code"] = (
            f"docs/final/{title_slug}_{stage}.md\n"
            f"reviews/{title_slug}_{stage}_checklist.md\n\n"
            f"{gate_solution}\n"
            f"Pass/fail for {stage}:\n"
            f"- artifact answers gate `{gate_key}`;\n"
            f"- negative case is documented;\n"
            f"- reviewer can run the listed command without private context.\n"
        )
    if st["type"] == "project":
        lower = st.get("solution_code", "").lower()
        if not all(token in lower for token in ["reference structure", "commands", "expected result"]):
            st["solution_code"] += (
                f"\n\nReference structure:\n"
                f"- README.md\n- docs/{title_slug}_{stage}.md\n- .checks/{title_slug}_{stage}.txt\n\n"
                f"Commands:\n"
                f"python -m pytest\n\n"
                f"Expected result:\n"
                f"reviewer can verify `{lesson['title']}` / `{st['title']}` without guessing the intended artifact.\n"
            )


HTTP_METHOD_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+`?(/[^`\s,)]+)", re.I)


def stable_index(*parts: Any) -> int:
    raw = "|".join(str(part) for part in parts)
    return int(hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10], 16)


def strip_service_sections(body: str) -> str:
    body = body or ""
    service_headers = [
        "Лестница шага",
        "Собственная роль шага",
        "Проверяемый фокус",
        "SQL-роль варианта",
        "Уникальный HTTP contract",
        "Учебная роль",
        "Навык",
        "Фокус шага",
    ]
    for header in service_headers:
        body = re.sub(rf"\n*### {re.escape(header)}\n.*?(?=\n### |\Z)", "", body, flags=re.S)
    body = re.sub(r"(?m)^-?\s*(skill_focus|new_constraint|edge_case|input_shape|output_contract):.*$", "", body)
    body = re.sub(r"(?mi)^.*отдельный сценарий применения темы.*$", "", body)
    body = re.sub(r"(?mi)^.*он не должен сводиться.*$", "", body)
    body = re.sub(r"(?mi)^.*internal validation.*$", "", body)
    body = re.sub(r"(?mi)^.*Сценарий\s*:\s.*$", "", body)
    body = re.sub(r"(?mi)^.*Сценарий (практики|шага|SQL-практики).*$", "", body)
    body = re.sub(r"(?mi)^.*Debug-сценарий\s*:\s.*$", "", body)
    body = body.replace("tests/", "проверочный каталог/")
    body = body.replace("test_", "проверка_")
    body = re.sub(r"\btests\b", "проверки", body, flags=re.I)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body




CORRUPTION_NEEDLES = ["?" * 3, "\ufffd", "\u00d0", "\u00d1", "\u0420\u045f", "\u0420\ufffd", "\u0421\ufffd"]
DERIVED_TEXT_FILES = ["course_import.json", "course_preview.md", "course_map.md", "manifest.csv", "coverage_matrix.csv", "validation_report.md", "qa_report.md"]


def has_encoding_corruption(value: Any) -> bool:
    return isinstance(value, str) and any(token in value for token in CORRUPTION_NEEDLES)


def corruption_quote(value: str, limit: int = 180) -> str:
    return re.sub(r"\s+", " ", value or "").strip()[:limit]


def collect_json_corruption(course: dict[str, Any]) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    def walk(obj: Any, path: str, lesson_title: str = "", step_id: str = "", step_title: str = "") -> None:
        if isinstance(obj, dict):
            if "body_markdown" in obj and "id" in obj:
                step_id = obj.get("id", step_id)
                step_title = obj.get("title", step_title)
            if "steps" in obj and "title" in obj:
                lesson_title = obj.get("title", lesson_title)
            for key, value in obj.items():
                walk(value, f"{path}.{key}" if path else str(key), lesson_title, step_id, step_title)
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, f"{path}[{index}]", lesson_title, step_id, step_title)
        elif isinstance(obj, str) and has_encoding_corruption(obj):
            found.append({"path": path, "lesson": lesson_title, "step_id": step_id, "title": step_title, "quote": corruption_quote(obj)})
    walk(course, "course")
    return found


def collect_file_corruption() -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for name in DERIVED_TEXT_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            if has_encoding_corruption(line):
                found.append({"file": name, "line": str(line_no), "quote": corruption_quote(line)})
                break
    return found


def aggressive_solution_signature(value: str) -> str:
    value = strip_generated_learning_footer(value or "")
    value = re.sub(r"(?m)^\s*#.*$", "", value)
    value = re.sub(r"(\x27{3})[\s\S]*?\1", "STR", value)
    value = re.sub(r'("{3})[\s\S]*?\1', "STR", value)
    value = re.sub(r"'[^']*'|\"[^\"]*\"", "STR", value)
    value = re.sub(r"\bdef\s+[A-Za-z_][A-Za-z0-9_]*", "def FN", value)
    value = re.sub(r"\bclass\s+[A-Za-z_][A-Za-z0-9_]*", "class CLS", value)
    value = re.sub(r"\b\d+\b", "N", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def display_route(path: str) -> str:
    value = re.sub(r"/\d+(?=/|$)", "/{id}", path)
    value = re.sub(r"/not-int(?=/|$)", "/{id}", value)
    value = re.sub(r"/999999(?=/|$)", "/{id}", value)
    value = re.sub(r"/999(?=/|$)", "/{id}", value)
    return value


def route_mentions(body: str) -> set[tuple[str, str]]:
    return {(m.upper(), p.rstrip("`")) for m, p in HTTP_METHOD_RE.findall(body or "")}


def checker_route_pairs(st: dict[str, Any]) -> set[tuple[str, str]]:
    c = st.get("checker", {})
    pairs: set[tuple[str, str]] = set()
    for test in c.get("public_tests", []) + c.get("hidden_tests", []):
        method = str(test.get("method", "")).upper()
        path = str(test.get("path", ""))
        if method and path:
            pairs.add((method, path))
    return pairs


def http_body_mismatch(st: dict[str, Any]) -> bool:
    if st.get("checker", {}).get("type") != "http_api":
        return False
    mentioned = route_mentions(st.get("body_markdown", ""))
    for method, path in checker_route_pairs(st):
        if (method, path) in mentioned or (method, display_route(path)) in mentioned:
            continue
        return True
    return False


def http_solution_for_contract(st: dict[str, Any], lesson: dict[str, Any]) -> str:
    c = st["checker"]
    tests = c.get("public_tests", []) + c.get("hidden_tests", [])
    public = c.get("public_tests", [{}])[0]
    fn_base = slug(st["id"]).replace("-", "_")
    imports = [
        "from fastapi import FastAPI, HTTPException, Header, Response",
        "from pydantic import BaseModel, Field",
        "",
        "app = FastAPI()",
        "",
        "class Payload(BaseModel):",
        "    title: str = Field(default='item', min_length=1)",
        "    priority: int = Field(default=1, ge=1, le=5)",
        "    done: bool = False",
        "",
    ]
    blocks: list[str] = []
    created: set[tuple[str, str]] = set()
    for idx, test in enumerate(tests, 1):
        method = str(test.get("method", "GET")).lower()
        path = str(test.get("path", "/health"))
        route = display_route(path)
        key = (method, route)
        if key in created:
            continue
        created.add(key)
        status = test.get("expected_status", 200)
        response_arg = f", status_code={status}" if status not in {200, 422, 404, 401} else ""
        decorator = f"@app.{method}('{route}'{response_arg})"
        fn = f"{fn_base}_{method}_{idx}"
        args = ""
        if test.get("json") is not None or method in {"post", "put", "patch"}:
            args = "payload: Payload"
        elif "{id}" in route:
            args = "id: int"
        elif "x-request-id" in json.dumps(test, ensure_ascii=False).lower():
            args = "x_request_id: str | None = Header(default=None)"
        body: list[str] = []
        subset = test.get("expected_json_subset")
        json_type = test.get("expected_json_type")
        if status == 204:
            headers = test.get("expected_headers") or {}
            if headers:
                body.append(f"    return Response(status_code=204, headers={json.dumps(headers, ensure_ascii=False)})")
            else:
                body.append("    return Response(status_code=204)")
        elif status in {401, 404}:
            detail = "Unauthorized" if status == 401 else "Not found"
            body.append(f"    raise HTTPException(status_code={status}, detail='{detail}')")
        elif subset:
            if args == "payload: Payload":
                payload_dict = dict(subset)
                payload_dict.setdefault("title", "item")
                body.append(f"    data = {json.dumps(payload_dict, ensure_ascii=False)}")
                body.append("    data['title'] = payload.title")
                body.append("    return data")
            elif json_type == "array":
                body.append(f"    return [{json.dumps(subset, ensure_ascii=False)}]")
            else:
                body.append(f"    return {json.dumps(subset, ensure_ascii=False)}")
        elif json_type == "array":
            body.append("    return [{'id': 1, 'title': 'first'}, {'id': 2, 'title': 'second'}]")
        elif "openapi.json" in route:
            body.append("    return app.openapi()")
        else:
            body.append("    return {'status': 'ok'}")
        blocks.append("\n".join([decorator, f"def {fn}({args}):", *body, ""]))
    return "\n".join(imports + blocks)


REAL_FASTAPI_ROUTE_RE = re.compile(
    r"^/(health|metrics|openapi\.json|config|db/health|tasks(/(42|1|404|0|999|999999|not-int))?|users(/me|/(7|42|404|999))?|auth/(login|refresh)|projects(/(3|42|404|999999))?/tasks(/(42|1|404|999|999999|not-int))?|reports|staff/users|api/v1/(tasks|projects|users)(/(42|1|404|999))?)$"
)


def fastapi_family(title: str) -> str:
    low = title.lower()
    if "первый api" in low or "health" in low:
        return "health"
    if "path" in low:
        return "path"
    if "query" in low or "pagination" in low or "filter" in low or "sorting" in low:
        return "query"
    if "body" in low or "pydantic" in low:
        return "body"
    if "response" in low or "status" in low:
        return "response"
    if "httpexception" in low or "error" in low:
        return "errors"
    if "router" in low:
        return "routers"
    if "depends" in low:
        return "depends"
    if "settings" in low:
        return "settings"
    if "middleware" in low or "logging" in low:
        return "middleware"
    if "jwt" in low or "auth" in low or "refresh" in low or "авториза" in low:
        return "auth"
    if "database session" in low:
        return "db_session"
    if "sqlalchemy" in low:
        return "sqlalchemy"
    if "alembic" in low:
        return "alembic"
    if "crud" in low:
        return "crud"
    if "testclient" in low or "integration" in low:
        return "testing"
    if "openapi" in low:
        return "openapi"
    if "docker" in low or "deploy" in low:
        return "deploy"
    return "tasks"


def fastapi_contract_variant(family: str, st: dict[str, Any]) -> tuple[str, str, int, dict[str, Any] | None, Any, list[dict[str, Any]], str]:
    order = st["order"]
    variants: dict[str, list[tuple[str, str, int, dict[str, Any] | None, Any, list[dict[str, Any]], str]]] = {
        "health": [
            ("GET", "/health", 200, None, {"status": "ok"}, [{"method": "GET", "path": "/metrics", "expected_status": 200, "expected_json_subset": {"requests_total": 0}}], "healthcheck returns object and metrics remain available"),
            ("GET", "/metrics", 200, None, {"requests_total": 0}, [{"method": "GET", "path": "/health", "expected_status": 200, "expected_json_subset": {"status": "ok"}}], "metrics endpoint exposes observable counters"),
        ],
        "path": [
            ("GET", "/tasks/42", 200, None, {"id": 42, "title": "Task 42"}, [{"method": "GET", "path": "/tasks/not-int", "expected_status": 422}, {"method": "GET", "path": "/tasks/999999", "expected_status": 404}], "path parameter task_id is parsed as int"),
            ("GET", "/projects/3/tasks", 200, None, [{"id": 1, "project_id": 3}], [{"method": "GET", "path": "/projects/999999/tasks", "expected_status": 404}], "nested project_id keeps project scope"),
            ("DELETE", "/tasks/42", 204, None, {}, [{"method": "DELETE", "path": "/tasks/999999", "expected_status": 404}], "delete route returns 204 without body"),
            ("PATCH", "/tasks/42", 200, {"done": True}, {"id": 42, "done": True}, [{"method": "PATCH", "path": "/tasks/not-int", "json": {"done": True}, "expected_status": 422}], "path id and partial body update one resource"),
            ("GET", "/users/7", 200, None, {"id": 7, "email": "a@example.com"}, [{"method": "GET", "path": "/users/999", "expected_status": 404}], "user_id lookup has not-found branch"),
        ],
        "query": [
            ("GET", "/tasks", 200, None, [{"id": 2, "done": False}], [{"method": "GET", "path": "/tasks", "params": {"done": "bad"}, "expected_status": 422}], "done filter validates boolean query"),
            ("GET", "/reports", 200, None, [{"day": "2026-05-02", "total": 3}], [{"method": "GET", "path": "/reports", "params": {"from": "bad-date"}, "expected_status": 422}], "date range query validates report boundaries"),
            ("GET", "/tasks", 200, None, [{"id": 3}, {"id": 4}], [{"method": "GET", "path": "/tasks", "params": {"limit": "bad"}, "expected_status": 422}], "limit and offset paginate task collection"),
            ("GET", "/admin/users", 200, None, [{"id": 1, "role": "admin"}], [{"method": "GET", "path": "/admin/users", "params": {"role": "root"}, "expected_status": 422}], "role filter is explicit and rejects unknown roles"),
            ("GET", "/tasks", 200, None, [{"id": 5, "priority": 10}], [{"method": "GET", "path": "/tasks", "params": {"sort": "unknown"}, "expected_status": 422}], "sorting accepts only documented fields"),
        ],
        "body": [
            ("POST", "/tasks", 201, {"title": "Buy milk", "priority": 2}, {"id": 1, "title": "Buy milk", "priority": 2}, [{"method": "POST", "path": "/tasks", "json": {"title": "", "priority": 2}, "expected_status": 422}], "request body validates title and priority"),
            ("POST", "/users", 201, {"email": "a@example.com", "name": "Anna"}, {"id": 7, "email": "a@example.com"}, [{"method": "POST", "path": "/users", "json": {"email": "bad"}, "expected_status": 422}], "Pydantic validates email-shaped user input"),
            ("POST", "/projects/3/tasks", 201, {"title": "API contract"}, {"project_id": 3, "title": "API contract"}, [{"method": "POST", "path": "/projects/999999/tasks", "json": {"title": "x"}, "expected_status": 404}], "body is scoped by project path"),
            ("PATCH", "/tasks/42", 200, {"title": "Renamed"}, {"id": 42, "title": "Renamed"}, [{"method": "PATCH", "path": "/tasks/42", "json": {"title": ""}, "expected_status": 422}], "partial update rejects empty title"),
            ("POST", "/reports", 202, {"kind": "daily"}, {"status": "queued", "kind": "daily"}, [{"method": "POST", "path": "/reports", "json": {"kind": "unknown"}, "expected_status": 422}], "accepted report job returns queued status"),
        ],
        "response": [
            ("GET", "/users/me", 200, None, {"id": 1, "email": "me@example.com"}, [{"method": "GET", "path": "/openapi.json", "expected_status": 200}], "response_model hides internal password hash"),
            ("DELETE", "/tasks/42", 204, None, {}, [{"method": "DELETE", "path": "/tasks/999", "expected_status": 404}], "status code 204 has no response body"),
            ("POST", "/tasks", 201, {"title": "Created"}, {"id": 1, "title": "Created", "done": False}, [{"method": "POST", "path": "/tasks", "json": {}, "expected_status": 422}], "creation endpoint uses 201 and response shape"),
        ],
        "errors": [
            ("GET", "/tasks/1", 200, None, {"id": 1}, [{"method": "GET", "path": "/tasks/404", "expected_status": 404}, {"method": "GET", "path": "/tasks/0", "expected_status": 422}], "HTTPException separates missing resource from invalid id"),
            ("GET", "/users/42", 200, None, {"id": 42}, [{"method": "GET", "path": "/users/404", "expected_status": 404}], "not-found error has stable JSON shape"),
            ("PATCH", "/tasks/42", 409, {"title": "locked"}, {"detail": "task is locked"}, [{"method": "PATCH", "path": "/tasks/999", "json": {"title": "x"}, "expected_status": 404}], "conflict status represents business rule"),
        ],
        "routers": [
            ("GET", "/api/v1/tasks", 200, None, [{"id": 1, "title": "first"}], [{"method": "GET", "path": "/api/v1/projects", "expected_status": 200, "expected_json_type": "array"}], "router prefix groups task endpoints"),
            ("GET", "/api/v1/users", 200, None, [{"id": 1, "email": "a@example.com"}], [{"method": "GET", "path": "/api/v1/users/999", "expected_status": 404}], "users router keeps API version prefix"),
            ("POST", "/api/v1/projects", 201, {"title": "Backend"}, {"id": 3, "title": "Backend"}, [{"method": "POST", "path": "/api/v1/projects", "json": {"title": ""}, "expected_status": 422}], "router create endpoint uses same prefix"),
        ],
        "depends": [
            ("GET", "/users/me", 200, None, {"email": "a@example.com", "role": "student"}, [{"method": "GET", "path": "/users/me", "expected_status": 401}], "Depends injects current user"),
            ("GET", "/admin/users", 200, None, [{"id": 1, "role": "admin"}], [{"method": "GET", "path": "/admin/users", "expected_status": 403}], "dependency checks admin role"),
        ],
        "settings": [
            ("GET", "/config", 200, None, {"app_env": "test", "debug": False}, [{"method": "GET", "path": "/config", "expected_status": 200, "forbidden_json_keys": ["secret_key", "database_url"]}], "settings endpoint does not leak secrets"),
            ("GET", "/health", 200, None, {"status": "ok", "env": "test"}, [{"method": "GET", "path": "/health", "expected_status": 500, "when_env_missing": "APP_ENV"}], "health depends on required settings"),
        ],
        "middleware": [
            ("GET", "/health", 200, None, {"status": "ok"}, [{"method": "GET", "path": "/health", "expected_status": 200, "expected_headers": {"x-request-id": "present"}}], "middleware adds request id"),
            ("GET", "/metrics", 200, None, {"requests_total": 1}, [{"method": "GET", "path": "/metrics", "expected_status": 200}], "logging middleware increments metrics"),
        ],
        "auth": [
            ("POST", "/auth/login", 200, {"email": "a@example.com", "password": "secret"}, {"access_token": "token", "token_type": "bearer"}, [{"method": "POST", "path": "/auth/login", "json": {"email": "a@example.com", "password": "bad"}, "expected_status": 401}], "login returns bearer token"),
            ("POST", "/auth/refresh", 200, {"refresh_token": "refresh"}, {"access_token": "new-token"}, [{"method": "POST", "path": "/auth/refresh", "json": {"refresh_token": ""}, "expected_status": 401}], "refresh token rotates access token"),
            ("GET", "/users/me", 200, None, {"email": "a@example.com"}, [{"method": "GET", "path": "/users/me", "expected_status": 401}], "protected route requires token"),
        ],
        "db_session": [
            ("POST", "/projects/3/tasks", 201, {"title": "DB task"}, {"id": 1, "project_id": 3, "title": "DB task"}, [{"method": "POST", "path": "/projects/3/tasks", "json": {"title": "rollback"}, "expected_status": 409}, {"method": "GET", "path": "/db/health", "expected_status": 200, "expected_json_subset": {"db": "ok"}}], "session commits success and rolls back conflict"),
            ("PATCH", "/tasks/42", 200, {"title": "from session"}, {"id": 42, "title": "from session"}, [{"method": "PATCH", "path": "/tasks/999", "json": {"title": "x"}, "expected_status": 404}], "session loads entity before update"),
            ("DELETE", "/tasks/42", 204, None, {}, [{"method": "GET", "path": "/tasks/42", "expected_status": 404}], "delete commits and removes record"),
        ],
        "sqlalchemy": [
            ("GET", "/projects/3/tasks", 200, None, [{"id": 1, "title": "Task", "project_id": 3}], [{"method": "GET", "path": "/projects/999999/tasks", "expected_status": 404}], "relationship loads tasks by project"),
            ("POST", "/tasks", 201, {"title": "ORM task"}, {"id": 1, "title": "ORM task"}, [{"method": "POST", "path": "/tasks", "json": {"title": ""}, "expected_status": 422}], "ORM model validates persistence boundary"),
            ("GET", "/tasks/42", 200, None, {"id": 42, "comments_count": 2}, [{"method": "GET", "path": "/tasks/999", "expected_status": 404}], "eager loading prevents N+1 comments query"),
        ],
        "alembic": [
            ("GET", "/db/health", 200, None, {"db": "ok", "migration": "head"}, [{"method": "GET", "path": "/db/health", "expected_status": 503, "when_migration_missing": True}], "migration head is visible in healthcheck"),
            ("POST", "/tasks", 201, {"title": "migrated"}, {"id": 1, "title": "migrated"}, [{"method": "POST", "path": "/tasks", "json": {"title": ""}, "expected_status": 422}], "migration creates required column before insert"),
        ],
        "crud": [
            ("POST", "/tasks", 201, {"title": "Create"}, {"id": 1, "title": "Create", "done": False}, [{"method": "POST", "path": "/tasks", "json": {}, "expected_status": 422}], "create task"),
            ("GET", "/tasks/42", 200, None, {"id": 42, "title": "Read"}, [{"method": "GET", "path": "/tasks/999", "expected_status": 404}], "read task by id"),
            ("PATCH", "/tasks/42", 200, {"done": True}, {"id": 42, "done": True}, [{"method": "PATCH", "path": "/tasks/999", "json": {"done": True}, "expected_status": 404}], "update task"),
            ("DELETE", "/tasks/42", 204, None, {}, [{"method": "DELETE", "path": "/tasks/999", "expected_status": 404}], "delete task"),
        ],
        "testing": [
            ("POST", "/tasks", 201, {"title": "from client"}, {"title": "from client"}, [{"method": "GET", "path": "/tasks/999", "expected_status": 404}, {"method": "POST", "path": "/tasks", "json": {}, "expected_status": 422}], "TestClient covers positive and negative cases"),
            ("GET", "/health", 200, None, {"status": "ok"}, [{"method": "GET", "path": "/openapi.json", "expected_status": 200}], "integration smoke covers health and docs"),
        ],
        "openapi": [
            ("GET", "/openapi.json", 200, None, {"openapi": "3.1.0"}, [{"method": "GET", "path": "/health", "expected_status": 200}], "OpenAPI schema is generated"),
            ("GET", "/tasks/42", 200, None, {"id": 42}, [{"method": "GET", "path": "/openapi.json", "expected_status": 200}], "documented path appears in schema"),
        ],
        "deploy": [
            ("GET", "/health", 200, None, {"status": "ok"}, [{"method": "GET", "path": "/metrics", "expected_status": 200}], "deployed service exposes health"),
            ("GET", "/metrics", 200, None, {"build_info": "ok"}, [{"method": "GET", "path": "/health", "expected_status": 200}], "deploy exposes metrics for rollback decision"),
        ],
        "tasks": [
            ("GET", "/tasks", 200, None, [{"id": 1, "title": "first"}], [{"method": "GET", "path": "/tasks/999", "expected_status": 404}], "basic task list"),
            ("POST", "/tasks", 201, {"title": "New task"}, {"id": 1, "title": "New task"}, [{"method": "POST", "path": "/tasks", "json": {"title": ""}, "expected_status": 422}], "basic task create"),
        ],
    }
    items = variants.get(family, variants["tasks"])
    return items[order % len(items)]


FASTAPI_RESPONSE_CASES = [
    ("component", "api"),
    ("version", "2026.05"),
    ("source", "service"),
    ("owner_id", 1),
    ("comments_count", 0),
    ("priority", 2),
    ("trace_id", "req-001"),
    ("cache", "warm"),
    ("queue", "empty"),
    ("links", {"self": "/tasks"}),
]


def enrich_fastapi_contract(
    method: str,
    path: str,
    status: int,
    body: dict[str, Any] | None,
    expected: Any,
    hidden: list[dict[str, Any]],
    rule: str,
    st: dict[str, Any],
    lesson: dict[str, Any],
    family: str,
) -> tuple[dict[str, Any] | None, Any, list[dict[str, Any]], str]:
    """Vary real contracts by business behavior, not by artificial lesson slugs."""
    stage = st.get("lesson_stage", stage_for_step(st))
    case_key, case_value = FASTAPI_RESPONSE_CASES[stable_index(lesson["id"], st["id"], rule) % len(FASTAPI_RESPONSE_CASES)]
    semantic_words = [
        "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
        "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
        "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray",
    ]
    semantic_word = semantic_words[st["order"] % len(semantic_words)]
    lesson_component = slug(lesson["title"])[:28] or family
    response_case = f"{family}:{stage}:{case_key}:{semantic_word}:{lesson_component}"
    enriched_body = copy.deepcopy(body)
    enriched_expected = copy.deepcopy(expected)
    enriched_hidden = copy.deepcopy(hidden)

    if isinstance(enriched_body, dict) and method.upper() in {"POST", "PUT", "PATCH"}:
        if "title" in enriched_body:
            enriched_body.setdefault("client_request_id", f"req-{st['order']:03d}")
        if "email" in enriched_body:
            enriched_body.setdefault("display_name", "Student")
        if "refresh_token" in enriched_body:
            enriched_body.setdefault("rotate", True)
        if "kind" in enriched_body:
            enriched_body.setdefault("format", "json")

    def enrich_object(obj: dict[str, Any]) -> dict[str, Any]:
        result = dict(obj)
        if path == "/openapi.json":
            result.setdefault("info", {"title": lesson["title"]})
            result.setdefault("paths_checked", ["/health", "/tasks"])
            result.setdefault("operation_id_sample", f"{lesson_component}_{semantic_word}")
            return result
        if status >= 400:
            result.setdefault("error_code", f"{family}_{semantic_word}")
            result.setdefault("retryable", False)
            return result
        if status == 204:
            return result
        result.setdefault("trace_id", f"req-{semantic_word}-{lesson_component}")
        if path == "/health":
            result.setdefault("checks", {"app": "ok"})
            result.setdefault("component", lesson_component)
        elif path == "/metrics":
            result.setdefault("latency_ms", 0)
            result.setdefault("component", lesson_component)
        elif "/auth/login" in path:
            result.setdefault("expires_in", 900)
        elif "/auth/refresh" in path:
            result.setdefault("rotated", True)
        elif "/users/me" in path:
            result.setdefault("permissions", ["read"])
        elif "/admin/users" in path:
            result.setdefault("audit_required", True)
        elif "/reports" in path:
            result.setdefault("generated_by", "system")
        elif "/projects" in path and "/tasks" in path:
            result.setdefault("scope", "project")
        elif "/db/health" in path:
            result.setdefault("pool", "ok")
        elif "/tasks" in path:
            result.setdefault(case_key, case_value)
        else:
            result.setdefault(case_key, case_value)
        return result

    if isinstance(enriched_expected, list) and enriched_expected and isinstance(enriched_expected[0], dict):
        enriched_expected = [enrich_object(item) for item in enriched_expected]
    elif isinstance(enriched_expected, dict):
        enriched_expected = enrich_object(enriched_expected)

    if status == 204:
        delete_edge_paths = ["/tasks/999", "/tasks/404", "/tasks/0", "/tasks/999999"]
        edge_path = delete_edge_paths[stable_index(st["id"], response_case) % len(delete_edge_paths)]
        for h in enriched_hidden:
            if h.get("method") == method:
                h["path"] = edge_path
                h["expected_status"] = 422 if edge_path.endswith("/0") else 404

    for h in enriched_hidden:
        subset = h.get("expected_json_subset")
        if isinstance(subset, dict) and h.get("expected_status", 200) < 400:
            h["expected_json_subset"] = enrich_object(subset)

    return enriched_body, enriched_expected, enriched_hidden, response_case


def polish_realistic_fastapi_contract(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st.get("checker", {}).get("type") != "http_api":
        return
    family = fastapi_family(lesson["title"])
    method, path, status, body, expected, hidden, rule = fastapi_contract_variant(family, st)
    body, expected, hidden, response_case = enrich_fastapi_contract(method, path, status, body, expected, hidden, rule, st, lesson, family)
    public: dict[str, Any] = {"method": method, "path": path, "expected_status": status}
    if status == 204:
        public["expected_headers"] = {"x-delete-result": response_case}
    if body is not None:
        public["json"] = body
    if isinstance(expected, list):
        public["expected_json_type"] = "array"
        if expected and isinstance(expected[0], dict):
            public["expected_json_subset"] = expected[0]
    elif expected:
        public["expected_json_subset"] = expected
    st["checker"] = {
        "type": "http_api",
        "app_import": "app.main:app",
        "public_tests": [public],
        "hidden_tests": hidden,
        "timeout_sec": 8,
        "api_focus": {
            "family": family,
            "business_rule": rule,
            "lesson": lesson["title"],
            "stage": st.get("lesson_stage", stage_for_step(st)),
            "response_case": response_case,
            "method": method,
            "path_template": display_route(path),
            "input_shape": "json" if body is not None else "path/query/header",
            "output_contract": expected,
        },
    }


def polish_http_step(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    c = st.get("checker", {})
    if c.get("type") != "http_api":
        return
    public = c.get("public_tests", [{}])[0]
    method = str(public.get("method", "GET")).upper()
    path = str(public.get("path", "/health"))
    template = display_route(path)
    api_focus = c.get("api_focus", {})
    skill = api_focus.get("business_rule") or c.get("contract_focus", {}).get("stage") or "http_contract"
    response_case = api_focus.get("response_case", "observable response contract")
    st["title"] = f"{method} {template}"
    st["body_markdown"] = (
        f"**Коротко:** реализуй HTTP-контракт `{method} {template}` для темы `{lesson['title']}`.\n\n"
        f"### Условие\n"
        f"Добавь endpoint `{method} {template}`. Он должен принимать данные и возвращать статус/JSON ровно по описанному контракту.\n\n"
        f"Бизнес-правило: {skill}. Отдельно проверь вариант ответа: {response_case}.\n\n"
        f"### Позитивный сценарий\n"
        f"`{method} {path}` возвращает `{public.get('expected_status', 200)}`."
    )
    if public.get("json") is not None:
        st["body_markdown"] += f"\n\nТело запроса:\n```json\n{json.dumps(public['json'], ensure_ascii=False, indent=2)}\n```"
    if public.get("params") is not None:
        st["body_markdown"] += f"\n\nQuery-параметры:\n```json\n{json.dumps(public['params'], ensure_ascii=False, indent=2)}\n```"
    if public.get("expected_json_subset") is not None:
        st["body_markdown"] += f"\n\nОтвет содержит:\n```json\n{json.dumps(public['expected_json_subset'], ensure_ascii=False, indent=2)}\n```"
    elif public.get("expected_json_type") == "array":
        st["body_markdown"] += "\n\nОтвет должен быть JSON-массивом."
    if public.get("expected_headers") is not None:
        st["body_markdown"] += f"\n\nОжидаемые заголовки ответа:\n```json\n{json.dumps(public['expected_headers'], ensure_ascii=False, indent=2)}\n```"
    hidden_lines = []
    for test in c.get("hidden_tests", []):
        h_method = str(test.get("method", method)).upper()
        h_path = str(test.get("path", path))
        hidden_lines.append(f"- `{h_method} {h_path}` возвращает `{test.get('expected_status')}`.")
    if hidden_lines:
        st["body_markdown"] += "\n\n### Негативные сценарии\n" + "\n".join(hidden_lines)
    st["body_markdown"] += (
        f"\n\n### Что проверить\n"
        f"Проверь совпадение method, path, status code и формы JSON. Если в условии указан `{template}`, не заменяй его универсальным `/health` или `/tasks`."
    )
    st["solution_code"] = http_solution_for_contract(st, lesson)
    st["editor_initial_code"] = "from fastapi import FastAPI\n\napp = FastAPI()\n\n"
    st["skill_focus"] = f"FastAPI: {lesson['title']} / {method} {template} / {skill} / {response_case}"
    st["new_constraint"] = f"method/path/status/body must match {method} {template} and {response_case}"
    st["edge_case"] = "; ".join(hidden_lines) if hidden_lines else "negative HTTP status is explicit"
    st["input_shape"] = "JSON body" if public.get("json") is not None else "path, query or header parameters"
    st["output_contract"] = f"HTTP {public.get('expected_status', 200)} response for {method} {template} with {response_case}"
    st["qa_notes"] = "Student-facing route/method is generated from checker public and hidden tests."


def sql_rows(schema: str, seed: str, solution: str) -> list[list[Any]]:
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema)
    if seed.strip():
        conn.executescript(seed)
    statements = [part.strip() for part in solution.strip().split(";") if part.strip()]
    rows: list[tuple[Any, ...]] = []
    for idx, statement in enumerate(statements):
        cur = conn.execute(statement)
        if idx == len(statements) - 1:
            rows = cur.fetchall()
    conn.close()
    return [list(row) for row in rows]


def semantic_sql_payload(st: dict[str, Any], lesson: dict[str, Any]) -> tuple[str, str, str, dict[str, Any], str]:
    idx = stable_index(lesson["id"], st["id"]) % 100000
    prefix = f"d{idx}"
    variant = (st["order"] + stable_index(lesson["title"]) % 18) % 18
    low = lesson["title"].lower()
    users = f"{prefix}_users"
    orders = f"{prefix}_orders"
    products = f"{prefix}_products"
    tasks = f"{prefix}_tasks"
    payments = f"{prefix}_payments"
    schema = (
        f"CREATE TABLE {users} (id INTEGER PRIMARY KEY, name TEXT NOT NULL, active INTEGER NOT NULL, email TEXT, manager_id INTEGER);"
        f"CREATE TABLE {products} (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price INTEGER NOT NULL, category TEXT NOT NULL);"
        f"CREATE TABLE {orders} (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, product_id INTEGER, total INTEGER NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL);"
        f"CREATE TABLE {tasks} (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, priority INTEGER NOT NULL DEFAULT 1, due_date TEXT);"
        f"CREATE TABLE {payments} (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL, amount INTEGER NOT NULL, status TEXT NOT NULL);"
    )
    seed = (
        f"INSERT INTO {users} VALUES "
        f"(1, 'Анна', 1, 'anna@example.com', NULL), (2, 'Олег', 1, NULL, 1), (3, 'Маша', 0, 'masha@example.com', 1), (4, 'Лена', 1, 'lena@example.com', NULL);"
        f"INSERT INTO {products} VALUES (1, 'Книга', 700, 'books'), (2, 'Курс', 5000, 'education'), (3, 'Мышь', 1200, 'devices');"
        f"INSERT INTO {orders} VALUES (1, 1, 2, 5700, 'paid', '2026-05-01'), (2, 2, 3, 1200, 'new', '2026-05-02'), (3, 1, 1, 700, 'paid', '2026-05-03');"
        f"INSERT INTO {tasks} VALUES (1, 'Create route', 0, 3, '2026-05-10'), (2, 'Write tests', 1, 2, NULL), (3, 'Fix SQL', 0, 5, '2026-05-04');"
        f"INSERT INTO {payments} VALUES (1, 1, 5700, 'paid'), (2, 2, 1200, 'pending'), (3, 3, 700, 'paid');"
    )
    patterns: list[tuple[str, str, str]] = [
        ("SELECT с алиасами", f"выбери активных пользователей: `id`, `name AS user_name`, `email_status`", f"SELECT id, name AS user_name, CASE WHEN email IS NULL THEN 'missing' ELSE 'ok' END AS email_status FROM {users} WHERE active = 1 ORDER BY id"),
        ("WHERE с NULL", f"найди активных пользователей без email: `id`, `name`", f"SELECT id, name FROM {users} WHERE active = 1 AND email IS NULL ORDER BY id"),
        ("LIKE и IN", f"выбери товары из категорий books/devices с буквой `и` в названии", f"SELECT id, title FROM {products} WHERE category IN ('books', 'devices') AND title LIKE '%и%' ORDER BY title, id"),
        ("ORDER BY tie-breaker", f"верни две ближайшие невыполненные задачи: `id`, `title`, `priority`", f"SELECT id, title, priority FROM {tasks} WHERE done = 0 ORDER BY priority DESC, due_date IS NULL, due_date, id LIMIT 2"),
        ("COUNT(column)", f"посчитай всех пользователей и пользователей с email", f"SELECT COUNT(*) AS users_total, COUNT(email) AS users_with_email FROM {users}"),
        ("GROUP BY/HAVING", f"найди пользователей с оплаченной суммой выше 1000: `user_id`, `paid_total`", f"SELECT user_id, SUM(total) AS paid_total FROM {orders} WHERE status = 'paid' GROUP BY user_id HAVING SUM(total) > 1000 ORDER BY user_id"),
        ("INNER JOIN", f"верни оплаченные заказы с именем пользователя и товаром", f"SELECT {users}.name, {products}.title, {orders}.total FROM {orders} JOIN {users} ON {users}.id = {orders}.user_id JOIN {products} ON {products}.id = {orders}.product_id WHERE {orders}.status = 'paid' ORDER BY {orders}.id"),
        ("self join", f"покажи сотрудников с менеджером: `employee`, `manager`", f"SELECT child.name AS employee, parent.name AS manager FROM {users} AS child JOIN {users} AS parent ON parent.id = child.manager_id ORDER BY child.id"),
        ("LEFT JOIN anti-join", f"найди активных пользователей без заказов", f"SELECT {users}.id, {users}.name FROM {users} LEFT JOIN {orders} ON {orders}.user_id = {users}.id WHERE {users}.active = 1 AND {orders}.id IS NULL ORDER BY {users}.id"),
        ("LEFT JOIN фильтр в ON", f"сохрани активных пользователей без оплаченных заказов", f"SELECT {users}.id, {users}.name, {orders}.id AS paid_order_id FROM {users} LEFT JOIN {orders} ON {orders}.user_id = {users}.id AND {orders}.status = 'paid' WHERE {users}.active = 1 ORDER BY {users}.id, paid_order_id"),
        ("CTE агрегация", f"через CTE посчитай оплаченный total по пользователям", f"WITH paid AS (SELECT user_id, SUM(total) AS paid_total FROM {orders} WHERE status = 'paid' GROUP BY user_id) SELECT {users}.id, {users}.name, paid.paid_total FROM {users} JOIN paid ON paid.user_id = {users}.id ORDER BY {users}.id"),
        ("подзапрос", f"найди заказы дороже среднего заказа", f"SELECT id, user_id, total FROM {orders} WHERE total > (SELECT AVG(total) FROM {orders}) ORDER BY total DESC, id"),
        ("ROW_NUMBER", f"пронумеруй заказы каждого пользователя по сумме", f"SELECT user_id, id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC, id) AS rn FROM {orders} ORDER BY user_id, rn"),
        ("running total", f"посчитай накопительную сумму заказов Анны", f"SELECT id, total, SUM(total) OVER (ORDER BY id) AS running_total FROM {orders} WHERE user_id = 1 ORDER BY id"),
        ("DML UPDATE", f"отметь просроченную задачу выполненной и верни невыполненные", f"UPDATE {tasks} SET done = 1 WHERE title = 'Fix SQL'; SELECT id, title FROM {tasks} WHERE done = 0 ORDER BY priority DESC, id"),
        ("transaction rollback", f"попробуй изменить pending-платёж внутри транзакции и откати изменение", f"BEGIN; UPDATE {payments} SET status = 'paid' WHERE status = 'pending'; ROLLBACK; SELECT id, status FROM {payments} ORDER BY id"),
        ("savepoint", f"зафиксируй оплату заказа 2, но откати ошибочную правку заказа 1 через savepoint", f"BEGIN; UPDATE {payments} SET status = 'paid' WHERE order_id = 2; SAVEPOINT bad_change; UPDATE {payments} SET amount = 0 WHERE order_id = 1; ROLLBACK TO bad_change; RELEASE bad_change; COMMIT; SELECT order_id, amount, status FROM {payments} ORDER BY order_id"),
        ("index diagnostic", f"создай индекс для поиска заказов пользователя и верни имя индекса", f"CREATE INDEX idx_{prefix}_orders_user_status ON {orders}(user_id, status); SELECT name FROM sqlite_master WHERE type = 'index' AND name = 'idx_{prefix}_orders_user_status'"),
    ]
    concept, task, query = patterns[variant]
    solution = query.strip() + ";\n"
    expected = sql_rows(schema, seed, solution)
    hidden_seed = seed + f"INSERT INTO {users} VALUES (20, 'Никита', 1, NULL, NULL); INSERT INTO {orders} VALUES (20, 20, 1, 100, 'cancelled', '2026-05-09');"
    hidden_expected = sql_rows(schema, hidden_seed, solution)
    checker = {
        "type": "sql_query",
        "dialect": "sqlite",
        "schema_sql": schema,
        "seed_sql": seed,
        "public_tests": [{"name": f"{concept}_{prefix}", "expected_rows": expected, "compare": "ordered_rows"}],
        "hidden_tests": [{"name": f"{concept}_{prefix}_edge", "seed_sql": hidden_seed, "expected_rows": hidden_expected, "compare": "ordered_rows"}],
        "semantic_sql_focus": {"concept": concept, "tables": [users, orders, products, tasks, payments]},
    }
    stage = st.get("lesson_stage", stage_for_step(st))
    order_words = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo"]
    order_word = order_words[st["order"] % len(order_words)]
    debug_line = ""
    if stage == "debug":
        debug_line = "\n\n### Что исправить\nDebug-сценарий: найди ошибку в SQL-логике, из-за которой теряются строки, ломается порядок или неверно работает NULL/JOIN/rollback."
    body = (
        f"**Коротко:** {task}.\n\n"
        f"### Условие\n"
        f"В учебной SQLite-базе для темы `{lesson['title']}` есть таблицы `{users}`, `{orders}`, `{products}`, `{tasks}`, `{payments}`. "
        f"Напиши запрос для сценария: {task}.\n\n"
        f"Сценарий SQL-практики: {concept} / {order_word}.\n\n"
        f"### Вход\nSQLite-база уже создана и заполнена данными из задания.\n\n"
        f"### Выход\nВерни только требуемые колонки. Если нужен порядок строк, задай его явно через `ORDER BY`.\n\n"
        f"### Что проверить\nПроверь смысл запроса на строках с отсутствующим email, пользователем без заказов и pending-платежом."
        f"{debug_line}"
    )
    return body, "-- напиши SQL ниже\n", solution, checker, concept


def polish_sql_step(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st.get("checker", {}).get("type") != "sql_query":
        return
    body, editor, solution, checker, concept = semantic_sql_payload(st, lesson)
    st["body_markdown"] = body
    st["editor_initial_code"] = editor
    st["solution_code"] = solution
    st["checker"] = checker
    st["title"] = concept
    st["skill_focus"] = f"SQL: {lesson['title']} / {concept}"
    st["new_constraint"] = f"{lesson['title']}: query must answer {concept} scenario"
    st["edge_case"] = "hidden seed adds a user/order edge case without changing the requested output"
    st["input_shape"] = "SQLite schema, seed data and one SQL query"
    st["output_contract"] = f"ordered rows with explicitly requested columns for {lesson['title']}"
    st["qa_notes"] = "SQL task is generated from semantic schema/query pair; no marker CTE or uniqueness comments are used."


def sqlite_python_payload(st: dict[str, Any], lesson: dict[str, Any]) -> tuple[str, str, str, dict[str, Any]]:
    idx = stable_index(lesson["id"], st["id"]) % 100000
    prefix = f"sqlite_{idx}"
    table = f"tasks_{prefix}"
    create_fn = f"create_{prefix}_db"
    add_fn = f"add_{prefix}_task"
    list_fn = f"list_{prefix}_tasks"
    if st["order"] % 2 == 0:
        body = (
            f"**Коротко:** создай SQLite-файл и таблицу `{table}` через Python.\n\n"
            f"### Условие\nНапиши функцию `{create_fn}(db_path)`. Она создаёт базу, включает `PRAGMA foreign_keys = ON` и таблицу `{table}`.\n\n"
            f"### Выход\nПосле вызова файл базы существует, а таблица содержит поля `id`, `title`, `done`, `created_at`.\n\n"
            f"### Что проверить\nПовторный запуск функции не падает и сохраняет ограничения `NOT NULL`/`DEFAULT`."
        )
        editor = f"import sqlite3\n\n\ndef {create_fn}(db_path):\n    pass\n"
        solution = (
            "import sqlite3\n\n\n"
            f"def {create_fn}(db_path):\n"
            "    conn = sqlite3.connect(db_path)\n"
            "    conn.execute('PRAGMA foreign_keys = ON')\n"
            f"    conn.execute('''CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)''')\n"
            "    conn.commit()\n"
            "    conn.close()\n"
        )
        test_code = (
            f"import sqlite3\nfrom solution import {create_fn}\n\n\n"
            f"def test_create_{prefix}(tmp_path):\n"
            "    db_path = tmp_path / 'app.db'\n"
            f"    {create_fn}(db_path)\n"
            "    conn = sqlite3.connect(db_path)\n"
            f"    columns = conn.execute('PRAGMA table_info({table})').fetchall()\n"
            "    assert [col[1] for col in columns] == ['id', 'title', 'done', 'created_at']\n"
            "    assert columns[1][3] == 1\n"
        )
    else:
        body = (
            f"**Коротко:** сделай repository layer для таблицы `{table}`.\n\n"
            f"### Условие\nРеализуй `{create_fn}(db_path)`, `{add_fn}(db_path, title)` и `{list_fn}(db_path)`. "
            "Вставка использует параметризованный запрос, список возвращается в стабильном порядке.\n\n"
            f"### Что проверить\nНазвание с кавычкой сохраняется как данные, а не ломает SQL."
        )
        editor = f"def {create_fn}(db_path):\n    pass\n\n\ndef {add_fn}(db_path, title):\n    pass\n\n\ndef {list_fn}(db_path):\n    pass\n"
        solution = (
            "import sqlite3\n\n\n"
            f"def {create_fn}(db_path):\n"
            "    conn = sqlite3.connect(db_path)\n"
            f"    conn.execute('''CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)''')\n"
            "    conn.commit()\n"
            "    conn.close()\n\n\n"
            f"def {add_fn}(db_path, title):\n"
            "    conn = sqlite3.connect(db_path)\n"
            f"    conn.execute('INSERT INTO {table} (title, created_at) VALUES (?, ?)', (title, '2026-05-02'))\n"
            "    conn.commit()\n"
            "    conn.close()\n\n\n"
            f"def {list_fn}(db_path):\n"
            "    conn = sqlite3.connect(db_path)\n"
            f"    rows = conn.execute('SELECT id, title, done FROM {table} ORDER BY id').fetchall()\n"
            "    conn.close()\n"
            "    return [{'id': row[0], 'title': row[1], 'done': bool(row[2])} for row in rows]\n"
        )
        test_code = (
            f"from solution import {create_fn}, {add_fn}, {list_fn}\n\n\n"
            f"def test_repository_{prefix}(tmp_path):\n"
            "    db_path = tmp_path / 'app.db'\n"
            f"    {create_fn}(db_path)\n"
            f"    {add_fn}(db_path, \"Bob's task\")\n"
            f"    assert {list_fn}(db_path)[0]['title'] == \"Bob's task\"\n"
        )
    checker = {"type": "python_pytest", "timeout_sec": 6, "test_code": test_code, "hidden_tests": [{"name": "sqlite_edge", "assertion": "uses temp database, commit and parameterized SQL"}]}
    return body, editor, solution, checker


def polish_sqlite_python_step(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st.get("checker", {}).get("type") != "python_pytest":
        return
    if lesson_mode(lesson["title"], lesson.get("roadmap_topics", [])) != "sqlite":
        return
    body, editor, solution, checker = sqlite_python_payload(st, lesson)
    st["body_markdown"] = body
    st["editor_initial_code"] = editor
    st["solution_code"] = solution
    st["checker"] = checker
    st["skill_focus"] = f"SQLite/sqlite3: {lesson['title']} database file, schema and repository"
    st["new_constraint"] = f"{lesson['title']}: temporary database, commit and parameterized SQL"
    st["edge_case"] = "quote in title and repeated migration run"
    st["input_shape"] = "db_path plus repository function arguments"
    st["output_contract"] = f"SQLite file, table schema and ordered rows for {lesson['title']}"


def stdout_practice_body(brief: str, condition: str, input_text: str, output_text: str, examples: list[tuple[str, str]], check: str) -> str:
    example_lines: list[str] = []
    for idx, (inp, out) in enumerate(examples, 1):
        example_lines.append(f"### Пример {idx}\nВвод:\n```text\n{inp.rstrip()}\n```\nВывод:\n```text\n{out.rstrip()}\n```")
    return (
        f"**Коротко:** {brief}.\n\n"
        f"### Условие\n{condition}\n\n"
        f"### Вход\n{input_text}\n\n"
        f"### Выход\n{output_text}\n\n"
        + "\n\n".join(example_lines)
        + f"\n\n### Что проверить\n{check}"
    )


def early_progression_payload(st: dict[str, Any], lesson: dict[str, Any]) -> tuple[str, str, str, str, dict[str, Any], str] | None:
    if not lesson["id"].startswith("v16_m01") or lesson["order"] > 8:
        return None
    title = lesson["title"]
    variant = st["order"] % 5
    scenarios: dict[str, list[dict[str, Any]]] = {
        "Первый код": [
            {"title": "Три строки", "brief": "выведи три строки в заданном порядке", "condition": "Напиши программу, которая выводит строки `Старт`, `Код`, `Готово` каждая с новой строки.", "initial": "", "solution": "print('Старт')\nprint('Код')\nprint('Готово')\n", "public": [("", "Старт\nКод\nГотово\n")], "hidden": [("", "Старт\nКод\nГотово\n")], "focus": "print_order"},
            {"title": "Выражение", "brief": "выведи результат простого выражения", "condition": "Выведи результат выражения `7 + 5` без кавычек и лишнего текста.", "initial": "", "solution": "print(7 + 5)\n", "public": [("", "12\n")], "hidden": [("", "12\n")], "focus": "print_expression"},
            {"title": "Переменная", "brief": "создай переменную и выведи её значение", "condition": "Создай переменную `city` со значением `Москва` и выведи её.", "initial": "city = ''\n", "solution": "city = 'Москва'\nprint(city)\n", "public": [("", "Москва\n")], "hidden": [("", "Москва\n")], "focus": "minimal_variable"},
            {"title": "Без лишнего текста", "brief": "оставь только требуемый вывод", "condition": "Исправь программу так, чтобы она выводила только `Python готов`.", "initial": "print('Ответ: Python готов')\n", "solution": "print('Python готов')\n", "public": [("", "Python готов\n")], "hidden": [("", "Python готов\n")], "focus": "exact_stdout"},
            {"title": "Порядок команд", "brief": "почини порядок строк", "condition": "Программа должна вывести `Первый`, потом `Второй`, потом `Третий`.", "initial": "print('Второй')\nprint('Первый')\nprint('Третий')\n", "solution": "print('Первый')\nprint('Второй')\nprint('Третий')\n", "public": [("", "Первый\nВторой\nТретий\n")], "hidden": [("", "Первый\nВторой\nТретий\n")], "focus": "execution_order"},
        ],
        "Ввод и числа": [
            {"title": "Следующий год", "brief": "прочитай год и выведи следующий", "condition": "На вход подаётся целое число. Преобразуй строку через `int()` и выведи число на 1 больше.", "initial": "year = input()\n", "solution": "year = int(input())\nprint(year + 1)\n", "public": [("2026\n", "2027\n")], "hidden": [("0\n", "1\n"), ("-5\n", "-4\n")], "focus": "input_int_plus"},
            {"title": "Сумма", "brief": "сложи два целых числа из одной строки", "condition": "На вход подаются два целых числа через пробел. Раздели строку через `split()`, преобразуй части в `int` и выведи сумму.", "initial": "a, b = input().split()\n", "solution": "a, b = input().split()\na = int(a)\nb = int(b)\nprint(a + b)\n", "public": [("3 8\n", "11\n")], "hidden": [("-2 7\n", "5\n"), ("0 0\n", "0\n")], "focus": "split_two_ints"},
            {"title": "Цена", "brief": "посчитай стоимость с количеством", "condition": "На вход подаются цена с копейками и количество. Выведи итоговую стоимость.", "initial": "price = input()\ncount = input()\n", "solution": "price = float(input())\ncount = int(input())\nprint(price * count)\n", "public": [("12.5\n4\n", "50.0\n")], "hidden": [("1.25\n8\n", "10.0\n")], "focus": "float_times_int"},
            {"title": "Деление", "brief": "найди среднее двух чисел", "condition": "На вход подаются два числа. Выведи их среднее арифметическое.", "initial": "", "solution": "a = float(input())\nb = float(input())\nprint((a + b) / 2)\n", "public": [("10\n20\n", "15.0\n")], "hidden": [("1\n2\n", "1.5\n")], "focus": "average_float"},
            {"title": "Округление", "brief": "округли результат до двух знаков", "condition": "На вход подаются сумма и количество людей. Выведи долю одного человека, округлённую до 2 знаков.", "initial": "", "solution": "total = float(input())\npeople = int(input())\nprint(round(total / people, 2))\n", "public": [("100\n3\n", "33.33\n")], "hidden": [("10\n4\n", "2.5\n")], "focus": "round_float"},
        ],
        "Строки": [
            {"title": "Края строки", "brief": "убери пробелы по краям", "condition": "Прочитай строку и выведи её без пробелов слева и справа.", "initial": "text = input()\n", "solution": "text = input()\nprint(text.strip())\n", "public": [("  hello  \n", "hello\n")], "hidden": [("\\tPython  \n", "Python\n")], "focus": "strip"},
            {"title": "Регистр", "brief": "приведи email к нижнему регистру", "condition": "Прочитай email, убери пробелы по краям и выведи в нижнем регистре.", "initial": "", "solution": "email = input().strip().lower()\nprint(email)\n", "public": [("  USER@EXAMPLE.COM \n", "user@example.com\n")], "hidden": [("Admin@Site.RU\n", "admin@site.ru\n")], "focus": "strip_lower"},
            {"title": "Срез", "brief": "выведи первые три символа", "condition": "Прочитай строку и выведи первые три символа.", "initial": "", "solution": "text = input()\nprint(text[:3])\n", "public": [("backend\n", "bac\n")], "hidden": [("py\n", "py\n")], "focus": "slice_prefix"},
            {"title": "Замена", "brief": "замени пробелы на дефисы", "condition": "Прочитай строку и выведи её с дефисами вместо пробелов.", "initial": "", "solution": "text = input()\nprint(text.replace(' ', '-'))\n", "public": [("fast api route\n", "fast-api-route\n")], "hidden": [("a b  c\n", "a-b--c\n")], "focus": "replace_spaces"},
            {"title": "Склейка", "brief": "собери строку из слов через точку", "condition": "На вход подаются слова через пробел. Выведи эти слова через точку.", "initial": "", "solution": "words = input().split()\nprint('.'.join(words))\n", "public": [("api v1 tasks\n", "api.v1.tasks\n")], "hidden": [("one\n", "one\n")], "focus": "split_join"},
        ],
        "bool и None": [
            {"title": "Пустая строка", "brief": "проверь truthiness строки", "condition": "Прочитай строку, убери пробелы и выведи `True`, если после этого строка непустая.", "initial": "", "solution": "text = input().strip()\nprint(bool(text))\n", "public": [(" hi \n", "True\n"), ("   \n", "False\n")], "hidden": [("0\n", "True\n")], "focus": "truthiness"},
            {"title": "None", "brief": "сравни значение с None через is", "condition": "В коде есть переменная `value`. Выведи результат проверки `value is None`.", "initial": "value = None\n", "solution": "value = None\nprint(value is None)\n", "public": [("", "True\n")], "hidden": [("", "True\n")], "focus": "is_none"},
            {"title": "Явное сравнение", "brief": "сравни введённый статус", "condition": "Прочитай строку. Выведи `True`, если она равна `ok`, иначе `False`.", "initial": "", "solution": "status = input().strip()\nprint(status == 'ok')\n", "public": [("ok\n", "True\n"), ("error\n", "False\n")], "hidden": [(" OK \n", "False\n")], "focus": "explicit_compare"},
            {"title": "Не равно", "brief": "проверь отличие от пустой строки", "condition": "Прочитай строку и выведи результат сравнения с пустой строкой.", "initial": "", "solution": "text = input()\nprint(text != '')\n", "public": [("x\n", "True\n")], "hidden": [("\\n", "False\n")], "focus": "not_equal_empty"},
            {"title": "Логическое и", "brief": "проверь два простых условия", "condition": "Прочитай два слова. Выведи `True`, если первое равно `yes` и второе равно `ok`.", "initial": "", "solution": "first = input().strip()\nsecond = input().strip()\nprint(first == 'yes' and second == 'ok')\n", "public": [("yes\nok\n", "True\n")], "hidden": [("yes\nno\n", "False\n")], "focus": "and_compare"},
        ],
        "Условия": [
            {"title": "Возраст", "brief": "выбери ответ по возрасту", "condition": "Если возраст 18 или больше, выведи `Можно`, иначе `Нельзя`.", "initial": "age = int(input())\n", "solution": "age = int(input())\nif age >= 18:\n    print('Можно')\nelse:\n    print('Нельзя')\n", "public": [("17\n", "Нельзя\n"), ("18\n", "Можно\n")], "hidden": [("99\n", "Можно\n")], "focus": "if_else_boundary"},
            {"title": "Статус", "brief": "обработай три варианта", "condition": "Прочитай статус. Для `new` выведи `Создать`, для `done` выведи `Закрыть`, иначе `Проверить`.", "initial": "", "solution": "status = input().strip()\nif status == 'new':\n    print('Создать')\nelif status == 'done':\n    print('Закрыть')\nelse:\n    print('Проверить')\n", "public": [("new\n", "Создать\n"), ("done\n", "Закрыть\n")], "hidden": [("hold\n", "Проверить\n")], "focus": "elif"},
            {"title": "Guard", "brief": "сначала проверь плохой ввод", "condition": "Прочитай число. Если оно меньше 0, выведи `Ошибка`, иначе выведи само число.", "initial": "", "solution": "value = int(input())\nif value < 0:\n    print('Ошибка')\nelse:\n    print(value)\n", "public": [("-1\n", "Ошибка\n"), ("5\n", "5\n")], "hidden": [("0\n", "0\n")], "focus": "guard_condition"},
            {"title": "Диапазон", "brief": "проверь попадание в диапазон", "condition": "Прочитай балл. Если он от 0 до 100 включительно, выведи `OK`, иначе `BAD`.", "initial": "", "solution": "score = int(input())\nif 0 <= score <= 100:\n    print('OK')\nelse:\n    print('BAD')\n", "public": [("100\n", "OK\n"), ("101\n", "BAD\n")], "hidden": [("-1\n", "BAD\n")], "focus": "range_condition"},
            {"title": "Вложенная проверка", "brief": "сначала проверь роль, потом действие", "condition": "Прочитай роль и действие. Роль `owner` может `delete`, остальные нет.", "initial": "", "solution": "role = input().strip()\naction = input().strip()\nif role == 'owner':\n    if action == 'delete':\n        print('Разрешено')\n    else:\n        print('Не нужно')\nelse:\n    print('Запрещено')\n", "public": [("owner\ndelete\n", "Разрешено\n")], "hidden": [("user\ndelete\n", "Запрещено\n")], "focus": "nested_if"},
        ],
        "Типы и память": [
            {"title": "Тип", "brief": "посмотри имя типа после преобразования", "condition": "Прочитай строку, преобразуй её в `int` и выведи имя типа результата.", "initial": "", "solution": "value = int(input())\nprint(type(value).__name__)\n", "public": [("12\n", "int\n")], "hidden": [("-7\n", "int\n")], "focus": "type_name"},
            {"title": "Строка плюс число", "brief": "исправь смешение типов", "condition": "Прочитай число как строку, преобразуй в `int` и прибавь 10.", "initial": "value = input()\nprint(value + 10)\n", "solution": "value = int(input())\nprint(value + 10)\n", "public": [("5\n", "15\n")], "hidden": [("0\n", "10\n")], "focus": "type_conversion_debug"},
            {"title": "Копия значения", "brief": "покажи, что новое присваивание не меняет старое число", "condition": "Создай `a = 5`, `b = a`, затем измени `b` на 9 и выведи `a`.", "initial": "", "solution": "a = 5\nb = a\nb = 9\nprint(a)\n", "public": [("", "5\n")], "hidden": [("", "5\n")], "focus": "assignment_value"},
            {"title": "Float", "brief": "преобразуй строку в число с точкой", "condition": "Прочитай число с точкой, прибавь `0.5` и выведи результат.", "initial": "", "solution": "value = float(input())\nprint(value + 0.5)\n", "public": [("1.5\n", "2.0\n")], "hidden": [("0\n", "0.5\n")], "focus": "float_conversion"},
            {"title": "Str", "brief": "склей число и текст безопасно", "condition": "Прочитай число и выведи строку `id=<число>`.", "initial": "", "solution": "value = int(input())\nprint('id=' + str(value))\n", "public": [("42\n", "id=42\n")], "hidden": [("0\n", "id=0\n")], "focus": "str_conversion"},
        ],
        "Циклы": [
            {"title": "Range", "brief": "выведи числа от 1 до n", "condition": "Прочитай `n` и выведи числа от 1 до `n`, каждое с новой строки.", "initial": "", "solution": "n = int(input())\nfor number in range(1, n + 1):\n    print(number)\n", "public": [("3\n", "1\n2\n3\n")], "hidden": [("1\n", "1\n")], "focus": "for_range"},
            {"title": "Сумма цикла", "brief": "посчитай сумму от 1 до n", "condition": "Прочитай `n` и выведи сумму чисел от 1 до `n`.", "initial": "", "solution": "n = int(input())\ntotal = 0\nfor number in range(1, n + 1):\n    total += number\nprint(total)\n", "public": [("4\n", "10\n")], "hidden": [("1\n", "1\n")], "focus": "loop_accumulator"},
            {"title": "While", "brief": "уменьшай число до нуля", "condition": "Прочитай `n` и выведи обратный отсчёт до 1.", "initial": "", "solution": "n = int(input())\nwhile n > 0:\n    print(n)\n    n -= 1\n", "public": [("3\n", "3\n2\n1\n")], "hidden": [("1\n", "1\n")], "focus": "while_countdown"},
            {"title": "Break", "brief": "остановись на стоп-слове", "condition": "Читай строки, пока не встретишь `stop`. Выводи каждую строку до `stop`.", "initial": "", "solution": "while True:\n    text = input()\n    if text == 'stop':\n        break\n    print(text)\n", "public": [("a\nb\nstop\n", "a\nb\n")], "hidden": [("stop\n", "")], "focus": "break_loop"},
            {"title": "Continue", "brief": "пропусти пустые строки", "condition": "Прочитай количество строк, затем строки. Выводи только непустые.", "initial": "", "solution": "n = int(input())\nfor _ in range(n):\n    text = input()\n    if text == '':\n        continue\n    print(text)\n", "public": [("3\na\n\nb\n", "a\nb\n")], "hidden": [("1\n\n", "")], "focus": "continue_empty"},
        ],
        "Списки": [
            {"title": "Индекс", "brief": "выведи элемент по индексу", "condition": "В коде есть список. Прочитай индекс и выведи элемент списка.", "initial": "items = ['api', 'sql', 'git']\n", "solution": "items = ['api', 'sql', 'git']\nindex = int(input())\nprint(items[index])\n", "public": [("1\n", "sql\n")], "hidden": [("0\n", "api\n")], "focus": "list_index"},
            {"title": "Append", "brief": "добавь элемент в конец списка", "condition": "В коде есть список. Прочитай новое слово, добавь его через `append` и выведи длину списка.", "initial": "items = ['api']\n", "solution": "items = ['api']\nitem = input().strip()\nitems.append(item)\nprint(len(items))\n", "public": [("sql\n", "2\n")], "hidden": [("git\n", "2\n")], "focus": "list_append"},
            {"title": "Копия", "brief": "измени копию списка", "condition": "Скопируй список через `.copy()`, добавь в копию слово `new` и выведи длину исходного списка.", "initial": "items = ['old']\n", "solution": "items = ['old']\ncopy_items = items.copy()\ncopy_items.append('new')\nprint(len(items))\n", "public": [("", "1\n")], "hidden": [("", "1\n")], "focus": "list_copy"},
            {"title": "Фильтр", "brief": "оставь положительные числа", "condition": "Прочитай числа через пробел. Выведи положительные числа через пробел.", "initial": "", "solution": "numbers = [int(x) for x in input().split()]\npositive = [x for x in numbers if x > 0]\nprint(' '.join(str(x) for x in positive))\n", "public": [("-1 2 0 5\n", "2 5\n")], "hidden": [("-3 -2\n", "\n")], "focus": "list_comprehension"},
            {"title": "Мутация", "brief": "замени первый элемент списка", "condition": "В коде есть список. Прочитай слово, замени первый элемент и выведи список через пробел.", "initial": "items = ['old', 'api']\n", "solution": "items = ['old', 'api']\nitems[0] = input().strip()\nprint(' '.join(items))\n", "public": [("new\n", "new api\n")], "hidden": [("fix\n", "fix api\n")], "focus": "list_mutation"},
        ],
    }
    items = scenarios.get(title)
    if not items:
        return None
    item = items[variant % len(items)]
    examples = item["public"][:2]
    body = stdout_practice_body(item["brief"], item["condition"], "Данные приходят из стандартного ввода. Если вход не нужен, оставь программу без `input()`.", "Выведи ровно то, что требуется в условии.", examples, "Сравни вывод с примером: важны пробелы, регистр и отсутствие лишнего текста.")
    checker = stdout_checker(item["public"], item.get("hidden", item["public"]))
    return item["title"], body, item["initial"], item["solution"], checker, item["focus"]


def pytest_payload(title: str, st: dict[str, Any], lesson: dict[str, Any]) -> tuple[str, str, str, str, str, str, str, str]:
    low = title.lower()
    stage = st.get("lesson_stage", stage_for_step(st))
    variant = stable_index(title, st.get("title", ""), stage, st["order"])
    step_slug = slug(st.get("title", "step")).replace("-", "_") or "step"
    order_words = [
        "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
        "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
        "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray",
    ]
    order_word = order_words[st["order"] % len(order_words)]
    suffix = f"{slug(title).replace('-', '_')}_{step_slug}_{order_word}"
    category = f"topic_{slug(title)[:24]}"
    if "dataclass" in low:
        category = "oop_dataclasses"
        cases = [
            ("invoice_total", "создай @dataclass для строки счёта и посчитай итог", "from dataclasses import dataclass\n\n\n@dataclass\nclass InvoiceLine_{suffix}:\n    title: str\n    price: int\n    qty: int = 1\n\n    def total(self):\n        return self.price * self.qty\n\n\ndef invoice_total_{suffix}(title, price, qty):\n    line = InvoiceLine_{suffix}(title=title, price=price, qty=qty)\n    return line.total()\n", "'api', 700, 3", "2100", "source = inspect.getsource(solution_module)\nassert '@dataclass' in source\nassert 'InvoiceLine' in source\nassert invoice_total_{suffix}('x', 10, 1) == 10"),
            ("tag_bucket", "используй field(default_factory=list) для независимых списков", "from dataclasses import dataclass, field\n\n\n@dataclass\nclass TagBucket_{suffix}:\n    name: str\n    tags: list[str] = field(default_factory=list)\n\n    def add(self, tag):\n        self.tags.append(tag)\n        return list(self.tags)\n\n\ndef tag_bucket_{suffix}(first, second):\n    left = TagBucket_{suffix}('left')\n    right = TagBucket_{suffix}('right')\n    left.add(first)\n    right.add(second)\n    return left.tags, right.tags\n", "'api', 'sql'", "(['api'], ['sql'])", "source = inspect.getsource(solution_module)\nassert 'default_factory' in source\nassert tag_bucket_{suffix}('a', 'b') == (['a'], ['b'])"),
            ("frozen_money", "сделай frozen dataclass для value object денег", "from dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass Money_{suffix}:\n    cents: int\n    currency: str = 'RUB'\n\n    def label(self):\n        return f'{{self.cents}} {{self.currency}}'\n\n\ndef frozen_money_{suffix}(cents):\n    return Money_{suffix}(cents).label()\n", "1250", "'1250 RUB'", "source = inspect.getsource(solution_module)\nassert 'frozen=True' in source\nassert frozen_money_{suffix}(0) == '0 RUB'"),
            ("ordered_priority", "используй order=True для сортировки приоритетов", "from dataclasses import dataclass\n\n\n@dataclass(order=True)\nclass Priority_{suffix}:\n    level: int\n    title: str\n\n\ndef ordered_priority_{suffix}(items):\n    priorities = [Priority_{suffix}(level, title) for level, title in items]\n    return [item.title for item in sorted(priorities)]\n", "[(2, 'sql'), (1, 'api')]", "['api', 'sql']", "source = inspect.getsource(solution_module)\nassert 'order=True' in source\nassert ordered_priority_{suffix}([]) == []"),
            ("post_init_slug", "проверь инвариант в __post_init__", "from dataclasses import dataclass\n\n\n@dataclass\nclass Slug_{suffix}:\n    value: str\n\n    def __post_init__(self):\n        cleaned = self.value.strip().lower().replace(' ', '-')\n        if not cleaned:\n            raise ValueError('slug required')\n        self.value = cleaned\n\n\ndef post_init_slug_{suffix}(raw):\n    return Slug_{suffix}(raw).value\n", "' API Route '", "'api-route'", "source = inspect.getsource(solution_module)\nassert '__post_init__' in source\nwith pytest.raises(ValueError):\n    post_init_slug_{suffix}('   ')"),
        ]
    elif "магичес" in low:
        category = "oop_magic_methods"
        cases = [
            ("money_add", "реализуй __add__ для value object денег", "class Money_{suffix}:\n    def __init__(self, cents):\n        self.cents = cents\n\n    def __add__(self, other):\n        return Money_{suffix}(self.cents + other.cents)\n\n    def __repr__(self):\n        return f'Money({{self.cents}})'\n\n\ndef money_add_{suffix}(left, right):\n    return repr(Money_{suffix}(left) + Money_{suffix}(right))\n", "100, 50", "'Money(150)'", "source = inspect.getsource(solution_module)\nassert '__add__' in source and '__repr__' in source\nassert money_add_{suffix}(0, 0) == 'Money(0)'"),
            ("task_eq", "сравни задачи по id через __eq__", "class Task_{suffix}:\n    def __init__(self, task_id, title):\n        self.task_id = task_id\n        self.title = title\n\n    def __eq__(self, other):\n        if not isinstance(other, Task_{suffix}):\n            return NotImplemented\n        return self.task_id == other.task_id\n\n\ndef task_eq_{suffix}(left_id, right_id):\n    return Task_{suffix}(left_id, 'a') == Task_{suffix}(right_id, 'b')\n", "1, 1", "True", "source = inspect.getsource(solution_module)\nassert '__eq__' in source\nassert task_eq_{suffix}(1, 2) is False"),
            ("queue_len", "верни длину очереди через __len__", "class ReviewQueue_{suffix}:\n    def __init__(self, items):\n        self.items = list(items)\n\n    def __len__(self):\n        return len(self.items)\n\n\ndef queue_len_{suffix}(items):\n    return len(ReviewQueue_{suffix}(items))\n", "['a', 'b']", "2", "source = inspect.getsource(solution_module)\nassert '__len__' in source\nassert queue_len_{suffix}([]) == 0"),
            ("tag_contains", "проверь членство через __contains__", "class TagSet_{suffix}:\n    def __init__(self, tags):\n        self.tags = {tag.lower() for tag in tags}\n\n    def __contains__(self, tag):\n        return tag.lower() in self.tags\n\n\ndef tag_contains_{suffix}(tags, needle):\n    return needle in TagSet_{suffix}(tags)\n", "['API'], 'api'", "True", "source = inspect.getsource(solution_module)\nassert '__contains__' in source\nassert tag_contains_{suffix}(['sql'], 'api') is False"),
            ("priority_lt", "отсортируй объекты через __lt__", "class Priority_{suffix}:\n    def __init__(self, title, level):\n        self.title = title\n        self.level = level\n\n    def __lt__(self, other):\n        return (self.level, self.title) < (other.level, other.title)\n\n\ndef priority_lt_{suffix}(items):\n    values = [Priority_{suffix}(title, level) for title, level in items]\n    return [item.title for item in sorted(values)]\n", "[('sql', 2), ('api', 1)]", "['api', 'sql']", "source = inspect.getsource(solution_module)\nassert '__lt__' in source\nassert priority_lt_{suffix}([]) == []"),
        ]
    elif "протокол" in low:
        category = "oop_protocols"
        cases = [
            ("json_writer_protocol", "опиши Protocol для writer-объекта", "from typing import Protocol\n\n\nclass JsonWriter_{suffix}(Protocol):\n    def write_json(self, payload: dict) -> str: ...\n\n\nclass MemoryWriter_{suffix}:\n    def write_json(self, payload: dict) -> str:\n        return f\"json:{{sorted(payload)}}\"\n\n\ndef json_writer_protocol_{suffix}(payload):\n    writer: JsonWriter_{suffix} = MemoryWriter_{suffix}()\n    return writer.write_json(payload)\n", "{'b': 2, 'a': 1}", "'json:['a', 'b']'", "source = inspect.getsource(solution_module)\nassert 'Protocol' in source\nassert json_writer_protocol_{suffix}({}) == 'json:[]'"),
            ("repository_protocol", "проверь структурную совместимость repository", "from typing import Protocol\n\n\nclass TaskRepository_{suffix}(Protocol):\n    def get_title(self, task_id: int) -> str: ...\n\n\nclass InMemoryTasks_{suffix}:\n    def __init__(self, rows):\n        self.rows = rows\n    def get_title(self, task_id: int) -> str:\n        return self.rows[task_id]\n\n\ndef repository_protocol_{suffix}(rows, task_id):\n    repo: TaskRepository_{suffix} = InMemoryTasks_{suffix}(rows)\n    return repo.get_title(task_id)\n", "{1: 'api'}, 1", "'api'", "source = inspect.getsource(solution_module)\nassert 'Protocol' in source and 'get_title' in source\nassert repository_protocol_{suffix}({2:'x'}, 2) == 'x'"),
            ("sendable_duck", "используй duck typing через Protocol", "from typing import Protocol\n\n\nclass Sendable_{suffix}(Protocol):\n    def send(self, text: str) -> bool: ...\n\n\nclass FakeSender_{suffix}:\n    def __init__(self):\n        self.sent = []\n    def send(self, text: str) -> bool:\n        self.sent.append(text)\n        return True\n\n\ndef sendable_duck_{suffix}(text):\n    sender: Sendable_{suffix} = FakeSender_{suffix}()\n    return sender.send(text)\n", "'hello'", "True", "source = inspect.getsource(solution_module)\nassert 'Protocol' in source\nassert sendable_duck_{suffix}('') is True"),
            ("render_protocol", "прими любой объект с render()", "from typing import Protocol\n\n\nclass Renderable_{suffix}(Protocol):\n    def render(self) -> str: ...\n\n\nclass Badge_{suffix}:\n    def __init__(self, text):\n        self.text = text\n    def render(self) -> str:\n        return f'[{self.text}]'\n\n\ndef render_protocol_{suffix}(text):\n    item: Renderable_{suffix} = Badge_{suffix}(text)\n    return item.render()\n", "'ok'", "'[ok]'", "source = inspect.getsource(solution_module)\nassert 'Protocol' in source\nassert render_protocol_{suffix}('') == '[]'"),
            ("runtime_protocol_check", "сделай runtime_checkable Protocol", "from typing import Protocol, runtime_checkable\n\n\n@runtime_checkable\nclass Closable_{suffix}(Protocol):\n    def close(self) -> None: ...\n\n\nclass Connection_{suffix}:\n    def close(self) -> None:\n        self.closed = True\n\n\ndef runtime_protocol_check_{suffix}():\n    conn = Connection_{suffix}()\n    return isinstance(conn, Closable_{suffix})\n", "", "True", "source = inspect.getsource(solution_module)\nassert 'runtime_checkable' in source\nassert runtime_protocol_check_{suffix}() is True"),
        ]
    elif "наслед" in low:
        category = "oop_inheritance"
        cases = [
            ("email_notification", "создай subclass и override метода", "class Notification_{suffix}:\n    def __init__(self, recipient):\n        self.recipient = recipient\n\n    def channel(self):\n        return 'base'\n\n\nclass EmailNotification_{suffix}(Notification_{suffix}):\n    def channel(self):\n        return 'email'\n\n\ndef email_notification_{suffix}(recipient):\n    note = EmailNotification_{suffix}(recipient)\n    return f'{{note.channel()}}:{{note.recipient}}'\n", "'a@example.com'", "'email:a@example.com'", "source = inspect.getsource(solution_module)\nassert '(Notification_' in source and 'class EmailNotification' in source\nassert email_notification_{suffix}('x') == 'email:x'"),
            ("super_init", "используй super() для базового состояния", "class BaseUser_{suffix}:\n    def __init__(self, name):\n        self.name = name.strip()\n\n\nclass StaffUser_{suffix}(BaseUser_{suffix}):\n    def __init__(self, name, role):\n        super().__init__(name)\n        self.role = role\n\n\ndef super_init_{suffix}(name, role):\n    user = StaffUser_{suffix}(name, role)\n    return f'{{user.name}}:{{user.role}}'\n", "' Anna ', 'mentor'", "'Anna:mentor'", "source = inspect.getsource(solution_module)\nassert 'super()' in source\nassert super_init_{suffix}(' O ', 'dev') == 'O:dev'"),
            ("base_parser", "переопредели parse() в наследнике", "class Parser_{suffix}:\n    def parse(self, raw):\n        return raw\n\n\nclass IntParser_{suffix}(Parser_{suffix}):\n    def parse(self, raw):\n        return int(raw)\n\n\ndef base_parser_{suffix}(raw):\n    parser = IntParser_{suffix}()\n    return parser.parse(raw)\n", "'42'", "42", "source = inspect.getsource(solution_module)\nassert 'class IntParser' in source and '(Parser_' in source\nassert base_parser_{suffix}('-1') == -1"),
            ("override_price", "измени расчёт цены в subclass", "class PricePolicy_{suffix}:\n    def price(self, amount):\n        return amount\n\n\nclass DiscountPolicy_{suffix}(PricePolicy_{suffix}):\n    def price(self, amount):\n        return int(super().price(amount) * 0.9)\n\n\ndef override_price_{suffix}(amount):\n    return DiscountPolicy_{suffix}().price(amount)\n", "1000", "900", "source = inspect.getsource(solution_module)\nassert 'super()' in source and 'DiscountPolicy' in source\nassert override_price_{suffix}(0) == 0"),
            ("template_method", "задай общий алгоритм в base class", "class Exporter_{suffix}:\n    def export(self, value):\n        return self.prefix() + str(value)\n    def prefix(self):\n        return ''\n\n\nclass JsonExporter_{suffix}(Exporter_{suffix}):\n    def prefix(self):\n        return 'json:'\n\n\ndef template_method_{suffix}(value):\n    return JsonExporter_{suffix}().export(value)\n", "7", "'json:7'", "source = inspect.getsource(solution_module)\nassert 'class JsonExporter' in source and '(Exporter_' in source\nassert template_method_{suffix}('x') == 'json:x'"),
        ]
    elif "полиморф" in low:
        category = "oop_polymorphism"
        cases = [
            ("render_many", "обработай разные реализации общего интерфейса", "class HtmlButton_{suffix}:\n    def render(self):\n        return '<button>OK</button>'\n\n\nclass TextButton_{suffix}:\n    def render(self):\n        return '[OK]'\n\n\ndef render_many_{suffix}(mode):\n    widgets = [HtmlButton_{suffix}(), TextButton_{suffix}()]\n    return [widget.render() for widget in widgets if mode != 'text' or isinstance(widget, TextButton_{suffix})]\n", "'all'", "['<button>OK</button>', '[OK]']", "source = inspect.getsource(solution_module)\nassert 'class HtmlButton' in source and 'class TextButton' in source\nassert render_many_{suffix}('text') == ['[OK]']"),
            ("calculate_fees", "примени разные fee policies через один вызов", "class FixedFee_{suffix}:\n    def fee(self, amount):\n        return 100\n\n\nclass PercentFee_{suffix}:\n    def fee(self, amount):\n        return amount // 10\n\n\ndef calculate_fees_{suffix}(amount):\n    policies = [FixedFee_{suffix}(), PercentFee_{suffix}()]\n    return [policy.fee(amount) for policy in policies]\n", "1000", "[100, 100]", "source = inspect.getsource(solution_module)\nassert '.fee(' in source\nassert calculate_fees_{suffix}(50) == [100, 5]"),
            ("notify_all", "отправь сообщение через разные каналы", "class EmailChannel_{suffix}:\n    def send(self, text):\n        return 'email:' + text\n\n\nclass SmsChannel_{suffix}:\n    def send(self, text):\n        return 'sms:' + text\n\n\ndef notify_all_{suffix}(text):\n    return [channel.send(text) for channel in [EmailChannel_{suffix}(), SmsChannel_{suffix}()]]\n", "'hi'", "['email:hi', 'sms:hi']", "source = inspect.getsource(solution_module)\nassert 'EmailChannel' in source and 'SmsChannel' in source\nassert notify_all_{suffix}('') == ['email:', 'sms:']"),
            ("serialize_resources", "используй общий метод to_dict()", "class UserResource_{suffix}:\n    def to_dict(self):\n        return {'type': 'user'}\n\n\nclass TaskResource_{suffix}:\n    def to_dict(self):\n        return {'type': 'task'}\n\n\ndef serialize_resources_{suffix}():\n    return [item.to_dict()['type'] for item in [UserResource_{suffix}(), TaskResource_{suffix}()]]\n", "", "['user', 'task']", "source = inspect.getsource(solution_module)\nassert '.to_dict' in source\nassert serialize_resources_{suffix}() == ['user', 'task']"),
            ("score_strategies", "подставь разные стратегии scoring", "class ExactScore_{suffix}:\n    def score(self, value):\n        return value\n\n\nclass BonusScore_{suffix}:\n    def score(self, value):\n        return value + 10\n\n\ndef score_strategies_{suffix}(value):\n    return max(strategy.score(value) for strategy in [ExactScore_{suffix}(), BonusScore_{suffix}()])\n", "5", "15", "source = inspect.getsource(solution_module)\nassert 'BonusScore' in source\nassert score_strategies_{suffix}(0) == 10"),
        ]
    elif "абстрак" in low:
        category = "oop_abstractions"
        cases = [
            ("gateway_abc", "создай ABC и конкретную реализацию", "from abc import ABC, abstractmethod\n\n\nclass PaymentGateway_{suffix}(ABC):\n    @abstractmethod\n    def charge(self, amount): ...\n\n\nclass FakeGateway_{suffix}(PaymentGateway_{suffix}):\n    def charge(self, amount):\n        return {'charged': amount}\n\n\ndef gateway_abc_{suffix}(amount):\n    return FakeGateway_{suffix}().charge(amount)\n", "500", "{'charged': 500}", "source = inspect.getsource(solution_module)\nassert 'ABC' in source and 'abstractmethod' in source\nassert gateway_abc_{suffix}(0) == {'charged': 0}"),
            ("repository_abc", "запрети неполный repository через abstractmethod", "from abc import ABC, abstractmethod\n\n\nclass Repository_{suffix}(ABC):\n    @abstractmethod\n    def get(self, key): ...\n\n\nclass MemoryRepository_{suffix}(Repository_{suffix}):\n    def __init__(self, data):\n        self.data = data\n    def get(self, key):\n        return self.data.get(key)\n\n\ndef repository_abc_{suffix}(data, key):\n    return MemoryRepository_{suffix}(data).get(key)\n", "{'a': 1}, 'a'", "1", "source = inspect.getsource(solution_module)\nassert 'abstractmethod' in source\nassert repository_abc_{suffix}({}, 'x') is None"),
            ("parser_template_abc", "задай абстрактный parse", "from abc import ABC, abstractmethod\n\n\nclass PayloadParser_{suffix}(ABC):\n    @abstractmethod\n    def parse(self, raw): ...\n\n\nclass CsvParser_{suffix}(PayloadParser_{suffix}):\n    def parse(self, raw):\n        return [part.strip() for part in raw.split(',')]\n\n\ndef parser_template_abc_{suffix}(raw):\n    return CsvParser_{suffix}().parse(raw)\n", "'a, b'", "['a', 'b']", "source = inspect.getsource(solution_module)\nassert 'PayloadParser' in source and 'abstractmethod' in source\nassert parser_template_abc_{suffix}('') == ['']"),
            ("policy_abc", "реализуй policy через ABC", "from abc import ABC, abstractmethod\n\n\nclass AccessPolicy_{suffix}(ABC):\n    @abstractmethod\n    def allow(self, role): ...\n\n\nclass StaffOnlyPolicy_{suffix}(AccessPolicy_{suffix}):\n    def allow(self, role):\n        return role in {'mentor', 'owner'}\n\n\ndef policy_abc_{suffix}(role):\n    return StaffOnlyPolicy_{suffix}().allow(role)\n", "'mentor'", "True", "source = inspect.getsource(solution_module)\nassert 'AccessPolicy' in source and 'abstractmethod' in source\nassert policy_abc_{suffix}('student') is False"),
            ("exporter_abc", "скрой общий контракт exporter за ABC", "from abc import ABC, abstractmethod\n\n\nclass Exporter_{suffix}(ABC):\n    @abstractmethod\n    def export(self, rows): ...\n\n\nclass CountExporter_{suffix}(Exporter_{suffix}):\n    def export(self, rows):\n        return {'rows': len(rows)}\n\n\ndef exporter_abc_{suffix}(rows):\n    return CountExporter_{suffix}().export(rows)\n", "[1, 2]", "{'rows': 2}", "source = inspect.getsource(solution_module)\nassert 'ABC' in source\nassert exporter_abc_{suffix}([]) == {'rows': 0}"),
        ]
    elif "инкапсул" in low:
        category = "oop_encapsulation"
        cases = [
            ("email_property", "защити email через property и validation", "class UserEmail_{suffix}:\n    def __init__(self, email):\n        self.email = email\n\n    @property\n    def email(self):\n        return self._email\n\n    @email.setter\n    def email(self, value):\n        if '@' not in value:\n            raise ValueError('invalid email')\n        self._email = value.lower()\n\n\ndef email_property_{suffix}(raw):\n    return UserEmail_{suffix}(raw).email\n", "'A@EXAMPLE.COM'", "'a@example.com'", "source = inspect.getsource(solution_module)\nassert '@property' in source and '_email' in source\nwith pytest.raises(ValueError):\n    email_property_{suffix}('bad')"),
            ("balance_invariant", "не дай балансу стать отрицательным", "class Wallet_{suffix}:\n    def __init__(self, balance=0):\n        self._balance = balance\n\n    @property\n    def balance(self):\n        return self._balance\n\n    def withdraw(self, amount):\n        if amount > self._balance:\n            raise ValueError('not enough money')\n        self._balance -= amount\n        return self._balance\n\n\ndef balance_invariant_{suffix}(balance, amount):\n    return Wallet_{suffix}(balance).withdraw(amount)\n", "100, 40", "60", "source = inspect.getsource(solution_module)\nassert '_balance' in source and '@property' in source\nwith pytest.raises(ValueError):\n    balance_invariant_{suffix}(10, 20)"),
            ("status_transition", "спрячь состояние и проверь переход", "class TaskState_{suffix}:\n    def __init__(self):\n        self._status = 'new'\n\n    @property\n    def status(self):\n        return self._status\n\n    def close(self):\n        if self._status != 'new':\n            raise ValueError('bad transition')\n        self._status = 'done'\n        return self._status\n\n\ndef status_transition_{suffix}():\n    task = TaskState_{suffix}()\n    return task.close()\n", "", "'done'", "source = inspect.getsource(solution_module)\nassert '_status' in source and '@property' in source\nassert status_transition_{suffix}() == 'done'"),
            ("priority_setter", "валидируй priority через setter", "class PriorityBox_{suffix}:\n    def __init__(self, priority):\n        self.priority = priority\n\n    @property\n    def priority(self):\n        return self._priority\n\n    @priority.setter\n    def priority(self, value):\n        if not 1 <= value <= 5:\n            raise ValueError('priority out of range')\n        self._priority = value\n\n\ndef priority_setter_{suffix}(value):\n    return PriorityBox_{suffix}(value).priority\n", "3", "3", "source = inspect.getsource(solution_module)\nassert '@priority.setter' in source\nwith pytest.raises(ValueError):\n    priority_setter_{suffix}(0)"),
            ("token_mask", "отдавай только masked token", "class ApiToken_{suffix}:\n    def __init__(self, raw):\n        if len(raw) < 4:\n            raise ValueError('short token')\n        self._raw = raw\n\n    @property\n    def masked(self):\n        return '***' + self._raw[-4:]\n\n\ndef token_mask_{suffix}(raw):\n    return ApiToken_{suffix}(raw).masked\n", "'abcdef'", "'***cdef'", "source = inspect.getsource(solution_module)\nassert '_raw' in source and '@property' in source\nwith pytest.raises(ValueError):\n    token_mask_{suffix}('abc')"),
        ]
    elif "композиц" in low:
        category = "oop_composition"
        cases = [
            ("cart_money", "помести Money внутрь Cart", "class Money_{suffix}:\n    def __init__(self, cents):\n        self.cents = cents\n\n\nclass Cart_{suffix}:\n    def __init__(self):\n        self.items = []\n    def add(self, money):\n        self.items.append(money)\n    def total(self):\n        return sum(item.cents for item in self.items)\n\n\ndef cart_money_{suffix}(amounts):\n    cart = Cart_{suffix}()\n    for amount in amounts:\n        cart.add(Money_{suffix}(amount))\n    return cart.total()\n", "[100, 50]", "150", "source = inspect.getsource(solution_module)\nassert 'Cart_' in source and 'Money_' in source\nassert cart_money_{suffix}([]) == 0"),
            ("service_repository", "service делегирует чтение repository", "class TaskRepository_{suffix}:\n    def __init__(self, rows):\n        self.rows = rows\n    def titles(self):\n        return [row['title'] for row in self.rows]\n\n\nclass TaskService_{suffix}:\n    def __init__(self, repository):\n        self.repository = repository\n    def list_titles(self):\n        return self.repository.titles()\n\n\ndef service_repository_{suffix}(rows):\n    return TaskService_{suffix}(TaskRepository_{suffix}(rows)).list_titles()\n", "[{'title':'api'}]", "['api']", "source = inspect.getsource(solution_module)\nassert 'TaskService' in source and 'repository' in source\nassert service_repository_{suffix}([]) == []"),
            ("invoice_lines", "Invoice состоит из LineItem объектов", "class LineItem_{suffix}:\n    def __init__(self, price, qty):\n        self.price = price\n        self.qty = qty\n    def total(self):\n        return self.price * self.qty\n\n\nclass Invoice_{suffix}:\n    def __init__(self, lines):\n        self.lines = lines\n    def total(self):\n        return sum(line.total() for line in self.lines)\n\n\ndef invoice_lines_{suffix}(pairs):\n    return Invoice_{suffix}([LineItem_{suffix}(p, q) for p, q in pairs]).total()\n", "[(10, 2), (5, 1)]", "25", "source = inspect.getsource(solution_module)\nassert 'Invoice_' in source and 'LineItem_' in source\nassert invoice_lines_{suffix}([]) == 0"),
            ("validator_pipeline", "Pipeline содержит список validator-объектов", "class RequiredValidator_{suffix}:\n    def validate(self, value):\n        return bool(value)\n\n\nclass Pipeline_{suffix}:\n    def __init__(self, validators):\n        self.validators = validators\n    def validate(self, value):\n        return all(validator.validate(value) for validator in self.validators)\n\n\ndef validator_pipeline_{suffix}(value):\n    return Pipeline_{suffix}([RequiredValidator_{suffix}()]).validate(value)\n", "'ok'", "True", "source = inspect.getsource(solution_module)\nassert 'Pipeline_' in source and 'validators' in source\nassert validator_pipeline_{suffix}('') is False"),
            ("order_policy", "Order использует вложенную policy", "class DiscountPolicy_{suffix}:\n    def apply(self, amount):\n        return amount - 100 if amount >= 1000 else amount\n\n\nclass Order_{suffix}:\n    def __init__(self, amount, policy):\n        self.amount = amount\n        self.policy = policy\n    def payable(self):\n        return self.policy.apply(self.amount)\n\n\ndef order_policy_{suffix}(amount):\n    return Order_{suffix}(amount, DiscountPolicy_{suffix}()).payable()\n", "1200", "1100", "source = inspect.getsource(solution_module)\nassert 'DiscountPolicy' in source and 'Order_' in source\nassert order_policy_{suffix}(500) == 500"),
        ]
    elif any(x in low for x in ["ооп", "атрибут", "метод"]):
        category = "oop_core"
        cases = [
            ("task_object", "создай класс задачи с __init__, состоянием и методом", "class Task_{suffix}:\n    def __init__(self, title):\n        self.title = title\n        self.done = False\n\n    def close(self):\n        self.done = True\n        return self.done\n\n\ndef task_object_{suffix}(title):\n    task = Task_{suffix}(title)\n    task.close()\n    return {'title': task.title, 'done': task.done}\n", "'API'", "{'title': 'API', 'done': True}", "source = inspect.getsource(solution_module)\nassert 'class Task' in source and '__init__' in source and 'self.' in source\nassert task_object_{suffix}('') == {'title': '', 'done': True}"),
            ("class_attribute", "раздели class attribute и instance attribute", "class Build_{suffix}:\n    created = 0\n\n    def __init__(self, name):\n        type(self).created += 1\n        self.name = name\n\n\ndef class_attribute_{suffix}(left, right):\n    before = Build_{suffix}.created\n    a = Build_{suffix}(left)\n    b = Build_{suffix}(right)\n    return [a.name, b.name, Build_{suffix}.created - before]\n", "'api', 'sql'", "['api', 'sql', 2]", "source = inspect.getsource(solution_module)\nassert 'created =' in source and 'self.name' in source\nassert class_attribute_{suffix}('x', 'y')[-1] == 2"),
            ("factory_method", "используй classmethod как фабрику", "class User_{suffix}:\n    def __init__(self, name, active=True):\n        self.name = name\n        self.active = active\n\n    @classmethod\n    def blocked(cls, name):\n        return cls(name, active=False)\n\n\ndef factory_method_{suffix}(name):\n    user = User_{suffix}.blocked(name)\n    return {'name': user.name, 'active': user.active}\n", "'Oleg'", "{'name': 'Oleg', 'active': False}", "source = inspect.getsource(solution_module)\nassert '@classmethod' in source\nassert factory_method_{suffix}('x')['active'] is False"),
            ("static_slug", "используй staticmethod для независимой нормализации", "class Slugger_{suffix}:\n    @staticmethod\n    def normalize(text):\n        return text.strip().lower().replace(' ', '-')\n\n    def __init__(self, title):\n        self.slug = self.normalize(title)\n\n\ndef static_slug_{suffix}(title):\n    return Slugger_{suffix}(title).slug\n", "' API Route '", "'api-route'", "source = inspect.getsource(solution_module)\nassert '@staticmethod' in source\nassert static_slug_{suffix}('X Y') == 'x-y'"),
            ("state_method", "измени состояние объекта через instance method", "class Counter_{suffix}:\n    def __init__(self):\n        self.value = 0\n\n    def add(self, step=1):\n        self.value += step\n        return self.value\n\n\ndef state_method_{suffix}(steps):\n    counter = Counter_{suffix}()\n    for step in steps:\n        counter.add(step)\n    return counter.value\n", "[1, 2, 3]", "6", "source = inspect.getsource(solution_module)\nassert 'class Counter' in source and 'def add' in source\nassert state_method_{suffix}([]) == 0"),
        ]
    elif "typing" in low or "mypy" in low or "типизац" in low:
        category = "typing_contracts"
        cases = [
            ("optional_title", "обработай Optional[str] без неявного None", "from typing import Optional\n\n\ndef optional_title_{suffix}(value: Optional[str]) -> str:\n    if value is None:\n        return 'untitled'\n    return value.strip() or 'untitled'\n", "None", "'untitled'", "source = inspect.getsource(solution_module)\nassert 'Optional' in source or '| None' in source\nassert optional_title_{suffix}(' API ') == 'API'"),
            ("typed_payload", "опиши TypedDict для payload", "from typing import TypedDict\n\n\nclass Payload_{suffix}(TypedDict):\n    title: str\n    priority: int\n\n\ndef typed_payload_{suffix}(payload: Payload_{suffix}) -> str:\n    return f\"{{payload['title']}}:{{payload['priority']}}\"\n", "{'title':'api','priority':2}", "'api:2'", "source = inspect.getsource(solution_module)\nassert 'TypedDict' in source\nassert typed_payload_{suffix}({'title':'x','priority':0}) == 'x:0'"),
            ("generic_box", "создай Generic контейнер", "from typing import Generic, TypeVar\n\n\nT = TypeVar('T')\n\n\nclass Box_{suffix}(Generic[T]):\n    def __init__(self, value: T):\n        self.value = value\n\n    def unwrap(self) -> T:\n        return self.value\n\n\ndef generic_box_{suffix}(value: int) -> int:\n    return Box_{suffix}(value).unwrap()\n", "7", "7", "source = inspect.getsource(solution_module)\nassert 'Generic' in source and 'TypeVar' in source\nassert generic_box_{suffix}(0) == 0"),
            ("union_parse", "обработай int | str явно", "def union_parse_{suffix}(value: int | str) -> int:\n    if isinstance(value, int):\n        return value\n    return int(value)\n", "'42'", "42", "source = inspect.getsource(solution_module)\nassert 'int | str' in source or 'Union' in source\nassert union_parse_{suffix}(5) == 5"),
            ("callable_mapper", "типизируй Callable mapper", "from collections.abc import Callable\n\n\ndef callable_mapper_{suffix}(items: list[int], mapper: Callable[[int], int]) -> list[int]:\n    return [mapper(item) for item in items]\n", "[1, 2], lambda x: x + 1", "[2, 3]", "source = inspect.getsource(solution_module)\nassert 'Callable' in source\nassert callable_mapper_{suffix}([], lambda x: x) == []"),
        ]
    elif "pytest" in low:
        category = "pytest_student_code"
        cases = [
            ("raise_on_empty", "подготовь функцию, которую удобно проверять через pytest.raises", "def raise_on_empty_{suffix}(title):\n    if not title:\n        raise ValueError('title required')\n    return title.strip()\n", "' api '", "'api'", "with pytest.raises(ValueError):\n    raise_on_empty_{suffix}('')"),
            ("param_case", "верни результат для нескольких parametrized inputs", "def param_case_{suffix}(status):\n    return {'new': 201, 'done': 200}.get(status, 400)\n", "'new'", "201", "assert [param_case_{suffix}(x) for x in ['done','bad']] == [200, 400]"),
            ("fixture_ready_config", "верни config, который удобно создавать fixture", "def fixture_ready_config_{suffix}(env):\n    return {'env': env, 'debug': env == 'dev'}\n", "'dev'", "{'env': 'dev', 'debug': True}", "assert fixture_ready_config_{suffix}('prod')['debug'] is False"),
            ("mockable_client", "принимай client как зависимость для monkeypatch/mock", "def mockable_client_{suffix}(client, path):\n    response = client.get(path)\n    return response['status']\n", "type('C', (), {'get': lambda self, path: {'status': 200}})(), '/health'", "200", "class C:\n    def get(self, path): return {'status': 404}\nassert mockable_client_{suffix}(C(), '/x') == 404"),
            ("coverage_branch", "сделай явные ветки для coverage", "def coverage_branch_{suffix}(value):\n    if value > 0:\n        return 'positive'\n    if value == 0:\n        return 'zero'\n    return 'negative'\n", "1", "'positive'", "assert coverage_branch_{suffix}(0) == 'zero'\nassert coverage_branch_{suffix}(-1) == 'negative'"),
        ]
    elif "функц" in low:
        category = "functions"
        cases = [
            ("shipping_total", "посчитай стоимость доставки с default-порогом бесплатной доставки", "def shipping_total_{suffix}(amount, city, free_from=5000):\n    fee = 0 if amount >= free_from else (400 if city == 'Москва' else 700)\n    return amount + fee\n", "4500, 'Москва'", "4900", "assert shipping_total_{suffix}(6000, 'Казань') == 6000"),
            ("safe_divide", "верни частное или fallback, если делить нельзя", "def safe_divide_{suffix}(left, right, fallback=None):\n    if right == 0:\n        return fallback\n    return left / right\n", "10, 2", "5.0", "assert safe_divide_{suffix}(5, 0, fallback='bad') == 'bad'"),
            ("build_label", "собери подпись из обязательного id и необязательного префикса", "def build_label_{suffix}(item_id, prefix='task'):\n    return f'{{prefix}}-{{item_id}}'\n", "7", "'task-7'", "assert build_label_{suffix}(3, prefix='user') == 'user-3'"),
            ("pure_increment", "верни новый список чисел, не меняя исходный", "def pure_increment_{suffix}(numbers, step=1):\n    return [number + step for number in numbers]\n", "[1, 2, 3]", "[2, 3, 4]", "data=[1]; pure_increment_{suffix}(data); assert data == [1]"),
            ("keyword_summary", "прими keyword-only флаг и верни краткую сводку", "def keyword_summary_{suffix}(name, *, active=True):\n    return f'{{name}}:{{\"active\" if active else \"blocked\"}}'\n", "'Anna'", "'Anna:active'", "assert keyword_summary_{suffix}('Oleg', active=False) == 'Oleg:blocked'"),
        ]
    elif "кортеж" in low:
        category = "tuples"
        cases = [
            ("point_distance", "посчитай манхэттенское расстояние между двумя точками-кортежами", "def point_distance_{suffix}(left, right):\n    lx, ly = left\n    rx, ry = right\n    return abs(lx - rx) + abs(ly - ry)\n", "(1, 2), (4, 6)", "7", "assert point_distance_{suffix}((0,0),(0,0)) == 0"),
            ("swap_pair", "поменяй значения пары местами", "def swap_pair_{suffix}(pair):\n    left, right = pair\n    return (right, left)\n", "('api', 'sql')", "('sql', 'api')", "assert swap_pair_{suffix}((1, 2)) == (2, 1)"),
            ("normalize_rect", "верни прямоугольник как `(left, top, right, bottom)` независимо от порядка точек", "def normalize_rect_{suffix}(a, b):\n    ax, ay = a\n    bx, by = b\n    return (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))\n", "(5, 1), (2, 4)", "(2, 1, 5, 4)", "assert normalize_rect_{suffix}((1,1),(1,1)) == (1,1,1,1)"),
            ("unpack_status", "разбери кортеж ответа `(code, body)`", "def unpack_status_{suffix}(response):\n    code, body = response\n    return code == 200 and body != ''\n", "(200, 'ok')", "True", "assert unpack_status_{suffix}((404, 'missing')) is False"),
            ("tuple_key", "собери неизменяемый ключ координаты", "def tuple_key_{suffix}(row, col):\n    return (int(row), int(col))\n", "'2', '5'", "(2, 5)", "assert tuple_key_{suffix}(0, 0) == (0, 0)"),
        ]
    elif "множеств" in low:
        category = "sets"
        cases = [
            ("common_tags", "найди общие теги двух карточек", "def common_tags_{suffix}(left, right):\n    return sorted(set(left) & set(right))\n", "['api','sql'], ['git','api']", "['api']", "assert common_tags_{suffix}([], ['api']) == []"),
            ("missing_permissions", "верни права, которых не хватает пользователю", "def missing_permissions_{suffix}(required, actual):\n    return sorted(set(required) - set(actual))\n", "['read','write'], ['read']", "['write']", "assert missing_permissions_{suffix}(['read'], ['read','admin']) == []"),
            ("unique_count", "посчитай количество уникальных значений", "def unique_count_{suffix}(items):\n    return len(set(items))\n", "['a','b','a']", "2", "assert unique_count_{suffix}([]) == 0"),
            ("symmetric_changes", "найди элементы, которые есть только в одном наборе", "def symmetric_changes_{suffix}(before, after):\n    return sorted(set(before) ^ set(after))\n", "['a','b'], ['b','c']", "['a', 'c']", "assert symmetric_changes_{suffix}([], []) == []"),
            ("is_subset", "проверь, покрывает ли роль набор требуемых прав", "def is_subset_{suffix}(required, actual):\n    return set(required) <= set(actual)\n", "['read'], ['read','write']", "True", "assert is_subset_{suffix}(['admin'], ['read']) is False"),
        ]
    elif "словар" in low:
        category = "dicts"
        cases = [
            ("count_statuses", "посчитай статусы задач через словарь", "def count_statuses_{suffix}(tasks):\n    result = {{}}\n    for task in tasks:\n        status = task.get('status', 'unknown')\n        result[status] = result.get(status, 0) + 1\n    return result\n", "[{'status':'new'}, {'status':'done'}, {'status':'new'}]", "{'new': 2, 'done': 1}", "assert count_statuses_{suffix}([{}]) == {'unknown': 1}"),
            ("project_titles", "построй словарь id проекта -> название", "def project_titles_{suffix}(projects):\n    return {{project['id']: project['title'] for project in projects}}\n", "[{'id':1,'title':'API'}, {'id':2,'title':'Docs'}]", "{1: 'API', 2: 'Docs'}", "assert project_titles_{suffix}([]) == {}"),
            ("nested_email", "достань email из вложенного профиля безопасно", "def nested_email_{suffix}(user):\n    return user.get('profile', {{}}).get('email')\n", "{'profile': {'email': 'a@example.com'}}", "'a@example.com'", "assert nested_email_{suffix}({}) is None"),
            ("upsert_counter", "увеличь счётчик ключа и верни новый словарь", "def upsert_counter_{suffix}(counters, key):\n    result = counters.copy()\n    result[key] = result.get(key, 0) + 1\n    return result\n", "{'api': 2}, 'api'", "{'api': 3}", "data={}; upsert_counter_{suffix}(data, 'x'); assert data == {}"),
            ("group_by_owner", "сгруппируй id задач по владельцу", "def group_by_owner_{suffix}(tasks):\n    result = {{}}\n    for task in tasks:\n        result.setdefault(task['owner'], []).append(task['id'])\n    return result\n", "[{'id':1,'owner':'Ann'}, {'id':2,'owner':'Ann'}]", "{'Ann': [1, 2]}", "assert group_by_owner_{suffix}([]) == {}"),
        ]
    elif "map/filter" in low or "lambda" in low:
        category = "functional_tools"
        cases = [
            ("map_prices", "преобразуй цены из копеек в рубли через map", "def map_prices_{suffix}(kopecks):\n    return list(map(lambda value: value / 100, kopecks))\n", "[199, 250]", "[1.99, 2.5]", "assert map_prices_{suffix}([]) == []"),
            ("filter_active", "оставь активные записи через filter", "def filter_active_{suffix}(rows):\n    return list(filter(lambda row: row.get('active') is True, rows))\n", "[{'id':1,'active':True},{'id':2,'active':False}]", "[{'id': 1, 'active': True}]", "assert filter_active_{suffix}([]) == []"),
            ("sort_by_key", "отсортируй записи по score через key-функцию", "def sort_by_key_{suffix}(rows):\n    return sorted(rows, key=lambda row: (-row['score'], row['id']))\n", "[{'id':2,'score':9},{'id':1,'score':9}]", "[{'id': 1, 'score': 9}, {'id': 2, 'score': 9}]", "assert sort_by_key_{suffix}([]) == []"),
            ("compose_filter_map", "сначала отфильтруй, потом преобразуй имена", "def compose_filter_map_{suffix}(users):\n    active = filter(lambda user: user.get('active'), users)\n    return list(map(lambda user: user['name'].strip().title(), active))\n", "[{'name':' anna ','active':True},{'name':'oleg','active':False}]", "['Anna']", "assert compose_filter_map_{suffix}([]) == []"),
            ("lambda_default", "замени пустой title через lambda в sorted", "def lambda_default_{suffix}(items):\n    return sorted(items, key=lambda item: item.get('title') or 'zzz')\n", "[{'title':''},{'title':'api'}]", "[{'title': 'api'}, {'title': ''}]", "assert lambda_default_{suffix}([]) == []"),
        ]
    elif "datetime" in low:
        category = "datetime"
        cases = [
            ("parse_iso_date", "распарсь ISO-дату и верни день недели", "from datetime import date\n\ndef parse_iso_date_{suffix}(raw):\n    return date.fromisoformat(raw).weekday()\n", "'2026-05-02'", "5", "import pytest\nwith pytest.raises(ValueError): parse_iso_date_{suffix}('bad')"),
            ("deadline_days", "посчитай дни до дедлайна", "from datetime import date\n\ndef deadline_days_{suffix}(today, deadline):\n    return (date.fromisoformat(deadline) - date.fromisoformat(today)).days\n", "'2026-05-02', '2026-05-10'", "8", "assert deadline_days_{suffix}('2026-05-02','2026-05-02') == 0"),
            ("format_timestamp", "отформатируй datetime для логов", "from datetime import datetime\n\ndef format_timestamp_{suffix}(raw):\n    return datetime.fromisoformat(raw).strftime('%Y-%m-%d %H:%M')\n", "'2026-05-02T09:30:00'", "'2026-05-02 09:30'", "assert format_timestamp_{suffix}('2026-05-02T00:00:00') == '2026-05-02 00:00'"),
            ("add_minutes", "добавь минуты к времени старта", "from datetime import datetime, timedelta\n\ndef add_minutes_{suffix}(raw, minutes):\n    return (datetime.fromisoformat(raw) + timedelta(minutes=minutes)).isoformat(timespec='minutes')\n", "'2026-05-02T10:00:00', 45", "'2026-05-02T10:45'", "assert add_minutes_{suffix}('2026-05-02T23:50:00', 20).endswith('00:10')"),
            ("month_key", "получи ключ месяца для агрегации", "from datetime import date\n\ndef month_key_{suffix}(raw):\n    value = date.fromisoformat(raw)\n    return f'{{value.year}}-{{value.month:02d}}'\n", "'2026-05-02'", "'2026-05'", "assert month_key_{suffix}('2026-01-01') == '2026-01'"),
        ]
    elif "итератор" in low:
        category = "iterators"
        cases = [
            ("next_or_none", "безопасно возьми следующий элемент iterator", "def next_or_none_{suffix}(iterator):\n    return next(iterator, None)\n", "iter(['api'])", "'api'", "assert next_or_none_{suffix}(iter([])) is None"),
            ("take_until", "читай iterator до stop-значения", "def take_until_{suffix}(iterator, stop):\n    result = []\n    for item in iterator:\n        if item == stop:\n            break\n        result.append(item)\n    return result\n", "iter(['a','stop','b']), 'stop'", "['a']", "assert take_until_{suffix}(iter([]), 'stop') == []"),
            ("iter_pages", "пройди iterator страниц и собери id", "def iter_pages_{suffix}(pages):\n    result = []\n    for page in pages:\n        result.extend(item['id'] for item in page)\n    return result\n", "iter([[{'id':1}], [{'id':2}]])", "[1, 2]", "assert iter_pages_{suffix}(iter([])) == []"),
            ("manual_iterator", "создай iterator и прочитай два значения", "def manual_iterator_{suffix}(items):\n    iterator = iter(items)\n    first = next(iterator, None)\n    second = next(iterator, None)\n    return (first, second)\n", "['api','sql','git']", "('api', 'sql')", "assert manual_iterator_{suffix}([]) == (None, None)"),
            ("iterator_exhausted", "проверь, что iterator исчерпывается", "def iterator_exhausted_{suffix}(items):\n    iterator = iter(items)\n    list(iterator)\n    return list(iterator)\n", "[1,2]", "[]", "assert iterator_exhausted_{suffix}([]) == []"),
        ]
    elif "генератор" in low:
        category = "generators"
        cases = [
            ("yield_batches", "генерируй батчи фиксированного размера", "def yield_batches_{suffix}(items, size):\n    for index in range(0, len(items), size):\n        yield items[index:index + size]\n", "[1,2,3], 2", "[[1, 2], [3]]", "assert list(yield_batches_{suffix}([], 2)) == []"),
            ("yield_non_empty", "yield только непустые строки", "def yield_non_empty_{suffix}(rows):\n    for row in rows:\n        cleaned = row.strip()\n        if cleaned:\n            yield cleaned\n", "[' a ', '', 'b']", "['a', 'b']", "assert list(yield_non_empty_{suffix}([''])) == []"),
            ("running_numbers", "лениво выдавай числа до лимита", "def running_numbers_{suffix}(limit):\n    current = 0\n    while current < limit:\n        yield current\n        current += 1\n", "3", "[0, 1, 2]", "assert list(running_numbers_{suffix}(0)) == []"),
            ("yield_errors", "выдели ошибки из потока событий", "def yield_errors_{suffix}(events):\n    for event in events:\n        if event.get('level') == 'error':\n            yield event['message']\n", "[{'level':'info','message':'ok'}, {'level':'error','message':'db'}]", "['db']", "assert list(yield_errors_{suffix}([])) == []"),
            ("generator_expression", "верни generator expression для квадратов", "def generator_expression_{suffix}(numbers):\n    return (number * number for number in numbers)\n", "[2,3]", "[4, 9]", "assert list(generator_expression_{suffix}([])) == []"),
        ]
    elif "декорат" in low:
        category = "decorators"
        cases = [
            ("log_calls", "напиши decorator, который считает вызовы", "def log_calls_{suffix}(func):\n    state = {{'calls': 0}}\n    def wrapper(*args, **kwargs):\n        state['calls'] += 1\n        return func(*args, **kwargs)\n    wrapper.state = state\n    return wrapper\n", "lambda x: x + 1", "2", "wrapped = log_calls_{suffix}(lambda x: x); wrapped(1); assert wrapped.state['calls'] == 1"),
            ("require_positive", "decorator отклоняет отрицательный аргумент", "def require_positive_{suffix}(func):\n    def wrapper(value):\n        if value < 0:\n            raise ValueError('positive required')\n        return func(value)\n    return wrapper\n", "lambda x: x * 2", "6", "import pytest\nwrapped=require_positive_{suffix}(lambda x:x)\nwith pytest.raises(ValueError): wrapped(-1)"),
            ("preserve_result", "decorator не меняет результат функции", "def preserve_result_{suffix}(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n", "lambda a,b: a+b", "5", "assert preserve_result_{suffix}(lambda: 'ok')() == 'ok'"),
            ("retry_once_decorator", "decorator повторяет вызов один раз после RuntimeError", "def retry_once_decorator_{suffix}(func):\n    def wrapper(*args, **kwargs):\n        try:\n            return func(*args, **kwargs)\n        except RuntimeError:\n            return func(*args, **kwargs)\n    return wrapper\n", "None", "'ok'", "calls={'n':0}\ndef op():\n    calls['n'] += 1\n    if calls['n'] == 1: raise RuntimeError('bad')\n    return 'ok'\nassert retry_once_decorator_{suffix}(op)() == 'ok'"),
            ("with_prefix", "decorator добавляет префикс к строковому результату", "def with_prefix_{suffix}(prefix):\n    def decorate(func):\n        def wrapper(*args, **kwargs):\n            return prefix + func(*args, **kwargs)\n        return wrapper\n    return decorate\n", "'api:'", "'api:ok'", "decorator=with_prefix_{suffix}('x:'); assert decorator(lambda:'y')() == 'x:y'"),
        ]
    elif "контекст" in low:
        category = "context_managers"
        cases = [
            ("read_first_line", "прочитай первую строку через with", "def read_first_line_{suffix}(path):\n    with open(path, encoding='utf-8') as file:\n        return file.readline().rstrip('\\n')\n", "path", "'hello'", "p=tmp_path/'a.txt'; p.write_text('x\\n', encoding='utf-8'); assert read_first_line_{suffix}(p) == 'x'"),
            ("write_report", "запиши отчёт через context manager файла", "def write_report_{suffix}(path, lines):\n    with open(path, 'w', encoding='utf-8') as file:\n        for line in lines:\n            file.write(line + '\\n')\n    return path.read_text(encoding='utf-8')\n", "path, ['a','b']", "'a\\nb\\n'", "p=tmp_path/'r.txt'; assert write_report_{suffix}(p, []) == ''"),
            ("managed_flag", "реализуй простой context manager класса", "class managed_flag_{suffix}:\n    def __init__(self, state):\n        self.state = state\n    def __enter__(self):\n        self.state['open'] = True\n        return self.state\n    def __exit__(self, exc_type, exc, tb):\n        self.state['open'] = False\n        return False\n", "{'open': False}", "False", "state={'open':False}\nwith managed_flag_{suffix}(state): assert state['open'] is True\nassert state['open'] is False"),
            ("suppress_key_error", "подави только KeyError в context manager", "class suppress_key_error_{suffix}:\n    def __enter__(self):\n        return self\n    def __exit__(self, exc_type, exc, tb):\n        return exc_type is KeyError\n", "None", "None", "with suppress_key_error_{suffix}(): raise KeyError('x')"),
            ("transaction_log", "добавь commit/rollback запись в контекстной транзакции", "class transaction_log_{suffix}:\n    def __init__(self, log):\n        self.log = log\n    def __enter__(self):\n        self.log.append('begin')\n        return self.log\n    def __exit__(self, exc_type, exc, tb):\n        self.log.append('rollback' if exc_type else 'commit')\n        return False\n", "[]", "['begin', 'commit']", "log=[]\ntry:\n    with transaction_log_{suffix}(log): raise RuntimeError('bad')\nexcept RuntimeError: pass\nassert log == ['begin','rollback']"),
        ]
    elif "исключ" in low:
        category = "exceptions"
        cases = [
            ("parse_positive_int", "преобразуй строку или подними ValueError", "def parse_positive_int_{suffix}(raw):\n    value = int(raw)\n    if value <= 0:\n        raise ValueError('positive required')\n    return value\n", "'5'", "5", "import pytest\nwith pytest.raises(ValueError): parse_positive_int_{suffix}('0')"),
            ("domain_error", "замени KeyError на понятный ValueError", "def domain_error_{suffix}(data):\n    try:\n        return data['id']\n    except KeyError as exc:\n        raise ValueError('id required') from exc\n", "{'id': 7}", "7", "import pytest\nwith pytest.raises(ValueError): domain_error_{suffix}({})"),
            ("finally_flag", "выполни cleanup в finally", "def finally_flag_{suffix}(state, fail=False):\n    try:\n        if fail:\n            raise RuntimeError('bad')\n        return 'ok'\n    finally:\n        state['closed'] = True\n", "{}, False", "'ok'", "state={}\ntry: finally_flag_{suffix}(state, True)\nexcept RuntimeError: pass\nassert state['closed'] is True"),
            ("safe_index", "верни fallback при IndexError", "def safe_index_{suffix}(items, index, fallback=None):\n    try:\n        return items[index]\n    except IndexError:\n        return fallback\n", "['a'], 0", "'a'", "assert safe_index_{suffix}([], 0, 'x') == 'x'"),
            ("validate_payload_error", "собери список ошибок валидации", "def validate_payload_error_{suffix}(payload):\n    errors = []\n    if not payload.get('title'):\n        errors.append('title required')\n    if payload.get('priority', 1) < 1:\n        errors.append('priority invalid')\n    if errors:\n        raise ValueError(', '.join(errors))\n    return payload\n", "{'title':'x','priority':1}", "{'title': 'x', 'priority': 1}", "import pytest\nwith pytest.raises(ValueError): validate_payload_error_{suffix}({'title':'','priority':0})"),
        ]
    elif "asyncio" in low:
        category = "asyncio"
        cases = [
            ("async_gather", "собери результаты async-функций через gather", "import asyncio\n\nasync def async_gather_{suffix}(workers):\n    return await asyncio.gather(*(worker() for worker in workers))\n", "[lambda: None]", "['ok']", "async def w(): return 'x'; assert asyncio.run(async_gather_{suffix}([w])) == ['x']"),
            ("async_timeout", "верни fallback при timeout", "import asyncio\n\nasync def async_timeout_{suffix}(coro, timeout, fallback):\n    try:\n        return await asyncio.wait_for(coro, timeout=timeout)\n    except TimeoutError:\n        return fallback\n", "None, 1, 'late'", "'late'", "async def fast(): return 'ok'; assert asyncio.run(async_timeout_{suffix}(fast(), 1, 'late')) == 'ok'"),
            ("async_limit", "ограничи параллельность через semaphore", "import asyncio\n\nasync def async_limit_{suffix}(items, handler, limit):\n    sem = asyncio.Semaphore(limit)\n    async def run(item):\n        async with sem:\n            return await handler(item)\n    return await asyncio.gather(*(run(item) for item in items))\n", "[1,2], None, 1", "[2, 4]", "async def h(x): return x+1; assert asyncio.run(async_limit_{suffix}([1], h, 1)) == [2]"),
            ("async_queue", "обработай очередь сообщений до sentinel", "import asyncio\n\nasync def async_queue_{suffix}(queue):\n    result = []\n    while True:\n        item = await queue.get()\n        if item is None:\n            break\n        result.append(item.upper())\n    return result\n", "None", "['A']", "q=asyncio.Queue(); q.put_nowait(None); assert asyncio.run(async_queue_{suffix}(q)) == []"),
            ("async_retry", "повтори async-вызов после временной ошибки", "async def async_retry_{suffix}(operation, attempts):\n    last = None\n    for _ in range(attempts):\n        try:\n            return await operation()\n        except RuntimeError as exc:\n            last = exc\n    raise last\n", "None, 2", "'ok'", "calls={'n':0}\nasync def op(): calls['n']+=1; return 'ok'\nassert asyncio.run(async_retry_{suffix}(op, 1)) == 'ok'"),
        ]
    elif "thread" in low or "multiprocessing" in low:
        category = "concurrency"
        cases = [
            ("locked_counter", "увеличь счётчик под lock", "def locked_counter_{suffix}(counter, lock, times):\n    for _ in range(times):\n        with lock:\n            counter['value'] += 1\n    return counter['value']\n", "{'value':0}, Lock(), 3", "3", "c={'value':1}; assert locked_counter_{suffix}(c, Lock(), 1) == 2"),
            ("chunk_jobs", "разбей задачи на чанки для процессов", "def chunk_jobs_{suffix}(items, size):\n    return [items[index:index + size] for index in range(0, len(items), size)]\n", "[1,2,3,4,5], 2", "[[1, 2], [3, 4], [5]]", "assert chunk_jobs_{suffix}([], 3) == []"),
            ("worker_result", "собери результат worker без общего mutable state", "def worker_result_{suffix}(items):\n    return [item * item for item in items]\n", "[2,3]", "[4, 9]", "assert worker_result_{suffix}([0]) == [0]"),
            ("queue_drain", "вычитай очередь до пустого состояния", "def queue_drain_{suffix}(queue):\n    result = []\n    while not queue.empty():\n        result.append(queue.get())\n    return result\n", "Queue()", "['a']", "q=Queue(); assert queue_drain_{suffix}(q) == []"),
            ("cpu_partition", "распредели диапазон по worker_count", "def cpu_partition_{suffix}(total, workers):\n    base = total // workers\n    rest = total % workers\n    return [base + (1 if index < rest else 0) for index in range(workers)]\n", "10, 3", "[4, 3, 3]", "assert cpu_partition_{suffix}(2, 4) == [1,1,0,0]"),
        ]
    elif "алгоритм" in low or "структур" in low:
        category = "algorithms"
        cases = [
            ("binary_search", "найди индекс числа бинарным поиском", "def binary_search_{suffix}(items, target):\n    left, right = 0, len(items) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if items[mid] == target:\n            return mid\n        if items[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1\n", "[1,3,5], 3", "1", "assert binary_search_{suffix}([1,2], 9) == -1"),
            ("valid_brackets", "проверь стеком скобочную последовательность", "def valid_brackets_{suffix}(text):\n    stack = []\n    pairs = {{')': '(', ']': '['}}\n    for char in text:\n        if char in '([':\n            stack.append(char)\n        elif char in pairs:\n            if not stack or stack.pop() != pairs[char]:\n                return False\n    return not stack\n", "'([])'", "True", "assert valid_brackets_{suffix}('([)]') is False"),
            ("bfs_distance", "найди расстояние в невзвешенном графе", "from collections import deque\n\ndef bfs_distance_{suffix}(graph, start, target):\n    queue = deque([(start, 0)])\n    seen = {{start}}\n    while queue:\n        node, dist = queue.popleft()\n        if node == target:\n            return dist\n        for nxt in graph.get(node, []):\n            if nxt not in seen:\n                seen.add(nxt)\n                queue.append((nxt, dist + 1))\n    return None\n", "{'a':['b'], 'b':['c']}, 'a', 'c'", "2", "assert bfs_distance_{suffix}({}, 'a', 'b') is None"),
            ("top_k", "верни top-k элементов по score", "def top_k_{suffix}(items, k):\n    return sorted(items, key=lambda item: (-item['score'], item['id']))[:k]\n", "[{'id':2,'score':9},{'id':1,'score':9}], 1", "[{'id': 1, 'score': 9}]", "assert top_k_{suffix}([], 3) == []"),
            ("prefix_sums", "построй массив префиксных сумм", "def prefix_sums_{suffix}(numbers):\n    result = []\n    total = 0\n    for number in numbers:\n        total += number\n        result.append(total)\n    return result\n", "[2, -1, 3]", "[2, 1, 4]", "assert prefix_sums_{suffix}([]) == []"),
        ]
    else:
        category = f"topic_{slug(title)[:24]}"
        cases = [
            ("cli_config_parser", "разбери CLI-конфиг `key=value` с обязательным `env`", "def cli_config_parser_{suffix}(pairs):\n    config = {{}}\n    for pair in pairs:\n        if '=' not in pair:\n            raise ValueError('key=value required')\n        key, value = pair.split('=', 1)\n        config[key.strip()] = value.strip()\n    if 'env' not in config:\n        raise ValueError('env required')\n    return config\n", "['env=dev', 'debug=true']", "{'env': 'dev', 'debug': 'true'}", "with pytest.raises(ValueError):\n    cli_config_parser_{suffix}(['debug=true'])"),
            ("rate_limit_bucket", "посчитай доступные запросы в rate-limit bucket", "def rate_limit_bucket_{suffix}(capacity, used, requested):\n    available = max(0, capacity - used)\n    allowed = min(available, requested)\n    return {'allowed': allowed, 'remaining': available - allowed}\n", "10, 7, 5", "{'allowed': 3, 'remaining': 0}", "assert rate_limit_bucket_{suffix}(5, 0, 2) == {'allowed': 2, 'remaining': 3}"),
            ("task_state_transition", "примени разрешённый переход состояния задачи", "def task_state_transition_{suffix}(state, event):\n    transitions = {('new', 'start'): 'in_progress', ('in_progress', 'finish'): 'done', ('done', 'archive'): 'archived'}\n    if (state, event) not in transitions:\n        raise ValueError('bad transition')\n    return transitions[(state, event)]\n", "'new', 'start'", "'in_progress'", "with pytest.raises(ValueError):\n    task_state_transition_{suffix}('new', 'archive')"),
            ("permissions_policy", "реши доступ по роли и действию", "def permissions_policy_{suffix}(role, action):\n    matrix = {'student': {'read'}, 'mentor': {'read', 'comment'}, 'owner': {'read', 'comment', 'delete'}}\n    return action in matrix.get(role, set())\n", "'mentor', 'comment'", "True", "assert permissions_policy_{suffix}('student', 'delete') is False"),
            ("invoice_calculator", "посчитай счёт с налогом и скидкой", "def invoice_calculator_{suffix}(lines, tax_percent=20, discount=0):\n    subtotal = sum(price * qty for price, qty in lines)\n    taxed = subtotal + subtotal * tax_percent // 100\n    return max(0, taxed - discount)\n", "[(100, 2), (50, 1)], 20, 30", "270", "assert invoice_calculator_{suffix}([], 20, 100) == 0"),
            ("delivery_window_planner", "выбери первое окно доставки, которое помещается в слот", "def delivery_window_planner_{suffix}(slots, duration):\n    for start, end in slots:\n        if end - start >= duration:\n            return {'start': start, 'end': start + duration}\n    return None\n", "[(9, 10), (11, 14)], 2", "{'start': 11, 'end': 13}", "assert delivery_window_planner_{suffix}([], 1) is None"),
            ("repository_method_filter", "отфильтруй repository-строки по владельцу и статусу", "def repository_method_filter_{suffix}(rows, owner, status):\n    return [row['id'] for row in rows if row.get('owner') == owner and row.get('status') == status]\n", "[{'id':1,'owner':'Ann','status':'new'}, {'id':2,'owner':'Ann','status':'done'}], 'Ann', 'new'", "[1]", "assert repository_method_filter_{suffix}([], 'Ann', 'new') == []"),
            ("sql_query_builder", "собери SQL-фрагмент WHERE и параметры без склейки значений", "def sql_query_builder_{suffix}(filters):\n    clauses = []\n    params = []\n    for key in sorted(filters):\n        clauses.append(f'{key} = ?')\n        params.append(filters[key])\n    return {'where': ' AND '.join(clauses) or '1=1', 'params': params}\n", "{'status':'new','owner':'Ann'}", "{'where': 'owner = ? AND status = ?', 'params': ['Ann', 'new']}", "assert sql_query_builder_{suffix}({}) == {'where': '1=1', 'params': []}"),
            ("http_response_mapper", "преобразуй доменный результат в HTTP-like ответ", "def http_response_mapper_{suffix}(result):\n    if result is None:\n        return {'status': 404, 'body': {'detail': 'not found'}}\n    return {'status': 200, 'body': result}\n", "{'id': 1}", "{'status': 200, 'body': {'id': 1}}", "assert http_response_mapper_{suffix}(None)['status'] == 404"),
            ("token_scope_validator", "проверь, что token содержит нужный scope", "def token_scope_validator_{suffix}(token, required_scope):\n    scopes = set(token.get('scopes', []))\n    if required_scope not in scopes:\n        raise PermissionError('scope denied')\n    return True\n", "{'scopes':['tasks:read']}, 'tasks:read'", "True", "with pytest.raises(PermissionError):\n    token_scope_validator_{suffix}({'scopes': []}, 'tasks:write')"),
            ("retry_budget_allocator", "распредели retry-budget по сервисам с ошибками", "def retry_budget_allocator_{suffix}(errors, budget):\n    result = {}\n    remaining = budget\n    for service, count in sorted(errors.items(), key=lambda item: -item[1]):\n        take = min(remaining, count)\n        result[service] = take\n        remaining -= take\n    return result\n", "{'api': 3, 'db': 1}, 2", "{'api': 2, 'db': 0}", "assert retry_budget_allocator_{suffix}({}, 3) == {}"),
            ("cache_invalidation_keys", "вычисли ключи cache для сброса", "def cache_invalidation_keys_{suffix}(entity, entity_id, related):\n    keys = {f'{entity}:{entity_id}'}\n    keys.update(f'{name}:{value}' for name, value in related)\n    return sorted(keys)\n", "'task', 7, [('project', 2)]", "['project:2', 'task:7']", "assert cache_invalidation_keys_{suffix}('x', 1, []) == ['x:1']"),
            ("pagination_cursor_page", "верни страницу и следующий cursor", "def pagination_cursor_page_{suffix}(items, cursor, limit):\n    page = items[cursor:cursor + limit]\n    next_cursor = cursor + len(page) if cursor + len(page) < len(items) else None\n    return {'items': page, 'next_cursor': next_cursor}\n", "['a','b','c'], 0, 2", "{'items': ['a', 'b'], 'next_cursor': 2}", "assert pagination_cursor_page_{suffix}(['a'], 0, 5)['next_cursor'] is None"),
            ("dto_mapper_public", "преобразуй entity в DTO без лишних полей", "def dto_mapper_public_{suffix}(entity):\n    return {'id': entity['id'], 'title': entity['title'], 'done': bool(entity.get('done'))}\n", "{'id':1,'title':'A','done':0,'secret':'x'}", "{'id': 1, 'title': 'A', 'done': False}", "assert 'secret' not in dto_mapper_public_{suffix}({'id':1,'title':'A'})"),
            ("unit_of_work_summary", "собери summary операций unit of work", "def unit_of_work_summary_{suffix}(operations):\n    return {'creates': operations.count('create'), 'updates': operations.count('update'), 'deletes': operations.count('delete')}\n", "['create', 'update', 'create']", "{'creates': 2, 'updates': 1, 'deletes': 0}", "assert unit_of_work_summary_{suffix}([]) == {'creates': 0, 'updates': 0, 'deletes': 0}"),
        ]
    name, brief, solution, args, expected, hidden_assert = cases[variant % len(cases)]
    fn = f"{name}_{suffix}"
    solution = solution.replace("{{", "{").replace("}}", "}")
    solution = solution.replace(f"{name}_{suffix}", fn).replace("{suffix}", suffix)
    hidden_assert = hidden_assert.replace("{suffix}", suffix).replace(name + "_" + suffix, fn)
    skill_terms = ", ".join(python_skill_terms(title, lesson.get("roadmap_topics", []))[:4])
    debug_note = ""
    if stage == "debug":
        debug_note = "\n\n### Что исправить\nDebug-сценарий: в стартовом коде может быть намеренная ошибка. Сначала найди её по падению проверки, затем исправь минимальным изменением."
    body = (
        f"**Коротко:** {brief}.\n\n"
        f"### Условие\nРеализуй функцию `{fn}` для темы `{title}`. Функция должна вернуть значение, а не печатать его.\n\n"
        f"Сценарий практики: {step_slug.replace('_', ' ')} / {order_word}.\n\n"
        f"### Вход\nАргументы функции: `{args}`.\n\n"
        f"### Выход\nОжидаемый результат: `{expected}`.\n\n"
        f"### Ограничения\nИспользуй ключевые инструменты урока: {skill_terms}.\n\n"
        f"### Что проверить\nПроверь основной пример и отдельный граничный случай из условия."
        f"{debug_note}"
    )
    editor = f"def {fn}(*args, **kwargs):\n    pass\n"
    test_imports = "import pytest\n"
    if category == "asyncio":
        test_imports += "import asyncio\n"
    if "solution_module" in hidden_assert or "inspect." in hidden_assert:
        test_imports += "import inspect\nimport solution as solution_module\n"
    if "Lock()" in args:
        test_imports += "from threading import Lock\n"
    if "Queue()" in args:
        test_imports += "from queue import Queue\n"
    test_code = (
        f"{test_imports}from solution import {fn}\n\n\n"
        f"def test_public_contract():\n"
    )
    if category == "asyncio" and name != "async_gather":
        test_code += f"    async def quick():\n        return 'ok'\n"
    if name == "async_gather":
        test_code += f"    async def worker():\n        return 'ok'\n    assert asyncio.run({fn}([worker])) == ['ok']\n\n\n"
    elif name == "async_timeout":
        test_code += f"    assert asyncio.run({fn}(quick(), 1, 'late')) == 'ok'\n\n\n"
    elif name == "async_limit":
        test_code += f"    async def handler(item):\n        return item * 2\n    assert asyncio.run({fn}([1, 2], handler, 1)) == [2, 4]\n\n\n"
    elif name == "async_queue":
        test_code += f"    q = asyncio.Queue()\n    q.put_nowait('a')\n    q.put_nowait(None)\n    assert asyncio.run({fn}(q)) == ['A']\n\n\n"
    elif name == "async_retry":
        test_code += f"    assert asyncio.run({fn}(quick, 1)) == 'ok'\n\n\n"
    elif name == "locked_counter":
        test_code += f"    assert {fn}({args}) == {expected}\n\n\n"
    elif name == "queue_drain":
        test_code += f"    q = Queue()\n    q.put('a')\n    assert {fn}(q) == ['a']\n\n\n"
    else:
        test_code += f"    assert {fn}({args}) == {expected}\n\n\n"
    hidden_assert_indented = "\n".join(("    " + line) if line else "" for line in hidden_assert.splitlines())
    test_code += f"def test_edge_contract():\n{hidden_assert_indented}\n"
    return name, body, editor, solution, test_code, category, args, expected


PY_DOMAIN_TASKS: list[tuple[str, str, str, str, str]] = []


def polish_python_step(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] != "practice" or st.get("checker", {}).get("type") != "python_pytest":
        return
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    if mode not in {"python", "complex_python"}:
        return
    early = early_progression_payload(st, lesson)
    if early:
        title, body, editor, solution, checker, focus = early
        stage = st.get("lesson_stage", stage_for_step(st))
        if stage == "debug":
            body += "\n\n### Что исправить\nDebug-сценарий: если пример не совпал, исправь ошибку в преобразовании, условии или формате вывода. Не добавляй лишний текст."
        st["title"] = title
        st["body_markdown"] = body
        st["editor_initial_code"] = editor
        st["solution_code"] = solution
        st["checker"] = checker
        st["skill_focus"] = f"Python early: {lesson['title']} / {focus}"
        st["new_constraint"] = f"{lesson['title']}: uses only concepts introduced up to lesson {lesson['order']}"
        st["edge_case"] = "hidden stdout case covers boundary input without future syntax"
        st["input_shape"] = "stdin text for a small script"
        st["output_contract"] = "exact stdout without extra text"
        st["algorithm_family"] = f"early:{lesson['order']}:{focus}"
        return
    name, body, editor, solution, test_code, category, args, expected = pytest_payload(lesson["title"], st, lesson)
    st["title"] = name.replace("_", " ").title()
    st["body_markdown"] = body
    st["editor_initial_code"] = editor
    st["solution_code"] = solution
    st["checker"] = {"type": "python_pytest", "timeout_sec": 8, "test_code": test_code, "hidden_tests": [{"name": f"{category}_{name}_edge", "assertion": "edge contract from the lesson-specific task is checked"}]}
    st["skill_focus"] = f"Python: {lesson['title']} / {category} / {name}"
    st["new_constraint"] = f"{lesson['title']}: task uses {category} mechanics, not a generic clamp/group/filter pattern"
    st["edge_case"] = f"edge case encoded in pytest for {name}"
    st["input_shape"] = f"function arguments for {category}:{name}"
    st["output_contract"] = f"returned Python value for {lesson['title']} without extra stdout"
    st["algorithm_family"] = f"python:{category}:{name}"


def polish_ai_python_step(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] != "practice" or st.get("checker", {}).get("type") != "python_pytest":
        return
    if lesson_mode(lesson["title"], lesson.get("roadmap_topics", [])) != "ai":
        return
    idx = stable_index(lesson["id"], st["id"]) % 100000
    lesson_low = lesson["title"].lower()
    step_low = st["title"].lower()
    stage = st.get("lesson_stage", stage_for_step(st))
    lesson_slug = slug(lesson["title"]).replace("-", "_")

    if "для учёбы" in lesson_low or "для учебы" in lesson_low:
        family = "study"
    elif "structured" in lesson_low or "json" in lesson_low or "schema" in lesson_low:
        family = "structured"
    elif "rag" in lesson_low:
        family = "rag"
    elif "vector" in lesson_low or "вектор" in lesson_low:
        family = "vector"
    elif "langchain" in lesson_low or "langgraph" in lesson_low:
        family = "graph"
    elif "вайб" in lesson_low or "безопас" in lesson_low:
        family = "vibecoding"
    elif "api" in lesson_low:
        family = "api"
    else:
        family = "api"

    cases_by_family: dict[str, list[tuple[str, str, str, str, str, str]]] = {
        "study": [
            ("study_question_prompt", "собери учебный вопрос с контекстом и запретом на готовый код", "def {fn}(topic, attempt):\n    return {'role': 'user', 'content': f'Объясни тему {topic}. Моя попытка: {attempt}. Не давай полный код.'}\n", "'циклы', 'for пропускает последний элемент'", "{'role': 'user', 'content': 'Объясни тему циклы. Моя попытка: for пропускает последний элемент. Не давай полный код.'}", "assert 'полный код' in {fn}('x', 'y')['content']"),
            ("explain_error_request", "попроси объяснить traceback без раскрытия решения", "def {fn}(error_text, code_excerpt):\n    if 'SECRET' in code_excerpt or 'api_key' in code_excerpt.lower():\n        raise ValueError('secret-like text')\n    return {'question': 'объясни причину ошибки', 'error': error_text.splitlines()[-1], 'code': code_excerpt}\n", "'ValueError: bad input', 'int(raw)'", "{'question': 'объясни причину ошибки', 'error': 'ValueError: bad input', 'code': 'int(raw)'}", "with pytest.raises(ValueError):\n    {fn}('err', 'api_key=123')"),
            ("socratic_hint_request", "запроси подсказку в сократическом стиле", "def {fn}(task, last_stdout):\n    return {'mode': 'hint', 'task': task, 'stdout': last_stdout, 'rules': ['question-first', 'no-full-answer']}\n", "'сумма двух чисел', '3'", "{'mode': 'hint', 'task': 'сумма двух чисел', 'stdout': '3', 'rules': ['question-first', 'no-full-answer']}", "assert 'no-full-answer' in {fn}('x', '')['rules']"),
            ("answer_checklist", "проверь ответ модели по чеклисту фактов", "def {fn}(answer, required_terms):\n    text = answer.lower()\n    missing = [term for term in required_terms if term.lower() not in text]\n    return {'ok': not missing, 'missing': missing}\n", "'Нужен int(input()) перед сложением', ['int', 'input']", "{'ok': True, 'missing': []}", "assert {fn}('только input', ['int']) == {'ok': False, 'missing': ['int']}"),
            ("secret_redaction", "убери секреты из текста перед отправкой AI", "def {fn}(text):\n    blocked = ['api_key', 'password=', 'secret=']\n    lowered = text.lower()\n    if any(token in lowered for token in blocked):\n        return {'allowed': False, 'text': '[redacted]'}\n    return {'allowed': True, 'text': text}\n", "'покажи ошибку ValueError'", "{'allowed': True, 'text': 'покажи ошибку ValueError'}", "assert {fn}('password=123')['allowed'] is False"),
            ("verify_model_claim", "отдели проверяемое утверждение модели от совета", "def {fn}(claim, sources):\n    matched = [source for source in sources if claim.lower() in source.lower()]\n    return {'verified': bool(matched), 'sources': matched}\n", "'input возвращает строку', ['input возвращает строку в Python']", "{'verified': True, 'sources': ['input возвращает строку в Python']}", "assert {fn}('x', []) == {'verified': False, 'sources': []}"),
            ("no_full_answer_boundary", "проверь, что prompt просит не выдавать полный ответ", "def {fn}(prompt):\n    banned = ['напиши весь код', 'дай решение целиком']\n    return {'safe': not any(item in prompt.lower() for item in banned), 'prompt': prompt}\n", "'дай направление, где искать ошибку'", "{'safe': True, 'prompt': 'дай направление, где искать ошибку'}", "assert {fn}('напиши весь код')['safe'] is False"),
        ],
        "api": [
            ("ai_messages_payload", "собери system/user messages для mock provider", "def {fn}(system_prompt, user_text):\n    if not system_prompt or not user_text:\n        raise ValueError('message text required')\n    return [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_text}]\n", "'answer in JSON', 'classify ticket'", "[{'role': 'system', 'content': 'answer in JSON'}, {'role': 'user', 'content': 'classify ticket'}]", "with pytest.raises(ValueError):\n    {fn}('', 'x')"),
            ("mock_provider_call", "вызови mock provider без внешнего API", "def {fn}(provider, messages):\n    response = provider.complete(messages)\n    return {'text': response, 'provider': 'mock'}\n", "Provider(), [{'role':'user','content':'ping'}]", "{'text': 'pong', 'provider': 'mock'}", "assert {fn}(Provider(), [])['text'] == 'pong'"),
            ("timeout_budget", "передай timeout и верни fallback при TimeoutError", "def {fn}(provider, messages, timeout):\n    try:\n        return provider.complete(messages, timeout=timeout)\n    except TimeoutError:\n        return 'timeout-fallback'\n", "TimeoutProvider(), [{'role':'user','content':'ping'}], 1", "'timeout-fallback'", "assert {fn}(Provider(), [], 3) == 'pong'"),
            ("retry_limited_provider", "повтори временно падающий provider ограниченное число раз", "def {fn}(provider, messages, attempts=3):\n    last = None\n    for _ in range(attempts):\n        try:\n            return provider.complete(messages)\n        except RuntimeError as exc:\n            last = exc\n    raise last\n", "FlakyProvider(), [{'role':'user','content':'ping'}]", "'pong'", "with pytest.raises(RuntimeError):\n    {fn}(BrokenProvider(), [], attempts=2)"),
            ("rate_limit_guard", "останови запрос, если исчерпан rate limit", "def {fn}(remaining, payload):\n    if remaining <= 0:\n        raise RuntimeError('rate limit exceeded')\n    return {'allowed': True, 'payload_size': len(str(payload))}\n", "2, {'messages': []}", "{'allowed': True, 'payload_size': 16}", "with pytest.raises(RuntimeError):\n    {fn}(0, {})"),
            ("request_cost_log", "посчитай приблизительную стоимость запроса", "def {fn}(messages, price_per_1k=0.01):\n    chars = sum(len(message.get('content', '')) for message in messages)\n    tokens = max(1, chars // 4)\n    return {'tokens': tokens, 'cost': round(tokens / 1000 * price_per_1k, 6)}\n", "[{'role':'user','content':'ping'}]", "{'tokens': 1, 'cost': 1e-05}", "assert {fn}([{'content':''}])['tokens'] == 1"),
        ],
        "structured": [
            ("parse_json_output", "распарси JSON-строку от provider", "import json\n\n\ndef {fn}(raw):\n    try:\n        return {'ok': True, 'data': json.loads(raw)}\n    except json.JSONDecodeError:\n        return {'ok': False, 'error': 'invalid json'}\n", "'{\"label\": \"ok\"}'", "{'ok': True, 'data': {'label': 'ok'}}", "assert {fn}('not json')['ok'] is False"),
            ("required_fields_schema", "проверь required fields structured output", "def {fn}(payload):\n    required = {'label', 'confidence'}\n    missing = sorted(required - set(payload))\n    if missing:\n        raise ValueError('missing: ' + ','.join(missing))\n    return payload\n", "{'label':'bug','confidence':0.8}", "{'label': 'bug', 'confidence': 0.8}", "with pytest.raises(ValueError):\n    {fn}({'label':'x'})"),
            ("type_mismatch_schema", "поймай неверный тип поля confidence", "def {fn}(payload):\n    value = payload.get('confidence')\n    if not isinstance(value, (int, float)):\n        raise TypeError('confidence must be number')\n    return round(value, 2)\n", "{'confidence':0.912}", "0.91", "with pytest.raises(TypeError):\n    {fn}({'confidence':'high'})"),
            ("enum_label_schema", "ограничь label допустимыми значениями", "def {fn}(payload):\n    allowed = {'bug', 'feature', 'question'}\n    label = payload.get('label')\n    if label not in allowed:\n        raise ValueError('unknown label')\n    return label\n", "{'label':'bug'}", "'bug'", "with pytest.raises(ValueError):\n    {fn}({'label':'other'})"),
            ("fallback_on_validation", "верни fallback при ошибке structured output", "def {fn}(payload):\n    if not isinstance(payload, dict) or 'answer' not in payload:\n        return {'answer': None, 'valid': False}\n    return {'answer': payload['answer'], 'valid': True}\n", "{'answer':'ok'}", "{'answer': 'ok', 'valid': True}", "assert {fn}('bad')['valid'] is False"),
        ],
        "rag": [
            ("chunk_text_sentences", "разбей документ на chunks по предложениям", "def {fn}(text):\n    return [{'id': index + 1, 'text': part.strip()} for index, part in enumerate(text.split('.')) if part.strip()]\n", "'Python uses FastAPI. SQL stores data.'", "[{'id': 1, 'text': 'Python uses FastAPI'}, {'id': 2, 'text': 'SQL stores data'}]", "assert {fn}('') == []"),
            ("keyword_retrieval", "найди chunks по ключевому слову", "def {fn}(question, chunks):\n    terms = set(question.lower().split())\n    return [chunk['id'] for chunk in chunks if terms & set(chunk['text'].lower().split())]\n", "'python api', [{'id':'d1','text':'python fastapi'}, {'id':'d2','text':'sql'}]", "['d1']", "assert {fn}('missing', []) == []"),
            ("score_retrieved_chunks", "отсортируй найденные chunks по score", "def {fn}(question_terms, chunks):\n    scored = []\n    for chunk in chunks:\n        score = sum(1 for term in question_terms if term in chunk['text'].lower())\n        if score:\n            scored.append((score, chunk['id']))\n    return [chunk_id for score, chunk_id in sorted(scored, key=lambda item: (-item[0], item[1]))]\n", "['api','python'], [{'id':'b','text':'python'}, {'id':'a','text':'python api'}]", "['a', 'b']", "assert {fn}(['x'], [{'id':'a','text':'y'}]) == []"),
            ("answer_with_citations", "ответь только с source citations", "def {fn}(question, chunks):\n    matched = [chunk for chunk in chunks if question.lower() in chunk['text'].lower()]\n    if not matched:\n        return {'answer': 'нет данных в базе знаний', 'sources': []}\n    return {'answer': matched[0]['text'], 'sources': [matched[0]['id']]}\n", "'fastapi', [{'id':'doc-1','text':'FastAPI строит API'}]", "{'answer': 'FastAPI строит API', 'sources': ['doc-1']}", "assert {fn}('missing', [])['sources'] == []"),
            ("hallucination_guard", "запрети ответ без найденного источника", "def {fn}(draft, source_ids):\n    if draft and not source_ids:\n        return {'allowed': False, 'reason': 'no source'}\n    return {'allowed': True, 'answer': draft, 'sources': source_ids}\n", "'FastAPI есть в документе', ['doc-1']", "{'allowed': True, 'answer': 'FastAPI есть в документе', 'sources': ['doc-1']}", "assert {fn}('ответ', [])['allowed'] is False"),
            ("max_context_budget", "ограничь context по суммарной длине chunks", "def {fn}(chunks, max_chars):\n    selected = []\n    used = 0\n    for chunk in chunks:\n        size = len(chunk['text'])\n        if used + size > max_chars:\n            break\n        selected.append(chunk['id'])\n        used += size\n    return selected\n", "[{'id':'a','text':'123'}, {'id':'b','text':'4567'}], 4", "['a']", "assert {fn}([], 10) == []"),
        ],
        "vector": [
            ("mock_embedding", "создай mock embedding как частоты символов", "def {fn}(text):\n    return [text.lower().count(ch) for ch in 'abc']\n", "'abca'", "[2, 1, 1]", "assert {fn}('zzz') == [0, 0, 0]"),
            ("cosine_similarity_mock", "посчитай cosine similarity для коротких векторов", "def {fn}(left, right):\n    dot = sum(a * b for a, b in zip(left, right))\n    left_norm = sum(a * a for a in left) ** 0.5\n    right_norm = sum(b * b for b in right) ** 0.5\n    if not left_norm or not right_norm:\n        return 0\n    return round(dot / (left_norm * right_norm), 3)\n", "[1, 0], [1, 0]", "1.0", "assert {fn}([0, 0], [1, 2]) == 0"),
            ("top_k_vector_search", "верни top-k документов по score", "def {fn}(scores, k):\n    return [doc_id for doc_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:k]]\n", "{'b':0.8,'a':0.8,'c':0.1}, 2", "['a', 'b']", "assert {fn}({}, 3) == []"),
            ("metadata_filter_search", "отфильтруй vector results по metadata", "def {fn}(results, language):\n    return [item['id'] for item in results if item.get('metadata', {}).get('lang') == language]\n", "[{'id':'d1','metadata':{'lang':'ru'}}, {'id':'d2','metadata':{'lang':'en'}}], 'ru'", "['d1']", "assert {fn}([], 'ru') == []"),
            ("stale_index_case", "обнаружь устаревший индекс по версии документа", "def {fn}(doc_version, index_version):\n    return {'fresh': doc_version == index_version, 'needs_rebuild': doc_version != index_version}\n", "3, 2", "{'fresh': False, 'needs_rebuild': True}", "assert {fn}(1, 1)['fresh'] is True"),
        ],
        "graph": [
            ("chain_state_steps", "проведи state через chain шагов", "def {fn}(state, steps):\n    current = state.copy()\n    for step in steps:\n        current = step(current)\n    return current\n", "{'text':'hi'}, [lambda s: {**s, 'length': len(s['text'])}]", "{'text': 'hi', 'length': 2}", "assert {fn}({}, []) == {}"),
            ("node_transition", "выбери следующий node по состоянию", "def {fn}(state):\n    if state.get('error'):\n        return 'retry'\n    if state.get('done'):\n        return 'finish'\n    return 'generate'\n", "{'done': True}", "'finish'", "assert {fn}({'error': 'timeout'}) == 'retry'"),
            ("retry_node_budget", "уменьши retry budget в graph-node", "def {fn}(state):\n    budget = state.get('retry_budget', 0)\n    if budget <= 0:\n        return {'next': 'fail', 'retry_budget': 0}\n    return {'next': 'retry', 'retry_budget': budget - 1}\n", "{'retry_budget': 2}", "{'next': 'retry', 'retry_budget': 1}", "assert {fn}({'retry_budget': 0})['next'] == 'fail'"),
            ("tool_call_abstraction", "опиши tool call без прямого внешнего вызова", "def {fn}(tool_name, args):\n    allowed = {'search_docs', 'read_file'}\n    if tool_name not in allowed:\n        raise ValueError('unknown tool')\n    return {'tool': tool_name, 'args': args, 'mocked': True}\n", "'search_docs', {'q':'api'}", "{'tool': 'search_docs', 'args': {'q': 'api'}, 'mocked': True}", "with pytest.raises(ValueError):\n    {fn}('shell', {})"),
            ("termination_condition", "останови graph по max_steps или done", "def {fn}(state, max_steps):\n    if state.get('done'):\n        return 'stop'\n    if state.get('steps', 0) >= max_steps:\n        return 'stop'\n    return 'continue'\n", "{'steps': 2}, 3", "'continue'", "assert {fn}({'steps': 3}, 3) == 'stop'"),
        ],
        "vibecoding": [
            ("diff_review_prompt", "собери prompt для review только по diff", "def {fn}(diff_text):\n    if 'api_key' in diff_text.lower():\n        raise ValueError('secret in diff')\n    return {'task': 'review diff', 'diff': diff_text, 'require_tests': True}\n", "'+ def add(a, b): return a + b'", "{'task': 'review diff', 'diff': '+ def add(a, b): return a + b', 'require_tests': True}", "with pytest.raises(ValueError):\n    {fn}('+ api_key=123')"),
            ("secret_scan_vibe", "найди секреты в сгенерированном коде", "def {fn}(files):\n    risky = []\n    for path, content in files.items():\n        if 'password=' in content.lower() or 'api_key' in content.lower():\n            risky.append(path)\n    return sorted(risky)\n", "{'app.py':'print(1)', '.env':'API_KEY=123'}", "['.env']", "assert {fn}({'x.py':'safe'}) == []"),
            ("dependency_risk_check", "отметь рискованную зависимость из AI-патча", "def {fn}(requirements, allowlist):\n    return [package for package in requirements if package.split('==')[0] not in allowlist]\n", "['fastapi==1.0', 'unknownpkg==0.1'], {'fastapi'}", "['unknownpkg==0.1']", "assert {fn}([], set()) == []"),
            ("hallucinated_api_detector", "поймай вызов несуществующего API в предложенном коде", "def {fn}(code, allowed_calls):\n    unknown = []\n    for marker in ['client.magic(', 'db.auto_migrate(', 'ai.solve_all(']:\n        if marker in code and marker not in allowed_calls:\n            unknown.append(marker[:-1])\n    return unknown\n", "'client.magic()\\nprint(1)' , set()", "['client.magic']", "assert {fn}('print(1)', set()) == []"),
            ("tests_required_gate", "не принимай AI-код без проверок", "def {fn}(changed_files):\n    has_code = any(path.endswith('.py') and not path.startswith('test_') for path in changed_files)\n    has_check = any(path.startswith('test_') for path in changed_files)\n    return {'accepted': (not has_code) or has_check}\n", "['app.py', 'test_app.py']", "{'accepted': True}", "assert {fn}(['app.py'])['accepted'] is False"),
        ],
    }
    cases = cases_by_family[family]
    original_step_title = st["title"]
    name, task, solution, args, expected, negative = cases[(st["order"] - 4) % len(cases)]
    fn = f"{name}_{lesson_slug}_{st['order']}_{idx}"
    solution = solution.replace("{fn}", fn)
    negative = negative.replace("{fn}", fn)
    provider_helper = ""
    if "Provider()" in args or "TimeoutProvider()" in args or "FlakyProvider()" in args or "BrokenProvider()" in negative:
        provider_helper = (
            "class Provider:\n"
            "    def complete(self, messages, timeout=None):\n"
            "        return 'pong'\n\n\n"
            "class TimeoutProvider:\n"
            "    def complete(self, messages, timeout=None):\n"
            "        raise TimeoutError('late')\n\n\n"
            "class FlakyProvider:\n"
            "    def __init__(self):\n"
            "        self.calls = 0\n"
            "    def complete(self, messages, timeout=None):\n"
            "        self.calls += 1\n"
            "        if self.calls == 1:\n"
            "            raise RuntimeError('temporary')\n"
            "        return 'pong'\n\n\n"
            "class BrokenProvider:\n"
            "    def complete(self, messages, timeout=None):\n"
            "        raise RuntimeError('down')\n\n\n"
        )
    call = f"{fn}({args})" if args else f"{fn}()"
    test_code = (
        f"import pytest\nfrom solution import {fn}\n\n\n"
        f"{provider_helper}"
        f"def test_ai_public_{idx}():\n    assert {call} == {expected}\n\n\n"
    )
    negative_indented = "\n".join(("    " + line) if line else "" for line in negative.splitlines())
    test_code += f"def test_ai_negative_{idx}():\n{negative_indented}\n"
    st["title"] = name.replace("_", " ").title()
    st["body_markdown"] = (
        f"**Коротко:** {task}.\n\n"
        f"### Условие\nРеализуй `{fn}` для темы `{lesson['title']}`. Сценарий: {original_step_title} / {stage}. Используй только mock/in-memory данные, без внешнего платного API.\n\n"
        f"### Вход\nАргументы функции: `{args if args else 'без аргументов'}`.\n\n"
        f"### Выход\nОжидаемый результат: `{expected}`.\n\n"
        f"### Что проверить\nПроверь основной сценарий и отдельный негативный случай: секрет, неверный JSON, timeout, пустой retrieval context, неподходящий tool или отсутствие проверки."
    )
    st["editor_initial_code"] = f"def {fn}(*args, **kwargs):\n    pass\n"
    st["solution_code"] = solution
    st["checker"] = {"type": "python_pytest", "timeout_sec": 8, "test_code": test_code, "hidden_tests": [{"name": f"ai_{family}_{name}_edge", "assertion": "family-specific AI edge contract is checked"}]}
    st["skill_focus"] = f"AI integration: {lesson['title']} / {family} / {name}"
    st["new_constraint"] = f"{lesson['title']}: {family} task uses a distinct input/output contract and mock-only execution"
    st["edge_case"] = f"AI {family} negative path for {name}"
    st["input_shape"] = f"AI {family} arguments for {name}"
    st["output_contract"] = f"AI {family} validated return value for {name}"
    st["algorithm_family"] = f"ai:{family}:{name}"


QUESTION_BLUEPRINTS = {
    "python": [
        ("Что вернёт Python-вызов {code} в сценарии {skill_token}?", "{answer}", "{explain}", ["ошибку импорта", "None", "пустой список"]),
        ("Почему Python-сценарий {skill_token} важно проверить отдельным примером?", "{answer}", "{explain}", ["из-за цвета IDE", "чтобы скрыть ошибку", "чтобы не писать return"]),
        ("Где в Python-сценарии {skill_token} появится крайний случай?", "{answer}", "{explain}", ["в Dockerfile", "в SSL", "в Git remote"]),
    ],
    "sql": [
        ("Почему SQL-сценарий {skill_token} может потерять строки?", "{answer}", "{explain}", ["из-за имени файла", "из-за Python print", "из-за Docker port"]),
        ("Что изменит ORDER BY в SQL-сценарии {skill_token}?", "{answer}", "{explain}", ["схему таблиц", "тип HTTP-ответа", "имя branch"]),
        ("Какой seed нужен, чтобы проверить SQL-сценарий {skill_token}?", "{answer}", "{explain}", ["только одна happy-path строка", "пустой README", "JWT без срока"]),
    ],
    "fastapi": [
        ("Почему FastAPI-контракт {skill_token} должен совпадать в условии и HTTP-проверке?", "{answer}", "{explain}", ["чтобы скрыть 500", "чтобы поменять порт", "чтобы не писать Pydantic"]),
        ("Какой status code нужен для негативного сценария FastAPI {skill_token}?", "{answer}", "{explain}", ["200 для любой ошибки", "301 всегда", "204 с телом ошибки"]),
        ("Что ломается, если route FastAPI {skill_token} заменить универсальным /health?", "{answer}", "{explain}", ["ничего, это тот же контракт", "только цвет Swagger", "только имя функции"]),
    ],
    "devops": [
        ("Что доказывает runtime-команда в DevOps-сценарии {skill_token}?", "{answer}", "{explain}", ["что файл просто существует", "что README длинный", "что SQL отсортирован"]),
        ("Почему для DevOps-сценария {skill_token} нужен dry-run или rollback?", "{answer}", "{explain}", ["чтобы пропустить проверку", "чтобы заменить тесты скриншотом", "чтобы не читать env"]),
        ("Какой сбой должен ловить DevOps-сценарий {skill_token}?", "{answer}", "{explain}", ["неверный цвет терминала", "пустой Python list", "лишний SQL alias"]),
    ],
    "project": [
        ("Какой артефакт делает final-gate {skill_token} проверяемым?", "{answer}", "{explain}", ["устное обещание", "пустой каталог", "скриншот без команды"]),
        ("Почему у final-gate {skill_token} нужны pass/fail критерии?", "{answer}", "{explain}", ["чтобы скрыть требования", "чтобы убрать README", "чтобы не запускать команды"]),
        ("Какой negative case нужен для final-gate {skill_token}?", "{answer}", "{explain}", ["только успешный путь", "случайный commit", "длинный заголовок"]),
    ],
}


def polish_test_questions(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] != "test":
        return
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    key = "project"
    if mode in {"python", "complex_python", "ai"}:
        key = "python"
    elif mode in {"sql", "sqlite"}:
        key = "sql"
    elif mode == "fastapi":
        key = "fastapi"
    elif mode in {"git", "ide", "devops", "final"}:
        key = "devops" if mode != "final" else "project"
    concept = f"{lesson['title']} / {st.get('lesson_stage', stage_for_step(st))}"
    variants = QUESTION_BLUEPRINTS[key]
    token_hash = hashlib.sha1(f"{lesson['id']}|{st['id']}".encode("utf-8")).hexdigest()[:8]
    scope_words = [
        "audit", "trace", "budget", "cursor", "ledger", "packet", "policy", "queue",
        "snapshot", "gateway", "registry", "timeline", "backpressure", "contract",
        "migration", "rollback", "observer", "fixture", "projection", "segment",
        "capacity", "boundary", "retry", "cache", "offset", "token", "schema", "probe",
    ]
    scope_word = scope_words[stable_index(lesson["id"], st["id"]) % len(scope_words)]
    domain_word = scope_word
    if key == "python":
        domain_word = slug(lesson["title"])
    elif key == "sql":
        domain_word = ["join-loss", "rollback-path", "window-rank", "cte-rollup", "null-filter", "index-plan"][stable_index(lesson["id"], st["id"]) % 6]
    elif key == "fastapi":
        domain_word = ["path-contract", "query-filter", "body-validation", "auth-guard", "router-depends", "error-shape"][stable_index(lesson["id"], st["id"]) % 6]
    elif key == "devops":
        domain_word = ["env-health", "image-layer", "compose-network", "ci-job", "deploy-dry-run", "rollback-check"][stable_index(lesson["id"], st["id"]) % 6]
    elif key == "project":
        domain_word = ["acceptance", "erd-index", "openapi-error", "jwt-refresh", "observability", "defense-risk"][stable_index(lesson["id"], st["id"]) % 6]
    skill_token = f"{scope_word}-{domain_word}-{slug(lesson['title'])}-{st.get('lesson_stage', stage_for_step(st))}-{slug(st['title'])}-{token_hash}"
    questions = []
    for idx, (text, answer, explain, wrong) in enumerate(variants, 1):
        if key == "python":
            fill = {
                "code": f"{slug(lesson['title']).replace('-', '_')}_case(['INFO:start', 'ERROR:db'])",
                "concept": concept,
                "skill_token": skill_token,
                "answer": "наблюдаемый return-контракт функции",
                "explain": "Проверка должна видеть возвращаемое значение и крайний случай, а не случайный stdout.",
            }
        elif key == "sql":
            fill = {
                "concept": concept,
                "skill_token": skill_token,
                "answer": "JOIN/WHERE/GROUP BY/ORDER BY меняют набор строк и порядок результата",
                "explain": "SQL-задача считается правильной только когда отвечает на вопрос к данным и стабильно сортирует результат.",
            }
        elif key == "fastapi":
            fill = {
                "concept": concept,
                "skill_token": skill_token,
                "answer": "method, path, request shape, status и response shape образуют один контракт",
                "explain": "Если студент реализует другой endpoint, автопроверка честно падает, даже если код синтаксически верный.",
            }
        elif key == "devops":
            fill = {
                "concept": concept,
                "skill_token": skill_token,
                "answer": "артефакт реально запускается и показывает наблюдаемый статус",
                "explain": "Production-сценарий нельзя принимать по наличию файла без команды запуска и диагностики.",
            }
        else:
            fill = {
                "concept": concept,
                "skill_token": skill_token,
                "answer": "файл, команда проверки, ожидаемый результат и критерии отказа",
                "explain": "Финальный gate должен быть воспроизводимым для ревьюера и понятным для студента.",
            }
        q_text = text.format(**fill)
        q_answer = answer.format(**fill)
        q_explain = explain.format(**fill)
        questions.append({
            "id": f"{st['id']}_prod_q{idx}",
            "question": q_text,
            "options": [{"id": "a", "text": wrong[0]}, {"id": "b", "text": q_answer}, {"id": "c", "text": wrong[1]}, {"id": "d", "text": wrong[2]}],
            "correct_answer_id": "b",
            "correct_option_index": 1,
            "explanation": q_explain,
        })
    st["questions"] = questions
    st["checker"] = quiz_checker(questions)


def production_role_text(st: dict[str, Any], lesson: dict[str, Any]) -> str:
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    stage = st.get("lesson_stage") or stage_for_step(st)
    order = st.get("order", 0)
    order_words = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango"]
    order_word = order_words[order % len(order_words)]
    if mode == "fastapi":
        checker = st.get("checker", {})
        public = checker.get("public_tests", [{}])[0]
        method = str(public.get("method", "HTTP")).upper()
        route_family = slug(display_route(str(public.get("path", "/endpoint"))))
        base_role = {
            "practice": "реализовать новый endpoint contract",
            "debug": "исправить неверный HTTP status и форму JSON",
            "edge": "обработать 401/404/422 negative path",
            "integration": "связать router, service и response model",
            "mini_project": "оформить router, schemas, service и OpenAPI table",
        }.get(stage, f"FastAPI contract stage {stage}")
        return f"{base_role}; {method} route family {route_family}; step {order_word}"
    if mode in {"sql", "sqlite"}:
        sql_focus = st.get("checker", {}).get("semantic_sql_focus", {}).get("concept") or st.get("title", "SQL scenario")
        base_role = {
            "practice": "написать запрос к конкретному seed-набору",
            "debug": "исправить запрос, который теряет строки или порядок",
            "edge": "проверить NULL, отсутствие строк или rollback",
            "integration": "связать DDL/DML, JOIN и диагностический запрос",
            "mini_project": "оформить SQL-файл с воспроизводимым запуском",
        }.get(stage, f"SQL stage {stage}")
        return f"{base_role}; concept {sql_focus}; step {order_word}"
    if "Git и GitHub" in lesson.get("roadmap_topics", []):
        git_roles = [
            "git init/config/status/add/commit",
            "restore/reset/revert для ошибочного изменения",
            "branch switch checkout и clean worktree",
            "merge conflict cleanup без маркеров",
            "rebase conflict и rebase --continue",
            "stash затем cherry-pick готового commit",
            "reflog recovery branch",
            "non-fast-forward pull --rebase и force-with-lease с риском",
        ]
        return f"{git_roles[order % len(git_roles)]}; step {order_word}"
    if mode in {"ide", "devops"}:
        devops_roles = [
            "Dockerfile build и запуск контейнера",
            "compose app+db с healthcheck",
            "env.example и отказ без обязательного секрета",
            "lint/test/build/deploy jobs в CI",
            "тесты внутри контейнера",
            "deploy dry-run и status check",
            "rollback dry-run после неудачного релиза",
            "logs/exec/networks diagnostics",
        ]
        return f"{devops_roles[order % len(devops_roles)]}; step {order_word}"
    if mode == "final":
        final_roles = [
            "acceptance criteria и ограничения",
            "ERD, связи, индексы и миграции",
            "OpenAPI contract, errors и statuses",
            "JWT auth, refresh и protected routes",
            "unit/integration/negative cases",
            "Docker runtime и env contract",
            "CI/CD jobs и rollback",
            "observability, README и defense checklist",
        ]
        return f"{final_roles[order % len(final_roles)]}; step {order_word}"
    return {
        "debug": "починить конкретную ошибку реализации",
        "edge": "обработать граничный вход",
        "integration": "связать новый навык с предыдущей темой",
        "mini_project": "собрать маленький воспроизводимый артефакт",
    }.get(stage, f"отработать практический сценарий {stage}") + f"; step {order_word}"


def polish_project_step(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] != "project":
        return
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    stage = st.get("lesson_stage") or stage_for_step(st)
    artifact = slug(f"{lesson['title']}-{st['title']}")
    role = production_role_text(st, lesson)
    role_slug = slug(role)[:48] or stage
    review_doc = f"docs/{artifact}-{role_slug}.md"
    proof_file = f".checks/{artifact}-{role_slug}.txt"
    st["body_markdown"] = (
        f"**Коротко:** сдай рабочий артефакт для `{lesson['title']}`.\n\n"
        f"### Условие\n"
        f"Тема работы: {lesson['title']}. Стадия: {stage}. Сценарий: {role}.\n"
        f"Подготовь проектный результат `{artifact}`: {role}. Добавь ключевой файл, команду запуска, отрицательный сценарий и короткое README-объяснение решения.\n\n"
        f"### Что сдаёшь\n"
        f"Файлы проекта, команду проверки из README и критерии pass/fail. Если это Git/DevOps/FastAPI/final gate, результат должен воспроизводиться без ручных догадок.\n\n"
        f"### Что проверить\n"
        f"Проверь чистое состояние репозитория, запуск команды, понятный expected result и отдельный негативный сценарий. Для Git-сценариев отдельно проверь merge, rebase, stash, cherry-pick, reflog и force-with-lease там, где они требуются."
    )
    if stage == "debug":
        st["body_markdown"] += "\n\n### Что исправить\nDebug-сценарий: найди конкретную ошибку в артефакте, зафиксируй причину в README и покажи команду, которая подтверждает исправление."
    st["skill_focus"] = f"{mode}: {lesson['title']} / {role}"
    st["new_constraint"] = f"artifact {artifact} must be reproducible at stage {stage}"
    st["edge_case"] = "negative case or rollback path is documented"
    st["input_shape"] = "project files, commands, runtime or git state"
    st["output_contract"] = f"required files and commands pass for {lesson['title']} / {role}"
    checker = st.get("checker", {})
    if checker.get("type") == "ide_plugin":
        checker["scenario_id"] = f"{slug(lesson['id'])}_{slug(st['id'])}_{slug(role)[:36]}"
        files = list(dict.fromkeys(checker.get("required_files", []) + [review_doc, proof_file]))
        checker["required_files"] = files
        checker["commands"] = list(checker.get("commands", [])) + [{"cmd": f"test -f {review_doc}", "expect_exit_code": 0}]
        checker["semantic_focus"] = {"role": role, "stage": stage, "artifact": artifact}
        if st.get("ide_plugin_check"):
            st["ide_plugin_check"]["scenario_id"] = checker["scenario_id"]
            st["ide_plugin_check"]["required_files"] = files
            st["ide_plugin_check"]["semantic_focus"] = checker["semantic_focus"]
    command_lines = "\n".join(cmd.get("cmd", "") for cmd in checker.get("commands", [])[:4] if cmd.get("cmd")) or "python -m pytest"
    st["solution_code"] = (
        f"Reference structure:\n"
        f"- README.md\n- {review_doc}\n- {proof_file}\n\n"
        f"Implementation focus:\n{lesson['title']} / {st['title']} / {role}\n\n"
        f"Commands:\n{command_lines}\nmkdir -p docs .checks\nprintf '%s\\n' '{role_slug}' > {proof_file}\n\n"
        f"Negative check:\nadd a failing input, missing env, bad branch, invalid payload or rollback path that matches `{role_slug}`.\n\n"
        f"Expected result:\nreviewer can verify `{lesson['title']}` / `{st['title']}` through `{review_doc}` and the command output without guessing.\n"
    )
    if "Git и GitHub" in lesson.get("roadmap_topics", []):
        st["solution_code"] += "\nGit scenario notes:\nmerge conflict, rebase conflict, stash, cherry-pick, reflog recovery, non-fast-forward and force-with-lease are checked across Git labs.\n"


def polish_ide_practice_step(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] != "practice" or st.get("checker", {}).get("type") != "ide_plugin":
        return
    checker = st.get("checker", {})
    mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
    stage = st.get("lesson_stage") or stage_for_step(st)
    role = production_role_text(st, lesson)
    role_slug = slug(role)[:48] or stage
    artifact = slug(f"{lesson['title']}-{st['title']}-{role_slug}")[:96]
    required = checker.get("required_files", [])
    command_lines = "\n".join(cmd.get("cmd", "") for cmd in checker.get("commands", [])[:4] if cmd.get("cmd")) or "python -m pytest"
    if mode == "devops":
        extra_commands = "docker compose config\nbash deploy/deploy.sh --dry-run || true\n"
        negative = "remove one required env key and confirm the runtime check fails before deploy."
    elif mode == "git":
        extra_commands = (
            f"git status --porcelain\n"
            f"git switch -c feature/{artifact[:40]}\n"
            f"git add {' '.join(required[:2]) if required else 'README.md'}\n"
            f"git commit -m 'Lab {role_slug[:32]}'\n"
            "git log --oneline --decorate -5\n"
        )
        negative = "leave a dirty file, conflict marker, wrong branch or missing commit and confirm the IDE check rejects it."
    else:
        extra_commands = "python -m pytest\npython -m compileall src\n"
        negative = "break the smallest required file and confirm the command fails before fixing it."
    st["body_markdown"] = (
        f"**Коротко:** собери воспроизводимый IDE-артефакт для темы `{lesson['title']}`.\n\n"
        f"### Условие\n"
        f"Тема работы: {lesson['title']}. Стадия: {stage}. Сценарий: {role}.\n"
        f"Подготовь файлы проекта, команду запуска и короткое README-объяснение. Результат должен проверять именно этот сценарий, а не только наличие README.\n\n"
        f"### Что сдаёшь\n"
        f"Минимальные файлы из проверки, команду из README и файл с подтверждением результата.\n\n"
        f"### Что проверить\n"
        f"{negative} После исправления команда должна завершиться успешно, а состояние проекта должно быть воспроизводимым."
    )
    if stage == "debug":
        st["body_markdown"] += "\n\n### Что исправить\nDebug-сценарий: покажи исходную ошибку, причину сбоя и команду, которая подтверждает исправленное состояние."
    st["solution_code"] = (
        f"Reference structure:\n"
        + "\n".join(f"- {path}" for path in required[:8])
        + f"\n- docs/{artifact}.md\n- .checks/{artifact}.txt\n\n"
        f"Implementation focus:\n{lesson['title']} / {st['title']} / {role}\n\n"
        f"Commands:\n{command_lines}\n{extra_commands}"
        f"mkdir -p docs .checks\nprintf '%s\\n' '{role_slug}' > .checks/{artifact}.txt\n\n"
        f"Negative check:\n{negative}\n\n"
        f"Expected result:\n`.checks/{artifact}.txt` records `{role_slug}`, required files exist, commands pass, and the negative check fails for the intended reason.\n"
    )


def append_student_role(st: dict[str, Any], lesson: dict[str, Any]) -> None:
    if st["type"] not in {"practice", "project"}:
        return
    role = production_role_text(st, lesson)
    scenario_seed = f"{lesson['id']}|{st['id']}|{role}|{st.get('checker', {}).get('type', 'manual')}"
    st["scenario_id"] = st.get("scenario_id") or f"{slug(lesson['id'])}_{slug(st['id'])}_{hashlib.sha1(scenario_seed.encode('utf-8')).hexdigest()[:12]}"
    placeholder_terms = ["validation-specific result", "task input described in body", "edge case for", "placeholder", "заглуш"]
    if any(term in str(st.get("edge_case", "")).lower() for term in placeholder_terms):
        st["edge_case"] = f"explicit negative or boundary case for {lesson['title']} / {st['title']}"
    if any(term in str(st.get("input_shape", "")).lower() for term in placeholder_terms):
        checker_type = st.get("checker", {}).get("type", "manual")
        st["input_shape"] = f"{checker_type} input for {lesson['title']} / {st['title']}"
    if any(term in str(st.get("output_contract", "")).lower() for term in placeholder_terms):
        checker_type = st.get("checker", {}).get("type", "manual")
        st["output_contract"] = f"{checker_type} observable output for {lesson['title']} / {st['title']}"
    st["skill_focus"] = f"{st.get('skill_focus', lesson_mode(lesson['title'], lesson.get('roadmap_topics', [])))} | {role}"
    st["new_constraint"] = f"{st.get('new_constraint', 'observable constraint')} | stage {st.get('lesson_stage', stage_for_step(st))}"
    st["output_contract"] = f"{st.get('output_contract', 'observable result')} | role {role}"


def remove_artificial_solution_bits(st: dict[str, Any]) -> None:
    solution = st.get("solution_code", "") or ""
    solution = re.sub(r"(?m)^\s*SCENARIO_MARKER_[A-Z0-9_]+\s*=.*\n?", "", solution)
    solution = re.sub(r"(?m)^\s*SCENARIO_PURPOSE_[A-Z0-9_]+\s*=.*\n?", "", solution)
    solution = re.sub(r"\n?def contract_requirements_[\s\S]*?(?=\n\s*(def |class |@|# Learning role:|Reference structure:|Commands:|Expected result:|\Z))", "\n", solution)
    solution = re.split(r"\n\s*# Learning role:", solution, maxsplit=1)[0].rstrip() + "\n"
    st["solution_code"] = solution
    checker = st.get("checker", {})
    if checker.get("type") == "python_pytest" and checker.get("test_code"):
        test_code = checker["test_code"]
        test_code = re.sub(r"\n\nSCENARIO_UNDER_TEST\s*=.*?\n\n\s*def test_contract_marker_[\s\S]*?(?=\n\n|\Z)", "", test_code)
        checker["test_code"] = test_code.strip() + "\n"
    for key in ["sql_scenario_marker", "contract_focus"]:
        checker.pop(key, None)


def final_production_polish(course: dict[str, Any]) -> None:
    for _, lesson, st in iter_steps(course):
        st["body_markdown"] = strip_service_sections(st.get("body_markdown", ""))
        if st["type"] == "test":
            polish_test_questions(st, lesson)
        if st.get("checker", {}).get("type") == "sql_query":
            polish_sql_step(st, lesson)
        if st.get("checker", {}).get("type") == "http_api":
            polish_realistic_fastapi_contract(st, lesson)
            polish_http_step(st, lesson)
        polish_sqlite_python_step(st, lesson)
        polish_python_step(st, lesson)
        polish_ai_python_step(st, lesson)
        polish_ide_practice_step(st, lesson)
        polish_project_step(st, lesson)
        append_student_role(st, lesson)
        if st["type"] in {"practice", "project"}:
            if not st.get("skill_focus"):
                st["skill_focus"] = f"{lesson_mode(lesson['title'], lesson.get('roadmap_topics', []))}: {lesson['title']} / {st['title']}"
            if not st.get("new_constraint"):
                st["new_constraint"] = f"new observable constraint for {st['title']}"
            if not st.get("edge_case"):
                st["edge_case"] = "explicit edge or negative scenario"
            if not st.get("input_shape"):
                st["input_shape"] = "student code, project files or query input"
            if not st.get("output_contract"):
                st["output_contract"] = "observable result described in student task"
            st["qa_notes"] = st.get("qa_notes", "Production polish keeps method/path/body/checker and semantic focus aligned.")
        remove_artificial_solution_bits(st)
        st["body_markdown"] = strip_service_sections(st.get("body_markdown", ""))
    for _, lesson in iter_lessons(course):
        lesson["estimated_hours"] = round(sum(s["estimated_minutes"] for s in lesson["steps"]) / 60, 2)


def post_process_course(course: dict[str, Any]) -> None:
    course["package_version"] = "v16_LESSON_LADDER"
    course["course"]["id"] = "python_backend_ai_v16_lesson_ladder"
    course["course"]["description"] = "Импортируемый пакет курса, пересобранный под стандарт учебной лестницы: зачем, объяснение с нуля, 3+ вопроса, практика, debugging, edge, integration/project и итог в каждом уроке."
    course["course"]["source_note"] = "v16 uses the approved roadmap order and adds lesson_stage metadata, richer theory, AI-specific tasks, deeper debugging and project artifacts before import."
    for _, lesson in iter_lessons(course):
        ensure_lesson_ladder(lesson)
    for module, lesson, st in iter_steps(course):
        mode = lesson_mode(lesson["title"], lesson.get("roadmap_topics", []))
        if st["type"] == "test":
            specialize_test_questions(st, lesson)
        if st["type"] == "practice" and st.get("checker", {}).get("type") == "python_pytest" and mode in {"python", "complex_python"}:
            specialize_python_practice(st, lesson)
            enrich_step_body(st, lesson)
        if st["type"] == "practice" and st.get("checker", {}).get("type") == "sql_query":
            specialize_sql_practice(st, lesson)
        if st.get("checker", {}).get("type") == "http_api":
            specialize_http_contract(st, lesson)
        specialize_ide_solution(st, lesson)
        add_test_code_contract_marker(st, lesson)
        apply_step_focus_fields(st, lesson)
        append_unique_solution_artifact(st, lesson)
        c = st.get("checker", {})
        if c.get("type") == "ide_plugin":
            skill = slug(f"{st.get('lesson_stage', 'step')}-{st.get('title', 'task')}-{c.get('semantic_focus', {}).get('role', 'role')}")
            scenario_id = f"{module['id']}_{lesson['id']}_{st['id']}_{skill}"
            c["scenario_id"] = scenario_id
            if st.get("ide_plugin_check"):
                st["ide_plugin_check"]["scenario_id"] = scenario_id
                st["ide_plugin_check"]["semantic_focus"] = c.get("semantic_focus")
    final_production_polish(course)


def infer_mode(title: str, topics: list[str]) -> str:
    if "финальный проект" in topics:
        return "final"
    if topics and set(topics) & {"AI для учёбы", "AI API", "RAG", "vector databases", "LangChain / LangGraph концептуально", "вайбкодинг"}:
        return "ai"
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
        mid = f"v16_m{mi:02d}"
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
                elif mode == "ai":
                    steps = make_ai_steps(lesson_id, title, topics)
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
    course = {
        "schema_version": "1.0",
        "package_version": "v16_LESSON_LADDER",
        "course": {
            "id": "python_backend_ai_v16_lesson_ladder",
            "title": TITLE,
            "description": "Полный импортируемый пакет курса, пересобранный под стандарт учебной лестницы: зачем, объяснение с нуля, проверка понимания, практика, debugging, edge, integration/project и итог.",
            "target_level": TARGET,
            "source_note": "Lesson order follows the approved roadmap skeleton. v16 adds lesson_stage metadata, AI-specific tasks, richer theory and stronger learning progression.",
            "modules": modules,
        },
    }
    post_process_course(course)
    return course


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
    with path.open("w", encoding="utf-8", newline="") as f:
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
    relevant = {k: c.get(k) for k in ["type", "scenario_id", "required_files", "commands", "git_checks", "public_tests", "schema_sql", "seed_sql", "app_import", "semantic_focus"] if k in c}
    return hashlib.sha1(json.dumps(relevant, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def normalized_for_duplicate(value: str) -> str:
    value = re.sub(r"`[^`]+`", "`x`", value or "")
    value = re.sub(r"\d+", "N", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def strip_generated_learning_footer(value: str) -> str:
    value = value or ""
    return re.split(r"\n\s*# Learning role:", value, maxsplit=1)[0]


def normalized_solution_code(value: str) -> str:
    value = strip_generated_learning_footer(value)
    value = re.sub(r"(?m)^\s*SCENARIO_MARKER_[A-Z0-9_]+\s*=.*$", "", value)
    value = re.sub(r"(?m)^\s*SCENARIO_PURPOSE_[A-Z0-9_]+\s*=.*$", "", value)
    value = re.sub(r"(?m)^\s*#.*$", "", value)
    value = re.sub(r"\bv\d+_m\d+_l\d+_[a-z0-9_-]+_s\d+_[a-z0-9_-]+\b", "ID", value, flags=re.I)
    value = re.sub(r"\bm\d+_l\d+_[a-z0-9_-]+_s\d+_[a-z0-9_-]+\b", "ID", value, flags=re.I)
    value = re.sub(r"\bs\d{3}\b", "STEP", value, flags=re.I)
    value = re.sub(r"\b\d+\b", "N", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def structural_solution_signature(value: str) -> str:
    value = strip_generated_learning_footer(value or "")
    value = re.sub(r"(?m)^\s*#.*$", "", value)
    value = re.sub(r"\bdef\s+[A-Za-z_][A-Za-z0-9_]*", "def FN", value)
    value = re.sub(r"\bclass\s+[A-Za-z_][A-Za-z0-9_]*", "class CLS", value)
    value = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*_[a-z0-9_]+_(alpha|bravo|charlie|delta|echo|foxtrot|golf|hotel|india|juliet|kilo|lima|mike|november|oscar|papa|quebec|romeo|sierra|tango|uniform|victor|whiskey|xray)\b", "NAME", value, flags=re.I)
    value = re.sub(r"\b(v\d+_)?m\d+_l\d+_[a-z0-9_-]+_s\d+_[a-z0-9_-]+\b", "ID", value, flags=re.I)
    value = re.sub(r"\b\d+\b", "N", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def normalized_test_code(value: str) -> str:
    value = value or ""
    value = re.sub(r"(?m)^\s*#.*$", "", value)
    value = re.sub(r"\b\d+\b", "N", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def normalized_sql_query(value: str) -> str:
    value = strip_generated_learning_footer(value)
    value = re.sub(r"--.*", "", value)
    value = re.sub(r"\b\d+\b", "N", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def http_contract_signature(st: dict[str, Any]) -> str:
    checker = st.get("checker", {})
    tests = checker.get("public_tests", []) + checker.get("hidden_tests", [])
    compact = []
    for test in tests:
        compact.append({
            "method": test.get("method"),
            "path": test.get("path"),
            "params": test.get("params"),
            "json": test.get("json"),
            "status": test.get("expected_status"),
            "json_subset": test.get("expected_json_subset"),
            "json_type": test.get("expected_json_type"),
            "headers": test.get("expected_headers"),
        })
    return hashlib.sha1(json.dumps(compact, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def python_skill_terms(title: str, topics: list[str]) -> list[str]:
    low = title.lower()
    joined = " ".join(topics).lower() + " " + low
    if "строк" in joined:
        return ["strip", "split", "casefold", "replace", "startswith", "endswith"]
    if "ввод" in joined or "числ" in joined:
        return ["int(", "float(", "split", "sum("]
    if "bool" in joined or "none" in joined:
        return ["is none", "is not none", " and ", " or ", "bool("]
    if "услов" in joined:
        return ["if ", "elif", "else"]
    if "тип" in joined or "память" in joined:
        return ["copy", "list(", "tuple(", "is "]
    if "цикл" in joined:
        return ["for ", "while ", "break", "continue"]
    if "списк" in joined:
        return ["append", "list(", "[", "enumerate"]
    if "функц" in joined:
        return ["def ", "return", "callable"]
    if "кортеж" in joined:
        return ["tuple", "x, y", "unpack"]
    if "множе" in joined:
        return ["set(", "intersection", "union", "difference"]
    if "словар" in joined:
        return ["dict", ".get(", ".items(", "keys("]
    if "map" in joined or "filter" in joined or "lambda" in joined:
        return ["map(", "filter(", "lambda"]
    if "datetime" in joined:
        return ["datetime", "date", "timedelta", "fromisoformat"]
    if "итератор" in joined:
        return ["iter(", "next(", "__iter__"]
    if "генератор" in joined:
        return ["yield", "generator"]
    if "декоратор" in joined:
        return ["wrapper", "*args", "**kwargs"]
    if "контекст" in joined:
        return ["with ", "__enter__", "__exit__", "contextmanager"]
    if "исключ" in joined:
        return ["try:", "except", "raise"]
    if "pathlib" in joined or "файл" in joined:
        return ["path", "read_text", "write_text", "suffix"]
    if "json" in joined:
        return ["json.", "loads", "dumps"]
    if "csv" in joined:
        return ["csv.", "reader", "dictreader"]
    if "логирован" in joined:
        return ["logging", "logger"]
    if "пакет" in joined or "импорт" in joined or "poetry" in joined:
        return ["import", "pyproject", "__init__"]
    if "pytest" in joined:
        return ["pytest", "assert", "fixture", "parametrize", "mock"]
    if "threading" in joined:
        return ["thread", "lock", "queue"]
    if "multiprocessing" in joined:
        return ["process", "pool", "queue", "cpu_count"]
    if "asyncio" in joined:
        return ["async", "await", "asyncio"]
    if "типизация" in joined or "mypy" in joined:
        return [": ", "->", "protocol", "typed"]
    if "ооп" in joined or "магические" in joined or "наследование" in joined or "полиморфизм" in joined or "протокол" in joined:
        return ["class ", "self", "__init__", "protocol"]
    return ["return", "def "]


def python_practice_uses_key_skill(st: dict[str, Any], lesson: dict[str, Any]) -> bool:
    blob = (st.get("body_markdown", "") + "\n" + st.get("solution_code", "") + "\n" + st.get("checker", {}).get("test_code", "")).lower()
    return any(term.lower() in blob for term in python_skill_terms(lesson["title"], lesson.get("roadmap_topics", [])))


REQUIRED_FOCUS_FIELDS = ["skill_focus", "new_constraint", "edge_case", "input_shape", "output_contract"]


def algorithmic_pattern(st: dict[str, Any], lesson: dict[str, Any]) -> str:
    if st["type"] not in {"practice", "project"}:
        return ""
    parts = [
        lesson_mode(lesson["title"], lesson.get("roadmap_topics", [])),
        st.get("skill_focus", ""),
        st.get("new_constraint", ""),
        st.get("input_shape", ""),
        st.get("output_contract", ""),
    ]
    return normalized_for_duplicate(" | ".join(parts))


BANNED_ALGORITHM_FAMILIES = [
    "lesson_contract",
    "safe_lookup",
    "window_pairs",
    "reject_none",
    "format_record",
]


def banned_algorithm_family_hit(st: dict[str, Any]) -> bool:
    blob = "\n".join([
        st.get("title", ""),
        st.get("skill_focus", ""),
        st.get("edge_case", ""),
        st.get("input_shape", ""),
        st.get("output_contract", ""),
        st.get("algorithm_family", ""),
        st.get("solution_code", ""),
        st.get("checker", {}).get("test_code", ""),
    ]).lower().replace(" ", "_")
    return any(family in blob for family in BANNED_ALGORITHM_FAMILIES)


def oop_requirement_violation(st: dict[str, Any], lesson: dict[str, Any]) -> str:
    if st["type"] != "practice" or st.get("checker", {}).get("type") != "python_pytest":
        return ""
    title_low = lesson["title"].lower()
    low = (lesson["title"] + " " + " ".join(lesson.get("roadmap_topics", []))).lower()
    sol = st.get("solution_code", "")
    if not any(term in low for term in ["ооп", "dataclass", "магичес", "протокол", "наслед", "полиморф", "абстрак", "инкапсул", "композиц"]):
        return ""
    if "dataclass" in title_low and "@dataclass" not in sol:
        return "dataclass lesson without @dataclass"
    if "dataclass" in title_low:
        return ""
    if "магичес" in title_low and not re.search(r"__(repr|str|eq|lt|len|contains|add)__", sol):
        return "magic methods lesson without dunder method"
    if "магичес" in title_low:
        return ""
    if "протокол" in title_low and "Protocol" not in sol and "runtime_checkable" not in sol:
        return "protocol lesson without Protocol"
    if "протокол" in title_low:
        return ""
    if "наслед" in title_low and not re.search(r"class\s+\w+\s*\(\s*\w+", sol):
        return "inheritance lesson without subclass"
    if "наслед" in title_low:
        return ""
    if "полиморф" in title_low and (sol.count("class ") < 2 or not re.search(r"for\s+\w+\s+in\s+", sol)):
        return "polymorphism lesson without multiple implementations"
    if "полиморф" in title_low:
        return ""
    if "абстрак" in title_low and ("ABC" not in sol or "abstractmethod" not in sol):
        return "abstraction lesson without ABC/abstractmethod"
    if "абстрак" in title_low:
        return ""
    if "инкапсул" in title_low and ("@property" not in sol or "ValueError" not in sol or "_" not in sol):
        return "encapsulation lesson without property/invariant"
    if "инкапсул" in title_low:
        return ""
    if "композиц" in title_low and (sol.count("class ") < 2 or "self." not in sol):
        return "composition lesson without object composition"
    if "композиц" in title_low:
        return ""
    if "ооп" in title_low and ("class " not in sol or "__init__" not in sol or "self." not in sol):
        return "OOP lesson without class/__init__/self"
    return ""


def fastapi_route_model_signature(st: dict[str, Any]) -> str:
    checker = st.get("checker", {})
    focus = checker.get("api_focus") or checker.get("contract_focus") or {}
    tests = checker.get("public_tests", []) + checker.get("hidden_tests", [])
    route_shapes = []
    for test in tests:
        route_shapes.append({
            "method": test.get("method"),
            "path_shape": re.sub(r"/labs/[^/]+/s\d+", "/labs/{lesson}/{step}", test.get("path", "")),
            "status": test.get("expected_status"),
            "body_keys": sorted((test.get("json") or {}).keys()),
            "json_keys": sorted((test.get("expected_json_subset") or {}).keys()),
            "json_type": test.get("expected_json_type"),
            "headers": test.get("expected_headers"),
        })
    payload = {
        "api_focus": focus,
        "route_shapes": route_shapes,
    }
    return hashlib.sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def has_artificial_fastapi_route(st: dict[str, Any]) -> bool:
    if st.get("checker", {}).get("type") != "http_api":
        return False
    for method, path in checker_route_pairs(st):
        if path.startswith("/labs/"):
            return True
        if not REAL_FASTAPI_ROUTE_RE.match(path):
            return True
    return False


def ai_family_for_lesson(title: str) -> str:
    low = title.lower()
    if "для уч" in low:
        return "study"
    if "prompt" in low or "messages" in low:
        return "messages"
    if "structured output" in low:
        return "structured"
    if "json schema" in low:
        return "schema"
    if "mock provider" in low:
        return "provider"
    if "retries" in low or "timeouts" in low:
        return "reliability"
    if "rate limits" in low or "cost" in low:
        return "rate_cost"
    if "rag" in low:
        return "rag"
    if "embedding" in low or "vector" in low or "вектор" in low:
        return "vector"
    if "retrieval" in low or "hallucination" in low:
        return "evaluation"
    if "langchain" in low or "langgraph" in low:
        return "graph"
    if "вайб" in low or "безопас" in low:
        return "vibecoding"
    return "request"


def ai_quality_violation(st: dict[str, Any], lesson: dict[str, Any]) -> str:
    if st["type"] != "practice" or st.get("checker", {}).get("type") != "python_pytest":
        return ""
    if lesson_mode(lesson["title"], lesson.get("roadmap_topics", [])) != "ai":
        return ""
    family = ai_family_for_lesson(lesson["title"])
    blob = (
        st.get("body_markdown", "")
        + "\n"
        + st.get("solution_code", "")
        + "\n"
        + st.get("checker", {}).get("test_code", "")
        + "\n"
        + st.get("skill_focus", "")
    ).lower()
    if family == "rag" and not ("retriev" in blob and "source" in blob and ("no_answer" in blob or "нет данных" in blob) and "hallucination" in blob):
        return "RAG task lacks retrieval/source/no-answer/hallucination guard"
    if family == "evaluation" and not ("source" in blob and ("faithful" in blob or "recall" in blob or "hallucination" in blob)):
        return "retrieval evaluation task lacks source/faithfulness/recall checks"
    if family == "graph" and not ("state" in blob and "node" in blob and "transition" in blob):
        return "LangGraph task lacks state/node/transition"
    if family == "vibecoding" and not any(token in blob for token in ["review", "diff", "secret", "dependency", "check_required", "check gate", "check_"]):
        return "safe vibe task lacks review/security/diff/dependency/check gate"
    return ""


def sql_progression_violation(st: dict[str, Any], lesson: dict[str, Any]) -> str:
    if st.get("checker", {}).get("type") != "sql_query":
        return ""
    if lesson["title"].strip().lower() != "sql: select":
        return ""
    blob = (
        st.get("body_markdown", "")
        + "\n"
        + st.get("solution_code", "")
        + "\n"
        + json.dumps(st.get("checker", {}), ensure_ascii=False)
    ).lower()
    future_tokens = ["row_number", " over ", "partition by", "rollback", "savepoint", "begin;", "commit;", "create index", "explain", " with ", "\nwith ", " join "]
    found = [token.strip() for token in future_tokens if token in blob]
    return "SQL SELECT contains future topic: " + ", ".join(found) if found else ""


def fastapi_title_method_mismatch(st: dict[str, Any]) -> bool:
    if st.get("checker", {}).get("type") != "http_api":
        return False
    public = st.get("checker", {}).get("public_tests", [{}])[0]
    method = str(public.get("method", "")).upper()
    title_match = re.match(r"^(GET|POST|PUT|PATCH|DELETE)\b", st.get("title", ""), flags=re.I)
    return bool(title_match and title_match.group(1).upper() != method)


def fastapi_solution_method_mismatch(st: dict[str, Any]) -> bool:
    if st.get("checker", {}).get("type") != "http_api":
        return False
    public = st.get("checker", {}).get("public_tests", [{}])[0]
    method = str(public.get("method", "")).lower()
    solution = st.get("solution_code", "").lower()
    return bool(method and f"@app.{method}" not in solution)


def early_future_knowledge_violation(st: dict[str, Any], lesson: dict[str, Any]) -> bool:
    if not lesson["id"].startswith("v16_m01") or lesson["order"] > 8 or st["type"] != "practice":
        return False
    blob = (st.get("editor_initial_code", "") + "\n" + st.get("solution_code", "") + "\n" + st.get("checker", {}).get("test_code", "")).lower()
    forbidden_by_order = {
        1: [r"\binput\s*\(", r"\bdef\s+", r"\breturn\b", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\{", r"\}", r"\.items\s*\(", r"\.copy\s*\(", r"\[.*\]"],
        2: [r"\bdef\s+", r"\breturn\b", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\{", r"\}", r"\.items\s*\(", r"\.copy\s*\(", r"\[[^\]]*,[^\]]*\]"],
        3: [r"\bdef\s+", r"\breturn\b", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\{", r"\}", r"\.items\s*\(", r"\.copy\s*\("],
        4: [r"\bdef\s+", r"\breturn\b", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\{", r"\}", r"\.items\s*\(", r"\.copy\s*\("],
        5: [r"\bdef\s+", r"\breturn\b", r"\bfor\s+", r"\bwhile\s+", r"\{", r"\}", r"\.items\s*\(", r"\.copy\s*\("],
        6: [r"\bdef\s+", r"\breturn\b", r"\bfor\s+", r"\bwhile\s+", r"\{", r"\}", r"\.items\s*\(", r"\.copy\s*\("],
        7: [r"\bdef\s+", r"\breturn\b", r"\{", r"\}", r"\.items\s*\(", r"\.copy\s*\(", r"\[[^\]]*,[^\]]*\]"],
        8: [r"\bdef\s+", r"\breturn\b", r"\{", r"\}", r"\.items\s*\("],
    }
    return any(re.search(pattern, blob) for pattern in forbidden_by_order.get(lesson["order"], []))


def sql_dataset_signature(st: dict[str, Any]) -> str:
    checker = st.get("checker", {})
    payload = {
        "schema_sql": normalized_sql_query(checker.get("schema_sql", "")),
        "seed_sql": normalized_sql_query(checker.get("seed_sql", "")),
        "expected_rows": checker.get("public_tests", [{}])[0].get("expected_rows"),
    }
    return hashlib.sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def semantic_checker_signature(st: dict[str, Any]) -> str:
    c = st.get("checker", {})
    relevant = {
        "type": c.get("type"),
        "semantic_focus": c.get("semantic_focus"),
        "scenario_id": c.get("scenario_id"),
        "required_files": c.get("required_files"),
        "commands": c.get("commands"),
        "git_checks": c.get("git_checks"),
        "schema_sql": c.get("schema_sql"),
        "seed_sql": c.get("seed_sql"),
        "public_tests": c.get("public_tests"),
        "app_import": c.get("app_import"),
    }
    if c.get("type") == "python_pytest":
        relevant["test_code"] = normalized_test_code(c.get("test_code", ""))
    return hashlib.sha1(json.dumps(relevant, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def stats(course: dict[str, Any]) -> dict[str, Any]:
    steps = list(iter_steps(course))
    by_type = Counter(st["type"] for _, _, st in steps)
    by_checker = Counter(st.get("checker", {}).get("type", "none") for _, _, st in steps)
    lessons = list(iter_lessons(course))
    lesson_stage_gaps = []
    lessons_without_project = []
    short_test_steps = []
    complex_short_lessons = []
    ai_non_ai_practices = []
    duplicate_question_over_limit = []
    duplicate_scenario_ids = []
    lesson_duplicate_body = []
    lesson_duplicate_solution = []
    lesson_duplicate_checker = []
    generic_test_questions = []
    bad_stage_content = []
    short_complex_theory = []
    weak_project_solutions = []
    course_solution_counts = Counter()
    course_solution_examples: dict[str, list[str]] = defaultdict(list)
    course_test_code_counts = Counter()
    lesson_test_code_dups = []
    sql_practice_counts = Counter()
    sql_practice_examples: dict[str, list[str]] = defaultdict(list)
    sql_dataset_counts = Counter()
    http_contract_counts = Counter()
    http_contract_examples: dict[str, set[str]] = defaultdict(set)
    fastapi_route_model_counts = Counter()
    algorithmic_pattern_counts = Counter()
    algorithm_family_counts = Counter()
    structural_solution_counts = Counter()
    ai_structural_solution_lessons: dict[str, set[str]] = defaultdict(set)
    ai_structural_solution_counts = Counter()
    ai_quality_violations = []
    sql_progression_violations = []
    fastapi_title_method_mismatches = []
    fastapi_solution_method_mismatches = []
    fastapi_lesson_business_duplicates = []
    fastapi_method_path_status_duplicates = []
    encoding_corruption_items = collect_json_corruption(course)
    package_file_corruption_items = collect_file_corruption()
    ai_aggressive_solution_counts = Counter()
    missing_focus_fields = []
    missing_top_level_scenario_ids = []
    placeholder_focus_fields = []
    body_service_sections = []
    http_body_checker_mismatches = []
    fastapi_artificial_routes = []
    future_knowledge_violations = []
    artificial_uniqueness_markers = []
    template_questions = []
    template_question_signature_counts = Counter()
    python_key_skill_mismatch = []
    oop_key_skill_mismatch = []
    banned_algorithm_family_hits = []
    question_counts = Counter()
    scenario_counts = Counter()
    lesson_dup_track: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: {"body": Counter(), "solution": Counter(), "checker": Counter()})
    for _, lesson in lessons:
        stages = {st.get("lesson_stage") for st in lesson["steps"]}
        missing = LADDER_REQUIRED_STAGES - stages
        if missing:
            lesson_stage_gaps.append({"lesson": lesson["title"], "missing": sorted(missing)})
        if not any(st["type"] == "project" for st in lesson["steps"]):
            lessons_without_project.append(lesson["title"])
        lesson_test_codes = Counter()
        lesson_fastapi_contracts = Counter()
        lesson_fastapi_method_path_status = Counter()
        for st in lesson["steps"]:
            if st["type"] == "test" and len(st.get("questions", [])) < 3:
                short_test_steps.append(st["id"])
            for q in st.get("questions", []):
                question_counts[q.get("question", "")] += 1
            c = st.get("checker", {})
            if c.get("scenario_id"):
                scenario_counts[c["scenario_id"]] += 1
            if st["type"] in {"practice", "project"}:
                if st.get("scenario_id"):
                    scenario_counts[st["scenario_id"]] += 1
                else:
                    missing_top_level_scenario_ids.append(st["id"])
                lesson_dup_track[lesson["id"]]["body"][normalized_for_duplicate(st.get("body_markdown", ""))] += 1
                lesson_dup_track[lesson["id"]]["solution"][normalized_solution_code(st.get("solution_code", ""))] += 1
                lesson_dup_track[lesson["id"]]["checker"][semantic_checker_signature(st)] += 1
                normalized_solution = normalized_solution_code(st.get("solution_code", ""))
                if normalized_solution:
                    course_solution_counts[normalized_solution] += 1
                    course_solution_examples[normalized_solution].append(st["id"])
                structural_signature = structural_solution_signature(st.get("solution_code", ""))
                if structural_signature:
                    structural_solution_counts[structural_signature] += 1
                    if lesson_mode(lesson["title"], lesson.get("roadmap_topics", [])) == "ai" and st["type"] == "practice":
                        ai_structural_solution_lessons[structural_signature].add(lesson["id"])
                        ai_structural_solution_counts[structural_signature] += 1
                        aggressive_signature = aggressive_solution_signature(st.get("solution_code", ""))
                        if aggressive_signature:
                            ai_aggressive_solution_counts[aggressive_signature] += 1
                        ai_violation = ai_quality_violation(st, lesson)
                        if ai_violation:
                            ai_quality_violations.append(f"{st['id']}: {ai_violation}")
                if banned_algorithm_family_hit(st):
                    banned_algorithm_family_hits.append(st["id"])
                oop_violation = oop_requirement_violation(st, lesson)
                if oop_violation:
                    oop_key_skill_mismatch.append(f"{st['id']}: {oop_violation}")
                missing = [field for field in REQUIRED_FOCUS_FIELDS if not str(st.get(field, "")).strip()]
                if missing:
                    missing_focus_fields.append(st["id"])
                placeholder_terms = ["validation-specific result", "task input described in body", "edge case for", "placeholder", "заглуш"]
                if any(any(term in str(st.get(field, "")).lower() for term in placeholder_terms) for field in REQUIRED_FOCUS_FIELDS):
                    placeholder_focus_fields.append(st["id"])
                pattern = algorithmic_pattern(st, lesson)
                if pattern:
                    algorithmic_pattern_counts[pattern] += 1
                family = str(st.get("algorithm_family", "")).strip()
                if family:
                    algorithm_family_counts[family] += 1
                if early_future_knowledge_violation(st, lesson):
                    future_knowledge_violations.append(st["id"])
            body_low = st.get("body_markdown", "").lower()
            for service_term in SERVICE_BODY_LEAKS:
                if service_term.lower() in body_low:
                    body_service_sections.append(st["id"])
                    break
            artifact_blob = st.get("solution_code", "") + "\n" + json.dumps(st.get("checker", {}), ensure_ascii=False)
            if any(marker in artifact_blob for marker in ["SCENARIO_MARKER", "SCENARIO_PURPOSE", "contract_requirements_", "sql_scenario_marker"]):
                artificial_uniqueness_markers.append(st["id"])
            if c.get("type") == "python_pytest" and c.get("test_code"):
                normalized_test = normalized_test_code(c["test_code"])
                lesson_test_codes[normalized_test] += 1
                course_test_code_counts[normalized_test] += 1
            if st["type"] == "practice" and c.get("type") == "sql_query":
                sql_violation = sql_progression_violation(st, lesson)
                if sql_violation:
                    sql_progression_violations.append(f"{st['id']}: {sql_violation}")
                normalized_sql = normalized_sql_query(st.get("solution_code", ""))
                sql_practice_counts[normalized_sql] += 1
                sql_practice_examples[normalized_sql].append(st["id"])
                sql_dataset_counts[sql_dataset_signature(st)] += 1
            if c.get("type") == "http_api":
                if http_body_mismatch(st):
                    http_body_checker_mismatches.append(st["id"])
                if has_artificial_fastapi_route(st):
                    fastapi_artificial_routes.append(st["id"])
                if fastapi_title_method_mismatch(st):
                    fastapi_title_method_mismatches.append(st["id"])
                if fastapi_solution_method_mismatch(st):
                    fastapi_solution_method_mismatches.append(st["id"])
                public = c.get("public_tests", [{}])[0]
                api_focus = c.get("api_focus", {})
                lesson_fastapi_contracts[json.dumps({
                    "method": public.get("method"),
                    "path": display_route(str(public.get("path", ""))),
                    "json_keys": sorted((public.get("json") or {}).keys()),
                    "business_rule": api_focus.get("business_rule"),
                }, ensure_ascii=False, sort_keys=True)] += 1
                lesson_fastapi_method_path_status[json.dumps({"method": public.get("method"), "path": display_route(str(public.get("path", ""))), "status": public.get("expected_status")}, ensure_ascii=False, sort_keys=True)] += 1
                signature = http_contract_signature(st)
                http_contract_counts[signature] += 1
                http_contract_examples[signature].add(lesson["title"])
                fastapi_route_model_counts[fastapi_route_model_signature(st)] += 1
            if (
                st["type"] == "practice"
                and c.get("type") == "python_pytest"
                and lesson_mode(lesson["title"], lesson.get("roadmap_topics", [])) in {"python", "complex_python"}
                and not python_practice_uses_key_skill(st, lesson)
            ):
                python_key_skill_mismatch.append(st["id"])
            if st["type"] == "test":
                lesson_terms = [lesson["title"].lower()] + [t.lower() for t in lesson.get("roadmap_topics", [])]
                technical_terms = ["python", "print", "input", "return", "pytest", "sql", "join", "where", "having", "rollback", "commit", "индекс", "git", "branch", "commit", "rebase", "merge", "docker", "compose", "healthcheck", "fastapi", "api", "http", "422", "jwt", "ai", "rag", "json", "mock", "provider", "vector", "chunk", "stdout", "переменн", "devops", "runtime", "final", "gate", "проект", "terminal", "терминал", "ci", "cd", "deploy"]
                for q in st.get("questions", []):
                    qtext = q.get("question", "").lower()
                    q_signature = qtext
                    q_signature = q_signature.replace(lesson["title"].lower(), "lesson")
                    for topic in lesson.get("roadmap_topics", []):
                        q_signature = q_signature.replace(topic.lower(), "topic")
                    q_signature = re.sub(r"`[^`]+`", "`x`", q_signature)
                    q_signature = re.sub(r"\d+", "N", q_signature)
                    q_signature = re.sub(r"\s+", " ", q_signature).strip()
                    if q_signature:
                        template_question_signature_counts[q_signature] += 1
                    if not any(term and term in qtext for term in lesson_terms) and not any(term in qtext for term in technical_terms):
                        generic_test_questions.append(q.get("id", st["id"]))
                    if any(pattern in qtext for pattern in ["где искать ошибку", "что важнее всего проверить", "что доказывает контрольный шаг", "какой подход безопаснее", "публичного примера совпал"]):
                        template_questions.append(q.get("id", st["id"]))
            if st.get("lesson_stage") == "debug" and st["type"] in {"practice", "project"}:
                blob = (st.get("body_markdown", "") + "\n" + st.get("solution_code", "")).lower()
                if not any(token in blob for token in ["ошиб", "debug", "исправ", "конфликт", "wrong", "bad", "failed", "timeout"]):
                    bad_stage_content.append(st["id"])
            if st["type"] == "theory" and target_step_count(lesson["title"], lesson.get("roadmap_topics", [])) >= 16 and len(st.get("body_markdown", "")) < 900:
                short_complex_theory.append(st["id"])
            if st["type"] == "project":
                sol = st.get("solution_code", "").lower()
                if not all(token in sol for token in ["reference structure", "commands", "expected result"]):
                    weak_project_solutions.append(st["id"])
        if any(count > 1 for code, count in lesson_test_codes.items() if code):
            lesson_test_code_dups.append(lesson["id"])
        if any(count > 1 for code, count in lesson_fastapi_contracts.items() if code):
            fastapi_lesson_business_duplicates.append(lesson["id"])
        if any(count > 1 for code, count in lesson_fastapi_method_path_status.items() if code):
            fastapi_method_path_status_duplicates.append(lesson["id"])
        if target_step_count(lesson["title"], lesson.get("roadmap_topics", [])) >= 16 and len(lesson["steps"]) < target_step_count(lesson["title"], lesson.get("roadmap_topics", [])):
            complex_short_lessons.append(lesson["title"])
        if set(lesson.get("roadmap_topics", [])) & AI_TOPICS:
            for st in lesson["steps"]:
                if st["type"] == "practice" and st["title"] in {"Скидка", "Группировка", "Граница", "Теги"}:
                    ai_non_ai_practices.append(st["id"])
    duplicate_question_over_limit = [q for q, n in question_counts.items() if q and n > 3]
    duplicate_scenario_ids = [sid for sid, n in scenario_counts.items() if sid and n > 1]
    duplicate_course_solutions = [code for code, n in course_solution_counts.items() if code and n > 1]
    structural_solution_repeats = [code for code, n in structural_solution_counts.items() if code and n > 20]
    ai_structural_solution_duplicates = [code for code, n in ai_structural_solution_counts.items() if code and n > 1]
    ai_aggressive_solution_duplicates = [code for code, n in ai_aggressive_solution_counts.items() if code and n > 1]
    duplicate_course_test_codes = [code for code, n in course_test_code_counts.items() if code and n > 1]
    duplicate_sql_practice_queries = [code for code, n in sql_practice_counts.items() if code and n > 1]
    duplicate_sql_datasets = [code for code, n in sql_dataset_counts.items() if code and n > 1]
    template_question_signature_repeats = [sig for sig, n in template_question_signature_counts.items() if sig and n > 3]
    fastapi_endpoint_template_reuse = [
        signature
        for signature, n in http_contract_counts.items()
        if n > 1 and len(http_contract_examples[signature]) > 1
    ]
    fastapi_route_model_reuse = [signature for signature, n in fastapi_route_model_counts.items() if n > 1]
    algorithmic_pattern_over_limit = [pattern for pattern, n in algorithmic_pattern_counts.items() if n > 3]
    mass_algorithm_family_repeats = [family for family, n in algorithm_family_counts.items() if n > 20]
    for lesson_id, data in lesson_dup_track.items():
        if any(v > 1 for v in data["body"].values()):
            lesson_duplicate_body.append(lesson_id)
        if any(v > 1 for v in data["solution"].values()):
            lesson_duplicate_solution.append(lesson_id)
        if any(v > 1 for v in data["checker"].values()):
            lesson_duplicate_checker.append(lesson_id)
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
        "lesson_stage_gaps": len(lesson_stage_gaps),
        "lessons_without_project": len(lessons_without_project),
        "short_test_steps": len(short_test_steps),
        "complex_short_lessons": len(complex_short_lessons),
        "ai_non_ai_practices": len(ai_non_ai_practices),
        "duplicate_question_over_limit": len(duplicate_question_over_limit),
        "duplicate_scenario_ids": len(duplicate_scenario_ids),
        "lesson_duplicate_normalized_body": len(lesson_duplicate_body),
        "lesson_duplicate_normalized_solution": len(lesson_duplicate_solution),
        "lesson_duplicate_checker_signature": len(lesson_duplicate_checker),
        "generic_test_questions": len(generic_test_questions),
        "bad_stage_content": len(bad_stage_content),
        "short_complex_theory": len(short_complex_theory),
        "weak_project_solutions": len(weak_project_solutions),
        "course_duplicate_normalized_solution": len(duplicate_course_solutions),
        "structural_solution_repeats_over_limit": len(structural_solution_repeats),
        "ai_structural_solution_duplicates": len(ai_structural_solution_duplicates),
        "ai_quality_violations": len(ai_quality_violations),
        "sql_progression_violations": len(sql_progression_violations),
        "fastapi_title_method_mismatches": len(fastapi_title_method_mismatches),
        "fastapi_solution_method_mismatches": len(fastapi_solution_method_mismatches),
        "fastapi_lesson_business_duplicates": len(fastapi_lesson_business_duplicates),
        "fastapi_method_path_status_duplicates": len(fastapi_method_path_status_duplicates),
        "encoding_corruption": len(encoding_corruption_items),
        "package_file_corruption": len(package_file_corruption_items),
        "ai_aggressive_solution_duplicates": len(ai_aggressive_solution_duplicates),
        "course_duplicate_normalized_test_code": len(duplicate_course_test_codes),
        "lesson_duplicate_normalized_test_code": len(lesson_test_code_dups),
        "duplicate_sql_practice_query": len(duplicate_sql_practice_queries),
        "duplicate_sql_checker_dataset": len(duplicate_sql_datasets),
        "fastapi_endpoint_template_reuse": len(fastapi_endpoint_template_reuse),
        "fastapi_route_model_signature_reuse": len(fastapi_route_model_reuse),
        "python_key_skill_mismatch": len(python_key_skill_mismatch),
        "oop_key_skill_mismatch": len(oop_key_skill_mismatch),
        "banned_algorithm_family_hits": len(banned_algorithm_family_hits),
        "algorithmic_pattern_over_limit": len(algorithmic_pattern_over_limit),
        "mass_algorithm_family_repeats": len(mass_algorithm_family_repeats),
        "missing_step_focus_fields": len(missing_focus_fields),
        "missing_top_level_scenario_ids": len(missing_top_level_scenario_ids),
        "placeholder_focus_fields": len(placeholder_focus_fields),
        "body_service_sections": len(body_service_sections),
        "http_body_checker_mismatch": len(http_body_checker_mismatches),
        "fastapi_artificial_routes": len(fastapi_artificial_routes),
        "future_knowledge_violations": len(future_knowledge_violations),
        "artificial_uniqueness_markers": len(artificial_uniqueness_markers),
        "template_test_questions": len(template_questions),
        "template_question_signature_repeats": len(template_question_signature_repeats),
    }


def write_docs(course: dict[str, Any]) -> None:
    preview = [f"# {TITLE}: v16_LESSON_LADDER", "", "Этот preview нужен для методиста. Импортировать нужно только `course_import.json`.", "", "v16 пересобран под учебную лестницу: зачем, объяснение с нуля, 3+ вопроса, практика, debugging, integration/project и итог проверяются валидатором.", ""]
    cmap = ["# Карта курса v16_LESSON_LADDER", ""]
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
    (ROOT / "import_instructions.md").write_text("# Инструкция импорта v16_LESSON_LADDER\n\n1. Запусти `python validate_course.py`.\n2. Импортируй только `course_import.json`.\n3. Markdown-preview не является источником для платформы.\n4. После импорта сравни уроки и шаги с `manifest.csv`.\n5. Если импортёр сортирует не по `order`, исправь импортёр до запуска потока.\n6. Скрытые поля `solution_code`, `checker`, `ai_review_config`, `admin_notes` не показываются студенту.\n", encoding="utf-8")
    ide_spec = """# IDE plugin spec v16

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
    (ROOT / "ide_plugin_checks.json").write_text(json.dumps({"version": "v16", "quality_rules": {"unique_scenario_id_required": True, "max_signature_repeat": 20, "project_solution_required": True, "runtime_checks_required_for_devops": True, "gate_checks_required_for_final": True}, "checks": ["files", "git", "pytest", "sql", "fastapi", "docker", "ci_cd", "final_gates", "rollback", "healthcheck", "env_example"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "mentor_handbook.md").write_text("# Handbook для наставника v16\n\n## Принцип ответа\nСначала выясни наблюдаемый результат: условие, код, команда запуска, вход, stdout, stderr, статус HTTP, SQL result set или состояние git. Не выдавай готовое решение, если можно довести студента вопросами до локализации ошибки.\n\n## Как пользоваться учебной лестницей v16\nКаждый урок теперь проверяется как последовательность стадий: why, example, understanding, practice, debug, edge, integration, mini_project, summary. Если студент застрял, сначала найди стадию, на которой он сломался. Не перескакивай к проекту, если он не может объяснить минимальный пример или пройти debugging-step.\n\n## Когда давать подсказку\n1. После первой неудачной попытки укажи область: ввод, преобразование, формат вывода, SQL-порядок, status code, git-state.\n2. После второй попытки дай короткий фрагмент правила, но не полный код.\n3. После третьей попытки можно показать минимальный пример на другой задаче.\n4. Полное решение показывай только после pass/fail политики платформы или при разборе после дедлайна.\n\n## Типовые ошибки по модулю 1\n- stdout содержит лишнее слово или пробел;\n- `input()` не преобразован через `int`/`float`;\n- переменная используется до создания;\n- Git-лаба сдаётся с грязным рабочим деревом.\n\n## Типовые ошибки по модулю 2\n- функция печатает результат вместо return;\n- pytest-тест зависит от порядка запуска;\n- mock скрывает настоящую ошибку контракта;\n- async-код создаёт coroutine, но не await.\n\n## Типовые ошибки по модулю 3\n- LEFT JOIN превращён в INNER JOIN из-за фильтра в WHERE;\n- SQL без ORDER BY даёт нестабильный результат;\n- транзакция не делает rollback при ошибке;\n- sqlite3-код забывает commit или использует строковую склейку вместо параметров.\n\n## Типовые ошибки по модулю 4\n- FastAPI возвращает 200 вместо 201/204/404/422;\n- healthcheck возвращает массив вместо объекта;\n- Dockerfile копирует лишние файлы или CMD не стартует приложение;\n- CI объединяет lint/test/build/deploy в один непрозрачный job.\n\n## Типовые ошибки по модулю 5\n- AI provider вызывается напрямую без timeout/retry/mock;\n- RAG отвечает без ссылок на найденные chunks;\n- deploy script не имеет dry-run и rollback;\n- финальный проект не содержит acceptance criteria и negative tests.\n\n## Как проверять финальный проект\nПроверь gates отдельно: ТЗ, user stories, ERD, миграции, API contract, auth, CRUD, tests, Docker, CI/CD, AI integration, logging, README, deploy, defense. Для каждого gate должен быть артефакт, команда проверки, pass/fail критерий и понятный риск.\n\n## Жалобы на hidden tests\nНе отвечай фразой «у тебя ошибка». Попроси публичный пример, локальный запуск, версию файла, команду и минимальный reproduction. Эскалируй, если публичный тест противоречит hidden-проверке или hidden требует того, чего нет в условии.\n\n## Маршруты восстановления\n- Отстаёт Python Core: верни на последние 5 stdout/pytest-задач и проверь базовый ввод/return.\n- Отстаёт SQL: дай 10 запросов на SELECT/WHERE/JOIN/GROUP BY с обязательным объяснением каждой строки.\n- Отстаёт Git: запрети force-команды, создай recovery branch, повтори restore/reset/revert/reflog на песочнице.\n- Отстаёт FastAPI: начать с `/health`, затем один POST, затем один negative 422.\n- Отстаёт DevOps: сначала локальный запуск без Docker, потом Dockerfile, потом compose, потом CI.\n\n## Эскалация\nЭскалируй методисту или инженеру платформы, если корректное решение падает на инфраструктуре, IDE-плагин не видит существующий файл, hidden tests проверяют неописанное поведение или массово повторяется одна и та же ошибка формулировки.\n", encoding="utf-8")
    student_faq = """# FAQ студента v16

## Как проходить курс

### Q01. Как идти по уроку?
Иди по учебной лестнице: зачем тема нужна, минимальный пример, вопросы, базовая практика, debugging, edge case, integration, mini-project и итог. Не перескакивай к проекту, если не можешь объяснить пример.

### Q02. Почему нельзя начинать с AI?
Сначала ты должен уметь запускать Python-код, читать ошибку и проверять результат. AI станет помощником, а не заменой базовых навыков.

### Q03. Что делать, если публичный пример проходит, а hidden test падает?
Проверь edge cases: пустой ввод, лишний stdout, порядок строк, типы, граничные числа, 404/422/401, SQL без ORDER BY, грязное git-дерево или отсутствующий env.

### Q04. Когда писать наставнику?
Пиши, если ты сделал локальный запуск, приложил код, команду, входные данные, stdout/stderr и не понимаешь причину. Без этих данных наставник не сможет быстро помочь.

## Python и stdout

### Q05. Почему нельзя писать лишний вывод?
stdout-задачи сравнивают точный текст. Одно лишнее слово, пробел или пустая строка ломают проверку.

### Q06. Почему `input()` даёт строку, хотя я ввёл число?
`input()` всегда возвращает `str`. Для арифметики явно используй `int()` или `float()`.

### Q07. Почему `return` нужен вместо `print()`?
`return` отдаёт значение вызывающему коду и тестам. `print()` только выводит текст в консоль.

### Q08. Что делать с пустым вводом?
Сначала проверь условие. Если пустой ввод допустим, обработай его отдельно: не вызывай `int("")`.

### Q09. Почему список изменился после вызова функции?
Список изменяемый. Если функция не должна менять исходные данные, сделай копию.

### Q10. Почему hidden test ловит регистр?
Если условие требует точный текст, `Yes`, `yes` и `YES` считаются разными строками.

### Q11. Как читать traceback?
Иди снизу вверх: нижняя строка показывает тип ошибки, строки выше показывают место, где она возникла.

### Q12. Почему `TypeError` появился только на hidden test?
Публичный пример мог не покрывать смешанные типы. Проверь, что функция не складывает строку и число и не сравнивает несовместимые значения.

### Q13. Как чинить задачу на чтение чужого кода?
Сначала запусти код на маленьком примере, затем подпиши значения переменных после каждой строки.

### Q14. Когда нужен рефакторинг?
Когда код проходит тесты, но содержит повторение, длинные условия или смешивает ввод, расчёт и вывод.

## pytest

### Q15. Почему pytest не видит мой тест?
Файл должен называться `test_*.py` или `*_test.py`, а функция должна начинаться с `test_`.

### Q16. Почему тест падает на импорте?
Проверь имя файла, имя функции и отсутствие кода, который запускается сразу при импорте без `if __name__ == "__main__"`.

### Q17. Как понять, что именно сравнивает assert?
Прочитай левую и правую часть assert. Pytest обычно показывает actual и expected рядом.

### Q18. Почему тест на время или случайность нестабилен?
Код зависит от текущего времени, random или внешнего состояния. Используй фиксированные данные, seed или mock.

### Q19. Когда писать тест до кода?
Когда понятен контракт функции: вход, выход, ошибки и граничные случаи.

### Q20. Почему fixture полезнее копипасты setup-кода?
Fixture делает подготовку данных единым местом и уменьшает риск, что тесты расходятся в деталях.

## SQL и SQLite

### Q21. Почему SQL требует ORDER BY?
Без сортировки база не обязана возвращать строки в одном порядке. Hidden test может сравнивать ordered rows.

### Q22. Почему LEFT JOIN потерял строки?
Частая ошибка: фильтр по правой таблице в `WHERE` превращает LEFT JOIN в INNER JOIN. Перенеси условие в `ON` или учитывай `IS NULL`.

### Q23. Когда нужен HAVING?
`WHERE` фильтрует строки до группировки. `HAVING` фильтрует группы после `GROUP BY`.

### Q24. Почему `COUNT(column)` отличается от `COUNT(*)`?
`COUNT(column)` не считает NULL. `COUNT(*)` считает все строки группы.

### Q25. Почему `= NULL` не работает?
NULL означает неизвестное значение. Используй `IS NULL` или `IS NOT NULL`.

### Q26. Что проверяет rollback?
Rollback отменяет изменения текущей транзакции. После rollback данные должны вернуться к состоянию до изменения.

### Q27. Почему SQLite не проверяет FOREIGN KEY?
В SQLite нужно включить `PRAGMA foreign_keys = ON` для каждого соединения.

### Q28. Почему параметризованный запрос безопаснее f-string?
Параметры передаются отдельно от SQL-кода. Это защищает от SQL injection и ошибок кавычек.

### Q29. Зачем нужен EXPLAIN?
EXPLAIN показывает план выполнения запроса: скан таблицы, использование индекса, порядок операций.

### Q30. Почему индекс не ускорил запрос?
Индекс может не использоваться, если условие не подходит, таблица маленькая или запрос применяет функцию к индексируемому полю.

### Q31. Как проверить схему SQLite?
Используй `PRAGMA table_info(table_name)` и `SELECT name FROM sqlite_master WHERE type='table'`.

### Q32. Почему импорт CSV сломался?
Проверь разделитель, кодировку, заголовок, пустые поля и соответствие типов колонок.

## Git и терминал

### Q33. Почему Git-задача требует чистое дерево?
Чистое дерево доказывает, что все нужные изменения добавлены в commit, а случайные файлы не остались рядом.

### Q34. Что делать при merge conflict?
Открой файл, убери маркеры `<<<<<<<`, `=======`, `>>>>>>>`, оставь правильный текст, затем сделай `git add` и commit.

### Q35. Чем `restore`, `reset` и `revert` отличаются?
`restore` меняет файлы, `reset` двигает указатель ветки или индекс, `revert` создаёт новый commit, который отменяет старый.

### Q36. Почему force push опасен?
Он может перезаписать чужие commits. Если команда разрешена, используй `--force-with-lease`, потому что он проверяет, что remote не изменился неожиданно.

### Q37. Когда нужен stash?
Когда нужно временно убрать незавершённые изменения, переключиться на другую задачу, а потом вернуть работу.

### Q38. Как восстановиться через reflog?
Найди нужное состояние в `git reflog`, создай recovery branch или сделай reset на найденный commit в учебной песочнице.

### Q39. Почему push получил non-fast-forward?
Remote содержит commits, которых нет локально. Сначала сделай `git fetch`, посмотри историю, затем `pull --rebase` или merge по условию.

### Q40. Почему терминальная команда не работает в Windows?
Проверь shell. В PowerShell, bash и cmd различаются кавычки, переменные окружения и некоторые команды.

## FastAPI и HTTP

### Q41. Почему FastAPI возвращает 422?
422 означает, что JSON, query или path parameters не прошли валидацию Pydantic.

### Q42. Когда нужен `response_model`?
Когда нужно зафиксировать форму ответа, скрыть лишние поля и получить корректную OpenAPI-схему.

### Q43. Почему healthcheck должен возвращать объект?
Объект `{ "status": "ok" }` расширяем: туда можно добавить version, db, uptime. Массив для healthcheck обычно не несёт контракта.

### Q44. Когда возвращать 201?
201 возвращают после создания ресурса, например `POST /tasks`, если задача реально создана.

### Q45. Когда возвращать 204?
204 подходит для успешного удаления или обновления без тела ответа.

### Q46. Почему endpoint должен возвращать 404?
Если ресурс по id не найден, нельзя возвращать пустой объект с 200: клиент не отличит ошибку от валидного результата.

### Q47. Почему auth-тест ждёт 401?
401 означает, что запрос не авторизован. Protected route без токена должен отказать.

### Q48. Как диагностировать сломанный TestClient?
Проверь import path `app.main:app`, наличие route, status code, тело ответа и validation errors.

## Docker, CI/CD и deploy

### Q49. Почему контейнер не стартует?
Смотри `docker compose logs`. Частые причины: неверный CMD, отсутствующий файл, неправильный порт, нет env, приложение падает на импорте.

### Q50. Что проверяет healthcheck?
Healthcheck проверяет, что процесс не просто запустился, а отвечает на ожидаемый запрос или команду.

### Q51. Почему `.env.example` нужен без настоящих секретов?
Он показывает список переменных для запуска, но не раскрывает реальные ключи и пароли.

### Q52. Почему тесты нужно запускать внутри контейнера?
Так проверяется та же среда, в которой приложение будет работать на сервере.

### Q53. Зачем разделять CI jobs?
Отдельные `lint`, `test`, `build`, `deploy` показывают, где именно сломался pipeline.

### Q54. Что должен делать deploy dry-run?
Показать план действий без изменения сервера: какие файлы, команды, сервисы и проверки будут затронуты.

### Q55. Почему rollback обязателен?
Без rollback команда может застрять на нерабочем релизе. Rollback возвращает предыдущую рабочую версию.

### Q56. Почему SSL и домен проверяются отдельно?
Приложение может работать по IP, но падать через домен из-за DNS, Nginx или сертификата.

## AI, RAG и безопасность

### Q57. Почему в задачах используется mock provider?
Mock делает проверку воспроизводимой и не требует платных API. Реальный provider подключается после проверки контракта.

### Q58. Что делать с неверным JSON от AI?
Не доверяй ответу напрямую. Валидируй JSON schema, логируй ошибку, делай retry или возвращай контролируемую ошибку.

### Q59. Как ограничить hallucination в RAG?
Передавай найденные chunks, требуй ссылки на источники и запрещай отвечать, если данных недостаточно.

### Q60. Почему нельзя вставлять секреты в код?
Код попадает в Git, CI и логи. Секреты должны жить в env или secret storage.

### Q61. Что делать при timeout AI-запроса?
Поставь явный timeout, retry с лимитом, логирование и fallback-ответ без бесконечного ожидания.

### Q62. Почему нужно считать стоимость AI-вызовов?
На большом потоке лишние токены быстро превращаются в деньги. Логируй модель, токены и тип запроса.

## Финальный проект

### Q63. Что сдавать в gate ТЗ?
User stories, ограничения, acceptance criteria, out-of-scope и критерии pass/fail.

### Q64. Что сдавать в DB schema gate?
ERD, таблицы, связи, индексы, миграции, rollback-план и объяснение выбора.

### Q65. Что сдавать в API contract gate?
OpenAPI, endpoints, статусы, ошибки, request/response примеры и negative cases.

### Q66. Почему README проверяется?
README показывает, может ли другой разработчик запустить проект, тесты и deploy без устного объяснения.

### Q67. Что спрашивают на final defense?
Почему выбрана схема БД, как работает auth, где тесты ловят ошибки, как устроен deploy, какие риски остались.

### Q68. Что делать, если IDE-плагин не видит файл?
Проверь рабочую директорию, имя файла, регистр букв, путь из задания и сохранён ли файл на диске.
"""
    (ROOT / "student_faq.md").write_text(student_faq, encoding="utf-8")
    (ROOT / "middle_readiness_rubric.md").write_text("# Рубрика готовности\n\n| Уровень | Python | SQL | API | Тесты | Git | DevOps | Архитектура | Финальный проект |\n|---|---|---|---|---|---|---|---|---|\n| Junior | функции, коллекции, ошибки | SELECT/JOIN | простые routes | базовый pytest | commit/branch | Dockerfile | слои видит | CRUD работает |\n| Junior+ | ООП, typing, async | CTE, transactions | auth, Depends | fixtures/mocks | rebase/conflicts | compose/CI | repository/service | тесты и README |\n| Middle-ready | проектирует boundaries | индексы/изоляция | SQLAlchemy/Alembic | integration suite | workflow ведёт | deploy/rollback | trade-offs объясняет | защита проходит |\n| Начинающий Middle | улучшает чужой код | оптимизирует запросы | владеет модулем | строит стратегию качества | держит историю чистой | снижает prod-risk | документирует решения | ведёт релиз |\n", encoding="utf-8")
    (ROOT / "release_checklist.md").write_text("# Release checklist v16\n\n## Автоматическая проверка\n- [ ] `python validate_course.py` возвращает PASS.\n- [ ] `duplicate_body_count = 0`.\n- [ ] `duplicate_learning_objectives = 0`.\n- [ ] `duplicate_question_over_limit = 0`.\n- [ ] `duplicate_scenario_ids = 0`.\n- [ ] `lesson_duplicate_normalized_body = 0`.\n- [ ] `lesson_duplicate_normalized_solution = 0`.\n- [ ] `lesson_duplicate_checker_signature = 0`.\n- [ ] `course_duplicate_normalized_solution = 0`.\n- [ ] `lesson_duplicate_normalized_test_code = 0`.\n- [ ] `course_duplicate_normalized_test_code = 0`.\n- [ ] `duplicate_sql_practice_query = 0`.\n- [ ] `duplicate_sql_checker_dataset = 0`.\n- [ ] `fastapi_endpoint_template_reuse = 0`.\n- [ ] `fastapi_route_model_signature_reuse = 0`.\n- [ ] `python_key_skill_mismatch = 0`.\n- [ ] `algorithmic_pattern_over_limit = 0`.\n- [ ] `missing_step_focus_fields = 0`.\n- [ ] `template_test_questions = 0`.\n- [ ] `body_service_sections = 0`.\n- [ ] `ai_structural_solution_duplicates = 0`.\n- [ ] `ai_quality_violations = 0`.\n- [ ] `sql_progression_violations = 0`.\n- [ ] `fastapi_lesson_business_duplicates = 0`.\n- [ ] `fastapi_title_method_mismatches = 0`.\n- [ ] `fastapi_solution_method_mismatches = 0`.\n- [ ] `http_body_checker_mismatch = 0`.\n- [ ] `artificial_uniqueness_markers = 0`.\n- [ ] `placeholder_focus_fields = 0`.\n- [ ] `template_question_signature_repeats = 0`.\n- [ ] `generic_test_questions = 0`.\n- [ ] `bad_stage_content = 0`.\n- [ ] `short_complex_theory = 0`.\n- [ ] `weak_project_solutions = 0`.\n- [ ] Empty solution_code у practice/project = 0.\n- [ ] Первый урок — `Первый код`.\n- [ ] Manifest совпадает с JSON.\n- [ ] Coverage matrix не содержит missing/thin/placeholder.\n- [ ] SQL transactions содержит BEGIN/COMMIT/ROLLBACK/ROLLBACK TO.\n- [ ] FastAPI healthcheck возвращает объект.\n- [ ] Docker/final tasks имеют runtime checks, dry-run и rollback.\n- [ ] lesson ladder stage gaps = 0: каждый урок содержит why, example, understanding, practice, debug, edge, integration, mini_project, summary.\n- [ ] Каждый test-step содержит минимум 3 structured questions.\n- [ ] AI/RAG уроки не содержат обычные Python-задачи под видом AI-интеграции.\n- [ ] Сложные уроки Git/SQL/FastAPI/DevOps/AI/final имеют усиленную длину и debugging/integration шаги.\n\n## Почему добавлены gates текущей версии\nЭти проверки нужны, чтобы ревьюер видел: курс не проходит за счёт разных формулировок одного и того же решения. Сейчас валидатор отдельно проверяет уникальность solution-кода, pytest-кода, SQL-запросов, SQL dataset, FastAPI route/model/checker signatures, algorithmic patterns и явные поля `skill_focus`, `new_constraint`, `edge_case`, `input_shape`, `output_contract`. Current hard gates also check student-facing body leaks, FastAPI route/method alignment with http_api checker, absence of marker/comment uniqueness hacks, non-placeholder focus fields, repeated quiz templates after lesson-title removal, and stricter normalized solution uniqueness. This is necessary so a reviewer sees that the package is not passing because of wording noise, ids or generated markers.\n\n## QA-регламент после импорта\n- [ ] Импортировать пакет на staging.\n- [ ] Сравнить количество уроков и шагов с `manifest.csv`.\n- [ ] Ручно пройти первые 10 уроков как студент.\n- [ ] Выборочно проверить 50-100 шагов: Python, Git, SQL, SQLite, FastAPI, Docker, final gates.\n- [ ] Запустить IDE-плагин на реальном проекте для Git, Docker, FastAPI и final gate.\n- [ ] Пройти один полный финальный проект от ТЗ до защиты.\n- [ ] Проверить hidden tests на пустые значения, неверные типы, 401/404/422, SQL injection, отсутствие ORDER BY, грязное git-дерево и отсутствие env/healthcheck.\n- [ ] Провести dry-run наставников: 10 типовых вопросов, 5 жалоб на hidden tests, 3 восстановления отстающих студентов.\n", encoding="utf-8")


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
    (ROOT / "checker_fixtures/projects/final_project_hidden_checks.json").write_text(json.dumps({"version": "v16", "gates": ["tz", "user_stories", "db_schema", "api_contract", "git_workflow", "fastapi_structure", "sqlalchemy_models", "alembic_migrations", "auth", "crud", "tests", "docker", "ci_cd", "ai_integration", "logging", "readme", "deploy", "defense"], "hidden_checks": [{"name": "no_secrets", "type": "file_scan", "patterns": ["API_KEY=", "SECRET_KEY=", "OPENAI_API_KEY="]}, {"name": "env_example", "type": "file_contains", "file": ".env.example", "must_contain": ["DATABASE_URL", "SECRET_KEY", "APP_ENV"]}, {"name": "health_endpoint_object", "type": "http_api", "method": "GET", "path": "/health", "expected_status": 200, "expected_json_subset": {"status": "ok"}}, {"name": "auth_negative_401", "type": "http_api", "method": "GET", "path": "/me", "expected_status": 401}, {"name": "task_not_found_404", "type": "http_api", "method": "GET", "path": "/tasks/999999", "expected_status": 404}, {"name": "validation_422", "type": "http_api", "method": "POST", "path": "/tasks", "json": {"title": ""}, "expected_status": 422}, {"name": "pytest", "type": "command", "cmd": "python -m pytest", "expect_exit_code": 0}, {"name": "compose_config", "type": "command", "cmd": "docker compose config", "expect_exit_code": 0}, {"name": "container_tests", "type": "command", "cmd": "docker compose exec -T app python -m pytest", "expect_exit_code": 0}, {"name": "deploy_dry_run", "type": "command", "cmd": "bash deploy/deploy.sh --dry-run", "expect_exit_code": 0}, {"name": "rollback_dry_run", "type": "command", "cmd": "bash deploy/deploy.sh --rollback --dry-run", "expect_exit_code": 0}]}, ensure_ascii=False, indent=2), encoding="utf-8")


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
            if not st.get("scenario_id"):
                errors.append(f"practice/project without top-level scenario_id: {sid}")
            lesson_objectives[sid.rsplit("_s", 1)[0]].append(st.get("learning_objective", ""))
        body = st.get("body_markdown", "")
        leaks += [f"{sid}: {x}" for x in BODY_LEAKS + SERVICE_BODY_LEAKS if x in body]
        if re.search(r"\btests\b|tests/", body, flags=re.I):
            leaks.append(f"{sid}: literal tests in body_markdown")
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
    if s.get("encoding_corruption", 0) > 0:
        errors.append(f"encoding corruption in course_import.json fields: {s['encoding_corruption']}")
    if s.get("package_file_corruption", 0) > 0:
        errors.append(f"encoding corruption in package text files: {s['package_file_corruption']}")
    if s["duplicate_body_count"] > 0:
        errors.append(f"duplicate body_markdown: {s['duplicate_body_count']} duplicates in {s['duplicate_body_groups']} groups")
    if s["max_ide_signature_repeat"] > 20:
        errors.append(f"IDE checker signatures repeat too much: max {s['max_ide_signature_repeat']}")
    if s["duplicate_learning_objectives"] > 0:
        errors.append(f"duplicate learning objectives: {s['duplicate_learning_objectives']}")
    if s["duplicate_question_over_limit"] > 0:
        errors.append(f"questions repeated more than 3 times: {s['duplicate_question_over_limit']}")
    if s["duplicate_scenario_ids"] > 0:
        errors.append(f"duplicate scenario_id values: {s['duplicate_scenario_ids']}")
    if s["lesson_duplicate_normalized_body"] > 0:
        errors.append(f"duplicate normalized practice/project body inside lessons: {s['lesson_duplicate_normalized_body']}")
    if s["lesson_duplicate_normalized_solution"] > 0:
        errors.append(f"duplicate normalized practice/project solution inside lessons: {s['lesson_duplicate_normalized_solution']}")
    if s["lesson_duplicate_checker_signature"] > 0:
        errors.append(f"duplicate semantic checker signatures inside lessons: {s['lesson_duplicate_checker_signature']}")
    if s["generic_test_questions"] > 0:
        errors.append(f"generic test questions without lesson topic terms: {s['generic_test_questions']}")
    if s["bad_stage_content"] > 0:
        errors.append(f"lesson_stage/content mismatch: {s['bad_stage_content']}")
    if s["short_complex_theory"] > 0:
        errors.append(f"complex theory steps below minimum explanation threshold: {s['short_complex_theory']}")
    if s["weak_project_solutions"] > 0:
        errors.append(f"project solution_code lacks structure/commands/expected result: {s['weak_project_solutions']}")
    if s["course_duplicate_normalized_solution"] > 0:
        errors.append(f"normalized_solution_code repeats across course: {s['course_duplicate_normalized_solution']}")
    if s["structural_solution_repeats_over_limit"] > 0:
        errors.append(f"structural solution signature repeats more than 20 times: {s['structural_solution_repeats_over_limit']}")
    if s["ai_structural_solution_duplicates"] > 0:
        errors.append(f"AI practice solution structure repeats across AI tasks: {s['ai_structural_solution_duplicates']}")
    if s["ai_quality_violations"] > 0:
        errors.append(f"AI task quality violations: {s['ai_quality_violations']}")
    if s.get("ai_aggressive_solution_duplicates", 0) > 0:
        errors.append(f"AI aggressive solution structures repeat: {s['ai_aggressive_solution_duplicates']}")
    if s["sql_progression_violations"] > 0:
        errors.append(f"SQL progression violations: {s['sql_progression_violations']}")
    if s["fastapi_title_method_mismatches"] > 0:
        errors.append(f"FastAPI title/checker method mismatches: {s['fastapi_title_method_mismatches']}")
    if s["fastapi_solution_method_mismatches"] > 0:
        errors.append(f"FastAPI solution/checker method mismatches: {s['fastapi_solution_method_mismatches']}")
    if s["fastapi_lesson_business_duplicates"] > 0:
        errors.append(f"FastAPI duplicate business contracts inside lessons: {s['fastapi_lesson_business_duplicates']}")
    if s.get("fastapi_method_path_status_duplicates", 0) > 0:
        errors.append(f"FastAPI duplicate method/path/status inside lessons: {s['fastapi_method_path_status_duplicates']}")
    if s["lesson_duplicate_normalized_test_code"] > 0:
        errors.append(f"normalized_test_code repeats inside lessons: {s['lesson_duplicate_normalized_test_code']}")
    if s["course_duplicate_normalized_test_code"] > 0:
        errors.append(f"normalized_test_code repeats across course: {s['course_duplicate_normalized_test_code']}")
    if s["duplicate_sql_practice_query"] > 0:
        errors.append(f"identical SQL query reused in practice steps: {s['duplicate_sql_practice_query']}")
    if s["duplicate_sql_checker_dataset"] > 0:
        errors.append(f"identical SQL schema_sql + seed_sql + expected_rows reused: {s['duplicate_sql_checker_dataset']}")
    if s["fastapi_endpoint_template_reuse"] > 0:
        errors.append(f"FastAPI endpoint template reused across different lessons: {s['fastapi_endpoint_template_reuse']}")
    if s["fastapi_route_model_signature_reuse"] > 0:
        errors.append(f"FastAPI route/model/checker signature reused: {s['fastapi_route_model_signature_reuse']}")
    if s["python_key_skill_mismatch"] > 0:
        errors.append(f"Python practice does not use key lesson skill: {s['python_key_skill_mismatch']}")
    if s["oop_key_skill_mismatch"] > 0:
        errors.append(f"OOP practice does not use required OOP construct: {s['oop_key_skill_mismatch']}")
    if s["banned_algorithm_family_hits"] > 0:
        errors.append(f"banned repeated algorithm families remain: {s['banned_algorithm_family_hits']}")
    if s["algorithmic_pattern_over_limit"] > 0:
        errors.append(f"algorithmic pattern repeats more than 3 times: {s['algorithmic_pattern_over_limit']}")
    if s["mass_algorithm_family_repeats"] > 0:
        errors.append(f"algorithm family repeats too much: {s['mass_algorithm_family_repeats']}")
    if s["missing_step_focus_fields"] > 0:
        errors.append(f"practice/project missing skill_focus/new_constraint/edge_case/input_shape/output_contract: {s['missing_step_focus_fields']}")
    if s["missing_top_level_scenario_ids"] > 0:
        errors.append(f"practice/project missing top-level scenario_id: {s['missing_top_level_scenario_ids']}")
    if s["placeholder_focus_fields"] > 0:
        errors.append(f"practice/project focus fields contain placeholders: {s['placeholder_focus_fields']}")
    if s["body_service_sections"] > 0:
        errors.append(f"body_markdown contains service sections or field names: {s['body_service_sections']}")
    if s["http_body_checker_mismatch"] > 0:
        errors.append(f"http_api body route/method mismatch with checker: {s['http_body_checker_mismatch']}")
    if s["fastapi_artificial_routes"] > 0:
        errors.append(f"FastAPI routes look artificial or outside approved backend API set: {s['fastapi_artificial_routes']}")
    if s["future_knowledge_violations"] > 0:
        errors.append(f"early Python lesson uses future knowledge: {s['future_knowledge_violations']}")
    if s["artificial_uniqueness_markers"] > 0:
        errors.append(f"artificial uniqueness markers remain in solution/checker: {s['artificial_uniqueness_markers']}")
    if s["template_test_questions"] > 0:
        errors.append(f"template-style test questions remain: {s['template_test_questions']}")
    if s["template_question_signature_repeats"] > 0:
        errors.append(f"test question templates repeat after removing lesson names: {s['template_question_signature_repeats']}")
    if s["lesson_stage_gaps"] > 0:
        errors.append(f"lesson ladder stage gaps: {s['lesson_stage_gaps']}")
    if s["lessons_without_project"] > 0:
        errors.append(f"lessons without mini-project: {s['lessons_without_project']}")
    if s["short_test_steps"] > 0:
        errors.append(f"test steps with fewer than 3 questions: {s['short_test_steps']}")
    if s["complex_short_lessons"] > 0:
        errors.append(f"complex lessons below target step count: {s['complex_short_lessons']}")
    if s["ai_non_ai_practices"] > 0:
        errors.append(f"AI lessons contain generic non-AI practice tasks: {s['ai_non_ai_practices']}")
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
        "# Validation report v16_LESSON_LADDER", "", f"final status: {result['status']}", "",
        "## Totals", f"- total modules: {s['total_modules']}", f"- total lessons: {s['total_lessons']}", f"- total steps: {s['total_steps']}", f"- total hours: {s['total_hours']}", f"- steps by type: {s['steps_by_type']}", f"- checkers by type: {s['checkers_by_type']}", f"- structured questions: {s['questions']}", "",
        "## Quality gates", f"- duplicate body_markdown: {s['duplicate_body_count']} duplicates / {s['duplicate_body_groups']} groups", f"- duplicate learning objectives: {s['duplicate_learning_objectives']}", f"- questions repeated more than 3 times: {s['duplicate_question_over_limit']}", f"- duplicate scenario_id values: {s['duplicate_scenario_ids']}", f"- missing top-level scenario_id values: {s['missing_top_level_scenario_ids']}", f"- duplicate normalized practice/project body inside lessons: {s['lesson_duplicate_normalized_body']}", f"- duplicate normalized practice/project solution inside lessons: {s['lesson_duplicate_normalized_solution']}", f"- duplicate semantic checker signatures inside lessons: {s['lesson_duplicate_checker_signature']}", f"- normalized_solution_code repeats across course: {s['course_duplicate_normalized_solution']}", f"- structural solution repeats over limit: {s['structural_solution_repeats_over_limit']}", f"- AI structural solution duplicates: {s['ai_structural_solution_duplicates']}", f"- AI quality violations: {s['ai_quality_violations']}", f"- SQL progression violations: {s['sql_progression_violations']}", f"- FastAPI title/method mismatches: {s['fastapi_title_method_mismatches']}", f"- FastAPI solution/method mismatches: {s['fastapi_solution_method_mismatches']}", f"- FastAPI duplicate business contracts inside lessons: {s['fastapi_lesson_business_duplicates']}", f"- FastAPI duplicate method/path/status inside lessons: {s.get('fastapi_method_path_status_duplicates', 0)}", f"- encoding corruption in JSON fields: {s.get('encoding_corruption', 0)}", f"- encoding corruption in package files: {s.get('package_file_corruption', 0)}", f"- AI aggressive solution duplicates: {s.get('ai_aggressive_solution_duplicates', 0)}", f"- normalized_test_code repeats across course: {s['course_duplicate_normalized_test_code']}", f"- normalized_test_code repeats inside lessons: {s['lesson_duplicate_normalized_test_code']}", f"- identical SQL query reused in practice: {s['duplicate_sql_practice_query']}", f"- identical SQL schema/seed/expected reused: {s['duplicate_sql_checker_dataset']}", f"- FastAPI endpoint template reuse: {s['fastapi_endpoint_template_reuse']}", f"- FastAPI route/model/checker signature reuse: {s['fastapi_route_model_signature_reuse']}", f"- FastAPI artificial routes: {s['fastapi_artificial_routes']}", f"- HTTP body/checker route mismatch: {s['http_body_checker_mismatch']}", f"- body service sections: {s['body_service_sections']}", f"- artificial uniqueness markers: {s['artificial_uniqueness_markers']}", f"- Python key-skill mismatch: {s['python_key_skill_mismatch']}", f"- OOP key-skill mismatch: {s['oop_key_skill_mismatch']}", f"- banned repeated algorithm families: {s['banned_algorithm_family_hits']}", f"- early Python future-knowledge violations: {s['future_knowledge_violations']}", f"- algorithmic pattern over limit: {s['algorithmic_pattern_over_limit']}", f"- mass algorithm family repeats: {s['mass_algorithm_family_repeats']}", f"- missing step focus fields: {s['missing_step_focus_fields']}", f"- placeholder focus fields: {s['placeholder_focus_fields']}", f"- template-style test questions: {s['template_test_questions']}", f"- repeated question templates after lesson removal: {s['template_question_signature_repeats']}", f"- generic test questions without lesson terms: {s['generic_test_questions']}", f"- lesson_stage/content mismatches: {s['bad_stage_content']}", f"- complex theory steps below threshold: {s['short_complex_theory']}", f"- weak project solution_code: {s['weak_project_solutions']}", f"- unique learning objectives: {s['unique_learning_objectives']}", f"- lesson ladder stage gaps: {s['lesson_stage_gaps']}", f"- lessons without mini-project: {s['lessons_without_project']}", f"- test steps with fewer than 3 questions: {s['short_test_steps']}", f"- complex lessons below target step count: {s['complex_short_lessons']}", f"- AI lessons with generic non-AI practice: {s['ai_non_ai_practices']}", f"- empty practice solutions: {len(result['empty_practice_solution'])}", f"- empty project solutions: {len(result['empty_project_solution'])}", f"- unique IDE signatures: {s['unique_ide_signatures']}", f"- max IDE signature repeat: {s['max_ide_signature_repeat']}", "",
        "## Required depth", f"- practice tasks: {s['practice_count']}", f"- project/IDE tasks: {s['project_or_ide_count']}", f"- SQL query tasks: {s['sql_tasks']}", f"- SQLite/sqlite3 steps: {s['sqlite_steps']}", f"- Git steps: {s['git_steps']}", f"- Git/terminal steps: {s['git_terminal_steps']}", f"- FastAPI steps: {s['fastapi_steps']}", f"- HTTP API tasks: {s['http_api_tasks']}", f"- pytest tasks: {s['pytest_tasks']}", f"- Docker/CI/CD/DevOps steps: {s['devops_steps']}", "",
        "## Critical checks", f"- missing checkers: {len(result['missing_checkers'])}", f"- missing quiz questions: {len(result['missing_questions'])}", f"- body leaks: {len(result['body_leaks'])}", f"- banned text: {len(result['banned_text'])}", f"- duplicate ids: {len(result['duplicate_ids'])}", f"- projects without IDE/AI review: {len(result['project_missing'])}",
    ]
    if result["errors"]:
        lines += ["", "## Errors"] + [f"- {e}" for e in result["errors"]]
    lines.append(f"\nResult: {result['status']}")
    (ROOT / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    qa = [
        "# QA report v16_LESSON_LADDER", "", f"PASS/FAIL: {result['status']}", "",
        "## Critical blockers", *([f"- {e}" for e in result["errors"]] if result["errors"] else ["- не найдено"]), "",
        "## Hard fail rules", "- первый урок должен быть `Первый код` и первый шаг `Смысл`;", "- каждый урок содержит стадии: why, example, understanding, practice, debug, edge, integration, mini_project, summary;", "- каждый test-step содержит минимум 3 structured questions;", "- один и тот же question не встречается чаще 3 раз;", "- scenario_id уникален во всем курсе;", "- внутри одного урока practice/project не дублируют normalized body, solution_code и checker signature;", "- normalized_solution_code не повторяется в course practice/project;", "- normalized_test_code не повторяется внутри урока и по курсу;", "- одинаковый SQL-запрос не используется в нескольких practice шагах;", "- SQL practice не повторяет тот же schema_sql + seed_sql + expected_rows;", "- FastAPI endpoint-template не закрывает разные темы без изменения контракта;", "- FastAPI route/model/checker signature не повторяется;", "- HTTP method/path в body_markdown совпадает с checker public/hidden routes;", "- Python practice использует ключевой навык урока, а не универсальный clamp/group/filter;", "- массовый structural solution repeat, массовый algorithm_family repeat и AI cross-lesson repeat запрещены;", "- practice/project содержит skill_focus, new_constraint, edge_case, input_shape, output_contract без заглушек;", "- generic-вопрос без термина урока запрещен;", "- шаблонные формы тестовых вопросов запрещены, включая повтор после удаления названия урока;", "- искусственные SCENARIO_MARKER/contract_requirements/sql_scenario_marker запрещены;", "- lesson_stage должен соответствовать содержанию шага;", "- theory в сложной теме не может быть короткой заметкой;", "- project solution_code содержит структуру файлов, команды и ожидаемый результат;", "- каждый урок содержит mini-project/project артефакт;", "- practice без checker запрещены;", "- project без IDE/AI проверки запрещены;", "- body_markdown не содержит служебные секции, solution/checker/admin и banned-фразы;", "- manifest и JSON совпадают построчно;", "- coverage_matrix не содержит missing/thin/placeholder;", "",
        "## Quantitative audit", f"- modules: {s['total_modules']}", f"- lessons: {s['total_lessons']}", f"- steps: {s['total_steps']}", f"- hours: {s['total_hours']}", f"- practice tasks: {s['practice_count']}", f"- project/IDE tasks: {s['project_or_ide_count']}", f"- structured questions: {s['questions']}", f"- SQL query tasks: {s['sql_tasks']}", f"- SQLite/sqlite3 steps: {s['sqlite_steps']}", f"- Git steps: {s['git_steps']}", f"- FastAPI steps: {s['fastapi_steps']}", f"- Docker/CI/CD/DevOps steps: {s['devops_steps']}", "",
        "## Duplicate and semantics audit", f"- exact duplicate body_markdown: {s['duplicate_body_count']}", f"- duplicate body groups: {s['duplicate_body_groups']}", f"- duplicate learning objectives: {s['duplicate_learning_objectives']}", f"- questions repeated more than 3 times: {s['duplicate_question_over_limit']}", f"- duplicate scenario_id values: {s['duplicate_scenario_ids']}", f"- missing top-level scenario_id values: {s['missing_top_level_scenario_ids']}", f"- duplicate normalized body inside lessons: {s['lesson_duplicate_normalized_body']}", f"- duplicate normalized solution inside lessons: {s['lesson_duplicate_normalized_solution']}", f"- duplicate checker signature inside lessons: {s['lesson_duplicate_checker_signature']}", f"- normalized_solution_code repeats across course: {s['course_duplicate_normalized_solution']}", f"- structural solution repeats over limit: {s['structural_solution_repeats_over_limit']}", f"- AI structural solution duplicates: {s['ai_structural_solution_duplicates']}", f"- AI quality violations: {s['ai_quality_violations']}", f"- SQL progression violations: {s['sql_progression_violations']}", f"- FastAPI title/method mismatches: {s['fastapi_title_method_mismatches']}", f"- FastAPI solution/method mismatches: {s['fastapi_solution_method_mismatches']}", f"- FastAPI duplicate business contracts inside lessons: {s['fastapi_lesson_business_duplicates']}", f"- FastAPI duplicate method/path/status inside lessons: {s.get('fastapi_method_path_status_duplicates', 0)}", f"- encoding corruption in JSON fields: {s.get('encoding_corruption', 0)}", f"- encoding corruption in package files: {s.get('package_file_corruption', 0)}", f"- AI aggressive solution duplicates: {s.get('ai_aggressive_solution_duplicates', 0)}", f"- normalized_test_code repeats across course: {s['course_duplicate_normalized_test_code']}", f"- normalized_test_code repeats inside lessons: {s['lesson_duplicate_normalized_test_code']}", f"- identical SQL query reused in practice: {s['duplicate_sql_practice_query']}", f"- identical SQL schema/seed/expected reused: {s['duplicate_sql_checker_dataset']}", f"- FastAPI endpoint template reuse: {s['fastapi_endpoint_template_reuse']}", f"- FastAPI route/model/checker reuse: {s['fastapi_route_model_signature_reuse']}", f"- FastAPI artificial routes: {s['fastapi_artificial_routes']}", f"- HTTP body/checker route mismatch: {s['http_body_checker_mismatch']}", f"- body service sections: {s['body_service_sections']}", f"- artificial uniqueness markers: {s['artificial_uniqueness_markers']}", f"- Python key-skill mismatch: {s['python_key_skill_mismatch']}", f"- OOP key-skill mismatch: {s['oop_key_skill_mismatch']}", f"- banned repeated algorithm families: {s['banned_algorithm_family_hits']}", f"- early Python future-knowledge violations: {s['future_knowledge_violations']}", f"- algorithmic pattern over limit: {s['algorithmic_pattern_over_limit']}", f"- mass algorithm family repeats: {s['mass_algorithm_family_repeats']}", f"- missing step focus fields: {s['missing_step_focus_fields']}", f"- placeholder focus fields: {s['placeholder_focus_fields']}", f"- template-style test questions: {s['template_test_questions']}", f"- repeated question templates after lesson removal: {s['template_question_signature_repeats']}", f"- generic test questions: {s['generic_test_questions']}", f"- lesson_stage/content mismatches: {s['bad_stage_content']}", f"- short complex theory steps: {s['short_complex_theory']}", f"- weak project solutions: {s['weak_project_solutions']}", f"- unique learning objectives: {s['unique_learning_objectives']}", f"- lesson ladder stage gaps: {s['lesson_stage_gaps']}", f"- lessons without mini-project: {s['lessons_without_project']}", f"- short test steps: {s['short_test_steps']}", "- semantic objective uniqueness, anti-duplication and lesson-stage coverage are hard gates, not warnings.", "",
        "## Solution audit", f"- practice with empty solution_code: {len(result['empty_practice_solution'])}", f"- project with empty solution_code: {len(result['empty_project_solution'])}", "- IDE/project solutions include expected files, commands, successful output shape and decision notes.", "",
        "## Checker audit", f"- unique IDE checker signatures: {s['unique_ide_signatures']}", f"- max IDE signature repeat: {s['max_ide_signature_repeat']}", "- Git labs check dirty worktree, conflict markers, branches, commit count, reflog/stash/force-with-lease scenarios.", "- DevOps labs include runtime checks: container start, healthcheck, env, tests inside container, deploy dry-run and rollback dry-run.", "- Final gates include gate_checks with required artifacts and pass/fail criteria.", "",
        "## Deep-topic audit", "- SQL advanced includes LEFT JOIN anti-patterns, window ranking, CTE aggregation, transactions with rollback/savepoint, indexes with EXPLAIN and lock/isolation simulations.", "- FastAPI tasks include 201/204/401/404/422 checks, request bodies, routers, auth, SQLAlchemy, TestClient and integration paths.", "- Docker/CI/CD/Deploy tasks check real runtime meaning instead of only file presence.", "- Final project gates are split into requirements, user stories, DB schema, API contract, Git workflow, FastAPI structure, SQLAlchemy, Alembic, auth, CRUD, tests, Docker, CI/CD, AI integration, logging, README, deploy and defense.", "",
        "## Hidden-test audit", "- hidden tests cover empty values, wrong types, missing ordering, SQL injection, 401/404/422, dirty git trees, missing env files, missing healthcheck and rollback paths.", "",
        "## Manual QA required before launch", "- import package on staging;", "- compare imported counts against manifest.csv;", "- complete first 10 lessons as a student;", "- manually sample 50-100 steps across Python, Git, SQLite, SQL, FastAPI, Docker and final gates;", "- run IDE plugin on a real Git/FastAPI/Docker/final-project repository;", "- complete one final project end to end including deploy and defense;", "- run mentor dry-run for hidden-test complaints and recovery routes.", "",
        "## 20 худших шагов",
        *([f"- encoding: {item.get('step_id') or item.get('path')} / {item.get('lesson','')} / {item.get('title','')}: {item.get('quote','')}" for item in collect_json_corruption(load_course())[:20]] if collect_json_corruption(load_course()) else ([f"- blocker: {e}" for e in result["errors"][:20]] if result["errors"] else ["- автоматический аудит не нашёл критичных кандидатов; ручная выборка на staging обязательна, потому что автоматическая проверка не оценивает педагогическую интонацию на уровне живого студента."])),
        "",
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
    print(f"question_repeats={s['duplicate_question_over_limit']} scenario_dups={s['duplicate_scenario_ids']} lesson_body_dups={s['lesson_duplicate_normalized_body']} lesson_solution_dups={s['lesson_duplicate_normalized_solution']} checker_dups={s['lesson_duplicate_checker_signature']}")
    print(f"course_solution_dups={s['course_duplicate_normalized_solution']} lesson_test_code_dups={s['lesson_duplicate_normalized_test_code']} sql_query_dups={s['duplicate_sql_practice_query']} fastapi_template_reuse={s['fastapi_endpoint_template_reuse']} python_key_skill_mismatch={s['python_key_skill_mismatch']}")
    print(f"course_test_code_dups={s['course_duplicate_normalized_test_code']} sql_dataset_dups={s['duplicate_sql_checker_dataset']} fastapi_route_model_reuse={s['fastapi_route_model_signature_reuse']} algorithmic_pattern_over_limit={s['algorithmic_pattern_over_limit']} missing_focus={s['missing_step_focus_fields']} template_questions={s['template_test_questions']}")
    print(f"http_body_mismatch={s['http_body_checker_mismatch']} body_service_sections={s['body_service_sections']} artificial_markers={s['artificial_uniqueness_markers']} placeholder_focus={s['placeholder_focus_fields']} template_question_signatures={s['template_question_signature_repeats']}")
    print(f"generic_questions={s['generic_test_questions']} bad_stage={s['bad_stage_content']} short_complex_theory={s['short_complex_theory']} weak_project_solutions={s['weak_project_solutions']}")
    print(f"ai_quality={s['ai_quality_violations']} sql_progression={s['sql_progression_violations']} fastapi_method_title={s['fastapi_title_method_mismatches']} fastapi_method_solution={s['fastapi_solution_method_mismatches']} fastapi_lesson_business_dups={s['fastapi_lesson_business_duplicates']}")
    print(f"ladder_gaps={s['lesson_stage_gaps']} lessons_without_project={s['lessons_without_project']} short_tests={s['short_test_steps']} complex_short={s['complex_short_lessons']} ai_generic={s['ai_non_ai_practices']}")
    print(f"encoding_corruption={s.get('encoding_corruption', 0)} package_file_corruption={s.get('package_file_corruption', 0)} ai_aggressive_dups={s.get('ai_aggressive_solution_duplicates', 0)} fastapi_mps_dups={s.get('fastapi_method_path_status_duplicates', 0)}")
    if result["errors"]:
        for e in result["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
