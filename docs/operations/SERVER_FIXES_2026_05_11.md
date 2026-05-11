# Server Fix Log — 2026-05-11

## Контекст

Проверка состояния production-сервера (`85.198.82.221`) выявила несколько критических проблем.
Все исправления выполнены в ходе одной сессии.

---

## Исправления на сервере

### 1. Nginx: неверный роутинг для `leonovcare.ru`

**Проблема:** `leonovcare.ru` отдавал фронтенд из `/main/LeonovCare/LeonovCare` (другое приложение — AutoHh)
и проксировал `/api/v1/` на порт `8080` (interview-assistant), а не на LeonovCare API (`8510`).

**Исправление:**
- Обновлён `/etc/nginx/sites-available/leonovcare.ru`
- `root` → `/opt/leonovcare-platform/current/frontend/dist`
- `/api/v1/` → `proxy_pass http://127.0.0.1:8510`
- Добавлены security-заголовки: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `HSTS`
- Добавлено кэширование статики (30 дней)
- Убраны устаревшие `location /actuator/` и двойной `/api/v1/api/v1/`
- Бэкап: `/etc/nginx/sites-available/leonovcare.ru.bak_20260511`

**Проверка:**
```bash
curl -sk https://leonovcare.ru/healthz
# {"service":"Leonov Care Platform","status":"ok"}
curl -sk https://leonovcare.ru/api/v1/courses
# {"error":"missing authorization header"}   ← 401, правильно
```

### 2. PM2: остановлен `interview-helper-api` (654 рестарта)

**Проблема:** PM2-процесс `interview-helper-api` (id=0) пытался запуститься на порту `8080`,
занятом `interview-assistant.jar`. Каждый запуск падал, PM2 рестартовал,
Java-процесс при старте потреблял ~400% CPU → load average: **2.56 / 3.46 / 3.75**.

**Исправление:**
```bash
pm2 stop interview-helper-api
pm2 save
```

**Результат:** load average после остановки: **0.70 / 2.54 / 3.18**

### 3. Очистка старых release-архивов

**Проблема:** 57 `.tgz` архивов (v229–v290) в `/opt/leonovcare-platform/current/`, суммарно ~886 МБ.
Один файл весил 569 МБ.

**Исправление:**
```bash
rm -f /opt/leonovcare-platform/current/leonovcare_*.tgz
```

**Результат:** диск: 49G → 48G использовано.

---

## Исправления в коде

### 4. `rows.Err()` не проверялся в 6 обработчиках

**Файл:** `backend/internal/app/handlers_learning.go`

Добавлены проверки после `for rows.Next()` в:
- `ListCourses` (строка 144)
- `GetTask` (строка 717)
- `SubmissionHistory` (строка 1174)
- `MyAchievements` (строка 1210)
- `Leaderboard` (строка 1237)
- `AdminMetricsExportCSV` (строка 1319)

Без проверки `rows.Err()` при сетевом сбое БД клиент получал
частичный результат с кодом `200` вместо `500`.

### 5. Polling в `TaskPage` без защиты от unmount

**Файл:** `frontend/src/pages/TaskPage.tsx`

Добавлен `submissionPollingAbortRef` — при уходе пользователя со страницы
цикл проверки статуса сабмишена прекращает вызывать `setState`,
предотвращая React-предупреждения и утечки.

### 6. `ErrorBoundary` в `App.tsx`

**Файл:** `frontend/src/components/ErrorBoundary.tsx` (новый)

Обёртка на уровне корневого компонента: вместо белого экрана при необработанном
исключении показывается человекочитаемое сообщение с кнопкой перезагрузки.

### 7. Security-заголовки в Go-роутере

**Файл:** `backend/internal/app/router.go`

Добавлены `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`,
`Referrer-Policy: strict-origin-when-cross-origin` на уровне middleware.
HSTS (`Strict-Transport-Security`) выставляется nginx.

---

## Состояние сервера после исправлений

| Компонент | До | После |
|-----------|-----|--------|
| `leonovcare.ru` домен | AutoHh (неверно) | LeonovCare Platform |
| `/api/v1/` прокси | порт 8080 (interview) | порт 8510 (leonovcare-api) |
| Load average | 2.56 / 3.46 / 3.75 | 0.70 / 2.54 / 3.18 |
| Архивы | 886 МБ мусора | очищено |
| PM2 рестарты | 654 (crash loop) | 0 |
| Security-заголовки | отсутствовали | добавлены (nginx + Go) |
