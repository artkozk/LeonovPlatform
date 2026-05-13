# Production Deploy Report — Canonical Progress Remediation (2026-05-13)

## 1. Цель релиза

1. Вкатить системное remediation прогресса обучения:
- canonical progress model;
- согласование lesson/quiz/tasks/dashboard/auth/streak семантики;
- без точечных костылей под один экран.

## 2. Контур деплоя

1. Сервер: `85.198.82.221`.
2. Каталог: `/opt/leonovcare-platform/current`.
3. Порты:
- API `8510`;
- Frontend `8511`.

## 3. Что произошло при первом прогоне

### Симптом

1. Деплой остановился на миграции `036_user_lesson_block_progress.sql` с ошибкой:
- `ON CONFLICT DO UPDATE command cannot affect row a second time`.

### Корневая причина

1. Backfill-часть миграции брала все `accepted` submissions.
2. Если у пользователя было несколько `accepted` по одной задаче/блоку, один `INSERT ... ON CONFLICT` получал несколько source-строк на один `(user_id, block_id)`.
3. Это приводило к множественному апдейту одного conflict key в одном statement.

### Системное исправление

1. Миграция `036` обновлена:
- добавлена дедупликация источника через `ROW_NUMBER() OVER (PARTITION BY user_id, block_id ...)`;
- в upsert попадает только `rn = 1` (последний accepted по блоку).

### Почему это важно архитектурно

1. Исправление не локальное: оно делает backfill устойчивым для любых исторических данных и любых курсов.
2. Устраняется целый класс сбоев миграций на production-базах с повторными accepted-попытками.

## 4. Повторный деплой после фикса

1. Обновленный SQL доставлен в `/opt/leonovcare-platform/current/backend/migrations/036_user_lesson_block_progress.sql`.
2. Выполнен `bash deploy/server/deploy.sh`.
3. Скрипт успешно прошел:
- DB backup;
- backend tests/build;
- migrator;
- frontend test/build;
- PM2 restart/save;
- post-deploy health checks.

## 5. Проверка после релиза

1. `curl http://127.0.0.1:8510/healthz` -> `{"service":"Leonov Care Platform","status":"ok"}`.
2. `curl http://127.0.0.1:8510/readyz` -> `{"service":"Leonov Care Platform","status":"ready"}`.
3. PM2-процессы `leonovcare-api`, `leonovcare-frontend`, `leonovcare-worker` в статусе `online`.

## 6. Риск-регистр релиза

1. Bundle-size warning во frontend build остается non-blocking и не влияет на функциональную корректность remediation.
2. Выявлен внешний процесс `interview-helper-api` в PM2 (не часть LeonovCarePlatform), находится вне scope этого релиза и должен сопровождаться отдельно.

## 7. История документа

1. v1.0 (2026-05-13): зафиксирован прод-инцидент миграции, его корневая причина, системный SQL-фикс и успешный повторный деплой.
