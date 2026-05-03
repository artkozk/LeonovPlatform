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

## 7. Дополнение 2026-05-03: педагогический reseed первых 10 уроков

После первичного внедрения v18 первые уроки были дополнительно проверены как материалы для ученика без опыта. Проверка показала, что технический PASS недостаточен: первый урок должен подробно объяснять программу, строку кода, `print`, скобки, кавычки, вывод и простые ошибки до практики.

Что изменено сейчас:

1. Полностью переписаны первые 10 уроков в `материалы/v18_STRICT_PEDAGOGY/course_import.json`.
2. В уроке `Первый код` убраны все будущие знания: нет `input`, `int`, `def`, списков, условий, циклов, Git, SQL, FastAPI.
3. Debug-задачи теперь имеют сломанный стартовый код в `editor_initial_code`, а не пустой редактор.
4. Mini-project шаги стали конкретными: `main.py`, `README.md`, команда запуска и ожидаемый вывод.
5. `course_preview.md` расширен: первые 10 уроков доступны полностью для методиста.
6. `ide_plugin_spec.md` расширен до практического контракта для разработчика IDE-плагина.
7. `validate_course.py` теперь падает на короткую теорию первых 10 уроков, отсутствие примеров в practice, future-knowledge violations, слабый preview/spec и повторяющиеся solution skeleton.

Почему создана новая миграция:

1. Миграция `026` уже была применена на production и находится в `schema_migrations`.
2. Изменять `026` нельзя: база не переисполнит уже применённую версию.
3. Для доставки исправленных материалов создана новая миграция `027_reseed_python_zero_v18_first10_pedagogy.sql`.

Актуальные метрики после правки:

1. modules: 5;
2. lessons: 169;
3. lesson blocks: 1960;
4. published tasks: 1159;
5. quiz steps: 294;
6. estimated hours: 674.9.

Проверки после правки:

1. `python материалы/v18_STRICT_PEDAGOGY/validate_course.py` — PASS.
2. Локальный независимый QA первых 10 уроков — PASS.
3. `node backend/tools/generate_python_v18_materials_migration.js` — PASS.
4. `node backend/tools/validate_python_v18_materials_import.js` — PASS против `027`.

Операционная инструкция теперь использует `027`, а не `026`:

1. Запушить commit с миграцией `027`.
2. Развернуть release на сервер.
3. Проверить запись `027_reseed_python_zero_v18_first10_pedagogy` в `schema_migrations`.
4. Проверить агрегаты курса: `5|169|1960|1159`.
5. Открыть первый урок `Первый код` и проверить, что первый шаг подробно объясняет программу и `print`.

## 8. Дополнение 2026-05-03: course-wide quality reseed

После самооценки материалов стало видно, что первые 10 уроков уже соответствуют входу с нуля, но в остальном курсе ещё оставались массовые шаблонные решения: одинаковые `str(value).strip()`, повторяющиеся OOP-каркасы, одинаковые FastAPI endpoint skeleton и однотипные AI payload-задачи. Технический импорт при этом проходил, но для обучения потока это недостаточно.

Что изменено сейчас:

1. В `course_import.json` переписаны hot spots за пределами первых 10 уроков:
   - generic Python practice заменены на задачи с разными контрактами входа/выхода;
   - OOP-практики теперь требуют реальные классы, property, magic methods, Protocol, inheritance, composition и dataclass;
   - AI-практики разведены на messages payload, timeout, retry, structured output, RAG citation, vector search, graph state и patch review;
   - FastAPI hidden solutions и body приведены к явному HTTP-контракту из public checker;
   - student-facing body очищен от `tests`, `admin`, `Сценарий` и битых `????`.
2. Усилен `validate_course.py`:
   - добавлен structural duplicate gate для решений;
   - добавлен отдельный AI structural duplicate gate;
   - gate падает при массовой группе больше `20`.
3. Пересобраны производные файлы:
   - `course_preview.md`;
   - `course_map.md`;
   - `manifest.csv`;
   - `validation_report.md`;
   - `qa_report.md`.
4. Создана новая миграция:
   - `028_reseed_python_zero_v18_coursewide_quality.sql`.

Почему создана новая миграция:

1. `026` и `027` уже являются отдельными слоями данных в migration-chain.
2. Переписывать применённые миграции нельзя: production база хранит применённые версии в `schema_migrations`.
3. `028` делает повторяемый полный reseed курса и позволяет ревьюеру отдельно проверить именно course-wide quality pass.

Актуальные метрики после `028`:

1. modules: 5;
2. lessons: 169;
3. lesson blocks: 1960;
4. published tasks: 1159;
5. quiz steps: 294;
6. estimated hours: 674.8;
7. max structural solution group: 18 / 20;
8. max AI structural group: 15 / 20.

Проверки после правки:

1. `python материалы/v18_STRICT_PEDAGOGY/validate_course.py` — PASS.
2. Независимый локальный QA:
   - encoding corruption: 0;
   - body leaks: 0;
   - short theory: 0;
   - FastAPI duplicate contracts inside lesson: 0;
   - first10 future-knowledge violations: 0;
   - manifest match: true;
   - coverage bad statuses: 0.
3. `node backend/tools/generate_python_v18_materials_migration.js` — создан `028`.
4. `node backend/tools/validate_python_v18_materials_import.js` — PASS против `028`.

Операционная инструкция теперь использует `028`:

1. Запушить commit с миграцией `028`.
2. Развернуть release на сервер.
3. Проверить запись `028_reseed_python_zero_v18_coursewide_quality` в `schema_migrations`.
4. Проверить агрегаты курса: `5|169|1960|1159`.
5. Открыть первые 10 уроков как студент и выборочно проверить FastAPI, AI, OOP и SQL practice.
