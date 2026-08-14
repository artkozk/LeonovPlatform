# Production deployment: связанное рабочее пространство сооснователей

Дата: 14 августа 2026 года.

Production: `https://control.e-rd.ru/`.

## 1. Объём релиза

Развёрнуты:

- единая очередь задач, карточек вопросов, исследований, решений, разногласий и встреч;
- глобальный поиск по карточкам, вопросам, ответам и итогам;
- интерактивный граф связей на локально встроенной Cytoscape.js;
- приоритеты и направления работы;
- личный и общий режим изменения карточки;
- родительская иерархия и продвижение карточки в новый корень;
- плановое и фактическое время;
- профили активности;
- серверный Groq-ready endpoint с локальным fallback;
- исправления mobile sidebar, диалогов и горизонтального переполнения.

Кодовый коммит функционального релиза: `d004d7e`.

Операционный коммит со скриптом развёртывания и идемпотентной фиксацией задач: `afe22e2`.

Ветка: `artkozk/business-control-platform`.

## 2. Проверки до deployment

Локально успешно выполнены:

```text
node --check web/app.js
go test ./...
go vet ./...
go build ./cmd/server
```

Интеграционные тесты дополнительно выполняют production SQL фиксации задач дважды и подтверждают идемпотентность: 8 записей направления платформы, 6 завершённых задач, 1 запланированная задача и 6 доказательств.

Browser QA:

- desktop `1440x900`;
- mobile `390x844`;
- единая очередь и независимые фильтры;
- форма задачи и локальная ИИ-подсказка;
- профиль активности;
- мобильное меню, backdrop и выход из карточки;
- карточка вопросов;
- локальный граф с непустым canvas и инспектором.

## 3. Preflight production

Подтверждено:

```text
host=cqydlbhvzt
current=/opt/business-control/releases/20260814-quiet-system-40c4dbc
business-control.service=active
nginx=active
database integrity=ok
```

Первая расширенная read-only команда диагностики некорректно экранировала SQL-конкатенацию при передаче через Windows PuTTY и завершилась до изменения состояния. Для deployment и итоговой проверки вместо длинных inline SQL использованы загруженные shell/SQL файлы. Это исключило зависимость критичных операций от локального quoting.

## 4. Сборка и доставка

Linux binary собран с параметрами:

```powershell
$env:GOOS='linux'
$env:GOARCH='amd64'
$env:CGO_ENABLED='0'
go build -trimpath -ldflags '-s -w' -o bin/business-control-d004d7e-linux-amd64 ./cmd/server
```

Размер: `12091554` байта.

SHA-256:

```text
4d61e11ea4e5d7ea3936289f8dcd53e6d42fd6cd71b765cb4b4cbde041860cf8
```

Перед запуском remote SHA-256 сравнён с локальным. Скрипт `deploy-connected-work-20260814.sh` проверен `bash -n` уже на production Linux, потому что локальная Windows-среда не содержит WSL Bash.

## 5. Backup и атомарное переключение

Скрипт:

1. остановил `business-control.service`;
2. создал SQLite `.backup`;
3. проверил `PRAGMA integrity_check` копии;
4. установил бинарник в новый release directory;
5. атомарно переключил `/opt/business-control/current` через `current.next` и `mv -Tf`;
6. запустил сервис;
7. дождался внутреннего health;
8. проверил миграции, новые столбцы и целостность базы;
9. при любой ошибке после переключения был готов вернуть прежний symlink и перезапустить старый бинарник.

Первый запрос health произошёл до готовности процесса и получил connection refused. Это ожидаемая первая итерация 30-секундного retry-loop. Следующая итерация прошла, deployment завершился успешно, rollback не запускался.

Текущий release:

```text
/opt/business-control/releases/20260814-connected-work-d004d7e
```

Предыдущая быстрая точка rollback:

```text
/opt/business-control/releases/20260814-quiet-system-40c4dbc
```

Backup до миграций:

```text
/var/lib/business-control/backups/business-control-20260814-001014-pre-connected-work.db
size=258048 bytes
sha256=447e8f0d379b3a25b3251427156cde4fdb5214293676b9e9ec80867d4ccff4f2
integrity=ok
owner=business-control:business-control
mode=0640
```

## 6. Миграции

После запуска список миграций:

```text
001_init.sql
002_question_workflow.sql
003_traceable_outputs_and_meetings.sql
004_record_priority.sql
005_collaboration_hierarchy_activity.sql
```

Проверены все шесть новых столбцов `records`: `priority`, `workstream`, `edit_policy`, `parent_id`, `is_root`, `actual_minutes`.

Финальная проверка базы:

```text
integrity=ok
foreign_key_violations=0
users=2
records=9
```

## 7. Фиксация задач разработки в платформе

От имени существующего пользователя `artkozk` создана отдельная корневая цель:

```text
Развитие платформы «Контур»
workstream=platform
is_root=true
edit_policy=owner_only
```

Под ней зафиксированы шесть завершённых задач:

1. объединить рабочую очередь и глобальный поиск;
2. построить интерактивную карту связей;
3. добавить права, направления и иерархию карточек;
4. добавить активность пользователей и точность оценок;
5. оптимизировать карточки и мобильный UX;
6. добавить безопасные ИИ-подсказки структуры карточки.

Каждая задача имеет оценку, фактическое время, результат, progress `100%` и текстовое доказательство выполненного прогона.

Одна задача оставлена активной:

```text
id=d004d7e0000000000000000000000008
title=Настроить секрет GROQ_API_KEY на сервере
owner=artkozk
edit_policy=owner_only
estimate=20 минут
status=planned
```

Почему она не отмечена выполненной: пользователь передал ссылку на Groq Console, но не значение секрета. Код и локальный fallback уже работают. Секрет запрещено извлекать из чужой сессии, записывать в Git, карточку или frontend.

Итоговые числа:

```text
platform_records=8
platform_roots=1
completed_platform_tasks=6
pending_platform_tasks=1
platform_proofs=6
```

SQL идемпотентен и использует фиксированные идентификаторы с `INSERT OR IGNORE`, поэтому повторный операционный запуск не создаёт копии карточек, доказательств или событий.

## 8. Сохранность прежней работы

Контрольная существующая карточка после миграции и фиксации задач:

```text
id=ec48bd57e6e0e7997f424529a4f42bc0
title=Список вопросов до начала работы
status=in_progress
due_at=2026-08-19T21:00:00Z
estimate_minutes=360
```

ID, заголовок, статус, срок и оценка не изменились.

## 9. Production smoke

Публичные проверки:

```text
/api/health                              200, 0.242 s
/                                        200, 0.099 s
/styles.css                              200, 0.144 s
/app.js                                  200, 0.171 s
/vendor/cytoscape-3.34.1.min.js          200, 0.192 s
```

Дополнительно:

- `business-control.service`: `active`;
- nginx: `active`;
- `business-control-backup.timer`: `enabled` и `active`;
- общий `WWW-Authenticate` отсутствует;
- закрытая production CSP разрешает только `self` и нужные `data:` изображения;
- в журнале сервиса после запуска нет panic или прикладных ошибок;
- production-страница входа визуально проверена при `1440x900`.

## 10. Rollback приложения

```bash
ln -sfn /opt/business-control/releases/20260814-quiet-system-40c4dbc /opt/business-control/current.next
mv -Tf /opt/business-control/current.next /opt/business-control/current
systemctl restart business-control
curl -fsS http://127.0.0.1:8522/api/health
```

Добавочные миграции `004` и `005` можно оставить: предыдущий бинарник игнорирует новые столбцы и таблицу.

## 11. Полное восстановление базы

Использовать только при подтверждённом повреждении данных или необходимости вернуть состояние до миграций и созданных задач:

```bash
systemctl stop business-control
cp /var/lib/business-control/business-control.db /var/lib/business-control/business-control.before-connected-work-restore.db
cp /var/lib/business-control/backups/business-control-20260814-001014-pre-connected-work.db /var/lib/business-control/business-control.db
chown business-control:business-control /var/lib/business-control/business-control.db
chmod 0640 /var/lib/business-control/business-control.db
sqlite3 /var/lib/business-control/business-control.db 'PRAGMA integrity_check;'
systemctl start business-control
curl -fsS http://127.0.0.1:8522/api/health
```

Production backups всё ещё находятся на том же VPS. Они защищают от ошибки релиза и оператора, но не заменяют offsite backup.
