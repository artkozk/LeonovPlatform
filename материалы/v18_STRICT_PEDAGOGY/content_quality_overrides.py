#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from fix_course_quality import COURSE_FILE, iter_steps, update_reports, independent_audit, write_quality_audit
from final_quality_pass import topic_tokens, display


def load_course() -> dict:
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def save_course(course: dict) -> None:
    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def terms_line(title: str) -> str:
    tokens = topic_tokens(title)
    if not tokens:
        return ""
    return "\n\n### Термины для проверки\n`" + "`, `".join(tokens) + f"`. Эти термины относятся к теме `{display(title)}`."


def sql_code_for(title: str, second: bool = False) -> tuple[str, str, str, str, str, str]:
    low = title.lower()
    if "where" in low:
        return (
            "SQL: WHERE оставляет только строки, которые проходят условие. Сначала выбери таблицу, потом задай фильтр, потом зафиксируй порядок.",
            "Фильтр нужен, чтобы не тащить в приложение лишние строки и не проверять условия вручную в Python.",
            "SELECT id, name\nFROM users\nWHERE active = 1\nORDER BY id;",
            "`WHERE active = 1` отбрасывает неактивных пользователей. `ORDER BY id` делает результат стабильным.",
            "Не путай фильтр строк и выбор колонок: `WHERE` решает, какие строки попадут в результат.",
            "Что изменится, если убрать `WHERE active = 1`?",
        )
    if "order by" in low or "limit" in low:
        return (
            "ORDER BY задаёт порядок строк, а LIMIT ограничивает количество строк результата.",
            "Без явного порядка база не обещает, какая строка будет первой. Это ломает страницы, отчёты и автопроверки.",
            "SELECT id, total\nFROM orders\nORDER BY total DESC, id\nLIMIT 2;",
            "`ORDER BY total DESC` ставит дорогие заказы выше. Второй ключ `id` убирает случайность при равной сумме.",
            "Не используй LIMIT без ORDER BY, если важно получить именно верхние строки.",
            "Почему два заказа с одинаковой суммой лучше дополнительно сортировать по `id`?",
        )
    if "like" in low or "between" in low or "null" in low:
        return (
            "LIKE, IN, BETWEEN и NULL закрывают частые фильтры: поиск по маске, список допустимых значений, диапазон и отсутствие значения.",
            "Эти операторы нужны для форм поиска, фильтров админки и обработки неполных данных.",
            "SELECT id, name\nFROM users\nWHERE city IS NULL OR city IN ('Казань', 'Москва')\nORDER BY id;",
            "`IS NULL` нужен отдельно: сравнение `city = NULL` не работает как обычное равенство.",
            "Частая ошибка — писать `= NULL` вместо `IS NULL`.",
            "Какая часть запроса найдёт пользователя без города?",
        )
    if "агрег" in low:
        return (
            "Агрегаты считают значения по набору строк: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.",
            "Backend часто отдаёт не все строки, а итог: количество задач, сумму заказов, среднюю оценку.",
            "SELECT user_id, COUNT(*) AS orders_count, SUM(total) AS total_sum\nFROM orders\nGROUP BY user_id\nORDER BY user_id;",
            "`GROUP BY user_id` собирает заказы по пользователю. `COUNT(*)` считает строки, `SUM(total)` складывает суммы.",
            "Не выбирай обычную колонку рядом с агрегатом без GROUP BY: результат будет неоднозначным.",
            "Почему `COUNT(*)` и `COUNT(city)` могут дать разные числа?",
        )
    if "group by" in low:
        return (
            "GROUP BY объединяет строки в группы, чтобы агрегат считался отдельно для каждой группы.",
            "Так строят отчёты по пользователям, проектам, курсам и статусам.",
            "SELECT status, COUNT(*) AS tasks_count\nFROM tasks\nGROUP BY status\nORDER BY status;",
            "`status` становится ключом группы. Для каждого статуса база считает отдельный `COUNT`.",
            "GROUP BY идёт после WHERE и до HAVING.",
            "Какая колонка в примере является ключом группы?",
        )
    if "having" in low:
        return (
            "HAVING фильтрует уже собранные группы. WHERE фильтрует строки до группировки, HAVING — результат GROUP BY.",
            "Это нужно, когда ты хочешь показать только проекты с двумя и более задачами или клиентов с крупной суммой заказов.",
            "SELECT project_id, COUNT(*) AS tasks_count\nFROM tasks\nGROUP BY project_id\nHAVING COUNT(*) >= 2\nORDER BY project_id;",
            "`GROUP BY` собирает задачи по проектам. `HAVING COUNT(*) >= 2` оставляет только большие группы.",
            "Не ставь агрегатное условие в WHERE: `WHERE COUNT(*)` не сработает.",
            "Почему `COUNT(*) >= 2` должен стоять в HAVING?",
        )
    if "inner join" in low:
        return (
            "INNER JOIN возвращает только пары строк, где условие связи нашло совпадение.",
            "Так API собирает задачу вместе с проектом, заказ вместе с пользователем или книгу вместе с автором.",
            "SELECT projects.name, tasks.title\nFROM tasks\nJOIN projects ON projects.id = tasks.project_id\nORDER BY tasks.id;",
            "`ON projects.id = tasks.project_id` связывает внешний ключ задачи с primary key проекта.",
            "Если забыть ON, получишь перемножение строк.",
            "Какие две колонки образуют key-связь?",
        )
    if "left join" in low:
        return (
            "LEFT JOIN сохраняет строки из левой таблицы, даже если справа нет совпадения.",
            "Он нужен для поиска пустых связей: пользователей без заказов, проектов без задач, книг без выдач.",
            "SELECT projects.id, projects.name\nFROM projects\nLEFT JOIN tasks ON tasks.project_id = projects.id\nWHERE tasks.id IS NULL\nORDER BY projects.id;",
            "Сначала LEFT JOIN сохраняет все проекты. Потом `WHERE tasks.id IS NULL` оставляет только проекты без задач.",
            "Если фильтровать правую таблицу обычным WHERE без NULL-условия, LEFT JOIN часто превращается в INNER JOIN.",
            "Почему условие `tasks.id IS NULL` показывает отсутствие связи?",
        )
    if "self join" in low:
        return (
            "Self join соединяет таблицу саму с собой через два псевдонима.",
            "Так ищут руководителя и подчинённого, родительскую и дочернюю задачу, похожие события в одной таблице.",
            "SELECT child.title, parent.title\nFROM tasks AS child\nJOIN tasks AS parent ON parent.id = child.project_id\nORDER BY child.id;",
            "Псевдонимы `child` и `parent` позволяют обращаться к одной таблице как к двум источникам.",
            "Без alias self join почти нечитаем и часто конфликтует по именам колонок.",
            "Зачем в примере нужны два имени для одной таблицы?",
        )
    if "подзапрос" in low:
        return (
            "Подзапрос — это SELECT внутри другого запроса. Он помогает сначала вычислить набор id или значение, а потом использовать его во внешнем запросе.",
            "Подзапросы полезны для фильтров вроде: покажи пользователей, у которых есть оплаченный заказ.",
            "SELECT id, name\nFROM users\nWHERE id IN (SELECT user_id FROM orders WHERE status = 'paid')\nORDER BY id;",
            "Внутренний SELECT возвращает user_id из оплаченных заказов. Внешний SELECT берёт пользователей с такими id.",
            "Следи, чтобы подзапрос возвращал подходящее количество колонок.",
            "Что вернёт внутренний SELECT?",
        )
    if "cte" in low:
        return (
            "CTE через WITH даёт имя промежуточному запросу. Это делает длинный SQL читаемее.",
            "CTE удобен, когда один результат нужен дальше в SELECT, JOIN или агрегате.",
            "WITH paid_orders AS (\n    SELECT user_id, total FROM orders WHERE status = 'paid'\n)\nSELECT user_id, SUM(total) AS paid_total\nFROM paid_orders\nGROUP BY user_id\nORDER BY user_id;",
            "`WITH paid_orders AS (...)` создаёт временное имя для оплаченных заказов. Ниже оно используется как таблица.",
            "Не превращай CTE в склад всего подряд: дай ему имя по смыслу.",
            "Какая часть запроса создаёт CTE?",
        )
    if "окон" in low:
        return (
            "Оконная функция считает значение поверх набора строк, но не схлопывает строки как GROUP BY.",
            "Так делают нумерацию, ранги и накопительные суммы в отчётах.",
            "SELECT user_id, total,\n       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS number\nFROM orders\nORDER BY user_id, number;",
            "`PARTITION BY user_id` делит окно по пользователю. `ORDER BY total DESC` задаёт порядок внутри окна.",
            "Не жди, что оконная функция уменьшит количество строк.",
            "Чем OVER отличается от GROUP BY?",
        )
    if "transaction" in low or "acid" in low or "транзак" in low:
        return (
            "Транзакция объединяет несколько изменений в одну операцию: всё применилось или всё откатилось.",
            "Это защищает деньги, статусы задач, бронирования и любые данные, где нельзя сохранить половину действия.",
            "BEGIN;\nUPDATE orders SET status = 'paid' WHERE id = 2;\nCOMMIT;\nSELECT id, status FROM orders ORDER BY id;",
            "`BEGIN` начинает транзакцию. `COMMIT` фиксирует изменение. `ROLLBACK` нужен, если действие надо отменить.",
            "Не оставляй транзакцию открытой после ошибки.",
            "Что будет отличаться после COMMIT и после ROLLBACK?",
        )
    if "sqlite" in low:
        return (
            "SQLite хранит базу в `.db` файле и выполняет SQL без отдельного сервера.",
            "Это удобно для локальных проектов, тестов на временной базе и маленьких сервисов.",
            "import sqlite3\n\nconn = sqlite3.connect('app.db')\nconn.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL)')\nconn.commit()\nconn.close()",
            "`sqlite3.connect` открывает `.db` файл. `execute` выполняет SQL. `commit` сохраняет изменение.",
            "Не забывай commit после DDL/DML и используй параметры вместо склейки строк.",
            "Какая строка создаёт файл базы?",
        )
    return (
        "SELECT берёт строки из таблицы и возвращает только нужные колонки.",
        "Это первый SQL-навык: без него нельзя читать данные для API, отчётов и проверок.",
        "SELECT id, name\nFROM users\nORDER BY id;",
        "`SELECT id, name` выбирает колонки. `FROM users` задаёт таблицу. `ORDER BY id` фиксирует порядок.",
        "Не используй `SELECT *`, если условие просит конкретные колонки.",
        "Какая часть запроса выбирает таблицу?",
    )


def theory_body(title: str, step_title: str, order: int, concept: str, why: str, code: str, walk: str, important: str, mistake: str, check: str, lang: str) -> str:
    comment = "--" if lang == "sql" else "#"
    code = f"{comment} {display(title)}: пример {order}\n{code.strip()}"
    if order == 2:
        code += "\n" + ("-- Измени одно значение и сравни результат." if lang == "sql" else "# Измени одно значение и сравни результат.")
    if order == 2:
        return f"""### Разбор перед практикой
Практика по теме `{display(title)}` начинается с маленькой диагностики. Сначала выпиши вход, затем выпиши действие, потом заранее назови результат. Для шага `{display(step_title)}` это важнее, чем переписать пример вслепую.

### Рабочий фрагмент
```{lang}
{code}
```

### Как проверить руками
{walk} После этого измени одно значение во входе и проверь, что меняется именно ожидаемая часть результата.

### Граница навыка
{important} В этом шаге не уходи в соседние темы: держи фокус на `{display(title)}` и на одном новом действии.
{terms_line(title)}

### Ошибка перед отправкой
{mistake} Перед отправкой найди этот риск в своём решении и исправь его, если он появился.

### Контрольный вопрос
{check} Ответ должен совпасть с тем, что показывает запуск, запрос или HTTP-ответ.
"""
    return f"""### Что это
{concept} Для темы `{display(title)}` это означает отдельное действие шага `{display(step_title)}`.

### Зачем это нужно
{why} Для темы `{display(title)}` это нужно не как термин, а как навык, который ты сразу проверишь в задаче.
{terms_line(title)}

### Минимальный код
```{lang}
{code}
```

### Как читать пример
{walk} Для темы `{display(title)}` сначала назови вход, затем действие, затем результат.

### Что здесь важно
{important} Для шага `{display(step_title)}` проверь не только обычный случай, но и крайний.

### Частая ошибка
{mistake} Для темы `{display(title)}` такая ошибка обычно проявляется сразу в выводе, строках результата или статусе ответа.

### Проверь себя
{check} Ответь до практики, потом проверь маленьким запуском.
"""


def override_s3(title: str, step_title: str, order: int) -> str:
    concept = "S3 и MinIO хранят файлы как объекты в bucket. У объекта есть key, bytes, metadata и content_type."
    why = "Backend использует object storage для аватаров, отчётов, вложений и выгрузок, которые не нужно хранить в SQL-таблице."
    code = "class FakeStorage:\n    def __init__(self):\n        self.objects = {}\n\n    def upload(self, bucket, key, data, content_type):\n        self.objects[(bucket, key)] = {\"data\": data, \"content_type\": content_type}\n        return {\"bucket\": bucket, \"key\": key}\n\nstorage = FakeStorage()\nstorage.upload(\"reports\", \"2026/may.txt\", b\"ok\", \"text/plain\")"
    walk = "`bucket` группирует объекты. `key` работает как путь внутри bucket. `upload` сохраняет bytes и metadata."
    important = "Object key должен быть стабильным: по нему ты потом делаешь download или presigned URL."
    mistake = "Частая ошибка — хранить локальный путь вместо object key и потом не мочь скачать файл с другого сервера."
    check = "Чем bucket отличается от object key?"
    return theory_body(title, step_title, order, concept, why, code, walk, important, mistake, check, "python")


def override_redis(title: str, step_title: str, order: int) -> str:
    concept = "Redis — key/value хранилище в памяти. Оно быстро отдаёт GET/SET, TTL, counters и простые locks."
    why = "Redis разгружает SQL-базу и хранит короткоживущие данные: кэш пользователя, rate limit, код подтверждения."
    code = "def cached_user(redis, user_id, loader):\n    key = f\"user:{user_id}\"\n    cached = redis.get(key)\n    if cached is not None:\n        return cached\n    value = loader(user_id)\n    redis.set(key, value, ex=60)\n    return value"
    walk = "`GET` проверяет key. При промахе вызывается loader. `SET ... ex=60` кладёт value с TTL."
    important = "TTL должен быть осознанным: слишком короткий даёт лишнюю нагрузку, слишком длинный отдаёт устаревшие данные."
    mistake = "Частая ошибка — обновить SQL-данные и забыть invalidation кэша."
    check = "Почему key лучше строить как `user:{id}`, а не просто из числа?"
    return theory_body(title, step_title, order, concept, why, code, walk, important, mistake, check, "python")


def override_final_project(title: str, step_title: str, order: int) -> str:
    gate = display(title.split(":", 1)[-1].strip() if ":" in title else title)
    concept = f"Финальный project gate `{gate}` сдаётся как конкретный артефакт: файл, route, миграция, workflow, Docker-конфигурация или deploy-проверка."
    why = "Большой проект нельзя проверять одной финальной демонстрацией. Gate ловит ошибку в моменте, когда её ещё дешево исправить."
    code = f"Goal: {gate}\nDeliverable: файл или route, который можно открыть\nPass/Fail: есть команда проверки и отрицательный путь\nRisk: что сломается, если gate принять слишком рано"
    walk = "`Goal` задаёт цель. `Deliverable` называет результат. `Pass/Fail` убирает спорность проверки."
    important = "Если gate нельзя проверить командой, файлом или HTTP-запросом, он ещё не готов."
    mistake = "Частая ошибка — сдавать общий текст без route, команды, файла или критерия отказа."
    check = "Какой один артефакт докажет готовность этого gate?"
    return theory_body(title, step_title, order, concept, why, code, walk, important, mistake, check, "text")


def override_sql(title: str, step_title: str, order: int) -> str:
    concept, why, code, walk, important, check = sql_code_for(title, order == 2)
    mistake = "Частая ошибка — написать запрос, который работает на одном примере, но не фиксирует порядок, связь или крайний случай."
    return theory_body(title, step_title, order, concept, why, code, walk, important, mistake, check, "python" if "sqlite" in title.lower() else "sql")


def main() -> int:
    course = load_course()
    changed = 0
    for module, lesson, step in iter_steps(course):
        if step["type"] != "theory":
            continue
        title = lesson["title"]
        low = title.lower()
        order = 1 if int(step["order"]) == 1 else 2
        if "s3" in low or "minio" in low:
            step["body_markdown"] = override_s3(title, step["title"], order)
            changed += 1
        elif "redis" in low:
            step["body_markdown"] = override_redis(title, step["title"], order)
            changed += 1
        elif "финальный проект" in low:
            step["body_markdown"] = override_final_project(title, step["title"], order)
            changed += 1
        elif module["id"] == "m03" and ("sql" in low or "sqlite" in low):
            step["body_markdown"] = override_sql(title, step["title"], order)
            changed += 1
    save_course(course)
    update_reports(course)
    audit = independent_audit(course)
    write_quality_audit(audit)
    print(f"content_overrides={changed}")
    print(f"strict_bad_patterns={sum(audit['bad_patterns'].values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
