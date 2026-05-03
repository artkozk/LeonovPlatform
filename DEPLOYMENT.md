# Leonov Care Platform — Deployment Guide (Launch Profile)

## 1. Цель

Пошагово развернуть платформу в production-профиле без демо-контента, с безопасными webhook настройками и email-only авторизацией.

## 2. Предусловия

1. Сервер Linux с доступом по SSH.
2. Установлены:
- `git`
- `curl`
- `nodejs` + `npm`
- `golang`
- `redis-server`
- `postgresql`
- `docker` (обязательно для `JUDGE_MODE=docker`)
- `pm2`

3. Открыты порты:
- `8510/tcp` (API)
- `8511/tcp` (frontend)

## 3. Подготовка репозитория на сервере

1. Перейти в рабочий каталог:
```bash
cd /opt/leonovcare-platform/current
```
2. Обновить код:
```bash
git fetch --all
git pull
```

## 4. Конфигурация окружения

Настроить env для PM2 (через shell env или `.env` в orchestration слое), минимум:

1. База и инфраструктура:
- `DATABASE_URL`
- `REDIS_URL`

2. JWT:
- `JWT_ACCESS_SECRET`
- `JWT_REFRESH_SECRET`

3. Launch toggle:
- `AUTO_MIGRATE=true`
- `AUTO_SEED=false`
- `JUDGE_MODE=docker`
- `SUBMISSION_MAX_ATTEMPTS=30`
- `EXPOSE_DEMO_TOKENS=false`

4. Billing:
- `CARDLINK_WEBHOOK_TOKEN`
- `CARDLINK_SECRET`
- `CARDLINK_REQUIRE_SIGNATURE=true`

5. AI (опционально):
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

## 5. Сборка и тест

1. Backend:
```bash
cd /opt/leonovcare-platform/current/backend
go mod tidy
go test ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker
```

2. Frontend:
```bash
cd /opt/leonovcare-platform/current/frontend
npm ci
npm run test
export VITE_API_URL="${VITE_API_URL:-http://85.198.82.221:8510/api/v1}"
npm run build
```

## 6. Запуск через PM2

```bash
cd /opt/leonovcare-platform/current
pm2 delete leonovcare-api leonovcare-worker leonovcare-frontend || true
pm2 start deploy/server/ecosystem.config.cjs
pm2 save
pm2 status
```

## 7. Проверки после запуска

1. Health:
```bash
curl -fsS http://127.0.0.1:8510/healthz
```
2. Auth UI:
- открыть `http://85.198.82.221:8511/auth`;
- убедиться, что виден только email-flow без Google/GitHub кнопок.
3. Регистрация:
- проверить поля `Имя`, `Фамилия`, `Ник`;
- после регистрации проверить `publicId` в `Настройки`.
4. Billing webhook security:
- проверить что без валидной подписи webhook получает `401`.
5. Submission worker:
- отправить задачу, убедиться что verdict появляется и queue не зависает.

### Актуализация smoke-проверок от 2026-05-02

1. Старый пункт про проверку `publicId` в `Настройки` оставлен выше как исторический контекст предыдущего UI.
2. Сейчас `publicId` проверяется на странице `/profile`, потому что экран `/settings` удалён из пользовательского интерфейса.
3. После деплоя дополнительно проверить:
- в меню профиля нет пункта `Настройки`;
- `/profile` содержит только account summary и переход к подписке;
- интерфейс и редактор задач открываются только в светлой теме.
4. Это нужно, чтобы production-проверка совпадала с текущим продуктовым решением: настройки больше не нужны ученику, а dark-mode выключен из-за низкого визуального качества.

## 8. Миграции launch-профиля

Миграция `005_launch_readiness.sql` делает:

1. удаление демо курса `java-start`;
2. очистку синтетических XP/достижений;
3. добавление `first_name`, `last_name`, `nickname`, `public_id`;
4. добавление `processing_attempts` для retry воркера.

## 9. Rollback (минимальный)

1. Откат к предыдущему commit:
```bash
git checkout <previous_commit>
```
2. Пересборка и перезапуск PM2 по шагам 5-6.

Примечание:

Миграции данных в этой версии изменяют профиль пользователей и очищают demo-метрики. Полноценный rollback данных требует отдельного DB backup.
