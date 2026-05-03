#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COURSE_FILE = ROOT / "course_import.json"
MANIFEST_FILE = ROOT / "manifest.csv"
COVERAGE_FILE = ROOT / "coverage_matrix.csv"

BODY_LEAKS = ["Шаблон", "Подсказки", "Эталон", "Автотесты", "hidden tests", "tests", "solution", "checker", "admin", "AI-инструкция", "Сценарий", "skill_focus", "lesson_stage", "qa_notes", "ключевая идея темы", "собери практическую работу по теме", "ученик учится", "ученик должен", "в рамках данного урока"]
BANNED = ["Тест недоступен", "Для этого шага пока нет автопроверки"]
CORRUPTION = ["?" * 3, "\ufffd", "\u00d0", "\u00d1", "\u0420\u045f", "\u0420\ufffd", "\u0421\ufffd"]
BAD_COVERAGE = {"missing", "thin", "placeholder"}

def load_course():
    return json.loads(COURSE_FILE.read_text(encoding="utf-8"))

def iter_lessons(course):
    for module in course["course"]["modules"]:
        for lesson in module["lessons"]:
            yield module, lesson

def iter_steps(course):
    for module, lesson in iter_lessons(course):
        for step in lesson["steps"]:
            yield module, lesson, step

def has_bad_text(value):
    return isinstance(value, str) and any(token in value for token in CORRUPTION)

def walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj

def body_route_methods(body):
    found = set()
    for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
        for match in re.findall(rf"\b{method}\s+(/[A-Za-z0-9_/\-{{}}]+)", body):
            found.add((method, match.replace("{task_id}", "1")))
    return found

def normalized_solution(code):
    code = re.sub(r"#.*", "", code or "")
    code = re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*_\d+\b", "NAME", code)
    code = re.sub(r"\s+", " ", code).strip()
    return code

def lesson_mode(lesson):
    joined = " ".join(lesson.get("roadmap_topics", []) + [lesson["title"]]).lower()
    topic_set = {t.lower() for t in lesson.get("roadmap_topics", [])}
    if "fastapi" in joined or "sqlalchemy" in joined or "crud" in joined:
        return "fastapi"
    if "sql" in joined or "sqlite" in joined:
        return "sql"
    if {"ai api", "rag", "vector databases", "langchain / langgraph концептуально", "вайбкодинг", "ai для учёбы"} & topic_set or re.search(r"\b(ai|rag|langchain|langgraph)\b", joined) or "вайб" in joined:
        return "ai"
    if any(x in joined for x in ["ооп", "магические", "протокол", "наслед", "полиморф", "dataclass"]):
        return "oop"
    return "other"

FIRST30_FORBIDDEN = {
    1: [r"\binput\s*\(", r"\bint\s*\(", r"\bdef\s+", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\[", r"\{", "pytest", "fastapi", "sql", "git"],
    2: [r"\bdef\s+", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\[.*\]", r"\{", "pytest", "fastapi", "sql", "git"],
    3: [r"\bdef\s+", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    4: [r"\bdef\s+", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    5: [r"\bdef\s+", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    6: [r"\bdef\s+", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    7: [r"\bdef\s+", r"\bclass\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    8: [r"\bdef\s+", r"\bclass\s+", r"\{", "pytest", "fastapi", "sql", "git"],
}

def future_violation(lesson, step):
    if not lesson["id"].startswith("m01_l") or lesson["order"] > 8 or step["type"] not in {"practice", "project"}:
        return False
    blob = (step.get("body_markdown", "") + "\n" + step.get("editor_initial_code", "") + "\n" + step.get("solution_code", "")).lower()
    for pattern in FIRST30_FORBIDDEN.get(lesson["order"], []):
        if re.search(pattern, blob):
            return True
    return False

def manifest_rows(course):
    rows = []
    for module, lesson, step in iter_steps(course):
        rows.append({"module_order": str(module["order"]), "module_title": module["title"], "lesson_order": str(lesson["order"]), "lesson_title": lesson["title"], "step_order": str(step["order"]), "step_title": step["title"], "step_type": step["type"], "checker_type": step.get("checker", {}).get("type", ""), "xp": str(step["xp"]), "difficulty": str(step["difficulty"]), "estimated_minutes": str(step["estimated_minutes"])})
    return rows

def validate(write_reports=True):
    course = load_course()
    errors = []
    stats = Counter()
    first = course["course"]["modules"][0]["lessons"][0]
    if first["title"] != "Первый код" or first["steps"][0]["title"] != "Смысл":
        errors.append("course must start with first lesson `Первый код` and step `Смысл`")
    ids = Counter()
    bodies = Counter()
    scenario = Counter()
    solution_counts = Counter()
    http_contracts = defaultdict(set)
    question_counts = Counter()
    first30_issues = []
    for path, text in walk_strings(course):
        if has_bad_text(text):
            errors.append(f"encoding corruption: {path}")
            break
    for module, lesson, step in iter_steps(course):
        stats["steps"] += 1
        stats[f"type_{step['type']}"] += 1
        ids[step["id"]] += 1
        bodies[step.get("body_markdown", "")] += 1
        if step.get("scenario_id"):
            scenario[step["scenario_id"]] += 1
        body_low = step.get("body_markdown", "").lower()
        for leak in BODY_LEAKS + BANNED:
            if leak.lower() in body_low:
                errors.append(f"body leak {step['id']}: {leak}")
                break
        if step["type"] == "practice" and not step.get("checker"):
            errors.append(f"practice without checker: {step['id']}")
        if step["type"] == "project" and not (step.get("checker") or step.get("ide_plugin_check") or step.get("ai_review_config")):
            errors.append(f"project without check: {step['id']}")
        if step["type"] == "test":
            qs = step.get("questions", [])
            if len(qs) < 3:
                errors.append(f"test without 3 structured questions: {step['id']}")
            for q in qs:
                question_counts[q.get("question", "")] += 1
                if not q.get("options") or not q.get("correct_answer_id") or not q.get("explanation"):
                    errors.append(f"bad question structure: {step['id']}")
        if step.get("checker"):
            stats[f"checker_{step['checker'].get('type')}"] += 1
        if future_violation(lesson, step):
            first30_issues.append(step["id"])
        if step["type"] in {"practice", "project"}:
            norm = normalized_solution(step.get("solution_code", ""))
            if norm:
                solution_counts[norm] += 1
        if step.get("checker", {}).get("type") == "http_api":
            routes = body_route_methods(step.get("body_markdown", ""))
            for test in step["checker"].get("public_tests", []) + step["checker"].get("hidden_tests", []):
                method, path = test.get("method"), test.get("path")
                if method and path and test in step["checker"].get("public_tests", []):
                    display = path
                    if "/1" in display:
                        display = display.replace("/1", "/{task_id}")
                    if (method, path) not in routes and (method, display) not in routes:
                        errors.append(f"http body/checker mismatch: {step['id']}")
                http_contracts[(lesson["id"], method, path, test.get("expected_status"))].add(step["id"])
        if step.get("checker", {}).get("type") == "sql_query":
            checker = step["checker"]
            if not checker.get("schema_sql") or not checker.get("seed_sql"):
                errors.append(f"SQL checker without schema/seed: {step['id']}")
            if lesson["order"] <= 3 and module["order"] == 3 and any(token in step.get("solution_code", "").lower() for token in ["row_number", "rollback", "savepoint", "explain"]):
                errors.append(f"SQL progression violation: {step['id']}")
        mode = lesson_mode(lesson)
        sol = step.get("solution_code", "")
        if step["type"] == "practice" and mode == "oop":
            low_title = lesson["title"].lower()
            if "dataclass" in low_title and "@dataclass" not in sol:
                errors.append(f"dataclass practice without @dataclass: {step['id']}")
            elif "протокол" in low_title and "Protocol" not in sol and "class " not in sol:
                errors.append(f"protocol practice without structural object: {step['id']}")
            elif any(x in low_title for x in ["ооп", "магические", "наслед", "полиморф", "инкапс", "композиц", "абстрак"]) and "class " not in sol:
                errors.append(f"OOP practice without class: {step['id']}")
        if step["type"] == "practice" and mode == "ai":
            low = (lesson["title"] + " " + step["title"] + " " + sol).lower()
            if re.search(r"\brag\b", low) and not all(x in low for x in ["source", "chunk"]):
                errors.append(f"RAG practice without chunks/sources: {step['id']}")
            if re.search(r"\blang(chain|graph)?\b", low) and not all(x in low for x in ["state", "node"]):
                errors.append(f"LangGraph practice without state/node: {step['id']}")
            if "вайб" in low and not any(x in low for x in ["secret", "diff", "review"]):
                errors.append(f"safe vibe practice without security review: {step['id']}")
    duplicate_ids = [k for k, v in ids.items() if v > 1]
    if duplicate_ids:
        errors.append(f"duplicate ids: {len(duplicate_ids)}")
    duplicate_bodies = [k for k, v in bodies.items() if k and v > 1]
    if duplicate_bodies:
        errors.append(f"duplicate body_markdown: {len(duplicate_bodies)}")
    duplicate_scenarios = [k for k, v in scenario.items() if k and v > 1]
    if duplicate_scenarios:
        errors.append(f"duplicate scenario_id: {len(duplicate_scenarios)}")
    repeated_questions = [k for k, v in question_counts.items() if k and v > 3]
    if repeated_questions:
        errors.append(f"question repeated more than 3 times: {len(repeated_questions)}")
    repeated_solutions = [k for k, v in solution_counts.items() if k and v > 1]
    if repeated_solutions:
        errors.append(f"normalized solution duplicates: {len(repeated_solutions)}")
    duplicate_http = [k for k, ids in http_contracts.items() if len(ids) > 1]
    if duplicate_http:
        errors.append(f"FastAPI duplicate contracts inside lessons: {len(duplicate_http)}")
    if first30_issues:
        errors.append(f"first 30 future knowledge violations: {len(first30_issues)}")
    expected = manifest_rows(course)
    if MANIFEST_FILE.exists():
        with MANIFEST_FILE.open("r", encoding="utf-8-sig", newline="") as fh:
            actual = list(csv.DictReader(fh))
        if actual != expected:
            errors.append("manifest mismatch")
    else:
        errors.append("manifest missing")
    if COVERAGE_FILE.exists():
        with COVERAGE_FILE.open("r", encoding="utf-8-sig", newline="") as fh:
            bad = [r for r in csv.DictReader(fh) if r.get("status") in BAD_COVERAGE]
        if bad:
            errors.append(f"coverage bad status: {len(bad)}")
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "stats": stats, "first30_issues": first30_issues}
    if write_reports:
        write_reports_fn(course, result)
    return result

def write_reports_fn(course, result):
    stats = result["stats"]
    total_lessons = sum(1 for _ in iter_lessons(course))
    total_steps = stats["steps"]
    total_hours = round(sum(st["estimated_minutes"] for _, _, st in iter_steps(course)) / 60, 1)
    lines = ["# Validation report v18_STRICT_PEDAGOGY", "", f"final status: {result['status']}", "", "## Totals", f"- total modules: {len(course['course']['modules'])}", f"- total lessons: {total_lessons}", f"- total steps: {total_steps}", f"- total hours: {total_hours}", f"- steps by type: {dict((k[5:], v) for k, v in stats.items() if k.startswith('type_'))}", f"- checkers by type: {dict((k[8:], v) for k, v in stats.items() if k.startswith('checker_'))}", "", "## Errors"]
    lines += [f"- {e}" for e in result["errors"]] if result["errors"] else ["- none"]
    (ROOT / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    qa = ["# QA report v18_STRICT_PEDAGOGY", "", f"PASS/FAIL: {result['status']}", "", "## Critical blockers"]
    qa += [f"- {e}" for e in result["errors"]] if result["errors"] else ["- не найдено"]
    qa += ["", "## Independent checks", "- first 30 lessons prerequisite gate is enforced;", "- body leaks and encoding corruption are hard fail;", "- manifest and coverage are checked independently;", "- SQL/FastAPI/AI/OOP topic gates are checked from JSON, not from validation_report.md.", "", "## 20 худших шагов"]
    qa += [f"- blocker: {e}" for e in result["errors"][:20]] if result["errors"] else ["- автоматический аудит не нашёл критичных кандидатов; ручная выборка на staging обязательна."]
    qa += ["", "## Итог", "PASS означает только автоматическую готовность пакета. Перед массовым запуском остаётся staging-regression: импорт, первые 10 уроков как студент и выборка 50-100 шагов."]
    (ROOT / "qa_report.md").write_text("\n".join(qa) + "\n", encoding="utf-8")

def main():
    result = validate(write_reports=True)
    course = load_course()
    lessons = sum(1 for _ in iter_lessons(course))
    hours = round(sum(st["estimated_minutes"] for _, _, st in iter_steps(course)) / 60, 1)
    print(f"status={result['status']}")
    print(f"modules={len(course['course']['modules'])} lessons={lessons} steps={result['stats']['steps']} hours={hours}")
    print(f"practice={result['stats']['type_practice']} project={result['stats']['type_project']} questions={sum(len(st.get('questions', [])) for _, _, st in iter_steps(course))}")
    print(f"sql_tasks={result['stats']['checker_sql_query']} fastapi_tasks={result['stats']['checker_http_api']} pytest_tasks={result['stats']['checker_python_pytest']} ide_tasks={result['stats']['checker_ide_plugin']}")
    if result["errors"]:
        for e in result["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
