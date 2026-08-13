# Production-развёртывание рабочего фокуса и быстрых карточек

Дата: 13 августа 2026 года.

Этот отчёт фиксирует фактически выполненное развёртывание коммита `96e5d12` на production-сервере платформы. Он дополняет предыдущие отчёты и не изменяет историю прошлых релизов.

## Целевой контур

- Публичный адрес: `https://control.e-rd.ru/`.
- DNS A-запись во время развёртывания: `159.194.231.150`.
- Сервис: `business-control.service`.
- Локальный адрес приложения за nginx: `127.0.0.1:8522`.
- Рабочая БД: `/var/lib/business-control/business-control.db`.
- Каталог релизов: `/opt/business-control/releases`.
- Активный симлинк: `/opt/business-control/current`.

DNS проверен непосредственно перед загрузкой бинарника. Это было необходимо, потому что в истории проекта упоминалось несколько серверов; обновлять узел, на который домен больше не указывает, нельзя.

## Исходное состояние

До переключения:

- активный релиз: `/opt/business-control/releases/20260813-question-workflow-8c71f26`;
- `business-control.service`: `active`;
- `business-control-backup.timer`: `active`;
- локальный `/api/health`: `{"status":"ok"}`;
- `PRAGMA integrity_check` рабочей БД: `ok`.

## Резервная копия до релиза

Перед загрузкой нового бинарника вручную запущен `business-control-backup.service`.

- Файл: `/var/lib/business-control/backups/business-control-20260813-103853.db`.
- Статус systemd unit: `SUCCESS`.
- Отдельная проверка `PRAGMA integrity_check`: `ok`.

Резервная копия создаётся штатным скриптом сервера, а не копированием живого SQLite-файла. Скрипт завершает работу только после проверки полученной БД.

## Сборка и контроль файла

Linux-бинарник собран из каталога `business-control` с параметрами:

```powershell
$env:GOOS = "linux"
$env:GOARCH = "amd64"
$env:CGO_ENABLED = "0"
go build -trimpath -ldflags="-s -w" -o business-control-96e5d12 ./cmd/server
```

SHA-256 загруженного файла:

```text
fa5cc1d3395fd04839ca3a882ca68d1c594b27531b798486a5b202a234a03dbb
```

Контрольная сумма проверена на сервере до установки. Это исключает переключение на неполный или повреждённый файл после передачи.

## Переключение релиза

Новый бинарник установлен в:

```text
/opt/business-control/releases/20260813-focus-ui-96e5d12/business-control
```

Далее выполнены следующие шаги:

1. Создан временный симлинк `current.next` на новый каталог.
2. Временный симлинк атомарно перемещён в `/opt/business-control/current`.
3. На ошибку после переключения установлен trap, возвращающий предыдущий симлинк и перезапускающий сервис.
4. `business-control.service` перезапущен.
5. Локальный health проверялся до пяти раз с секундным интервалом, чтобы не считать нормальное время старта ошибкой.
6. После успешного health подтверждено, что сервис `active`, а симлинк указывает именно на новый релиз.

Первый health-запрос попал в короткое окно перезапуска и получил отказ соединения. Следующая попытка успешно вернула `{"status":"ok"}`; rollback не запускался. Такое поведение ожидаемо для текущего однопроцессного развёртывания и ограничивает перерыв временем старта Go-процесса.

## Проверки после переключения

Подтверждено:

- `https://control.e-rd.ru/api/health` возвращает HTTP `200` и `{"status":"ok"}`;
- nginx обслуживает production как `nginx/1.28.3 (Ubuntu)`;
- production `styles.css` содержит `.project-brief` и `.focus-panel`;
- production `app.js` содержит `detailCache` и отдельный путь `/relations`;
- `nginx -t` завершён успешно;
- `business-control.service` и `business-control-backup.timer` активны;
- `PRAGMA integrity_check` рабочей БД вернул `ok`;
- таблицы `records`, `question_items`, `question_answers`, `question_decisions` присутствуют;
- `journalctl -u business-control.service --since=-5min -p warning` не содержит записей.

## Резервная копия после релиза

После проверки приложения повторно запущен штатный backup unit.

- Файл: `/var/lib/business-control/backups/business-control-20260813-104055.db`.
- Статус systemd unit: `SUCCESS`.
- `PRAGMA integrity_check`: `ok`.

Эта копия фиксирует рабочую БД после запуска нового бинарника и дополняет дорелизную точку восстановления.

## Rollback

Проверенная предыдущая версия не удалялась:

```text
/opt/business-control/releases/20260813-question-workflow-8c71f26
```

Ручной откат при необходимости:

```bash
ln -sfn /opt/business-control/releases/20260813-question-workflow-8c71f26 /opt/business-control/current.rollback
mv -Tf /opt/business-control/current.rollback /opt/business-control/current
systemctl restart business-control.service
curl -fsS http://127.0.0.1:8522/api/health
```

Откат БД для этого релиза обычно не требуется: схема данных не менялась. Если причиной отката станет повреждение данных, сначала сервис останавливается, затем используется одна из проверенных резервных копий по штатной процедуре восстановления из предыдущего deployment runbook.
