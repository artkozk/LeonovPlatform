# Support Chat — Attachment Viewer & Auth-Aware Download (2026-05-17)

> Append-only. §1–6 не редактировать; добавления только в §7.

## 1. Контекст

1. Дата: 2026-05-17.
2. Автор: Claude.
3. Симптом, описанный пользователем: «нельзя просматривать медиа».
   На скриншоте — `{"error":"missing authorization header"}`,
   страница `/api/v1/support/attachments/<id>` открыта прямо из
   `<a href>` ссылки в чате.

## 2. Корневая причина

1. Backend `GET /api/v1/support/attachments/:id` требует Bearer-токен
   (см. blueprint §9 и handlers_support_student.go).
2. Frontend в обеих страницах (`SupportPage`, `AdminSupportPage`)
   рендерил вложение как обычный `<a href={downloadUrl} target="_blank">`.
3. Браузер при клике по `<a>` НЕ отправляет `Authorization` —
   токен живёт только в JS-памяти (axios interceptor). Запрос
   улетел без заголовка → 401.

## 3. Что сделано

### 3.1. Backend — Content-Disposition разделён по типу MIME

`backend/internal/app/handlers_support_student.go::GetSupportAttachment`:
- Если MIME попадает в whitelist «media-safe» (`image/*` кроме
  `image/svg+xml`, `video/*`, `audio/*`, `application/pdf`) —
  `Content-Disposition: inline`. Браузер показывает контент
  прямо в новой вкладке.
- Иначе — `attachment` (как и было). Защита от XSS через произвольный
  HTML/SVG сохранена.
- `X-Content-Type-Options: nosniff` остался для всех ответов.

Новая функция `supportMimeAllowsInline` (в `support_messages.go`) +
unit-тест `TestSupportMimeAllowsInline` со списком safe/non-safe
кейсов (включая `image/svg+xml` и `text/html` — должны быть
attachment).

### 3.2. Frontend — auth-aware open-attachment

Новый модуль `frontend/src/api/supportAttachments.ts`:
1. `openAttachment(att)` — `fetch(downloadUrl, { Authorization: Bearer })`.
2. На успех — `URL.createObjectURL(blob)`.
3. Если MIME inline-safe → `window.open(blobUrl, "_blank")` —
   браузер показывает картинку/видео прямо в новой вкладке.
4. Иначе → программный `<a download>` с original filename, чтобы
   сохранилось как файл.
5. Через 60 сек blob URL `revokeObjectURL`'ится — освобождаем память.
6. Ошибки нормализуются в человекочитаемые сообщения для UI.

Обе страницы (`SupportPage.tsx`, `AdminSupportPage.tsx`) переведены
с `<a href>` на `<button class="support-attachment-link" onClick>`,
вызывающий `openAttachment`. Ошибки кидаются в существующий
`setError` — пользователь увидит баннер.

CSS-класс `.support-attachment-link` дописан в `global.css`
(append-only) — выглядит как обычная ссылка.

### 3.3. Production smoke

- backend rebuild + `go test ./internal/app/ -run 'Support|Mime'` PASS;
- frontend rebuild dist (бандл `index-BbIM5msu.js`);
- `pm2 restart leonovcare-api leonovcare-api-2 --update-env` — оба online;
- GET вложения с Bearer'ом → **200 OK**, `Content-Disposition: inline`,
  `Content-Type: audio/mpeg`, файл отдан целиком (1.8 MB mp3
  скачан корректно, `file` подтверждает MPEG ADTS);
- GET без auth → **401** (unchanged).

## 4. Почему именно так

1. **fetch + blob URL** (а не presigned URL):
   - Не требует backend-изменений (HMAC, secret rotation, валидация TTL).
   - Сразу работает с существующим Bearer-флоу без дублей auth-логики.
2. **inline для media** улучшает UX: клик по картинке → открывается
   в новой вкладке; не приходится «сначала скачайте, потом откройте».
3. **SVG исключён** из inline-whitelist намеренно — SVG может
   содержать `<script>` и при inline-рендере выполнится в контексте
   нашего домена. Останется как `attachment`.
4. **revokeObjectURL через 60s** освобождает память, при этом
   браузерная вкладка успевает прочитать ресурс (опытным путём
   фрейм рендерится за < 1 сек).

## 5. Что НЕ сделано (отложено)

1. **Presigned URL** (signed `?t=<hmac>&exp=<unix>` token) — даст:
   - возможность правильных `Range`-запросов для больших видео
     (сейчас blob грузится целиком в память);
   - возможность вставить `<img src=...>` / `<video src=...>` прямо
     в чат без клика.
   Имеет смысл при росте размера типичного вложения. Зафиксировано
   в blueprint §9 «production evolution».
2. **Thumbnail-предпросмотр** маленьких картинок прямо в ленте
   сообщений — отдельная задача.
3. **Streaming для больших файлов** — fetch+blob тащит всё в память;
   при 50+ MB видео это уже неприемлемо. Решится presigned URL.

## 6. Файлы

Backend:
1. `backend/internal/app/handlers_support_student.go` — inline/attachment branching.
2. `backend/internal/app/support_messages.go` — `supportMimeAllowsInline`.
3. `backend/internal/app/support_messages_test.go` — `TestSupportMimeAllowsInline`.

Frontend:
4. `frontend/src/api/supportAttachments.ts` (new) — `openAttachment` helper.
5. `frontend/src/pages/SupportPage.tsx` — `<a>` → `<button onClick>`.
6. `frontend/src/pages/AdminSupportPage.tsx` — same.
7. `frontend/src/styles/global.css` — `.support-attachment-link` стили.

Docs:
8. `docs/operations/SUPPORT_ATTACHMENT_VIEWER_2026_05_17.md` — этот документ.
9. `docs/operations/IMPLEMENTATION_CHANGELOG.md` — append-only entry.

## 7. Дополнения

> Раздел зарезервирован. §1–6 не редактировать.
