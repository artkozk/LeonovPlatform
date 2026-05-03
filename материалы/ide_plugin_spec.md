# IDE Plugin Spec

## Назначение
IDE-плагин проверяет проектные шаги, где обычного stdout или SQL-запроса недостаточно. Он подтверждает файлы, структуру, команды, Git-состояние, API, Docker, CI/CD и деплойные артефакты.

## Проверяемые области
- Создание файлов: required_files, forbidden files, структура директорий.
- Структура проекта: `src`, `app`, `tests`, `migrations`, `deploy`.
- pytest: запуск `python -m pytest`, таймаут, код выхода, выборочные hidden cases.
- SQL fixtures: schema SQL, seed SQL, временная база, сравнение результата.
- FastAPI endpoints: импорт `app.main:app`, HTTP-методы, статус-коды, JSON subset.
- Dockerfile: инструкции `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`, отсутствие небезопасного `latest` там, где нужен pinning.
- docker compose: сервисы `app` и `db`, `depends_on`, `healthcheck`, переменные окружения.
- Git commands: clean worktree, ветки, коммиты, история, отсутствие конфликтных маркеров.
- CI/CD workflow: GitHub Actions, GitLab CI, jobs `lint`, `test`, `build`.
- README: запуск, проверка, структура, переменные окружения.
- `.env.example`: ключи без реальных секретов.
- Миграции: наличие каталога и хотя бы одного файла миграции.
- Деплойные файлы: nginx, compose, deploy script.

## Почему проверка вынесена в плагин
Проектные задания требуют состояния файловой системы и Git. Эти данные нельзя надёжно проверить только текстовым ответом студента. Плагин снижает нагрузку наставников и оставляет AI-review для качества решений, а не для базовой механики.

## Схема результата
Плагин возвращает JSON: `status`, `failed_checks`, `stdout`, `stderr`, `files_snapshot`, `git_snapshot`, `duration_ms`. Платформа сохраняет этот результат в попытке сдачи.
