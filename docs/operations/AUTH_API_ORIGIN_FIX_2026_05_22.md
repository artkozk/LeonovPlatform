# AUTH API Origin Fix — 2026-05-22

## Контекст инцидента

1. Пользовательский сценарий входа показывал ошибку:
- `Не удаётся подключиться к серверу авторизации. Проверьте интернет/VPN и адрес платформы.`
2. Проблема воспроизводилась на production-URL платформы `https://platform.ngix.leonovcare.ru`.

## Root cause

1. В production-сборку frontend был зашит абсолютный API URL:
- `http://85.198.82.221:8510/api/v1`
2. При открытии платформы по HTTPS это приводило к сетевым отказам на клиенте (браузерный mixed-content/CORS класс ошибок), которые в UI маппились в generic auth network error.
3. Дополнительно backend env содержал исторический `FRONTEND_URL=http://85.198.82.221:8511`, не совпадающий с каноническим HTTPS-доменом платформы.

## Что изменено в коде

1. Обновлён runtime-резолв API URL в frontend:
- файл: `frontend/src/api/types.ts`
- поведение:
  - если задан `VITE_API_URL`, используется он;
  - для localhost сохраняется прямой режим `:<8510>`;
  - для production/non-localhost по умолчанию используется same-origin путь `https://<host>/api/v1` (через `window.location.origin`).
2. Обновлён deploy default для frontend-build:
- файл: `deploy/server/deploy.sh`
- было: `VITE_API_URL=http://85.198.82.221:8510/api/v1`
- стало: `VITE_API_URL=/api/v1`

## Почему сделано именно так

1. Same-origin `/api/v1` устраняет класс проблем с протоколом, портами и CORS при работе за reverse-proxy и TLS.
2. Изменение в `deploy.sh` защищает от повторного появления бага в следующих релизах.
3. Локальная разработка не ломается: localhost-путь сохранён отдельной веткой резолва.

## Техническая валидация после фикса

1. Локально:
- `npm test -- --run` (frontend) — PASS.
- `npm run build` (frontend) — PASS.
2. Проверка собранного bundle:
- в `dist/assets/*.js` отсутствует зашитый `http://85.198.82.221:8510/api/v1` как production base URL для браузерного runtime.
3. Production-проверка после выката:
- открыть `https://platform.ngix.leonovcare.ru/auth`;
- выполнить `POST /api/v1/auth/login` из браузера;
- убедиться, что запрос идёт на same-origin `/api/v1/auth/login` и возвращает рабочий ответ без network error.

## Фактический rollout на production (2026-05-22)

1. На сервер загружены обновлённые файлы frontend/deploy/docs в `/opt/leonovcare-platform/current`.
2. В `backend/.env` обновлён `FRONTEND_URL`:
- было: `http://85.198.82.221:8511`
- стало: `https://platform.ngix.leonovcare.ru`
3. Пересобран frontend:
- `cd /opt/leonovcare-platform/current/frontend`
- `npm ci`
- `npm run test -- --run`
- `npm run build`
4. Перезапущены процессы PM2 из `ecosystem.config.cjs`:
- `pm2 delete leonovcare-api leonovcare-api-2 leonovcare-worker`
- `pm2 start /opt/leonovcare-platform/current/deploy/server/ecosystem.config.cjs`
- `pm2 save`
5. Проверки после перезапуска:
- `curl http://127.0.0.1:8510/healthz` → `200 {"status":"ok"}`
- `curl http://127.0.0.1:8510/readyz` → `200 {"status":"ready"}`
- preflight `OPTIONS https://platform.ngix.leonovcare.ru/api/v1/auth/login` возвращает `Access-Control-Allow-Origin: https://platform.ngix.leonovcare.ru`
- `POST /api/v1/auth/login` с невалидными данными возвращает `401` (endpoint доступен и отвечает, сетевой ошибки нет)
- `GET https://platform.ngix.leonovcare.ru/auth` возвращает `200`

## Операционный комментарий

1. Исторический fallback `HARD_FALLBACK_API_URL` в коде оставлен как non-browser safety fallback (`typeof window === "undefined"`), чтобы не ломать вспомогательные non-DOM сценарии.
2. Канонический production способ для браузера теперь same-origin через nginx-vhost `platform.ngix.leonovcare.ru`.
