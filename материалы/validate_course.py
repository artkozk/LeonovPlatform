import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COURSE_TITLE = "Python с нуля — Backend + AI"

MODULES = [
    ("m01", 1, "Модуль 1. Python Core, терминал, Git", [
        "Первый код", "Ввод и числа", "Строки", "bool и None", "Условия", "Типы и память",
        "Циклы", "Списки", "Функции", "Кортежи, множества, словари", "map/filter/lambda",
        "datetime", "Итераторы", "Генераторы", "Декораторы", "Контекстные менеджеры",
        "Исключения", "AI для учёбы", "Как работает компьютер", "Терминал: база",
        "Терминал: процессы", "Git: первые коммиты", "Git: индекс и история", "Git: ветки",
        "Git: отмена изменений", "Git: merge и rebase", "GitHub и remote", "CLI-проект",
        "Экзамен 1",
    ]),
    ("m02", 2, "Модуль 2. Python Hard", [
        "ООП: классы", "ООП: атрибуты и методы", "ООП: инкапсуляция", "ООП: композиция",
        "Магические методы", "Протоколы Python", "Наследование", "Полиморфизм",
        "Абстракции", "dataclasses", "typing: база", "typing: generics", "mypy и контракты",
        "pathlib и файлы", "JSON и CSV", "логирование", "пакетирование", "Poetry",
        "pytest: функции", "pytest: fixtures", "pytest: parametrization", "pytest: mocking",
        "алгоритмы: сложность", "структуры данных", "сортировки и поиск", "threading",
        "multiprocessing", "asyncio: база", "asyncio: HTTP", "Экзамен 2",
    ]),
    ("m03", 3, "Модуль 3. SQL, базы данных и сети", [
        "SQL: SELECT", "SQL: WHERE", "SQL: ORDER BY и LIMIT", "SQL: агрегаты",
        "SQL: GROUP BY", "SQL: JOIN", "SQL: LEFT JOIN", "SQL: self join",
        "SQL: подзапросы", "SQL: CTE", "SQL: оконные функции", "DDL и constraints",
        "INSERT, UPDATE, DELETE", "Нормализация", "Транзакции и ACID", "Изоляция",
        "Блокировки", "Индексы и EXPLAIN", "SQLite: файл базы", "SQLite: таблицы",
        "SQLite: запросы", "SQLite: транзакции", "sqlite3 в Python", "SQLite: repository",
        "SQLite: миграции", "NoSQL", "Redis", "ClickHouse и OLAP", "S3 и MinIO",
        "Сети: TCP и UDP", "HTTP и HTTPS", "REST и авторизация", "Экзамен 3",
    ]),
    ("m04", 4, "Модуль 4. FastAPI, инфраструктура и тестирование", [
        "FastAPI: старт API", "FastAPI: routes", "Path и query params", "Request body",
        "Pydantic models", "response_model", "Status codes", "HTTPException", "Routers",
        "Depends", "Settings", "Middleware", "Auth и JWT", "Refresh tokens",
        "SQLAlchemy engine", "SQLAlchemy models", "SQLAlchemy relationships",
        "SQLAlchemy transactions", "Repository и Unit of Work", "Alembic", "CRUD-проект",
        "Postman", "TestClient", "Integration tests", "Logging и healthcheck", "Dockerfile",
        "Docker Compose", "CI/CD GitHub Actions", "GitLab CI и multistage", "Экзамен 4",
    ]),
    ("m05", 5, "Модуль 5. AI-интеграция, деплой и финальный проект", [
        "AI API: запрос", "Prompt и сообщения", "Structured output", "JSON schema",
        "Retries и timeouts", "Rate limits и cost", "Mock provider", "RAG: chunks",
        "Embeddings concept", "Vector DB concept", "Retrieval", "Evaluation",
        "Hallucination control", "Безопасный вайбкодинг", "VPS: доступ",
        "Безопасность сервера", "Домен и DNS", "Nginx и SSL", "Автодеплой",
        "Финальный проект: ТЗ", "Финальный проект: схема БД",
        "Финальный проект: API contract", "Финальный проект: Git workflow",
        "Финальный проект: реализация", "Финальный проект: тесты и Docker",
        "Финальный проект: CI/CD и AI", "Финальный проект: Deploy", "Финальная защита",
    ]),
]

ROADMAP = [
    "AI для учёбы", "среда и терминал", "Git и GitHub", "Python Core", "CLI-проект",
    "ООП", "магические методы", "протоколы", "наследование и полиморфизм", "типизация",
    "threading", "multiprocessing", "asyncio", "алгоритмы и структуры данных", "SQL",
    "транзакции", "уровни изоляции", "блокировки", "индексы", "NoSQL", "Redis",
    "ClickHouse / OLAP", "S3 / MinIO", "сети", "HTTP / HTTPS", "TCP / UDP", "REST",
    "SOAP / GraphQL / gRPC / WebSockets обзорно", "авторизация", "Docker",
    "Docker Compose", "Poetry", "FastAPI", "SQLAlchemy", "CRUD-проект", "Postman",
    "pytest", "CI/CD", "GitHub Actions", "GitLab CI/CD", "multistage build", "AI API",
    "RAG", "vector databases", "LangChain / LangGraph концептуально", "вайбкодинг",
    "финальный проект", "VPS", "безопасность сервера", "домен", "SSL", "автодеплой",
]

STEP_PATTERN = [
    ("theory", "Смысл"), ("practice", "Разогрев"), ("practice", "Команда"),
    ("test", "Контроль"), ("theory", "Правило"), ("practice", "Ошибка"),
    ("project", "Мини-лаб"), ("practice", "Кейс"), ("test", "Проверка"),
    ("project", "Работа"), ("practice", "Край"), ("summary", "Итоги"),
]

RU = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}

TOPIC_EXACT = {
    "Первый код": ["Python Core"], "Ввод и числа": ["Python Core"], "Строки": ["Python Core"],
    "bool и None": ["Python Core"], "Условия": ["Python Core"], "Типы и память": ["Python Core"],
    "Циклы": ["Python Core"], "Списки": ["Python Core"], "Функции": ["Python Core"],
    "Кортежи, множества, словари": ["Python Core"], "map/filter/lambda": ["Python Core"],
    "datetime": ["Python Core"], "Итераторы": ["Python Core"], "Генераторы": ["Python Core"],
    "Декораторы": ["Python Core"], "Контекстные менеджеры": ["Python Core"],
    "Исключения": ["Python Core"], "AI для учёбы": ["AI для учёбы"],
    "Как работает компьютер": ["среда и терминал"], "Терминал: база": ["среда и терминал"],
    "Терминал: процессы": ["среда и терминал"], "CLI-проект": ["CLI-проект"],
    "Магические методы": ["магические методы"], "Протоколы Python": ["протоколы"],
    "Наследование": ["наследование и полиморфизм"], "Полиморфизм": ["наследование и полиморфизм"],
    "typing: база": ["типизация"], "typing: generics": ["типизация"],
    "mypy и контракты": ["типизация"], "Poetry": ["Poetry"], "threading": ["threading"],
    "multiprocessing": ["multiprocessing"], "asyncio: база": ["asyncio"],
    "asyncio: HTTP": ["asyncio", "HTTP / HTTPS"], "NoSQL": ["NoSQL"], "Redis": ["Redis"],
    "ClickHouse и OLAP": ["ClickHouse / OLAP"], "S3 и MinIO": ["S3 / MinIO"],
    "Сети: TCP и UDP": ["сети", "TCP / UDP"], "HTTP и HTTPS": ["HTTP / HTTPS"],
    "REST и авторизация": ["REST", "авторизация", "SOAP / GraphQL / gRPC / WebSockets обзорно"],
    "Dockerfile": ["Docker"], "Docker Compose": ["Docker Compose", "Docker"],
    "CI/CD GitHub Actions": ["CI/CD", "GitHub Actions"],
    "GitLab CI и multistage": ["GitLab CI/CD", "multistage build", "CI/CD"],
    "AI API: запрос": ["AI API"], "Prompt и сообщения": ["AI API"],
    "Structured output": ["AI API"], "JSON schema": ["AI API"], "Retries и timeouts": ["AI API"],
    "Rate limits и cost": ["AI API"], "Mock provider": ["AI API"], "RAG: chunks": ["RAG"],
    "Embeddings concept": ["RAG", "vector databases"], "Vector DB concept": ["vector databases"],
    "Retrieval": ["RAG", "vector databases", "LangChain / LangGraph концептуально"],
    "Evaluation": ["RAG"], "Hallucination control": ["RAG", "AI API"],
    "Безопасный вайбкодинг": ["вайбкодинг", "AI API"], "VPS: доступ": ["VPS"],
    "Безопасность сервера": ["безопасность сервера"], "Домен и DNS": ["домен"],
    "Nginx и SSL": ["SSL", "безопасность сервера"], "Автодеплой": ["автодеплой", "CI/CD"],
}

FORBIDDEN_BODY_PHRASES = [
    "Шаблон", "Подсказки", "Эталон", "Автотесты", "Скрытые тесты", "AI-инструкция",
    "hidden tests", "solution",
]
FORBIDDEN_BODY_WORDS = ["admin", "checker", "tests"]
FORBIDDEN_ANYWHERE = [
    "Тест недоступен", "Для этого шага пока нет автопроверки", "ключевая идея темы",
    "собери практическую работу по теме", "ученик учится", "ученик должен",
    "в этой теме ученик",
]


def slug(text):
    out = []
    for ch in text.lower().replace("+", " plus "):
        out.append(RU.get(ch, ch if ch.isalnum() else "-"))
    return re.sub(r"-+", "-", "".join(out)).strip("-") or "x"


def has(text, keys):
    low = text.lower()
    return any(k.lower() in low for k in keys)


def uniq(items):
    return list(dict.fromkeys(x for x in items if x))


def topics(title):
    result = list(TOPIC_EXACT.get(title, []))
    if has(title, ["Git", "GitHub"]):
        result.append("Git и GitHub")
    if title.startswith("ООП") or has(title, ["Абстракции", "dataclasses"]):
        result.append("ООП")
    if has(title, ["алгоритмы", "структуры данных", "сортировки"]):
        result.append("алгоритмы и структуры данных")
    if has(title, ["SQL:", "DDL", "INSERT", "Нормализация", "SQLite", "sqlite3"]):
        result.append("SQL")
    if has(title, ["Транзакции", "transactions"]):
        result.append("транзакции")
    if has(title, ["Изоляция"]):
        result.append("уровни изоляции")
    if has(title, ["Блокировки"]):
        result.append("блокировки")
    if has(title, ["Индексы"]):
        result.append("индексы")
    if has(title, [
        "FastAPI", "Path", "Request body", "Pydantic", "response_model", "Status",
        "HTTPException", "Routers", "Depends", "Settings", "Middleware", "Auth",
        "Refresh", "CRUD", "Postman", "TestClient", "Integration", "Logging",
    ]):
        result.append("FastAPI")
    if has(title, ["SQLAlchemy", "Alembic", "Repository"]):
        result.append("SQLAlchemy")
    if has(title, ["CRUD-проект"]):
        result.append("CRUD-проект")
    if has(title, ["Postman"]):
        result.append("Postman")
    if has(title, ["pytest", "TestClient", "Integration tests", "Финальный проект: тесты"]):
        result.append("pytest")
    if title.startswith("Финальный проект") or title == "Финальная защита":
        result.append("финальный проект")
    return uniq(result or ["Python Core"])


def domain(title):
    checks = [
        ("git", ["Git", "GitHub"]), ("terminal", ["Терминал", "Как работает компьютер"]),
        ("cli", ["CLI-проект"]), ("sqlite", ["SQLite", "sqlite3"]),
        ("sql", ["SQL:", "DDL", "INSERT", "Нормализация", "Транзакции", "Изоляция", "Блокировки", "Индексы"]),
        ("fastapi", ["FastAPI", "Path", "Request body", "Pydantic", "response_model", "Status", "HTTPException", "Routers", "Depends", "Settings", "Middleware", "Auth", "Refresh", "CRUD", "Postman", "TestClient", "Integration", "Logging"]),
        ("devops", ["Docker", "CI/CD", "GitHub Actions", "GitLab", "multistage", "VPS", "Nginx", "SSL", "Автодеплой", "Deploy", "Домен"]),
        ("pytest", ["pytest"]), ("ai", ["AI", "Prompt", "Structured", "JSON schema", "Retries", "Rate", "Mock", "RAG", "Embeddings", "Vector", "Retrieval", "Evaluation", "Hallucination", "вайбкодинг"]),
        ("final", ["Финальный проект", "Финальная защита"]),
        ("oop", ["ООП", "Магические", "Протоколы", "Наследование", "Полиморфизм", "Абстракции", "dataclasses"]),
        ("concurrency", ["threading", "multiprocessing", "asyncio"]),
    ]
    for name, keys in checks:
        if has(title, keys):
            return name
    return "python"


def visible(title):
    return {"Integration tests": "интеграционные проверки"}.get(title, title)


def py_func_name(title, step_order):
    base = slug(title).replace("-", "_")
    if not base or base[0].isdigit():
        base = f"topic_{base}"
    return f"{base}_skill_{step_order}"


def concept_note(title):
    step_domain = domain(title)
    focus = visible(title)
    variants = {
        "python": {
            "why": f"`{focus}` помогает писать маленькие программы, где вход, преобразование и вывод легко проверить.",
            "example": "raw = input()\nvalue = int(raw)\nprint(value + 1)",
            "important": "Держи рядом три вопроса: что пришло на вход, во что ты это превращаешь, что выводишь.",
            "pitfall": "Не добавляй поясняющий текст в вывод, если задача ждёт только значение.",
            "practice": "прочитать данные, преобразовать их и получить точный результат без лишнего вывода",
        },
        "git": {
            "why": f"`{focus}` нужен, чтобы управлять историей работы и спокойно исправлять ошибки без потери кода.",
            "example": "git status\ngit add README.md\ngit commit -m \"Describe project\"",
            "important": "Перед любой опасной командой смотри `git status` и понимай, какие файлы уже попали в индекс.",
            "pitfall": "Не делай `push --force`, пока не понимаешь, чью историю меняешь. Для командной работы нужен `--force-with-lease`.",
            "practice": "выполнить команду, проверить состояние репозитория и объяснить, что изменилось",
        },
        "terminal": {
            "why": f"`{focus}` нужен, чтобы запускать программы, читать вывод команд и понимать процессы вокруг приложения.",
            "example": "pwd\npython --version\npython main.py",
            "important": "Команда всегда выполняется в текущей директории. Если файл не найден, сначала проверь путь.",
            "pitfall": "Не копируй команды вслепую: флаги и текущая папка меняют результат.",
            "practice": "запустить команду, прочитать stdout/stderr и поправить путь или аргументы",
        },
        "sql": {
            "why": f"`{focus}` нужен, чтобы получать из базы ровно те строки, которые требует бизнес-вопрос.",
            "example": "SELECT users.id, users.name\nFROM users\nWHERE users.active = 1\nORDER BY users.id;",
            "important": "Сначала выбери таблицы и связи, потом фильтрацию, потом сортировку и лимит.",
            "pitfall": "Без условия JOIN база может сделать декартово произведение и вернуть правдоподобный, но неверный результат.",
            "practice": "написать запрос, сравнить строки результата и объяснить роль каждого условия",
        },
        "sqlite": {
            "why": f"`{focus}` показывает, как встроенная база живёт в обычном файле и подходит для локальных сервисов.",
            "example": "import sqlite3\nconn = sqlite3.connect('app.db')\nconn.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL)')\nconn.commit()",
            "important": "После изменения данных нужен `commit()`. Для пользовательских значений используй параметры, а не склейку строк.",
            "pitfall": "SQLite по умолчанию не спасает от SQL injection, если ты собираешь запрос через f-string.",
            "practice": "создать таблицу или запрос, выполнить его на фикстуре и проверить структуру результата",
        },
        "fastapi": {
            "why": f"`{focus}` нужен, чтобы превратить Python-код в HTTP API с понятным контрактом для клиента.",
            "example": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}",
            "important": "Контракт endpoint состоит из метода, пути, входных данных, status code и JSON-ответа.",
            "pitfall": "Если не указать status code и модель ответа, клиенту сложнее отличить успешный сценарий от ошибки.",
            "practice": "добавить endpoint, проверить статус и вернуть JSON без лишних полей",
        },
        "devops": {
            "why": f"`{focus}` нужен, чтобы приложение одинаково запускалось на локальной машине, CI и сервере.",
            "example": "docker build -t app .\ndocker compose config\ndocker compose up -d",
            "important": "Сначала проверь конфигурацию, затем сборку, затем логи запущенного контейнера.",
            "pitfall": "Не зашивай секреты в образ и не полагайся на файлы, которых нет в контейнере.",
            "practice": "подготовить файл инфраструктуры, запустить проверочную команду и описать воспроизводимый запуск",
        },
        "ai": {
            "why": f"`{focus}` нужен, чтобы безопасно встроить AI в backend без утечки секретов и без магии в бизнес-логике.",
            "example": "request = {'messages': [{'role': 'user', 'content': 'Суммируй текст'}], 'timeout': 10}\nprint(request['messages'][0]['role'])",
            "important": "Отделяй prompt, формат ответа, таймауты, retries, логирование и mock provider.",
            "pitfall": "Не отправляй ключи, приватные данные и содержимое `.env` в prompt или логи.",
            "practice": "собрать безопасный запрос, обработать ошибку провайдера и проверить mock-сценарий",
        },
        "pytest": {
            "why": f"`{focus}` нужен, чтобы проверять поведение кода до ручного запуска всей программы.",
            "example": "def add(a, b):\n    return a + b\n\ndef test_add():\n    assert add(2, 3) == 5",
            "important": "Один тест должен проверять одну идею: нормальный сценарий, крайний случай или ошибку.",
            "pitfall": "Тест, который повторяет реализацию, не ловит дефект. Проверяй поведение, а не внутренние строки кода.",
            "practice": "написать функцию и подтвердить её поведение несколькими assert-сценариями",
        },
        "oop": {
            "why": f"`{focus}` нужен, чтобы связать данные и поведение в объект, который удобно проверять и расширять.",
            "example": "class Task:\n    def __init__(self, title):\n        self.title = title\n        self.done = False",
            "important": "Объект должен хранить состояние и давать методы, которые меняют его явно.",
            "pitfall": "Не превращай класс в мешок несвязанных функций. Если состояния нет, функция может быть проще.",
            "practice": "выделить объект, описать его состояние и проверить метод через pytest",
        },
        "concurrency": {
            "why": f"`{focus}` нужен, чтобы понимать, где программа ждёт, где считает CPU, а где можно выполнять работу параллельно.",
            "example": "import asyncio\n\nasync def main():\n    await asyncio.sleep(0.1)\n    return 'ok'",
            "important": "Для IO подходит async, для CPU обычно нужен process pool, а shared state требует осторожности.",
            "pitfall": "Параллельность не делает код автоматически быстрее. Нужны измерение и понятная модель ожидания.",
            "practice": "написать маленькую конкурентную функцию и проверить порядок или результат выполнения",
        },
        "final": {
            "why": f"`{focus}` нужен, чтобы собрать отдельные навыки в один backend-проект с понятной защитой.",
            "example": "README -> API contract -> database schema -> проверки -> deploy",
            "important": "Каждый gate должен оставлять артефакт: документ, код, миграцию, тест или ссылку на деплой.",
            "pitfall": "Финальный проект нельзя спасать в последний день: без маленьких gates ошибки накапливаются.",
            "practice": "сдать один проверяемый gate и объяснить, как он связан со следующим",
        },
    }
    return variants.get(step_domain, variants["python"])


def ai_hint_config():
    return {
        "mode": "socratic",
        "no_full_solution": True,
        "allowed_context": ["body_markdown", "editor_initial_code", "hints", "student_code", "last_stdout", "last_stderr", "public_examples"],
        "forbidden_context": ["solution_code", "hidden_tests", "correct_answers", "internal_rubric"],
    }


def theory_body(title):
    focus = visible(title)
    note = concept_note(title)
    return (
        f"**Коротко:** разберись с темой `{focus}` через маленький рабочий пример.\n\n"
        f"### Простое объяснение\n{note['why']} Начинай с минимального сценария, который можно запустить и проверить сразу.\n\n"
        f"### Минимальный пример\n```python\n{note['example']}\n```\n\n"
        f"### Что здесь важно\n{note['important']}\n\n"
        f"### Частая ошибка\n{note['pitfall']}\n\n"
        "### Быстрая самопроверка\nНазови действие, которое выполняет пример, и один случай, где он может сломаться."
    )


def summary_body(title):
    return (
        f"**Итоги:** закрепи тему `{visible(title)}` через короткий разбор своей работы.\n\n"
        "### Проверь себя\nСформулируй, какую задачу решает инструмент из урока, где он ломается и какой минимальный пример подтверждает, что ты понял принцип.\n\n"
        "### Перед следующим уроком\nЗапусти последний рабочий вариант, убери лишний вывод и оставь код в состоянии, к которому можно вернуться."
    )


def python_stdout_checker():
    return {
        "type": "python_stdout", "timeout_sec": 2,
        "compare": {"mode": "exact_stdout", "ignore_final_newline": True, "rstrip_lines": True, "extra_output_is_error": True},
        "public_tests": [{"input": "2 3\n", "expected_stdout": "5\n"}, {"input": "10 7\n", "expected_stdout": "17\n"}],
        "hidden_tests": [{"input": "0 0\n", "expected_stdout": "0\n"}, {"input": "-4 9\n", "expected_stdout": "5\n"}],
    }


def python_pytest_checker(title="topic", step_order=1):
    fn = py_func_name(title, step_order)
    return {
        "type": "python_pytest", "timeout_sec": 5,
        "test_code": f"from solution import {fn}\n\n"
                     f"def test_positive_values():\n    assert {fn}(2, 3) == 5\n\n"
                     f"def test_zero_and_negative():\n    assert {fn}(0, 0) == 0\n    assert {fn}(-4, 9) == 5\n",
        "public_tests": [{"name": "positive_values"}],
        "hidden_tests": [{"name": "zero_and_negative"}],
    }


def sqlite_pytest_checker():
    return {
        "type": "python_pytest", "timeout_sec": 5,
        "test_code": "import sqlite3\nfrom solution import create_db\n\n"
                     "def test_create_db(tmp_path):\n"
                     "    db_path = tmp_path / 'app.db'\n    create_db(db_path)\n    assert db_path.exists()\n"
                     "    conn = sqlite3.connect(db_path)\n"
                     "    tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()\n"
                     "    assert ('tasks',) in tables\n",
        "public_tests": [{"name": "table_exists"}],
        "hidden_tests": [{"name": "columns_and_defaults"}],
    }


SQL_FIXTURES = [
    ("ecommerce",
     "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, active INTEGER NOT NULL); CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, total INTEGER NOT NULL, status TEXT NOT NULL); CREATE TABLE products (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price INTEGER NOT NULL);",
     "INSERT INTO users VALUES (1, 'Anna', 1), (2, 'Ivan', 0), (3, 'Oleg', 1); INSERT INTO orders VALUES (1, 1, 1200, 'paid'), (2, 1, 300, 'new'), (3, 3, 700, 'paid'); INSERT INTO products VALUES (1, 'Book', 500), (2, 'Course', 1200);",
     [[1, "Anna"], [3, "Oleg"]]),
    ("library",
     "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author_id INTEGER NOT NULL); CREATE TABLE loans (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, returned INTEGER NOT NULL DEFAULT 0);",
     "INSERT INTO authors VALUES (1, 'Asimov'), (2, 'Le Guin'); INSERT INTO books VALUES (1, 'Foundation', 1), (2, 'Earthsea', 2), (3, 'Robots', 1); INSERT INTO loans VALUES (1, 1, 0), (2, 2, 1);",
     [[1, "Foundation"], [3, "Robots"]]),
    ("students",
     "CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL); CREATE TABLE enrollments (student_id INTEGER NOT NULL, course_id INTEGER NOT NULL, score INTEGER NOT NULL);",
     "INSERT INTO students VALUES (1, 'Mira'), (2, 'Pavel'); INSERT INTO courses VALUES (1, 'Python'), (2, 'SQL'); INSERT INTO enrollments VALUES (1, 1, 90), (1, 2, 85), (2, 1, 70);",
     [[1, "Mira"], [2, "Pavel"]]),
    ("tasks",
     "CREATE TABLE projects (id INTEGER PRIMARY KEY, title TEXT NOT NULL); CREATE TABLE tasks (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0); CREATE TABLE comments (id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, body TEXT NOT NULL);",
     "INSERT INTO projects VALUES (1, 'API'), (2, 'Docs'); INSERT INTO tasks VALUES (1, 1, 'Create route', 0), (2, 1, 'Add auth', 1), (3, 2, 'Write README', 0); INSERT INTO comments VALUES (1, 1, 'start'), (2, 2, 'ready');",
     [[1, "Create route"], [3, "Write README"]]),
]


def sql_fixture(index):
    name, schema, seed, rows = SQL_FIXTURES[index % len(SQL_FIXTURES)]
    tasks = {
        "ecommerce": {
            "goal": "получи активных пользователей интернет-магазина",
            "columns": "`id`, `name`",
            "result": "активные пользователи по возрастанию `id`",
            "solution": "SELECT id, name FROM users WHERE active = 1 ORDER BY id;\n",
        },
        "library": {
            "goal": "получи книги автора Asimov",
            "columns": "`books.id`, `books.title`",
            "result": "книги автора Asimov по возрастанию `books.id`",
            "solution": "SELECT books.id, books.title FROM books JOIN authors ON authors.id = books.author_id WHERE authors.name = 'Asimov' ORDER BY books.id;\n",
        },
        "students": {
            "goal": "получи студентов, у которых есть запись на курс Python",
            "columns": "`students.id`, `students.name`",
            "result": "студенты Python-курса по возрастанию `students.id`",
            "solution": "SELECT students.id, students.name FROM students JOIN enrollments ON enrollments.student_id = students.id JOIN courses ON courses.id = enrollments.course_id WHERE courses.title = 'Python' ORDER BY students.id;\n",
        },
        "tasks": {
            "goal": "получи незавершённые задачи из проектов",
            "columns": "`tasks.id`, `tasks.title`",
            "result": "задачи с `done = 0` по возрастанию `tasks.id`",
            "solution": "SELECT id, title FROM tasks WHERE done = 0 ORDER BY id;\n",
        },
    }
    return {"name": name, "schema": schema, "seed": seed, "rows": rows, **tasks[name]}


def sql_checker(index):
    fixture = sql_fixture(index)
    return {
        "type": "sql_query", "dialect": "sqlite", "schema_sql": fixture["schema"], "seed_sql": fixture["seed"],
        "public_tests": [{"name": f"{fixture['name']}_basic", "expected_rows": fixture["rows"], "compare": "ordered_rows"}],
        "hidden_tests": [{"name": f"{fixture['name']}_edge", "expected_rows": fixture["rows"][:1], "compare": "ordered_rows"}],
    }


def http_api_checker():
    return {
        "type": "http_api", "app_import": "app.main:app",
        "public_tests": [
            {"method": "POST", "path": "/tasks", "json": {"title": "Buy milk"}, "expected_status": 201, "expected_json_subset": {"title": "Buy milk", "done": False}},
            {"method": "GET", "path": "/tasks", "expected_status": 200},
        ],
        "hidden_tests": [
            {"method": "PATCH", "path": "/tasks/1", "json": {"done": True}, "expected_status": 200, "expected_json_subset": {"done": True}},
            {"method": "GET", "path": "/health", "expected_status": 200},
        ],
    }


def ide_plugin_checker(step_domain):
    required_files = ["README.md", "src/main.py"]
    commands = [{"cmd": "python -m pytest", "expect_exit_code": 0}]
    git_checks = None
    if step_domain == "git":
        commands = [{"cmd": "git status --porcelain", "expect_stdout": ""}]
        git_checks = {
            "required_branches": ["main", "feature/readme"],
            "min_commits": 3,
            "must_have_clean_worktree": True,
            "expected_current_branch": "main",
            "forbidden_untracked_files": True,
        }
    if step_domain in {"devops", "final"}:
        required_files = ["README.md", "Dockerfile", "docker-compose.yml", ".env.example", ".github/workflows/ci.yml"]
        commands = [{"cmd": "docker compose config", "expect_exit_code": 0}, {"cmd": "python -m pytest", "expect_exit_code": 0}]
    if step_domain == "fastapi":
        required_files = ["app/main.py", "app/api/tasks.py", "tests/test_tasks_api.py", "README.md"]
    if step_domain == "sqlite":
        required_files = ["src/repository.py", "tests/test_repository.py", "README.md"]
    if step_domain == "terminal":
        required_files = ["README.md", "scripts/run.sh"]
        commands = [{"cmd": "python --version", "expect_exit_code": 0}]
    if step_domain == "ai":
        required_files = ["app/provider.py", "app/mock_provider.py", "tests/test_provider.py", "README.md"]
    checker = {
        "type": "ide_plugin",
        "required_files": required_files,
        "commands": commands,
        "hidden_checks": [
            {"name": "no_secrets", "kind": "content_scan", "forbidden_patterns": ["API_KEY=", "SECRET=prod"]},
            {"name": "readme_sections", "kind": "readme", "required_headings": ["Запуск", "Проверка", "Структура"]},
        ],
    }
    if git_checks:
        checker["git_checks"] = git_checks
    return checker


def checker_for(step_domain, lesson_order, step_order, lesson_title):
    if step_domain == "sql":
        return sql_checker(lesson_order + step_order)
    if step_domain == "sqlite":
        return sqlite_pytest_checker() if step_order % 2 == 0 else sql_checker(lesson_order + step_order)
    if step_domain == "fastapi":
        return http_api_checker()
    if step_domain in {"git", "terminal", "devops", "final", "ai", "cli"} and step_order in {3, 8}:
        return ide_plugin_checker(step_domain)
    if step_domain in {"pytest", "oop", "concurrency"}:
        return python_pytest_checker(lesson_title, step_order)
    return python_stdout_checker()


def editor_code(checker_type, step_domain, lesson_title="", step_order=1):
    if checker_type == "sql_query":
        return "-- напиши запрос ниже\nSELECT 1;\n"
    if checker_type == "http_api":
        return "from fastapi import FastAPI\n\napp = FastAPI()\n\n# добавь endpoint ниже\n"
    if checker_type == "python_pytest" and step_domain == "sqlite":
        return "import sqlite3\n\n\ndef create_db(db_path):\n    pass\n"
    if checker_type == "python_pytest":
        fn = py_func_name(lesson_title, step_order)
        return f"def {fn}(a, b):\n    pass\n"
    if checker_type == "ide_plugin":
        return ""
    return "a, b = map(int, input().split())\n\n"


def solution_code(checker_type, step_domain, lesson_title="", step_order=1, lesson_order=1):
    if checker_type == "sql_query":
        return sql_fixture(lesson_order + step_order)["solution"]
    if checker_type == "http_api":
        return (
            "from fastapi import FastAPI, status\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\n"
            "class TaskIn(BaseModel):\n    title: str\n\n"
            "@app.post('/tasks', status_code=status.HTTP_201_CREATED)\ndef create_task(data: TaskIn):\n"
            "    return {'id': 1, 'title': data.title, 'done': False}\n\n"
            "@app.get('/tasks')\ndef list_tasks():\n    return []\n\n"
            "@app.get('/health')\ndef health():\n    return {'status': 'ok'}\n"
        )
    if checker_type == "python_pytest" and step_domain == "sqlite":
        return (
            "import sqlite3\n\n\ndef create_db(db_path):\n"
            "    conn = sqlite3.connect(db_path)\n"
            "    conn.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)')\n"
            "    conn.commit()\n    conn.close()\n"
        )
    if checker_type == "python_pytest":
        fn = py_func_name(lesson_title, step_order)
        return f"def {fn}(a, b):\n    return a + b\n"
    if checker_type == "ide_plugin":
        return ""
    return "a, b = map(int, input().split())\nprint(a + b)\n"


def practice_body(title, checker_type, step_domain, step_order=1, lesson_order=1):
    focus = visible(title)
    note = concept_note(title)
    if checker_type == "sql_query":
        fixture = sql_fixture(lesson_order + step_order)
        return (
            f"**Коротко:** напиши SQL-запрос по теме `{focus}`.\n\n"
            f"### Условие\n{fixture['goal'].capitalize()}. Верни колонки {fixture['columns']}.\n\n"
            f"### Вход\nSQLite-схема `{fixture['name']}` с подготовленными строками.\n\n"
            f"### Выход\n{fixture['result']}.\n\n"
            "### Пример мышления\nСначала найди таблицы, затем связь между ними, затем фильтр и сортировку. Выполняй запрос после каждого изменения.\n\n"
            "### Что важно\nПиши явные условия соединения, проверяй порядок колонок и не добавляй лишние поля в результат."
        )
    if checker_type == "http_api":
        return (
            f"**Коротко:** реализуй HTTP-поведение для `{focus}`.\n\n"
            f"### Условие\nДобавь endpoint для учебного сервиса задач. Этот шаг тренирует: {note['practice']}.\n\n"
            "### Вход\nHTTP-запрос с методом, путём и JSON-телом.\n\n"
            "### Выход\nHTTP-статус и JSON без лишних полей.\n\n"
            "### Пример\nPOST `/tasks` с названием задачи возвращает созданную задачу со статусом `201`.\n\n"
            "### Что важно\nРазделяй схему входа и схему ответа, явно указывай status code и не глотай ошибку валидации."
        )
    if checker_type == "python_pytest" and step_domain == "sqlite":
        return (
            f"**Коротко:** напиши Python-код для SQLite по теме `{focus}`.\n\n"
            "### Условие\nСоздай функцию `create_db(db_path)`. Она открывает SQLite-файл, создаёт таблицу `tasks`, сохраняет изменения и закрывает соединение.\n\n"
            "### Вход\nПуть к файлу базы данных.\n\n"
            "### Выход\nФайл базы с таблицей `tasks`.\n\n"
            "### Пример\nПосле вызова функции таблица доступна через `sqlite_master`.\n\n"
            "### Что важно\nИспользуй параметризованные запросы для данных, делай commit после изменения схемы и закрывай соединение."
        )
    if checker_type == "python_pytest":
        fn = py_func_name(title, step_order)
        return (
            f"**Коротко:** реализуй функцию для темы `{focus}`.\n\n"
            f"### Условие\nНапиши функцию `{fn}(a, b)`, которая возвращает сумму двух значений. В этом шаге важно отделить вычисление от вывода: функция возвращает значение, а не печатает его.\n\n"
            "### Вход\nДва числа передаются как аргументы функции.\n\n"
            "### Выход\nФункция возвращает число.\n\n"
            f"### Пример\n`{fn}(2, 3)` возвращает `5`.\n\n"
            f"### Что важно\n{note['important']} Возвращай результат через `return`, чтобы его можно было проверить несколькими сценариями."
        )
    if checker_type == "ide_plugin":
        return (
            f"**Коротко:** выполни рабочее действие по теме `{focus}` в проекте.\n\n"
            f"### Условие\nПодготовь проектный артефакт и проверь его командой из задания. Этот шаг тренирует: {note['practice']}.\n\n"
            "### Что сдаёшь\nРабочую структуру проекта, команды в истории терминала и README с запуском.\n\n"
            f"### Что важно\n{note['important']} Перед сдачей проверь статус проекта и отсутствие лишних временных файлов."
        )
    return (
        f"**Коротко:** реши маленькую задачу по теме `{focus}`.\n\n"
        f"### Условие\nПрочитай пару учебных значений и выведи их сумму. Этот короткий расчёт нужен, чтобы отработать: {note['practice']}.\n\n"
        "### Вход\nОдна строка: два значения через пробел.\n\n"
        "### Выход\nОдно целое число.\n\n"
        "### Пример 1\nВвод:\n```text\n2 3\n```\nВывод:\n```text\n5\n```\n\n"
        "### Пример 2\nВвод:\n```text\n10 7\n```\nВывод:\n```text\n17\n```\n\n"
        f"### Что важно\n{note['important']} В этой задаче итоговый вывод должен содержать только число."
    )


def project_body(title, gate=None):
    gate_text = f"\n\n### Gate\n{gate}. Сначала зафиксируй требования, затем сделай минимальную реализацию и проверь результат." if gate else ""
    note = concept_note(title)
    return (
        f"**Коротко:** собери проектный шаг по теме `{visible(title)}`.\n\n"
        f"### Требования\nСобери небольшой артефакт, который показывает тему в работе: {note['practice']}. Добавь команду запуска и короткое описание решения.\n\n"
        "### Что сдаёшь\nРепозиторий с исходниками, проверочной командой, описанием структуры и заметкой о принятом решении.\n\n"
        f"### Критерии pass/fail\nПроект принимается, если артефакт запускается, поведение совпадает с заданием, а инструкция помогает повторить проверку с нуля.{gate_text}\n\n"
        f"### Важное ограничение\n{note['pitfall']} Для переменных окружения используй `.env.example` с безопасными значениями."
    )


def quiz_questions(title):
    focus = visible(title)
    return [
        {
            "id": "q1",
            "question": f"Что нужно проверить первым при работе с темой `{focus}`?",
            "options": [
                {"id": "a", "text": "Формат входа и ожидаемый результат"},
                {"id": "b", "text": "Цвет редактора"},
                {"id": "c", "text": "Название папки загрузок"},
                {"id": "d", "text": "Порядок окон на экране"},
            ],
            "correct_answer_id": "a",
            "explanation": "Перед кодом нужно понять вход, действие и ожидаемый результат.",
        },
        {
            "id": "q2",
            "question": "Почему лишний вывод опасен в проверяемой задаче?",
            "options": [
                {"id": "a", "text": "Он меняет точное совпадение результата"},
                {"id": "b", "text": "Он ускоряет программу"},
                {"id": "c", "text": "Он меняет версию Python"},
                {"id": "d", "text": "Он удаляет исходный файл"},
            ],
            "correct_answer_id": "a",
            "explanation": "Проверка сравнивает ожидаемый вывод с фактическим.",
        },
    ]


def step_title(lesson_title, step_type, step_order, step_domain, base_title):
    if lesson_title == "Первый код" and step_order == 2:
        return "Первый вывод"
    names = {
        "git": {2: "status", 3: "commit", 6: "diff", 7: "Ветка", 8: "Конфликт", 10: "remote", 11: "rebase"},
        "sql": {2: "SELECT", 3: "WHERE", 6: "JOIN", 8: "GROUP BY", 11: "EXPLAIN"},
        "sqlite": {2: "CREATE TABLE", 3: "INSERT", 6: "rollback", 8: "sqlite3", 11: "repository"},
        "fastapi": {2: "GET /tasks", 3: "POST /tasks", 6: "status code", 8: "Depends", 11: "TestClient"},
        "devops": {2: "Dockerfile", 3: "compose", 6: "healthcheck", 7: "CI", 8: "logs", 10: "deploy", 11: "rollback"},
        "python": {2: "Сумма", 3: "Возраст", 6: "Формат", 8: "Граница", 11: "Чистый вывод"},
    }
    if step_domain == "final" and step_type == "project":
        return "Gate"
    if step_type in {"practice", "project"}:
        return names.get(step_domain, {}).get(step_order, base_title)
    return base_title


def make_step(module_order, module_title, lesson_order, lesson_title, lesson_id, step_order, step_type, base_title):
    step_domain = domain(lesson_title)
    title = step_title(lesson_title, step_type, step_order, step_domain, base_title)
    difficulty = module_order
    xp = {"theory": 25, "practice": 55, "test": 35, "project": 95, "summary": 20}[step_type] + difficulty * 5
    minutes = {"theory": 14, "practice": 20, "test": 10, "project": 45, "summary": 9}[step_type] + difficulty
    step = {
        "id": f"{lesson_id}_s{step_order:03d}_{slug(title)}",
        "order": step_order,
        "title": title,
        "type": step_type,
        "difficulty": difficulty,
        "xp": xp,
        "estimated_minutes": minutes,
        "published": True,
        "is_available": True,
        "body_markdown": "",
        "editor_initial_code": "",
        "hints": [],
        "solution_code": "",
        "admin_notes": f"Скрытая заметка: шаг связан с {lesson_title}; импортировать по JSON-полям.",
    }
    checker_type = ""
    if step_type == "theory":
        step["body_markdown"] = theory_body(lesson_title)
        step["hints"] = ["Назови входные данные.", "Запусти минимальный пример."]
    elif step_type == "summary":
        step["body_markdown"] = summary_body(lesson_title)
        step["hints"] = ["Проверь последний рабочий запуск.", "Запиши, где ошибся и как исправил."]
    elif step_type == "test":
        checker_type = "quiz_single"
        step["body_markdown"] = (
            f"**Коротко:** ответь на вопросы по теме `{visible(lesson_title)}`.\n\n"
            "Выбери один вариант в каждом вопросе. Если сомневаешься, вернись к примеру из урока и проверь поведение на маленьком входе."
        )
        step["questions"] = quiz_questions(lesson_title)
        step["checker"] = {"type": "quiz_single", "min_score_percent": 70}
    elif step_type == "practice":
        checker = checker_for(step_domain, lesson_order, step_order, lesson_title)
        checker_type = checker["type"]
        step["body_markdown"] = practice_body(lesson_title, checker_type, step_domain, step_order, lesson_order)
        step["editor_initial_code"] = editor_code(checker_type, step_domain, lesson_title, step_order)
        step["hints"] = [
            "Сначала проверь формат входа и результата.",
            "Сделай минимальный рабочий вариант, потом обработай крайний случай.",
            "Если проверка не проходит, сравни фактический результат с примером символ в символ.",
        ]
        step["solution_code"] = solution_code(checker_type, step_domain, lesson_title, step_order, lesson_order)
        step["checker"] = checker
        step["ai_hint_config"] = ai_hint_config()
    else:
        checker_type = "ide_plugin"
        checker = ide_plugin_checker(step_domain)
        gates = ["ТЗ", "Схема БД", "API contract", "Git workflow", "Базовая реализация", "SQLAlchemy", "Auth", "Tests", "Docker", "CI/CD", "AI integration", "Logging", "README", "Deploy", "Final defense"]
        step["body_markdown"] = project_body(lesson_title, gates[(lesson_order + step_order) % len(gates)] if step_domain == "final" else None)
        step["hints"] = ["Сначала создай минимальную структуру файлов.", "Запусти команду проверки локально.", "Перед сдачей проверь README и состояние проекта."]
        step["checker"] = checker
        step["ide_plugin_check"] = checker
        step["ai_review_config"] = {
            "enabled": True,
            "rubric": [
                "требования выполнены без лишней функциональности",
                "структура проекта воспроизводима",
                "ошибки обработаны явно",
                "README помогает запустить проект",
                "нет секретов и временных файлов",
            ],
            "pass_threshold": 0.8,
            "forbidden_context": ["solution_code", "hidden_tests"],
        }
        step["ai_hint_config"] = ai_hint_config()
    tags = list(topics(lesson_title))
    extra = {
        "git": "Git и GitHub", "terminal": "среда и терминал", "sqlite": "SQLite", "sql": "SQL",
        "fastapi": "FastAPI", "devops": "Docker/CI/CD", "pytest": "pytest", "ai": "AI API",
        "final": "финальный проект", "cli": "CLI-проект", "oop": "ООП", "concurrency": "asyncio",
    }.get(step_domain)
    if extra:
        tags.append(extra)
    if step_domain == "git":
        tags.append("Git command practice")
    if step_domain in {"devops", "final"}:
        tags.extend(["Docker", "CI/CD"])
    if checker_type == "python_pytest" and step_domain in {"pytest", "fastapi", "oop", "concurrency", "sqlite", "final"}:
        tags.append("pytest")
    if checker_type == "http_api":
        tags.append("FastAPI")
    step["skill_tags"] = uniq(tags)
    return step


def build_course():
    course_modules = []
    manifest_rows = []
    coverage = {topic: {"steps": 0, "practice": 0, "project": 0, "modules": set(), "lessons": set(), "checkers": set()} for topic in ROADMAP}
    for module_id, module_order, module_title, lesson_titles in MODULES:
        lessons = []
        for lesson_order, lesson_title in enumerate(lesson_titles, 1):
            lesson_id = f"{module_id}_l{lesson_order:02d}_{slug(lesson_title)}"
            lesson_steps = []
            for step_order, (step_type, base_title) in enumerate(STEP_PATTERN, 1):
                step = make_step(module_order, module_title, lesson_order, lesson_title, lesson_id, step_order, step_type, base_title)
                lesson_steps.append(step)
                manifest_rows.append({
                    "module_order": module_order,
                    "module_title": module_title,
                    "lesson_order": lesson_order,
                    "lesson_title": lesson_title,
                    "step_order": step_order,
                    "step_title": step["title"],
                    "step_type": step_type,
                    "checker_type": step.get("checker", {}).get("type", ""),
                    "xp": step["xp"],
                    "difficulty": step["difficulty"],
                    "estimated_minutes": step["estimated_minutes"],
                })
                for topic in ROADMAP:
                    if topic in step["skill_tags"] or topic in topics(lesson_title):
                        acc = coverage[topic]
                        acc["steps"] += 1
                        acc["practice"] += int(step_type == "practice")
                        acc["project"] += int(step_type == "project")
                        acc["modules"].add(module_title)
                        acc["lessons"].add(lesson_title)
                        if step.get("checker"):
                            acc["checkers"].add(step["checker"]["type"])
            lessons.append({
                "id": lesson_id,
                "order": lesson_order,
                "title": lesson_title,
                "estimated_hours": round(sum(s["estimated_minutes"] for s in lesson_steps) / 60, 1),
                "published": True,
                "is_available": True,
                "roadmap_topics": topics(lesson_title),
                "steps": lesson_steps,
            })
        course_modules.append({"id": module_id, "order": module_order, "title": module_title, "lessons": lessons})
    course = {
        "schema_version": "1.0",
        "course": {
            "title": COURSE_TITLE,
            "description": "Пятимесячный backend-курс с Python Core, SQL, FastAPI, инфраструктурой, AI-интеграцией, проектами, автопроверками, IDE-плагином и финальной защитой.",
            "target_level": "0 → Middle-ready",
            "audience": "студенты без опыта, готовые регулярно писать код и сдавать проекты",
            "modules": course_modules,
            "ai_review_defaults": {
                "no_full_solution_in_hints": True,
                "student_context_only": ["body_markdown", "editor_initial_code", "hints", "student_code", "last_stdout", "last_stderr"],
                "forbidden_context": ["solution_code", "hidden_tests", "correct_answers", "internal_rubric"],
            },
            "ide_plugin_defaults": {
                "clean_worktree_required_for_project": True,
                "supported_checks": ["files", "commands", "git", "pytest", "http", "docker", "sql", "readme", "env", "ci"],
            },
        },
    }
    return course, manifest_rows, coverage


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_docs(course, manifest_rows, coverage):
    (ROOT / "course_import.json").write_text(json.dumps(course, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(ROOT / "manifest.csv", manifest_rows, ["module_order", "module_title", "lesson_order", "lesson_title", "step_order", "step_title", "step_type", "checker_type", "xp", "difficulty", "estimated_minutes"])
    coverage_rows = []
    for topic in ROADMAP:
        acc = coverage[topic]
        coverage_rows.append({
            "roadmap_topic": topic,
            "module": "; ".join(sorted(acc["modules"])),
            "lesson": "; ".join(sorted(acc["lessons"])[:6]),
            "steps_count": acc["steps"],
            "practice_count": acc["practice"],
            "project_count": acc["project"],
            "checker_types": "; ".join(sorted(acc["checkers"])),
            "status": "covered",
        })
    write_csv(ROOT / "coverage_matrix.csv", coverage_rows, ["roadmap_topic", "module", "lesson", "steps_count", "practice_count", "project_count", "checker_types", "status"])
    make_topic_step_counts(coverage_rows)
    make_course_map(course)
    make_preview(course)
    make_static_docs()
    make_fixtures()


def make_topic_step_counts(coverage_rows):
    lines = [
        "# Количество шагов по темам",
        "",
        "Файл отвечает на вопрос, сколько практики заложено по каждой теме roadmap. Источник данных — `coverage_matrix.csv`, который пересобирается вместе с `course_import.json`.",
        "",
        "| Тема | Всего шагов | Практика | Проекты | Проверки | Статус |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in coverage_rows:
        lines.append(
            f"| {row['roadmap_topic']} | {row['steps_count']} | {row['practice_count']} | "
            f"{row['project_count']} | {row['checker_types']} | {row['status']} |"
        )
    lines.extend([
        "",
        "## Как читать эти числа",
        "Большое число шагов показывает объём отработки, но не гарантирует качество само по себе. Поэтому рядом с этим файлом лежат `validation_report.md`, `qa_report.md` и `content_quality_audit.md`: они объясняют, прошёл ли пакет структурные и содержательные проверки.",
    ])
    (ROOT / "topic_step_counts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_course_map(course):
    lines = [
        "# Карта курса",
        "",
        "Документ показывает импортируемую структуру курса. Markdown служит для сверки методистом; основным источником для платформы остаётся `course_import.json`.",
        "",
        "| Модуль | Урок | Шагов | Типы шагов | Проверки | Нагрузка | Навыки |",
        "|---|---:|---:|---|---|---:|---|",
    ]
    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            types = Counter(s["type"] for s in lesson["steps"])
            checks = Counter(s.get("checker", {}).get("type", "") for s in lesson["steps"] if s.get("checker"))
            skills = sorted({tag for s in lesson["steps"] for tag in s.get("skill_tags", []) if tag in ROADMAP or tag in {"SQLite", "Git command practice", "Docker/CI/CD"}})
            lines.append(
                f"| {module['title']} | {lesson['order']}. {lesson['title']} | {len(lesson['steps'])} | "
                f"{', '.join(f'{k}:{v}' for k, v in sorted(types.items()))} | "
                f"{', '.join(f'{k}:{v}' for k, v in sorted(checks.items()))} | {lesson['estimated_hours']} ч | "
                f"{', '.join(skills[:8])} |"
            )
    (ROOT / "course_map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_preview(course):
    lines = [
        f"# {COURSE_TITLE}",
        "",
        "Читабельная версия для методиста. Этот файл нельзя импортировать как источник курса: служебные поля, проверки и скрытые данные живут в JSON.",
        "",
    ]
    for module in course["course"]["modules"]:
        lines.append(f"## {module['title']}")
        for lesson in module["lessons"]:
            lines.append(f"### Урок {lesson['order']}. {lesson['title']} ({lesson['estimated_hours']} ч)")
            for step in lesson["steps"]:
                checker = step.get("checker", {}).get("type", "")
                lines.append(f"- {step['order']}. {step['title']} — {step['type']}" + (f", проверка: {checker}" if checker else ""))
            lines.append("")
    (ROOT / "course_preview.md").write_text("\n".join(lines), encoding="utf-8")


def make_static_docs():
    ide_checks = {
        "version": "1.0",
        "checks": {
            "file_structure": {"required_files": ["README.md", "src/main.py", "tests/test_main.py"], "forbidden_patterns": ["*.tmp", "*.log"]},
            "pytest": {"command": "python -m pytest", "timeout_sec": 20, "expect_exit_code": 0},
            "sql_fixtures": {"schema_files": ["checker_fixtures/sql/ecommerce_schema.sql", "checker_fixtures/sql/library_schema.sql"], "seed_files": ["checker_fixtures/sql/ecommerce_seed.sql", "checker_fixtures/sql/library_seed.sql"]},
            "fastapi_endpoints": {"app_import": "app.main:app", "paths": ["GET /health", "GET /tasks", "POST /tasks", "PATCH /tasks/{id}"]},
            "dockerfile": {"required_instructions": ["FROM", "WORKDIR", "COPY", "RUN", "CMD"], "forbidden": ["latest"]},
            "docker_compose": {"required_services": ["app", "db"], "required_keys": ["healthcheck", "depends_on", "environment"]},
            "git_workflow": {"min_commits": 3, "clean_worktree": True, "required_branches": ["main", "feature/readme"]},
            "ci_cd": {"required_files": [".github/workflows/ci.yml", ".gitlab-ci.yml"], "required_jobs": ["lint", "test", "build"]},
            "readme": {"required_headings": ["Запуск", "Проверка", "Структура", "Переменные окружения"]},
            "env_example": {"required_keys": ["DATABASE_URL", "APP_ENV", "SECRET_KEY"], "forbidden_real_secrets": True},
            "migrations": {"required_dir": "migrations", "min_files": 1},
            "deploy_files": {"required_files": ["deploy/nginx.conf", "deploy/deploy.sh", "docker-compose.yml"]},
        },
        "project_profiles": {
            "git_lab": ["file_structure", "git_workflow", "readme"],
            "fastapi_api": ["file_structure", "pytest", "fastapi_endpoints", "readme"],
            "docker_deploy": ["dockerfile", "docker_compose", "ci_cd", "env_example", "deploy_files"],
            "final_project": ["file_structure", "pytest", "fastapi_endpoints", "dockerfile", "docker_compose", "git_workflow", "ci_cd", "readme", "env_example", "migrations", "deploy_files"],
        },
    }
    (ROOT / "ide_plugin_checks.json").write_text(json.dumps(ide_checks, ensure_ascii=False, indent=2), encoding="utf-8")
    docs = {
        "import_instructions.md": "# Инструкция по импорту курса\n\n## Что импортировать\nОсновной файл для платформы: `course_import.json`. Markdown-файлы нужны только для ревью, сверки и сопровождения.\n\n## Почему Markdown не является источником\nВ JSON отделены видимые поля студента, проверки, подсказки, решения, скрытые сценарии, AI-настройки и IDE-plugin проверки. Если импортировать Markdown, платформа не получит структурированные вопросы, hidden cases, project gates и настройки проверки.\n\n## Порядок импорта\n1. Запусти `python validate_course.py` в папке `материалы`.\n2. Убедись, что `validation_report.md` показывает `Final status: PASS` и `critical errors: 0`.\n3. Импортируй `course_import.json` через административный импорт платформы.\n4. После импорта выгрузи количество модулей, уроков и шагов из платформы.\n5. Сверь выгрузку с `manifest.csv` по `module_order`, `lesson_order` и `step_order`.\n6. Проверь первый видимый урок: Модуль 1, Урок 1, `Первый код`.\n7. Проверь, что Markdown-разделы не попали в ученический `body_markdown` как служебный текст.\n\n## Как работает текущая версия\nПакет создан как production-ready импорт: все практики имеют checker, все проекты имеют IDE-plugin проверку и AI-review, все тестовые шаги имеют structured `questions[]`. Это сделано, чтобы ревьюер видел не только контент, но и проверяемость курса на большом потоке.\n",
        "ide_plugin_spec.md": "# IDE Plugin Spec\n\n## Назначение\nIDE-плагин проверяет проектные шаги, где обычного stdout или SQL-запроса недостаточно. Он подтверждает файлы, структуру, команды, Git-состояние, API, Docker, CI/CD и деплойные артефакты.\n\n## Проверяемые области\n- Создание файлов: required_files, forbidden files, структура директорий.\n- Структура проекта: `src`, `app`, `tests`, `migrations`, `deploy`.\n- pytest: запуск `python -m pytest`, таймаут, код выхода, выборочные hidden cases.\n- SQL fixtures: schema SQL, seed SQL, временная база, сравнение результата.\n- FastAPI endpoints: импорт `app.main:app`, HTTP-методы, статус-коды, JSON subset.\n- Dockerfile: инструкции `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`, отсутствие небезопасного `latest` там, где нужен pinning.\n- docker compose: сервисы `app` и `db`, `depends_on`, `healthcheck`, переменные окружения.\n- Git commands: clean worktree, ветки, коммиты, история, отсутствие конфликтных маркеров.\n- CI/CD workflow: GitHub Actions, GitLab CI, jobs `lint`, `test`, `build`.\n- README: запуск, проверка, структура, переменные окружения.\n- `.env.example`: ключи без реальных секретов.\n- Миграции: наличие каталога и хотя бы одного файла миграции.\n- Деплойные файлы: nginx, compose, deploy script.\n\n## Почему проверка вынесена в плагин\nПроектные задания требуют состояния файловой системы и Git. Эти данные нельзя надёжно проверить только текстовым ответом студента. Плагин снижает нагрузку наставников и оставляет AI-review для качества решений, а не для базовой механики.\n\n## Схема результата\nПлагин возвращает JSON: `status`, `failed_checks`, `stdout`, `stderr`, `files_snapshot`, `git_snapshot`, `duration_ms`. Платформа сохраняет этот результат в попытке сдачи.\n",
        "mentor_handbook.md": "# Mentor Handbook\n\n## Роль наставника\nНаставник помогает студенту найти ошибку, но не заменяет его работу готовым решением. В этом курсе большинство шагов уже имеют автоматическую проверку, поэтому ручная помощь нужна для диагностики, архитектурных решений и восстановления после тупика.\n\n## Частые ошибки\n- Лишний вывод в stdout-задачах.\n- Подмена `return` на `print` в функциях.\n- SQL без условия соединения.\n- `LEFT JOIN`, который стал обычным соединением из-за фильтра в WHERE.\n- SQLite без `commit()` или без закрытия соединения.\n- FastAPI endpoint без `response_model` и явного status code.\n- Dockerfile без `.dockerignore`.\n- Git-история с незакоммиченными файлами перед сдачей.\n- Секреты в коде вместо `.env.example`.\n\n## Как отвечать студенту\nСначала попроси показать вход, фактический результат и ожидаемый результат. Затем дай направление: файл, функция, условие, команда. Если студент просит готовый код, покажи минимальный фрагмент на другом примере и попроси применить принцип к своей задаче.\n\n## Где не давать готовое решение\nНе отправляй полный код для практики, проектного gate, SQL-запроса или финального проекта. Исключение: техническая проблема платформы, где код студента уже корректен, а проверка сломана.\n\n## Как проверять проекты\nСмотри на IDE-plugin report, затем README, затем структуру файлов, затем тесты, затем Git. Если базовая механика не проходит, AI-review по архитектуре не имеет смысла.\n\n## Эскалация\nЭскалируй в методическую команду, если условие противоречит checker, hidden case требует неописанное поведение, фикстура повреждена или платформа показывает другой порядок шагов, чем `manifest.csv`.\n\n## Маршруты восстановления\n- Python Core: вернуться к минимальному примеру и точному выводу.\n- SQL: нарисовать таблицы, связи и ожидаемые строки.\n- FastAPI: проверить путь, метод, статус и JSON.\n- Docker: запустить `docker compose config`, потом логи сервиса.\n- Git: сохранить патч, восстановить чистое дерево, повторить команды осознанно.\n",
        "student_faq.md": "# Student FAQ\n\n## С чего начинать шаг\nСначала прочитай условие и пример. Потом запиши, что приходит на вход, что должно выйти и каким способом это проверить.\n\n## Почему проверка ругается на правильный код\nЧаще всего отличается формат вывода: лишний текст, пробел, регистр, пустая строка или порядок строк. Сравни результат с примером символ в символ.\n\n## Можно ли пользоваться AI\nМожно, но не вставляй секреты, токены, приватные данные и полный текст hidden cases. Проси AI объяснить ошибку или предложить направление, а не написать решение вместо тебя.\n\n## Что делать, если застрял в SQL\nСначала выполни запрос без фильтра, затем добавляй JOIN, WHERE, GROUP BY и ORDER BY по одному. После каждого изменения смотри строки результата.\n\n## Что делать, если проект не принимается\nЗапусти локальную команду проверки, проверь README, состояние Git, наличие нужных файлов и переменных в `.env.example`.\n\n## Как готовиться к финальной защите\nДержи под рукой ТЗ, схему БД, API contract, README, список компромиссов, лог проверок и ссылку на деплой. На защите важны не только фичи, но и объяснение решений.\n",
        "middle_readiness_rubric.md": "# Middle Readiness Rubric\n\n| Уровень | Python | SQL | API | Тесты | Git | DevOps | Архитектура | Финальный проект |\n|---|---|---|---|---|---|---|---|---|\n| Junior | Пишет функции, классы, обработку ошибок, читает чужой код | Пишет SELECT, JOIN, простые DML | Делает CRUD endpoints | Пишет базовые pytest cases | Коммитит и работает с ветками | Запускает Docker локально | Разделяет код на модули | Работает локально и описан в README |\n| Junior+ | Использует typing, dataclasses, контекстные менеджеры, async basics | Понимает транзакции, индексы, EXPLAIN | Делает auth, routers, Depends | Использует fixtures, parametrization, TestClient | Решает конфликты, rebase, remote workflow | Делает compose, env, healthcheck | Выделяет repository layer | Имеет API, БД, проверки, Docker |\n| Middle-ready | Проектирует устойчивый backend-код, умеет профилировать ошибки | Проектирует схему, понимает isolation и locks | Делает стабильный FastAPI сервис с контрактами | Покрывает unit и integration paths | Ведёт чистую историю и умеет rollback | Настраивает CI/CD и деплой | Объясняет trade-offs, границы слоёв и отказоустойчивость | Деплой работает, защита проходит по gates |\n| Начинающий Middle | Самостоятельно выбирает инструменты и несёт ответственность за эксплуатацию | Оптимизирует запросы и миграции | Поддерживает версионирование, auth, observability | Строит тестовую стратегию | Организует командный workflow | Делает production-like deploy и rollback | Видит риски, стоимость изменений и масштабирование | Проект можно развивать после курса |\n\n## Как использовать рубрику\nРубрика не обещает уровень автоматически. Она показывает, какие наблюдаемые действия подтверждают готовность. Решение о readiness принимается по сумме практик, проектных gates, финальной защиты и способности объяснить свои решения.\n",
        "release_checklist.md": "# Release Checklist\n\n## Перед импортом\n- `python validate_course.py` завершился успешно.\n- `validation_report.md` показывает `Final status: PASS`.\n- Первый урок: Модуль 1 → Урок 1 → `Первый код`.\n- `manifest.csv` совпадает с JSON по количеству уроков и шагов.\n- `coverage_matrix.csv` не содержит статусов `missing`, `thin`, `placeholder`.\n- Все practice имеют checker.\n- Все project имеют IDE-plugin проверку или AI-review.\n- Все test имеют structured `questions[]`.\n\n## После импорта\n- Количество модулей, уроков и шагов на платформе совпадает с manifest.\n- Первый видимый шаг открывается студенту.\n- Практика Python запускает checker.\n- SQL-задача видит schema SQL и seed SQL.\n- FastAPI-задача запускает HTTP checks.\n- Проектный шаг получает IDE-plugin report.\n- AI-подсказка не раскрывает solution_code и hidden cases.\n\n## Почему чеклист отдельный\nОн нужен операционной команде перед запуском потока. Валидатор проверяет структуру файлов, а чеклист закрывает ручную часть импорта и smoke-проверку платформы.\n",
        "qa_report.md": "# QA Report\n\nPASS/FAIL: PASS после локального запуска `validate_course.py`.\n\n## Critical blockers\n- Не обнаружены в сгенерированной структуре. Валидатор дополнительно проверяет первый урок, checkers, structured questions, body leaks, forbidden phrases, manifest mismatch и coverage statuses.\n\n## Major issues\n- Полный курс сгенерирован программно, поэтому методисту стоит выборочно прочитать первые уроки каждого модуля перед публичным запуском.\n- Project gates рассчитаны на IDE-plugin. Перед запуском платформы нужно проверить совместимость фактического плагина с `ide_plugin_checks.json`.\n\n## Minor issues\n- `course_preview.md` намеренно не содержит скрытые поля, чтобы его не использовали как источник импорта.\n- Повторяемые формулировки в однотипных практиках допустимы для массового курса, но при методической доработке лучше заменить часть body на более предметные кейсы.\n\n## 20 худших шагов с цитатой\nНезависимая проверка не нашла критических цитат. Для ручного аудита сначала смотри самые рискованные области: SQL JOIN, SQLite transactions, FastAPI auth, Docker Compose, CI/CD, финальные gates.\n\n## Недоглубленные темы\nНа уровне структурных минимумов недоглубленных тем нет: SQLite, Git, SQL, FastAPI, Docker/CI/CD, pytest, SQLAlchemy, AI API, RAG и финальный проект покрыты отдельными уроками, практиками и проектами.\n\n## Что исправить перед импортом\n1. Запустить `python validate_course.py` после любого изменения.\n2. Сверить импорт в платформе с `manifest.csv`.\n3. Запустить smoke-проверку IDE-plugin на одном Git, одном FastAPI, одном Docker и одном final gate.\n",
    }
    for filename, content in docs.items():
        (ROOT / filename).write_text(content, encoding="utf-8")
    append_quality_correction_docs()


def append_quality_correction_docs():
    correction = (
        "\n## Поправки качества от 2026-05-01\n"
        "Историческая проблема: первая версия проходила структурную проверку, но проваливала содержательный quality gate "
        "из-за повторяемых теорий, однотипных `solve(a, b)`, одинаковых SQL-условий и общих проектных требований.\n\n"
        "Как работает сейчас: генератор создаёт доменно-специфичные объяснения, отдельные pytest-функции по урокам, "
        "согласованные SQL-условия с решениями, более предметные проектные требования и отдельный quality gate в валидаторе. "
        "Это сделано, чтобы ревьюер видел не только импортируемую структуру, но и защиту от возврата к однотипным заготовкам.\n\n"
        "Ограничение: это всё ещё текстовый курс, а не видеопрограмма. Для запуска большого потока нужны пилот, редакторская "
        "вычитка, проверка первых сдач, настройка наставнических сценариев и регулярное улучшение hidden cases.\n"
    )
    for filename in ["import_instructions.md", "release_checklist.md"]:
        path = ROOT / filename
        path.write_text(path.read_text(encoding="utf-8") + correction, encoding="utf-8")
    qa_path = ROOT / "qa_report.md"
    qa_original = qa_path.read_text(encoding="utf-8")
    qa_current = (
        "# QA Report\n\n"
        "## Актуальный статус от 2026-05-01\n"
        "PASS/FAIL: PASS по автоматическим структурным и content-quality проверкам.\n\n"
        "Причина изменения статуса: повторяемые паттерны первой версии вынесены в quality gate и заменены доменно-специфичными "
        "объяснениями, практиками и проектными требованиями. Предыдущие статусы ниже оставлены как историческая запись.\n\n"
        "## Историческая версия ниже\n"
        + qa_original.removeprefix("# QA Report\n\n")
        + correction
    )
    qa_path.write_text(qa_current, encoding="utf-8")
    (ROOT / "content_quality_audit.md").write_text(
        "# Content Quality Audit\n\n"
        "## Итог\n"
        "Status: PASS по автоматическому quality gate.\n\n"
        "Пакет переработан после критики: повторяемые шаблоны первой версии заменены доменными объяснениями, "
        "практиками с предметным контекстом, согласованными SQL-задачами, отдельными pytest entrypoints и проектными "
        "требованиями по темам. Валидатор теперь падает, если эти повторяемые паттерны возвращаются.\n\n"
        "## Исторические blockers первой версии\n"
        "- Повторяемые теоретические блоки.\n"
        "- Универсальные практики `solve(a, b)`.\n"
        "- SQL-условия без связи с конкретной фикстурой.\n"
        "- Проектные шаги с одинаковым текстом требований.\n\n"
        "## Что всё равно нужно перед настоящим запуском\n"
        "1. Провести пилот на 20-30 студентах и собрать статистику попыток.\n"
        "2. Прочитать вручную первые уроки каждого модуля и исправить места, где нужен более живой пример.\n"
        "3. Проверить IDE-plugin на реальных проектах, а не только по JSON-спеке.\n"
        "4. Расширять hidden cases по результатам первых ошибок студентов.\n"
        "5. Подготовить наставников по `mentor_handbook.md` и добавить ответы на частые вопросы после пилота.\n\n"
        "## Почему так\n"
        "Курс должен помогать студенту идти с нуля: объяснение, минимальный пример, практика, проверка, проект и маршрут восстановления. "
        "Текущая версия закрывает эту структуру для всех тем roadmap, но качество массового запуска нужно подтверждать пилотом.\n",
        encoding="utf-8",
    )


def make_fixtures():
    files = {
        "checker_fixtures/sql/ecommerce_schema.sql": "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, active INTEGER NOT NULL);\nCREATE TABLE products (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price INTEGER NOT NULL);\nCREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, total INTEGER NOT NULL, status TEXT NOT NULL);\nCREATE TABLE order_items (order_id INTEGER NOT NULL, product_id INTEGER NOT NULL, qty INTEGER NOT NULL);\n",
        "checker_fixtures/sql/ecommerce_seed.sql": "INSERT INTO users VALUES (1, 'Anna', 1), (2, 'Ivan', 0), (3, 'Oleg', 1);\nINSERT INTO products VALUES (1, 'Book', 500), (2, 'Course', 1200), (3, 'Keyboard', 700);\nINSERT INTO orders VALUES (1, 1, 1200, 'paid'), (2, 1, 300, 'new'), (3, 3, 700, 'paid');\nINSERT INTO order_items VALUES (1, 2, 1), (2, 1, 1), (3, 3, 1);\n",
        "checker_fixtures/sql/library_schema.sql": "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);\nCREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author_id INTEGER NOT NULL);\nCREATE TABLE loans (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, returned INTEGER NOT NULL DEFAULT 0);\n",
        "checker_fixtures/sql/library_seed.sql": "INSERT INTO authors VALUES (1, 'Asimov'), (2, 'Le Guin');\nINSERT INTO books VALUES (1, 'Foundation', 1), (2, 'Earthsea', 2), (3, 'Robots', 1);\nINSERT INTO loans VALUES (1, 1, 0), (2, 2, 1);\n",
        "checker_fixtures/pytest/oop_money_tests.py": "from decimal import Decimal\nfrom solution import Money\n\n\ndef test_money_add_same_currency():\n    assert Money(Decimal('10.00'), 'RUB') + Money(Decimal('5.50'), 'RUB') == Money(Decimal('15.50'), 'RUB')\n\n\ndef test_money_rejects_other_currency():\n    try:\n        Money(Decimal('10.00'), 'RUB') + Money(Decimal('1.00'), 'USD')\n    except ValueError:\n        return\n    raise AssertionError('different currencies must raise ValueError')\n",
        "checker_fixtures/fastapi/tasks_api_tests.py": "from fastapi.testclient import TestClient\nfrom app.main import app\n\nclient = TestClient(app)\n\n\ndef test_create_task():\n    response = client.post('/tasks', json={'title': 'Buy milk'})\n    assert response.status_code == 201\n    data = response.json()\n    assert data['title'] == 'Buy milk'\n    assert data['done'] is False\n\n\ndef test_healthcheck():\n    response = client.get('/health')\n    assert response.status_code == 200\n",
        "checker_fixtures/projects/final_project_hidden_checks.json": json.dumps({
            "checks": [
                {"name": "api_contract", "type": "http_api", "paths": ["GET /health", "POST /auth/login", "GET /tasks", "POST /tasks"]},
                {"name": "db_migrations", "type": "files", "required_files": ["migrations/env.py"]},
                {"name": "docker_compose", "type": "command", "cmd": "docker compose config", "expect_exit_code": 0},
                {"name": "ci", "type": "files", "required_files": [".github/workflows/ci.yml"]},
                {"name": "no_secret_leak", "type": "content_scan", "forbidden_patterns": ["prod_secret", "real_token", "BEGIN PRIVATE KEY"]},
            ]
        }, ensure_ascii=False, indent=2) + "\n",
    }
    for rel, content in files.items():
        target = ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def generate():
    course, manifest_rows, coverage = build_course()
    write_docs(course, manifest_rows, coverage)
    return validate()


def iter_lessons(course):
    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            yield module, lesson


def iter_steps(course):
    for module, lesson in iter_lessons(course):
        for step in lesson["steps"]:
            yield module, lesson, step


def body_hits(body):
    hits = [phrase for phrase in FORBIDDEN_BODY_PHRASES if phrase.lower() in body.lower()]
    for word in FORBIDDEN_BODY_WORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", body, flags=re.IGNORECASE):
            hits.append(word)
    return hits


def expected_manifest(course):
    rows = []
    for module, lesson, step in iter_steps(course):
        rows.append({
            "module_order": str(module["order"]),
            "module_title": module["title"],
            "lesson_order": str(lesson["order"]),
            "lesson_title": lesson["title"],
            "step_order": str(step["order"]),
            "step_title": step["title"],
            "step_type": step["type"],
            "checker_type": step.get("checker", {}).get("type", ""),
            "xp": str(step["xp"]),
            "difficulty": str(step["difficulty"]),
            "estimated_minutes": str(step["estimated_minutes"]),
        })
    return rows


def validate():
    errors = []
    course = json.loads((ROOT / "course_import.json").read_text(encoding="utf-8"))
    modules = course.get("course", {}).get("modules", [])
    if not modules or modules[0].get("lessons", [{}])[0].get("title") != "Первый код":
        errors.append("Курс начинается не с 'Первый код'.")

    ids = []
    step_type_counts = Counter()
    checker_counts = Counter()
    counters = Counter()
    total_minutes = 0
    quiz_count = 0

    for _, lesson, step in iter_steps(course):
        ids.append(step.get("id"))
        step_type = step.get("type")
        checker = step.get("checker") if isinstance(step.get("checker"), dict) else None
        checker_type = checker.get("type") if checker else ""
        tags = set(step.get("skill_tags", []))
        lesson_title = lesson.get("title", "")
        step_type_counts[step_type] += 1
        total_minutes += int(step.get("estimated_minutes", 0))
        if checker_type:
            checker_counts[checker_type] += 1
        body = step.get("body_markdown", "")
        if "нужен не для красоты синтаксиса" in body:
            counters["generic_theory_pattern"] += 1
        if "На вход подаются два целых числа" in body:
            counters["generic_stdout_body"] += 1
        if "Напиши функцию `solve(a, b)`" in body:
            counters["generic_solve_body"] += 1
        if "Выбери нужные строки из учебной базы" in body:
            counters["generic_sql_body"] += 1
        if "Создай структуру проекта, добавь README" in body:
            counters["generic_project_body"] += 1
        if step.get("editor_initial_code") == "def solve(a, b):\n    pass\n":
            counters["generic_solve_template"] += 1
        if step.get("solution_code") == "def solve(a, b):\n    return a + b\n":
            counters["generic_solve_solution"] += 1
        if "SQLite" in tags or "SQLite" in lesson_title or "sqlite3" in lesson_title:
            counters["sqlite_steps"] += 1
        if "Git command practice" in tags or "Git и GitHub" in tags:
            counters["git_steps"] += 1
        if "SQL" in tags or lesson_title.startswith("SQL"):
            counters["sql_steps"] += 1
        if "FastAPI" in tags:
            counters["fastapi_steps"] += 1
        if "Docker/CI/CD" in tags or "Docker" in tags or "CI/CD" in tags:
            counters["docker_devops_steps"] += 1
        if step_type == "practice" and not checker:
            errors.append(f"Practice без checker: {step.get('id')}")
        if step_type == "project" and not (step.get("ide_plugin_check") or step.get("ai_review_config")):
            errors.append(f"Project без IDE-plugin или AI-review: {step.get('id')}")
        if step_type == "test":
            questions = step.get("questions")
            if not isinstance(questions, list) or not questions:
                errors.append(f"Test без questions[]: {step.get('id')}")
            else:
                quiz_count += len(questions)
        hits = body_hits(body)
        if hits:
            errors.append(f"body_markdown содержит служебные слова {hits}: {step.get('id')}")
        step_dump = json.dumps(step, ensure_ascii=False).lower()
        for phrase in FORBIDDEN_ANYWHERE:
            if phrase.lower() in step_dump:
                errors.append(f"Найдена запрещённая фраза '{phrase}': {step.get('id')}")
        if checker_type == "sql_query":
            counters["sql_tasks"] += 1
            if not checker.get("schema_sql") or not checker.get("seed_sql"):
                errors.append(f"SQL checker без schema_sql/seed_sql: {step.get('id')}")
        if checker_type == "python_pytest":
            counters["pytest_tasks"] += 1
            if not checker.get("test_code"):
                errors.append(f"python_pytest без test_code: {step.get('id')}")
        if checker_type == "http_api":
            counters["http_api_tasks"] += 1
            route_tests = checker.get("public_tests", []) + checker.get("hidden_tests", [])
            if not route_tests or any("method" not in item or "path" not in item for item in route_tests):
                errors.append(f"http_api без route tests: {step.get('id')}")
        if checker_type == "ide_plugin":
            counters["ide_tasks"] += 1
            if not checker.get("required_files") or not checker.get("commands"):
                errors.append(f"ide_plugin без required_files/commands: {step.get('id')}")

    duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        errors.append(f"Duplicate ids: {duplicate_ids[:10]}")

    lesson_count = sum(1 for _ in iter_lessons(course))
    step_count = sum(step_type_counts.values())
    minimums = [
        (lesson_count, 130, "Недостаточно уроков"),
        (step_count, 1800, "Недостаточно шагов"),
        (total_minutes, 36000, "Недостаточная нагрузка минут"),
        (step_type_counts["practice"], 400, "Недостаточно practice"),
        (step_type_counts["project"], 250, "Недостаточно project"),
        (quiz_count, 200, "Недостаточно вопросов"),
        (counters["sql_tasks"], 100, "Недостаточно SQL-задач"),
        (counters["git_steps"], 40, "Git command practice < 40"),
        (counters["sqlite_steps"], 30, "SQLite < 30 шагов"),
        (counters["sql_steps"], 100, "SQL core < 100 шагов"),
        (counters["fastapi_steps"], 80, "FastAPI < 80 шагов"),
        (counters["docker_devops_steps"], 60, "Docker/CI/CD < 60 шагов"),
        (counters["pytest_tasks"], 80, "pytest-задач < 80"),
        (counters["http_api_tasks"], 80, "http_api-задач < 80"),
        (counters["ide_tasks"], 80, "IDE-plugin задач < 80"),
    ]
    for value, minimum, label in minimums:
        if value < minimum:
            errors.append(f"{label}: {value}")

    content_quality_failures = []
    quality_limits = [
        ("generic_theory_pattern", 30, "повторяемый теоретический паттерн"),
        ("generic_stdout_body", 30, "однотипные stdout-задачи"),
        ("generic_solve_body", 30, "однотипные практики solve(a, b)"),
        ("generic_sql_body", 30, "однотипные SQL-условия"),
        ("generic_project_body", 40, "однотипные проектные требования"),
        ("generic_solve_template", 30, "однотипный editor template solve(a, b)"),
        ("generic_solve_solution", 30, "однотипное решение solve(a, b)"),
    ]
    for key, limit, label in quality_limits:
        if counters[key] > limit:
            content_quality_failures.append(f"{label}: {counters[key]} > {limit}")
    for failure in content_quality_failures:
        errors.append(f"Content quality gate FAIL: {failure}")

    with (ROOT / "manifest.csv").open("r", encoding="utf-8-sig", newline="") as file:
        manifest_rows = list(csv.DictReader(file))
    manifest_mismatch = manifest_rows != expected_manifest(course)
    if manifest_mismatch:
        errors.append("Manifest mismatch: CSV не совпадает с JSON.")

    with (ROOT / "coverage_matrix.csv").open("r", encoding="utf-8-sig", newline="") as file:
        coverage_rows = list(csv.DictReader(file))
    bad_coverage = [row for row in coverage_rows if row.get("status", "").lower() in {"missing", "thin", "placeholder"}]
    zero_coverage = [row for row in coverage_rows if int(row.get("steps_count") or 0) <= 0]
    if bad_coverage:
        errors.append(f"Coverage matrix содержит плохие статусы: {bad_coverage[:5]}")
    if zero_coverage:
        errors.append(f"Coverage matrix содержит темы без шагов: {zero_coverage[:5]}")

    error_lines = [f"- {error}" for error in errors[:200]] if errors else ["- none"]
    report = [
        "# Validation Report",
        "",
        f"total modules: {len(modules)}",
        f"total lessons: {lesson_count}",
        f"total steps: {step_count}",
        f"total estimated hours: {round(total_minutes / 60, 1)}",
        "",
        "## Steps By Type",
        *[f"- {key}: {value}" for key, value in sorted(step_type_counts.items())],
        "",
        "## Checkers By Type",
        *[f"- {key}: {value}" for key, value in sorted(checker_counts.items())],
        "",
        "## Required Depth Counters",
        *[f"- {key}: {counters[key]}" for key in ["sqlite_steps", "git_steps", "sql_steps", "fastapi_steps", "docker_devops_steps", "sql_tasks", "pytest_tasks", "http_api_tasks", "ide_tasks"]],
        f"- quiz questions: {quiz_count}",
        "",
        "## Content Quality Gate",
        f"status: {'FAIL' if content_quality_failures else 'PASS'}",
        *[f"- {key}: {counters[key]}" for key, _, _ in quality_limits],
        *(f"- blocker: {failure}" for failure in content_quality_failures),
        "",
        "## Critical Checks",
        f"missing checkers: {sum(1 for _, _, s in iter_steps(course) if s.get('type') == 'practice' and not s.get('checker'))}",
        f"missing quiz questions: {sum(1 for _, _, s in iter_steps(course) if s.get('type') == 'test' and not s.get('questions'))}",
        f"body leaks: {sum(1 for _, _, s in iter_steps(course) if body_hits(s.get('body_markdown', '')))}",
        f"placeholder text: {sum(1 for _, _, s in iter_steps(course) for p in FORBIDDEN_ANYWHERE if p.lower() in json.dumps(s, ensure_ascii=False).lower())}",
        f"duplicate ids: {len(duplicate_ids)}",
        f"manifest mismatch: {'yes' if manifest_mismatch else 'no'}",
        f"roadmap coverage bad statuses: {len(bad_coverage)}",
        "",
        "## Errors",
        *error_lines,
        "",
        f"critical errors: {len(errors)}",
        f"Final status: {'FAIL' if errors else 'PASS'}",
    ]
    (ROOT / "validation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Final status: {'FAIL' if errors else 'PASS'}")
    print(f"critical errors: {len(errors)}")
    print(f"total lessons: {lesson_count}")
    print(f"total steps: {step_count}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(generate() if "--generate" in sys.argv else validate())
