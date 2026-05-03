# Инструкция импорта v14_CONTENT_POLISHED

1. Запусти `python validate_course.py`.
2. Импортируй только `course_import.json`.
3. Markdown-preview не является источником для платформы.
4. После импорта сравни уроки и шаги с `manifest.csv`.
5. Если импортёр сортирует не по `order`, исправь импортёр до запуска потока.
6. Скрытые поля `solution_code`, `checker`, `ai_review_config`, `admin_notes` не показываются студенту.
