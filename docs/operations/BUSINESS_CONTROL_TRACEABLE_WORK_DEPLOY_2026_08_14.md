# Production-развёртывание причинных цепочек, встреч и quiet-system UI

Дата пользовательского релиза: 14 августа 2026 года, Europe/Moscow.

Сервер хранит время в UTC, поэтому backup-файлы, созданные ночью 14 августа по Москве, имеют префикс `20260813`.

## 1. Объём релиза

В production развёрнуты:

- результаты совместных вопросов: критерии, ограничения, правила, выводы, задачи, идеи, исследования и цели;
- неизменяемое точное происхождение результата от конкретного вопроса и снимка совместного решения;
- отдельные карточки встреч;
- быстрые производные карточки из встреч и других рабочих объектов;
- постоянный раздел `Правила и критерии`;
- предметные поля для разных типов карточек;
- исправление перехода с главной страницы в нефильтрованный список задач;
- переработанный главный экран и редактор шаблонов;
- графитово-минеральная визуальная система с хвойным акцентом;
- встроенные локальные шрифты Inter без CDN;
- mobile-исправление одноколоночной карточки.

Подробное продуктовое поведение находится в `docs/product/BUSINESS_CONTROL_TRACEABLE_WORK_AND_QUIET_SYSTEM_UI_2026_08_14.md`. Схема данных описана в `docs/architecture/BUSINESS_CONTROL_TRACEABLE_OUTCOMES_DATA_MODEL_2026_08_14.md`.

## 2. Коммиты и артефакты

Основной функциональный коммит:

```text
153f8f3 feat(business-control): trace decisions into working outcomes
```

Внешний визуальный smoke после первого production-развёртывания обнаружил, что экран входа всё ещё использовал лиловую поверхность предыдущего релиза. Исправление оформлено отдельным коммитом:

```text
40c4dbc fix(business-control): align authentication visual system
```

Оба коммита отправлены в `origin/artkozk/business-control-platform`.

Финальный Linux-артефакт:

```text
GOOS=linux
GOARCH=amd64
CGO_ENABLED=0
size=10981538 bytes
sha256=8682701f0d62f66b423c9aae9c03f4b0906931ef50920b27f86ee3b6b34f4d26
```

Хэш локальной сборки совпал с хэшем `/opt/business-control/current/business-control` после установки.

## 3. Состояние до миграции

Перед первым переключением подтверждено:

- активный release: `/opt/business-control/releases/20260813-reference-visual-408d56a`;
- `business-control.service`: `active`;
- `nginx`: `active`;
- внутренний health: `{"status":"ok"}`;
- размер SQLite: `233472` байта;
- `PRAGMA integrity_check`: `ok`;
- пользователей: `2`;
- карточек: `1`;
- контрольная карточка `ec48bd57e6e0e7997f424529a4f42bc0` существует.

Свободное место на корневом разделе составляло около `5.7 GB`.

## 4. Копия до миграции

Штатный `business-control-backup.service` создал:

```text
/var/lib/business-control/backups/business-control-20260813-223128.db
```

Размер копии: `233472` байта. SHA-256:

```text
94bc94d27e43b5973529448600cb8ca9c30dc750ed64a34b1c129a9546a5c0ba
```

`PRAGMA integrity_check` копии вернул `ok`. Этот файл является точкой восстановления до применения миграции `003`.

## 5. Миграция

При первом запуске нового бинарника применена append-only миграция:

```text
003_traceable_outputs_and_meetings.sql
```

Она добавила `records.record_kind`, индекс и таблицу `record_derivations` с внешними ключами `ON DELETE RESTRICT` и снимком `source_excerpt`.

Финальный список миграций:

```text
001_init.sql
002_question_workflow.sql
003_traceable_outputs_and_meetings.sql
```

## 6. Фактический автоматический rollback

Первый deployment-скрипт после успешного старта приложения ошибочно проверял столбец `schema_migrations.name`. Реальная схема использует `schema_migrations.version`. Проверка завершилась ошибкой, и shell trap автоматически:

1. вернул `/opt/business-control/current` на `/opt/business-control/releases/20260813-reference-visual-408d56a`;
2. перезапустил прежний бинарник;
3. сохранил рабочую доступность сервиса.

Миграция к этому моменту уже была применена. База не восстанавливалась, поскольку изменения схемы добавочные, а прежний бинарник игнорирует новые столбец и таблицу. После rollback подтверждены `active` и `{"status":"ok"}`.

После исправления диагностики с `name` на `version` release повторно переключён. Эта ошибка относится только к post-deploy проверке, а не к приложению или данным.

## 7. Промежуточный функциональный release

Основная функция была успешно запущена из:

```text
/opt/business-control/releases/20260814-traceable-work-153f8f3
```

После миграции проверены:

- сервис и публичный health;
- наличие `record_kind`;
- наличие `record_derivations`;
- две учётные записи;
- одна прежняя карточка;
- отсутствие общего Basic Auth;
- HTTP `200` у CSS, JavaScript и встроенных шрифтов.

После этого создана копия:

```text
/var/lib/business-control/backups/business-control-20260813-223524.db
```

Размер: `258048` байт, mode `0640`, владелец `business-control:business-control`, `PRAGMA integrity_check`: `ok`.

## 8. Визуальный контроль и финальное исправление

Production-страница открыта в управляемом браузере при viewport `1440x900`. Проверка подтвердила загрузку Inter, новый акцент `#1f6657` и отсутствие горизонтального переполнения, но выявила старую лиловую поверхность в левой части формы входа.

После коммита `40c4dbc` страница входа использует:

- внешний фон `#e6e8e4`;
- графитовую бренд-панель `#26312d`;
- хвойный акцент `#1f6657`;
- локальный Inter;
- отсутствие декоративного лилового контура.

Перед финальным переключением создана проверенная копия:

```text
/var/lib/business-control/backups/business-control-20260813-223657.db
```

## 9. Финальный release

Текущий production-каталог:

```text
/opt/business-control/releases/20260814-quiet-system-40c4dbc
```

Предыдущая точка быстрого rollback:

```text
/opt/business-control/releases/20260814-traceable-work-153f8f3
```

Финальная проверка:

- `business-control.service`: `active`;
- `nginx`: `active`, `nginx -t` успешен;
- внутренний health: HTTP `200`, `{"status":"ok"}`;
- `https://control.e-rd.ru/api/health`: HTTP `200`, `{"status":"ok"}`;
- корневая страница: HTTP `200`;
- CSS и JavaScript: HTTP `200`;
- `Inter-Regular.woff2` и `Inter-SemiBold.woff2`: HTTP `200`;
- production CSS содержит хвойный акцент и графитовую оболочку;
- production JavaScript содержит `renderPrinciples` и создание результатов вопроса;
- заголовок `WWW-Authenticate` отсутствует;
- `PRAGMA integrity_check`: `ok`;
- backup timer: `active` и `enabled`;
- в журнале сервиса нет panic или прикладной ошибки запуска.

Последняя копия после финального deployment:

```text
/var/lib/business-control/backups/business-control-20260813-223812.db
size=258048 bytes
integrity=ok
```

## 10. Сохранность рабочей карточки

После всех переключений контрольная карточка содержит:

```text
id=ec48bd57e6e0e7997f424529a4f42bc0
type=document
subtype=question_set
title=Список вопросов до начала работы
status=in_progress
due_at=2026-08-19T21:00:00Z
estimate_minutes=360
```

Количество пользователей осталось `2`, количество карточек — `1`. Production-smoke не создавал тестовые аккаунты или записи и не изменял рабочее содержимое.

## 11. Rollback приложения

Для возврата только исправления экрана входа:

```bash
ln -sfn /opt/business-control/releases/20260814-traceable-work-153f8f3 /opt/business-control/current.next
mv -Tf /opt/business-control/current.next /opt/business-control/current
systemctl restart business-control
curl -fsS http://127.0.0.1:8522/api/health
```

Для возврата всего функционального релиза:

```bash
ln -sfn /opt/business-control/releases/20260813-reference-visual-408d56a /opt/business-control/current.next
mv -Tf /opt/business-control/current.next /opt/business-control/current
systemctl restart business-control
curl -fsS http://127.0.0.1:8522/api/health
sqlite3 /var/lib/business-control/business-control.db 'PRAGMA integrity_check;'
```

При обычном rollback бинарника миграцию `003` удалять нельзя и восстанавливать БД не требуется: совместимость со старым бинарником фактически проверена автоматическим rollback.

## 12. Восстановление БД при отдельной аварии

Копия `business-control-20260813-223128.db` используется только для подтверждённого повреждения данных или необходимости полного возврата к состоянию до миграции. Перед восстановлением текущую БД необходимо сохранить отдельно.

```bash
systemctl stop business-control
cp /var/lib/business-control/business-control.db /var/lib/business-control/business-control.before-restore.db
cp /var/lib/business-control/backups/business-control-20260813-223128.db /var/lib/business-control/business-control.db
chown business-control:business-control /var/lib/business-control/business-control.db
chmod 0640 /var/lib/business-control/business-control.db
sqlite3 /var/lib/business-control/business-control.db 'PRAGMA integrity_check;'
systemctl start business-control
curl -fsS http://127.0.0.1:8522/api/health
```

Копии по-прежнему находятся на том же VPS. Они защищают от ошибок приложения и оператора, но не заменяют offsite backup.
