# Auth Full Audit 2026-05-10

## 1. Контекст и цель

1. Пользовательский запрос: проверить, работает ли регистрация новых пользователей, и провести полный тест auth-взаимодействий.
2. Цель этого аудита: зафиксировать фактическое поведение production API, устранить обнаруженные дефекты в коде, повторно проверить сценарии и оставить подробный append-only протокол для ревью.

## 2. Что считалось полным auth-контуром в этой проверке

1. `GET /healthz`, `GET /readyz`.
2. `POST /api/v1/auth/register`:
- успешный сценарий;
- конфликт по `email`;
- конфликт по `nickname`;
- кириллический nickname;
- nickname, который после нормализации становится короче 3 символов.
3. `POST /api/v1/auth/login`:
- успешный сценарий;
- неверный пароль;
- email с пробелами и верхним регистром.
4. `POST /api/v1/auth/refresh`:
- успешная ротация токенов;
- повторное использование старого refresh token.
5. `GET /api/v1/me`:
- с валидным access token;
- без access token.
6. Password recovery:
- `POST /api/v1/auth/forgot-password` для существующего и несуществующего email;
- `POST /api/v1/auth/reset-password` с невалидным UUID и несуществующим UUID.
7. Email verify:
- `POST /api/v1/auth/verify-email` с невалидным UUID и несуществующим UUID.

## 3. Pre-fix production-аудит (до деплоя исправления)

Дата проверки: `2026-05-10`  
Контур: `http://85.198.82.221:8510`

Итог pre-fix матрицы:

1. Всего сценариев: `19`.
2. Успешно: `17`.
3. Падает: `2`.

Падающие сценарии:

1. `login_email_with_spaces_should_work`:
- фактический ответ: `400 bad request`;
- детали: `Field validation for 'Email' failed on the 'email' tag`.
2. `register_cyrillic_nickname_should_work`:
- фактический ответ: `400 bad request`;
- детали: `nickname must contain letters, numbers, underscore or hyphen`.

Почему это признано дефектом:

1. По текущему контракту backend должен нормализовать email (`trim + lowercase`) и не ломать вход при пробелах вокруг адреса.
2. Русскоязычный продуктовый сценарий требует поддержки кириллических nickname (например, `Иван Петров` -> `иван_петров`).

## 4. Корневая причина и фиксация в коде

### 4.1 Root cause №1: email валидация выполнялась до нормализации

1. В `register/login/forgot-password` использовался `binding:"required,email"` в структуре запроса.
2. `ShouldBindJSON` запускал валидацию до вызова `normalizeEmail`, поэтому `email` с ведущими/замыкающими пробелами отбрасывался на этапе bind.

### 4.2 Что исправлено

1. Файл: `backend/internal/app/handlers_auth.go`.
2. Изменения:
- для `Email` в `registerRequest/loginRequest/forgot-password` оставлен `binding:"required"`;
- добавлен helper `normalizeAndValidateEmail(raw string) (string, error)`;
- helper выполняет:
  - `trim + lowercase` через `normalizeEmail`;
  - валидацию адреса через `net/mail.ParseAddress`;
  - строгую проверку `parsed.Address == normalized`, чтобы не принимать display-name формат.
- `Register`, `Login`, `ForgotPassword` переведены на единый flow:
  - сначала bind;
  - затем `normalizeAndValidateEmail`;
  - только потом бизнес-логика.

Почему сделано именно так:

1. Это минимальный change-set без изменения API-контракта полей.
2. Нормализация и валидация теперь гарантированно работают в правильном порядке.
3. Единый helper исключает расхождение поведения между `register/login/forgot-password`.

### 4.3 Regression-тесты

1. Файл: `backend/internal/app/handlers_auth_test.go`.
2. Добавлены тесты:
- `TestNormalizeAndValidateEmailAcceptsTrimmedInput`;
- `TestNormalizeAndValidateEmailRejectsInvalidInput`;
- `TestNormalizeAndValidateEmailRejectsDisplayNameFormat`.

Почему тесты обязательны:

1. Дефект проявлялся только в связке `bind + normalize`, поэтому простого теста `normalizeEmail` недостаточно.
2. Regression-тесты фиксируют точный пользовательский сценарий и не дают вернуть дефект при будущих рефакторах.

## 5. Локальная верификация после фикса

Выполненные команды:

1. `cd backend && go test ./internal/app`
2. `cd backend && go test ./...`
3. `cd backend && go build -o bin/leonovcare-api ./cmd/server`
4. `cd backend && go build -o bin/leonovcare-worker ./cmd/worker`
5. `cd backend && go build -o bin/leonovcare-migrator ./cmd/migrator`
6. `cd frontend && npm.cmd test -- --run`
7. `cd frontend && npm.cmd run lint`
8. `cd frontend && npm.cmd run build`

Итог:

1. Backend tests: PASS.
2. Backend builds: PASS.
3. Frontend tests/build: PASS.
4. `npm run lint`: без ошибок, только существующие non-blocking warnings вне этого фикса.

## 6. Почему это изменение нельзя считать «лишним»

1. Регистрация и вход — первый критичный путь пользователя. Любая ошибка в email/nickname flow напрямую блокирует онбординг.
2. Ошибка с пробелами вокруг email выглядит как «случайный» UX-баг, но в реальности отсекает валидные логины в реальном вводе.
3. Поддержка кириллицы в nickname — продуктово обязательна для русскоязычной аудитории и уже зафиксирована в тест-плане проекта.
4. Документирование pre-fix и post-fix состояния оставлено явно, чтобы ревью видел не «косметику», а закрытие конкретных production-симптомов.

## 7. Post-deploy production re-check (после выката)

Этот раздел заполняется после деплоя на production-сервер и повторного прогона той же auth-матрицы.
