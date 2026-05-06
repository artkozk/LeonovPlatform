#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COURSE_FILE = ROOT / "course_import.json"

BAD_BODY_PATTERNS = [
    "??",
    "В разделе `",
    "важно следующее",
    "Когда ты встречаешь `",
    "первая часть задаёт вход",
    "Средняя часть выполняет",
    "Последняя часть фиксирует",
    "Минимальные данные для `",
    "результат должен быть наблюдаемым",
    "Перед задачей по `",
    "Этот шаг относится к уроку `",
    "проверяет действие `",
    "сравни именно этот контракт",
    "Разбор для урока `",
    "Backend-контекст для `",
    "сделать действие Git, но не проверить точный признак результата",
    "Ответь на вопросы по конкретным ситуациям урока",
    "собери конкретный результат",
    "цель шага, действие, ожидаемый результат",
]

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya",
}


def slugify(text: str, limit: int = 72) -> str:
    text = "".join(TRANSLIT.get(ch, ch) for ch in text.lower())
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:limit].strip("-") or "step"


def load_course() -> dict:
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def save_course(course: dict) -> None:
    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def iter_steps(course: dict):
    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            for step in lesson["steps"]:
                yield module, lesson, step


def has_bad_pattern(text: str) -> bool:
    return any(pattern in (text or "") for pattern in BAD_BODY_PATTERNS)


SCHEMAS = {
    "ecommerce": {
        "title": "магазин",
        "schema": """
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, active INTEGER NOT NULL, city TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, total INTEGER NOT NULL, status TEXT NOT NULL);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL);
""".strip(),
        "seed": """
INSERT INTO users VALUES (1,'Анна',1,'Казань'),(2,'Олег',0,NULL),(3,'Маша',1,'Москва');
INSERT INTO orders VALUES (1,1,1200,'paid'),(2,1,300,'new'),(3,3,800,'paid');
INSERT INTO products VALUES (1,'Book',500),(2,'Mouse',900);
""".strip(),
        "hidden_seed": """
INSERT INTO users VALUES (1,'Анна',1,'Казань'),(2,'Олег',0,NULL),(3,'Маша',1,'Москва'),(4,'Ира',1,'Казань');
INSERT INTO orders VALUES (1,1,1200,'paid'),(2,1,300,'new'),(3,3,800,'paid'),(4,4,1500,'paid');
INSERT INTO products VALUES (1,'Book',500),(2,'Mouse',900),(3,'Keyboard',1500);
""".strip(),
    },
    "library": {
        "title": "библиотека",
        "schema": """
CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL, country TEXT);
CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author_id INTEGER, published_year INTEGER NOT NULL, price INTEGER NOT NULL);
CREATE TABLE loans (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, reader TEXT NOT NULL, returned INTEGER NOT NULL);
""".strip(),
        "seed": """
INSERT INTO authors VALUES (1,'Толстой','RU'),(2,'Оруэлл','UK'),(3,'Ле Гуин','US');
INSERT INTO books VALUES (1,'Война и мир',1,1869,900),(2,'1984',2,1949,500),(3,'Волшебник Земноморья',3,1968,650),(4,'Без автора',NULL,2020,300);
INSERT INTO loans VALUES (1,1,'Анна',0),(2,2,'Олег',1),(3,3,'Маша',0);
""".strip(),
        "hidden_seed": """
INSERT INTO authors VALUES (1,'Толстой','RU'),(2,'Оруэлл','UK'),(3,'Ле Гуин','US'),(4,'Булгаков','RU');
INSERT INTO books VALUES (1,'Война и мир',1,1869,900),(2,'1984',2,1949,500),(3,'Волшебник Земноморья',3,1968,650),(4,'Без автора',NULL,2020,300),(5,'Мастер и Маргарита',4,1967,700);
INSERT INTO loans VALUES (1,1,'Анна',0),(2,2,'Олег',1),(3,3,'Маша',0),(4,5,'Ира',0);
""".strip(),
    },
    "school": {
        "title": "учебные группы",
        "schema": """
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT, active INTEGER NOT NULL);
CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, level TEXT NOT NULL);
CREATE TABLE enrollments (id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, course_id INTEGER NOT NULL, score INTEGER);
""".strip(),
        "seed": """
INSERT INTO students VALUES (1,'Анна','Казань',1),(2,'Олег',NULL,1),(3,'Маша','Москва',0);
INSERT INTO courses VALUES (1,'Python','junior'),(2,'SQL','junior'),(3,'FastAPI','middle');
INSERT INTO enrollments VALUES (1,1,1,95),(2,1,2,88),(3,2,2,NULL),(4,3,3,74);
""".strip(),
        "hidden_seed": """
INSERT INTO students VALUES (1,'Анна','Казань',1),(2,'Олег',NULL,1),(3,'Маша','Москва',0),(4,'Ира','Пермь',1);
INSERT INTO courses VALUES (1,'Python','junior'),(2,'SQL','junior'),(3,'FastAPI','middle'),(4,'Docker','middle');
INSERT INTO enrollments VALUES (1,1,1,95),(2,1,2,88),(3,2,2,NULL),(4,3,3,74),(5,4,4,91);
""".strip(),
    },
    "workflow": {
        "title": "задачи проекта",
        "schema": """
CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT NOT NULL, archived INTEGER NOT NULL);
CREATE TABLE tasks (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL, assignee TEXT);
CREATE TABLE comments (id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, author TEXT NOT NULL, body TEXT NOT NULL);
""".strip(),
        "seed": """
INSERT INTO projects VALUES (1,'Backend',0),(2,'Website',0),(3,'Archive',1);
INSERT INTO tasks VALUES (1,1,'Auth','open','Анна'),(2,1,'Tests','done',NULL),(3,2,'Landing','open','Олег');
INSERT INTO comments VALUES (1,1,'Анна','start'),(2,1,'Олег','review'),(3,3,'Маша','copy');
""".strip(),
        "hidden_seed": """
INSERT INTO projects VALUES (1,'Backend',0),(2,'Website',0),(3,'Archive',1),(4,'Mobile',0);
INSERT INTO tasks VALUES (1,1,'Auth','open','Анна'),(2,1,'Tests','done',NULL),(3,2,'Landing','open','Олег'),(4,4,'Push','open',NULL);
INSERT INTO comments VALUES (1,1,'Анна','start'),(2,1,'Олег','review'),(3,3,'Маша','copy'),(4,4,'Ира','todo');
""".strip(),
    },
    "final": {
        "title": "финальный проект",
        "schema": """
CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL, role TEXT NOT NULL);
CREATE TABLE projects (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, name TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE memberships (user_id INTEGER NOT NULL, project_id INTEGER NOT NULL, role TEXT NOT NULL, PRIMARY KEY (user_id, project_id));
CREATE TABLE tasks (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, assignee_id INTEGER, title TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE comments (id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, author_id INTEGER NOT NULL, body TEXT NOT NULL);
""".strip(),
        "seed": """
INSERT INTO users VALUES (1,'owner@example.com','owner'),(2,'dev@example.com','member'),(3,'qa@example.com','member');
INSERT INTO projects VALUES (1,1,'Care Board','active'),(2,1,'Old Board','archived');
INSERT INTO memberships VALUES (1,1,'owner'),(2,1,'developer'),(3,1,'qa');
INSERT INTO tasks VALUES (1,1,2,'API contract','open'),(2,1,NULL,'Deploy checklist','open'),(3,2,3,'Legacy cleanup','done');
INSERT INTO comments VALUES (1,1,1,'define routes'),(2,1,2,'add tests'),(3,2,3,'check deploy');
""".strip(),
        "hidden_seed": """
INSERT INTO users VALUES (1,'owner@example.com','owner'),(2,'dev@example.com','member'),(3,'qa@example.com','member'),(4,'ops@example.com','member');
INSERT INTO projects VALUES (1,1,'Care Board','active'),(2,1,'Old Board','archived'),(3,4,'Deploy Board','active');
INSERT INTO memberships VALUES (1,1,'owner'),(2,1,'developer'),(3,1,'qa'),(4,3,'ops');
INSERT INTO tasks VALUES (1,1,2,'API contract','open'),(2,1,NULL,'Deploy checklist','open'),(3,2,3,'Legacy cleanup','done'),(4,3,4,'SSL renewal','open');
INSERT INTO comments VALUES (1,1,1,'define routes'),(2,1,2,'add tests'),(3,2,3,'check deploy'),(4,4,4,'renew cert');
""".strip(),
    },
}


def schema_key_for(module: dict, lesson: dict) -> str:
    title = lesson["title"].lower()
    if module["id"] == "m05" and "финальный проект" in title:
        return "final"
    if "sqlalchemy" in title or "database session" in title or "repository" in title:
        return "workflow"
    if "sqlite" in title:
        return "library" if lesson["order"] % 2 else "workflow"
    if module["id"] == "m03":
        if lesson["order"] <= 4:
            return "ecommerce"
        if lesson["order"] <= 10:
            return "library"
        if lesson["order"] <= 18:
            return "school" if lesson["order"] % 2 else "workflow"
        if lesson["order"] <= 25:
            return "library" if lesson["order"] % 2 else "workflow"
        return "workflow"
    return "ecommerce"


def role_for_sql_step(step: dict) -> str:
    text = f"{step['id']} {step.get('title', '')}".lower()
    if "rollback" in text:
        return "rollback"
    if "commit" in text:
        return "commit"
    if "explain" in text or "индекс" in text:
        return "explain"
    if "cte" in text:
        return "cte"
    if "окно" in text or "window" in text:
        return "window"
    if "left" in text:
        return "left"
    if "join" in text or "связанные" in text:
        return "join"
    if "агрег" in text or "group" in text or "having" in text:
        return "aggregate"
    if "null" in text or "пустое" in text:
        return "null"
    if "фильтр" in text or "where" in text or "условие" in text:
        return "filter"
    return "columns"


def sql_query_for(schema_key: str, role: str) -> tuple[str, str, str]:
    if schema_key == "ecommerce":
        mapping = {
            "columns": ("выведи `id` и `name` всех пользователей по возрастанию `id`", "id, name", "SELECT id, name FROM users ORDER BY id;"),
            "filter": ("выведи активных пользователей", "id, name", "SELECT id, name FROM users WHERE active = 1 ORDER BY id;"),
            "null": ("найди пользователей без города", "id, name", "SELECT id, name FROM users WHERE city IS NULL ORDER BY id;"),
            "join": ("соедини пользователей с заказами и покажи сумму каждого заказа", "user_name, total", "SELECT users.name, orders.total FROM users JOIN orders ON orders.user_id = users.id ORDER BY orders.id;"),
            "left": ("найди пользователей без заказов через LEFT JOIN", "id, name", "SELECT users.id, users.name FROM users LEFT JOIN orders ON orders.user_id = users.id WHERE orders.id IS NULL ORDER BY users.id;"),
            "aggregate": ("посчитай количество заказов по каждому пользователю", "user_id, orders_count", "SELECT user_id, COUNT(*) FROM orders GROUP BY user_id ORDER BY user_id;"),
            "cte": ("через CTE выбери оплаченные заказы", "id, total", "WITH paid_orders AS (SELECT id, total FROM orders WHERE status = 'paid') SELECT id, total FROM paid_orders ORDER BY id;"),
            "window": ("пронумеруй заказы каждого пользователя по сумме", "user_id, total, number", "SELECT user_id, total, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS number FROM orders ORDER BY user_id, number;"),
            "commit": ("обнови статус заказа в транзакции и зафиксируй изменение", "id, status", "BEGIN; UPDATE orders SET status = 'paid' WHERE id = 2; COMMIT; SELECT id, status FROM orders ORDER BY id;"),
            "rollback": ("обнови статус заказа в транзакции и откати изменение", "id, status", "BEGIN; UPDATE orders SET status = 'paid' WHERE id = 2; ROLLBACK; SELECT id, status FROM orders ORDER BY id;"),
            "explain": ("создай индекс по городу и верни пользователей из Казани", "id, name", "CREATE INDEX idx_users_city ON users(city); SELECT id, name FROM users WHERE city = 'Казань' ORDER BY id;"),
        }
    elif schema_key == "library":
        mapping = {
            "columns": ("выведи `id` и `title` всех книг", "id, title", "SELECT id, title FROM books ORDER BY id;"),
            "filter": ("выведи книги дороже или равные 650", "id, title", "SELECT id, title FROM books WHERE price >= 650 ORDER BY id;"),
            "null": ("найди книги без автора", "id, title", "SELECT id, title FROM books WHERE author_id IS NULL ORDER BY id;"),
            "join": ("соедини книги с авторами", "author_name, book_title", "SELECT authors.name, books.title FROM books JOIN authors ON authors.id = books.author_id ORDER BY books.id;"),
            "left": ("найди книги, которые ни разу не выдавались", "id, title", "SELECT books.id, books.title FROM books LEFT JOIN loans ON loans.book_id = books.id WHERE loans.id IS NULL ORDER BY books.id;"),
            "aggregate": ("посчитай книги по каждому автору", "author_id, books_count", "SELECT author_id, COUNT(*) FROM books WHERE author_id IS NOT NULL GROUP BY author_id ORDER BY author_id;"),
            "cte": ("через CTE выбери дорогие книги", "id, title", "WITH expensive AS (SELECT id, title FROM books WHERE price >= 650) SELECT id, title FROM expensive ORDER BY id;"),
            "window": ("пронумеруй книги каждого автора по году публикации", "author_id, title, number", "SELECT author_id, title, ROW_NUMBER() OVER (PARTITION BY author_id ORDER BY published_year) AS number FROM books WHERE author_id IS NOT NULL ORDER BY author_id, number;"),
            "commit": ("зафиксируй возврат книги в транзакции", "id, returned", "BEGIN; UPDATE loans SET returned = 1 WHERE id = 1; COMMIT; SELECT id, returned FROM loans ORDER BY id;"),
            "rollback": ("откати ошибочную отметку возврата книги", "id, returned", "BEGIN; UPDATE loans SET returned = 1 WHERE id = 1; ROLLBACK; SELECT id, returned FROM loans ORDER BY id;"),
            "explain": ("создай индекс по году публикации и верни книги после 1950 года", "id, title", "CREATE INDEX idx_books_year ON books(published_year); SELECT id, title FROM books WHERE published_year >= 1950 ORDER BY id;"),
        }
    elif schema_key == "school":
        mapping = {
            "columns": ("выведи `id` и `name` всех студентов", "id, name", "SELECT id, name FROM students ORDER BY id;"),
            "filter": ("выведи активных студентов", "id, name", "SELECT id, name FROM students WHERE active = 1 ORDER BY id;"),
            "null": ("найди студентов без города", "id, name", "SELECT id, name FROM students WHERE city IS NULL ORDER BY id;"),
            "join": ("соедини студентов с курсами через enrollments", "student_name, course_title", "SELECT students.name, courses.title FROM enrollments JOIN students ON students.id = enrollments.student_id JOIN courses ON courses.id = enrollments.course_id ORDER BY enrollments.id;"),
            "left": ("найди курсы без записей", "id, title", "SELECT courses.id, courses.title FROM courses LEFT JOIN enrollments ON enrollments.course_id = courses.id WHERE enrollments.id IS NULL ORDER BY courses.id;"),
            "aggregate": ("посчитай записи на каждый курс", "course_id, enrollments_count", "SELECT course_id, COUNT(*) FROM enrollments GROUP BY course_id ORDER BY course_id;"),
            "cte": ("через CTE выбери высокие оценки", "student_id, score", "WITH high_scores AS (SELECT student_id, score FROM enrollments WHERE score >= 90) SELECT student_id, score FROM high_scores ORDER BY student_id;"),
            "window": ("пронумеруй оценки внутри каждого курса", "course_id, student_id, number", "SELECT course_id, student_id, ROW_NUMBER() OVER (PARTITION BY course_id ORDER BY score DESC) AS number FROM enrollments WHERE score IS NOT NULL ORDER BY course_id, number;"),
            "commit": ("зафиксируй изменение оценки в транзакции", "id, score", "BEGIN; UPDATE enrollments SET score = 80 WHERE id = 3; COMMIT; SELECT id, score FROM enrollments ORDER BY id;"),
            "rollback": ("откати ошибочное изменение оценки", "id, score", "BEGIN; UPDATE enrollments SET score = 80 WHERE id = 3; ROLLBACK; SELECT id, score FROM enrollments ORDER BY id;"),
            "explain": ("создай индекс по городу и верни студентов из Казани", "id, name", "CREATE INDEX idx_students_city ON students(city); SELECT id, name FROM students WHERE city = 'Казань' ORDER BY id;"),
        }
    elif schema_key == "final":
        mapping = {
            "columns": ("выведи `id` и `email` пользователей финального проекта", "id, email", "SELECT id, email FROM users ORDER BY id;"),
            "filter": ("выведи активные проекты", "id, name", "SELECT id, name FROM projects WHERE status = 'active' ORDER BY id;"),
            "null": ("найди задачи без исполнителя", "id, title", "SELECT id, title FROM tasks WHERE assignee_id IS NULL ORDER BY id;"),
            "join": ("соедини задачи с проектами", "project_name, task_title", "SELECT projects.name, tasks.title FROM tasks JOIN projects ON projects.id = tasks.project_id ORDER BY tasks.id;"),
            "left": ("найди проекты без задач", "id, name", "SELECT projects.id, projects.name FROM projects LEFT JOIN tasks ON tasks.project_id = projects.id WHERE tasks.id IS NULL ORDER BY projects.id;"),
            "aggregate": ("посчитай участников каждого проекта", "project_id, members_count", "SELECT project_id, COUNT(*) FROM memberships GROUP BY project_id ORDER BY project_id;"),
            "cte": ("через CTE выбери открытые задачи активных проектов", "id, title", "WITH open_tasks AS (SELECT tasks.id, tasks.title FROM tasks JOIN projects ON projects.id = tasks.project_id WHERE tasks.status = 'open' AND projects.status = 'active') SELECT id, title FROM open_tasks ORDER BY id;"),
            "window": ("пронумеруй задачи внутри проекта", "project_id, title, number", "SELECT project_id, title, ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY id) AS number FROM tasks ORDER BY project_id, number;"),
            "commit": ("зафиксируй закрытие задачи в транзакции", "id, status", "BEGIN; UPDATE tasks SET status = 'done' WHERE id = 1; COMMIT; SELECT id, status FROM tasks ORDER BY id;"),
            "rollback": ("откати ошибочное закрытие задачи", "id, status", "BEGIN; UPDATE tasks SET status = 'done' WHERE id = 1; ROLLBACK; SELECT id, status FROM tasks ORDER BY id;"),
            "explain": ("создай индекс по статусу задач и верни открытые задачи", "id, title", "CREATE INDEX idx_tasks_status ON tasks(status); SELECT id, title FROM tasks WHERE status = 'open' ORDER BY id;"),
        }
    else:
        mapping = {
            "columns": ("выведи `id` и `title` всех задач", "id, title", "SELECT id, title FROM tasks ORDER BY id;"),
            "filter": ("выведи открытые задачи", "id, title", "SELECT id, title FROM tasks WHERE status = 'open' ORDER BY id;"),
            "null": ("найди задачи без исполнителя", "id, title", "SELECT id, title FROM tasks WHERE assignee IS NULL ORDER BY id;"),
            "join": ("соедини проекты с задачами", "project_name, task_title", "SELECT projects.name, tasks.title FROM tasks JOIN projects ON projects.id = tasks.project_id ORDER BY tasks.id;"),
            "left": ("найди проекты без задач", "id, name", "SELECT projects.id, projects.name FROM projects LEFT JOIN tasks ON tasks.project_id = projects.id WHERE tasks.id IS NULL ORDER BY projects.id;"),
            "aggregate": ("посчитай задачи по каждому проекту", "project_id, tasks_count", "SELECT project_id, COUNT(*) FROM tasks GROUP BY project_id ORDER BY project_id;"),
            "cte": ("через CTE выбери открытые задачи", "id, title", "WITH open_tasks AS (SELECT id, title FROM tasks WHERE status = 'open') SELECT id, title FROM open_tasks ORDER BY id;"),
            "window": ("пронумеруй задачи внутри каждого проекта", "project_id, title, number", "SELECT project_id, title, ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY id) AS number FROM tasks ORDER BY project_id, number;"),
            "commit": ("зафиксируй закрытие задачи в транзакции", "id, status", "BEGIN; UPDATE tasks SET status = 'done' WHERE id = 1; COMMIT; SELECT id, status FROM tasks ORDER BY id;"),
            "rollback": ("откати ошибочное закрытие задачи", "id, status", "BEGIN; UPDATE tasks SET status = 'done' WHERE id = 1; ROLLBACK; SELECT id, status FROM tasks ORDER BY id;"),
            "explain": ("создай индекс по статусу и верни открытые задачи", "id, title", "CREATE INDEX idx_tasks_status ON tasks(status); SELECT id, title FROM tasks WHERE status = 'open' ORDER BY id;"),
        }
    return mapping.get(role, mapping["columns"])


def strip_sql_comments(sql: str) -> str:
    return re.sub(r"/\*.*?\*/", "", sql, flags=re.S).strip()


def execute_sql(schema: str, seed: str, sql: str) -> list[list]:
    conn = sqlite3.connect(":memory:")
    conn.isolation_level = None
    try:
        conn.executescript(schema)
        conn.executescript(seed)
        body = strip_sql_comments(sql)
        parts = [part.strip() for part in body.split(";") if part.strip()]
        if not parts:
            return []
        for part in parts[:-1]:
            conn.execute(part)
        cur = conn.execute(parts[-1])
        return [list(row) for row in cur.fetchall()]
    finally:
        conn.close()


def update_sql_step(module: dict, lesson: dict, step: dict) -> None:
    checker = step["checker"]
    schema_key = schema_key_for(module, lesson)
    schema = SCHEMAS[schema_key]
    role = role_for_sql_step(step)
    task, columns, query = sql_query_for(schema_key, role)
    comment = f"/* {lesson['title']} / {step['title']} */"
    solution = f"{comment}\n{query}\n"
    public_rows = execute_sql(schema["schema"], schema["seed"], solution)
    hidden_rows = execute_sql(schema["schema"], schema["hidden_seed"], solution)
    checker["schema_sql"] = schema["schema"]
    checker["seed_sql"] = schema["seed"]
    checker["public_tests"] = [{"name": role, "expected_rows": public_rows, "compare": "ordered_rows"}]
    checker["hidden_tests"] = [{"seed_sql": schema["hidden_seed"], "expected_rows": hidden_rows, "compare": "ordered_rows"}]
    checker["scenario_id"] = f"{step['id']}_{schema_key}_{role}"
    step["solution_code"] = solution
    step["editor_initial_code"] = "-- напиши запрос ниже\n"
    step["body_markdown"] = f"""**Коротко:** {task}.

### Условие
Работаешь с учебной базой `{schema["title"]}`. Напиши SQL-запрос: {task}. Верни только колонки `{columns}` и задай порядок строк явно.

### Схема
Проверка создаст таблицы из этого урока: {schema["schema"].splitlines()[0]} ...

### Вход
Данные уже загружены в SQLite перед запуском твоего запроса.

### Выход
Таблица с колонками `{columns}`. Порядок должен быть стабильным, поэтому используй `ORDER BY`, если результат содержит несколько строк.

### Пример формы
```sql
SELECT ...
```

### Что проверить
Сначала назови таблицу-источник. Потом назови условие отбора или соединения. В конце проверь, что запрос не возвращает лишние колонки и не зависит от случайного порядка строк.
"""


def profile_for(lesson: dict) -> dict:
    title = lesson["title"]
    low = title.lower()
    if "магические" in low:
        return {
            "kind": "python",
            "concept": "Магические методы позволяют объекту вести себя как встроенный тип: красиво печататься, сравниваться, участвовать в сортировке или работать как коллекция.",
            "why": "Без них приходится писать отдельные функции вроде `money_equals(a, b)`. С ними контракт живёт внутри класса, и код чтения становится проще.",
            "code": "class Money:\n    def __init__(self, amount, currency):\n        self.amount = amount\n        self.currency = currency\n\n    def __repr__(self):\n        return f\"Money({self.amount}, {self.currency!r})\"\n\n    def __eq__(self, other):\n        return isinstance(other, Money) and (self.amount, self.currency) == (other.amount, other.currency)",
            "walk": "`__repr__` нужен для понятного отображения объекта. `__eq__` определяет равенство двух объектов и обязательно проверяет тип второго значения.",
            "important": "Сравнивай все поля, которые определяют смысл объекта. Деньги в разных валютах не равны, даже если сумма совпала.",
            "mistake": "Частая ошибка — сравнить только `amount` и случайно признать `10 RUB` равным `10 USD`.",
            "check": "Что вернёт `Money(10, 'RUB') == Money(10, 'USD')` в примере выше?",
        }
    if "протокол" in low:
        return {
            "kind": "python",
            "concept": "Протокол описывает поведение объекта без привязки к конкретному классу. Если объект имеет нужные методы, его можно использовать в функции.",
            "why": "Так сервис зависит от маленького контракта, а не от тяжёлой реализации. Это удобно для тестов, адаптеров и внешних API.",
            "code": "from typing import Protocol\n\nclass Sender(Protocol):\n    def send(self, target: str, text: str) -> bool: ...\n\ndef notify(sender: Sender, email: str) -> bool:\n    return sender.send(email, \"hello\")",
            "walk": "`Sender` требует метод `send`. Функция `notify` не знает, SMTP это, мок или запись в файл; ей важен только метод.",
            "important": "Protocol хорош там, где нужен минимальный интерфейс. Не добавляй в него методы, которые функция не использует.",
            "mistake": "Частая ошибка — наследоваться от большого базового класса там, где хватило бы одного метода в Protocol.",
            "check": "Какой метод должен быть у объекта, чтобы его можно было передать в `notify`?",
        }
    if any(x in low for x in ["ооп", "инкапс", "композ", "наслед", "полиморф", "абстрак", "dataclass"]):
        return {
            "kind": "python",
            "concept": f"{title} помогает держать данные и поведение рядом. Объект хранит состояние, а методы меняют его по понятным правилам.",
            "why": "В backend это снижает количество разрозненных словарей и проверок. Правило можно поместить в класс и покрыть тестом.",
            "code": "class Task:\n    def __init__(self, title):\n        self.title = title.strip()\n        self.done = False\n\n    def mark_done(self):\n        self.done = True\n\n    def is_open(self):\n        return not self.done",
            "walk": "`__init__` создаёт начальное состояние. `mark_done` меняет объект. `is_open` возвращает ответ, не меняя данные.",
            "important": "Метод должен делать одно действие. Если метод и меняет данные, и печатает, и читает файл, его трудно тестировать.",
            "mistake": "Частая ошибка — хранить состояние в глобальной переменной вместо поля объекта.",
            "check": "Какая строка меняет состояние задачи, а какая только читает его?",
        }
    if "typing" in low or "mypy" in low:
        return {
            "kind": "python",
            "concept": f"{title} делает контракт функции явным: какие типы приходят на вход и какой тип возвращается.",
            "why": "Аннотации не заменяют тесты, но помогают раньше увидеть ошибку: например, когда `None` передали туда, где нужна строка.",
            "code": "from typing import Optional\n\ndef normalize_email(email: Optional[str]) -> str:\n    if email is None:\n        return \"\"\n    return email.strip().lower()",
            "walk": "`Optional[str]` означает `str | None`. Перед вызовом строковых методов нужно отдельно обработать `None`.",
            "important": "Типы должны отражать реальность. Если функция иногда возвращает `None`, это нужно написать в аннотации.",
            "mistake": "Частая ошибка — поставить `str`, а потом вернуть `None` в одной из веток.",
            "check": "Почему `email.strip()` нельзя вызвать до проверки `email is None`?",
        }
    if "pytest" in low:
        return {
            "kind": "python",
            "concept": f"{title} проверяет поведение кода через вход, действие и `assert`.",
            "why": "Тест фиксирует ожидание. После правки кода ты видишь, что сломалось: расчёт, ошибка, формат ответа или работа с файлом.",
            "code": "import pytest\n\n\ndef parse_age(value: str) -> int:\n    age = int(value)\n    if age < 0:\n        raise ValueError(\"age must be positive\")\n    return age\n\n\ndef test_parse_age_error():\n    with pytest.raises(ValueError):\n        parse_age(\"-1\")",
            "walk": "Тест вызывает функцию с плохим входом и проверяет, что ошибка действительно возникает.",
            "important": "Один тест должен проверять один заметный контракт. Тогда падение быстро показывает причину.",
            "mistake": "Частая ошибка — написать тест без `assert` или проверить только счастливый путь.",
            "check": "Что именно проверяет блок `pytest.raises`?",
        }
    if any(x in low for x in ["алгорит", "массив", "hash", "stack", "queue", "deque", "сорт", "binary"]):
        return {
            "kind": "python",
            "concept": f"{title} учит выбирать структуру данных и оценивать стоимость решения.",
            "why": "На маленьком списке разница незаметна. На большом входе вложенный цикл или неверная структура превращают быстрый endpoint в медленный.",
            "code": "def has_user_id(users, target_id):\n    ids = {user[\"id\"] for user in users}\n    return target_id in ids",
            "walk": "Сначала один проход строит множество id. Потом проверка `in` для множества обычно выполняется быстро.",
            "important": "Смотри не только на результат, но и на количество проходов по данным.",
            "mistake": "Частая ошибка — для каждого поиска заново проходить весь список.",
            "check": "Когда выгоднее заранее построить `set`: для одной проверки или для сотен проверок?",
        }
    if any(x in low for x in ["threading", "multiprocessing", "asyncio"]):
        return {
            "kind": "python",
            "concept": f"{title} нужен, когда программа делает несколько независимых действий: ждёт сеть, обрабатывает задачи или считает тяжёлые данные.",
            "why": "Потоки подходят для ожидания, процессы — для CPU-bound работы, asyncio — для большого числа сетевых операций без лишних потоков.",
            "code": "import asyncio\n\nasync def fetch_name(user_id):\n    await asyncio.sleep(0.01)\n    return f\"user-{user_id}\"\n\nasync def main():\n    return await asyncio.gather(fetch_name(1), fetch_name(2))",
            "walk": "`async def` создаёт coroutine. `await` отдаёт управление, пока операция ждёт. `gather` запускает несколько coroutine вместе.",
            "important": "Не смешивай модели наугад. Блокирующий код внутри async-функции остановит весь event loop.",
            "mistake": "Частая ошибка — забыть `await` и получить coroutine object вместо результата.",
            "check": "Почему `asyncio.sleep` не блокирует выполнение так же, как обычный `time.sleep`?",
        }
    if "sql" in low or "sqlite" in low or "индекс" in low or "схем" in low:
        return {
            "kind": "sql",
            "concept": f"{title} работает с таблицами как с набором строк. Запрос должен явно описывать источник, условие, связи и порядок результата.",
            "why": "Без явного условия или `ORDER BY` результат легко станет случайным. На реальной базе это приводит к неверным отчётам и плавающим тестам.",
            "code": "SELECT users.name, orders.total\nFROM users\nJOIN orders ON orders.user_id = users.id\nWHERE orders.status = 'paid'\nORDER BY orders.id;",
            "walk": "`FROM` выбирает основную таблицу. `JOIN ... ON` связывает строки по ключу. `WHERE` оставляет нужные строки. `ORDER BY` фиксирует порядок.",
            "important": "У каждого JOIN должно быть условие связи. Иначе получишь перемножение строк.",
            "mistake": "Частая ошибка — поставить фильтр по правой таблице после LEFT JOIN и случайно превратить его в INNER JOIN.",
            "check": "Какая часть запроса отвечает за связь пользователей и заказов?",
        }
    if "fastapi" in low or "response_model" in low or "httpexception" in low or "router" in low or "depends" in low or "auth" in low:
        return {
            "kind": "python",
            "concept": f"{title} строит HTTP-контракт: метод, путь, входные данные, статус и JSON-ответ.",
            "why": "Клиенту не важно, как устроен код внутри. Клиенту нужен стабильный ответ на конкретный запрос.",
            "code": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\"}",
            "walk": "`@app.get('/health')` связывает GET-запрос с функцией. Возвращаемый `dict` FastAPI отдаёт как JSON.",
            "important": "Путь и метод должны совпадать с контрактом буквально. `/health` и `/api/health` — разные endpoints.",
            "mistake": "Частая ошибка — напечатать ответ через `print`, хотя endpoint должен вернуть значение.",
            "check": "Что изменится, если заменить `@app.get` на `@app.post`?",
        }
    if "sqlalchemy" in low or "alembic" in low or "database" in low or "repository" in low:
        return {
            "kind": "python",
            "concept": f"{title} отделяет работу с базой от route layer. Engine подключается к базе, session держит транзакцию, model описывает таблицу.",
            "why": "Так бизнес-код не собирает SQL-строки вручную и легче тестируется на временной базе.",
            "code": "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\nclass Base(DeclarativeBase):\n    pass\n\nclass Task(Base):\n    __tablename__ = \"tasks\"\n    id: Mapped[int] = mapped_column(primary_key=True)\n    title: Mapped[str]",
            "walk": "`Base` хранит metadata. `Task` описывает таблицу. Поля класса становятся колонками.",
            "important": "Session нужно закрывать или отдавать через dependency, иначе соединения будут зависать.",
            "mistake": "Частая ошибка — делать commit внутри каждой мелкой функции и ломать общую транзакцию.",
            "check": "Где в примере задаётся имя таблицы?",
        }
    if any(x in low for x in ["docker", "compose", "container", "ci/cd", "github actions", "gitlab"]):
        return {
            "kind": "bash",
            "concept": f"{title} делает запуск приложения воспроизводимым: одинаковые файлы сборки, окружение, команды проверки и сетевые зависимости.",
            "why": "Если проект запускается только на одной машине, его нельзя безопасно передать команде или развернуть на сервере.",
            "code": "FROM python:3.12-slim\nWORKDIR /app\nCOPY pyproject.toml poetry.lock ./\nRUN pip install poetry && poetry install --only main\nCOPY . .\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\"]",
            "walk": "`FROM` выбирает базовый образ. `WORKDIR` задаёт каталог. `COPY` переносит файлы. `CMD` описывает запуск контейнера.",
            "important": "Не копируй `.env` и виртуальное окружение в image. Для этого нужен `.dockerignore`.",
            "mistake": "Частая ошибка — держать секреты прямо в Dockerfile или workflow.",
            "check": "Какая строка задаёт команду запуска приложения?",
        }
    if any(x in low for x in ["ai", "prompt", "rag", "embedding", "vector", "langchain", "langgraph", "вайб"]):
        return {
            "kind": "python",
            "concept": f"{title} добавляет AI в backend как обычную внешнюю зависимость: есть вход, таймаут, ответ, логирование и обработка ошибки.",
            "why": "Нельзя строить автопроверку на платном провайдере. Для обучения используется mock provider, чтобы поведение было повторяемым.",
            "code": "class MockAIProvider:\n    def complete(self, messages):\n        if not messages:\n            raise ValueError(\"messages required\")\n        return {\"answer\": \"ok\", \"source\": \"mock\"}",
            "walk": "Provider получает список сообщений и возвращает структурированный ответ. Ошибка на пустом входе делает контракт явным.",
            "important": "AI не должен видеть секреты, скрытые ответы и внутренние рубрики. В коде фиксируй timeout и формат ответа.",
            "mistake": "Частая ошибка — сразу доверять тексту модели без схемы и проверки источников.",
            "check": "Почему mock provider лучше для автопроверки, чем реальный платный API?",
        }
    if "финальный проект" in low:
        gate = title.split(":", 1)[-1].strip()
        return {
            "kind": "text",
            "concept": f"Gate `{gate}` превращает большую работу в проверяемый этап. На каждом этапе есть артефакт, критерии pass/fail и отрицательный путь.",
            "why": "Финальный проект нельзя проверять одной финальной кнопкой. Ошибка в схеме БД или API-контракте должна всплыть до деплоя.",
            "code": "Goal: описать контракт API\nDeliverable: openapi.yaml и README\nPass/Fail: есть 401 для закрытого route, 201 для создания задачи, 404 для отсутствующей задачи",
            "walk": "`Goal` объясняет цель gate. `Deliverable` называет файл или работающий endpoint. `Pass/Fail` убирает спорность проверки.",
            "important": "Каждый gate должен сдавать то, что можно открыть, запустить или проверить командой.",
            "mistake": "Частая ошибка — написать общую заметку без конкретного файла, route, команды или критерия отказа.",
            "check": "Какой артефакт докажет, что gate готов: текст обещания или файл с проверяемым контрактом?",
        }
    return {
        "kind": "python",
        "concept": f"{title} вводит новый приём, который нужно сразу применить в маленьком воспроизводимом примере.",
        "why": "Новый навык должен быть виден в коде, команде или файле. Иначе его нельзя проверить.",
        "code": "def normalize_title(title: str) -> str:\n    cleaned = title.strip()\n    return cleaned if cleaned else \"Untitled\"",
        "walk": "Функция получает строку, убирает пробелы и возвращает запасное значение для пустого заголовка.",
        "important": "Сначала обработай граничный вход, потом обычный. Так код не падает на пустом значении.",
        "mistake": "Частая ошибка — проверить только красивый пример и забыть пустую строку.",
        "check": "Что вернёт функция для строки из трёх пробелов?",
    }


def theory_body(profile: dict, lesson_title: str, step_order: int) -> str:
    lang = "sql" if profile["kind"] == "sql" else "bash" if profile["kind"] == "bash" else "text" if profile["kind"] == "text" else "python"
    if step_order == 1:
        return f"""### Что это
{profile["concept"]}

### Зачем это нужно
{profile["why"]}

### Минимальный код
```{lang}
{profile["code"]}
```

### Как читать пример
{profile["walk"]}

### Что здесь важно
{profile["important"]}

### Частая ошибка
{profile["mistake"]}

### Проверь себя
{profile["check"]}
"""
    return f"""### Разбор перед практикой
Сначала найди в примере входные данные. Потом найди строку, где выполняется новое действие из темы `{lesson_title}`. После этого назови результат, который можно проверить запуском.

```{lang}
{profile["code"]}
```

### Пошагово
1. Вход задаёт начальное состояние.
2. Основная строка применяет новый приём урока.
3. Последняя часть возвращает или показывает результат без лишних побочных действий.

### Мини-диагностика
{profile["important"]} Если пример кажется понятным, измени одно значение во входе и заранее предскажи новый результат.

### Ошибка, которую нужно поймать
{profile["mistake"]}

### Перед задачей
Ответь себе: какой вход принимает код, что именно меняется и какой результат должен увидеть тест или команда запуска.
"""


def clean_body_text(body: str) -> str:
    body = body or ""
    body = re.sub(r"\n+### Граница задачи[\s\S]*$", "", body).rstrip()
    body = body.replace("Если  ?? `", "Если проверка `")
    body = body.replace("Если ?? `", "Если проверка `")
    body = body.replace("??", "проверка")
    body = body.replace("Ответь на вопросы по конкретным ситуациям урока.", "Проверь понимание перед практикой.")
    body = body.replace("Контекст именно этого шага:", "Фокус шага:")
    return body


def topic_terms(title: str) -> list[str]:
    low = title.lower()
    if "docker" in low:
        return ["Dockerfile", "FROM", "CMD"]
    if "compose" in low:
        return ["docker-compose", "services", "healthcheck"]
    if "ci/cd" in low:
        return ["workflow", "pytest", "image"]
    if "fastapi" in low or "api" in low:
        return ["route", "status", "JSON"]
    if "sql" in low or "sqlite" in low:
        return ["SELECT", "WHERE", "ORDER BY"]
    if "pytest" in low:
        return ["pytest", "assert", "edge"]
    if "typing" in low:
        return ["type", "None", "contract"]
    if "git" in low:
        return ["branch", "commit", "status"]
    if "ai" in low or "rag" in low:
        return ["provider", "schema", "timeout"]
    if "финальный проект" in low:
        return ["Goal", "Deliverable", "Pass/Fail"]
    return ["input", "action", "edge"]


def project_paths(module: dict, lesson: dict, step: dict) -> tuple[list[str], list[dict], str]:
    lesson_slug = slugify(lesson["title"], 48)
    step_slug = slugify(step["title"], 32)
    artifact = f"artifacts/{lesson['id']}_{step['order']}_result.txt"
    title = lesson["title"]
    low = title.lower()
    terms = topic_terms(title)
    if module["id"] == "m02" or "pytest" in low:
        source = f"src/{lesson_slug}/{step_slug}.py"
        spec = f"checks/{lesson_slug}/{step_slug}_notes.md"
        files = [source, spec, artifact]
        commands = [
            {"cmd": f"test -s {source}", "expect_exit_code": 0},
            {"cmd": f"test -s {spec}", "expect_exit_code": 0},
            {"cmd": f"grep -E \"{terms[0]}|{terms[1]}|{terms[2]}\" {spec}", "expect_exit_code": 0},
        ]
        body = f"""**Коротко:** собери маленькую лабу по теме `{title}`.

### Условие
Создай файл `{source}` и опиши в нём один рабочий пример из урока. Рядом создай `{spec}`: перечисли вход, действие, обычный случай и крайний случай. В `{artifact}` запиши команду запуска и фактический результат.

### Что сдать
Три файла должны быть не пустыми. В описании должны быть слова `{terms[0]}`, `{terms[1]}` или `{terms[2]}`, чтобы было видно, что ты работал именно с этой темой.

### Что проверить
Запусти пример локально. Если меняешь вход, результат должен меняться предсказуемо. Не ограничивайся пересказом теории: в файле с кодом должно быть действие, которое можно выполнить.
"""
        return files, commands, body
    if "fastapi" in low or "api" in low or "auth" in low:
        source = f"app/{lesson_slug}_{step_slug}.py"
        spec = f"checks/{lesson_slug}_{step_slug}.http.md"
        files = [source, spec, artifact]
        commands = [
            {"cmd": f"test -s {source}", "expect_exit_code": 0},
            {"cmd": f"grep -E \"@app|@router|FastAPI\" {source}", "expect_exit_code": 0},
            {"cmd": f"grep -E \"status|JSON|route|HTTP\" {spec}", "expect_exit_code": 0},
        ]
        body = f"""**Коротко:** зафиксируй HTTP-контракт по теме `{title}`.

### Условие
Создай `{source}` с минимальным FastAPI endpoint из урока. В `{spec}` запиши method, path, ожидаемый status code, JSON-форму ответа и один ошибочный запрос. В `{artifact}` сохрани команду запуска или curl-запрос.

### Что сдать
Endpoint должен быть виден в коде через `@app` или `@router`. В описании должны быть route, status и JSON.

### Что проверить
Сверь path буквально. Если условие говорит `/tasks`, endpoint `/api/tasks` не подходит.
"""
        return files, commands, body
    if "docker" in low or "compose" in low or "ci/cd" in low or "deploy" in low:
        source = "Dockerfile" if "dockerfile" in low else f"deploy/{lesson_slug}_{step_slug}.md"
        extra = ".github/workflows/ci.yml" if "ci/cd" in low else f"deploy/{lesson_slug}_{step_slug}.checklist.md"
        files = [source, extra, artifact]
        commands = [
            {"cmd": f"test -s {source}", "expect_exit_code": 0},
            {"cmd": f"test -s {extra}", "expect_exit_code": 0},
            {"cmd": f"grep -E \"Dockerfile|compose|pytest|healthcheck|rollback|CMD|FROM\" {source} {extra}", "expect_exit_code": 0},
        ]
        body = f"""**Коротко:** собери воспроизводимый инфраструктурный артефакт по теме `{title}`.

### Условие
Создай `{source}` и `{extra}`. Опиши команду запуска, проверку результата, переменные окружения и способ отката или диагностики. В `{artifact}` запиши, что именно запускал и какой результат получил.

### Что сдать
Файлы должны быть не пустыми и содержать конкретные команды или ключи конфигурации: `FROM`, `CMD`, `services`, `pytest`, `healthcheck` или `rollback` по смыслу урока.

### Что проверить
Другой разработчик должен понять, какую команду выполнить и какой признак успешного результата увидеть.
"""
        return files, commands, body
    if "sql" in low or "sqlite" in low or "схем" in low or "индекс" in low:
        source = f"sql/{lesson_slug}_{step_slug}.sql"
        spec = f"checks/{lesson_slug}_{step_slug}.md"
        files = [source, spec, artifact]
        commands = [
            {"cmd": f"test -s {source}", "expect_exit_code": 0},
            {"cmd": f"grep -E \"SELECT|JOIN|CREATE|BEGIN|ORDER BY|INDEX\" {source}", "expect_exit_code": 0},
            {"cmd": f"grep -E \"input|output|edge|schema\" {spec}", "expect_exit_code": 0},
        ]
        body = f"""**Коротко:** оформи SQL-решение по теме `{title}` как файл, который можно повторить.

### Условие
Создай `{source}` с запросом или DDL из урока. В `{spec}` опиши таблицы, ожидаемые колонки результата и один крайний случай: пустой результат, `NULL`, дубль строки, откат транзакции или отсутствие связи.

### Что сдать
SQL-файл должен содержать конкретный оператор: `SELECT`, `JOIN`, `CREATE`, `BEGIN`, `ORDER BY` или `INDEX` по смыслу урока. В `{artifact}` запиши команду запуска через SQLite.

### Что проверить
Запрос должен быть читаемым без соседних уроков: таблицы, условие и порядок результата должны быть названы явно.
"""
        return files, commands, body
    if "финальный проект" in low:
        gate = title.split(":", 1)[-1].strip()
        source = f"docs/final_project/{lesson_slug}_{step_slug}.md"
        files = [source, artifact]
        commands = [
            {"cmd": f"test -s {source}", "expect_exit_code": 0},
            {"cmd": f"grep -F \"Pass/Fail\" {source}", "expect_exit_code": 0},
            {"cmd": f"grep -E \"Goal|Deliverable|Risk|Command|Route|File\" {source}", "expect_exit_code": 0},
        ]
        body = f"""**Коротко:** подготовь gate `{gate}` для финального проекта.

### Условие
Создай `{source}`. В файле должны быть разделы `Goal`, `Deliverable`, `Pass/Fail`, `Risk` и `How to check`. Назови конкретный файл, route, команду или конфигурацию, по которой ментор проверит gate.

### Что сдать
Документ должен объяснять, что уже готово, как это проверить и какой отрицательный путь учтён. В `{artifact}` запиши короткий итог проверки.

### Что проверить
Если gate нельзя проверить командой, файлом, route или критерием pass/fail, он ещё не готов.
"""
        return files, commands, body
    source = f"artifacts/{lesson['id']}_{step['order']}_work.md"
    files = [source, artifact]
    commands = [
        {"cmd": f"test -s {source}", "expect_exit_code": 0},
        {"cmd": f"grep -E \"input|action|edge|result\" {source}", "expect_exit_code": 0},
    ]
    body = f"""**Коротко:** собери рабочий пример по теме `{title}`.

### Условие
Создай `{source}`. Опиши вход, действие, результат и крайний случай. В `{artifact}` запиши команду или шаг, которым ты проверил работу.

### Что сдать
Файлы должны быть не пустыми и относиться к текущему уроку.

### Что проверить
Материал должен помогать повторить действие, а не просто пересказывать определение.
"""
    return files, commands, body


def strengthen_hands_on_step(module: dict, lesson: dict, step: dict) -> None:
    body = step.get("body_markdown", "")
    if "собери конкретный результат" not in body and "цель шага, действие, ожидаемый результат" not in body:
        return
    files, commands, new_body = project_paths(module, lesson, step)
    checker = step.setdefault("checker", {"type": "ide_plugin"})
    checker["type"] = "ide_plugin"
    checker["required_files"] = files
    checker["commands"] = commands
    checker.setdefault("git_checks", {"must_have_clean_worktree": True, "forbidden_untracked_files": True})
    checker["scenario_id"] = f"{step['id']}_{slugify(lesson['title'])}_{step['order']}"
    checker["hidden_tests"] = commands[:]
    step["body_markdown"] = new_body
    step["ai_review_config"] = {
        "enabled": True,
        "rubric": [
            "есть конкретный файл или команда",
            "виден навык текущего урока",
            "описан крайний случай",
            "результат можно повторить без устного объяснения",
        ],
    }


def fix_http_ids(lesson: dict, step: dict) -> None:
    checker = step.get("checker") or {}
    if checker.get("type") != "http_api":
        return
    public = checker.get("public_tests") or []
    if not public:
        return
    method = public[0].get("method", "").lower()
    path = public[0].get("path", "")
    slug = slugify(f"{method}-{path}")
    step["id"] = f"{lesson['id']}_s{int(step['order']):03d}_{slug}"


def update_reports(course: dict) -> None:
    rows = []
    for module, lesson, step in iter_steps(course):
        rows.append({
            "module_order": module["order"],
            "module_title": module["title"],
            "lesson_order": lesson["order"],
            "lesson_title": lesson["title"],
            "step_order": step["order"],
            "step_title": step["title"],
            "step_type": step["type"],
            "checker_type": (step.get("checker") or {}).get("type", ""),
            "xp": step["xp"],
            "difficulty": step["difficulty"],
            "estimated_minutes": step["estimated_minutes"],
        })
    with (ROOT / "manifest.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    coverage_rows = []
    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            checkers = sorted({(step.get("checker") or {}).get("type", "") for step in lesson["steps"] if step.get("checker")})
            coverage_rows.append({
                "roadmap_topic": lesson["title"],
                "module": module["title"],
                "lesson": lesson["title"],
                "steps_count": len(lesson["steps"]),
                "practice_count": sum(1 for step in lesson["steps"] if step["type"] == "practice"),
                "project_count": sum(1 for step in lesson["steps"] if step["type"] == "project"),
                "checker_types": "|".join(checkers),
                "status": "covered",
            })
    with (ROOT / "coverage_matrix.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(coverage_rows[0].keys()))
        writer.writeheader()
        writer.writerows(coverage_rows)

    preview = ["# Course preview", ""]
    course_map = ["# Course map", ""]
    for module in course["course"]["modules"]:
        preview += [f"# {module['title']}", ""]
        course_map += [f"## {module['title']}", ""]
        for lesson in module["lessons"]:
            types = Counter(step["type"] for step in lesson["steps"])
            checkers = Counter((step.get("checker") or {}).get("type", "none") for step in lesson["steps"] if step.get("checker"))
            course_map.append(
                f"- {lesson['order']}. {lesson['title']}: {len(lesson['steps'])} шагов; "
                f"типы {dict(types)}; проверки {dict(checkers)}; нагрузка {lesson.get('estimated_hours', 0)} ч."
            )
            preview += [f"## {lesson['order']}. {lesson['title']}", ""]
            for step in lesson["steps"]:
                preview += [f"### {step['order']}. {step['title']} [{step['type']}]", "", step.get("body_markdown", ""), ""]
        course_map.append("")
    (ROOT / "course_preview.md").write_text("\n".join(preview), encoding="utf-8")
    (ROOT / "course_map.md").write_text("\n".join(course_map), encoding="utf-8")


def independent_audit(course: dict) -> dict:
    stats = Counter()
    examples = defaultdict(list)
    sql_schemas = Counter()
    project_artifact = 0
    for module, lesson, step in iter_steps(course):
        body = step.get("body_markdown", "")
        for pattern in BAD_BODY_PATTERNS:
            if pattern in body:
                stats[f"pattern:{pattern}"] += 1
                if len(examples[pattern]) < 5:
                    examples[pattern].append(step["id"])
        checker = step.get("checker") or {}
        if checker.get("type") == "sql_query":
            sql_schemas[checker.get("schema_sql", "")] += 1
        if "собери конкретный результат" in body or "цель шага, действие, ожидаемый результат" in body:
            project_artifact += 1
    return {"bad_patterns": stats, "examples": examples, "sql_schema_count": len(sql_schemas), "project_artifact": project_artifact}


def write_quality_audit(audit: dict) -> None:
    lines = [
        "# Strict quality audit",
        "",
        f"- bad template/corruption pattern hits: {sum(audit['bad_patterns'].values())}",
        f"- distinct SQL schemas: {audit['sql_schema_count']}",
        f"- old generic artifact tasks: {audit['project_artifact']}",
        "",
        "## Pattern Examples",
    ]
    if audit["bad_patterns"]:
        for pattern, count in audit["bad_patterns"].items():
            lines.append(f"- `{pattern}`: {count}; examples: {', '.join(audit['examples'][pattern])}")
    else:
        lines.append("- none")
    status = "PASS" if not audit["bad_patterns"] and audit["sql_schema_count"] >= 4 and audit["project_artifact"] == 0 else "FAIL"
    lines += ["", "## Final Status", f"- {status}"]
    (ROOT / "strict_quality_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    course = load_course()
    rewritten_theory = 0
    cleaned_steps = 0
    rewritten_sql = 0
    strengthened_projects = 0
    fixed_http_ids = 0
    for module, lesson, step in iter_steps(course):
        original_body = step.get("body_markdown", "")
        if step["type"] == "theory" and has_bad_pattern(original_body):
            profile = profile_for(lesson)
            step["body_markdown"] = theory_body(profile, lesson["title"], 1 if step["order"] == 1 else 2)
            step["admin_notes"] = (step.get("admin_notes", "") + " strict_quality_rewrite").strip()
            rewritten_theory += 1
        elif step["type"] in {"practice", "project", "test", "summary"}:
            cleaned = clean_body_text(original_body)
            if cleaned != original_body:
                step["body_markdown"] = cleaned
                cleaned_steps += 1
        if (step.get("checker") or {}).get("type") == "sql_query":
            update_sql_step(module, lesson, step)
            rewritten_sql += 1
        if step["type"] in {"practice", "project"}:
            before = step.get("body_markdown", "")
            strengthen_hands_on_step(module, lesson, step)
            if step.get("body_markdown", "") != before:
                strengthened_projects += 1
        before_id = step["id"]
        fix_http_ids(lesson, step)
        if step["id"] != before_id:
            fixed_http_ids += 1
    save_course(course)
    update_reports(course)
    audit = independent_audit(course)
    write_quality_audit(audit)
    print(f"rewritten_theory={rewritten_theory}")
    print(f"cleaned_steps={cleaned_steps}")
    print(f"rewritten_sql={rewritten_sql}")
    print(f"strengthened_projects={strengthened_projects}")
    print(f"fixed_http_ids={fixed_http_ids}")
    print(f"strict_bad_patterns={sum(audit['bad_patterns'].values())}")
    print(f"distinct_sql_schemas={audit['sql_schema_count']}")
    print(f"generic_artifact_tasks={audit['project_artifact']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
