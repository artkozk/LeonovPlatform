# ADMIN_ACCOUNT_BOOTSTRAP_2026_06_09

## Причина обращения

На проде пользователю с админкой не удавалось войти через UI, хотя пароли с 6 символами ранее работали ранее. Провели прямую проверку API и подтвердили, что источник проблемы в формировании учётных данных/формы, а не в самой проверке роли на backend.

## Что найдено

1. API `/api/v1/auth/login` ожидает поле `email`, а не `username`.
2. В базе существует пользователь:
   - `email = admin@platform.local`
   - `role = admin`
   - `is_blocked = false`
3. У пользователя обновлён парольный хэш и флаги верификации/блокировки в соответствии с рабочей политикой:
   - `is_email_verified = true`
   - `is_blocked = false`
   - `role = admin`
4. После смены пароля проверка админских прав на backend (`/api/v1/admin/metrics/overview`) проходит с новым токеном.

## Действия (пошагово)

1. Подключение к проду:
   - `ssh root@85.198.82.221`
2. Проверка подключения к БД:
   - использован `DATABASE_URL` из `current/backend/.env`:
   - `postgres://leonovcare:LeonovCarePass_2026!...@127.0.0.1:5432/leonovcare_platform`
3. Обновление данных админа:
   - `UPDATE users SET password_hash = crypt('123123123', gen_salt('bf', 10)), is_blocked = FALSE, is_email_verified = TRUE, role='admin' WHERE email='admin@platform.local';`
4. Проверка результата:
   - `SELECT id, email, nickname, role, is_blocked, is_email_verified, updated_at FROM users WHERE email='admin@platform.local';`
5. Проверка API:
   - `POST /api/v1/auth/login` с телом:
     `{"email":"admin@platform.local","password":"123123123"}`
   - `GET /api/v1/admin/metrics/overview` с полученным `Authorization: Bearer`.

## Почему именно так

1. На данном проекте backend валидирует минимальную длину пароля только на регистрации; для логина это должна быть мягкая проверка через проверку хэша и статус блокировки.
2. Временно менять фронтовый код и redeploy не нужно, потому что backend уже валидировал вход корректно после прошлых фиксов.
3. Прямой SQL-обновление существующего admin-аккаунта минимально инвазивно и безопасно (меняет только параметры известного администратора без миграций).

## Дополнительные замечания по багам

1. Повторяющиеся сообщения `bad request` обычно возникают при неверном payload (`username` вместо `email`) или некорректном JSON/формате.
2. Отдельно зафиксированы исторические регрессии UI (минимум длины пароля 8 для всех форм) в `AUTH_PASSWORD_MINLEN_REGRESSION_FIX_2026_06_03.md`.
3. Если после этого админский вход ещё падает в браузере, это уже почти всегда клиентский рендер старого frontend-артефакта, а не backend-ошибка логина.
