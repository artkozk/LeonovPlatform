# Развёртывание production-quality релиза BizFlow

Дата: 14 августа 2026 года.

## Разрешённая инфраструктура

Единственный разрешённый production-хост: `159.194.231.150`. Домен: `control.e-rd.ru`. Приложение, SQLite, вложения, секреты и резервные копии нельзя отправлять на другие серверы.

## Процедура

1. Локально выполняются JavaScript syntax-check, Go tests, `go vet` и проверка diff.
2. Linux amd64 binary собирается с `CGO_ENABLED=0`, `-trimpath` и удалёнными debug symbols.
3. Binary и `deploy-production-quality-release-20260814.sh` загружаются во временные файлы основного сервера.
4. Скрипт создаёт согласованный SQLite backup и проверяет integrity и foreign keys.
5. В root-only env без чтения или вывода ключа устанавливаются Vertex Express endpoint и модель `gemini-2.5-flash`.
6. Binary устанавливается в новый неизменяемый release-каталог, symlink `current` переключается атомарно.
7. При любой ошибке после переключения symlink возвращается на предыдущий релиз и сервис запускается снова.
8. После health-check создаётся краткоживущая сессия `artkozk` для AI health. Сессия удаляется в успешном и аварийном сценарии.
9. Запускается штатная зашифрованная резервная копия с пробной расшифровкой.
10. После скрипта отдельно проверяются HTTPS-домен, версии JS/CSS, systemd, nginx, backup timer и журнал ошибок.

## Почему старый deploy script не используется повторно

Workflow-comfort script включает миграцию и seed задач предыдущего релиза. Повторный запуск был бы формально идемпотентным только частично и смешал бы новый UI-релиз со старой операцией данных. Новый script не меняет бизнес-записи и не применяет seed. Он создаёт backup, переключает binary и выполняет диагностическую сессию.

## AI preflight

Проверка с разрешённого production-сервера выполнена для двух официальных Vertex endpoint: Express и project/location. Оба вернули `403 PERMISSION_DENIED`, причина `BILLING_DISABLED` для project number `940127702170`. Ключ распознан и связан с проектом; проблема не относится к региону, DNS или формату endpoint.

Релиз допускает `source=heuristic` только при явном сообщении о выключенном биллинге. Это позволяет пользоваться системой без задержек и не выдаёт локальные правила за ответ Gemini.

## Фактический результат

Этот раздел дополняется после развёртывания. Исторический план выше не удаляется: release path, предыдущий release, SHA-256 backup и binary, AI health, состояние сервисов и доменные smoke-проверки будут добавлены отдельным подразделом.

## Фактический production-результат

Развёртывание выполнено только на `159.194.231.150`.

Активный release:

```text
/opt/business-control/releases/20260814-production-quality-384b395
```

Предыдущий release для атомарного rollback:

```text
/opt/business-control/releases/20260814-rich-reader-c45f878
```

Согласованный pre-release SQLite backup:

```text
/var/lib/business-control/backups/business-control-20260814-203543-pre-production-quality.db
SHA-256: b97eea19f17260f4b0366b6a090acf02502f95c7af4fe266ee74cd11cf31cea7
```

Развёрнутый binary:

```text
SHA-256: 567b2cfe0f19b40050d3a420c0ececb103d600e3feb7d72bb3d965cf2de694a9
```

Проверки после переключения:

```text
business-control=active
nginx=active
business-control-backup.timer=enabled/active
NRestarts=0
ExecMainStatus=0
SQLite integrity=ok
foreign key violations=0
GET https://control.e-rd.ru/api/health -> {"status":"ok"}
CSS -> /styles.css?v=20260814-production-quality
JS -> /app.js?v=20260814-production-quality
systemd warnings since deployment -> none
```

Первый локальный health-запрос в retry-loop попал в короткий промежуток между `systemctl start` и открытием порта. Следующий запрос прошёл, deployment script продолжил проверки и завершился с кодом `0`. Это ожидаемое поведение retry-loop, а не сбой или rollback.

AI health после установки server env:

```text
configured=true
provider=gemini
model=gemini-2.5-flash
providerAvailable=false
source=heuristic
message=В Google Cloud не включён биллинг; локальный анализ активен
```

Таким образом, endpoint, key binding и project определены корректно, но внешний ответ блокируется настройкой биллинга Google Cloud. Секрет в отчёт, Git, SQLite и backup не добавлялся.

Созданный после завершения production-задачи зашифрованный backup:

```text
/var/backups/business-control/business-control-20260814-203906.tar.gz.enc
SHA-256: f8cdaf7e400cf9fdf3b43c894fac04cd736d50dfecf8860e0b01760d21987798
owner=root:root
mode=0600
bytes=70064
plaintext files in encrypted backup directory=0
```

Задача `Довести BizFlow до устойчивого production-качества` (`8f21a9c127d67e41989f72652bafc31e`) закрыта штатным API от имени `artkozk`: семь пунктов чек-листа завершены с отдельными отчётами, добавлено Markdown-доказательство, итоговый статус `completed`, прогресс `100%`, партнёру создано уведомление. После этих изменений backup запущен повторно, поэтому последний архив включает окончательное состояние задачи и истории.
