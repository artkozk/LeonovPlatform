# Support Recovery Report — 2026-05-25

## Context

В текущей рабочей линии платформы support-функционал оказался деградирован относительно `main`.
Пользовательский эффект: отсутствовал полноценный продуктовый контур `/support` и `/admin/support` (частично/полностью выпадали backend и frontend части).

## When and why support dropped

- Опорный коммит feature support в `main`:
  - `30bb920` от `2026-05-16 11:47:55 +0300`
  - сообщение: `feat(support): implement embedded support chat (student <-> admin) per blueprint`
- Merge-base текущей ветки с `main`:
  - `3d5c9a2` от `2026-05-16 08:31:29 +0300`
- Вывод:
  - текущая ветка разошлась с `main` **до** feature-коммита support;
  - support не «сломался внутри одной и той же линии», а **не был перенесён целиком** в эту ветку;
  - позже были точечные фиксы стилей, но без полного возврата feature-контракта.

## Recovery scope executed

### Backend restored

- Восстановлены файлы:
  - `backend/internal/app/handlers_support_admin.go`
  - `backend/internal/app/handlers_support_student.go`
  - `backend/internal/app/support_messages.go`
  - `backend/internal/app/support_store.go`
  - `backend/internal/app/support_types.go`
  - `backend/internal/app/support_realtime.go`
  - тесты `support_messages_test.go`, `support_realtime_test.go`
- Подключены инфраструктурные изменения:
  - `backend/internal/config/config.go` — env-параметры support;
  - `backend/internal/app/types.go` — lifecycle `SupportHub`;
  - `backend/internal/app/middleware.go` — SSE без gzip + лимиты payload для upload;
  - `backend/internal/app/router.go` — маршруты `/api/v1/support/*` и `/api/v1/admin/support/*`.

### DB schema restored

- Добавлена миграция:
  - `backend/migrations/039_support_chat_core.sql`
- Причина номера `039`:
  - `038` уже занят другой миграцией в текущей линии.

### Frontend restored

- Возвращены страницы и API-клиенты:
  - `frontend/src/pages/SupportPage.tsx`
  - `frontend/src/pages/AdminSupportPage.tsx`
  - `frontend/src/api/support.ts`
  - `frontend/src/api/supportAttachments.ts`
- Подключены маршруты и навигация:
  - `frontend/src/App.tsx` (`/support`, `/admin/support`)
  - `frontend/src/components/AppLayout.tsx` (пункт меню `Поддержка`, admin-redirect)

## Verification

### Compile/test

- `go test ./...` (backend) — PASS.
- `npm test -- --watch=false` (frontend) — PASS.
- `npm run build` (frontend) — PASS.

### Behavioral expectations after recovery

- Доступны экраны `/support` и `/admin/support`.
- Работают:
  - список обращений;
  - открытие треда;
  - отправка сообщений;
  - вложения;
  - read/status;
  - SSE обновления.

## Why recovered this way

- Выбран точечный перенос support-модулей из `main`, чтобы не перетирать текущие фиксы lesson/task/quiz в ветке.
- Восстановлен полный контур (backend + migration + frontend + routing), иначе feature остаётся частично-рабочей и снова регрессирует в проде.
