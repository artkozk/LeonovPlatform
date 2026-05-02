# Инструкция импорта v16_LESSON_LADDER

1. Запусти `python validate_course.py`.
2. Импортируй только `course_import.json`.
3. Markdown-preview не является источником для платформы.
4. После импорта сравни уроки и шаги с `manifest.csv`.
5. Если импортёр сортирует не по `order`, исправь импортёр до запуска потока.
6. Скрытые поля `solution_code`, `checker`, `ai_review_config`, `admin_notes` не показываются студенту.

## Обязательная проверка перед staging

После исправления кодировки импорт запрещён, если `python validate_course.py` не показывает:

- `encoding_corruption=0`;
- `package_file_corruption=0`;
- `ai_aggressive_dups=0`;
- `fastapi_mps_dups=0`;
- `sql_progression=0`;
- `http_body_mismatch=0`.

Это нужно потому, что старый smoke-pass мог не заметить битые вопросительные знаки в student-facing полях, повторяющиеся AI-скелеты или одинаковые FastAPI-контракты внутри урока. Теперь импорт считается безопасным только после проверки JSON, Markdown/CSV отчётов, первых 30 уроков и соответствия `manifest.csv`.
