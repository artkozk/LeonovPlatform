# Развёртывание workflow-comfort BizFlow

Дата: 14 августа 2026 года.

## Жёсткое ограничение размещения

Единственный разрешённый production-хост BizFlow: `159.194.231.150`. Домен: `control.e-rd.ru`. Приложение, SQLite, вложения, секреты и резервные копии запрещено переносить на другие серверы без нового явного решения основателей.

Адрес `85.198.82.221`, ранее присутствовавший в локальной инструкции репозитория, не используется для BizFlow. Это не техническая рекомендация, а требование конфиденциальности пользователя и потому имеет приоритет для этой программы.

## Состав релиза

- миграция `business-control/internal/app/migrations/007_workflow_comfort.sql`;
- Go binary с встроенным frontend;
- seed выполненных задач разработки `seed-workflow-comfort-release-20260814.sql`;
- зашифрованный backup script и systemd timer;
- server-side Gemini configuration;
- product, architecture и operations документация.

## Секреты

Gemini key записывается только в `/etc/business-control.env` строкой `GEMINI_API_KEY=...`. Файл должен принадлежать root и иметь режим `0600`. Ключ нельзя помещать в:

- исходный код;
- JavaScript и HTML;
- SQLite;
- SQL seed;
- shell-скрипт релиза;
- Git commit;
- JSON export;
- backup payload.

Ключ шифрования backup создаётся на основном сервере командой `openssl rand -hex 32` и хранится в `/etc/business-control-backup.key` с режимом `0600`.

## Сборка

Из `business-control`:

```powershell
$env:GOOS='linux'
$env:GOARCH='amd64'
$env:CGO_ENABLED='0'
go build -trimpath -ldflags='-s -w' -o business-control-workflow-comfort ./cmd/server
```

Перед отправкой выполняются:

```powershell
go test ./...
go vet ./...
node --check web/app.js
```

## Предварительная проверка SQL

Production DB не используется как первая среда выполнения seed. Сначала создаётся локальная копия совместимой БД, применяется миграция 007 и seed, затем проверяются:

```sql
PRAGMA integrity_check;
SELECT COUNT(*) FROM pragma_foreign_key_check;
SELECT COUNT(*) FROM records WHERE id LIKE 'f814%' AND status='completed';
```

Ожидается `ok`, `0`, `8`.

## Порядок развёртывания

1. Binary, migration, seed, backup script и units загружаются во временные файлы основного сервера.
2. В `/etc/business-control.env` устанавливается Gemini key и `BUSINESS_UPLOAD_PATH`.
3. Запускается `deploy-workflow-comfort-release-20260814.sh`.
4. Скрипт останавливает сервис и создаёт согласованный pre-release SQLite backup.
5. Миграция и seed применяются транзакционно.
6. Binary устанавливается в новый неизменяемый release-каталог.
7. Symlink `current` атомарно переключается.
8. Проверяются health, SQLite, foreign keys, число release-задач и каталог вложений.
9. Для `artkozk` создаётся краткоживущая временная сессия только для server-side AI health; после запроса сессия удаляется.
10. AI health обязан вернуть `provider=gemini`, `providerAvailable=true`, `source=gemini`.
11. Запускается encrypted backup, затем проверяется наличие итогового `.tar.gz.enc` и активный timer.

## Автоматический rollback

При ошибке после изменения БД скрипт:

1. останавливает сервис;
2. удаляет временную smoke-сессию;
3. восстанавливает SQLite из pre-release backup;
4. возвращает symlink предыдущего релиза;
5. запускает предыдущий binary.

Вложения не перезаписываются миграцией. До завершения smoke пользовательский трафик не должен добавлять новые файлы, поэтому отдельный rollback каталога не нужен.

## Проверка домена

После успешного локального smoke проверяются:

```text
https://control.e-rd.ru/api/health
https://control.e-rd.ru/
```

Страница должна отдавать новый JS/CSS, nginx не должен запрашивать общий логин `founders`, а штатная сессия пользователя должна сохраняться.

## Восстановление зашифрованного backup

Восстановление выполняется только на основном сервере в закрытом root-каталоге:

```bash
install -d -o root -g root -m 0700 /root/bizflow-restore
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
  -in /var/backups/business-control/business-control-TIMESTAMP.tar.gz.enc \
  -out /root/bizflow-restore/payload.tar.gz \
  -pass file:/etc/business-control-backup.key
tar -C /root/bizflow-restore -xzf /root/bizflow-restore/payload.tar.gz
cd /root/bizflow-restore
sha256sum -c MANIFEST.sha256
sqlite3 business-control.db 'PRAGMA integrity_check;'
```

Только после `ok` сервис останавливается, текущие DB/WAL/SHM сохраняются отдельно, проверенный DB устанавливается в `/var/lib/business-control/business-control.db`, а каталог `uploads` возвращается в `/var/lib/business-control/uploads`. Владелец обоих объектов — `business-control:business-control`.

## Ротация ключей

Gemini key был передан в рабочем диалоге и после успешного подключения должен быть перевыпущен в консоли провайдера. Новый ключ заменяется только в `/etc/business-control.env`, затем выполняется `systemctl restart business-control` и повторяется `/api/ai/health`.

Backup key не следует ротировать без расшифровки или отдельного сохранения старого ключа: старые архивы иначе станут невосстановимыми. При ротации старый ключ хранится root-only до истечения retention всех созданных им копий.

## Фактический результат

Этот раздел заполняется после production-развёртывания без удаления описанного выше плана: release path, предыдущая версия, SHA-256 pre-release backup, результат AI health, encrypted backup и доменные smoke-проверки фиксируются как доказательство операции.

## Уточнение AI preflight перед развёртыванием

Фактический preflight с `159.194.231.150` вернул `400 FAILED_PRECONDITION: User location is not supported for the API use`. Ключ распознан endpoint Google, но Gemini Developer API применяет региональное ограничение по IP вызывающего сервера. Россия отсутствует в официальном списке доступных стран.

План выше требовал `providerAvailable=true`. После полученного факта правило скорректировано без удаления исторического плана: deployment принимает `provider=gemini`, `configured=true` и один из двух честных результатов. `source=gemini` завершает задачу внешнего AI; `source=heuristic` оставляет её заблокированной и подтверждает, что недоступность Google не блокирует продукт. Обход через второй сервер запрещён требованием конфиденциальности. Официальная альтернатива Google Enterprise/Vertex требует отдельной OAuth-конфигурации, которой в переданных данных нет.
