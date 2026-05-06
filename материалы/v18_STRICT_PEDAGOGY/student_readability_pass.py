#!/usr/bin/env python3
from __future__ import annotations

import json
import re

from fix_course_quality import COURSE_FILE, iter_steps, update_reports, independent_audit, write_quality_audit


def load_course() -> dict:
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def save_course(course: dict) -> None:
    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_self_check(body: str, new_block: str) -> str:
    pattern = r"\n### Самопроверка перед отправкой\n[\s\S]*?(?=\n### |\Z)"
    if re.search(pattern, body):
        return re.sub(pattern, "\n" + new_block.rstrip() + "\n", body).strip() + "\n"
    return body.rstrip() + "\n\n" + new_block.rstrip() + "\n"


def early_python_self_check(step: dict) -> str:
    checker = (step.get("checker") or {}).get("type", "")
    if checker == "python_stdout":
        return f"""### Самопроверка перед отправкой
1. Запусти пример из условия.
2. Сравни вывод посимвольно: буквы, пробелы, порядок строк.
3. Проверь крайний случай для шага `{step['title']}`.
4. Убери лишний текст: программа должна вывести только то, что просит условие.
"""
    if checker == "python_pytest":
        return f"""### Самопроверка перед отправкой
1. Проверь обычный пример из условия.
2. Проверь крайний случай для шага `{step['title']}`.
3. Если задача просит функцию, верни значение через `return`, а не печатай его.
4. Убедись, что функция не меняет входные данные без необходимости.
"""
    return f"""### Самопроверка перед отправкой
1. Назови, что приходит на вход.
2. Назови, что должен сделать код.
3. Проверь крайний случай для шага `{step['title']}`.
4. Убери лишние действия, которых нет в условии.
"""


def final_schema_theory(step: dict, order: int) -> str:
    if order == 1:
        return """### Что это
Схема БД финального проекта описывает сущности, связи и ограничения до того, как ты начнёшь писать endpoints. Для проекта задач минимальный набор обычно такой: `users`, `projects`, `memberships`, `tasks`, `comments`.

### Зачем это нужно
Если схема неполная, API начинает хранить состояние в случайных JSON-полях или в коде. Потом сложно добавить права доступа, фильтры, историю действий и тестовые данные.

### Минимальный код
```sql
-- Финальный проект: схема БД: пример 1
CREATE TABLE memberships (
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    PRIMARY KEY (user_id, project_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Как читать пример
`memberships` связывает пользователя и проект. Составной primary key запрещает добавить одного и того же пользователя в проект дважды. `role` хранит права внутри проекта.

### Что здесь важно
Связь many-to-many лучше вынести в отдельную таблицу, особенно если у связи есть собственные поля: роль, дата добавления или статус приглашения.

### Частая ошибка
Частая ошибка — положить `project_ids` строкой внутрь `users`. Такой вариант трудно фильтровать, валидировать и связывать с задачами.

### Проверь себя
Почему `memberships` лучше, чем поле `project_ids` в таблице `users`?
"""
    return """### Разбор перед практикой
Перед SQL-задачами нарисуй связи: пользователь владеет проектом, проект содержит задачи, задача может иметь исполнителя и комментарии. Потом проверь, где связь обязательная, а где значение может быть пустым.

### Рабочий фрагмент
```sql
-- Финальный проект: схема БД: пример 2
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    assignee_id INTEGER,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id)
);
```

### Как проверить руками
`project_id` обязателен: задача не должна жить без проекта. `assignee_id` может быть пустым: задачу можно создать до назначения исполнителя.

### Граница навыка
Сейчас ты проверяешь не красивое название таблиц, а правила данных: обязательность, уникальность, внешние ключи и допустимые пустые значения.

### Ошибка перед отправкой
Не заменяй связи текстовыми полями вроде `assignee_email`, если дальше API должен фильтровать задачи по пользователю.

### Контрольный вопрос
Почему `assignee_id` может быть `NULL`, а `project_id` нет?
"""


def main() -> int:
    course = load_course()
    changed = 0
    for module, lesson, step in iter_steps(course):
        if module["id"] == "m01" and int(lesson["order"]) <= 19 and step["type"] in {"practice", "project"}:
            before = step.get("body_markdown", "")
            step["body_markdown"] = replace_self_check(before, early_python_self_check(step))
            if step["body_markdown"] != before:
                changed += 1
        if lesson["id"] == "m05_l017_finalnyy-proekt-shema-bd" and step["type"] == "theory":
            before = step.get("body_markdown", "")
            step["body_markdown"] = final_schema_theory(step, 1 if int(step["order"]) == 1 else 2)
            if step["body_markdown"] != before:
                changed += 1
    save_course(course)
    update_reports(course)
    audit = independent_audit(course)
    write_quality_audit(audit)
    print(f"readability_changes={changed}")
    print(f"strict_bad_patterns={sum(audit['bad_patterns'].values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
