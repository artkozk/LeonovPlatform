# Python v18 Strict Pedagogy Rollout — 2026-05-03

## 1. Контекст

Пакет `материалы/v18_STRICT_PEDAGOGY` нужно внедрить в работающую платформу как актуальный курс `python-zero`.

Цель rollout:

1. Заменить опубликованный учебный контент курса `python-zero` на v18.
2. Сохранить существующий runtime платформы: уроки, блоки, задачи, quiz, run/submit, AI-подсказки и IDE/project-check данные.
3. Не смешивать старые v16/v10 блоки с новой педагогической версией.

Почему это делается через миграцию:

1. Миграция воспроизводима и проверяема в code review.
2. Production получает один атомарный reseed вместо ручного импорта через UI.
3. Старые записи не удаляются физически, а снимаются с публикации через `is_published=false`, поэтому rollback остаётся возможным на уровне backup/миграционного состояния.

## 2. Источник данных

Единый источник курса:

1. `материалы/v18_STRICT_PEDAGOGY/course_import.json`

Проверенные метрики источника:

1. modules: 5
2. lessons: 169
3. steps: 1963
4. practice: 815
5. project: 338
6. quiz/test steps: 304
7. questions: 912
8. estimated hours: 678.9

Курс начинается с:

1. Модуль 1.
2. Урок 1: `Первый код`.
3. Шаг 1: `Смысл`.

Это важно, потому что студент должен сначала написать и запустить самый простой Python-код, а AI, терминал и Git идут только после базового входа в Python.

## 3. Что изменено

### 3.1 Генератор миграции

Добавлен инструмент:

1. `backend/tools/generate_python_v18_materials_migration.js`

Он читает `course_import.json` из `v18_STRICT_PEDAGOGY` и создаёт runtime-совместимую SQL-миграцию.

Почему нужен отдельный генератор, а не повторное использование v16:

1. Путь источника другой.
2. В `source_policy.import_source` должен быть точный путь v18, чтобы диагностировать происхождение задачи.
3. Имя и комментарии миграции должны отражать конкретный rollout, иначе в production сложно отличить старую поставку от новой.

### 3.2 Миграция

Добавлена миграция:

1. `backend/migrations/026_reseed_python_zero_v18_strict_pedagogy.sql`

Что делает миграция:

1. Обновляет `courses.slug='python-zero'`.
2. Переопубликовывает 5 модулей и 169 уроков.
3. Снимает с публикации старые blocks/tasks этого курса.
4. Вставляет новые `lesson_blocks`.
5. Вставляет practice/project как `tasks`.
6. Вставляет public/hidden executable test cases для `python_stdout` и `sql_query`.
7. Переносит checker configs в `tasks.source_policy`.
8. Публикует test steps как `lesson_blocks.block_type='quiz'` с `quiz_payload.questions[]`.

### 3.3 Валидация миграции

Добавлен инструмент:

1. `backend/tools/validate_python_v18_materials_import.js`

Отчёт:

1. `docs/operations/PYTHON_V18_STRICT_PEDAGOGY_IMPORT_VALIDATION_2026_05_03.md`

Проверки:

1. Количество blocks в SQL совпадает с количеством steps в JSON.
2. Количество task policy tags совпадает с practice+project.
3. Количество executable test cases совпадает с `python_stdout + sql_query`.
4. Checker counts совпадают по типам.
5. `python_pytest.test_code` преобразован в runtime key `pytest_code`.
6. `http_api.public_tests/hidden_tests` преобразованы в runtime `tests[]`.
7. Quiz payload содержит structured `questions[]`.

## 4. Проверки до deploy

Локально выполнено:

1. `python материалы/v18_STRICT_PEDAGOGY/validate_course.py` — PASS.
2. Независимый JSON-аудит v18 — PASS.
3. `node backend/tools/generate_python_v18_materials_migration.js` — PASS.
4. `node backend/tools/validate_python_v18_materials_import.js` — PASS.
5. `go test ./...` в `backend` — PASS.

Почему этих проверок достаточно до серверного rollout:

1. Runtime Go-код не меняется.
2. Изменение ограничено генератором, SQL-миграцией и документацией.
3. Совместимость checker payload проверяется до применения миграции.

## 5. Операционная инструкция

1. Запушить commit с миграцией `026`.
2. Развернуть новый release на сервер.
3. Убедиться, что `AUTO_MIGRATE=true` или вручную применить migration-chain.
4. Проверить запись `026_reseed_python_zero_v18_strict_pedagogy` в `schema_migrations`.
5. Проверить агрегаты курса:
   - modules: 5;
   - lessons: 169;
   - lesson blocks: 1963;
   - published tasks: 1153.
6. Открыть frontend и проверить курс `Python с нуля — Backend + AI`.
7. Smoke:
   - открыть первый урок `Первый код`;
   - проверить первый шаг `Смысл`;
   - открыть practice-step с редактором;
   - отправить решение;
   - открыть quiz-step;
   - проверить AI-подсказку на задаче;
   - открыть SQL/FastAPI/project шаг выборочно.

## 6. Что важно для ревью

1. Старые rollout-документы не удалялись.
2. v18 внедряется поверх платформы как отдельная миграция `026`.
3. `course_import.json` остаётся главным источником импорта, Markdown-preview не используется как источник платформы.
4. Документация явно объясняет, почему generator/validation layer нужен, а не является лишней инфраструктурой.
