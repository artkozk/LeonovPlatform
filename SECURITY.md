# Leonov Care Platform — Security Notes (Launch)

## 1. Цель

Зафиксировать текущую модель защиты перед production-запуском и список обязательных контролей на окружении.

## 2. Основные риски и контрмеры

### 2.1 Auth и токены

Риск:

1. Компрометация access/refresh секретов.
2. Выдача технических токенов в публичный API.

Контрмеры:

1. `JWT_ACCESS_SECRET` и `JWT_REFRESH_SECRET` должны храниться только в runtime env.
2. `EXPOSE_DEMO_TOKENS=false` в production.
3. Refresh token хранится в БД и валидируется по сроку действия.

### 2.2 OAuth поверхность

Риск:

1. Небезопасная интеграция внешнего OAuth-провайдера в launch-фазе.

Контрмеры:

1. OAuth-вход отключен в launch-профиле (email-only auth).
2. OAuth маршруты удалены из router.

### 2.3 Webhook платежей

Риск:

1. Подмена webhook запроса.
2. Повторное применение успешного события.

Контрмеры:

1. Проверка `X-Cardlink-Token`.
2. Проверка `X-Cardlink-Signature` (HMAC SHA256) при `CARDLINK_REQUIRE_SIGNATURE=true`.
3. Идемпотентное применение paid/succeeded статуса.

### 2.4 Выполнение пользовательского кода

Риск:

1. Выполнение недоверенного Java-кода на хосте.

Контрмеры:

1. Production режим `JUDGE_MODE=docker`.
2. Контейнер запускается с ограничениями:
- `--network none`
- `--memory 256m`
- `--cpus 1.0`
- `--pids-limit 128`
- `--read-only`

### 2.5 Очередь проверки

Риск:

1. Потеря/зависание задач при исключениях воркера.

Контрмеры:

1. `processing_attempts` в `submissions`.
2. retry до `SUBMISSION_MAX_ATTEMPTS`.
3. перевод в `failed` после превышения лимита с записью ошибки в `run_log`.

## 3. Операционные требования

1. Ротация секретов:
- JWT secrets;
- Cardlink webhook token;
- Cardlink secret;
- DB пароль.

2. Логи:
- хранить server/worker логи;
- мониторить рост ошибок в `run_log`.

3. Бэкапы:
- регулярный backup PostgreSQL перед релизом и перед миграциями.

## 4. Статус по критичным пунктам

1. Demo-token leakage: закрыт (`EXPOSE_DEMO_TOKENS=false`).
2. OAuth surface: закрыт (routes removed).
3. Webhook signature: включена проверка.
4. Queue retries: реализованы.
5. Java demo content/statistics: удалены launch migration.

## 5. Открытые задачи

1. Добавить rate-limits на auth endpoints на уровне reverse proxy/API gateway.
2. Добавить централизованный аудит security-событий (отдельная таблица/канал).
3. Добавить интеграционные security тесты для webhook signatures и auth brute-force.
