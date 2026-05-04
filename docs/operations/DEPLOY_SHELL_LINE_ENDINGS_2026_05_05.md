# Deploy shell line endings — 2026-05-05

## Что изменено

В `.gitattributes` добавлено правило `*.sh text eol=lf`.

## Почему это нужно

Сервер запускает shell-скрипты через Bash. Если файл попадает на сервер с Windows CRLF, Bash читает `set -euo pipefail\r` и завершает деплой с ошибкой `invalid option name`. Поэтому shell-скрипты должны храниться и архивироваться с LF независимо от локальной настройки Git на Windows.

## Как проверять

Перед деплоем проверь:

```bash
git check-attr eol -- deploy/server/deploy.sh
```

Ожидаемый результат: `eol: lf`.

На сервере можно проверить первые строки:

```bash
head -3 /opt/leonovcare-platform/current/deploy/server/deploy.sh | cat -v
```

В выводе не должно быть `^M`.

## Почему не исправлять вручную на сервере

Ручной `dos2unix` чинит только текущий файл. Правило в `.gitattributes` фиксирует причину: последующие архивы и деплои получают корректные line endings автоматически.