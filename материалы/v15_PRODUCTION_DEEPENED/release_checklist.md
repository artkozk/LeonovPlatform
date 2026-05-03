# Release checklist v15

## Автоматическая проверка
- [ ] `python validate_course.py` возвращает PASS.
- [ ] `duplicate_body_count = 0`.
- [ ] `duplicate_learning_objectives = 0`.
- [ ] Empty solution_code у practice/project = 0.
- [ ] Первый урок — `Первый код`.
- [ ] Manifest совпадает с JSON.
- [ ] Coverage matrix не содержит missing/thin/placeholder.
- [ ] SQL transactions содержит BEGIN/COMMIT/ROLLBACK/ROLLBACK TO.
- [ ] FastAPI healthcheck возвращает объект.
- [ ] Docker/final tasks имеют runtime checks, dry-run и rollback.

## QA-регламент после импорта
- [ ] Импортировать пакет на staging.
- [ ] Сравнить количество уроков и шагов с `manifest.csv`.
- [ ] Ручно пройти первые 10 уроков как студент.
- [ ] Выборочно проверить 50-100 шагов: Python, Git, SQL, SQLite, FastAPI, Docker, final gates.
- [ ] Запустить IDE-плагин на реальном проекте для Git, Docker, FastAPI и final gate.
- [ ] Пройти один полный финальный проект от ТЗ до защиты.
- [ ] Проверить hidden tests на пустые значения, неверные типы, 401/404/422, SQL injection, отсутствие ORDER BY, грязное git-дерево и отсутствие env/healthcheck.
- [ ] Провести dry-run наставников: 10 типовых вопросов, 5 жалоб на hidden tests, 3 восстановления отстающих студентов.
