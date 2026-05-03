# Python v10 Production Deploy Report — 2026-04-30

## 1. Цель

Подтвердить, что курс `python-zero` обновлен на `v10` в production-контуре и готов к массовому запуску без ручных допроверок критичных путей.

## 2. Что было развернуто

1. Commit:
- `e368ea02f1d043e2efd402e37bfb4bb17b236a6d`
2. Release archive:
- `leonovcare_release_20260430_v276.tgz`
3. Branch:
- `codex/leonovcare-minimal-redesign`
4. Server:
- `root@85.198.82.221`
5. Target path:
- `/opt/leonovcare-platform/current`

## 3. Процедура деплоя (факт выполнения)

1. Загружен релиз-архив в `/opt/leonovcare-platform/`.
2. Выполнено атомарное переключение директории:
- `current -> current_backup_20260430_130404_v276`
- `current_new_* -> current`
3. Запущен `deploy/server/deploy.sh` в новом `current`.
4. Выполнены backend/unit проверки в процессе деплоя:
- `go test ./...` — pass.
5. Выполнены frontend проверки в процессе деплоя:
- `npm run test` — pass.
- `npm run build` — pass.
6. PM2 процессы платформы перезапущены и сохранены:
- `leonovcare-api`
- `leonovcare-worker` (4 инстанса)
- `leonovcare-frontend`
7. Health-check:
- `GET http://127.0.0.1:8510/healthz` -> `{"service":"Leonov Care Platform","status":"ok"}`
- `HEAD http://127.0.0.1:8511` -> `HTTP/1.1 200 OK`

## 4. Post-deploy валидация Python v10 (production)

Выполнен автоматизированный скрипт `tmp_remote_validate_v276.py` на сервере с проверкой SQL-инвариантов + API runtime-path.

Итог:
- `VALIDATION_OK`
- `issues: []`

Проверки, которые прошли:

1. Применение migration:
- `023_reseed_python_zero_v10_polished_full` присутствует в `schema_migrations`.
2. Структура курса:
- modules = `5` (ожидание `5`)
- lessons_published = `145` (ожидание `145`)
3. Публикация блоков:
- theory = `303`
- quiz = `269`
- practice = `367`
- project = `509`
4. Публикация задач:
- tasks_published = `876`
5. Распределение checker-типов:
- `http_api=44`
- `ide_plugin=509`
- `python_pytest=152`
- `python_stdout=57`
- `sql_query=114`
6. Launch-gates:
- practice без task = `0`
- project без `ide_plugin` или без `ai_review.enabled=true` = `0`
7. Контентные guardrails:
- утечек `Шаблон/Подсказки/Эталон/Автотесты` в student body = `0`
8. Quiz security API:
- `GET /api/v1/lessons/:lessonId` не содержит `correctOptionId`
- `POST /api/v1/lessons/:lessonId/quiz-check` работает корректно
9. Runtime smoke через API `/run`:
- `python_stdout`, `python_pytest`, `sql_query`, `http_api`, `ide_plugin` — все endpoint-пути работают без runtime-fail.
10. IDE files bundle:
- `POST /api/v1/tasks/:taskId/submissions` с `files[]` принят,
- submission доходит до финального статуса (не зависает в `queued`).

## 5. Почему этого достаточно для запуска когорты

1. Проверены не только статические SQL-количества, но и реальные runtime-пути API для ключевых checker-типов.
2. Подтверждена server-side проверка quiz, что исключает утечку правильных ответов в уроках.
3. Подтверждена обработка `files[]` для project/IDE-сценария, что критично для прохождения задач из PyCharm/IDE plugin.
4. Все инварианты из `PYTHON_V10_ROLLOUT_2026_04_30.md` и runbook-секции по migration `023` соблюдены.

## 6. Что еще нужно доделать

На момент завершения отчета обязательных блокеров не обнаружено.

Рекомендованные не-блокирующие улучшения (без остановки запуска):

1. Планово обновить Node.js на сервере до `>=20` (сейчас есть `npm WARN EBADENGINE` от части frontend-зависимостей).
2. Запланировать оптимизацию frontend bundle-size (предупреждение Vite по chunk > 500KB).
