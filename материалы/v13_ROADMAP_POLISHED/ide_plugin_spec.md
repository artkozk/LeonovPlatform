# IDE plugin spec

Плагин проверяет проекты локально и отдаёт платформе структурированный результат.

## Проверяемые области
- создание файлов и структура проекта;
- pytest и отчёт по падениям;
- SQL fixtures и временные базы SQLite;
- FastAPI endpoints через TestClient;
- Dockerfile, docker compose, healthcheck, networks, volumes;
- Git commands: branches, commits, clean worktree, merge, rebase, tags, reflog;
- CI/CD workflow для GitHub Actions и GitLab CI;
- README, `.env.example`, миграции, деплойные файлы.

## Контракт ответа
Плагин возвращает `passed`, `failed_checks`, `stdout`, `stderr`, `artifacts`, `duration_ms`. Проверки должны быть детерминированными и не требовать платных API.
