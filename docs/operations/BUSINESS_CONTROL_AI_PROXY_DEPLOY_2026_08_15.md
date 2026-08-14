# Развёртывание рабочего Gemini через прокси

Дата: 15 августа 2026 года.

## Разрешённая инфраструктура

Единственный production-хост приложения и данных: `159.194.231.150`, домен `control.e-rd.ru`. Внешний прокси разрешён только для исходящего AI-трафика. Размещать на нём приложение, базу, вложения или резервные копии запрещено.

## Предварительная проверка

С основного production-хоста выполнен прямой запрос к Gemini Developer API через выбранный HTTP-прокси. Проверка завершилась:

```text
HTTP 200
Gemini candidate present
```

Значение proxy URL и API key намеренно не записывается в документацию или вывод deployment script.

Первый полный smoke выявил две отдельные проблемы и штатно вернул предыдущий release: первый выбранный прокси начал отвечать нестабильно, а Gemini 2.5 завершал короткий структурированный ответ после расходования output budget на thinking. Четыре альтернативных прокси затем одновременно вернули `HTTP 200`, `finishReason=STOP` и `{"ok":true}` с полным production generation config. Активный маршрут выбран из этой проверенной группы, а в payload зафиксирован `thinkingBudget=0`. Исторический неуспешный прогон сохранён здесь, потому что он подтверждает работу автоматического rollback.

## Процедура релиза

1. Локально выполняются `gofmt`, `go test ./...`, `go vet ./...` и `git diff --check`.
2. Новый unit test поднимает тестовый HTTP-прокси и доказывает, что Gemini-запрос проходит через него.
3. Отдельный тест доказывает отсутствие прямого fallback при некорректном proxy URL.
4. В root-only env основного сервера устанавливаются `AI_PROXY_URL`, Gemini Developer API endpoint и модель `gemini-2.5-flash`.
5. Собирается статический Linux amd64 binary.
6. `deploy-ai-proxy-release-20260815.sh` создаёт согласованный SQLite backup и проверяет integrity/foreign keys.
7. Binary устанавливается в новый release-каталог; symlink `current` переключается атомарно.
8. Временная сессия `artkozk` вызывает `/api/ai/health` и `/api/ai/suggest-record`.
9. Релиз принимается только при `route=proxy`, `providerAvailable=true`, `source=gemini` в обоих реальных вызовах.
10. При ошибке восстанавливаются предыдущие env и release, временная сессия удаляется.
11. После успеха запускается штатная зашифрованная резервная копия.

## Почему health недостаточно

TCP-соединение или HTTP 200 от общего health не доказывают работу нейросети. Поэтому AI health внутри приложения сам запрашивает валидируемую классификацию, а deployment дополнительно проходит пользовательский endpoint подсказки. Так проверяются proxy, TLS, key, model, формат ответа, JSON-декодирование и бизнес-валидация.

## Фактический production-результат

Этот раздел дополняется после развёртывания. Исторический план не удаляется; release path, rollback path, хеши, состояние AI, БД, systemd, nginx, домена и backup будут записаны отдельным подразделом.

## Фактический production-результат

Развёртывание выполнено только на разрешённом основном хосте `159.194.231.150`.

```text
release=/opt/business-control/releases/20260815-ai-proxy-694acaa
previous=/opt/business-control/releases/20260814-production-quality-384b395
binary_sha256=de230d7eefbea65a149801263c6551aeffef86389d9fc610e495a7875549d88e
pre_release_backup=/var/lib/business-control/backups/business-control-20260814-213020-pre-ai-proxy.db
pre_release_backup_sha256=96e55451cec5ca170c9e3a170314627f64546eccf55c456bd8bf50f481c0bd20
```

Реальный AI smoke через локальный backend и повторно через публичный HTTPS-домен:

```text
provider=gemini
model=gemini-2.5-flash
route=proxy
providerAvailable=true
source=gemini
suggestion_source=gemini
GET https://control.e-rd.ru/api/health -> 200 {"status":"ok"}
```

Проверки процесса и данных:

```text
business-control=active
nginx=active
business-control NRestarts=0
business-control ExecMainStatus=0
business-control-backup.timer=enabled/active
database integrity=ok
foreign key violations=0
/etc/business-control.env owner=root:root mode=0600
AI_PROXY_URL entries=1
application warnings after deploy=0
nginx warnings after deploy=0
```

Первый запрос общего health в retry-loop снова попал в короткий промежуток до открытия локального порта. Последующий запрос прошёл; это предусмотренный retry, а не ошибка сервиса. Успешный процесс имеет `NRestarts=0`.

После записи production-задачи создана и проверена новая зашифрованная копия:

```text
/var/backups/business-control/business-control-20260814-213313.tar.gz.enc
SHA-256: 69698954d9695974d21d65c27afe35f31a7786cde29becbe65be23ddede5ce7e
owner=root:root
mode=0600
bytes=71424
plaintext archives in encrypted backup directory=0
```

В платформе от имени `artkozk` создана задача `Подключить рабочий Gemini через серверный прокси` (`da39096f74eae32582f076ebe4f9d8c1`). Она связана с корневой веткой разработки платформы, имеет `priority=high`, план `120` минут, факт `90` минут, предметное Markdown-доказательство, итоговый результат, `status=completed`, `progress=100%` и уведомление второго основателя. Последний зашифрованный backup включает карточку, доказательство и activity.

Временные smoke-сессии и загруженные файлы из `/tmp` удалены. Неуспешный release-каталог первого прогона удалён после проверки, активный и rollback-релизы сохранены.
