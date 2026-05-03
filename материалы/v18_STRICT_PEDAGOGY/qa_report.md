# QA report v18_STRICT_PEDAGOGY

PASS/FAIL: PASS

## Critical blockers
- не найдено

## Major issues
- не найдено автоматической независимой проверкой.

## Minor issues
- Ручная редакторская вычитка всё равно нужна перед рекламным запуском: автоматический аудит не заменяет методиста.

## Independent JSON Checks
- modules: 5
- lessons: 169
- steps: 1963
- estimated hours: 678.9
- questions: 912
- practice steps: 815
- project steps: 338
- checker types: {'quiz_single': 304, 'python_stdout': 33, 'ide_plugin': 422, 'python_pytest': 357, 'sql_query': 221, 'http_api': 120}
- qmark/mojibake scan: PASS
- body leak scan: PASS
- literal `tests` in body: PASS
- manifest exact match: PASS
- coverage statuses: PASS
- first 30 prerequisite gate: PASS
- FastAPI body/checker route match: PASS
- FastAPI duplicate business contract inside lesson: PASS
- SQL progression gate: PASS
- AI semantic gate for RAG/LangGraph/safe vibe: PASS
- OOP key-skill gate: PASS

## First 30 Lessons Readiness
- 01. Первый код: PASS
- 02. Ввод и числа: PASS
- 03. Строки: PASS
- 04. bool и None: PASS
- 05. Условия: PASS
- 06. Типы и память: PASS
- 07. Циклы: PASS
- 08. Списки: PASS
- 09. Функции: PASS
- 10. Кортежи: PASS
- 11. Множества: PASS
- 12. Словари: PASS
- 13. map/filter/lambda: PASS
- 14. datetime: PASS
- 15. Итераторы: PASS
- 16. Генераторы: PASS
- 17. Декораторы: PASS
- 18. Контекстные менеджеры: PASS
- 19. Исключения: PASS
- 20. AI для учёбы: PASS
- 21. Как работает компьютер: PASS
- 22. Терминал: базовые команды: PASS
- 23. Терминал: процессы и bash: PASS
- 24. Git: первые коммиты: PASS
- 25. Git: индекс и история: PASS
- 26. Git: ветки: PASS
- 27. Git: отмена изменений: PASS
- 28. Git: merge и rebase: PASS
- 29. GitHub и remote: PASS
- 30. CLI-проект: менеджер задач: PASS

## 20 Worst Steps
- критичных кандидатов нет: автоматический аудит не нашёл битый текст, body leaks, mismatch checker/body или future-knowledge violation.

## Undergrounded Topics
- автоматический аудит не отметил thin/placeholder; ручная проверка на staging должна дополнительно пройти SQL advanced, FastAPI auth/session, Docker/CI/CD, AI RAG и финальные gates.

## Before Import
- Импортировать только `course_import.json`.
- Markdown-preview не использовать как источник импорта.
- Запустить `python validate_course.py` в каталоге пакета.
- После импорта сверить количество уроков и шагов с `manifest.csv`.
- Пройти первые 10 уроков как студент и один gate финального проекта.

## Final
PASS. Отчёт не доверяет `validation_report.md`: проверки выше выполнены по `course_import.json`, `manifest.csv` и `coverage_matrix.csv`.
