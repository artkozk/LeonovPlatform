# Domain Protection Policy — `leonovcare.ru` (2026-05-13)

## 1. Контекст инцидента

1. В ходе релизных действий контур разработки `LeonovCarePlatform` был ошибочно привязан к основному домену `leonovcare.ru`.
2. Этот домен занят другим сайтом и не должен обслуживать текущий проект в разработке.
3. Инцидент критичный, потому что подмена root/proxy на основном домене ломает боевой сайт владельца домена.

## 2. Как было на момент инцидента

1. Активный nginx-конфиг ` /etc/nginx/sites-available/leonovcare.ru ` содержал привязку к LeonovCarePlatform:
- `root /opt/leonovcare-platform/current/frontend/dist`
- прокси API на `127.0.0.1:8510`
2. Это переводило внешний домен `https://leonovcare.ru` на приложение в разработке.

## 3. Что сделано для восстановления

1. Перед откатом создан backup текущей проблемной версии:
- `/etc/nginx/sites-available/leonovcare.ru.backup_before_restore_20260513_091148`
2. Восстановлена рабочая историческая версия конфига:
- источник: `/etc/nginx/sites-available/leonovcare.ru.bak_20260511`
- назначение: `/etc/nginx/sites-available/leonovcare.ru`
3. Применён reload nginx после проверки синтаксиса:
```bash
nginx -t
systemctl reload nginx
```

## 4. Проверка результата (обязательная)

1. Проверка HTTP-статуса:
```bash
curl -k -I https://leonovcare.ru
```
Ожидание: `HTTP/1.1 200 OK`.

2. Проверка, что отдается не LeonovCarePlatform:
```bash
curl -k https://leonovcare.ru | head
```
Ожидание: HTML старого сайта (например, `IT Mentorship Lab — ИП Олег Леонов`), а не UI LeonovCarePlatform.

3. Дополнительная проверка root-директории в nginx:
```bash
grep -n "root " /etc/nginx/sites-available/leonovcare.ru
```
Ожидание: root не указывает на `/opt/leonovcare-platform/current/frontend/dist`.

## 5. Постоянный запрет на изменение домена

### 5.1 Обязательное правило

1. Домен `leonovcare.ru` является защищённым и не должен использоваться для LeonovCarePlatform.
2. Любая автоматизация, скрипт деплоя, ручной релиз и любая AI-агентная сессия должны считать привязку этого домена к текущему проекту запрещённой.
3. Публикация LeonovCarePlatform выполняется только на отдельном контуре (`85.198.82.221:8511` или отдельный явный dev/stage-домен).

### 5.2 Техническая блокировка в deploy

1. В `deploy/server/deploy.sh` добавлен preflight `enforce_domain_lock`.
2. Проверка выполняется до сборки/миграций и останавливает деплой (`exit 1`), если конфиг `leonovcare.ru`:
- указывает `root` на `/opt/leonovcare-platform/current/frontend/dist`;
- проксирует API на `127.0.0.1:8510`;
- проксирует frontend на `127.0.0.1:8511`.
3. Проверка fail-closed:
- если файл `/etc/nginx/sites-available/leonovcare.ru` не найден, деплой останавливается.
4. Осознанное отключение возможно только вручную через `DOMAIN_LOCK_ENABLED=false`, что должно быть зафиксировано отдельно в release-note и согласовано до запуска.

## 6. Почему сделано именно так

1. Инцидент был не в коде продукта, а в ошибочной маршрутизации домена на инфраструктурном уровне.
2. Документ + preflight-блокировка формируют двойную защиту: процессную (операционный запрет) и техническую (аварийная остановка deploy).
3. Fail-closed режим выбран специально, чтобы нельзя было «молча» пройти деплой при неизвестном состоянии доменного конфига.

## 7. Чеклист для каждого деплоя (добавочный)

1. Перед `bash deploy/server/deploy.sh` проверить:
```bash
grep -nE "root |proxy_pass" /etc/nginx/sites-available/leonovcare.ru
```
2. Убедиться, что нет ссылок на:
- `/opt/leonovcare-platform/current/frontend/dist`
- `127.0.0.1:8510`
- `127.0.0.1:8511`
3. Запустить deploy.
4. Повторно проверить:
```bash
curl -k -I https://leonovcare.ru
curl -k https://leonovcare.ru | head
```

## 8. Ссылки на связанные документы

1. `docs/operations/DEPLOYMENT_RUNBOOK.md` — обновлённый deploy-порядок с доменным preflight.
2. `DEPLOYMENT.md` — канонический deploy flow с обязательным domain lock.
3. `docs/operations/SERVER_FIXES_2026_05_11.md` — append-only актуализация статуса домена после rollback.
4. `docs/operations/IMPLEMENTATION_CHANGELOG.md` — запись о внесённом изменении.
