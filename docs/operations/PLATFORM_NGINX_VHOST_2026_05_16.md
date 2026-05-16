# Platform Nginx Vhost & HTTPS — 2026-05-16

> **Append-only.** Запрещено редактировать или удалять разделы 1–7.
> Любые правки/уточнения — отдельными подразделами в §8 вида
> `## 8.X — YYYY-MM-DD`.

## 1. Контекст

1. Дата: 2026-05-16.
2. Автор: Claude (по запросу пользователя через Claude Code).
3. Триггер: пункт §4.2 из
   `docs/operations/100RPS_READINESS_2026_05_16.md` — нужен полноценный
   nginx edge перед API и frontend для подготовки к ~100 RPS.
4. Пользователь выделил выделенный поддомен
   `platform.ngix.leonovcare.ru` и направил A-запись на
   `85.198.82.221`. Domain-lock policy на `leonovcare.ru` не задета
   (см. `docs/operations/DOMAIN_PROTECTION_LEONOVCARE_RU_2026_05_13.md`)
   — этот основной домен по-прежнему принадлежит другому проекту.

## 2. Что сделано на production

1. На сервере создан и активирован nginx vhost:
   - `/etc/nginx/sites-available/platform.ngix.leonovcare.ru`
     (зеркало в репо: `deploy/server/nginx/platform.ngix.leonovcare.ru.conf`);
   - symlink в `/etc/nginx/sites-enabled/`.
2. `nginx -t` пройден, `systemctl reload nginx` выполнен. Существующие
   vhost'ы `leonovcare.ru / shop.e-rd.ru / e-rd.ru` остались
   нетронутыми (HTTPS 200 после reload подтверждено).
3. Получен сертификат Let's Encrypt:
   `certbot --nginx -d platform.ngix.leonovcare.ru --non-interactive --agree-tos --redirect`
   - сертификат: `/etc/letsencrypt/live/platform.ngix.leonovcare.ru/`
   - срок: до `2026-08-14` (auto-renew через `certbot.timer`).
4. certbot сам добавил 443 server-блок и редирект 80→443.

## 3. Что обслуживает vhost

1. SPA (frontend dist) — отдаётся напрямую nginx'ом из
   `/opt/leonovcare-platform/current/frontend/dist`. Никакого
   `vite preview` Node-процесса между nginx и пользователем НЕТ.
2. `/api/v1/*` → `proxy_pass http://127.0.0.1:8510` (Go API).
3. `/healthz`, `/readyz` → точечно проксируются на Go API
   (для внешних health-чек механизмов).
4. `/api/v1/support/stream` — отдельный `location =` с
   `proxy_buffering off; gzip off; proxy_read_timeout 3600s` для
   корректной работы SSE без буферизации
   (см. blueprint `docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md` §6).
5. `/assets/*` — `Cache-Control: public, max-age=31536000, immutable`
   (Vite кладёт build-hash в имя файла, поэтому immutable безопасен).
6. SPA-fallback `try_files $uri /index.html` — React Router сам
   разрулит маршруты типа `/support`, `/admin/support` и т.д.

## 4. Что НЕ сделано в этой итерации (осознанно)

1. **PM2-процесс `leonovcare-frontend` (vite preview) НЕ удалён.**
   Сейчас одновременно работают:
   - nginx отдаёт `dist/` для домена `platform.ngix.leonovcare.ru` —
     это новый production-путь;
   - `pm2 leonovcare-frontend` (vite preview на 8511) — оставлен
     как fallback на случай rollback'а.
   Решение убрать его — отдельный шаг, требует подтверждения
   пользователя, чтобы не было «тихо отключили доступ через
   `:8511`».
2. **2-й API-инстанс и Redis Pub/Sub для SupportHub** —
   зависит от перехода на multi-process API; зафиксировано в
   `100RPS_READINESS_2026_05_16.md` §4.3.
3. **Postgres tuning** (§4.1 в том же документе) — отдельный шаг
   с микро-даунтаймом.

## 5. Безопасность и анти-регрессии

1. Никакие чужие vhost'ы не редактированы; внесён только новый файл.
2. Конфиг каждого ответа SPA несёт `Cache-Control: no-cache` для
   `index.html` — пользователи получают свежий HTML при каждой
   загрузке, поэтому деплой фронта не зависает в браузерном кэше.
3. `client_max_body_size 64m` явно проставлен и в `server`-блоке,
   и в `location /api/v1/` — чтобы при включённом nginx
   support-чат принимал свои до 52 МБ payload, не упираясь в
   nginx-уровневый лимит 1m (default).
4. Сертификат выпущен с `--non-interactive --agree-tos`. ACME
   валидация прошла, потому что public-DNS (Google/Cloudflare/Yandex)
   правильно резолвят `platform.ngix.leonovcare.ru` →
   `85.198.82.221`. Локальный DNS сервера ещё держит timeweb
   parking IP (92.53.123.166) — но это не влияет на ACME (Let's Encrypt
   ходит из своей сети).
5. Auto-renew проверен через `systemctl list-timers` — `certbot.timer`
   активен и стрельнёт ежесуточно.

## 6. Smoke-проверки (выполнены 2026-05-16)

Все проверки делались на сервере с принудительным резолвингом
`--resolve platform.ngix.leonovcare.ru:443:85.198.82.221`, чтобы
обойти локальный stale-DNS:

1. `GET https://.../healthz` → `200 {"status":"ok"}`.
2. `GET https://.../readyz`  → `200 {"status":"ready"}`.
3. `GET https://.../api/v1/courses` (без auth) → `401` (как и должно).
4. `GET https://.../`  → `200`, отдаётся `index.html` из `dist/`.
5. `HTTP /` → `301 https://platform.ngix.leonovcare.ru/` (редирект
   на HTTPS, certbot-managed).
6. Параллельный smoke сторонних сайтов:
   - `https://leonovcare.ru/`  → 200,
   - `https://shop.e-rd.ru/`    → 200,
   - `https://e-rd.ru/`         → 200.

## 7. Файлы, изменённые в этой итерации

1. `deploy/server/nginx/platform.ngix.leonovcare.ru.conf` —
   нормальная копия активного vhost из `/etc/nginx/sites-available/`
   (синхронно с production на дату коммита).
2. `docs/operations/PLATFORM_NGINX_VHOST_2026_05_16.md` —
   этот документ.
3. `docs/operations/IMPLEMENTATION_CHANGELOG.md` — append-only entry.
4. `README.md` — append-only актуализация.

## 8. Дополнения после первичной публикации

> Раздел зарезервирован. Запрещено редактировать §1–7. Любые
> уточнения добавляются сюда отдельными датированными подразделами.
