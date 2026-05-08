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

## 6. Remediation ограничения и безопасные дефолты (append-only, 2026-05-08)

### 6.1 Зафиксированные контурные ограничения

1. В этом релизе домен `leonovcare.ru` не переключается.
2. Эксплуатируемый внешний контур сохраняется по IP/портам:
- `http://85.198.82.221:8511` (web)
- `http://85.198.82.221:8510/api/v1` (API)
3. Это ограничение введено осознанно, чтобы не смешивать remediation-релиз с DNS/ingress-изменениями и уменьшить blast radius.

### 6.2 Политика миграций и запусков

1. Runtime дефолт `AUTO_MIGRATE=false` считается обязательным security/ops-инвариантом.
2. Миграции выполняются только явным deploy-шагом через `leonovcare-migrator`.
3. Почему так:
- исключается скрытое изменение схемы при рестарте API/worker;
- миграции переходят в контролируемую процедуру с backup-гейтом и rollback-артефактом.

### 6.3 DB backup gate

1. Перед каждым deploy запускается pre-migration backup (`pg_dump` + `gzip`).
2. Добавлены явные env-флаги:
- `SKIP_DB_BACKUP` (default `false`);
- `DB_BACKUP_DIR` (явный путь хранения backup-файлов).
3. Почему так:
- backup становится обязательной частью change-control;
- отключение backup возможно только явным флагом, что делает риск наблюдаемым в аудите.

### 6.4 IDE checker allowlist default

1. `IDE_CHECKER_ALLOWED_COMMANDS` по умолчанию пустой.
2. Строгий allowlist включается только явной production-настройкой.
3. Почему так:
- убирается конфликт между безопасным встроенным policy и случайным жёстким fallback;
- security-гейт остаётся управляемым и воспроизводимым через env.
