# IDE plugin spec v16

Плагин проверяет конкретные артефакты, а не общие обещания. Проверка считается полезной только если студент может локально воспроизвести тот же результат командой из задания.

## Базовый контракт
- каждый `ide_plugin` checker имеет уникальный `scenario_id`;
- `required_files` описывает минимальный набор файлов, без которых навык нельзя считать отработанным;
- `commands` запускаются из корня проекта и должны завершаться ожидаемым кодом;
- `runtime_checks` используются для Docker/Deploy/final gates, где простого наличия файла недостаточно;
- `gate_checks` обязательны для финального проекта и содержат pass/fail критерии.

## Git labs
- проверяй `git status --porcelain`, текущую ветку, количество коммитов и отсутствие untracked-файлов;
- для конфликтов проверяй отсутствие `<<<<<<<`, `=======`, `>>>>>>>`;
- для rebase и non-fast-forward сценариев требуй объяснение риска force-команд;
- для восстановления требуй `git reflog --oneline` и отдельный recovery commit;
- для stash/cherry-pick проверяй, что изменения применены в нужной ветке, а рабочее дерево чистое.

## SQL и SQLite
- `sql_query` задачи обязаны иметь `schema_sql`, `seed_sql`, public tests и hidden tests;
- sqlite3-задачи через Python проверяются `python_pytest` на временной базе;
- hidden tests должны ловить отсутствие `ORDER BY`, SQL injection, неверный `NULL`, ошибочный JOIN и rollback без эффекта.

## FastAPI
- `http_api` проверки запускают `app.main:app` и проверяют status code, JSON subset и negative cases;
- healthcheck возвращает объект вида `{ "status": "ok" }`, не массив;
- для auth обязательны 401/403 negative cases;
- для CRUD обязательны 201, 204, 404 и 422 там, где это соответствует endpoint.

## Docker, CI/CD, Deploy
- `docker compose config` проверяет синтаксис, но не считается достаточным;
- production-сценарии должны запускать `docker compose up -d --build`;
- тесты должны запускаться внутри контейнера через `docker compose exec -T app python -m pytest`;
- `.env.example` должен содержать `APP_ENV`, `DATABASE_URL`, `SECRET_KEY` без реальных секретов;
- deploy script должен поддерживать `--dry-run`, `--rollback --dry-run` и проверку статуса после релиза;
- CI должен разделять jobs `lint`, `test`, `build`, `deploy`, чтобы падение было диагностируемым.

## Final gates
- каждый gate требует документ, кодовый артефакт, команду проверки и pass/fail критерии;
- ТЗ проверяется через user stories, ограничения, acceptance criteria и out-of-scope;
- DB gate проверяет ERD, индексы, связи и миграции с rollback-планом;
- API contract проверяет OpenAPI, статусы, ошибки и примеры request/response;
- Auth gate проверяет JWT, refresh, protected routes и negative cases;
- Deploy gate проверяет домен, SSL, env, healthcheck, dry-run и rollback;
- Final defense проверяет demo script, trade-offs и ответы на вопросы по SQL/API/DevOps/AI.
