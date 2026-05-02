# Release checklist v16

## Автоматическая проверка
- [ ] `python validate_course.py` возвращает PASS.
- [ ] `duplicate_body_count = 0`.
- [ ] `duplicate_learning_objectives = 0`.
- [ ] `duplicate_question_over_limit = 0`.
- [ ] `duplicate_scenario_ids = 0`.
- [ ] `lesson_duplicate_normalized_body = 0`.
- [ ] `lesson_duplicate_normalized_solution = 0`.
- [ ] `lesson_duplicate_checker_signature = 0`.
- [ ] `course_duplicate_normalized_solution = 0`.
- [ ] `lesson_duplicate_normalized_test_code = 0`.
- [ ] `course_duplicate_normalized_test_code = 0`.
- [ ] `duplicate_sql_practice_query = 0`.
- [ ] `duplicate_sql_checker_dataset = 0`.
- [ ] `fastapi_endpoint_template_reuse = 0`.
- [ ] `fastapi_route_model_signature_reuse = 0`.
- [ ] `python_key_skill_mismatch = 0`.
- [ ] `algorithmic_pattern_over_limit = 0`.
- [ ] `missing_step_focus_fields = 0`.
- [ ] `template_test_questions = 0`.
- [ ] `body_service_sections = 0`.
- [ ] `ai_structural_solution_duplicates = 0`.
- [ ] `ai_quality_violations = 0`.
- [ ] `sql_progression_violations = 0`.
- [ ] `fastapi_lesson_business_duplicates = 0`.
- [ ] `fastapi_title_method_mismatches = 0`.
- [ ] `fastapi_solution_method_mismatches = 0`.
- [ ] `http_body_checker_mismatch = 0`.
- [ ] `artificial_uniqueness_markers = 0`.
- [ ] `placeholder_focus_fields = 0`.
- [ ] `template_question_signature_repeats = 0`.
- [ ] `generic_test_questions = 0`.
- [ ] `bad_stage_content = 0`.
- [ ] `short_complex_theory = 0`.
- [ ] `weak_project_solutions = 0`.
- [ ] Empty solution_code у practice/project = 0.
- [ ] Первый урок — `Первый код`.
- [ ] Manifest совпадает с JSON.
- [ ] Coverage matrix не содержит missing/thin/placeholder.
- [ ] SQL transactions содержит BEGIN/COMMIT/ROLLBACK/ROLLBACK TO.
- [ ] FastAPI healthcheck возвращает объект.
- [ ] Docker/final tasks имеют runtime checks, dry-run и rollback.
- [ ] lesson ladder stage gaps = 0: каждый урок содержит why, example, understanding, practice, debug, edge, integration, mini_project, summary.
- [ ] Каждый test-step содержит минимум 3 structured questions.
- [ ] AI/RAG уроки не содержат обычные Python-задачи под видом AI-интеграции.
- [ ] Сложные уроки Git/SQL/FastAPI/DevOps/AI/final имеют усиленную длину и debugging/integration шаги.

## Почему добавлены gates текущей версии
Эти проверки нужны, чтобы ревьюер видел: курс не проходит за счёт разных формулировок одного и того же решения. Сейчас валидатор отдельно проверяет уникальность solution-кода, pytest-кода, SQL-запросов, SQL dataset, FastAPI route/model/checker signatures, algorithmic patterns и явные поля `skill_focus`, `new_constraint`, `edge_case`, `input_shape`, `output_contract`. Current hard gates also check student-facing body leaks, FastAPI route/method alignment with http_api checker, absence of marker/comment uniqueness hacks, non-placeholder focus fields, repeated quiz templates after lesson-title removal, and stricter normalized solution uniqueness. This is necessary so a reviewer sees that the package is not passing because of wording noise, ids or generated markers.

## QA-регламент после импорта
- [ ] Импортировать пакет на staging.
- [ ] Сравнить количество уроков и шагов с `manifest.csv`.
- [ ] Ручно пройти первые 10 уроков как студент.
- [ ] Выборочно проверить 50-100 шагов: Python, Git, SQL, SQLite, FastAPI, Docker, final gates.
- [ ] Запустить IDE-плагин на реальном проекте для Git, Docker, FastAPI и final gate.
- [ ] Пройти один полный финальный проект от ТЗ до защиты.
- [ ] Проверить hidden tests на пустые значения, неверные типы, 401/404/422, SQL injection, отсутствие ORDER BY, грязное git-дерево и отсутствие env/healthcheck.
- [ ] Провести dry-run наставников: 10 типовых вопросов, 5 жалоб на hidden tests, 3 восстановления отстающих студентов.

## Дополнительный gate после исправления кодировки
- [ ] `encoding_corruption = 0` в `validation_report.md`.
- [ ] `package_file_corruption = 0` в `validation_report.md`.
- [ ] `ai_aggressive_solution_duplicates = 0`.
- [ ] `fastapi_method_path_status_duplicates = 0`.
- [ ] Первые 30 уроков проверены отдельно: нет битых символов, нет future-knowledge violations, нет practice/project без проверки.
- [ ] В `body_markdown` не встречаются серии вопросительных знаков вместо текста, replacement character, `Сценарий:`, `Сценарий практики`, `Сценарий шага`.
- [ ] `/admin/users` не используется в student-facing тексте; для учебного staff-доступа применяется `/staff/users`.

Почему это добавлено сейчас: прежний PASS не ловил реальные битые вопросительные знаки в JSON и отчётах. Новый gate защищает массовый запуск от ситуации, когда импорт технически проходит, но студент видит битый текст или получает однообразные AI/FastAPI/SQL задания под разными названиями.
