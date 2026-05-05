# Leonov Care Platform — Deployment Guide (Launch Profile)

## 1. Цель

Пошагово развернуть платформу в production-профиле без демо-контента, с безопасными webhook настройками и email-only авторизацией.

## 2. Предусловия

1. Сервер Linux с доступом по SSH.
2. Установлены:
- `git`
- `curl`
- `nodejs` + `npm`
- `golang`
- `redis-server`
- `postgresql`
- `docker` (обязательно для `JUDGE_MODE=docker`)
- `pm2`

3. Открыты порты:
- `8510/tcp` (API)
- `8511/tcp` (frontend)

## 3. Подготовка репозитория на сервере

1. Перейти в рабочий каталог:
```bash
cd /opt/leonovcare-platform/current
```
2. Обновить код:
```bash
git fetch --all
git pull
```

## 4. Конфигурация окружения

Настроить env для PM2 (через shell env или `.env` в orchestration слое), минимум:

1. База и инфраструктура:
- `DATABASE_URL`
- `REDIS_URL`

2. JWT:
- `JWT_ACCESS_SECRET`
- `JWT_REFRESH_SECRET`

3. Launch toggle:
- `AUTO_MIGRATE=true`
- `AUTO_SEED=false`
- `JUDGE_MODE=docker`
- `SUBMISSION_MAX_ATTEMPTS=30`
- `EXPOSE_DEMO_TOKENS=false`

4. Billing:
- `CARDLINK_WEBHOOK_TOKEN`
- `CARDLINK_SECRET`
- `CARDLINK_REQUIRE_SIGNATURE=true`

5. AI (опционально):
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

## 5. Сборка и тест

1. Backend:
```bash
cd /opt/leonovcare-platform/current/backend
go mod tidy
go test ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker
```

2. Frontend:
```bash
cd /opt/leonovcare-platform/current/frontend
npm ci
npm run test
export VITE_API_URL="${VITE_API_URL:-http://85.198.82.221:8510/api/v1}"
npm run build
```

## 6. Запуск через PM2

```bash
cd /opt/leonovcare-platform/current
pm2 delete leonovcare-api leonovcare-worker leonovcare-frontend || true
pm2 start deploy/server/ecosystem.config.cjs
pm2 save
pm2 status
```

## 7. Проверки после запуска

1. Health:
```bash
curl -fsS http://127.0.0.1:8510/healthz
```
2. Auth UI:
- открыть `http://85.198.82.221:8511/auth`;
- убедиться, что виден только email-flow без Google/GitHub кнопок.
3. Регистрация:
- проверить поля `Имя`, `Фамилия`, `Ник`;
- после регистрации проверить `publicId` в `Настройки`.
4. Billing webhook security:
- проверить что без валидной подписи webhook получает `401`.
5. Submission worker:
- отправить задачу, убедиться что verdict появляется и queue не зависает.

### Актуализация smoke-проверок от 2026-05-02

1. Старый пункт про проверку `publicId` в `Настройки` оставлен выше как исторический контекст предыдущего UI.
2. Сейчас `publicId` проверяется на странице `/profile`, потому что экран `/settings` удалён из пользовательского интерфейса.
3. После деплоя дополнительно проверить:
- в меню профиля нет пункта `Настройки`;
- `/profile` содержит только account summary и переход к подписке;
- интерфейс и редактор задач открываются только в светлой теме.
4. Это нужно, чтобы production-проверка совпадала с текущим продуктовым решением: настройки больше не нужны ученику, а dark-mode выключен из-за низкого визуального качества.

## 8. Миграции launch-профиля

Миграция `005_launch_readiness.sql` делает:

1. удаление демо курса `java-start`;
2. очистку синтетических XP/достижений;
3. добавление `first_name`, `last_name`, `nickname`, `public_id`;
4. добавление `processing_attempts` для retry воркера.

## 9. Rollback (минимальный)

1. Откат к предыдущему commit:
```bash
git checkout <previous_commit>
```
2. Пересборка и перезапуск PM2 по шагам 5-6.

Примечание:

Миграции данных в этой версии изменяют профиль пользователей и очищают demo-метрики. Полноценный rollback данных требует отдельного DB backup.

## 10. Backend hardening update (append-only, 2026-05-05)

### 10.1 Как было

1. Runtime-процессы (`server`/`worker`) могли полагаться на `AUTO_MIGRATE=true`.
2. Очередь сабмитов была без `processing`-очереди и без явного ack-подтверждения через Redis.
3. При работе с материалами frontend делал fanout-запросы к урокам (`getLesson` для каждого lesson), что давало N+1 и высокую латентность.
4. Не было отдельного readiness probe, который проверяет и DB, и Redis одновременно.

### 10.2 Как стало

1. Миграции вынесены в отдельный deployment-шаг через новый бинарь `backend/cmd/migrator`.
2. `db.ApplyMigrations(...)` теперь берет PostgreSQL advisory lock, чтобы исключить параллельное применение миграций.
3. `worker` использует надежный цикл обработки очереди:
- `BRPOPLPUSH main -> processing`;
- `LREM processing` после финала (ack);
- requeue при recoverable error;
- фоновый reconciler для `queued` записей.
4. `worker` и `server` больше не должны использовать runtime-миграции как основной путь релиза; в PM2 дефолт `AUTO_MIGRATE=false`.
5. Добавлен `GET /readyz` (проверяет `DB.Ping` и `Redis.Ping`).
6. Добавлен `GET /api/v1/courses/:courseID/tasks-catalog` и расширен `GET /api/v1/courses/:courseID` полем `lessons[].blockCount`.
7. Включено gzip-сжатие API-ответов.

### 10.3 Почему сделано именно так

1. Отдельный шаг миграций с advisory lock нужен, чтобы исключить race между несколькими процессами/инстансами при старте.
2. `main -> processing` + ack в Redis нужен для предсказуемого at-least-once поведения после рестартов и сетевых сбоев.
3. `tasks-catalog` и `blockCount` нужны, чтобы убрать N+1 на страницах материалов и сократить число запросов до фиксированного набора.
4. `readyz` нужен для корректного orchestration health-gate: `healthz` показывает liveliness, `readyz` — реальную готовность зависимостей.

### 10.4 Новый обязательный порядок деплоя

1. Обновить код:
```bash
cd /opt/leonovcare-platform/current
git fetch --all
git pull
```

2. Сборка backend (включая migrator):
```bash
cd /opt/leonovcare-platform/current/backend
go mod tidy
go test ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker
go build -o bin/leonovcare-migrator ./cmd/migrator
```

3. Применить миграции отдельным шагом ДО запуска runtime:
```bash
cd /opt/leonovcare-platform/current/backend
./bin/leonovcare-migrator
```

4. Сборка frontend:
```bash
cd /opt/leonovcare-platform/current/frontend
npm ci
npm run test
export VITE_API_URL="${VITE_API_URL:-http://85.198.82.221:8510/api/v1}"
npm run build
```

5. Перезапуск PM2:
```bash
cd /opt/leonovcare-platform/current
pm2 delete leonovcare-api leonovcare-worker leonovcare-frontend || true
pm2 start deploy/server/ecosystem.config.cjs
pm2 save
pm2 status
```

6. Проверки после запуска:
```bash
curl -fsS http://127.0.0.1:8510/healthz
curl -fsS http://127.0.0.1:8510/readyz
```

### 10.5 Новые env-параметры (добавлены, старые секции выше не удаляются)

1. Queue reliability:
- `SUBMISSION_PROCESSING_QUEUE=submission_jobs_processing`
- `SUBMISSION_RECONCILE_INTERVAL=30s`
- `SUBMISSION_RECONCILE_BATCH=200`

2. Security / checker guard:
- `IDE_CHECKER_ALLOWED_COMMANDS=python -m pytest,pytest`

3. Rate limiting:
- `AUTH_RATE_LIMIT_PER_MINUTE=60`
- `AI_HINT_RATE_LIMIT_PER_MINUTE=20`
- `WEBHOOK_RATE_LIMIT_PER_MINUTE=120`

4. Runtime migrations:
- `AUTO_MIGRATE=false` (для production-профиля; миграции идут через `leonovcare-migrator`)

## 11. Plugin Backend Stabilization Update (append-only, 2026-05-05)

### 11.1 Что было проблемой до фикса

1. IDE-клиенту не хватало полного backend-контракта (`/template`, `/style-check`, `/reference-solution`, `/progress/reset`, `/sync`), поэтому часть сценариев работала через fallback и была нестабильной.
2. Для больших курсов plugin получал задачи через fanout (`course -> lessons -> lesson details`) и создавал N+1 нагрузку.
3. В `GET /submissions/{id}` возвращался raw `feedback` из judge, что могло раскрывать внутренние детали hidden-проверок.
4. При ошибке Redis push в submit API пользователь получал `500`, хотя запись сабмита уже была создана в БД и могла быть обработана позже.
5. Не было явных runtime-limitов на размер payload для run/submit запросов, что при очень больших решениях увеличивало риск деградации API.

### 11.2 Как работает сейчас

1. В backend добавлены endpoint’ы для plugin-контракта:
- `GET /api/v1/tasks/:taskID/template`
- `POST /api/v1/tasks/:taskID/style-check`
- `GET /api/v1/tasks/:taskID/reference-solution`
- `POST /api/v1/tasks/:taskID/progress/reset`
- `POST /api/v1/sync`
2. Плагин в `HttpPlatformApiClient` сначала использует `GET /api/v1/courses/:courseID/tasks-catalog`, а при ошибке автоматически падает в старый lesson-fanout путь.
3. Ответ `GET /api/v1/submissions/:submissionID` отдает только sanitized feedback (без `input/expected` из тестов), поле `referenceCode` больше не используется для передачи эталона.
4. При ошибке Redis в `POST /tasks/:taskID/submissions` backend сохраняет `queued` и возвращает `202` с `deferredDispatch=true`; дальше запись подхватывается reconciler-процессом worker.
5. Добавлены ограничения payload:
- `MAX_REQUEST_BODY_BYTES` (общий HTTP body лимит);
- `MAX_SUBMISSION_SOURCE_BYTES` (лимит содержимого submit/run payload).

### 11.3 Почему так сделано

1. Полный контракт endpoint’ов убирает хрупкие клиентские обходы и снижает количество “плавающих” ошибок в IDE.
2. `tasks-catalog` как первый путь критичен для производительности на курсах с очень большим числом уроков/задач.
3. Санитизация feedback исключает утечку hidden-тестовой логики в пользовательский API.
4. `deferredDispatch` при Redis-failure убирает ложный “submit failed” UX и предотвращает лишние повторные отправки.
5. Размерные лимиты нужны как эксплуатационный предохранитель под реальные большие решения и высокий параллелизм.

### 11.4 Что проверить после деплоя (обязательно)

1. API контракт:
```bash
curl -fsS -H "Authorization: Bearer <token>" http://127.0.0.1:8510/api/v1/tasks/<task_id>/template
curl -fsS -X POST -H "Authorization: Bearer <token>" http://127.0.0.1:8510/api/v1/sync
```
2. Submit reliability:
- временно остановить Redis или симулировать push-failure;
- проверить, что `POST /tasks/:taskID/submissions` возвращает `202` и `deferredDispatch=true`;
- после восстановления Redis убедиться, что worker доводит submission до финального статуса.
3. Security regression:
- проверить, что `GET /submissions/:id` не содержит `expected`/`input` hidden-тестов;
- проверить, что `GET /tasks/:taskID/reference-solution` до `accepted` возвращает запрет/недоступность.
4. Performance regression:
- на большом курсе убедиться, что plugin sync не вызывает fanout на каждый lesson при доступном `tasks-catalog`.

### 11.5 Новые env-параметры (добавлены, старые секции не удаляются)

1. Payload limits:
- `MAX_REQUEST_BODY_BYTES=16777216`
- `MAX_SUBMISSION_SOURCE_BYTES=8388608`

## 12. Runtime Node Baseline Update (append-only, 2026-05-05)

### 12.1 Что было

1. На production-сервере использовался `Node v18.19.1`.
2. Часть frontend-зависимостей (например `react-router` и `eslint-visitor-keys`) уже требует Node `>=20` и в логах деплоя появлялись `EBADENGINE` предупреждения.

### 12.2 Что сделано

1. Для деплой-контура зафиксирован baseline `Node >=20.19.0`.
2. В `deploy/server/deploy.sh` добавлена preflight-проверка версии Node перед `npm ci`.
3. Во frontend `package.json` добавлены `engines`:
- `node: >=20.19.0`
- `npm: >=10.0.0`

### 12.3 Почему так

1. Это устраняет риск внезапного падения сборки после обновления зависимостей.
2. Preflight в deploy-скрипте завершает релиз сразу с понятной причиной, а не в середине `npm ci`.

### 12.4 Практический шаг на сервере

1. Обновить Node до LTS 20+ (или выше) системно и проверить:
```bash
node -v
npm -v
```
2. После обновления перезапустить стандартный deploy-проход.

## 13. Judge Runtime Availability Update (append-only, 2026-05-05)

### 13.1 Что зафиксировано

1. Для PM2 default в `deploy/server/ecosystem.config.cjs` используется `JUDGE_MODE=auto` (вместо hard default `docker`).
2. Для stdout-задач backend теперь не блокирует проверку при отсутствии Docker: judge переключается на local runtime.
3. Docker-dependent checker’ы (`python_pytest`, `http_api`) остаются требовательными к Docker и при его отсутствии возвращают контролируемую ошибку.

### 13.2 Почему это важно

1. Рабочий код пользователя не должен падать с `FAILED` из-за инфраструктурной недоступности Docker в базовых задачах.
2. `auto` даёт предсказуемое поведение:
- Docker есть: используется sandbox;
- Docker нет: stdout-задачи работают в local runtime, без блокировки обучения.
3. Отдельные sandbox-checker’ы не переведены на local fallback, чтобы не размывать ограничения изоляции.

### 13.3 Как проверить после деплоя

1. Проверить эффективный judge mode в окружении PM2:
```bash
pm2 env leonovcare-api | grep JUDGE_MODE
```
2. Выполнить smoke-check stdout задачи через plugin/API и убедиться, что нет ошибки `docker is not available`.
3. Для задач типа `python_pytest`/`http_api` убедиться, что:
- при наличии Docker проверки проходят штатно;
- при отсутствии Docker ошибка явно сообщает причину sandbox-недоступности.

### 13.4 Когда включать strict docker режим

1. Если требуется принудительная контейнеризация всех проверок, на сервере должен быть установлен и доступен Docker runtime для процессов API/worker.
2. После этого можно явно задать:
```bash
export JUDGE_MODE=docker
```
3. И обязательно проверить:
```bash
docker ps
pm2 restart leonovcare-api leonovcare-worker
```

## 14. IDE Checker + Template Contract Update (append-only, 2026-05-05)

### 14.1 Что изменено

1. `GET /api/v1/tasks/:taskID/template` теперь отдает все `required_files` для `ide_plugin` задач, а не только один entry file.
2. Для `README.md` backend выдает стартовый шаблон, чтобы пользователь не блокировался на `required file is missing` сразу после открытия задачи.
3. Production-политика IDE checker команд расширена безопасным default-набором:
- `pytest`, `python -m pytest`,
- простые `python/python3` команды,
- безопасный шаблон `printf ... | python ...`.
4. По-прежнему запрещены команды с опасными shell-токенами (`;`, `&&`, `||`, `` ` ``, `$(`, redirect и т.д.).

### 14.2 Почему это важно

1. Для project-step задач пользователь должен получать полноценный стартовый набор файлов из template API.
2. Ранее валидные учебные команды могли блокироваться allowlist-политикой и давать ложный `FAILED`.
3. Новая политика сохраняет защиту от опасных команд и одновременно не ломает нормальные сценарии обучения.

### 14.3 Проверка после деплоя

1. Проверить template выдачу для project-задачи:
```bash
curl -fsS -H "Authorization: Bearer <token>" http://127.0.0.1:8510/api/v1/tasks/<task_id>/template
```
2. Убедиться, что в `files[]` присутствуют как минимум `main.py` и `README.md` (если они требуются checker'ом).
3. Запустить проверку project-step в IDE и убедиться, что ошибка `command is blocked in production` для безопасных python-команд больше не возникает.
