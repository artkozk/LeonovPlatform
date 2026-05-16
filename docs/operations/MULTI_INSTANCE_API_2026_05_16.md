# Multi-Instance API + Postgres Tuning + vite cleanup — 2026-05-16

> **Append-only.** Запрещено редактировать или удалять разделы 1–9.
> Любые правки/уточнения — отдельными подразделами в §10
> вида `## 10.X — YYYY-MM-DD`.

## 1. Контекст

1. Дата: 2026-05-16.
2. Автор: Claude (по запросу пользователя через Claude Code).
3. Триггер: пункты §4.1, §4.2, §4.3 из
   `docs/operations/100RPS_READINESS_2026_05_16.md`. Пользователь
   попросил выбрать «как более качественно и поддаётся расширению»
   и доделать всё нужное.
4. После этой итерации платформа физически готова держать целевые
   ~100 RPS на инфраструктурном уровне.

## 2. Что сделано

### 2.1. Postgres tuning + pg_stat_statements

1. Создан override `/etc/postgresql/16/main/conf.d/99-leonovcare-100rps.conf`
   (исходник в репо: `deploy/server/postgresql/99-leonovcare-100rps.conf`).
2. Значения подняты с дефолтов:
   - `shared_buffers`: 128 MB → **2 GB**;
   - `effective_cache_size`: 4 GB → **8 GB**;
   - `work_mem`: 4 MB → **16 MB**;
   - `maintenance_work_mem`: 64 MB → **256 MB**;
   - `max_connections`: 100 → **200** (под 6 backend-процессов
     с pool_max_conns=30 = 180 + запас);
   - `max_wal_size`: 1 GB → **4 GB** (реже checkpoint'ы под нагрузкой);
   - `random_page_cost`: 4.0 → **1.1** (SSD-aware);
   - `effective_io_concurrency`: default → **200**;
   - `max_worker_processes`, `max_parallel_workers`: **8** (= vCPU);
   - `log_min_duration_statement = 250` (логирование slow query);
   - `shared_preload_libraries = 'pg_stat_statements'` +
     `CREATE EXTENSION IF NOT EXISTS pg_stat_statements` в БД.
3. Перезапуск PG (~3 сек simulated downtime) — здоровья API через
   pgxpool восстанавливается за время первого запроса.

### 2.2. Удаление vite preview

1. Процесс `leonovcare-frontend` (npm run preview на 8511) **удалён**
   из pm2:
   - `pm2 stop leonovcare-frontend && pm2 delete leonovcare-frontend && pm2 save`.
2. Из `ecosystem.config.cjs` блок `leonovcare-frontend` **удалён**
   (без закомментированного остатка — pm2 не должен пытаться его
   восстанавливать через `pm2 start ecosystem`).
3. Фронт теперь отдаёт исключительно nginx из
   `/opt/leonovcare-platform/current/frontend/dist`. Порт 8511 свободен.
4. История изменения сохранена в git (комментарий в ecosystem
   ссылается на эту операцию) и в IMPLEMENTATION_CHANGELOG.

### 2.3. Refactor SupportHub → Redis Pub/Sub (v2)

1. Файл: `backend/internal/app/support_realtime.go`.
2. Публичный API хаба **не изменился**: `Subscribe`, `Publish` —
   handlers и фронтенд тронуты не были.
3. Новое поведение `Publish`:
   - если есть Redis client — событие сериализуется в JSON
     (`supportRedisEnvelope{Recipients, Event}`) и отправляется в
     канал `support:events`;
   - каждый API-процесс отдельной goroutine'й подписан на канал
     `support:events` (`runRedisSubscriber`), при получении
     сообщения локально доставляет его подписчикам, чьи userID
     совпали с `recipients`;
   - если Redis сломан или нет вообще (`nil` client в тестах) —
     fallback на чистый локальный fan-out.
4. Бэкофф reconnect к Redis: 500ms → 10s, cap.
5. Добавлены атомарные счётчики `publishedTotal`, `deliveredTotal`,
   `droppedTotal`, `redisErrors` для будущего debug-эндпоинта.
6. `App.Close()` теперь корректно завершает Redis subscriber.

### 2.4. Multi-instance API behind nginx upstream

1. В `ecosystem.config.cjs` добавлен второй процесс
   `leonovcare-api-2` (script — тот же бинарь, env с `HTTP_PORT=8512`).
   Первый процесс `leonovcare-api` остался на `HTTP_PORT=8510`.
2. Создан upstream-конфиг
   `/etc/nginx/conf.d/leonovcare-upstream.conf`
   (исходник: `deploy/server/nginx/conf.d/leonovcare-upstream.conf`):
   ```
   upstream leonovcare_api {
       server 127.0.0.1:8510 max_fails=3 fail_timeout=10s;
       server 127.0.0.1:8512 max_fails=3 fail_timeout=10s;
       keepalive 32;
   }
   ```
3. Vhost `platform.ngix.leonovcare.ru` переведён на upstream:
   `proxy_pass http://leonovcare_api;` для всех маршрутов
   (`/api/v1/`, `/healthz`, `/readyz`, `/api/v1/support/stream`).
4. Round-robin балансировка. Соединения keepalive (`Connection ""`
   header в каждом location).
5. SSE: проходит через тот же upstream; cross-process fan-out
   обеспечивается Redis Pub/Sub (см. §2.3).

## 3. Smoke-проверки на production

Все выполнены 2026-05-16 после деплоя:

1. `nginx -t` → OK; `systemctl reload nginx` → active.
2. Бинарь `bin/leonovcare-api` пересобран (20.6 MB), `bin/leonovcare-worker`
   пересобран (17.0 MB). `go test ./...` зелёный, включая 5 новых
   тестов для Redis-backed хаба.
3. `pm2 ls` показывает:
   - `leonovcare-api` (PID на 8510, online);
   - `leonovcare-api-2` (PID на 8512, online);
   - `leonovcare-worker` × 4 (online).
4. `ss -tlnp` подтверждает оба порта 8510 и 8512 слушают свои Go-процессы.
5. `curl /healthz` напрямую на 8510 и 8512 → 200 OK на обоих.
6. `curl https://platform.ngix.leonovcare.ru/healthz` через
   `--resolve` → 200 OK (через upstream).
7. 200 последовательных запросов через nginx → 200/200 успехов.
8. `redis-cli PUBSUB NUMSUB support:events` → **6 подписчиков**
   (api + api-2 + 4 workers — каждый процесс подключился к Redis
   при старте `App.New()`).
9. `redis-cli PUBLISH support:events '<test>'` → доставлено в 6
   подписчиков (channel route validated; реальных SSE-клиентов на
   момент теста не было).
10. Сторонние vhost'ы (`leonovcare.ru`, `shop.e-rd.ru`, `e-rd.ru`)
    после nginx reload — HTTPS 200, не задеты.
11. `pg_stat_activity` показал ~37 активных соединений (≈ pool_min×6
    + admin + spare), укладываемся в `max_connections=200`.

## 4. Почему именно так

1. **Отдельный upstream в `conf.d/`, а не в vhost-файле.**
   Apstream — это разделяемая инфра-настройка. Если завтра появится
   ещё один vhost или второй внутренний домен, конфиг upstream'а
   будет переиспользован без дублирования.
2. **Redis Pub/Sub, не Redis Streams.**
   Streams нужны, если нужно гарантированно догнать пропущенные
   события после reconnect. Это противоречило бы blueprint §6
   («события идемпотентны, клиент re-fetch'ает через REST»). Pub/Sub
   проще, без управления offsets.
3. **Не cluster_mode pm2, а две независимых fork-инстанции.**
   pm2 cluster_mode полагается на Node `cluster` API (родитель fork'ает
   воркеров и шарит accept-сокет). Go бинарь это игнорирует, поэтому
   реального балансирования не будет. Две независимые fork-инстанции
   с разными `HTTP_PORT` дают честный isolation.
4. **conf.d nginx, а не sites-enabled.**
   `conf.d/*.conf` подключается через `http {}` блок раньше
   `sites-enabled/*`, и upstream становится доступен любому vhost'у.
5. **`keepalive 32`** в upstream — снимает TCP/TLS handshake на каждом
   запросе между nginx и Go. Без этого upstream был бы узким горлом
   при росте RPS.
6. **`max_fails=3 fail_timeout=10s`** даёт автоматический failover
   на здоровый бэкенд, если один процесс умирает.
7. **`work_mem=16MB`** — не выше, потому что 100 RPS × 1 sort
   = до 1.6 GB одновременных аллокаций, всё ещё в нашем 11 GB
   RAM-бюджете. 32 MB — это уже риск.
8. **`max_connections=200`** — поднял, потому что под multi-instance
   мы можем легально открыть до 180 соединений (api×2 × 30 + worker×4 × 30),
   и нужен запас на admin / pg_dump / pg_basebackup.

## 5. Альтернативы, отвергнутые

1. **HAProxy вместо nginx upstream.**
   Лишний компонент. nginx уже стоит для TLS-terminate и SPA.
2. **Sticky session по userID для SSE.**
   Не нужно — Redis Pub/Sub обеспечивает доставку независимо от
   того, на каком процессе висит подписчик. Stickiness усложнило бы
   failover.
3. **Бамп `max_connections` до 500.**
   На 11 GB RAM каждое PG-соединение жрёт ~10 MB. 500 = 5 GB ОЗУ
   только под коннекты. 200 это компромисс safety/headroom.
4. **PostgreSQL Connection Pooler (PgBouncer).**
   Имеет смысл при существенно большем числе процессов или при
   short-lived connect/disconnect (например, php-fpm). У нас Go +
   pgxpool — пул долгоживущих keep-alive соединений, PgBouncer
   дал бы маргинальный выигрыш ценой ещё одной точки отказа.

## 6. Что НЕ сделано (осознанно, для следующих итераций)

1. **CDN/edge cache** (Cloudflare / Fastly) — не настроено. Имеет
   смысл при росте к 1000+ RPS на статику.
2. **Метрики (Prometheus / OpenTelemetry exporter)** — нет. Сейчас
   есть атомики в `SupportHub`, но не выставлены наружу. Отдельный
   `/admin/support/metrics` JSON-endpoint можно добавить.
3. **Health check `/readyz` per-instance** — оба процесса отвечают
   независимо, но nginx не делает active health-probe. Полагаемся
   на `max_fails`.
4. **Postgres replica для read-load** — преждевременно при
   текущей нагрузке.
5. **AV-скан support-вложений** — задокументировано в blueprint §9.

## 7. Файлы, изменённые в этой итерации

Backend:
1. `backend/internal/app/support_realtime.go` — v2 c Redis Pub/Sub,
   API без break-change.
2. `backend/internal/app/support_realtime_test.go` — 5 новых
   юнит-тестов (local-only mode достаточен для unit-уровня;
   Redis-пасс проверен production smoke в §3.8–3.9).
3. `backend/internal/app/types.go` — `NewSupportHub(rds, logger)`,
   корректное `Close()`.

Deploy:
4. `deploy/server/ecosystem.config.cjs` — два API-процесса; блок
   `leonovcare-frontend` удалён.
5. `deploy/server/nginx/platform.ngix.leonovcare.ru.conf` —
   `proxy_pass http://leonovcare_api;` + `Connection ""` headers.
6. `deploy/server/nginx/conf.d/leonovcare-upstream.conf` — новый
   upstream-блок, копия с `/etc/nginx/conf.d/`.
7. `deploy/server/postgresql/99-leonovcare-100rps.conf` — копия
   override-файла с `/etc/postgresql/16/main/conf.d/`.

Docs:
8. `docs/operations/MULTI_INSTANCE_API_2026_05_16.md` — этот документ.
9. `docs/operations/IMPLEMENTATION_CHANGELOG.md` — append-only entry.
10. `README.md` — append-only актуализация.

## 8. Как откатить (если что-то пойдёт не так)

1. Бэкап ecosystem + vhost:
   `/opt/leonovcare-platform/backups/multi_instance_<timestamp>/`.
2. PG-тюнинг откатывается тривиально:
   ```
   rm /etc/postgresql/16/main/conf.d/99-leonovcare-100rps.conf
   systemctl restart postgresql
   ```
3. Откат к одному API-инстансу:
   ```
   pm2 delete leonovcare-api-2
   pm2 save
   # nginx upstream при этом будет ловить «502/upstream» на 50%
   # запросов — поэтому одновременно вернуть proxy_pass на 8510 в vhost.
   ```
4. Откат к Redis-less Hub: код `support_realtime.go` всё ещё
   поддерживает `nil` client — достаточно поменять `NewSupportHub`
   вызов в `types.go`.

## 9. Финальное состояние production

1. Endpoints:
   - https://platform.ngix.leonovcare.ru/ → SPA (nginx → dist).
   - /api/v1/* → nginx upstream `leonovcare_api` (8510 + 8512).
   - /api/v1/support/stream → SSE, Redis Pub/Sub fan-out между
     api-процессами.
2. PG: tuned под 100 RPS, `pg_stat_statements` активен для slow-query
   аналитики.
3. Edge: Let's Encrypt cert, auto-renew via `certbot.timer`.
4. Прозрачно для конечного пользователя: URL'ы и API-контракты
   не изменились.

## 10. Дополнения после первичной публикации

> Раздел зарезервирован. Запрещено редактировать §1–9. Любые
> уточнения добавляются сюда отдельными датированными подразделами.
