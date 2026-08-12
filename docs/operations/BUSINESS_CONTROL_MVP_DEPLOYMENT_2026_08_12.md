# Развёртывание Business Control MVP

Дата фиксации: 2026-08-12.

## 1. Цель

Развернуть независимый Business Control на сервере `85.198.82.221`, не изменяя процессы, порты, БД и домен Leonov Care.

Production профиль первого релиза:

- HTTP port: `8522`;
- бинарник: `/opt/business-control/current/business-control`;
- releases: `/opt/business-control/releases/<timestamp>`;
- SQLite: `/var/lib/business-control/business-control.db`;
- env: `/etc/business-control.env`;
- service: `business-control.service`;
- Linux user/group: `business-control`;
- разрешённые регистрации: `artkozk`, `sweetybboy`.

## 2. Почему отдельный контур

На сервере уже работает Leonov Care. Новый сервис имеет отдельный каталог, Unix-пользователя, systemd unit и порт. Деплой не выполняет restart PM2, не меняет `/opt/leonovcare-platform`, не применяет старые миграции и не редактирует существующий nginx. Это снижает риск остановить учебную платформу во время запуска бизнес-инструмента.

## 3. Подготовка артефакта

Сборка Linux amd64 выполняется локально:

```powershell
cd C:\prog\Comercial\LeonovCarePlatform\business-control
$env:CGO_ENABLED = "0"
$env:GOOS = "linux"
$env:GOARCH = "amd64"
go build -trimpath -ldflags "-s -w" -o bin\business-control-linux-amd64 ./cmd/server
```

Перед каждой сборкой обязательно:

```powershell
gofmt -w cmd\server\main.go internal\app\*.go web\assets.go
go test ./...
go vet ./...
node --check web\app.js
```

## 4. Первичная подготовка сервера

Выполняется от root один раз:

```bash
id business-control >/dev/null 2>&1 || useradd --system --home /var/lib/business-control --shell /usr/sbin/nologin business-control
install -d -o root -g root -m 0755 /opt/business-control/releases
install -d -o business-control -g business-control -m 0750 /var/lib/business-control
install -m 0640 /dev/null /etc/business-control.env
chown root:business-control /etc/business-control.env
```

Содержимое `/etc/business-control.env`:

```dotenv
BUSINESS_ADDRESS=:8522
BUSINESS_DATABASE_PATH=/var/lib/business-control/business-control.db
BUSINESS_COOKIE_SECURE=false
BUSINESS_ALLOWED_USERNAMES=artkozk,sweetybboy
```

`BUSINESS_COOKIE_SECURE=false` является текущим фактическим состоянием, потому что первый доступ идёт по HTTP и IP. После настройки HTTPS переменная обязана стать `true`, иначе cookie не использует transport protection.

## 5. Выкладка release

1. Создать новый каталог `/opt/business-control/releases/<timestamp>`.
2. Передать бинарник с правами `0755`.
3. Передать unit из `business-control/deploy/business-control.service` в `/etc/systemd/system/business-control.service`.
4. Создать или атомарно заменить symlink `/opt/business-control/current`.
5. Выполнить `systemctl daemon-reload`.
6. Выполнить `systemctl enable business-control`.
7. Выполнить `systemctl restart business-control`.

Новый release не распаковывается поверх работающей версии. Отдельный каталог оставляет быстрый rollback и не смешивает файлы разных коммитов.

## 6. Проверка после деплоя

На сервере:

```bash
systemctl is-active business-control
systemctl status business-control --no-pager
curl -fsS http://127.0.0.1:8522/api/health
curl -fsSI http://127.0.0.1:8522/
ss -ltnp | grep ':8522'
```

С рабочей машины:

```powershell
Invoke-RestMethod http://85.198.82.221:8522/api/health
```

Ожидаемый health payload: `{"status":"ok"}`.

Ручной smoke-test:

1. Зарегистрировать `artkozk` с реальной почтой и паролем.
2. В отдельном браузере зарегистрировать `sweetybboy`.
3. Создать идею и проверить, что она появилась в `Все идеи`.
4. Одним действием перевести её в `На рассмотрении`, затем в `Главные идеи`.
5. Проверить, что идентификатор и заполненные разделы не изменились.
6. Создать критерий, оценить идею и связать карточки.
7. Назначить задачу `sweetybboy` со сроком и оценкой времени.
8. Под аккаунтом исполнителя обновить прогресс.
9. Проверить запрет завершения без доказательства.
10. Добавить доказательство, завершить задачу и включить уведомление.
11. Под `artkozk` проверить непрочитанное уведомление и переход в задачу.
12. Проверить событие в истории и Timeline.

## 7. Резервное копирование

Данные важнее бинарника. Бинарник воспроизводится из Git, SQLite содержит текущий бизнес.

Online backup выполняется командой SQLite backup API, а не простым копированием открытого файла:

```bash
install -d -o business-control -g business-control -m 0750 /var/lib/business-control/backups
sqlite3 /var/lib/business-control/business-control.db ".backup '/var/lib/business-control/backups/business-control-$(date +%Y%m%d-%H%M%S).db'"
find /var/lib/business-control/backups -type f -name 'business-control-*.db' -mtime +30 -delete
```

Если системный `sqlite3` отсутствует, безопасный минимальный backup:

```bash
systemctl stop business-control
cp --preserve=mode,ownership,timestamps /var/lib/business-control/business-control.db /var/lib/business-control/backups/business-control-$(date +%Y%m%d-%H%M%S).db
systemctl start business-control
curl -fsS http://127.0.0.1:8522/api/health
```

До появления автоматического offsite backup оператор должен выгружать резервную копию с сервера. Хранение backup только на том же диске не защищает от потери VPS.

Автоматизация, которая работает сейчас после первого production деплоя:

- `/usr/local/sbin/business-control-backup` создаёт online backup через SQLite backup API;
- каждый backup проверяется `PRAGMA integrity_check` до атомарного переименования;
- `business-control-backup.timer` запускает backup ежедневно в `02:15 UTC` с небольшим случайным сдвигом;
- backups старше 30 дней удаляются только после успешного создания нового;
- каталог `/var/lib/business-control/backups` доступен только сервисному пользователю и root.

Проверка timer:

```bash
systemctl list-timers business-control-backup.timer --no-pager
systemctl start business-control-backup.service
systemctl status business-control-backup.service --no-pager
ls -lh /var/lib/business-control/backups
```

Локальная автоматизация не отменяет offsite backup: она защищает от ошибки приложения и части операционных ошибок, но не от полной потери VPS или диска.

## 8. Rollback приложения

Rollback кода не должен откатывать БД без отдельного анализа совместимости:

```bash
readlink -f /opt/business-control/current
ln -sfn /opt/business-control/releases/<previous_timestamp> /opt/business-control/current
systemctl restart business-control
curl -fsS http://127.0.0.1:8522/api/health
```

Миграции append-only. Уже применённая миграция не редактируется и не удаляется. Если новая схема несовместима со старым бинарником, rollback выполняется только после восстановления подтверждённого backup в отдельный файл и проверки целостности.

## 9. Восстановление БД

1. Остановить сервис.
2. Скопировать текущую БД и WAL/SHM в отдельный incident-каталог, ничего не удаляя.
3. Проверить backup командой `PRAGMA integrity_check;`.
4. Поместить backup как `/var/lib/business-control/business-control.db`.
5. Восстановить owner `business-control:business-control` и mode `0640`.
6. Запустить сервис и выполнить health + ручной smoke.

## 10. Наблюдаемость

Логи:

```bash
journalctl -u business-control -n 200 --no-pager
journalctl -u business-control -f
```

Проверка размера БД:

```bash
du -h /var/lib/business-control/business-control.db*
```

В MVP нет внешнего мониторинга. Минимальная эксплуатационная проверка после каждого релиза включает systemd active, health, главную страницу, регистрацию/вход и одну запись/чтение карточки.

## 11. Известные ограничения первого production профиля

1. Доступ по IP и HTTP не шифрует трафик. Для постоянного использования следующим инфраструктурным шагом нужен отдельный домен/поддомен и HTTPS, после чего `BUSINESS_COOKIE_SECURE=true`.
2. Нет password recovery. Пароль нужно хранить в менеджере паролей; административный reset будет отдельной контролируемой процедурой.
3. Регистрация ограничена двумя логинами. Это защищает временно открытый IP-порт, но не заменяет firewall/VPN/HTTPS.
4. SQLite размещена на одном сервере. Нужен регулярный offsite backup.

Эти ограничения зафиксированы явно, чтобы MVP не воспринимался как законченная массовая SaaS-платформа. Он предназначен для немедленной работы двух партнёров и безопасного накопления реальных данных во время дальнейшей разработки.

## 12. Правило обновления документа

Существующие разделы не удаляются. При изменении фактического production поведения в конец добавляется датированная актуализация: что работало раньше, что работает сейчас, причина изменения, миграционный путь и rollback.

## 13. Актуализация 2026-08-12: HTTPS и закрытие прямого порта

Исторические разделы выше описывают первый технический запуск через `http://85.198.82.221:8522`. Этот этап использовался только для проверки работоспособности отдельного процесса и firewall. Текущее production поведение после hardening:

- пользовательский адрес: `https://business-control.85-198-82-221.sslip.io/`;
- HTTP автоматически возвращает `301` на HTTPS;
- nginx принимает внешний трафик на стандартных `80/443`;
- Go-сервис слушает только `127.0.0.1:8522`;
- отдельное UFW-правило `8522/tcp` удалено для IPv4 и IPv6;
- `BUSINESS_COOKIE_SECURE=true`;
- сертификат Let's Encrypt выпущен для `business-control.85-198-82-221.sslip.io` и управляется certbot auto-renew;
- nginx-конфигурация хранится в `business-control/deploy/business-control.nginx.conf` и после установки дополняется certbot директивами сертификата и redirect.
- nginx требует общий Basic Auth команды из `/etc/nginx/business-control.htpasswd` и задаёт `X-Robots-Tag: noindex, nofollow, nosnippet`.

Почему сделано именно так:

1. Регистрация передаёт пароль, поэтому постоянное использование открытого HTTP неприемлемо даже для MVP двух партнёров.
2. Binding на localhost исключает обход nginx, TLS и его ограничений прямым обращением к `8522`.
3. Использование отдельного hostname не меняет и не перезаписывает конфигурацию домена Leonov Care.
4. `sslip.io` даёт немедленно работающий DNS для IP и позволяет начать защищённую работу до выбора постоянного бизнес-домена.
5. Allowlist логинов не доказывает, что первый регистрирующийся действительно является владельцем логина. Внешний командный пароль закрывает риск захвата `artkozk` или `sweetybboy` до создания личных аккаунтов.

Создание или замена командного доступа выполняется без записи открытого пароля в Git:

```bash
printf 'founders:%s\n' "$(openssl passwd -apr1 '<strong-team-password>')" > /etc/nginx/business-control.htpasswd
chown root:www-data /etc/nginx/business-control.htpasswd
chmod 0640 /etc/nginx/business-control.htpasswd
nginx -t && systemctl reload nginx
```

Командный пароль передаётся обоим партнёрам через закрытый канал и хранится в менеджере паролей. После ввода nginx browser challenge пользователь проходит обычную личную регистрацию по почте, логину и паролю без подтверждения почты и кодов.

Актуальные env:

```dotenv
BUSINESS_ADDRESS=127.0.0.1:8522
BUSINESS_DATABASE_PATH=/var/lib/business-control/business-control.db
BUSINESS_COOKIE_SECURE=true
BUSINESS_ALLOWED_USERNAMES=artkozk,sweetybboy
```

Проверки после HTTPS hardening:

```bash
curl -fsSI http://business-control.85-198-82-221.sslip.io/
curl -u founders:'<team-password>' -fsS https://business-control.85-198-82-221.sslip.io/api/health
ss -ltnp | grep '127.0.0.1:8522'
ufw status | grep 8522  # не должно быть разрешающего правила
certbot certificates
```

При переходе на постоянный домен создаётся новый отдельный nginx host, выпускается сертификат, проверяется HTTPS health, и только после этого старый hostname выводится из эксплуатации. БД и release-каталог от смены hostname не меняются.

## 14. Актуализация 2026-08-13: схема без общего nginx-пароля

Раздел 13 документирует предыдущую конфигурацию и не удаляется. В актуальном шаблоне `business-control/deploy/business-control.nginx.conf` больше нет `auth_basic`, `auth_basic_user_file` и зависимости от `/etc/nginx/business-control.htpasswd`.

Проверка актуальной схемы:

```bash
nginx -t
! grep -Eq 'auth_basic|business-control\.htpasswd' /etc/nginx/sites-available/business-control
curl -fsSI https://control.e-rd.ru/ | grep -v '^WWW-Authenticate:'
curl -fsS https://control.e-rd.ru/api/health
```

Пользовательская авторизация выполняется только приложением. Это убирает второй экран входа, но не отменяет HTTPS, `Secure`/HttpOnly cookie и username allowlist. До регистрации второго партнёра приоритетным следующим усилением является одноразовое приглашение, привязанное к конкретному логину.

Новый hostname устанавливается только на целевом сервере. Старый production host не переименовывается до успешного переноса базы, чтобы оставался rollback. Пошаговое состояние миграции и правило удаления старого экземпляра находятся в `BUSINESS_CONTROL_SERVER_MIGRATION_2026_08_13.md`.

## 15. Актуализация 2026-08-13: окончательный production hostname

Указанное в промежуточной подготовке имя `business-control.178-234-15-210.sslip.io` не развёртывалось. Окончательный пользовательский адрес — `https://control.e-rd.ru/`, DNS A-record которого указывает на `159.194.231.150`.

Развёртывание выполняется с новой пустой SQLite-базой по прямому решению владельца проекта. Старые тестовые пользователь и карточка не являются бизнес-данными и не переносятся. Оба партнёра проходят быструю регистрацию заново.
