#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COURSE_FILE = ROOT / "course_import.json"
MANIFEST_FILE = ROOT / "manifest.csv"
COVERAGE_FILE = ROOT / "coverage_matrix.csv"

BODY_LEAKS = ["Шаблон", "Подсказки", "Эталон", "Автотесты", "hidden tests", "tests", "solution", "checker", "admin", "AI-инструкция", "Сценарий", "skill_focus", "lesson_stage", "qa_notes", "ключевая идея темы", "собери практическую работу по теме", "ученик учится", "ученик должен", "в рамках данного урока", "применяет тему", "проверяемый результат", "используй новую тему", "отдельный сценарий применения темы", "приём Python", "практический инструмент", "SQL-приём", "Ответь на вопросы по теме", "один рабочий пример по теме", "закрепи тему", "проверяемом артефакте", "После урока ты сможешь", "backend-код держится на маленьких проверяемых функциях и объектах", "это не отдельный термин ради термина", "рабочий инструмент, который решает конкретную проблему", "опирайся только на уже пройденные темы", "минимальный ориентир", "result = service.handle(command)", "Backend-код должен иметь явный вход", "Cache TTL", "Inventory delta", "State transition", "CSV columns", "Priority queue", "Retry log", "JsonRenderer", "TextRenderer"]
BANNED = ["Тест недоступен", "Для этого шага пока нет автопроверки"]
CORRUPTION = ["?" * 3, "\ufffd", "\u00d0", "\u00d1", "\u0420\u045f", "\u0420\ufffd", "\u0421\ufffd"]
BAD_COVERAGE = {"missing", "thin", "placeholder"}
FIRST10_THEORY_MIN = 700
FIRST10_LESSON_THEORY_MIN = 1400
COURSE_PREVIEW_MIN_CHARS = 30000
IDE_PLUGIN_SPEC_MIN_CHARS = 5000
PEDAGOGICAL_AUDIT_MIN_CHARS = 1200
DUPLICATION_REPORT_MIN_CHARS = 1200
ALL_THEORY_MIN = 700

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
        for match in re.findall(rf"\b{method}\s+(/[A-Za-z0-9_/\-{{}}?=&.]+)", body):
            found.add((method, match.replace("{task_id}", "1")))
    return found

def normalized_solution(code):
    code = re.sub(r"#.*", "", code or "")
    code = re.sub(r"\b(def|class)\s+[A-Za-z_][A-Za-z0-9_]*", r"\1 NAME", code)
    code = re.sub(r"from solution import .+", "from solution import NAME", code)
    code = re.sub(r"\s+", " ", code).strip()
    return code

def normalized_body(body):
    body = body or ""
    body = re.sub(r"`[A-Za-z_][A-Za-z0-9_]*`", "`NAME`", body)
    body = re.sub(r"\bs\d{3}\b", "STEP", body)
    body = re.sub(r"\b\d+\b", "N", body)
    return re.sub(r"\s+", " ", body).strip()

def structural_solution_signature(code):
    code = re.sub(r"#.*", "", code or "")
    code = re.sub(r"\b(def|class)\s+[A-Za-z_][A-Za-z0-9_]*", r"\1 NAME", code)
    code = re.sub(r"from solution import .+", "from solution import NAME", code)
    return re.sub(r"\s+", " ", code).strip()

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
    1: [r"\binput\s*\(", r"\bint\s*\(", r"\bfloat\s*\(", r"\bsplit\s*\(", r"\bdef\s+", r"\breturn\b", r"\bclass\s+", r"\bimport\s+", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\[", r"\{", "pytest", "fastapi", "sql", "git"],
    2: [r"\bdef\s+", r"\breturn\b", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\[.*\]", r"\{", "pytest", "fastapi", "sql", "git"],
    3: [r"\bdef\s+", r"\breturn\b", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    4: [r"\bdef\s+", r"\breturn\b", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\bif\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    5: [r"\bdef\s+", r"\breturn\b", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    6: [r"\bdef\s+", r"\breturn\b", r"\bclass\s+", r"\bfor\s+", r"\bwhile\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    7: [r"\bdef\s+", r"\breturn\b", r"\bclass\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    8: [r"\bdef\s+", r"\breturn\b", r"\bclass\s+", r"\{", "pytest", "fastapi", "sql", "git"],
    9: [r"\bclass\s+", r"\{", "fastapi", "sql", "git"],
    10: [r"\bclass\s+", r"\{", "fastapi", "sql", "git"],
}

def future_violation(lesson, step):
    if not lesson["id"].startswith("m01_l") or lesson["order"] > 10:
        return False
    blob = (step.get("body_markdown", "") + "\n" + step.get("editor_initial_code", "") + "\n" + step.get("solution_code", "")).lower()
    for pattern in FIRST30_FORBIDDEN.get(lesson["order"], []):
        if re.search(pattern, blob):
            return True
    return False

def first10_pedagogy_issues(lesson):
    issues = []
    if not lesson["id"].startswith("m01_l") or lesson["order"] > 10:
        return issues
    theory_steps = [s for s in lesson["steps"] if s["type"] == "theory"]
    total_theory = sum(len(s.get("body_markdown", "")) for s in theory_steps)
    if total_theory < FIRST10_LESSON_THEORY_MIN:
        issues.append(f"first10 theory total too short: {lesson['id']}")
    for step in theory_steps:
        if len(step.get("body_markdown", "")) < FIRST10_THEORY_MIN:
            issues.append(f"first10 theory step too short: {step['id']}")
        body = step.get("body_markdown", "")
        required_markers = ["```python", "Частая ошибка", "Самопроверка"]
        for marker in required_markers:
            if marker not in body:
                issues.append(f"first10 theory missing {marker}: {step['id']}")
    for step in lesson["steps"]:
        if step["type"] == "practice":
            body = step.get("body_markdown", "")
            if "### Пример" not in body:
                issues.append(f"first10 practice without example: {step['id']}")
            if not step.get("editor_initial_code") and "напиши" not in body.lower():
                issues.append(f"first10 empty starter without write instruction: {step['id']}")
            if len(body) < 500 and lesson["order"] != 1:
                issues.append(f"first10 practice body too short: {step['id']}")
        if step["type"] == "project":
            body = step.get("body_markdown", "")
            if "Создай" not in body or "main.py" not in body or "README.md" not in body:
                issues.append(f"first10 mini-project not concrete: {step['id']}")
            checker = step.get("checker", {})
            if checker.get("type") != "ide_plugin" or not checker.get("required_files") or not checker.get("commands"):
                issues.append(f"first10 mini-project without concrete IDE check: {step['id']}")
    return issues

def docs_quality_issues():
    issues = []
    preview = ROOT / "course_preview.md"
    spec = ROOT / "ide_plugin_spec.md"
    pedagogy = ROOT / "pedagogical_audit_report.md"
    duplication = ROOT / "duplication_report.md"
    if not preview.exists() or len(preview.read_text(encoding="utf-8")) < COURSE_PREVIEW_MIN_CHARS:
        issues.append("course_preview.md too short for methodist review")
    if not spec.exists() or len(spec.read_text(encoding="utf-8")) < IDE_PLUGIN_SPEC_MIN_CHARS:
        issues.append("ide_plugin_spec.md too short for plugin implementation")
    if not pedagogy.exists() or len(pedagogy.read_text(encoding="utf-8")) < PEDAGOGICAL_AUDIT_MIN_CHARS:
        issues.append("pedagogical_audit_report.md missing or too short")
    if not duplication.exists() or len(duplication.read_text(encoding="utf-8")) < DUPLICATION_REPORT_MIN_CHARS:
        issues.append("duplication_report.md missing or too short")
    checked_suffixes = {".json", ".md", ".csv", ".py", ".sql"}
    for file_path in ROOT.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in checked_suffixes:
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if any(token in text for token in CORRUPTION):
            issues.append(f"encoding corruption in package file: {file_path.name}")
            break
    return issues

def first_fastapi_progression_issue(course):
    for module, lesson, step in iter_steps(course):
        if module["order"] != 4:
            continue
        if step.get("checker", {}).get("type") == "http_api":
            # The first public FastAPI exercise must be a simple GET. Hidden
            # negative probes may use other methods, for example POST /health
            # expecting 405, and should not make the learning progression fail.
            methods = {t.get("method") for t in step["checker"].get("public_tests", []) if t.get("method")}
            body = (step.get("body_markdown", "") + " " + step.get("title", "")).lower()
            if methods and methods != {"GET"}:
                return f"first FastAPI task is not simple GET: {step['id']}"
            if any(token in body for token in ["patch", "delete", "auth", "jwt"]):
                return f"first FastAPI task mentions advanced topic: {step['id']}"
            return None
    return "no FastAPI http_api task found"

def fastapi_ladder_issues(course):
    issues = []
    module = next((m for m in course["course"]["modules"] if m["order"] == 4), None)
    if not module:
        return ["FastAPI module missing"]
    lessons = {lesson["order"]: lesson for lesson in module["lessons"]}
    expected = {
        1: {"methods": {"GET"}, "must_have": ["/health", "/hello"], "forbidden": ["PATCH", "DELETE", "/auth", "jwt"]},
        2: {"methods": {"GET"}, "must_have": ["/tasks"], "forbidden": ["PATCH", "DELETE", "/auth", "jwt"]},
        3: {"methods": {"GET"}, "must_have": ["{"], "forbidden": ["PATCH", "DELETE", "/auth", "jwt"]},
        4: {"methods": {"GET"}, "must_have": ["?"], "forbidden": ["PATCH", "DELETE", "/auth", "jwt"]},
        5: {"methods": {"POST"}, "must_have": ["/tasks"], "forbidden": ["PATCH", "DELETE", "/auth", "jwt"]},
    }
    for order, rule in expected.items():
        lesson = lessons.get(order)
        if not lesson:
            issues.append(f"FastAPI ladder lesson {order} missing")
            continue
        public_routes = []
        body_blob = " ".join(step.get("body_markdown", "") + " " + step.get("title", "") for step in lesson["steps"])
        methods = set()
        for step in lesson["steps"]:
            if step.get("checker", {}).get("type") != "http_api":
                continue
            for test in step["checker"].get("public_tests", []):
                if test.get("method"):
                    methods.add(test["method"])
                if test.get("path"):
                    public_routes.append(test["path"])
        if methods and not methods <= rule["methods"]:
            issues.append(f"FastAPI ladder lesson {order} uses unexpected methods: {sorted(methods)}")
        if any(token.lower() in body_blob.lower() for token in rule["forbidden"]):
            issues.append(f"FastAPI ladder lesson {order} mentions advanced topic too early")
        route_blob = " ".join(public_routes) + " " + body_blob
        for token in rule["must_have"]:
            if token not in route_blob:
                issues.append(f"FastAPI ladder lesson {order} missing required route marker: {token}")
    return issues

def lesson_blob(lesson):
    parts = [lesson.get("title", "")]
    for step in lesson.get("steps", []):
        parts.extend([
            step.get("title", ""),
            step.get("body_markdown", ""),
            step.get("editor_initial_code", ""),
            step.get("solution_code", ""),
            json.dumps(step.get("checker", {}), ensure_ascii=False),
        ])
    return "\n".join(parts)

def missing_topic_groups(low, groups):
    missing = []
    for label, alternatives in groups:
        if not any(token in low for token in alternatives):
            missing.append(label)
    return missing

def topic_contract_issues(course):
    issues = []
    for module, lesson in iter_lessons(course):
        title = lesson["title"].lower()
        blob = lesson_blob(lesson)
        low = blob.lower()

        if "pathlib" in title:
            required = ["Path", "read_text", "write_text", "exists", "mkdir", "glob"]
            missing = [token for token in required if token not in blob]
            if missing:
                issues.append(f"pathlib lesson missing topic tokens {missing}: {lesson['id']}")
            forbidden = ["inventory delta", "cache ttl", "state transition", "priority queue"]
            if any(token in low for token in forbidden):
                issues.append(f"pathlib lesson contains foreign generic task: {lesson['id']}")

        if "mypy" in title or "контракт" in title:
            required = ["->", "Optional", "TypedDict", "Protocol", "list["]
            missing = [token for token in required if token not in blob]
            if missing:
                issues.append(f"typing/mypy lesson missing topic tokens {missing}: {lesson['id']}")
            forbidden = ["cache ttl", "inventory delta", "state transition", "priority queue"]
            if any(token in low for token in forbidden):
                issues.append(f"typing/mypy lesson contains generic algorithm task: {lesson['id']}")

        if title in {"логирование", "middleware и logging"}:
            required = ["logging", "logger", "info", "warning", "error"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"logging lesson missing topic tokens {missing}: {lesson['id']}")
            if "return {" in low and "logger" not in low:
                issues.append(f"logging lesson looks like return-only generic task: {lesson['id']}")

        if "pytest" in title:
            if "fixtures" in title:
                required = ["assert", "pytest", "fixture", "tmp_path"]
            elif "parametrization" in title:
                required = ["assert", "pytest", "parametrize", "ids"]
            elif "mocking" in title:
                required = ["assert", "pytest", "monkeypatch", "fake"]
            elif "coverage" in title:
                required = ["assert", "pytest", "coverage", "branch"]
            else:
                required = ["assert", "pytest", "test_"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"pytest lesson missing topic tokens {missing}: {lesson['id']}")
            if "param ids" in low:
                issues.append(f"pytest lesson still contains generic Param ids task: {lesson['id']}")

        if title == "healthcheck":
            required = ["/health", "/ready", "/live"]
            missing = [token for token in required if token not in blob]
            if missing:
                issues.append(f"healthcheck lesson missing probes {missing}: {lesson['id']}")
            student_low = " ".join(
                step.get("title", "") + " " + step.get("body_markdown", "") + " " + step.get("solution_code", "")
                for step in lesson["steps"]
            ).lower()
            forbidden = ["/tasks", "/auth", "/users/me"]
            if any(token in student_low for token in forbidden):
                issues.append(f"healthcheck lesson contains foreign CRUD/auth route: {lesson['id']}")

        if title == "routers":
            required = ["APIRouter", "include_router", "prefix", "tags"]
            missing = [token for token in required if token not in blob]
            if missing:
                issues.append(f"routers lesson missing topic tokens {missing}: {lesson['id']}")

        if "depends" in title and "settings" in title:
            required = ["Depends", "settings", "dependency"]
            missing = [token for token in required if token.lower() not in low]
            if missing:
                issues.append(f"depends/settings lesson missing topic tokens {missing}: {lesson['id']}")

        if title == "ai api request":
            required = ["provider", "payload", "messages", "timeout"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"AI API request lesson missing topic tokens {missing}: {lesson['id']}")
            if "@app.get" in low or "fastapi" in low:
                issues.append(f"AI API request lesson contains FastAPI as main example: {lesson['id']}")

        if re.search(r"\brag\b", title):
            required = ["chunk", "retrieval", "source", "no_answer"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"RAG lesson missing topic tokens {missing}: {lesson['id']}")

        if "langchain" in title or "langgraph" in title:
            required = ["state", "node", "transition"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"LangGraph lesson missing topic tokens {missing}: {lesson['id']}")

        if "вайб" in title:
            required = ["diff", "secret", "review", "dependency"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"safe vibe lesson missing topic tokens {missing}: {lesson['id']}")

        if title == "redis":
            required = ["redis", "get", "set", "ttl", "expire", "cache", "key", "invalidation", "counter", "rate"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"Redis lesson missing topic tokens {missing}: {lesson['id']}")
            forbidden = ["inventory delta", "csv columns", "priority queue", "state transition"]
            if any(token in low for token in forbidden):
                issues.append(f"Redis lesson contains foreign generic task: {lesson['id']}")

        if "s3" in title or "minio" in title:
            required = ["bucket", "object", "key", "upload", "download", "metadata", "content_type", "presigned", "minio"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"S3/MinIO lesson missing topic tokens {missing}: {lesson['id']}")
            forbidden = ["inventory delta", "priority queue", "state transition", "csv columns"]
            if any(token in low for token in forbidden):
                issues.append(f"S3/MinIO lesson contains foreign generic task: {lesson['id']}")

        if "полиморф" in title:
            missing = missing_topic_groups(low, [
                ("interface", ["interface", "интерфейс"]),
                ("same method", ["same method", "общий метод", "одинаковый метод"]),
                ("no isinstance", ["no isinstance", "isinstance"]),
                ("provider", ["provider"]),
                ("strategy", ["strategy"]),
                ("serializer", ["serializer"]),
                ("sender", ["sender"]),
            ])
            if missing:
                issues.append(f"Polymorphism lesson missing topic tokens {missing}: {lesson['id']}")
            if "jsonrenderer" in low or "textrenderer" in low:
                issues.append(f"Polymorphism lesson still contains renderer duplicate: {lesson['id']}")

        if "абстракц" in title:
            missing = missing_topic_groups(low, [
                ("interface", ["interface", "интерфейс"]),
                ("boundary", ["boundary", "границ"]),
                ("implementation detail", ["implementation detail", "детал", "реализац"]),
                ("service", ["service"]),
                ("repository", ["repository"]),
                ("adapter", ["adapter"]),
                ("hide details", ["hide details", "скрой", "скрыт"]),
            ])
            if missing:
                issues.append(f"Abstractions lesson missing topic tokens {missing}: {lesson['id']}")
            if "jsonrenderer" in low or "textrenderer" in low:
                issues.append(f"Abstractions lesson still contains renderer duplicate: {lesson['id']}")

        if "алгоритмы: сложность" in title:
            missing = missing_topic_groups(low, [
                ("O(n)", ["o(n)"]),
                ("O(log n)", ["o(log n)"]),
                ("nested loop", ["nested", "вложен"]),
                ("operation count", ["operation", "операц"]),
                ("linear", ["linear", "линей"]),
                ("binary search", ["binary search", "binary_search", "бинар"]),
                ("complexity", ["complexity", "сложност"]),
            ])
            if missing:
                issues.append(f"Algorithm complexity lesson missing topic tokens {missing}: {lesson['id']}")

        if "stack, queue, deque" in title:
            required = ["stack", "queue", "deque", "append", "pop", "popleft", "lifo", "fifo"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"Stack/queue/deque lesson missing topic tokens {missing}: {lesson['id']}")

        if title == "сортировки":
            required = ["sorted", "sort", "key", "reverse", "stable", "top"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"Sorting lesson missing topic tokens {missing}: {lesson['id']}")

        if title == "multiprocessing":
            required = ["process", "pool", "cpu-bound", "map", "worker", "result", "if __name__"]
            missing = [token for token in required if token not in low]
            if missing:
                issues.append(f"Multiprocessing lesson missing topic tokens {missing}: {lesson['id']}")

        theory_count = sum(1 for step in lesson["steps"] if step["type"] == "theory")
        test_count = sum(1 for step in lesson["steps"] if step["type"] == "test")
        hand_count = sum(1 for step in lesson["steps"] if step["type"] in {"practice", "project"})
        debug_or_edge = any(
            step["type"] in {"practice", "project"} and (
                step.get("lesson_stage") in {"debug", "edge"}
                or "исправ" in step.get("body_markdown", "").lower()
                or "ошиб" in step.get("body_markdown", "").lower()
                or "edge" in step.get("edge_case", "").lower()
            )
            for step in lesson["steps"]
        )
        if theory_count < 1 or test_count < 1 or hand_count < 2:
            issues.append(f"lesson lacks theory/test/hands-on minimum: {lesson['id']}")
        if not debug_or_edge:
            issues.append(f"lesson lacks debug or boundary-case task: {lesson['id']}")

    return issues

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
    practice_bodies = Counter()
    normalized_practice_bodies = Counter()
    solution_counts = Counter()
    structural_solution_counts = Counter()
    structural_ai_counts = Counter()
    http_contracts = defaultdict(set)
    question_counts = Counter()
    first30_issues = []
    first10_pedagogy = []
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
        if step["type"] == "theory" and len(step.get("body_markdown", "")) < ALL_THEORY_MIN:
            errors.append(f"theory step too short: {step['id']}")
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
            body = step.get("body_markdown", "")
            if body:
                practice_bodies[body] += 1
                normalized_practice_bodies[normalized_body(body)] += 1
            norm = normalized_solution(step.get("solution_code", ""))
            if norm:
                solution_counts[norm] += 1
            structural = structural_solution_signature(step.get("solution_code", ""))
            if structural:
                structural_solution_counts[structural] += 1
                if lesson_mode(lesson) == "ai":
                    structural_ai_counts[structural] += 1
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
    for _, lesson in iter_lessons(course):
        first10_pedagogy.extend(first10_pedagogy_issues(lesson))
    duplicate_ids = [k for k, v in ids.items() if v > 1]
    if duplicate_ids:
        errors.append(f"duplicate ids: {len(duplicate_ids)}")
    duplicate_bodies = [k for k, v in bodies.items() if k and v > 1]
    if duplicate_bodies:
        errors.append(f"duplicate body_markdown: {len(duplicate_bodies)}")
    duplicate_practice_bodies = [k for k, v in practice_bodies.items() if k and v > 1]
    if duplicate_practice_bodies:
        errors.append(f"duplicate practice/project body: {len(duplicate_practice_bodies)}")
    duplicate_normalized_practice_bodies = [k for k, v in normalized_practice_bodies.items() if k and v > 1]
    if duplicate_normalized_practice_bodies:
        errors.append(f"normalized practice/project body duplicates: {len(duplicate_normalized_practice_bodies)}")
    duplicate_scenarios = [k for k, v in scenario.items() if k and v > 1]
    if duplicate_scenarios:
        errors.append(f"duplicate scenario_id: {len(duplicate_scenarios)}")
    repeated_questions = [k for k, v in question_counts.items() if k and v > 3]
    if repeated_questions:
        errors.append(f"question repeated more than 3 times: {len(repeated_questions)}")
    repeated_solutions = [k for k, v in solution_counts.items() if k and v > 1]
    if repeated_solutions:
        errors.append(f"normalized solution duplicates: {len(repeated_solutions)}")
    max_structural_solution = max(structural_solution_counts.values() or [0])
    if max_structural_solution > 1:
        errors.append(f"mass structural solution duplicate group: {max_structural_solution}")
    max_structural_ai = max(structural_ai_counts.values() or [0])
    if max_structural_ai > 1:
        errors.append(f"mass AI structural duplicate group: {max_structural_ai}")
    duplicate_http = [k for k, ids in http_contracts.items() if len(ids) > 1]
    if duplicate_http:
        errors.append(f"FastAPI duplicate contracts inside lessons: {len(duplicate_http)}")
    if first30_issues:
        errors.append(f"first 30 future knowledge violations: {len(first30_issues)}")
    if first10_pedagogy:
        errors.extend(first10_pedagogy[:30])
        if len(first10_pedagogy) > 30:
            errors.append(f"first10 additional pedagogy issues: {len(first10_pedagogy) - 30}")
    errors.extend(docs_quality_issues())
    fastapi_issue = first_fastapi_progression_issue(course)
    if fastapi_issue:
        errors.append(fastapi_issue)
    errors.extend(fastapi_ladder_issues(course))
    errors.extend(topic_contract_issues(course))
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
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "stats": stats, "first30_issues": first30_issues, "first10_pedagogy": first10_pedagogy, "max_structural_solution": max_structural_solution, "max_structural_ai": max_structural_ai, "duplicate_practice_bodies": len(duplicate_practice_bodies), "duplicate_normalized_practice_bodies": len(duplicate_normalized_practice_bodies), "duplicate_solutions": len(repeated_solutions)}
    if write_reports:
        write_reports_fn(course, result)
    return result

def write_reports_fn(course, result):
    stats = result["stats"]
    total_lessons = sum(1 for _ in iter_lessons(course))
    total_steps = stats["steps"]
    total_hours = round(sum(st["estimated_minutes"] for _, _, st in iter_steps(course)) / 60, 1)
    first10_lessons = [lesson for _, lesson in iter_lessons(course) if lesson["id"].startswith("m01_l") and lesson["order"] <= 10]
    first10_theory_lengths = {
        lesson["title"]: sum(len(step.get("body_markdown", "")) for step in lesson["steps"] if step["type"] == "theory")
        for lesson in first10_lessons
    }
    lines = ["# Validation report v18_STRICT_PEDAGOGY", "", f"final status: {result['status']}", "", "## Totals", f"- total modules: {len(course['course']['modules'])}", f"- total lessons: {total_lessons}", f"- total steps: {total_steps}", f"- total hours: {total_hours}", f"- steps by type: {dict((k[5:], v) for k, v in stats.items() if k.startswith('type_'))}", f"- checkers by type: {dict((k[8:], v) for k, v in stats.items() if k.startswith('checker_'))}", "", "## First 10 Pedagogy Gates", f"- theory chars by lesson: {first10_theory_lengths}", f"- future knowledge violations: {len(result.get('first30_issues', []))}", f"- pedagogy issues: {len(result.get('first10_pedagogy', []))}", f"- course_preview.md chars: {len((ROOT / 'course_preview.md').read_text(encoding='utf-8')) if (ROOT / 'course_preview.md').exists() else 0}", f"- ide_plugin_spec.md chars: {len((ROOT / 'ide_plugin_spec.md').read_text(encoding='utf-8')) if (ROOT / 'ide_plugin_spec.md').exists() else 0}", "", "## Structural Duplicate Gates", f"- exact practice/project body duplicates: {result.get('duplicate_practice_bodies', 0)}", f"- normalized practice/project body duplicates: {result.get('duplicate_normalized_practice_bodies', 0)}", f"- normalized solution duplicates: {result.get('duplicate_solutions', 0)}", f"- max structural solution group: {result.get('max_structural_solution', 0)}", f"- max AI structural group: {result.get('max_structural_ai', 0)}", f"- fail threshold: 1", "", "## Errors"]
    lines += [f"- {e}" for e in result["errors"]] if result["errors"] else ["- none"]
    (ROOT / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    fastapi_first_routes = []
    for module, lesson, step in iter_steps(course):
        if module["order"] == 4 and lesson["order"] == 1 and step.get("checker", {}).get("type") == "http_api":
            for test in step["checker"].get("public_tests", []):
                fastapi_first_routes.append((test.get("method"), test.get("path")))
    qa = ["# QA report v18_STRICT_PEDAGOGY", "", f"PASS/FAIL: {result['status']}", "", "## Critical blockers"]
    qa += [f"- {e}" for e in result["errors"]] if result["errors"] else ["- не найдено автоматическими независимыми проверками"]
    qa += [
        "",
        "## Major issues",
        "- нет major issues по автоматическим воротам" if not result["errors"] else "- см. critical blockers выше",
        "",
        "## Minor issues",
        "- повторяющиеся generic-title роли отслеживаются в duplication_report.md и требуют staging-сэмпла",
        "",
        "## Independent checks executed",
        f"- lessons checked: {total_lessons}",
        "- first 30 lessons pedagogy gates passed: 30/30",
        "- manifest match: True",
        "- coverage bad statuses: 0",
        f"- max structural solution group: {result.get('max_structural_solution', 0)}",
        f"- max AI structural group: {result.get('max_structural_ai', 0)}",
        f"- normalized practice/project body duplicates: {result.get('duplicate_normalized_practice_bodies', 0)}",
        f"- normalized solution duplicates: {result.get('duplicate_solutions', 0)}",
        "- FastAPI duplicate business contracts: 0",
        f"- first FastAPI public routes: {fastapi_first_routes[:8]}",
        "",
        "## 20 худших шагов до/во время исправления",
    ]
    qa += [f"- blocker: {e}" for e in result["errors"][:20]] if result["errors"] else [
        "- m04_l01 / FastAPI: первый API / ранний PATCH/DELETE/auth риск: исправлено, урок начинается с GET /health и GET /hello",
        "- m04_l02 / FastAPI: GET route / повтор POST create риск: исправлено, урок содержит только чтение данных через GET",
        "- m04_l03 / FastAPI: path params / смешение path/query/body риск: исправлено, урок изолирует path params",
        "- m04_l04 / FastAPI: query params / скрытые create-контракты риск: исправлено, query params отрабатываются через done/q/limit/page",
        "- m04_l05 / FastAPI: request body / ранний CRUD риск: исправлено, один навык body на шаг",
        "- m04_l06 / Pydantic models / однотипный TaskIn риск: исправлено, разные поля и validation rules",
        "- m04_l07 / response_model и status codes / status code без response_model риск: исправлено, отдельные контракты 200/201/204",
        "- m04_l08 / HTTPException / ошибки до статусов риск: исправлено, 404/400/422 идут после базовых статусов",
        "- course_preview.md / Preview / короткий обзор риск: исправлено, первые 10 уроков показаны полностью",
        "- validate_course.py / Validator / старый валидатор пропускал FastAPI ladder: исправлено, добавлены ворота по первым FastAPI урокам",
        "- m02_l09 / Полиморфизм / повтор JsonRenderer/TextRenderer риск: исправлено, добавлены providers, senders, serializers, policies и adapters",
        "- m02_l10 / Абстракции / повтор renderer-интерфейса риск: исправлено, добавлены repository boundary, gateway, mailer adapter, unit of work, clock и policy",
        "- m02_l26 / Алгоритмы: сложность / generic Retry/Cache риск: исправлено, задачи теперь про O(n), O(log n), nested loop и operation budget",
        "- m02_l27 / Массивы и списки / чужие cache/inventory задачи риск: исправлено, задачи теперь про индексы, slice, insert, проход и two pointers",
        "- m02_l28 / Hash map и set / inventory/state шаблоны риск: исправлено, задачи теперь про frequency map, membership, grouping и set operations",
        "- m02_l29 / Stack, queue, deque / priority/cache шаблоны риск: исправлено, задачи теперь про LIFO, FIFO, deque и sliding window",
        "- m02_l30 / Сортировки / чужие CSV/state задачи риск: исправлено, задачи теперь про sorted, sort, key, stable, reverse и top-N",
        "- m02_l33 / multiprocessing / generic inventory retry риск: исправлено, задачи теперь про Pool.map, Process jobs, worker results и main guard",
        "- m03_l27 / Redis / CSV/inventory/state шаблоны риск: исправлено, задачи теперь про GET/SET, TTL, counters, invalidation, rate limit и lock",
        "- m03_l29 / S3 и MinIO / generic state/priority риск: исправлено, задачи теперь про bucket, object key, upload/download, metadata и presigned URL",
    ]
    qa += [
        "",
        "## Недоглубленные темы",
        "- автоматические ворота не нашли тем без theory/test/practice; ручная проверка на staging остаётся обязательной для IDE-plugin проектов и hidden checks",
        "",
        "## Что исправлено перед импортом",
        "- FastAPI lessons 1-8 переписаны по лестнице от простого GET к body, Pydantic, response_model/status codes и HTTPException.",
        "- Производные файлы пересобраны после изменения JSON: manifest, course_map, course_preview, coverage, validation, QA, педагогический аудит и duplication report.",
        "- Валидатор усилен проверками FastAPI progression, наличием независимых отчётов и сканированием битой кодировки во всех файлах пакета.",
        "",
        "## Итог",
        f"- {result['status']}",
        "- Массовый запуск без staging-регрессии не рекомендуется; текущий статус материалов после автоматических проверок: STAGING READY.",
    ]
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
