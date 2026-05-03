# Backend (Go)

## Быстрый запуск

1. Установите PostgreSQL, Redis, Java (JDK), Go.
2. Скопируйте `.env.example` в `.env` и задайте секреты.
3. Запустите API:

```bash
go mod tidy
go run ./cmd/server
```

4. Запустите воркер проверки:

```bash
go run ./cmd/worker
```

## Что реализовано

- JWT auth, регистрация, восстановление пароля, email verify.
- Личный кабинет и персональные настройки редактора.
- Курсы/уроки/задачи + демо-курс Java Start.
- Очередь проверок через Redis + Java judge.
- Геймификация: XP, уровни, достижения, лидерборд.
- Подписки Free/Pro/Premium и Cardlink-подготовка.
- AI-подсказки (OpenAI) с plan-gating и аудитом в БД.
- Админ API: контент, блокировка пользователей, метрики, CSV экспорт.
- Google OAuth через проверку `id_token` (при заданном `GOOGLE_CLIENT_ID`).

## Python v18 Strict Pedagogy rollout (2026-05-03)

1. Курс `python-zero` переводится на пакет:
- `материалы/v18_STRICT_PEDAGOGY/course_import.json`.

2. Добавлены backend-артефакты внедрения:
- `backend/tools/generate_python_v18_materials_migration.js`;
- `backend/tools/validate_python_v18_materials_import.js`;
- `backend/migrations/026_reseed_python_zero_v18_strict_pedagogy.sql`;
- `docs/operations/PYTHON_V18_STRICT_PEDAGOGY_ROLLOUT_2026_05_03.md`;
- `docs/operations/PYTHON_V18_STRICT_PEDAGOGY_IMPORT_VALIDATION_2026_05_03.md`.

3. Что попадает в runtime:
- 5 модулей;
- 169 уроков;
- 1963 `lesson_blocks`;
- 1153 practice/project tasks;
- 304 quiz blocks;
- 912 structured quiz questions.

4. Почему это сделано как новая migration `026`, а не заменой старой `025`:
- старые миграции уже являются частью production history, их нельзя переписывать без риска рассинхронизации `schema_migrations`;
- отдельная `026` явно фиксирует переход от v16 к v18;
- deploy остаётся стандартным: backend стартует, применяет неприменённые migrations, затем отдаёт уже обновлённый курс.

5. Checker payload адаптируется генератором:
- `python_pytest.test_code` сохраняется в runtime как `pytest_code`;
- `http_api.public_tests/hidden_tests` преобразуются в runtime `tests[]`;
- `sql_query.schema_sql + seed_sql` сохраняются в `source_policy.checker.init_sql`;
- test steps публикуются как quiz blocks с `quiz_payload.questions[]`.

6. Проверки перед deploy:
- `python материалы/v18_STRICT_PEDAGOGY/validate_course.py` — PASS;
- `node backend/tools/generate_python_v18_materials_migration.js` — PASS;
- `node backend/tools/validate_python_v18_materials_import.js` — PASS;
- `go test ./...` — PASS.

## OpenAI env

- `OPENAI_API_KEY` — ключ API для генерации подсказок.
- `OPENAI_BASE_URL` — базовый URL OpenAI API (по умолчанию `https://api.openai.com`).
- `OPENAI_MODEL` — модель для подсказок (по умолчанию `gpt-5.4-mini`).
- `OPENAI_HTTP_PROXY` — полный URL HTTP-прокси для OpenAI запросов (например, `http://user:pass@host:port`).
- `OPENAI_PROXY_HOST`, `OPENAI_PROXY_PORT`, `OPENAI_PROXY_USERNAME`, `OPENAI_PROXY_PASSWORD` — альтернативный способ задать тот же прокси по частям.
- `GOOGLE_CLIENT_ID` — client id Google OAuth для проверки `aud` в `id_token`.

## Launch update (2026-04-29)

1. OAuth входы выведены из launch-профиля (email-only auth flow).
2. Регистрация использует профиль:
- `firstName`
- `lastName`
- `nickname` (unique)
3. В `users` добавлен системный `public_id`.
4. Demo Java seed отключен (`AUTO_SEED=false` по умолчанию).
5. Для production judge рекомендован `JUDGE_MODE=docker`.
6. Для платежного webhook включена подпись:
- `CARDLINK_REQUIRE_SIGNATURE=true`
- `X-Cardlink-Signature` (HMAC SHA256).

## Payments update (2026-04-29, v2.22)

1. Рабочий checkout:
- при заполненных `CARDLINK_BASE_URL`, `CARDLINK_SHOP_ID`, `CARDLINK_API_TOKEN` backend создает bill через Cardlink API;
- при неполной конфигурации остается безопасный `pending_config`.

2. Статусы оплаты:
- endpoint `GET /api/v1/subscription/payments/:paymentId` возвращает статус конкретного платежа;
- параметр `sync=true` принудительно сверяет статус счета через Cardlink API.

3. Webhook форматы:
- поддержан Cardlink form postback (`InvId`, `Status`, `OutSum`, `SignatureValue`);
- сохранена поддержка legacy JSON webhook (`X-Cardlink-Token` + HMAC подпись тела).

4. Подписки:
- истекшие active-подписки автоматически переводятся в `expired`;
- fallback на `free` гарантируется при отсутствии валидной active-подписки;
- повторная оплата текущего paid-плана продлевает `ends_at`.

5. Новые env для платежного контура:
- `CARDLINK_SHOP_ID`
- `CARDLINK_API_TOKEN`
- `CARDLINK_CURRENCY_IN`
- `CARDLINK_BILL_TTL_SECONDS`
- `CARDLINK_SUCCESS_URL`
- `CARDLINK_FAIL_URL`
- `CARDLINK_RETURN_URL`

## Payments reliability hardening (2026-04-29, v2.53)

1. Checkout теперь работает по fail-fast модели:
- если Cardlink не готов для создания реального счёта, `POST /api/v1/subscription/checkout` возвращает `503` с детальной причиной;
- backend больше не имитирует «успешно созданный» checkout в `pending_config` при неполной конфигурации прод-оплаты;
- в ответе возвращается список недостающих обязательных параметров (`missing`), чтобы оператор видел точный чек-лист.

2. Добавлены backend callback endpoints для Cardlink redirect POST:
- `POST /api/v1/payments/cardlink/return/success`
- `POST /api/v1/payments/cardlink/return/fail`
- и зеркальные `GET`-маршруты на те же URL для совместимости с браузерными fallback-сценариями.

3. Для callback redirect реализован безопасный flow:
- принимается `InvId/OutSum/SignatureValue` из Cardlink;
- проверяется подпись `SignatureValue` (формула `md5(OutSum:InvId:apiToken)` в upper-case);
- статус платежа фиксируется в БД (`paid` для success, `failed` для fail, если Cardlink не прислал явный `Status`);
- после фиксации backend делает `303 redirect` на frontend `/billing?pendingPayment=<id>&cardlinkResult=<status>`.

4. Автоматическая подстановка callback URL при создании счёта:
- если `CARDLINK_SUCCESS_URL` / `CARDLINK_FAIL_URL` не заданы явно, backend автоматически отправляет в Cardlink URL на свои новые callback routes;
- адрес строится из входящего запроса (`X-Forwarded-Proto`, `X-Forwarded-Host`, fallback на `Request.Host`).

5. Операционные требования для production:
- `CARDLINK_BASE_URL` должен быть рабочим (`https://cardlink.link` или актуальный endpoint Cardlink API);
- обязательно заполнить `CARDLINK_SHOP_ID` (или `CARDLINK_MERCHANT_ID`);
- обязательно заполнить `CARDLINK_API_TOKEN` (или `CARDLINK_SECRET` как совместимый fallback);
- в кабинете Cardlink нужно добавить серверный IP в allowlist API, иначе API возвращает `403 api:error.ip_access_denied`.

Почему сделано именно так:

1. Для запуска на 1500 пользователей «тихий» `pending_config` при неготовой платёжке создаёт ложное ощущение работоспособности и увеличивает время на инцидент-диагностику.
2. Cardlink шлёт user redirect как `POST`, а фронтенд-статика обычно принимает только `GET/HEAD`; без backend callback пользователь получает «битый» возврат после оплаты.
3. Перенос проверки подписи и фиксации статуса на backend убирает зависимость от браузерного поведения и повышает предсказуемость платежного результата.
4. Автогенерация callback URL снижает риск misconfig в релизах, когда success/fail URL забывают обновить вручную.

## Cardlink production enablement status (2026-04-30, v2.55)

1. Что уже применено на production:
- merchant/shop/token параметры Cardlink заполнены в `backend/.env`;
- backend callback URL явно зафиксированы:
  - `CARDLINK_SUCCESS_URL=http://85.198.82.221:8510/api/v1/payments/cardlink/return/success`
  - `CARDLINK_FAIL_URL=http://85.198.82.221:8510/api/v1/payments/cardlink/return/fail`
- checkout больше не блокируется по причине отсутствия `CARDLINK_SHOP_ID`.

2. Фактический текущий ответ Cardlink API на create-bill:
- HTTP `403`;
- payload содержит `api:error.ip_access_denied`;
- провайдер возвращает IP сервера: `85.198.82.221`.

3. Что нужно для полного go-live оплаты:
- добавить IP `85.198.82.221` в API allowlist/whitelist в кабинете Cardlink;
- после внесения IP повторить smoke `POST /api/v1/subscription/checkout` и убедиться, что backend возвращает `200` + реальный `checkoutUrl` от Cardlink.

Почему это важно:

1. При заблокированном IP платежный backend формально исправен, но не может создать счёт у провайдера — пользователь получает `502 failed to create cardlink checkout`.
2. Документированная фиксация конкретного внешнего блокера экономит время при запуске и не позволяет команде тратить часы на ложный дебаг приложения.

## Monthly tariff boundary fix (2026-04-30, v2.56)

1. Срок paid-подписки переведен с фиксированного `30 day` на календарный `1 month`:
- активация после успешной оплаты;
- продление при повторной оплате того же тарифа;
- fallback-расчет `ends_at` при `cancel_at_period_end`.

2. Что это меняет в поведении:
- подписка теперь заканчивается ровно через календарный месяц от даты активации/продления;
- после наступления `ends_at` пользователь автоматически переводится в `free` (через `ensureSubscriptionState`).

3. Почему сделано именно так:
- `30 day` и «один месяц» не эквивалентны для календаря (месяцы 28/29/30/31 дней), из-за чего возникал сдвиг срока;
- для тарифа «на месяц» продуктово корректен именно календарный интервал `1 month`.

## Tariff duration rollback to fixed 30 days (2026-04-30, v2.57)

1. По продуктовой обратной связи длительность paid-тарифа возвращена к фиксированному интервалу:
- `interval '30 day'` вместо `interval '1 month'`.

2. Где применяется:
- активация подписки после успешной оплаты;
- продление текущего paid-плана;
- `cancel_at_period_end` fallback, когда `ends_at` у active подписки ещё не задан.

3. Почему сделано именно так:
- операционно проще считать поддержку и коммуникацию срока по фиксированным 30 дням;
- фиксированный интервал убирает календарные отличия между месяцами 28/29/30/31 дней и делает срок единообразным для всех пользователей.

## Python lesson + session refresh update (2026-04-29, v2.24)

1. Auth session resilience:
- frontend API client теперь автоматически делает `POST /auth/refresh` при `401` от защищенных endpoint;
- исходный запрос ретраится после получения нового access token;
- при провале refresh токены очищаются и пользователь переводится на auth-экран.

2. Tasks language model:
- в таблицу `tasks` добавлено поле `language` (`java`/`python`), миграция `007_python_course_and_lesson_blocks.sql`;
- `AdminCreateTask` поддерживает `language` с серверной валидацией.

3. Judge:
- интерфейс judge расширен методом `EvaluatePython`;
- добавлен Python runner (stdin/stdout) для `local` и `docker` режимов;
- worker получает язык задачи из `tasks.language` и запускает соответствующий evaluator.

4. Learning API:
- `GET /lessons/:lessonID` теперь возвращает:
  - `lesson.moduleTitle`;
  - `tasks[].language`;
  - `blocks[]` (структурированные шаги урока).
- `GET /tasks/:taskID` возвращает `task.language`.

5. Launch content:
- добавлен курс `python-zero` с первым уроком;
- добавлены практические задачи и тест-кейсы автопроверки.

Почему так:

1. Для стабильного UX при коротком TTL access token нужен автоматический механизм refresh/retry.
2. Python-контур должен быть нативно поддержан на backend уровне, иначе практические шаги первого урока будут нефункциональны.
3. Структурированные блоки урока делают контент масштабируемым под формат "теория + код + тест".

## Lesson UX update (2026-04-29, v2.25)

1. Added authenticated preview run endpoint:
- `POST /tasks/:taskID/run`
- Returns judge verdict immediately without creating submission rows.

2. Lesson page switched to in-step practice workflow:
- editor embedded in practice step;
- actions: run, submit, AI hint, reset;
- no required redirect to `/tasks/:taskID`.

3. Quiz interaction updated:
- explicit check action;
- failed answer can be reset via retry button;
- no immediate reveal of correct option on failure.

4. Step completion model in UI:
- theory/summary step is marked completed on open;
- practice step is marked completed on `accepted` run/submission verdict.

5. Content cleanup:
- removed invalid-code educational fragment `print(Привет)` from lesson 1 theory block via migration `008_cleanup_python_lesson_content.sql`.

## Judge fallback note (2026-04-29)

1. Если `JUDGE_MODE=docker`, но docker runtime недоступен для API-процесса, judge автоматически переходит на local execution mode.
2. Это поведение добавлено для сохранения работоспособности встроенного запуска кода в шагах урока.

## Starter templates + newline normalization (2026-04-29, v2.27)

1. Миграция `009_fix_python_starter_templates_and_newlines.sql`:
- исправляет уже развернутые `python-zero` задачи, где `starter_code`/`solution_code` могли содержать буквальные `\n`;
- обновляет `starter_code` на шаблоны без готового решения;
- сохраняет `solution_code` как эталон для judge.

2. Для новых инсталляций обновлена миграция `007_python_course_and_lesson_blocks.sql`:
- `starter_code`/`solution_code` переведены на `E''`-строки, чтобы переносы строк сохранялись корректно;
- `starter_code` теперь не подставляет финальный ответ ученику заранее.

3. Frontend нормализует стартовый код при загрузке задачи:
- поддержка декодирования `\r\n`, `\n`, `\t`, `\"` в `LessonPage` и `TaskPage`.

4. Результат запуска кода выводится в интерфейсе перед отправкой:
- добавлен блок `Консоль (первый тест)` со `stdin/stdout/stderr` для `run` сценария.

## Source policy guardrails + style hints (2026-04-29, v2.28)

1. Добавлен столбец `tasks.source_policy JSONB` (миграция `010_source_policy_guardrails.sql`).

2. `source_policy` применяется на трех слоях:
- `POST /tasks/:taskID/run` (preview запуск),
- `POST /tasks/:taskID/submissions` (валидация до постановки в очередь),
- worker (`processSubmissionByID`) перед judge evaluation.

3. Формат `source_policy`:
- `language` — язык, для которого правило активно;
- `message` — пользовательское сообщение при нарушении;
- `requireAllRegex` — список regex, каждый должен совпасть;
- `forbidAnyRegex` — список regex, ни один не должен совпасть;
- `ignoreCommentOnlyLines` — исключать строки-комментарии (`#`, `//`) из проверки.

4. Для `python-zero` задачи `Простая математика` включены guardrails:
- нельзя сдавать прямой вывод готовых констант (`print(20)`, `print(25)`, `print(42)`);
- требуется использование арифметических выражений по условию.

5. UI-часть:
- в `LessonPage` и `TaskPage` блок консоли запуска (`stdin/stdout/stderr`) сделан всегда видимым;
- после принятого решения (`accepted`) в Python-редакторе показываются style-hints через иконку лампочки и hover (пример: `a = a + 3` -> `a += 3`).

Почему так:

1. Защита от обходов должна работать серверно и одинаково для run/submit/worker, иначе баг будет возвращаться через другой маршрут.
2. Task-level JSON policy позволяет масштабировать правила на новые задачи без хардкода в judge.
3. Style hints включаются только после принятого решения, чтобы улучшать качество кода без раскрытия ответов заранее.

Hotfix (v2.29):

1. Добавлена миграция `011_fix_source_policy_regex_escaping.sql`.
2. Назначение:
- исправить экранирование regex в уже примененном `source_policy` для `Простая математика`;
- убрать ложный `wrong_answer` на корректном коде вида `print(12 + 8)`, `print(30 - 5)`, `print(7 * 6)`.

Update (v2.30):

1. Source policy поддерживает контекстные rule-объекты:
- `requireAll: [{ pattern, message }]`
- `forbidAny: [{ pattern, message }]`

2. Добавлен специальный сценарий для пустого решения:
- если после фильтрации комментариев код пуст, возвращается `emptySourceMessage` (или дефолтный текст о пустом коде).

3. Для `Простая математика` policy переведен на контекстные сообщения:
- отдельный текст на каждый отсутствующий расчет;
- отдельный текст на каждую запрещенную константу.

4. Для уже развернутых БД добавлена миграция:
- `012_source_policy_contextual_messages.sql`.

Почему так:

1. Это устраняет ложное сообщение про "готовые константы" в случае, когда пользователь еще не написал код.
2. Ошибка становится привязанной к конкретному действию ученика, что улучшает обучающий UX и уменьшает повторяемость подобных инцидентов.

## Python module 1 task adaptation (2026-04-29, v2.41)

1. Добавлена миграция `016_seed_python_module1_tasks_bindings_and_tests.sql`:
- импортирует задачи уроков 2–13 курса `python-zero`;
- импортирует автотесты;
- связывает практические `lesson_blocks` с `task_id`.

2. Добавлен генератор миграции:
- `backend/tools/generate_module1_tasks_migration.js`;
- источник контента: `C:/Users/Artemy/Downloads/osnovy_python_platform_ready_v3 (1).md`.

3. Команда пересборки миграции из исходного markdown:

```bash
node backend/tools/generate_module1_tasks_migration.js
```

4. Контрольные значения после генерации:
- `Lessons: 12`
- `Tasks: 75`
- `Tests: 211`

Почему так:

1. Ранее lessons 2–13 были импортированы только как блоки контента без привязанных задач, поэтому в UI практики не открывали редактор с автопроверкой.
2. Генерация из исходного markdown исключает ручные расхождения между условием, шаблоном, эталоном и тестами.

## Full course v4 import (2026-04-29, v2.49)

1. Добавлен генератор полной миграции курса:
- `backend/tools/generate_full_course_v4_migration.js`.
- Источники:
  - `C:/Users/Artemy/Downloads/python_course_platform_v4_full.md`
  - `C:/Users/Artemy/Downloads/import_manifest.csv`
- Результат генерации:
  - `backend/migrations/018_seed_python_zero_full_v4.sql`.

2. Логика импорта практики переведена на whitelist-модель body:
- в `body_markdown` попадают только секции:
  - `Коротко`
  - `Условие`
  - `Вход`
  - `Выход`
  - `Пример 1..3`
- служебные секции не попадают в видимый body:
  - `Шаблон`
  - `Подсказки`
  - `Эталон`
  - `Автотесты`
  - `Скрытые тесты`
  - `AI-инструкция`
  - `Админ`.

3. Системные поля задачи при импорте:
- `Шаблон` -> `starter_code`;
- `Подсказки` -> `source_policy.hints[]`;
- `Эталон` -> `solution_code`;
- `Автотесты/Скрытые тесты` -> `task_test_cases` (с корректной `is_hidden`).

4. Дополнительные правила парсера:
- поддержаны заголовки уроков/шагов в форматах `#|##|###`;
- исправлен разбор секций `Пример N` (вложенные `Ввод:/Вывод:` больше не разрывают пример на верхние секции);
- метаданные шага (`Вид/Difficulty/XP/Language`) читаются как из markdown с `**...**`, так и из plain-формата.

5. Валидация после сборки:
- для каждого практического statement выполняется проверка отсутствия запрещенных секций;
- при нарушении генератор завершает работу с ошибкой.

6. Инструментальная проверка полноты:
- генератор выводит агрегаты (`Modules/Lessons/Blocks/Practice/Tasks/Tests`);
- опциональный debug-режим:

```bash
REPORT_TASK_GAPS=1 node backend/tools/generate_full_course_v4_migration.js
```

- режим показывает практические шаги без `task`-биндинга и причины (например, отсутствие тестов).

7. AI-подсказки:
- backend `POST /api/v1/ai/task-hint` теперь подхватывает авторские подсказки из `tasks.source_policy.hints`;
- подсказка дается по направлению решения и не раскрывает эталонное решение.

Почему сделано именно так:

1. Импорт через полный рендер markdown приводил к утечке служебного контента в ученический интерфейс.
2. Whitelist-подход жестко разделяет зоны видимости и исключает повторение этой категории дефектов.
3. Полный генератор с детерминированной миграцией дает повторяемый импорт и прозрачный аудит изменений в git.
4. Debug-отчет по task gaps позволяет вручную доработать только действительно проблемные шаги, а не перепроверять весь курс вслепую.

## Import reseed hotfix (2026-04-29, v2.50)

1. Добавлена миграция `019_reseed_python_zero_full_v4_import_hotfix.sql`.
2. Назначение `019`:
- повторно применить full-course import после первичного `018`, когда в production уже был зафиксирован старый снимок импорта;
- обновить `statement_md`, `starter_code`, `source_policy.hints`, `task_test_cases` и `lesson_blocks` по текущей whitelist-логике.
3. Почему нужен отдельный номер миграции:
- `schema_migrations` не переисполняет уже примененный файл `018_*`, даже если его содержимое обновили в git;
- отдельный `019` гарантирует, что correction-patch реально дойдёт до уже развернутой БД.

## Cardlink provider block handling hardening (2026-04-30, v2.59)

1. Добавлена явная классификация провайдерской ошибки `api:error.ip_access_denied` в checkout flow:
- backend распознает ответ Cardlink с блокировкой IP;
- платеж в БД фиксируется со статусом `pending_config` (вместо общего `provider_error`);
- API `POST /api/v1/subscription/checkout` возвращает `503` + structured payload:
  - `error: payment provider is not configured`
  - `status: pending_config`
  - `paymentId` (для трассировки и повторной проверки статуса после операционного фикса)
  - `details` с конкретным blocked IP и shop id
  - `missing` с прямым действием для оператора (добавить IP в allowlist).

2. Для `GET /api/v1/subscription/payments/:paymentID` включен retry-флаг для `pending_config`:
- `canRetry = true` для случаев, когда после настройки allowlist нужно повторить checkout без изменения пользовательского сценария.

3. Добавлены unit-тесты:
- разбор Cardlink payload с `ip_access_denied`;
- классификация ошибки в `pending_config` с проверкой наличия IP и Shop ID в диагностике.

Почему сделано именно так:

1. Ошибка `ip_access_denied` является внешней операционной блокировкой провайдера, а не ошибкой бизнес-логики checkout. Нужна отдельная, однозначная ветка, чтобы не терять время на ложный дебаг кода.
2. Статус `pending_config` лучше отражает природу инцидента и позволяет операционно наблюдать «не готово из-за конфигурации провайдера».
3. Явная инструкция в `details/missing` снижает риск повторного запуска без устранения первопричины.

## Production capacity hardening (2026-04-30, v2.60)

1. В process-manager конфиге (`deploy/server/ecosystem.config.cjs`) добавлено горизонтальное масштабирование:
- `API_INSTANCES` (default `2`) для `leonovcare-api` в режиме PM2 `cluster`;
- `WORKER_INSTANCES` (default `4`) для `leonovcare-worker` в многопроцессном режиме.

2. Добавлены эксплуатационные guard-параметры:
- `max_memory_restart` для API/worker процессов;
- `kill_timeout` для корректного завершения и перезапуска.

3. Добавлен безопасный парсер positive integer для env-настроек числа инстансов:
- некорректные значения не валят конфиг;
- используется fallback к дефолту.

Почему сделано именно так:

1. Для целевого запуска на 1500 пользователей single-process конфигурация API/worker даёт лишний риск всплесков latency и очередей.
2. Масштабирование через PM2 позволяет увеличить устойчивость без рефакторинга runtime-кода backend.
3. Memory/timeout guard повышают операционную стабильность при длительной работе под нагрузкой.

## Production process mode correction for Go API (2026-04-30, v2.61)

1. Для `leonovcare-api` режим PM2 скорректирован с `cluster` на `fork` при сохранении `instances`.
2. Причина:
- `cluster`-режим PM2 ориентирован на Node.js cluster runtime;
- для Go binary это вызвало `errored` состояние процессов на production.
3. Текущая рабочая схема:
- API: `fork` + `API_INSTANCES` (default 2);
- Worker: `fork` + `WORKER_INSTANCES` (default 4).

Почему сделано именно так:

1. Многопроцессный `fork` является совместимым и стабильным вариантом масштабирования для Go executables в PM2.
2. Исправление устраняет риск недоступности API при рестартах и сохраняет цель по пропускной способности.

## API instance stabilization for current network layout (2026-04-30, v2.62)

1. Для `leonovcare-api` зафиксирован одиночный инстанс (`instances: 1`) в PM2 ecosystem.
2. Причина:
- backend биндингует один фиксированный порт `HTTP_PORT=8510`;
- несколько `fork`-инстансов на одном порту приводят к аварийному падению лишних процессов.
3. Масштабирование оставлено на worker-слое:
- `WORKER_INSTANCES` (default `4`) безопасно увеличивает throughput обработки submission queue.

Почему сделано именно так:

1. Это устраняет риск частичной недоступности API из-за конфликтов bind на одном порту.
2. Сохраняется практическая польза для запуска на поток учеников за счет параллельной обработки проверок в worker-процессах.

## Production memory safety baseline (2026-04-30, v2.63)

1. На production включен swap:
- `/swapfile_leonovcare` размером `4G`;
- добавлен в `/etc/fstab` для автоподъема после reboot.

2. Применен `vm.swappiness=10`:
- выставлен runtime через `sysctl`;
- зафиксирован в `/etc/sysctl.conf`.

Почему сделано именно так:

1. Без swap (`0B`) сервер уязвим к OOM при кратковременных пиках памяти.
2. Swap-буфер снижает риск аварийного kill процессов API/worker при пиковом окне.

## Cardlink callback URL policy fallback (2026-04-30, v2.64)

1. В `createCardlinkBill` изменена политика формирования URL-параметров:
- `success_url` и `fail_url` теперь передаются в Cardlink **только если явно заданы** в env;
- при пустых env backend не подставляет auto-generated callback URL, а полагается на shop settings Cardlink.

2. `return_url` сохраняет старое поведение:
- параметр отправляется только если задан явно.

Почему сделано именно так:

1. В Cardlink действует ограничение соответствия доменов магазина и callback URL; при принудительной подстановке backend-URL возникал `api:error.url_not_allowed`.
2. Использование callback URL из настроек магазина Cardlink исключает конфликт доменных политик провайдера без ухудшения API-интеграции checkout.

## Migration 020 deployment debt closure (2026-04-30, v2.65)

1. На production подтверждено успешное применение миграций:
- `020_reseed_python_zero_full_v4_sql_checker_and_gap_reduction`;
- `021_tasks_language_include_sql`.

2. Схема language-constraint приведена к рабочему виду:
- `chk_tasks_language` допускает `java`, `python`, `python3`, `py`, `sql`;
- фактическое распределение после применения: `python` + `sql` задачи.

3. После закрытия миграционного блока:
- `AUTO_MIGRATE` возвращен в `true`;
- backend стартует штатно с auto-migrate без аварийных падений.

Почему сделано именно так:

1. Временное отключение `AUTO_MIGRATE=false` использовалось как operational safety gate для восстановления сервиса во время инцидента.
2. После фикса схемы и успешного применения `020/021` режим auto-migrate должен быть возвращен, иначе это оставляет скрытый операционный техдолг перед следующими релизами.

## SQL checker + gap reduction update (2026-04-30, v2.51)

1. Добавлен SQL режим автопроверки в judge (`language=sql`):
- сравнение запроса ученика с эталонным SQL из `solution_code` после нормализации (регистр/пробелы/комментарии/`;`).

2. Импортёр full-course обновлён:
- SQL-практики с эталоном теперь получают задачу и скрытый тест с reference SQL;
- Python-практики без явных тестов, но с эталоном, получают fallback-тест:
  - либо по фактическому stdout эталона,
  - либо source-equivalence (`__SOURCE_EQ__`) для структурных задач.

3. Сгенерирована новая corrective migration:
- `backend/migrations/020_reseed_python_zero_full_v4_sql_checker_and_gap_reduction.sql`
- нужна потому, что `019` уже могла быть применена и не переисполняется.

4. Состояние покрытия после генерации `020`:
- `Practice blocks: 256`
- `Tasks created: 178`
- `Practice blocks without task binding: 78`

5. Почему остаются 78 незабинженных практик:
- в исходном markdown для них отсутствуют и эталон, и автотесты, и однозначный ожидаемый вывод;
- без этих данных корректная автопроверка невозможна без ручной методической доразметки.

## Migration chain hardening for SQL tasks (2026-04-30, v2.64)

1. На production выявлен дефект применения `020_reseed_python_zero_full_v4_sql_checker_and_gap_reduction.sql`:
- при старом constraint `chk_tasks_language` (`java/python`) вставки SQL-задач падали с check violation;
- при `AUTO_MIGRATE=false` дефект не проявлялся автоматически, пока `020` не запускалась вручную.

2. Исправление в репозитории:
- в начало `020` добавлен явный DDL-блок:
  - `ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_tasks_language`;
  - `ADD CONSTRAINT ... CHECK (language IN ('java','python','python3','py','sql'))`;
- в генератор `backend/tools/generate_full_course_v4_migration.js` добавлена та же вставка, чтобы последующие пересборки `020` не теряли фикс;
- добавлена отдельная миграция `021_tasks_language_include_sql.sql` для явной стабилизации схемы.

3. Почему сделано именно так:

1. Это устраняет падение reseed-миграции в окружениях, где constraint ещё не расширен под SQL.
2. Фикс на уровне генератора предотвращает повтор инцидента при следующем regen миграции.
3. Отдельная `021` фиксирует схему как постоянный инвариант и снижает операционные риски при частичных/ручных миграционных сценариях.

## Multi-course v1 import (2026-04-30, v2.70)

1. Добавлен генератор мульти-курсовой миграции:
- `backend/tools/generate_multicourse_v1_migration.js`;
- источники:
  - `C:/Users/Artemy/Downloads/java_course_platform_v1_import.json`
  - `C:/Users/Artemy/Downloads/frontend_course_platform_v1_import.json`
  - `C:/Users/Artemy/Downloads/go_course_platform_v1_import.json`
- результат генерации:
  - `backend/migrations/022_seed_java_frontend_go_v1_catalog_and_sql_practice.sql`.

2. Что импортируется в `022`:
- 3 курса (`java-zero-core`, `frontend-zero`, `go-zero-backend`);
- 15 модулей;
- 355 уроков;
- 11872 lesson blocks (`theory/practice/quiz/project/summary`) с upsert-логикой и идемпотентным переизданием.

3. Политика задач в `022`:
- автопроверяемые `tasks` создаются только для практик с `checker.type='sql_query'` и валидным `solution_code`;
- итог: 404 SQL-задачи + 404 hidden test cases;
- для non-SQL практик блоки и контент сохраняются, но `task_id` не биндуется.

4. Почему сделано именно так:

1. В v1 JSON большинство non-SQL практик используют `checker` типов `ide_plugin` и `http_api` и содержат инструктивные/комментарные `solution_code`, а не исполнимые stdin/stdout тесты для текущего backend judge.
2. Прямой импорт таких шагов как обычных `tasks` приводил бы к ложной автопроверке и технически некорректным verdict.
3. SQL-практики полностью совместимы с текущим `EvaluateSQL`, поэтому выделены в отдельный безопасный и повторяемый путь импорта без потери учебного каталога.

## Python v10 full reseed + checker runtime (2026-04-30, v2.76)

1. Добавлен генератор импорта `v10`:
- `backend/tools/generate_python_v10_migration.js`;
- источник: `C:/Users/Artemy/AppData/Local/Temp/python_course_platform_v10_import.json`.

2. Сгенерирована миграция:
- `backend/migrations/023_reseed_python_zero_v10_polished_full.sql`.

3. Что импортирует `023`:
- курс `python-zero` полностью reseed-ится на контент `v10`;
- 5 модулей, 145 уроков, 1448 lesson blocks;
- 876 задач (`practice + project`) с source_policy checker-данными;
- `tasks.language` стабилизируется на `('java','python','python3','py','sql')`.

4. Runtime проверок backend расширен:
- новый файл: `backend/internal/app/checker_runtime.go`;
- поддержаны checker-типы:
  - `python_stdout`;
  - `python_pytest`;
  - `sql_query`;
  - `http_api`;
  - `ide_plugin`.

5. Сохранена совместимость сабмитов:
- web-формат `sourceCode` работает как раньше;
- добавлен bundle-формат `__LC_BUNDLE_V1__` для file-based project checks из IDE.

6. Quiz без утечки правильных ответов:
- `GET /lessons/:lessonId` очищает `correctOptionId` из quiz payload;
- добавлен endpoint `POST /lessons/:lessonId/quiz-check` для серверной проверки.

7. Зачем сделано именно так:

1. `v10` поставляется как structured import с разделением student-visible и hidden checker-логики; перенос checker в `source_policy` обязателен для корректной безопасности контента.
2. Project-уроки требуют проверки файлов/команд, а не только stdin/stdout, поэтому нужен bundle-submit и `ide_plugin` runtime.
3. Серверная проверка quiz устраняет прямую утечку правильного варианта в клиентский payload.
4. Reseed миграцией обеспечивает идемпотентный production rollout через стандартный migration-chain.

8. Автовалидация импорта:
- `backend/tools/validate_python_v10_import.js`;
- отчет: `docs/operations/PYTHON_V10_IMPORT_VALIDATION_2026_04_30.md`;
- статус: PASS.

## Актуализация от 2026-05-02: тема и пользовательские настройки

1. Web UI больше не показывает экран `/settings`; это изменение относится к frontend-навигации, но backend должен сохранять совместимость с прежним API.
2. Поле `user_settings.theme` остаётся в таблице, потому что оно уже есть в production-схеме и входит в контракт `GET /me`.
3. Текущее поведение backend:
- `GET /me` всегда отдаёт `theme: "light"`;
- `PATCH /me/settings` принимает старый payload, но нормализует `theme` в `light`;
- migration `024_light_theme_only.sql` меняет default и все старые значения на `light`.
4. Почему не удаляем поле из БД:
- удаление колонки увеличило бы риск для старых клиентов и исторических данных;
- compatibility layer дешевле и безопаснее;
- продуктовая цель достигнута на UI-слое: ученик больше не видит настройки и не может включить dark-mode.
## Python v18 first 10 pedagogy reseed — 2026-05-03

Backend теперь содержит новую миграцию курса:

1. `migrations/027_reseed_python_zero_v18_first10_pedagogy.sql`

Она создана после педагогической правки первых 10 уроков пакета `материалы/v18_STRICT_PEDAGOGY`. Миграция `026` остаётся в истории и не редактируется, потому что production уже мог записать её в `schema_migrations`.

Что проверяет актуальный validator:

1. количество blocks/tasks/testcases в SQL совпадает с `course_import.json`;
2. `python_pytest.test_code` преобразуется в runtime key `pytest_code`;
3. `http_api.public_tests/hidden_tests` преобразуются в runtime `tests[]`;
4. quiz blocks содержат structured `questions[]`;
5. первый урок курса остаётся `Первый код`;
6. первые 10 уроков имеют подробную теорию, примеры и не используют будущие темы в student-facing полях.

Команды:

```bash
node backend/tools/generate_python_v18_materials_migration.js
node backend/tools/validate_python_v18_materials_import.js
```

Почему это нужно: backend import layer должен защищать production от ситуации, когда JSON формально валиден, но runtime-миграция не соответствует фактическому содержанию курса.
