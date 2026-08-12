# Business Control MVP: отчёт первого production деплоя

Дата: 2026-08-12.

## 1. Результат

Business Control MVP развёрнут как независимый production-сервис на `85.198.82.221`.

Публичный адрес первого контура: `http://85.198.82.221:8522/`.

Health endpoint: `http://85.198.82.221:8522/api/health`.

Git:

- branch: `artkozk/business-control-platform`;
- initial application commit: `8e0d6cf` (`Add business control platform MVP`);
- remote: `origin` / `https://github.com/artkozk/LeonovPlatform.git`.

## 2. Фактическая production конфигурация

- release: `/opt/business-control/releases/20260812-8e0d6cf`;
- current symlink: `/opt/business-control/current`;
- systemd unit: `business-control.service`;
- процесс: `/opt/business-control/current/business-control`;
- listener: `*:8522`;
- database: `/var/lib/business-control/business-control.db`;
- env: `/etc/business-control.env`;
- Unix user/group: `business-control`;
- allowed usernames: `artkozk,sweetybboy`;
- cookie secure mode: `false`, потому что текущий первый адрес использует HTTP.

Существующие сервисы Leonov Care не перезапускались. Каталоги `/opt/leonovcare-platform`, существующие PM2 процессы, порты `8510/8511` и nginx не изменялись.

## 3. Сетевое изменение

До деплоя UFW имел default policy `deny incoming`, а порт `8522` не был разрешён. Поэтому приложение отвечало локально на сервере, но внешний health-check завершался timeout.

Добавлено одно адресное правило:

```text
8522/tcp ALLOW Anywhere # Business Control MVP
8522/tcp (v6) ALLOW Anywhere (v6) # Business Control MVP
```

После добавления правила внешний health и главная страница отвечают успешно. Другие firewall правила не удалялись и не менялись.

## 4. Проверки до деплоя

Выполнено:

```text
go test ./...       PASS
go vet ./...        PASS
node --check web/app.js PASS
git diff --check    PASS
Linux amd64 build without CGO PASS
```

Интеграционный тест подтвердил:

1. Регистрацию и долговременную cookie session двух пользователей.
2. Создание единственной карточки идеи в `inbox`.
3. Переход той же карточки в `review` без изменения ID.
4. Универсальные разделы идеи.
5. Оценку по критерию и связь между карточками.
6. Назначение задачи партнёру.
7. Запрет завершения задачи без доказательства.
8. Добавление текстового proof.
9. Завершение, прогресс 100% и уведомление партнёра.
10. Историю причины и значений `before/after`.
11. Изменение логина пользователя.

Браузерный smoke-test подтвердил desktop и viewport `390x844`, отсутствие горизонтального переполнения, работу встроенного окна причины и отсутствие console errors.

## 5. Проверки после деплоя

Подтверждено:

- `systemctl is-active business-control` -> `active`;
- service enabled в `multi-user.target`;
- локальный `GET /api/health` -> `{"status":"ok"}`;
- внешний `GET /api/health` -> `{"status":"ok"}`;
- внешний `HEAD /` -> `HTTP/1.1 200 OK`;
- CSP, `X-Content-Type-Options`, `X-Frame-Options` и `Referrer-Policy` присутствуют;
- SQLite, WAL и SHM созданы с owner `business-control:business-control` и mode `0640`;
- current symlink указывает на ожидаемый release.

## 6. Backup после деплоя

В production устанавливаются:

- `/usr/local/sbin/business-control-backup`;
- `business-control-backup.service`;
- `business-control-backup.timer`.

Backup создаётся SQLite backup API, проверяется через `PRAGMA integrity_check`, хранится 30 дней и не публикуется через HTTP. Первый ручной запуск timer/service является обязательным smoke-test после установки.

## 7. Что пользователь должен учитывать сейчас

Первый адрес работает по HTTP. Это позволяет немедленно начать работу, но трафик и пароль не защищены TLS на транспортном уровне. Следующий инфраструктурный шаг — выделенный домен или поддомен с HTTPS и переключение `BUSINESS_COOKIE_SECURE=true`.

До HTTPS следует использовать отдельные уникальные пароли только для этой системы и не повторять пароли от почты, GitHub, банка или других сервисов.

Регистрация закрыта на логины `artkozk` и `sweetybboy`. Почта не подтверждается, как и требовалось для быстрого старта. После регистрации сессия живёт 90 дней, если cookie не очищена.

## 8. Правило последующих отчётов

Этот документ фиксирует историческое состояние первого деплоя и не удаляется. Изменения адреса, HTTPS, backup, БД или процесса публикуются отдельным датированным отчётом либо актуализацией в конце документа с объяснением прошлого и текущего поведения.

## 9. Актуализация 2026-08-12: production hardening после первого smoke

Разделы 1–3 и 7 сохраняют историю первоначального запуска по IP и временному открытому порту. Сразу после подтверждения работоспособности выполнен hardening; текущие значения имеют приоритет над историческими:

- актуальный адрес: `https://business-control.85-198-82-221.sslip.io/`;
- HTTP адрес перенаправляет на HTTPS кодом `301`;
- внешний HTTPS health возвращает `{"status":"ok"}`;
- сертификат Let's Encrypt действителен до 2026-11-10 и имеет настроенное автоматическое обновление certbot;
- backend слушает `127.0.0.1:8522`, а не `*:8522`;
- UFW rule `8522/tcp`, добавленное для первого smoke, удалено для IPv4 и IPv6;
- внешний доступ идёт через существующие стандартные nginx-порты `80/443`;
- `BUSINESS_COOKIE_SECURE=true`;
- конфигурации Leonov Care и других nginx hosts не удалялись и не заменялись.
- перед приложением включён nginx Basic Auth пользователя `founders`, credential хранится только в `/etc/nginx/business-control.htpasswd` с mode `0640` и не находится в Git;
- для hostname добавлен `X-Robots-Tag: noindex, nofollow, nosnippet`.

Причина изменения: рабочая регистрация и сессия содержат чувствительные данные. Первый HTTP этап был допустим только как короткая техническая проверка процесса; ежедневная работа должна идти через TLS и без прямого доступа к application port.

Дополнительная причина Basic Auth: production регистрация разрешает только логины `artkozk` и `sweetybboy`, но без внешнего барьера любой посетитель мог бы первым зарегистрировать один из них. Общий доступ команды закрывает этот race до появления полноценных invitations. Он вводится браузером один раз на устройство и не отменяет личные аккаунты или длинные сессии приложения.

## 10. Фактическая проверка автоматического backup

После установки backup units выполнен ручной production запуск:

- `business-control-backup.service` завершился `status=0/SUCCESS`;
- создан `/var/lib/business-control/backups/business-control-20260812-204000.db`;
- owner/mode: `business-control:business-control`, `0640`;
- `PRAGMA integrity_check` вернул `ok`;
- `business-control-backup.timer` активен;
- следующий автоматический запуск назначен на 2026-08-13 около `02:15 UTC` с `RandomizedDelaySec=300`;
- retention: 30 дней.

Этот backup находится на том же VPS и не является offsite-копией. Это текущее известное ограничение: автоматизация защищает от части ошибок приложения и оператора, но offsite выгрузка всё ещё необходима для защиты от полной потери сервера.
