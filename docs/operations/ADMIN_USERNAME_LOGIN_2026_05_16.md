# Username login (admin shortcut) — 2026-05-16

> Append-only. §1–6 не редактировать; добавления только в §7.

## 1. Контекст

1. Дата: 2026-05-16.
2. Автор: Claude.
3. Запрос пользователя: дать админу логиниться коротко (`admin/123123`),
   не печатая полный email.

## 2. Изменения

1. `backend/internal/app/handlers_auth.go::Login`: если поле `email`
   не содержит `@` — lookup по `LOWER(users.username)` вместо email.
   Email-flow для строк с `@` не изменился: те же `normalizeAndValidateEmail`,
   тот же запрос по `users.email`.
2. Создан админский аккаунт на проде:
   - `email = admin@platform.local`,
   - `username = admin`,
   - `nickname = admin`,
   - `password = 123123` (bcrypt cost 10),
   - `role = admin`,
   - `is_email_verified = true`,
   - `public_id = LC-…` (сгенерирован SQL),
   - вставлена строка в `user_settings` (иначе `/me` падал в 500
     из-за NULL'ов после LEFT JOIN).

## 3. Smoke на production

1. `POST /api/v1/auth/login {"email":"admin","password":"123123"}` → 200, accessToken.
2. `POST /api/v1/auth/login {"email":"admin@platform.local","password":"123123"}` → 200.
3. `POST /api/v1/auth/login {"email":"admin","password":"WRONG"}` → 401.
4. `POST /api/v1/auth/login {"email":"nonexistent_user","password":"123123"}` → 401.
5. `GET /api/v1/me` с access токеном → `role: "admin"`.

## 4. Почему именно так

1. Минимально-инвазивно: меняется только разветвление в Login. Все
   существующие email-логины работают как раньше.
2. Безопасность сохранена: bcrypt-проверка пароля одинаковая в обеих
   ветках. Brute-force ограничен существующим `AUTH_RATE_LIMIT_PER_MINUTE`.
3. Username case-insensitive (`LOWER(...)`), как email.
4. Никакой backdoor для конкретного `admin` — просто generic
   username-login для любого пользователя с непустым username.
5. Register по-прежнему требует валидный email — username-логин
   только на login-стороне.

## 5. Как зайти в админку

1. Открыть `https://platform.ngix.leonovcare.ru/`.
2. Email/login: `admin`.
3. Пароль: `123123`.
4. Перейти на `/admin` (или клик «Админ» в шапке) — общая админка.
5. `/admin/support` — Telegram-style чат поддержки.

## 6. Как сменить пароль / отозвать

```sql
-- Сменить пароль (PG psql):
\set newhash `python3 -c "import bcrypt; import sys; sys.stdout.write(bcrypt.hashpw(b'NEW_PASS', bcrypt.gensalt(rounds=10)).decode())"`
UPDATE users SET password_hash = :'newhash' WHERE username = 'admin';

-- Отозвать админ-роль:
UPDATE users SET role = 'student' WHERE username = 'admin';

-- Полностью удалить аккаунт (каскад снесёт связанное):
DELETE FROM users WHERE username = 'admin';
```

## 7. Дополнения

> Раздел зарезервирован. §1–6 не редактировать.
