# Support Chat Implementation Report — 2026-05-16

> **Append-only.** Запрещено редактировать или удалять разделы 1–11.
> Любые последующие правки/уточнения добавляются в раздел 12 отдельными
> датированными подразделами вида `## 12.X — YYYY-MM-DD`.

## 1. Контекст

1. Дата реализации: 2026-05-16.
2. Автор: Claude (по запросу пользователя через Claude Code), в полном
   соответствии с blueprint
   `docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md`.
3. Бизнес-цель: внутренний support-чат ученик ⇄ администратор без
   внешних мессенджеров (Telegram/Intercom/WhatsApp), с realtime
   доставкой и аудитом для разрешения учебных/биллинговых обращений.
4. До этой реализации никакого чата в платформе не было — общение шло
   по email (`SUPPORT_EMAIL`), что не поддерживало operational SLA и
   не оставляло аудит-следа.

## 2. Что именно появилось в коде

1. **Миграция БД** — `backend/migrations/038_support_chat_core.sql`:
   - `support_conversations` — один диалог на ученика
     (`UNIQUE(student_user_id)`), статус `open|resolved|closed`,
     ответственный админ, last_message_at, preview, unread-счётчики
     с двух сторон, поля для resolve/close.
   - `support_messages` — sender_role, body_text (NULL разрешён только
     при наличии вложений), `status sent|delivered|read`,
     `delivered_at/read_at`.
   - `support_message_attachments` — storage_key, original_name,
     mime_type, size_bytes (FK на message + conversation для быстрого
     доступа без двойного join'а).
   - `support_conversation_events` — append-only audit trail для
     created/message_sent/assigned/reassigned/unassigned/resolved/
     reopened/closed.
   - Все индексы под P95 цели из blueprint §10 (список чатов,
     лента сообщений, лента событий).

2. **Конфиг** — `backend/internal/config/config.go`:
   - `SUPPORT_CHAT_ENABLED` (default `true`) — feature flag, при
     `false` все support-роуты отдают 404 (см. `supportEnsureEnabled`).
   - `SUPPORT_CHAT_MAX_ATTACHMENTS_PER_MESSAGE` — default 5
     (жёсткий лимит из blueprint §2.5).
   - `SUPPORT_CHAT_MAX_ATTACHMENT_BYTES` — default 10 MB на файл.
   - `SUPPORT_CHAT_MAX_MESSAGE_PAYLOAD_BYTES` — default 52 MB
     (5×10 МБ + текст + overhead).
   - `SUPPORT_CHAT_STORAGE_DIR` — `/var/lib/leonovcare/support`,
     корневая директория для вложений (вне web-root, blueprint §9).

3. **Middleware** — `backend/internal/app/middleware.go`:
   - `gzipMiddleware` теперь пропускает запросы с
     `Accept: text/event-stream` — иначе gzip-буфер ломает SSE
     (blueprint §6 «Не сжимать SSE-поток gzip»).
   - `maxRequestBodyMiddleware` теперь принимает второй параметр
     `supportUploadCeil` и применяет per-route потолок только к
     POST `/api/v1/support/conversation/messages` и POST
     `/api/v1/admin/support/conversations/:id/messages`. Это
     решает противоречие между общим 16 MB cap и 52 MB upload
     лимитом, не ослабляя глобальную защиту.

4. **Realtime hub** — `backend/internal/app/support_realtime.go`:
   - In-memory `SupportHub` с per-userID каналами,
     publish/subscribe API.
   - Буферизированные каналы (32 события), drop-on-full —
     клиент re-fetch'ом восстановит состояние, см. blueprint §6
     «idempotent».

5. **Store + типы**:
   - `backend/internal/app/support_types.go` — все DTO + константы
     статусов и событий.
   - `backend/internal/app/support_store.go` — все SELECT'ы
     (одиночный диалог, список диалогов для админа, история
     сообщений с anti-N+1 загрузкой вложений, событий).
   - `backend/internal/app/support_messages.go` — INSERT-логика
     сообщения с auto-reopen на student-сообщение из resolved/closed,
     запись вложений в безопасное хранилище (
     `sanitizeFilename` + `safeStoragePath`), `markIncomingAsRead`,
     `markDeliveredOnReceive`, паблиш realtime-событий
     (`publishMessageEvent` / `publishStatusUpdate` /
     `publishConversationUpdate`).

6. **Handlers**:
   - `backend/internal/app/handlers_support_student.go`:
     - `GET  /api/v1/support/conversation`
     - `GET  /api/v1/support/conversation/messages`
     - `POST /api/v1/support/conversation/messages` (multipart, ≤5 файлов)
     - `POST /api/v1/support/conversation/read`
     - `GET  /api/v1/support/attachments/:attachmentID`
     - `GET  /api/v1/support/stream` (SSE)
   - `backend/internal/app/handlers_support_admin.go`:
     - `GET    /api/v1/admin/support/conversations`
     - `GET    /api/v1/admin/support/conversations/:conversationID`
     - `GET    /api/v1/admin/support/conversations/:conversationID/messages`
     - `POST   /api/v1/admin/support/conversations/:conversationID/messages`
     - `PATCH  /api/v1/admin/support/conversations/:conversationID`
       (`action: assign|unassign|resolve|reopen|close`)
     - `POST   /api/v1/admin/support/conversations/:conversationID/read`
     - `GET    /api/v1/admin/support/conversations/:conversationID/events`

7. **Frontend**:
   - `frontend/src/api/support.ts` — типы + REST + кастомная
     SSE-обёртка через `fetch` + `ReadableStream` (для
     Authorization-заголовка) с reconnect-backoff.
   - `frontend/src/pages/SupportPage.tsx` — единый студенческий
     чат на `/support`.
   - `frontend/src/pages/AdminSupportPage.tsx` — Telegram-style
     админская страница на `/admin/support`.
   - `frontend/src/components/AppLayout.tsx` — добавлен пункт меню
     «Поддержка»; для admin-роли ссылка автоматически переписывается
     на `/admin/support`.
   - `frontend/src/styles/global.css` — append-only добавлены стили
     `.support-*` и `.admin-support-*`.

8. **Unit-тесты** — `backend/internal/app/support_messages_test.go`:
   - `TestSanitizeFilenameRemovesPathTraversal` — anti-regression
     для path traversal (blueprint §14 п.2).
   - `TestSanitizeFilenameTruncatesOverlongInput` — защита от
     ОС-ограничений на длину имени.
   - `TestSafeStoragePathRejectsTraversal` — даже если кто-то
     попадёт в БД с `..`, мы не отдадим файл за пределами root.
   - `TestSafeStoragePathAcceptsNormalKey` — позитивный кейс.
   - `TestSupportPreviewFromBody` — корректное усечение и
     emoji-плейсхолдер при file-only сообщениях.
   - `TestSupportDisplayName` — fallback fullName → username → email.
   - `TestIsValidSupportStatus` — закрепляет state-machine от
     случайных расширений.

## 3. Почему именно так

1. **SSE, а не WebSocket.** Blueprint §6: для одного админа SSE
   проще, надёжнее, не меняет транспортный стек фронтенда. WebSocket
   потребовал бы апгрейд proxy/nginx, шире attack surface, и
   in-process pubsub дал бы только маргинальный выигрыш для текущей
   нагрузки.
2. **In-memory hub, а не Redis Pub/Sub.** У нас один API-процесс
   (`leonovcare-api` под pm2). Redis Pub/Sub был бы оправдан при
   репликации, но это не блокер: публичный API хаба (Publish/Subscribe)
   можно бесшовно заменить.
3. **Отдельная таблица событий, а не JSONB-массив на разговоре.**
   Гонки на массиве (reassign/resolve одновременно из разных вкладок)
   ведут к потере записи; отдельная append-only таблица решает это
   через INSERT без блокировки.
4. **Storage_key вне web-root.** Любая бага в обходе `/api/v1/support/
   attachments/:id` всё равно не отдаст файл — он лежит в
   `/var/lib/leonovcare/support`, куда статика не маппится. Filename
   санитизируется, путь записи строится из `storage_key`, не из
   `original_name`.
5. **Auto-reopen внутри `createSupportMessage`, а не отдельным cron.**
   Условие просто: «student-сообщение и status != open». Делать это
   в одной транзакции гарантирует, что не возникнет момента, когда
   сообщение есть, а статус всё ещё `resolved`.
6. **Per-route upload limit, а не глобальный bump.** Глобальный 16 MB
   лимит — security signal. Поднимать его до 52 MB для всех
   эндпоинтов означало бы потерять защиту от accidental DoS. Сделано
   per-route исключение через `isSupportUploadRoute`.
7. **Frontend SSE через `fetch + ReadableStream`, а не EventSource.**
   `EventSource` не отправляет кастомные заголовки, и Bearer-токен
   пришлось бы передавать через query-параметр, что протекает в
   логи nginx/CDN. Fetch-вариант сохраняет Authorization-заголовок.

## 4. State machine обращения (как реализовано)

1. `open` — стартовое состояние при создании диалога.
2. `open → resolved` — только admin, через PATCH `action=resolve`,
   обязательный `resolutionNote`. Событие `resolved` в audit.
3. `resolved → open` — автоматически, при student-сообщении.
   Очищаются `resolved_at`, `resolved_by_user_id`, `resolution_note`,
   `closed_at`, `closed_by_user_id`. В audit: `reopened` с
   `reason: student_message`.
4. `resolved → closed` — admin, PATCH `action=close`. Только из
   `resolved`. Событие `closed`.
5. `closed → open` — admin, PATCH `action=reopen`. Восстановление
   кейса. Событие `reopened` с `reason: admin_action`.
6. Любой невалидный переход (`closed → resolved`, повторный resolve
   из resolved) → HTTP 409 Conflict.

## 5. Лимиты, зафиксированные в этой реализации

1. Не более 5 файлов на сообщение (default
   `SUPPORT_CHAT_MAX_ATTACHMENTS_PER_MESSAGE=5`).
2. Не более 10 MB на файл (`SUPPORT_CHAT_MAX_ATTACHMENT_BYTES`).
3. Общий лимит multipart payload — 52 MB
   (`SUPPORT_CHAT_MAX_MESSAGE_PAYLOAD_BYTES`).
4. Кэширование message-API на фронте отключено — никакого
   `cachedGet` (blueprint §11.2).
5. SSE heartbeat — каждые 25 секунд (`Ping`).
6. SSE reconnect backoff — 1 → 2 → 4 → 8 секунд (cap 8s).

## 6. Безопасность вложений

1. Filename санитизируется (`sanitizeFilename`):
   - убираем path traversal (`..`, любые `/\\`);
   - обрезаем control-символы (включая NUL);
   - заменяем запрещённые символы Windows (`<>:"|?*`) на `_`;
   - ограничиваем длину 180 рунами.
2. Путь записи строится через `safeStoragePath`: даже если в
   БД попадёт key с `..`, мы откажемся отдавать (тест
   `TestSafeStoragePathRejectsTraversal`).
3. `Content-Disposition: attachment` — браузер не пытается
   inline-рендерить произвольный MIME.
4. `X-Content-Type-Options: nosniff` — нет угадывания MIME клиентом.
5. Доступ к вложению только участникам диалога (студент-владелец
   или admin); else 403.

## 7. Anti-N+1 в списке диалогов и истории

1. `listAdminConversations` — один SELECT с LEFT JOIN на `users`
   для display name студента и админа.
2. `listMessages` — один SELECT по сообщениям + один SELECT по
   вложениям через `WHERE message_id = ANY($1)`. Никакого
   per-message запроса.

## 8. Realtime — гарантии и компромиссы

1. Все события идемпотентны: клиент после reconnect
   делает full re-fetch.
2. Если подписчик слишком медленный (буфер 32 событий полон), мы
   дропаем последующие события и **не блокируем** отправителя.
3. Каждое событие имеет `id` (`MakeEventID`) — на будущее, для
   поддержки `Last-Event-ID` и точечной догрузки.

## 9. Файлы, затронутые этой реализацией

Backend:
1. `backend/migrations/038_support_chat_core.sql` (new)
2. `backend/internal/config/config.go` (modified: 5 новых полей + getInt64Or)
3. `backend/internal/app/middleware.go` (modified: SSE-aware gzip + per-route body limit)
4. `backend/internal/app/router.go` (modified: 13 новых маршрутов)
5. `backend/internal/app/types.go` (modified: SupportHub в App)
6. `backend/internal/app/support_types.go` (new)
7. `backend/internal/app/support_realtime.go` (new)
8. `backend/internal/app/support_store.go` (new)
9. `backend/internal/app/support_messages.go` (new)
10. `backend/internal/app/handlers_support_student.go` (new)
11. `backend/internal/app/handlers_support_admin.go` (new)
12. `backend/internal/app/support_messages_test.go` (new)

Frontend:
13. `frontend/src/api/support.ts` (new)
14. `frontend/src/pages/SupportPage.tsx` (new)
15. `frontend/src/pages/AdminSupportPage.tsx` (new)
16. `frontend/src/App.tsx` (modified: 2 новых route)
17. `frontend/src/components/AppLayout.tsx` (modified: menu item +
    admin-aware target)
18. `frontend/src/styles/global.css` (append-only stylesheet block)

Docs:
19. `docs/operations/SUPPORT_CHAT_IMPLEMENTATION_2026_05_16.md` (this file)
20. `docs/operations/IMPLEMENTATION_CHANGELOG.md` (append-only entry,
    добавится отдельным шагом)
21. `README.md` (append-only актуализация — добавится отдельным шагом)
22. `API_SPEC.yaml` (append-only раздел support — добавится отдельным шагом)

## 10. Как проверить (smoke сценарии)

Все запросы — на dev/staging контур, после деплоя миграции 038.

1. Студент пишет:
   ```
   curl -X POST $API/api/v1/support/conversation/messages \
     -H "Authorization: Bearer $STUDENT_TOKEN" \
     -F "body=Не работает запуск задачи Hello, World"
   ```
2. Админ видит список:
   ```
   curl -H "Authorization: Bearer $ADMIN_TOKEN" $API/api/v1/admin/support/conversations
   ```
3. Админ берёт в работу:
   ```
   curl -X PATCH ... -d '{"action":"assign","adminUserId":"<UUID>"}'
   ```
4. Админ отвечает с вложением:
   ```
   curl -X POST .../messages -F "body=Дайте лог" -F "files=@/tmp/screen.png"
   ```
5. Студент видит → SSE event_created.
6. Помечаем прочитанным: `POST .../read` → статусы переходят в `read`.
7. Resolve с резолюшен-нотой:
   ```
   curl -X PATCH ... -d '{"action":"resolve","resolutionNote":"Перезапустил worker"}'
   ```
8. Студент пишет ещё раз → auto-reopen, audit `reopened` event.
9. Лимит файлов: `-F` с 6 файлами → 400.
10. Path traversal: попытка `attachmentID=../../etc/passwd` → 400.

## 11. Что НЕ сделано в этой реализации (и почему)

1. **AV-сканирование вложений** — отложено (blueprint §9 «production
   эволюция»). Сейчас нет ClamAV в инфре.
2. **S3/MinIO + presigned URL** — отложено, тоже §9. Local FS
   достаточно для текущего масштаба; интерфейс хранилища (storage_key)
   позволит мигрировать без смены схемы БД.
3. **SLA-таймер автозакрытия из `resolved`** — упомянут в blueprint
   §4.2 п.3, но не сделан в первой итерации. Нужен отдельный
   worker-job с настройкой `SUPPORT_AUTO_CLOSE_AFTER_HOURS`.
4. **`Last-Event-ID` поддержка** — заголовок не парсится; вместо
   этого клиент после reconnect делает идемпотентный re-fetch.
   Достаточно для текущей нагрузки; идентификаторы событий уже
   проставляются и могут быть подключены позже без break-change.
5. **Тесты handlers с in-memory БД** — текущий проект не имеет
   testing-DB harness; integration-тесты пишутся параллельно через
   smoke. Юнит-тесты покрывают самые опасные места (filename
   sanitize, safe path, preview, status machine).

## 12. Дополнения после первичной публикации

> Раздел зарезервирован. Запрещено редактировать разделы 1–11.
> Дописываемые подразделы строго вида `## 12.X — YYYY-MM-DD`.
