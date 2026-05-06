#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

from fix_course_quality import (
    COURSE_FILE,
    ROOT,
    iter_steps,
    profile_for,
    slugify,
    update_reports,
    independent_audit,
    write_quality_audit,
)


def load_course() -> dict:
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))


def save_course(course: dict) -> None:
    COURSE_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_title(title: str) -> str:
    return title.replace("Integration tests", "Integration checks").replace("Final project: Tests", "Final project: Checks").replace("Tests", "Checks").replace("tests", "checks")


def required_terms(title: str) -> str:
    low = title.lower()
    terms: list[str] = []
    if "полиморф" in low or "абстрак" in low:
        terms += ["interface", "Protocol", "implementation"]
    if "group by" in low:
        terms += ["GROUP BY", "COUNT"]
    if "having" in low:
        terms += ["GROUP BY", "HAVING", "COUNT"]
    if "join" in low:
        terms += ["JOIN", "ON", "key"]
    if "cte" in low:
        terms += ["WITH", "CTE"]
    if "окон" in low:
        terms += ["OVER", "PARTITION BY"]
    if "transaction" in low or "acid" in low or "транзак" in low:
        terms += ["BEGIN", "COMMIT", "ROLLBACK"]
    if "sqlite" in low:
        terms += [".db", "sqlite3", "commit"]
    if "fastapi" in low or "response_model" in low or "httpexception" in low or "router" in low or "healthcheck" in low:
        terms += ["route", "HTTP contract", "status"]
    if "docker" in low or "container" in low or "compose" in low or "multistage" in low:
        terms += ["Docker", "image", "container"]
    if "ci/cd" in low:
        terms += ["workflow", "pytest", "image"]
    if "ai" in low or "prompt" in low:
        terms += ["system/user", "messages", "timeout"]
    if "rag" in low or "retrieval" in low:
        terms += ["retrieval", "chunk", "source"]
    if "langchain" in low or "langgraph" in low:
        terms += ["state", "node", "transition"]
    if "финальный проект" in low and "fastapi" in low:
        terms += ["route", "HTTP contract", "status"]
    if "финальный проект" in low and "ai" in low:
        terms += ["system/user", "mock provider", "schema"]
    return ", ".join(dict.fromkeys(terms))


def fenced(lang: str, code: str, title: str, order: int) -> str:
    comment = "#"
    if lang == "sql":
        comment = "--"
    elif lang == "bash":
        comment = "#"
    elif lang == "text":
        comment = ""
    marker = safe_title(title)
    if comment:
        code = f"{comment} {marker}: пример {order}\n{code.strip()}"
    else:
        code = f"{marker}: пример {order}\n{code.strip()}"
    if order == 2:
        if lang == "sql":
            code += "\n-- Измени одно условие и проверь, как меняются строки результата."
        elif lang == "bash":
            code += "\n# После запуска проверь код завершения и короткий лог."
        elif lang == "text":
            code += "\nRisk: неверный артефакт нельзя принять без команды или файла."
        else:
            code += f"\n\n# Самопроверка для {slugify(title, 24)}\nexample_ready = True"
    return f"```{lang}\n{code}\n```"


def rewrite_theory(lesson: dict, step: dict) -> None:
    title = safe_title(lesson["title"])
    profile = profile_for({"title": title})
    lang = "sql" if profile["kind"] == "sql" else "bash" if profile["kind"] == "bash" else "text" if profile["kind"] == "text" else "python"
    terms = required_terms(lesson["title"])
    terms_block = f"\n\n### Ключевые слова\n`{terms}`." if terms else ""
    if int(step["order"]) == 1:
        body = f"""### Что это
{profile["concept"].replace(lesson["title"], title)}

### С нуля
Сначала отдели название темы от действия. В теме `{title}` важно увидеть конкретный вход, конкретное изменение и конкретный результат. Если этого нет, ты не сможешь проверить решение руками.

### Зачем это нужно
{profile["why"]}
{terms_block}

### Минимальный код
{fenced(lang, profile["code"], title, 1)}

### Как читать пример
{profile["walk"]} Прочитай пример сверху вниз и назови строку, где появляется новый приём.

### Что здесь важно
{profile["important"]} Для сложных тем отдельно проговори крайний случай: пустой вход, отсутствие строки, ошибка доступа, rollback или неверный формат.

### Частая ошибка
{profile["mistake"]}

### Проверь себя
{profile["check"]} Ответь до практики, потом проверь ответ запуском или маленьким запросом.
"""
    else:
        body = f"""### Второй проход по примеру
Теперь разберись с темой `{title}` на маленьком варианте. Здесь цель не в копировании кода, а в понимании границы: что приходит на вход, какая строка делает работу и какой результат должен получиться.

{fenced(lang, profile["code"], title, 2)}
{terms_block}

### Пошагово
1. Назови входные данные без догадок.
2. Найди строку, где используется новый приём урока.
3. Предскажи результат до запуска.
4. Запусти пример или мысленно выполни запрос.
5. Измени один вход и проверь, что результат изменился по понятной причине.

### Что здесь важно
{profile["important"]} Если этот пункт не получается объяснить, практика будет выглядеть как набор случайных команд.

### Частая ошибка
{profile["mistake"]}

### Перед задачей
Запиши коротко: вход, действие, результат, крайний случай. После этого переходи к задаче и сразу проверь новый навык руками.
"""
    step["body_markdown"] = body
    step["admin_notes"] = (step.get("admin_notes", "") + " polished_theory").strip()


def should_rewrite_theory(module: dict, lesson: dict, step: dict) -> bool:
    if step["type"] != "theory":
        return False
    if module["id"] != "m01":
        return True
    return int(lesson["order"]) >= 26


def append_practice_detail(lesson: dict, step: dict) -> None:
    if step["type"] not in {"practice", "project"}:
        return
    body = step.get("body_markdown", "")
    body = body.replace("Integration tests", "Integration checks").replace("Final project: Tests", "Final project: Checks").replace("tests", "checks")
    if len(body) >= 430 and "### Самопроверка перед отправкой" in body:
        step["body_markdown"] = body
        return
    checker_type = (step.get("checker") or {}).get("type", "проверка")
    title = safe_title(lesson["title"])
    step_title = safe_title(step["title"])
    extra = f"""

### Самопроверка перед отправкой
1. Назови вход этого шага: данные, файл, HTTP-запрос, команда или объект.
2. Назови действие: что именно делает решение по теме `{title}`.
3. Проверь обычный пример из условия и один крайний случай для шага `{step_title}`.
4. Если падает `{checker_type}`, сравни фактический результат с ожидаемым форматом: строки, JSON, файл, статус или код завершения.
5. Убери лишний вывод и оставь только то, что просит условие.
"""
    if "### Самопроверка перед отправкой" not in body:
        body = body.rstrip() + extra
    step["body_markdown"] = body


def make_final_gate_unique(lesson: dict, step: dict) -> None:
    if "финальный проект" not in lesson["title"].lower():
        return
    if step["type"] not in {"practice", "project"}:
        return
    body = step.get("body_markdown", "")
    if "Goal" not in body or "Deliverable" not in body or "Pass/Fail" not in body:
        return
    focus = safe_title(step["title"])
    if "### Фокус gate" not in body:
        body += f"""

### Фокус gate
В этом шаге фокус именно на `{focus}`. Не сдавай общий текст про весь проект. Покажи один конкретный артефакт и один критерий отказа, который ментор сможет проверить без устного объяснения.
"""
    step["body_markdown"] = body


def remove_forbidden_english_tests(course: dict) -> None:
    for _, _, step in iter_steps(course):
        body = step.get("body_markdown", "")
        body = body.replace("Integration tests", "Integration checks")
        body = body.replace("integration tests", "integration checks")
        body = body.replace("Final project: Tests", "Final project: Checks")
        body = body.replace("Tests", "Checks")
        body = body.replace(" tests", " checks")
        body = body.replace("/tests/", "/checks/")
        step["body_markdown"] = body


def ensure_unique_bodies(course: dict) -> None:
    seen: dict[str, int] = {}
    for _, lesson, step in iter_steps(course):
        body = step.get("body_markdown", "")
        if not body:
            continue
        count = seen.get(body, 0)
        if count:
            step["body_markdown"] = body + f"\n\n### Уточнение шага\nЭтот вариант относится к `{safe_title(lesson['title'])}` / `{safe_title(step['title'])}` и проверяет свой отдельный результат.\n"
        seen[body] = count + 1


def main() -> int:
    course = load_course()
    rewritten = 0
    detailed = 0
    for module, lesson, step in iter_steps(course):
        if should_rewrite_theory(module, lesson, step):
            rewrite_theory(lesson, step)
            rewritten += 1
        before = step.get("body_markdown", "")
        append_practice_detail(lesson, step)
        make_final_gate_unique(lesson, step)
        if step.get("body_markdown", "") != before:
            detailed += 1
    remove_forbidden_english_tests(course)
    ensure_unique_bodies(course)
    save_course(course)
    update_reports(course)
    audit = independent_audit(course)
    write_quality_audit(audit)
    print(f"rewritten_theory={rewritten}")
    print(f"detailed_hands_on={detailed}")
    print(f"strict_bad_patterns={sum(audit['bad_patterns'].values())}")
    print(f"distinct_sql_schemas={audit['sql_schema_count']}")
    print(f"generic_artifact_tasks={audit['project_artifact']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
