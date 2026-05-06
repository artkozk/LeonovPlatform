# Leonov Care Platform — Launch Architecture (2026-04-29)

## 1. Цель документа

Документ фиксирует фактическую техническую архитектуру платформы перед запуском на первую волну учеников (ориентир: 200 активных пользователей в когорте).

## 2. Компоненты

1. `frontend` (React + Vite):
- страницы: auth, dashboard, courses, tasks, lesson, leaderboard, billing, settings, admin.
- вход только через email+пароль (социальные OAuth-кнопки убраны из продукта).

2. `backend/cmd/server` (Go + Gin):
- REST API, auth, learning, billing, admin.
- хранение данных в PostgreSQL.
- запись заданий на проверку в Redis очередь.

3. `backend/cmd/worker` (Go):
- читает submission job из Redis.
- выполняет проверку решения через Java judge.
- обновляет verdict, XP, достижения.
- поддерживает retry до лимита `SUBMISSION_MAX_ATTEMPTS`.

4. `postgresql`:
- пользователи, профили, подписки, платежи, контент, отправки решений, XP/достижения.

5. `redis`:
- очередь `submission_jobs`.

## 3. Модель аккаунта

Пользовательская сущность `users` использует:

1. `id` — внутренний UUID (системный ключ БД).
2. `public_id` — внешний системный ID для поддержки (формат `LC-XXXXXXXXXX`).
3. `first_name`, `last_name`.
4. `nickname` — уникальный пользовательский ник.
5. `email`, `password_hash`, `role`, `xp`, `level`, `streak`.

Почему так:

1. Пользователь получает привычную модель (имя/фамилия/ник).
2. Поддержка получает стабильный публичный ID, который безопасно использовать в коммуникации.
3. Ник хранится уникально на уровне БД (case-insensitive индекс).

## 4. Поток авторизации

1. Клиент отправляет `POST /api/v1/auth/register`:
- `email`, `firstName`, `lastName`, `nickname`, `password`.
2. Backend:
- нормализует ник;
- создает пользователя с `public_id`;
- создает `user_settings`;
- назначает активный `free` план;
- возвращает JWT access/refresh.
3. Клиент хранит токены локально и запрашивает профиль `GET /api/v1/me`.

Примечание:

1. Demo-токены (verify/reset) по умолчанию не выдаются в API (`EXPOSE_DEMO_TOKENS=false`).

## 5. Поток проверки задач

1. Клиент отправляет `POST /api/v1/tasks/:taskID/submissions`.
2. Backend:
- валидирует лимиты тарифа;
- создает submission в статусе `queued`;
- кладет job в Redis.
3. Worker:
- забирает job (`BLPop`);
- переводит submission в `processing`, увеличивает `processing_attempts`;
- запускает Java judge;
- записывает итог `accepted/wrong_answer/failed`.
4. Ошибки воркера:
- запись ошибки в `run_log`;
- повторная постановка в очередь до `SUBMISSION_MAX_ATTEMPTS`;
- после лимита статус фиксируется как `failed`.

## 6. Поток оплаты (Cardlink)

1. Клиент создает checkout `POST /api/v1/subscription/checkout`.
2. Backend создает запись `payments` со статусом:
- `pending_config` — если production параметры Cardlink не готовы;
- `pending` — если конфигурация готова.
3. Cardlink webhook:
- проверяет `X-Cardlink-Token`;
- проверяет `X-Cardlink-Signature` (HMAC SHA256) при `CARDLINK_REQUIRE_SIGNATURE=true`;
- пишет `payment_events`;
- применяет смену подписки только один раз при первом `paid/succeeded`.

## 7. Контент и запускной профиль

1. Демо Java курс удален из production пути.
2. `AUTO_SEED` по умолчанию выключен.
3. Синтетическая XP/достижения очищаются миграцией launch-профиля.

Почему так:

1. На старте нельзя показывать учебный демо-контент как «боевой».
2. Убирается искусственная статистика, которая искажает реальные метрики запуска.

## 8. Режим judge sandbox

1. В конфигурации есть `JUDGE_MODE`:
- `docker` — выполнение Java в контейнере (рекомендуется для production);
- `local` — локальный процесс (для разработки).
2. Для production в PM2 конфиге задан `JUDGE_MODE=docker`.

## 9. Масштабирование на 200 учеников

1. API масштабируется горизонтально.
2. Worker масштабируется количеством процессов (PM2 apps/instances).
3. Базовый контур:
- API latency обслуживает web-запросы;
- judge нагрузка уходит в очередь/воркеры.

## 10. Ограничения текущей версии

1. OAuth login отключен для launch-профиля.
2. Плагин IntelliJ не включен в текущий production scope.

## 11. Актуализация UI-навигации и темы (2026-05-02)

1. Пользовательский экран `/settings` удалён из frontend router и больше не показывается в profile-menu.
2. На странице `/profile` оставлен только переход к подписке, потому что настройки профиля/уведомлений/редактора не нужны в текущем учебном сценарии.
3. Тема интерфейса стала строго светлой:
- frontend shell не читает `user.theme`;
- Monaco editor всегда получает `theme="light"`;
- dark CSS tokens больше не участвуют в активной сборке.
4. Backend оставляет `user_settings.theme` и `PATCH /me/settings` как compatibility layer для старых клиентов, но нормализует значение темы в `light`.
5. Так сделано, чтобы не ломать контракт `GET /me` и историческую схему БД, но убрать из продукта визуально слабую и неиспользуемую ветку dark-mode.

## 12. Full backend/plugin hardening (2026-05-06)

1. Проведен полный аудит backend + IDEA plugin по контуру:
- auth;
- submission queue;
- checker security;
- отображение lesson материалов в plugin UI;
- автотесты backend/plugin.

2. Закрытые архитектурные риски:
- `authMiddleware` переведен в fail-closed режим:
  - при `pgx.ErrNoRows` -> `401 invalid access token`;
  - при ошибке чтения user context -> `500 failed to resolve user context`;
  - запрос не проходит дальше при ошибке чтения пользователя.
- submission reconciler получил защиту от дублей payload:
  - перед `RPUSH` проверяется наличие payload в `mainQueue` и `processingQueue`;
  - при наличии payload повторная постановка пропускается.
- checker runtime усилен:
  - блокируются опасные shell separators (`&`, `|`, `>`, `<` и др.);
  - добавлен запрет volume path (`C:/...`) через `filepath.VolumeName`.

3. Улучшение plugin UX материалов:
- `LessonMaterialFormatter.buildTaskAndLessonText` теперь рендерит полный lesson-context:
  - `Теория`;
  - `Шаги урока`;
  - отдельный блок `Практическое задание` с требованиями.

4. Почему это сделано именно так:
- auth должен быть fail-closed, иначе защищенные endpoint’ы уязвимы при ошибках user lookup;
- очередь submissions должна быть устойчива к деградации воркера без бесконечного размножения одинаковых jobs;
- checker policy-команды должны иметь строгий production gate против command chaining;
- plugin должен отображать весь учебный контекст, иначе пользователь теряет pedagogical continuity внутри IDE.

5. Подробный протокол аудита:
- [docs/operations/BACKEND_PLUGIN_FULL_AUDIT_2026_05_06.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/BACKEND_PLUGIN_FULL_AUDIT_2026_05_06.md)

## 13. Full backend/plugin hardening phase 2 (2026-05-06)

1. JWT policy:
- `ParseToken` принимает только `HS256`;
- токены с иным `alg` отклоняются как невалидные.

2. Auth input normalization:
- регистрация, логин и восстановление пароля используют общий `normalizeEmail`;
- исключается разное поведение endpoint’ов при `email` с пробелами/регистром.

3. Security defaults for env:
- добавлен `applySecurityDefaults` в config layer;
- при `<=0` значениях клампятся:
  - request/source body limits;
  - rate-limit thresholds;
  - worker retry/reconcile параметры;
  - Cardlink bill TTL.

4. Почему сделано именно так:
- signing policy должен быть явно фиксирован, а не зависеть от `alg` в user-controlled заголовке;
- auth-flow должен иметь одинаковую нормализацию e-mail на всех входах;
- production не должен терять защитные лимиты из-за ошибочного env.
