# Python v10 Rollout — 2026-04-30

## 1. Контекст и цель

Этот rollout заменяет текущий контент курса `python-zero` на новую поставку `v10` из JSON-импорта, с обязательной автопроверкой для code-step и с сохранением скрытых критериев проверки вне student-visible UI.

Почему это сделано именно так:

1. Источник `v10` уже содержит структурированные checker-конфиги (`python_stdout`, `python_pytest`, `sql_query`, `http_api`, `ide_plugin`) и правила видимости. Сохранять их нужно в `source_policy`, а не в `body_markdown`, чтобы:
   - не раскрывать hidden/server-side правила студенту;
   - использовать один и тот же source для backend-checker, AI-hint и IDE-plugin.
2. Ресид через миграцию (`023`) выбран вместо ручных SQL-правок, чтобы rollout был воспроизводим в любом контуре и проходил через стандартный `AUTO_MIGRATE`.
3. Серверная проверка quiz вынесена в отдельный endpoint, чтобы правильные ответы не утекали в payload урока до отправки ответа.

## 2. Входные артефакты

1. `C:/Users/Artemy/AppData/Local/Temp/python_course_platform_v10_import.json` — единственный источник импорта.
2. `C:/Users/Artemy/AppData/Local/Temp/CODEX_IMPORT_INSTRUCTIONS_v10.md` — правила видимости и validation gate.
3. Валидационные reference-файлы:
   - `python_course_platform_v10_validation_report.md`
   - `python_course_platform_v10_preview.md`
   - `python_course_platform_v10_manifest.csv`
   - `python_course_platform_v10_course_map.md`
   - `IDE_PLUGIN_SPEC_v10.md`
   - `MIDDLE_READINESS_RUBRIC_v10.md`

## 3. Что изменено в коде

### 3.1 Импорт и миграция курса

1. Добавлен генератор:
   - `backend/tools/generate_python_v10_migration.js`
2. Сгенерирована миграция:
   - `backend/migrations/023_reseed_python_zero_v10_polished_full.sql`
3. Миграция делает:
   - reseed `python-zero` на 5 модулей / 145 уроков / 1448 шагов;
   - tasks для всех `practice + project` шагов (876 задач);
   - автотесты в `task_test_cases` там, где checker-exec совместим напрямую (`python_stdout`, `sql_query`);
   - сохранение checker/hints/ai-review/admin-notes в `tasks.source_policy`.

### 3.2 Backend checker-runtime

1. Добавлен runtime для v10 checker-типов:
   - `backend/internal/app/checker_runtime.go`
2. Реализовано:
   - `python_stdout` -> стандартный python judge на тестах checker;
   - `sql_query` -> SQL judge на проверках checker;
   - `python_pytest` -> lightweight python test-runner (без внешней зависимости на pytest пакет);
   - `http_api` -> lightweight FastAPI-compatible runner со stub-реализацией `FastAPI`;
   - `ide_plugin` -> файловая/командная проверка проекта (required/forbidden/commands).
3. Обратная совместимость:
   - если checker не найден, backend остается в legacy-пути через `task_test_cases`.

### 3.3 Submission bundle из IDE

1. Добавлена поддержка bundle-посылок файлов:
   - backend кодирует payload в `source_code` с префиксом `__LC_BUNDLE_V1__`.
2. Worker декодирует bundle и проверяет проект как файловое дерево.
3. Для legacy web submit формат `sourceCode` продолжает работать без изменений.

### 3.4 Серверная проверка quiz без утечки правильных ответов

1. В `GET /lessons/:lessonId` правильные варианты теперь очищаются из `quiz_payload`.
2. Добавлен endpoint:
   - `POST /api/v1/lessons/:lessonId/quiz-check`
3. Frontend больше не сравнивает ответы локально с `correctOptionId`; проверка идет через backend.

### 3.5 Frontend/IDE-поведение

1. `LessonPage` обновлен:
   - block type `project` теперь отдельный визуальный тип;
   - code editor/submit/hint доступны для code-step (`practice` и `project`);
   - quiz-check переведен на серверный endpoint.
2. IDEA plugin updated:
   - submit отправляет полный `files[]` bundle на backend;
   - тип задачи читается из API (`PROJECT`, `UNIT_TEST`, `CONSOLE`) для корректной маршрутизации сценариев.

## 4. Автоматическая валидация и контроль качества

1. Добавлен валидатор:
   - `backend/tools/validate_python_v10_import.js`
2. Отчет валидатора:
   - `docs/operations/PYTHON_V10_IMPORT_VALIDATION_2026_04_30.md`
3. Валидатор проверяет:
   - полноту шагов/задач/тестов между JSON и SQL;
   - отсутствие forbidden секций в student `body_markdown`;
   - отсутствие practice без checker;
   - отсутствие project без `ide_plugin + ai_review.enabled=true`.

## 5. Команды, использованные верификацией

1. Backend:
   - `go test ./...` (pass)
2. Frontend:
   - `npm.cmd test -- --run` (pass)
   - `npm.cmd run build` (pass)
3. IDEA plugin:
   - `gradlew.bat test -x instrumentCode -x instrumentTestCode` (pass)
   - примечание: стандартный `gradlew.bat test` в текущем локальном окружении падал на `:instrumentCode` из-за host-specific JDK path, поэтому проверка выполнена без инструментирования.
4. Импортный валидатор:
   - `node backend/tools/validate_python_v10_import.js` (pass)

## 6. Почему reviewer не должен отклонять этот rollout

1. Rollout закрывает продуктовый риск “слабый Python-контент” полным переходом на `v10`.
2. Проверки теперь системно покрывают все типы code-step, включая project-проверки по файловой структуре и командам.
3. Убрана утечка quiz-answers в lesson payload.
4. Сохранена backward compatibility для существующих web/submit сценариев.
5. Все изменения документированы отдельно и не перезаписывают исторические документы.
