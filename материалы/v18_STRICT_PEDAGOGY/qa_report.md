# QA report v18_STRICT_PEDAGOGY

PASS/FAIL: PASS

## Critical blockers
- не найдено

## Independent checks
- first 10 lessons theory length and examples are checked from JSON;
- first 30 lessons prerequisite gate is enforced;
- body leaks and encoding corruption are hard fail;
- manifest and coverage are checked independently;
- course_preview.md and ide_plugin_spec.md have minimum useful length gates;
- SQL/FastAPI/AI/OOP topic gates are checked from JSON, not from validation_report.md.

## 20 худших шагов
- автоматический аудит не нашёл критичных кандидатов в первых 10 уроках; ручная staging-проверка остаётся обязательной.

## Недоглубленные темы
- если PASS: автоматический аудит не нашёл недоглубления по заданным hard gates;
- если FAIL: см. critical blockers выше.

## Итог
PASS означает, что пакет прошёл автоматические педагогические и структурные ворота. Перед массовым запуском остаётся staging-regression: импорт, первые 10 уроков как студент и выборка 50-100 шагов.
