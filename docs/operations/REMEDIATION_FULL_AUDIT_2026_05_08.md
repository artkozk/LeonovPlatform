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
