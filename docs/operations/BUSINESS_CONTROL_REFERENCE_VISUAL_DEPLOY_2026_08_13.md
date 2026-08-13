# Production-развёртывание визуальной системы по продуктовому референсу

Дата: 13 августа 2026 года.

Документ фиксирует фактическое production-развёртывание визуального релиза «Контур бизнеса». Он дополняет предыдущие deployment-отчёты, не удаляет старые release-каталоги и сохраняет возможность быстрого возврата.

## Версия и окружение

- Production-домен: `control.e-rd.ru`.
- Production-сервер домена: `159.194.231.150`.
- Git-ветка: `artkozk/business-control-platform`.
- Коммит приложения: `408d56a` (`feat(business-control): apply premium visual system`).
- Новый release-каталог: `/opt/business-control/releases/20260813-reference-visual-408d56a`.
- Предыдущий release-каталог: `/opt/business-control/releases/20260813-interface-redesign-27ba365`.
- Production-БД: `/var/lib/business-control/business-control.db`.
- Резервная копия deployment: `/var/lib/business-control/backups/business-control-20260813-202415.db`.

## Состав релиза

В release включены:

1. светлая боковая навигация;
2. холодная нейтральная палитра;
3. единый фиолетовый акцент главных действий;
4. обновлённый экран входа;
5. обновлённые состояния обзора, списков и быстрых действий;
6. карточка с табличной колонкой фактов справа;
7. полноэкранная мобильная карточка;
8. блокировка прокрутки фоновой страницы при открытом диалоге;
9. обновлённое оформление цепочки вопросов и ответов.

API, схема SQLite и production-данные не изменялись.

## Локальные проверки перед deployment

Перед сборкой выполнены:

```text
node --check web/app.js
go test ./...
go vet ./...
git diff --check
```

Результаты:

- `business-control/internal/app` — успешно;
- `business-control/web` — успешно;
- `go vet` — без замечаний;
- JavaScript syntax check — без ошибок;
- проверка пробелов — без ошибок.

Браузерный QA выполнен после полного перезапуска локального Go-сервера, потому что web-ресурсы встроены в бинарник.

На desktop проверены обзор, навигация, карточка задачи, вкладки и правая колонка фактов. На viewport `390 × 844` проверены обзор, полноэкранный диалог, карточка вопросов и поле ответа. Горизонтальное переполнение не обнаружено.

## Предварительная production-проверка

До переключения release подтверждено:

1. `/opt/business-control/current` указывал на `/opt/business-control/releases/20260813-interface-redesign-27ba365`;
2. `business-control.service` находился в состоянии `active`;
3. `nginx` находился в состоянии `active`;
4. локальный health endpoint возвращал `{"status":"ok"}`;
5. `PRAGMA integrity_check` возвращал `ok`;
6. на файловой системе оставалось около `5.7 GB` свободного места.

## Сборка и передача

Бинарник собран для production:

```text
GOOS=linux
GOARCH=amd64
CGO_ENABLED=0
go build -trimpath -ldflags="-s -w" -o business-control-408d56a ./cmd/server
```

Размер бинарника: `10,584,226` байт.

SHA-256:

```text
e54c5fbf7305e4bfb5709ddf9cee115c67629422e887c09261eea06cfcf7a88f
```

Хэш проверен повторно на production-сервере до установки. Бинарник установлен с владельцем `business-control:business-control` и правами `0755`.

## Переключение release

Перед переключением вручную запущен `business-control-backup.service`. Затем:

1. создан новый release-каталог;
2. бинарник установлен в release-каталог;
3. временная символическая ссылка `current.next` направлена на новый release;
4. `current.next` атомарно переименована в `current`;
5. `business-control.service` перезапущен;
6. внутренний health check повторялся до успешного ответа;
7. при любой ошибке скрипт был готов вернуть ссылку на предыдущий release и перезапустить сервис.

Первый health-запрос пришёлся на момент старта процесса и не подключился. Следующий запрос вернул `{"status":"ok"}`. Rollback не потребовался.

Один предварительный запуск deployment-команды был остановлен локальной интерпретацией PowerShell до изменения production-ссылки. После этого текущий release был повторно проверен, Linux-команда передана буквальным многострочным аргументом, а deployment выполнен штатно. Этот факт зафиксирован, чтобы история операции не выглядела безошибочной задним числом.

## Итоговая production-проверка

После переключения подтверждено:

1. `/opt/business-control/current` указывает на `/opt/business-control/releases/20260813-reference-visual-408d56a`;
2. `business-control.service` находится в состоянии `active`;
3. `nginx` находится в состоянии `active`;
4. `nginx -t` завершён успешно;
5. внутренний `http://127.0.0.1:8522/api/health` возвращает HTTP `200` и `{"status":"ok"}`;
6. публичный `https://control.e-rd.ru/api/health` возвращает HTTP `200` и `{"status":"ok"}`;
7. главная страница возвращает HTTP `200`;
8. production CSS возвращает HTTP `200`;
9. production CSS содержит `--accent: #5b46e8`;
10. production CSS содержит светлую сетку приложения шириной `238px`;
11. production CSS содержит блокировку фонового scroll при открытом `dialog`;
12. production CSS содержит полноэкранное правило `100dvh` для мобильной карточки;
13. `PRAGMA integrity_check` возвращает `ok`;
14. журнал `business-control.service` не содержит warning и error за период deployment;
15. production-страница входа открыта и визуально проверена в браузере.

Общий nginx-пароль перед страницей не появился. Пользователь сразу видит штатный вход и регистрацию приложения.

## Сохранность рабочей карточки

После deployment проверена существующая карточка:

- ID: `ec48bd57e6e0e7997f424529a4f42bc0`;
- подтип: `question_set`;
- название: `Список вопросов до начала работы`;
- статус: `in_progress`;
- срок: `2026-08-19T21:00:00Z`;
- оценка времени: `360` минут.

Данные совпадают с состоянием до визуального релиза. Миграция и восстановление БД не выполнялись.

## Rollback приложения

Для возврата предыдущего интерфейса без изменения БД:

```bash
ln -sfn /opt/business-control/releases/20260813-interface-redesign-27ba365 /opt/business-control/current.next
mv -Tf /opt/business-control/current.next /opt/business-control/current
systemctl restart business-control
curl -fsS http://127.0.0.1:8522/api/health
curl -fsS https://control.e-rd.ru/api/health
sqlite3 /var/lib/business-control/business-control.db 'PRAGMA integrity_check;'
```

Rollback БД для этого релиза не требуется, поскольку схема и данные не менялись.

## Восстановление БД при отдельной аварии

Резервная копия deployment предназначена только для отдельного повреждения данных, не для обычного возврата CSS. Перед восстановлением необходимо остановить сервис и сохранить текущий файл БД отдельно.

```bash
systemctl stop business-control
cp /var/lib/business-control/business-control.db /var/lib/business-control/business-control.before-restore.db
cp /var/lib/business-control/backups/business-control-20260813-202415.db /var/lib/business-control/business-control.db
chown business-control:business-control /var/lib/business-control/business-control.db
systemctl start business-control
sqlite3 /var/lib/business-control/business-control.db 'PRAGMA integrity_check;'
curl -fsS http://127.0.0.1:8522/api/health
```

Такое восстановление не требуется для текущего deployment и не выполнялось.
