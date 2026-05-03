# PROD Readiness Validation — 2026-04-30 (v2.64)

## Контекст

Цель проверки: подтвердить, что контур обучения (backend + frontend + IDEA plugin) находится в рабочем состоянии для запуска когорты и убрать блокеры из предыдущей валидации.

## Что было исправлено в этом цикле

### 1) Backend: восстановлена целостность Go-модулей

Проблема:
- `go test ./...` падал из-за отсутствующего `backend/go.sum`.

Действия:
1. Выполнен `go mod tidy` в `backend`.
2. Зафиксирован `go.sum` в репозитории.

Почему сделано именно так:
- Без `go.sum` тесты и сборка не являются повторяемыми; для production-стабильности модульные checksums должны быть зафиксированы.

### 2) Backend judge: исправлен выбор Python runtime на Windows/CI

Проблема:
- В окружениях с alias-заглушкой `python3` (Windows App Alias) judge выбирал нерабочий бинарник, что приводило к `compile_error` в Python-тестах.

Действия:
1. Обновлён детектор Python в `backend/internal/judge/java.go`:
- теперь кандидат считается валидным только если `--version` завершается с кодом `0` и содержит `python`.
2. Добавлен отдельный helper `detectPythonBinaryFromCandidates(...)` для testability.
3. Обновлены тесты `backend/internal/judge/java_test.go`:
- Python-тесты используют реальный `detectPythonBinary()`;
- добавлен регрессионный тест `TestDetectPythonBinaryFromCandidatesSkipsBrokenAlias`.

Почему сделано именно так:
- Это устраняет ложноположительный выбор `python3` alias и стабилизирует judge в mixed Windows/Linux pipeline.

## Локальная валидация после фиксов

### Backend

Команда:
- `go test ./...`

Результат:
- PASS (`internal/app`, `internal/judge`, `internal/security` зелёные).

### IDEA plugin

Команды:
- `./gradlew test`
- `./gradlew buildPlugin`

Результат:
- PASS.

### Frontend

Команды:
- `npm run test -- --run`
- `npm run build`

Результат:
- PASS.

## Практическая проверка на production-сервере

Сервер:
- `85.198.82.221`
- контур: `/opt/leonovcare-platform/current`

### Smoke

Проверки:
1. `GET /healthz` -> `200` (`{"status":"ok"}`)
2. `register -> me -> courses -> run -> submissions`

Фактические коды:
- `/me` -> `200`
- `/courses` -> `200`
- `/tasks/{id}/run` -> `200`
- `/tasks/{id}/submissions` -> `202`

### Load sample

1. `GET /api/v1/courses` (`wrk -t6 -c120 -d15s`)
- ~5892 req/s
- p99 latency ~38.84ms

2. `POST /api/v1/tasks/{id}/run` (`wrk -t4 -c30 -d15s`, валидная python-задача с тестами)
- ~85 req/s
- p99 latency ~468.08ms
- non-2xx не зафиксированы

3. Queue burst для submissions (60 отправок параллельно)
- enqueue: 60 за ~1s
- drain до `pending=0`: ~3s

## Важное уточнение по предыдущему инциденту non-2xx на `/run`

Причина предыдущего ложного алерта:
- нагрузочный скрипт брал задачу по заголовку (`Первый вывод`), а не гарантировал наличие тест-кейсов;
- для задач без тестов endpoint корректно отвечает `422`, что дало `Non-2xx` под wrk.

Текущее правило для проверки:
- выбирать задачу только с условием `exists(select 1 from task_test_cases ...)`.

## Вывод по готовности

1. Критический блокер сборки/тестов backend закрыт.
2. Judge Python стабилизирован и покрыт тестом.
3. API/очередь на проде показывают рабочее поведение под прикладной нагрузкой.
4. Контур готов к запуску когорты при условии стандартного операционного мониторинга (CPU/RAM/queue depth/DB) во время первого дня.

## Что контролировать в день запуска

1. PM2-процессы `leonovcare-api` и `leonovcare-worker` (restarts, memory).
2. Redis queue depth для submission jobs.
3. Долю `4xx/5xx` по endpoint’ам `run` и `submissions`.
4. Время обработки submission (drain time) при пиковых волнах.

## Deployment verification addendum (v2.65)

### 1) Что произошло при первом деплое

1. Первичный перезапуск сборки на сервере упал на новом тесте `TestDetectPythonBinaryFromCandidatesSkipsBrokenAlias`.
2. Причина: тест был Windows-ориентирован (`.cmd` + узкий PATH) и не учитывал Linux-окружение сервера.

### 2) Исправление

1. Тест переведен в кроссплатформенный режим:
- Windows: создаются `python3.cmd` и `python.cmd`;
- Linux: создаются исполняемые `python3` и `python` shell scripts.
2. PATH в тесте теперь собирается как `tempDir + original PATH`, чтобы shebang/`env sh` корректно резолвился.

Почему так:
- цель теста — проверить fallback-логику выбора интерпретатора, а не ломать CI/production build на другой ОС.

### 3) Повторный деплой и результат

Команды на сервере:
1. `go test ./...`
2. `go build -o bin/leonovcare-api ./cmd/server`
3. `go build -o bin/leonovcare-worker ./cmd/worker`
4. `pm2 restart leonovcare-api`
5. `pm2 restart leonovcare-worker`
6. `curl -fsS http://127.0.0.1:8510/healthz`

Итог:
- backend тесты PASS;
- API и workers перезапущены успешно;
- health endpoint вернул `{"status":"ok"}`.

### 4) Повторная нагрузочная проверка после деплоя

1. `GET /api/v1/courses` (`wrk -t6 -c120 -d15s`):
- ~7727.92 req/s;
- p99 ~497.42ms (видны редкие хвосты при пике).

2. `POST /api/v1/tasks/{id}/run` (`wrk -t4 -c30 -d15s`, python task with tests):
- ~104.72 req/s;
- p99 ~356.38ms;
- non-2xx в отчете не зафиксированы.

3. Submission queue burst (60 отправок):
- enqueue 60 за ~2s;
- drain до `pending=0` за ~2s.

## Текущий статус по этому циклу

1. Регрессия теста закрыта.
2. Backend сборка/тесты и деплой подтверждены на сервере.
3. Учебный run/submit контур и очередь после рестарта работают стабильно в рамках выполненных smoke/load сценариев.
