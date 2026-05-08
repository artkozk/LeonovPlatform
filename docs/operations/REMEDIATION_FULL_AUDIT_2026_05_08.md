# Full Remediation Audit — 2026-05-08 (append-only)

## Scope

1. Контур без смены домена:
- web: `http://85.198.82.221:8511`
- API: `http://85.198.82.221:8510/api/v1`
2. Потоки remediation:
- `code/config`
- `deploy/ops`
- `security/deps`
- `documentation`

## Step 1

Цель:
Подтвердить базовое состояние целевых файлов до изменений.

Команды:
```bash
git status --short
Get-Content -Raw deploy/server/deploy.sh
Get-Content -Raw backend/internal/config/config.go
Get-Content -Raw backend/.env.example
Get-Content -Raw tests/smoke.sh
Get-Content -Raw frontend/src/api/types.ts
Get-Content -Raw frontend/package.json
```

Фактический результат:
1. В `deploy/server/deploy.sh` отсутствовали backup/migrator/readyz gate.
2. `AUTO_MIGRATE` в backend config имел default `true`.
3. `tests/smoke.sh` использовал legacy поле `username`.
4. Frontend имел fallback API на `http://localhost:8080/api/v1`.

Почему сделано так:
Сначала зафиксировано исходное состояние, чтобы все последующие изменения были проверяемыми и воспроизводимыми.

Rollback:
Возврат к текущему commit перед правками (`git checkout <baseline-commit>` в аварийном сценарии).

Статус:
PASS

## Step 2

Цель:
Закрыть deploy-корень проблем: backup gate + migrator + post-deploy health.

Команды:
```bash
apply_patch deploy/server/deploy.sh
```

Фактический результат:
1. Добавлены env-флаги `SKIP_DB_BACKUP`, `DB_BACKUP_DIR`, `HEALTHCHECK_URL`, `READYCHECK_URL`.
2. Добавлена обязательная сборка `leonovcare-migrator`.
3. Миграции вынесены в отдельный шаг (`./bin/leonovcare-migrator`) до PM2 restart.
4. Добавлен post-deploy gate: `healthz` и `readyz`.

Почему сделано так:
Без отдельного migrator шага и backup-гейта миграции могут идти неконтролируемо и усложняют rollback данных.

Rollback:
Вернуть прежний `deploy/server/deploy.sh` из git и повторно выполнить релиз по старому порядку.

Статус:
PASS

## Step 3

Цель:
Добавить обязательный pre-migration backup script и регулярные autobackup артефакты.

Команды:
```bash
apply_patch deploy/server/backup-db.sh
apply_patch deploy/server/systemd/leonovcare-db-backup.service
apply_patch deploy/server/systemd/leonovcare-db-backup.timer
```

Фактический результат:
1. Добавлен `deploy/server/backup-db.sh`:
- читает `DATABASE_URL` из env или `backend/.env`;
- делает `pg_dump | gzip` в `DB_BACKUP_DIR`;
- применяет retention cleanup.
2. Добавлены systemd unit/timer для регулярного backup.

Почему сделано так:
Backup перед миграциями и регулярный backup по расписанию закрывают риск потери данных и ускоряют восстановление.

Rollback:
Удалить новые файлы и убрать вызов backup в `deploy.sh`.

Статус:
PASS

## Step 4

Цель:
Синхронизировать backend runtime defaults с production-подходом.

Команды:
```bash
apply_patch backend/internal/config/config.go
apply_patch backend/internal/config/config_test.go
apply_patch backend/.env.example
```

Фактический результат:
1. `AUTO_MIGRATE` default изменён на `false`.
2. Добавлен тест `TestLoad_DefaultAutoMigrateIsDisabled`.
3. `.env.example` синхронизирован:
- `AUTO_MIGRATE=false`
- `AUTO_SEED=false`
- `IDE_CHECKER_ALLOWED_COMMANDS=`.

Почему сделано так:
Production runtime не должен выполнять миграции неявно; это должно быть отдельной операцией релиза.

Rollback:
Вернуть старые значения defaults в config и `.env.example`.

Статус:
PASS

## Step 5

Цель:
Привести smoke в соответствие с текущим auth/API-контрактом.

Команды:
```bash
apply_patch tests/smoke.sh
```

Фактический результат:
1. Регистрация переведена на `firstName/lastName/nickname/email/password`.
2. Добавлены шаги `login`, `tasks-catalog`, `submission`.
3. Smoke теперь валидирует end-to-end цепочку после deploy.

Почему сделано так:
Legacy payload с `username` больше не соответствует backend-контракту и давал ложные проверки.

Rollback:
Вернуть прежний `tests/smoke.sh` (legacy вариант) только для исторического окружения с устаревшим API.

Статус:
PASS

## Step 6

Цель:
Убрать небезопасный frontend fallback API на localhost.

Команды:
```bash
apply_patch frontend/src/api/types.ts
```

Фактический результат:
1. Удалён fallback `http://localhost:8080/api/v1`.
2. Добавлен runtime-safe fallback:
- от текущего host (`:8510/api/v1`) в браузере;
- `http://85.198.82.221:8510/api/v1` как server-side fallback.

Почему сделано так:
`localhost` fallback на проде ломает API для пользователей вне сервера и маскирует конфигурационные ошибки.

Rollback:
Вернуть прежний fallback URL в `types.ts`.

Статус:
PASS

## Step 7

Цель:
Закрыть уязвимости frontend-зависимостей и зафиксировать lockfile.

Команды:
```bash
npm.cmd install -D vite@^6.4.2 vitest@^4.1.5 @vitejs/plugin-react@^5.1.0
apply_patch frontend/package.json   # overrides.dompurify
npm.cmd install
npm.cmd audit --json
```

Фактический результат:
1. Обновлены:
- `vite` до `^6.4.2`
- `vitest` до `^4.1.5`
- `@vitejs/plugin-react` до `^5.1.0`
2. Добавлен `overrides.dompurify=^3.4.0`.
3. `npm audit` итог: `0 vulnerabilities`.
4. `frontend/package-lock.json` обновлён и зафиксирован.

Почему сделано так:
Изначально audit показывал moderate уязвимости (`vite/esbuild/dompurify`), закрытие требовало major-upgrade и override транзитивной зависимости.

Rollback:
Откат `package.json`/`package-lock.json` к предыдущему состоянию и возврат старого toolchain.

Статус:
PASS

## Step 8

Цель:
Добавить CI quality gate для backend/frontend/idea-plugin.

Команды:
```bash
apply_patch .github/workflows/ci-quality-gate.yml
```

Фактический результат:
1. Добавлен workflow на `push/pull_request` в `main`.
2. Backend gate: `go test`, `go vet`, build `api/worker/migrator`.
3. Frontend gate: `npm ci`, `test`, `lint`, `build`.
4. IDEA plugin gate: `gradle test`, `buildPlugin`.

Почему сделано так:
До изменения CI отсутствовал, поэтому regression-гейт зависел только от ручного запуска.

Rollback:
Удалить workflow-файл или временно отключить job на уровне GitHub Actions.

Статус:
PASS

## Step 9

Цель:
Подтвердить локальную регрессию после всех кодовых правок.

Команды:
```bash
cd backend
go test ./...
go vet ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker
go build -o bin/leonovcare-migrator ./cmd/migrator

cd ../frontend
npm.cmd ci
npm.cmd run test
npm.cmd run lint
npm.cmd run build
npm.cmd audit

cd ../idea-plugin
./gradlew.bat test --console=plain
./gradlew.bat buildPlugin --console=plain
```

Фактический результат:
1. Backend checks: PASS.
2. Frontend checks: PASS.
3. `npm audit`: `0 vulnerabilities`.
4. Idea plugin checks: PASS.

Почему сделано так:
Полный regression до server rollout обязателен для безопасного релиза.

Rollback:
При FAIL откатить проблемную правку и повторить полный regression-проход.

Статус:
PASS

## Step 10

Цель:
Снять preflight-снимок production до выката и сохранить rollback-артефакты.

Команды:
```bash
sshpass -p \"***\" ssh root@85.198.82.221 '<preflight snapshot script>'
```

Фактический результат:
1. Snapshot каталог: `/opt/leonovcare-platform/ops_snapshots/20260508_084148`.
2. До выката:
- `healthz=200`
- `readyz=200`
- `PM2` процессы `leonovcare-*` online.
3. Сохранены копии:
- `backend/.env`
- `deploy.sh`
- `ecosystem.config.cjs`
- nginx config dump.

Почему сделано так:
Это обеспечивает точку возврата конфигов и точный baseline перед изменениями на проде.

Rollback:
Вернуть конфиги из snapshot-каталога и повторно запустить старый release path.

Статус:
PASS

## Step 11

Цель:
Выпустить remediation-изменения в `main` перед production rollout.

Команды:
```bash
git add <remediation files>
git commit -m "Full remediation hardening: deploy flow, CI, smoke, security defaults"
git push origin main
```

Фактический результат:
1. Создан commit: `50d5e81`.
2. Push в `origin/main` выполнен успешно.

Почему сделано так:
Релизный поток по требованиям проекта фиксируется через `main` до выката на production.

Rollback:
`git revert 50d5e81` и повторный deploy с revert commit.

Статус:
PASS

## Step 12

Цель:
Доставить релизные изменения в production-каталог сервера.

Команды:
```bash
tar -czf remediation_patch_20260508_50d5e81.tgz <changed files>
scp remediation_patch_20260508_50d5e81.tgz root@85.198.82.221:/opt/leonovcare-platform/current/
ssh root@85.198.82.221 "cd /opt/leonovcare-platform/current && tar -xzf remediation_patch_20260508_50d5e81.tgz"
```

Фактический результат:
1. Путь `/opt/leonovcare-platform/current` на сервере обновлён.
2. Новые файлы (`backup-db.sh`, systemd units, workflow/docs changes) доставлены в текущий релизный каталог.

Почему сделано так:
На сервере каталог `current` не является git-repo, поэтому доставка выполнена безопасным patch-архивом.

Rollback:
Вернуть файлы из snapshot-каталога `/opt/leonovcare-platform/ops_snapshots/<ts>` или rollback-директории релиза.

Статус:
PASS

## Step 13

Цель:
Синхронизировать production `.env` с новыми правилами runtime.

Команды:
```bash
cp -a backend/.env backend/.env.pre_remediation_<ts>
bash /tmp/tmp_remote_update_env.sh
```

Фактический результат:
На production установлены и подтверждены:
1. `AUTO_MIGRATE=false`
2. `AUTO_SEED=false`
3. `IDE_CHECKER_ALLOWED_COMMANDS=`
4. `SUBMISSION_QUEUE=submission_jobs`
5. `SUBMISSION_PROCESSING_QUEUE=submission_jobs_processing`
6. `SUBMISSION_RECONCILE_INTERVAL=30s`
7. `SUBMISSION_RECONCILE_BATCH=200`
8. `SUBMISSION_MAX_ATTEMPTS=30`

Почему сделано так:
Deploy/migration flow и queue reliability зависят от этих env-инвариантов.

Rollback:
Восстановить сохранённый файл `backend/.env.pre_remediation_<ts>` и перезапустить PM2-процессы.

Статус:
PASS

## Step 14

Цель:
Установить и активировать регулярный DB backup timer на сервере.

Команды:
```bash
cp deploy/server/systemd/leonovcare-db-backup.service /etc/systemd/system/
cp deploy/server/systemd/leonovcare-db-backup.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now leonovcare-db-backup.timer
systemctl start leonovcare-db-backup.service
```

Фактический результат:
1. Таймер `leonovcare-db-backup.timer` активен.
2. Выполнен ручной старт service.
3. В каталоге `/opt/leonovcare-platform/backups/db` создан backup-файл:
- `leonovcare_db_20260508T085013Z.sql.gz`.

Почему сделано так:
Автобэкап должен быть введён до деплоя, чтобы исключить окно без защиты данных.

Rollback:
`systemctl disable --now leonovcare-db-backup.timer` и удаление unit-файлов при возврате к старой схеме.

Статус:
PASS

## Step 15

Цель:
Выполнить первый прогон нового deploy-flow на production.

Команды:
```bash
cd /opt/leonovcare-platform/current
bash deploy/server/deploy.sh
```

Фактический результат:
1. Deploy остановился на шаге migrator с ошибкой:
- `load config: DATABASE_URL is required`.
2. Причина: migrator запускается вне PM2 и не получает env из `backend/.env` автоматически.

Почему сделано так:
Этот шаг зафиксирован как фактическая production-валидация и выявил недостающий env-bridge в deploy-скрипте.

Rollback:
Release не был завершён; процессы не были перезапущены на этом шаге, откат не требовался.

Статус:
FAIL

## Step 16

Цель:
Исправить env-bridge для migrator в deploy-скрипте и повторить rollout.

Команды:
```bash
apply_patch deploy/server/deploy.sh   # safe parser ENV_FILE + export_if_missing(...)
scp deploy/server/deploy.sh root@85.198.82.221:/opt/leonovcare-platform/current/deploy/server/deploy.sh
cd /opt/leonovcare-platform/current
bash deploy/server/deploy.sh
```

Фактический результат:
1. Deploy прошёл полностью:
- pre-deploy DB backup создан (`...T085136Z.sql.gz`);
- backend tests/build PASS;
- migrator PASS (`migrations applied successfully from migrations`);
- frontend `npm ci/test/build` PASS;
- PM2 restart PASS;
- post-deploy `healthz/readyz` gate PASS.

Почему сделано так:
Без явного экспорта критичных env (`DATABASE_URL`, `JWT_*`) migrator не может корректно загрузить конфиг.

Rollback:
При повторном fail использовать pre-deploy DB backup и snapshot-конфиги из шага 10.

Статус:
PASS

## Step 17

Цель:
Провести post-release эксплуатационную валидацию.

Команды:
```bash
curl -w '%{http_code}' http://127.0.0.1:8510/healthz
curl -w '%{http_code}' http://127.0.0.1:8510/readyz
curl -w '%{http_code}' http://127.0.0.1:8511
redis-cli LLEN submission_jobs
redis-cli LLEN submission_jobs_processing
pm2 status --no-color
cd tests && bash smoke.sh
pm2 env 677 | grep AUTO_MIGRATE
```

Фактический результат:
1. `healthz=200`, `readyz=200`, frontend root `200`.
2. Redis queue lengths: `0/0`.
3. PM2: `leonovcare-api`, `leonovcare-frontend`, `leonovcare-worker x4` — `online`, restart-loop отсутствует.
4. Smoke chain (`register -> login/token -> courses -> tasks-catalog -> submission`) — PASS.
5. `pm2 env` подтверждает `AUTO_MIGRATE=false`.

Почему сделано так:
Post-deploy валидация закрывает риск “технически задеплоено, но функционально неработоспособно”.

Rollback:
При деградации вернуть предыдущий release + восстановить DB из свежего backup-файла.

Статус:
PASS

## Step 18

Цель:
Проверить rollback-готовность (артефакты + читаемость backup).

Команды:
```bash
LATEST_SNAPSHOT=$(ls -dt /opt/leonovcare-platform/ops_snapshots/* | head -n 1)
LATEST_BACKUP=$(ls -1t /opt/leonovcare-platform/backups/db/leonovcare_db_*.sql.gz | head -n 1)
test -f "$LATEST_SNAPSHOT/backend.env.predeploy"
test -f "$LATEST_SNAPSHOT/deploy.sh.predeploy"
gunzip -t "$LATEST_BACKUP"
```

Фактический результат:
1. Snapshot каталог найден: `/opt/leonovcare-platform/ops_snapshots/20260508_084148`.
2. Актуальный backup найден: `/opt/leonovcare-platform/backups/db/leonovcare_db_20260508T085136Z.sql.gz`.
3. `gunzip -t` PASS, файл не повреждён.

Почему сделано так:
Rollback-процедура должна быть не только описана, но и подтверждена доступностью артефактов восстановления.

Rollback:
Неприменимо (это проверка rollback readiness).

Статус:
PASS
