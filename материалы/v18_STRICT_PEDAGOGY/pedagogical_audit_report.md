# Pedagogical audit report v18_STRICT_PEDAGOGY

Отчёт проверяет учебную лестницу по JSON. Он не заменяет ручное прохождение на staging, но фиксирует автоматические педагогические ворота.

## Totals
- total lessons checked: 169
- total steps checked: 1960
- steps by type: {'practice': 831, 'project': 328, 'summary': 169, 'test': 294, 'theory': 338}
- first 30 lessons checked: 30
- first 30 lessons with theory/test/practice gates passed: 30
- body leaks found: 0
- max structural duplicate group: 18

## Weak lessons before fixes
- Модуль 4 / FastAPI: первый API: FastAPI started too abruptly or mixed later API concepts into early lessons.
- Модуль 4 / FastAPI: GET route: FastAPI started too abruptly or mixed later API concepts into early lessons.
- Модуль 4 / FastAPI: path params: FastAPI started too abruptly or mixed later API concepts into early lessons.
- Модуль 4 / FastAPI: query params: FastAPI started too abruptly or mixed later API concepts into early lessons.
- Модуль 4 / FastAPI: request body: FastAPI started too abruptly or mixed later API concepts into early lessons.
- Модуль 4 / Pydantic models: FastAPI started too abruptly or mixed later API concepts into early lessons.
- Модуль 4 / response_model и status codes: FastAPI started too abruptly or mixed later API concepts into early lessons.
- Модуль 4 / HTTPException: FastAPI started too abruptly or mixed later API concepts into early lessons.

## Weak lessons after fixes
- 0 by the automated gates added in `validate_course.py`.
- Remaining risk is manual: staging must sample complete student flow, especially hidden checks and IDE-plugin projects.

## Lessons rewritten
- Модуль 4 / FastAPI: первый API
- Модуль 4 / FastAPI: GET route
- Модуль 4 / FastAPI: path params
- Модуль 4 / FastAPI: query params
- Модуль 4 / FastAPI: request body
- Модуль 4 / Pydantic models
- Модуль 4 / response_model и status codes
- Модуль 4 / HTTPException

## Examples of fixed lessons
- `FastAPI: первый API`: now starts from `GET /health`, `GET /hello`, exact response shapes, one-line diagnostics and negative method checks.
- `FastAPI: path params`: now isolates path parameters before request body, auth, database or Docker.
- `FastAPI: query params`: now uses `done`, `q`, `limit`, `kind`, `active`, `page/size` instead of repeating POST create tasks.
- `HTTPException`: now checks 404/400/422 behavior only after status codes and models were introduced.

## First 30 lesson gate sample
- Первый код: PASS
- Ввод и числа: PASS
- Строки: PASS
- bool и None: PASS
- Условия: PASS
- Типы и память: PASS
- Циклы: PASS
- Списки: PASS
- Функции: PASS
- Кортежи: PASS
- Множества: PASS
- Словари: PASS
- map/filter/lambda: PASS
- datetime: PASS
- Итераторы: PASS
- Генераторы: PASS
- Декораторы: PASS
- Контекстные менеджеры: PASS
- Исключения: PASS
- AI для учёбы: PASS
- Как работает компьютер: PASS
- Терминал: базовые команды: PASS
- Терминал: процессы и bash: PASS
- Git: первые коммиты: PASS
- Git: индекс и история: PASS
- Git: ветки: PASS
- Git: отмена изменений: PASS
- Git: merge и rebase: PASS
- GitHub и remote: PASS
- CLI-проект: менеджер задач: PASS

## Remaining risks
- STAGING regression is still required: import the migration, pass the first 10 lessons as a student, and manually sample 50-100 later steps.
- Some repeated generic titles remain by role. They are tracked in `duplication_report.md` and must stay below structural duplicate thresholds.

## Final status
- STAGING READY
