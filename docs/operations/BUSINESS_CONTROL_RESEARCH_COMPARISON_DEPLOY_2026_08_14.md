# Production-развёртывание исследований и карты BizFlow, 14 августа 2026

## Статус документа

Этот отчёт создаётся до переключения production и дополняется фактическими путями release, backup, контрольными суммами и результатами smoke после успешного развёртывания. Предварительное описание не удаляется: оно фиксирует запланированный безопасный порядок и причины каждой проверки.

## Состав релиза

- Миграция `006_research_comparison.sql`.
- API вариантов и общих полей исследования.
- Режим чтения карточки с явным редактированием.
- Безопасный локальный Markdown через Marked и DOMPurify.
- Поиск по вариантам и показ вариантов на карте.
- Расширенные функции карты, настройки и mobile-адаптация.
- Исправление скачка диалога создания.
- Идемпотентный перенос существующего исследования `Выбор сервера`.
- Завершённая platform-задача релиза от `artkozk`.

## Предрелизный порядок

1. Выполнить `gofmt`, `node --check`, `go test`, `go vet` и `git diff --check`.
2. Проверить desktop и mobile сценарии в реальном браузере, включая повторное открытие в режиме чтения.
3. Собрать Linux-бинарник и вычислить SHA-256.
4. Загрузить бинарник, migration, seed и два release-скрипта во временные пути `/tmp`.
5. Выполнить `bash -n` скриптов на Linux-сервере.
6. Запустить `validate-research-comparison-release-20260814.sh` на SQLite-копии production. Скрипт применяет migration и seed дважды, проверяя идемпотентность, целостность и внешние ключи.
7. Только после dry-run выполнить deploy-скрипт.

## Безопасность развёртывания

Deploy сначала останавливает сервис и делает консистентный SQLite `.backup`. Миграция применяется транзакционно и регистрируется в `schema_migrations`, затем запускается seed. Бинарник устанавливается в новый неизменяемый release-каталог, а `current` переключается атомарно.

При любой ошибке после изменения БД trap останавливает сервис, восстанавливает pre-release backup, возвращает предыдущий release и запускает сервис. Это важно: откат только бинарника после добавления таблиц и seed не является полным операционным откатом.

## Запланированный smoke

После переключения обязательны:

```text
systemctl is-active business-control
GET http://127.0.0.1:8522/api/health
GET https://control.e-rd.ru/api/health
PRAGMA integrity_check
pragma_foreign_key_check
наличие 006_research_comparison.sql в schema_migrations
наличие выполненной platform-задачи и proof
наличие Begget и Timeweb Cloud в найденном исследовании
наличие пяти общих полей сравнения
HTTP 200 для app.js, styles.css, Marked и DOMPurify
отсутствие новых ошибок в journalctl
```

## Фактический результат

Будет дописан после выполнения deployment. До появления здесь release path, backup path, SHA-256 и smoke-результатов этот документ нельзя считать подтверждением production-выпуска.

## Откат

Точные команды будут дополнены фактическими путями. Общий порядок: остановить сервис, вернуть предыдущий symlink, удалить SQLite WAL/SHM, восстановить pre-release backup через временный файл, вернуть владельца `business-control`, запустить сервис и повторить health/integrity/foreign-key/journal проверки. Если после релиза уже появились новые пользовательские данные, перед восстановлением старого backup необходимо отдельно сохранить или перенести эти записи.

## Дополнение после фактического развёртывания

Развёртывание успешно завершено 14 августа 2026 года. Предварительный порядок выше выполнен без сокращений.

- Продуктовый коммит: `df1c2be feat(business-control): add research comparison workspace`.
- Ветка: `artkozk/business-control-platform`.
- Release: `/opt/business-control/releases/20260814-research-comparison-df1c2be`.
- Предыдущий release: `/opt/business-control/releases/20260814-ai-visual-46b3237`.
- Backup: `/var/lib/business-control/backups/business-control-20260814-132209-pre-research-comparison.db`.
- SHA-256 backup: `83b64f6fe93331139f5654f24eda312321542a389206e4ef0260a4c9e61adafb`.
- SHA-256 Linux-бинарника: `bd396fb7e066c4f23a556294241dd332461c0fe83e3ca8b379c143fee410f185`.
- Production-домен: `https://control.e-rd.ru`.

Локально перед коммитом подтверждены:

```text
node --check web/app.js                         ok
go test ./...                                  ok
go vet ./...                                   ok
git diff --check                               ok
Linux amd64 build                              ok
```

Browser QA выполнен на desktop `1280×720` и mobile `390×844`. Проверены создание исследования, отложенная AI-подсказка без сдвига формы, создание поля и варианта, Markdown-заголовок, список, цитата, оценка и значение поля, повторное открытие без видимых textarea, явная кнопка редактирования, поиск `Timeweb`, отсутствие горизонтального переполнения и отрисовка карты тремя canvas-слоями. После исправления весов шрифта и возврата стандартной чувствительности колеса новые console warning/error отсутствовали.

Загруженные во временный каталог Linux-скрипты прошли `bash -n`. Dry-run на SQLite-копии production применил migration и seed дважды. Оба запуска вернули:

```text
release_task=1
research_fields=5
research_options=2
integrity_check=ok
foreign_key_violations=0
```

Равные количества после второго запуска подтверждают идемпотентность: повторное развёртывание не создаёт дополнительные поля, варианты, задачи, proof или activity с release-ID.

При старте нового systemd-процесса первая попытка health-check попала в короткое окно до открытия порта и вернула `connection refused`. Следующая попытка предусмотренного 30-секундного retry-цикла прошла, deploy завершился с exit code `0`, rollback не запускался.

Независимая production-проверка после переключения:

```text
current release                                  20260814-research-comparison-df1c2be
systemd service                                  active
local /api/health                                {"status":"ok"}
https://control.e-rd.ru/                         200, 6970 bytes
https://control.e-rd.ru/api/health               200, 16 bytes
https://control.e-rd.ru/app.js                    200, 254352 bytes
https://control.e-rd.ru/styles.css                200, 141075 bytes
Marked asset                                     200, 43821 bytes
DOMPurify asset                                  200, 29474 bytes
renderResearchComparison marker                  1
renderMarkdown marker                            1
renderGraphSettings marker                       1
SQLite integrity_check                           ok
SQLite foreign key violations                    0
006_research_comparison.sql migration             1
release platform task                            completed, 100%
release task proofs                              1
journal errors за 10 минут                       0
```

Production-карточка `4939b10980e10ace81a941701ac93c06` с названием `Выбор сервера` получила поля `Цена в месяц`, `Конфигурация`, `Локация`, `Надёжность`, `Удобство управления` и варианты `Begget`, `Timeweb Cloud`. Обе оценки оставлены `0`, потому что система не должна придумывать исследовательский вывод за основателя.

## Фактический откат

Откат использовать только при подтверждённой регрессии. Перед ним необходимо сохранить записи, созданные после `13:22:09 UTC`, иначе восстановление backup их удалит.

```bash
systemctl stop business-control
ln -sfn /opt/business-control/releases/20260814-ai-visual-46b3237 \
  /opt/business-control/current.next
mv -Tf /opt/business-control/current.next /opt/business-control/current
rm -f /var/lib/business-control/business-control.db-wal \
  /var/lib/business-control/business-control.db-shm
install -o business-control -g business-control -m 0640 \
  /var/lib/business-control/backups/business-control-20260814-132209-pre-research-comparison.db \
  /var/lib/business-control/business-control.db.restore
mv -f /var/lib/business-control/business-control.db.restore \
  /var/lib/business-control/business-control.db
systemctl start business-control
curl -fsS http://127.0.0.1:8522/api/health
sqlite3 /var/lib/business-control/business-control.db 'PRAGMA integrity_check;'
sqlite3 /var/lib/business-control/business-control.db \
  'SELECT COUNT(*) FROM pragma_foreign_key_check;'
journalctl -u business-control --since=-10min -p err --no-pager
```

После отката доменный health-check и доступность frontend-assets проверяются отдельно через HTTPS. Старый бинарник не должен запускаться на post-release БД без подтверждения обратной совместимости; именно поэтому штатный откат возвращает и бинарник, и snapshot базы одновременно.

## Hotfix горячих клавиш Markdown

После замечания о неработающих `Ctrl+B` и `Ctrl+K` выпущен отдельный hotfix без изменения схемы данных.

- Коммит: `c229888 feat(business-control): add markdown keyboard shortcuts`.
- Release: `/opt/business-control/releases/20260814-markdown-shortcuts-c229888`.
- Предыдущий release: `/opt/business-control/releases/20260814-research-comparison-df1c2be`.
- Backup: `/var/lib/business-control/backups/business-control-20260814-140126-pre-research-comparison.db`.
- SHA-256 backup: `a8ffa2ef489156785357d0a2f39867ba52d8b9f910cddc8866bb71ca3581aea4`.
- SHA-256 Linux-бинарника: `1aa186851ff05eb80d3dea389dec0ca23314b6c80345603b7aa080228d5ea40a`.

В реальном браузере проверены `Ctrl+B`, `Ctrl+I`, `Ctrl+K`, `Ctrl+Backtick`, `Ctrl+Alt+2`, `Ctrl+Shift+7`, `Ctrl+Shift+8` и `Ctrl+Shift+.`. Для `Ctrl+K` отдельно подтверждено, что фокус остаётся в textarea, выделение преобразуется в `[текст](https://)`, диапазон выделения перемещается на адрес, а глобальный поиск не получает фокус. Панель содержит девять кнопок, на desktop имеет одинаковые `clientWidth=294` и `scrollWidth=294`, поэтому не обрезается. Новых browser warning/error после прогона нет.

Локальные проверки:

```text
node --check web/app.js    ok
go test ./...             ok
go vet ./...              ok
git diff --check          ok
Linux amd64 build         ok
```

Dry-run применил seed дважды на копии актуальной production-БД. Оба запуска вернули `shortcut_task=1`, `integrity_check=ok` и `foreign_key_violations=0`. До hotfix пользователь уже добавил ещё два варианта исследования: общее число активных вариантов `Выбора сервера` стало равно четырём. После production-переключения оно осталось равно четырём, что подтверждает сохранность параллельно введённых данных.

Финальный smoke:

```text
current release                 20260814-markdown-shortcuts-c229888
systemd service                 active
local /api/health               {"status":"ok"}
public /api/health              200
markdownShortcutAction marker   1
KeyK link marker                1
SQLite integrity_check          ok
foreign key violations          0
shortcut platform task          completed, 100%
shortcut task proofs            1
active research options         4
journal errors за 10 минут      0
```

Для отката именно hotfix используются предыдущий release `/opt/business-control/releases/20260814-research-comparison-df1c2be` и backup `/var/lib/business-control/backups/business-control-20260814-140126-pre-research-comparison.db`. Предупреждение о сохранении новых post-release записей перед восстановлением snapshot остаётся обязательным.
