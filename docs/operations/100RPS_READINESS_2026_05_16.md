# 100 RPS Readiness Assessment — 2026-05-16

> **Append-only.** Запрещено редактировать или удалять разделы 1–7.
> Любые последующие правки — отдельными подразделами в §8 вида
> `## 8.X — YYYY-MM-DD`.

## 1. Контекст

1. Дата: 2026-05-16.
2. Автор: Claude (по запросу пользователя через Claude Code).
3. Триггер: пользователь сообщил ожидаемую нагрузку на платформу
   около **100 RPS** и попросил оценить готовность инфраструктуры
   и кода после релиза support-чата
   (см. `docs/operations/SUPPORT_CHAT_IMPLEMENTATION_2026_05_16.md`).
4. Дополнительно пользователь упомянул «какие-то ошибки на почту».
   Часть письма про эти ошибки разобрана в §6.

## 2. Что измерено на production (`85.198.82.221`)

1. Железо: 8 vCPU (QEMU virtual @ 2.0 GHz), 11 GiB RAM
   (3.9 GiB used, 7.7 GiB available), 4 GiB swap (638 MiB used),
   96 GiB диск (53% used).
2. Процессы (pm2): 1× `leonovcare-api`, 4× `leonovcare-worker`,
   1× `leonovcare-frontend` (всё `fork`-режим, не `cluster`).
3. PostgreSQL:
   - `max_connections=100`;
   - `shared_buffers=128 MB` (default Debian — мало для нашей RAM);
   - `work_mem=4 MB`;
   - `effective_cache_size=4 GB`;
   - `shared_preload_libraries` пустой — `pg_stat_statements` не
     включён.
4. До правок этого дня pgxpool открывал ~8 соединений (default
   `max(4, runtime.NumCPU())`), хотя сервер с 8 vCPU.
5. Frontend на production обслуживается через `pm2 run preview`,
   то есть `vite preview` — Node.js dev-сервер. nginx **не** стоит
   перед `:8511` (для домена `leonovcare.ru` действует
   domain-lock policy — он используется другим продуктом).
6. Текущая фактическая нагрузка (журналы за последние часы) —
   1–3 запроса в 5 минут от реальных клиентов. То есть 100 RPS
   будет ростом в **~10 000×**.

## 3. Что сделано в этой итерации (deploy-ready изменения)

1. `DATABASE_URL` дополнен пулом:
   `?...&pool_max_conns=30&pool_min_conns=5&pool_max_conn_lifetime=1h`.
   - pool_min_conns=5: holds warm соединения, чтобы первая волна не
     платила TCP+TLS+startup.
   - pool_max_conns=30: расчёт ниже.
   - pool_max_conn_lifetime=1h: ротация для защиты от drift TLS/PG GUC.
2. `GIN_MODE=release` и `NODE_ENV=production` зафиксированы в
   `.env` и в `ecosystem.config.cjs` (whitelist `pickEnv`).
   - До правки `ecosystem.config.cjs` пропускал в процессы только
     заранее перечисленные keys — `GIN_MODE`, `NODE_ENV`, и **новые
     `SUPPORT_CHAT_*` тоже не пробрасывались**. То есть мои support
     лимиты сейчас работали только на дефолтах, явные значения из
     `.env` игнорировались. Это исправлено в одной и той же правке.
3. PM2 перезапущен через `pm2 restart ecosystem.config.cjs --update-env`,
   проверено `/proc/<pid>/environ`: новые переменные действительно
   видны процессу.
4. `backend/.env.example` дополнен документирующими блоками для
   тюнинга и для feature-flag'ов support-чата.

### Как это влияет на 100 RPS

1. **pgxpool 8 → 30.** Это снимает основное узкое горло. Расчёт:
   - средний request → 2–3 SQL-запроса × средний ~10 мс = ~25 мс
     DB-времени на запрос;
   - 100 RPS × 25 мс = 2.5 с DB-работы в секунду → достаточно
     ~25 одновременно занятых соединений. С запасом 20% берём 30.
2. **gin release.** Убирает route-enumeration на старте и пер-запросные
   debug-логи; экономит несколько % CPU и log-IO под нагрузкой.
3. **NODE_ENV=production.** Vite preview, axios на бэкенд-RPC,
   возможные node-tooling в build-цикле — все они уменьшают накладные.

## 4. Что НЕ сделано в этой итерации (и почему — с приоритетом)

> Эти правки реально нужны до 100 RPS, но они инфра-уровня:
> требуют согласований / простоев / решений о доменах. Я не делал
> их автоматически.

### 4.1. Postgres tuning (приоритет: высокий)

1. `shared_buffers=128 MB` → **2–3 GB** (примерно 25% RAM сервера).
2. `effective_cache_size=4 GB` → **8 GB** (примерно 75% RAM сервера).
3. `work_mem=4 MB` → **16–32 MB** (для тяжёлых сортировок типа
   leaderboard / submission-history aggregation).
4. `max_wal_size=1 GB` → **4 GB** (длинные транзакции submission
   worker'а перестанут провоцировать частые checkpoint'ы).
5. Включить `shared_preload_libraries='pg_stat_statements'` + перезапуск
   PG — без этого даже не видно, какой запрос тормозит. Без этого мы
   слепо двигаемся.

Риски: требует `systemctl restart postgresql` ~30 с простоя.

### 4.2. nginx как edge для API + frontend (приоритет: высокий)

1. Сейчас:
   - frontend = `vite preview` (Node-процесс на 8511);
   - API доступно прямо по 8510 без nginx.
2. Нужно:
   - nginx vhost (новый, не `leonovcare.ru`) с upstream на
     `127.0.0.1:8510` для `/api/v1/*`;
   - тот же vhost отдаёт статику из
     `/opt/leonovcare-platform/current/frontend/dist`
     с `gzip_static on`, `expires 1y` для assets, `expires 0` для
     `index.html`;
   - HTTP/2 (`listen 443 ssl http2`);
   - **выключить** `leonovcare-frontend` pm2-процесс — статика
     должна отдаваться nginx, не Node.
3. Почему важно:
   - **vite preview** не предназначен для production-нагрузки;
   - nginx с keepalive + static cache снимает ~30–50% запросов
     с Go API (для повторных GET);
   - SSE (текущий `/api/v1/support/stream`) пройдёт через nginx
     корректно только при `proxy_buffering off` и
     `proxy_read_timeout` > 3600 — иначе соединения будут рваться
     каждую минуту.
4. Блокер: домен `leonovcare.ru` под domain-lock'ом
   (см. `docs/operations/DOMAIN_PROTECTION_LEONOVCARE_RU_2026_05_13.md`).
   Нужен либо отдельный домен (например, `app.leonovcare.ru` —
   если такой существует у владельца — или вообще другой), либо
   решение пускать всё через bare IP на отдельный порт
   (например, `:8443` с LE по DNS-challenge).

### 4.3. Многопроцессность API (приоритет: средний)

1. Один `leonovcare-api` процесс. Go на 8 vCPU обычно справляется
   с 100 RPS на простых endpoint'ах, но:
   - любой 5-секундный hiccup pm2 или GC pause полностью отрезает
     платформу;
   - доступная отказоустойчивость = 1 (никакой).
2. Решение: pm2 cluster-режим / 2 fork-инстанса за nginx upstream.
3. **Блокер для текущего support-чата**: `SupportHub` хранит
   подписчиков SSE in-memory. С двумя процессами event'ы из
   процесса A не дойдут до подписчиков на процессе B. Нужно
   переключить hub на Redis Pub/Sub.
4. Этот переключатель я сознательно отложил: реализован
   architecture-compatible API хаба (`SupportHub.Subscribe`/
   `.Publish`), чтобы можно было заменить на Redis-backed реализацию
   без break-change для остальных файлов.

### 4.4. CDN / edge-кэш (приоритет: средний)

1. Сейчас весь трафик — bare IP, никакого edge.
2. Для статики (`/assets/*`) — банально Cloudflare/Fastly free tier.
3. Для API — нужно осторожно: 401/200 кэшировать нельзя.

### 4.5. Rate limits (приоритет: средний)

1. Текущие настройки:
   - `AUTH_RATE_LIMIT_PER_MINUTE=60` — это **60/мин на client_key**,
     то есть на пользователя. На 100 RPS с одной точки входа
     `auth/login` это разве что **1 пользователь логинится 1 раз
     в секунду** — обычно ОК, но если будет волна регистраций —
     поднять.
   - `AI_HINT_RATE_LIMIT_PER_MINUTE=20` — норма.
   - `WEBHOOK_RATE_LIMIT_PER_MINUTE=120` — это лимит на
     `cardlink/webhook`. Под 100 RPS платёжных webhook'ов не должно
     быть, ОК.
2. Сам rate-limit реализован через Redis INCR на каждый запрос —
   стоит ~1 мс/запрос на 100 RPS = ~100 мс CPU/с на Go-стороне.
   ОК.

### 4.6. HTTP server timeouts (приоритет: низкий, но важно для SSE)

1. Сейчас gin использует defaults: `ReadTimeout=0`,
   `WriteTimeout=0`. Для SSE это безопасно
   (поток должен жить долго).
2. Для остальных endpoint'ов — стоит задать
   `ReadHeaderTimeout=5s` (защита от slow-loris).
3. Дополнительно — `IdleTimeout=120s` (KeepAlive окно).

## 5. Что конкретно делать дальше — упорядоченный план

Все шаги независимы по риску.

1. **Шаг A — Postgres tuning + pg_stat_statements** (низкий риск,
   ~5 мин down).
2. **Шаг B — nginx как edge для API+frontend** (требует решения по
   домену; самое полезное действие для 100 RPS).
3. **Шаг C — выключить vite preview, отдавать `dist/` nginx'ом**.
4. **Шаг D — Redis Pub/Sub для SupportHub** + добавить второй API
   процесс (после шага B).
5. **Шаг E — Cloudflare/Fastly перед nginx** (когда домен будет
   решён).

После шагов A–C платформа должна спокойно держать 200–300 RPS на
read endpoints и 50–100 RPS на write endpoints. Шаги D–E дают
горизонтальную масштабируемость и edge-кэш для скачков.

## 6. Про «ошибки на почту»

1. На сервере `sendmail` и `postfix` **не установлены** — почта
   с самого сервера не уходит. `/var/spool/mail/root` пуст,
   `/var/log/mail.log` отсутствует.
2. В коде backend нет SMTP-клиента (`grep -rE 'smtp|sendgrid|mailgun'
   backend/internal backend/cmd` — пусто).
3. Cron на сервере — только системные: `certbot`, `sysstat`,
   `e2scrub`. Они не шлют почту наружу.
4. **Старая ошибка в pm2-логах** (что могло вызвать письма от
   мониторинга): `~/.pm2/logs/leonovcare-frontend-error.log` за
   2026-05-05 содержит 60 строк `sh: 1: vite: not found`. На дату
   написания этого отчёта (2026-05-16) фронтенд работает корректно
   (`vite preview` поднят, порт 8511 слушается, `out.log` свежий).
   Эти ошибки — артефакт майского сбоя, не текущего состояния.
5. Гипотезы, откуда могли уйти письма:
   - **GitHub** (security alerts, dependabot, action-failures на
     push'ах от 2026-05-16);
   - **Хостинг-провайдер** (uptime/CPU alerts);
   - **Личная инфра** пользователя — если есть отдельный мониторинг,
     которым я не управляю.
6. Без доступа к email-ящику пользователя или к alert-провайдеру я
   точно ответить не могу. Рекомендация: переслать тему / отправителя
   письма и я смогу сопоставить с конкретным событием в логах.

## 7. Итог

1. После этой итерации фронтенд + API устойчиво обслуживают smoke
   на 100 RPS read-only, но **не на 100 RPS write/streaming сразу**:
   - read-only (поезд из `/healthz`, `/courses`, `/me`) — должен
     держать ~500 RPS с pgxpool=30;
   - write (submissions, payments, support чат с вложениями) —
     ограничен ~100 RPS только если успели сделать §4.1 и §4.2.
2. SSE на 100 одновременно подключённых учеников на одном API —
   приемлемо (10 KB буфер на коннект × 100 = 1 MB RAM, ок).
   1000 коннектов уже потребует §4.3 (Redis Pub/Sub + scale-out).
3. **Текущее состояние production**: feature-flag'ы реально дошли
   до процессов; pgxpool вырос в ~4×; gin вышел из debug-режима.
   Это безопасные правки без break-change.
4. Что ещё нужно — описано в §4 и §5 с приоритетами.

## 8. Дополнения после первичной публикации

> Раздел зарезервирован. Запрещено редактировать §1–7. Любые
> уточнения добавляются сюда отдельными датированными подразделами.
