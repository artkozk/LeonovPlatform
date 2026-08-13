# Развёртывание карточек вопросов Business Control

Дата: 2026-08-13

Production: `https://control.e-rd.ru/`

Git commit приложения: `8c71f26` (`Add founder question workflow`)

## 1. Состав релиза

На production развёрнут релиз с первой структурированной цепочкой совместной работы основателей:

`группа вопросов -> вопрос -> отдельный ответ каждого основателя -> совместное решение`.

В тот же бинарник входят обновлённая навигация, единый раздел истории, быстрые действия обзора, типовые формы карточек, новый экран обсуждения и четырёхшаговое обучение первого входа.

Серверная миграция `002_question_workflow.sql` добавляет `records.subtype`, `question_items`, `question_answers`, `question_decisions` и необходимые индексы. Существующая миграция `001_init.sql` не редактировалась.

## 2. Проверка до развёртывания

Перед сборкой выполнены:

- `go test ./...` — успешно;
- `go vet ./...` — успешно;
- `node --check web/app.js` — успешно;
- `git diff --check` — успешно;
- интеграционный тест двух пользователей, двух вопросов и двух способов совместного решения;
- browser QA desktop и mobile `390x844` без горизонтального переполнения;
- проверка отсутствия warning/error в консоли браузера.

Перед переключением production release запущен штатный online backup. Копия:

`/var/lib/business-control/backups/business-control-20260813-100932.db`

Её параметры: owner `business-control:business-control`, mode `0640`, `PRAGMA integrity_check=ok`. До миграции база содержала 1 пользователя, 1 карточку и только `001_init.sql` в `schema_migrations`.

## 3. Артефакт и установка

Linux `amd64` бинарник собран с `CGO_ENABLED=0`, `-trimpath` и `-ldflags="-s -w"`.

SHA-256:

`45d8043c3a68a2f122962b825de61aefdc7a632feaa9a22f6ac8b2f9cdb90320`

Release-каталог:

`/opt/business-control/releases/20260813-question-workflow-8c71f26`

Текущий symlink:

`/opt/business-control/current -> /opt/business-control/releases/20260813-question-workflow-8c71f26`

Предыдущий release для rollback:

`/opt/business-control/releases/20260813-usability-r3`

Бинарник сначала загружен во временный путь, проверен по SHA-256, установлен в отдельный неизменяемый release-каталог, после чего symlink переключён и `business-control.service` перезапущен.

## 4. Проверенный rollback

Первая попытка post-deploy проверки содержала ошибку кавычек в диагностическом Python-выражении. Сам новый сервис к этому моменту уже прошёл health-check, но shell trap корректно вернул symlink на `20260813-usability-r3` и перезапустил прежний бинарник.

После автоматического отката подтверждены:

- сервис `active`;
- локальный health-check успешен;
- база имеет `integrity_check=ok`;
- миграция `002_question_workflow.sql` уже зафиксирована;
- прежний бинарник продолжает работать с расширенной append-only схемой;
- 1 пользователь и 1 карточка сохранены.

После исправления только диагностической команды релиз повторно переключён. Этот эпизод документируется, потому что он фактически проверил предусмотренный механизм rollback и совместимость предыдущего бинарника с новой схемой.

Ручной rollback кода:

```bash
ln -sfn /opt/business-control/releases/20260813-usability-r3 /opt/business-control/current
systemctl restart business-control
curl -fsS http://127.0.0.1:8522/api/health
```

Миграцию базы при rollback кода удалять нельзя. Она добавляет новые столбец и таблицы и не нарушает чтение прежним бинарником.

## 5. Проверка после развёртывания

Подтверждено на сервере:

- `business-control.service` активен и включён;
- процесс слушает `127.0.0.1:8522`;
- локальный `/api/health` возвращает `{"status":"ok"}`;
- HTTPS `/api/health` возвращает `{"status":"ok"}`;
- `nginx -t` успешен;
- production root возвращает `200`;
- HTTP root возвращает `301` на HTTPS;
- заголовок `WWW-Authenticate` отсутствует, общий командный пароль не возвращён;
- Content Security Policy присутствует;
- `X-Robots-Tag: noindex, nofollow, nosnippet` сохранён;
- production `app.js` содержит `question_set` и `onboardingSteps` и не содержит старый класс `type-code`;
- экран входа визуально проверен, в консоли браузера нет warning/error.

Проверка SQLite после миграции:

- `PRAGMA integrity_check=ok`;
- `schema_migrations=001_init.sql,002_question_workflow.sql`;
- пользователей: 1;
- карточек: 1;
- новых вопросов, ответов и решений: 0 до начала реальной работы.

Существующие данные не сбрасывались и не копировались в новую БД. Миграция применена к текущей рабочей базе автоматически при старте нового бинарника.

## 6. Backup после миграции

После успешного smoke создан новый online backup:

`/var/lib/business-control/backups/business-control-20260813-101137.db`

Проверено:

- owner `business-control:business-control`;
- mode `0640`;
- размер `233472` байта;
- `PRAGMA integrity_check=ok`;
- присутствуют обе миграции;
- присутствуют исходные 1 пользователь и 1 карточка.

`business-control-backup.timer` остаётся `enabled` и `active`. Копия находится на том же VPS и не заменяет требуемый offsite backup.

## 7. Границы production smoke

Авторизованный production-сценарий не выполнялся, потому что пароль существующего пользователя не извлекается и не сбрасывается ради деплоя. Полный пользовательский сценарий с двумя отдельными сессиями проверен локально на чистой базе тем же бинарным кодом, а production проверен на уровне миграции, сохранности данных, публичного интерфейса, статических ресурсов, HTTPS и systemd.

Пользовательский процесс и ограничения релиза описаны в `docs/product/BUSINESS_CONTROL_QUESTION_WORKFLOW_AND_UI_RELEASE_2026_08_13.md`.
