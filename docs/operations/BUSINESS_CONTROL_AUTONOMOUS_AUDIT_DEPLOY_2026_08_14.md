# Production-развёртывание автономного аудита «Контура»

## Результат

14 августа 2026 года релиз автономного продуктового аудита развёрнут на `https://control.e-rd.ru`.

- активный релиз: `/opt/business-control/releases/20260814-autonomous-audit-c425d66`;
- предыдущий релиз: `/opt/business-control/releases/20260814-connected-work-d004d7e`;
- продуктовый коммит: `c425d66`;
- релизные и проверочные коммиты: `ea979ff`, `f0639e3`, `05d7b7e`, `c427a4f`;
- SHA-256 Linux-бинарника: `b4f84a0613e7d08e3636d51f9feb990f035fa8456b746d41381e56eb7f9cb9ae`;
- домен: `https://control.e-rd.ru`;
- локальный backend: `127.0.0.1:8522`.

## Зачем потребовался отдельный релиз

Изменения затронули не только CSS. Они изменили рабочую навигацию, способ фильтрации, видимость иерархии, загрузку истории, мобильную геометрию Cytoscape и пустые состояния. Поэтому выпуск проведён как атомарная замена Go-бинарника с резервной копией базы, проверкой SQL seed на клоне БД и возможностью автоматического возврата к предыдущему релизу.

## Подготовка

Локально выполнены:

```text
node --check web/app.js
go test ./...
go vet ./...
```

Linux-бинарник собран с `GOOS=linux`, `GOARCH=amd64`, `CGO_ENABLED=0`, `-trimpath` и `-ldflags="-s -w"`. Полученный размер — `12132514` байт.

Перед production-развёртыванием SQL seed был выполнен на временной копии действующей базы скриптом `validate-autonomous-audit-20260814.sh`. Проверка подтвердила:

- `audit_tasks=3`;
- `audit_proofs=3`;
- `platform_goal_progress=52`;
- `integrity_check=ok`;
- `foreign_key_violations=0`;
- исходная рабочая карточка не изменена;
- задача настройки `GROQ_API_KEY` остаётся запланированной и личной.

Первый защищённый запуск release-скрипта остановился до изменения production на проверке `test -x`: загруженный бинарник имел права `0644`. Сервис, symlink и БД не менялись. После установки `0755` скрипт был запущен повторно. Этот случай подтверждает, что предохранитель прекращает выпуск до остановки production, если staged artifact не готов.

## Backup до переключения

- путь: `/var/lib/business-control/backups/business-control-20260814-005121-pre-autonomous-audit.db`;
- размер: `303104` байта;
- SHA-256: `e459e83351f7c071636cf03adcbfdb595df3445030573fe70147669f76cec308`;
- `PRAGMA integrity_check`: `ok`.

Копия создана встроенной командой SQLite `.backup` после остановки сервиса. Права установлены `business-control:business-control`, режим `0640`.

## Переключение

Скрипт `deploy-autonomous-audit-20260814.sh` выполнил:

1. проверку staged binary, SQL и действующей БД;
2. остановку `business-control`;
3. backup до релиза;
4. установку бинарника в неизменяемый release-каталог;
5. транзакционный seed задач с `sqlite3 -bail`;
6. атомарную замену symlink `current.next -> current`;
7. запуск systemd unit;
8. ожидание health-check;
9. проверку миграций, целостности, внешних ключей, задач и доказательств.

При ошибке после смены symlink trap возвращает `current` на предыдущий release и перезапускает сервис.

## Задачи внутри платформы

От имени `artkozk` под корнем `Развитие платформы «Контур»` созданы и завершены:

1. `Провести автономный аудит интерфейса без списка замечаний` — план `240 мин`, факт `255 мин`.
2. `Упростить единую очередь и показать иерархию без графа` — план `150 мин`, факт `165 мин`.
3. `Доработать карточки, историю и мобильную карту` — план `210 мин`, факт `225 мин`.

Каждая задача имеет текстовое доказательство, результат, статус `completed`, направление `platform` и родителя `d004d7e0000000000000000000000001`. Первая задача личная, остальные общие. Прогресс корневой цели разработки обновлён с `35%` до `52%`.

## Проверка данных

После запуска `verify-autonomous-audit-20260814.sql` получено:

```text
users=2
records=12
migrations=001_init.sql,002_question_workflow.sql,003_traceable_outputs_and_meetings.sql,004_record_priority.sql,005_collaboration_hierarchy_activity.sql
audit_tasks=3
audit_proofs=3
platform_goal_progress=52
original_record=ec48bd57e6e0e7997f424529a4f42bc0|Список вопросов до начала работы|in_progress|2026-08-19T21:00:00Z|normal|360
pending_groq_task=d004d7e0000000000000000000000008|Настроить секрет GROQ_API_KEY на сервере|planned|owner_only
ok
foreign_key_violations=0
```

Проверка исходной карточки важна, потому что работа над интерфейсом не должна изменять пользовательские бизнес-данные. Сохранены ID, название, статус, срок, приоритет и оценка времени.

## Проверка сервисов и домена

- `business-control.service`: `active`;
- `nginx.service`: `active`;
- `business-control-backup.timer`: `active`;
- `http://127.0.0.1:8522/api/health`: `{"status":"ok"}`;
- `https://control.e-rd.ru/api/health`: `{"status":"ok"}`;
- production `app.js` содержит marker `sortWorkHierarchy`;
- systemd journal показывает чистый запуск нового процесса на `127.0.0.1:8522`;
- хеш установленного бинарника совпадает с локальным.

## Backup после проверки

- путь: `/var/lib/business-control/backups/business-control-20260814-005238-post-autonomous-audit.db`;
- размер: `307200` байт;
- SHA-256: `004616de28d127ee35fc567da92f4fc7b5a9f659daf90f922c461bbc5d09bbb8`;
- `PRAGMA integrity_check`: `ok`;
- нарушений внешних ключей: `0`.

Копия создана только после проверки публичного домена, статического marker, сервисов и SQL-инвариантов. Она является предпочтительной точкой восстановления нового релиза.

## Rollback

Для возврата только приложения:

```bash
ln -sfn /opt/business-control/releases/20260814-connected-work-d004d7e /opt/business-control/current.next
mv -Tf /opt/business-control/current.next /opt/business-control/current
systemctl restart business-control
curl -fsS http://127.0.0.1:8522/api/health
```

Seed добавляет только новые задачи, доказательства и события и обновляет прогресс корневой цели. Старый бинарник понимает эти записи, поэтому обычный rollback приложения не требует отката БД. Если нужен полный возврат данных до релиза, сервис сначала останавливается, текущая БД сохраняется отдельно, затем восстанавливается `business-control-20260814-005121-pre-autonomous-audit.db`, устанавливаются владелец и режим, выполняются `integrity_check` и `foreign_key_check`, после чего сервис запускается.

## Связанные документы

- `docs/product/BUSINESS_CONTROL_AUTONOMOUS_PRODUCT_AUDIT_PROMPT_2026_08_14.md` — постоянная инструкция самостоятельного аудита.
- `docs/product/BUSINESS_CONTROL_AUTONOMOUS_USABILITY_AUDIT_RELEASE_2026_08_14.md` — найденные проблемы и реализованные решения.
- `docs/operations/BUSINESS_CONTROL_CONNECTED_WORK_DEPLOY_2026_08_14.md` — предыдущий production-релиз и исходная точка rollback.
