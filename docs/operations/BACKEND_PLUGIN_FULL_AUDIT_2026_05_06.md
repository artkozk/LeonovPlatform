# Backend + IDEA Plugin Full Audit Report (2026-05-06)

## 1. Цель и границы аудита

1. Проверить backend-контур (API, auth, submission queue, checker runtime, AI endpoint, стабильность worker-процесса).
2. Проверить IDEA plugin-контур (загрузка курсов/уроков/материалов, открытие задач, отправка решений, отображение theory/lesson blocks, AI hint flow).
3. Найти архитектурные пробелы, исправить критичные и high-impact дефекты, зафиксировать изменения в коде и тестах.

## 2. Что было запущено в рамках проверки

### 2.1 Backend

1. `go test ./...` — PASS.
2. `go vet ./...` — PASS.
3. `go test -race ./...`:
- не выполнен в текущем окружении, потому что отсутствует `gcc` для CGO (`cgo: C compiler "gcc" not found`).

### 2.2 IDEA plugin

1. `./gradlew.bat check --console=plain` — PASS.
2. `./gradlew.bat test --console=plain` — PASS после фикса тестового импорта.

## 3. Найденные архитектурные и security-пробелы

### 3.1 Auth middleware fail-open при проблеме чтения пользователя (исправлено)

1. Что было:
- `authMiddleware` после валидации JWT допускал запрос дальше даже если чтение `users/subscriptions` падало или не находило пользователя.
- Фактически это был fail-open путь: при ошибке БД контекст плана выставлялся в `free`, запрос не блокировался.

2. Что сделано:
- В `backend/internal/app/middleware.go` добавлена строгая обработка:
  - `pgx.ErrNoRows` -> `401 invalid access token`;
  - прочие ошибки чтения контекста пользователя -> `500 failed to resolve user context`;
  - только при успешном чтении пользователь проходит дальше.

3. Почему это обязательно:
- middleware авторизации не должен работать в режиме "пропусти при ошибке";
- иначе JWT с невалидным user-state может получить доступ к защищенным endpoint'ам.

### 3.2 Риск раздувания Redis-очереди через reconciler-дубли (исправлено)

1. Что было:
- reconciler периодически requeue-ил `queued` submissions без проверки наличия payload в `main`/`processing` очередях;
- при деградации worker или длинной обработке могли копиться дубли payload одного submission.

2. Что сделано:
- В `backend/internal/app/worker.go`:
  - reconciler теперь получает и `mainQueue`, и `processingQueue`;
  - перед `RPUSH` проверяет наличие payload в обеих очередях (`LPos`);
  - если payload уже есть, повторно не добавляет.

3. Почему это обязательно:
- снижает риск неограниченного роста очереди и паразитной нагрузки на Redis/worker;
- уменьшает хвост повторных попыток и шум в логах.

### 3.3 IDE checker command hardening для production-пути (исправлено)

1. Что было:
- фильтр опасных shell-токенов не блокировал одиночные `&` и общий `|`;
- на Windows `cmd /C` трактует `&` как separator команд, что создавало инъекционный путь в policy-командах.

2. Что сделано:
- В `backend/internal/app/checker_runtime.go` расширен blacklist токенов:
  - добавлены `&`, `|`, `>`, `<` и др.
- Сохранен отдельный безопасный путь для `printf ... | python ...` через `isSafePrintfPipeToPython`.

3. Почему это обязательно:
- устраняется возможность выполнения цепочки произвольных команд через task policy в production.

### 3.4 Неполная валидация file path для checker workspace на volume-path (исправлено)

1. Что было:
- `normalizePathForWorkspace` не блокировал пути с volume prefix (`C:/...`);
- это создавало кросс-платформенный риск выхода за workspace на Windows-сценариях.

2. Что сделано:
- В `backend/internal/app/checker_runtime.go` добавлена проверка `filepath.VolumeName(cleaned)`.
- Путь с volume now отклоняется как `absolute volume path is not allowed`.

3. Почему это обязательно:
- гарантирует единый запрет абсолютных путей и volume путей в sandbox workspace.

### 3.5 Отображение материалов урока в plugin UI было неполным (исправлено)

1. Что было:
- в `TaskStatementPanel` показывался в основном task statement;
- lesson theory/blocks не были гарантированно включены в итоговый текст текущей задачи.

2. Что сделано:
- В `idea-plugin/src/main/kotlin/com/leonovcare/plugin/task/LessonMaterialFormatter.kt`:
  - `buildTaskAndLessonText` теперь собирает полноценный markdown:
    - lesson markdown (`Теория` + `Шаги урока`);
    - отдельный раздел `Практическое задание` с названием задачи;
    - список обязательных требований из `TaskStatement.requirements`.

3. Почему это обязательно:
- пользователь в plugin получает весь учебный контекст урока, а не только финальный statement;
- это снижает переключения между IDE и веб-UI и закрывает пробел "материалы видны частично".

## 4. Добавленные regression-тесты

### 4.1 Backend

1. `backend/internal/app/checker_runtime_test.go`:
- проверка, что `python main.py & whoami` блокируется;
- проверка, что произвольный pipe `python main.py | cat` блокируется;
- проверка, что volume path (`C:/...`) отклоняется.

### 4.2 IDEA plugin

1. Новый тест `idea-plugin/src/test/kotlin/com/leonovcare/plugin/task/LessonMaterialFormatterTest.kt`:
- подтверждает, что итоговый текст содержит:
  - lesson title/theory/steps;
  - раздел `Практическое задание`;
  - секцию требований.
- отдельная проверка сценария без lesson (fallback на task section).

## 5. Прохождение ключевых сценариев после исправлений

1. Auth + protected API:
- неконсистентный user context теперь блокируется корректно (no fail-open).
2. Submission worker:
- reconciler не создает лишние дубли payload при повторных циклах.
3. Checker security:
- command separator/pipe injection path закрыт для production allowlist режима.
4. Lesson material UX:
- теория и шаги урока гарантированно доходят до plugin panel вместе с задачей.
5. AI hint flow:
- контракт и endpoint рабочие, тесты backend/plugin зелёные.

## 6. Изменённые файлы

1. `backend/internal/app/middleware.go`
2. `backend/internal/app/worker.go`
3. `backend/internal/app/checker_runtime.go`
4. `backend/internal/app/checker_runtime_test.go`
5. `idea-plugin/src/main/kotlin/com/leonovcare/plugin/task/LessonMaterialFormatter.kt`
6. `idea-plugin/src/test/kotlin/com/leonovcare/plugin/task/LessonMaterialFormatterTest.kt`

## 7. Ограничения текущей проверки

1. `go test -race` не запущен из-за отсутствия `gcc` в текущем окружении.
2. Полный визуальный ручной smoke внутри IDE (interactive PyCharm session) не автоматизируется этим CI-runner, но кодовые и API-контрактные проверки выполнены.

## 8. Вывод

1. Критичные security/architecture пробелы по auth fail-open, queue duplication и checker command/path hardening закрыты.
2. UX-дефект отображения учебных материалов в plugin закрыт.
3. Автотесты backend и plugin проходят, изменения документированы и готовы к deploy-процедуре.

## 9. Additional hardening pass (2026-05-06, phase 2)

### 9.1 JWT signing policy hardening

1. Что было:
- `ParseToken` принимал любой HMAC-алгоритм из заголовка токена.
2. Что сделано:
- в `backend/internal/security/jwt.go` добавлена строгая проверка `HS256` перед валидацией подписи.
3. Почему это важно:
- исключает algorithm-downgrade/agility и фиксирует единый ожидаемый signing policy.
4. Тест:
- `TestParseTokenRejectsUnexpectedSigningMethod` в `backend/internal/security/jwt_test.go`.

### 9.2 Auth input normalization hardening

1. Что было:
- login/forgot-password не использовали единую нормализацию email с trim.
2. Что сделано:
- введен `normalizeEmail(...)`;
- применен в `Register`, `Login`, `ForgotPassword`.
3. Почему это важно:
- убирает edge-case ошибки из-за пробелов и повышает предсказуемость auth-flow.
4. Тест:
- `TestNormalizeEmailTrimsAndLowercases` в `backend/internal/app/handlers_auth_test.go`.

### 9.3 Security defaults against unsafe numeric env overrides

1. Что было:
- отрицательные/нулевые значения env могли отключать ограничения (например body limits и rate limits).
2. Что сделано:
- в `backend/internal/config/config.go` добавен `applySecurityDefaults(...)` с клампом security-критичных параметров.
3. Почему это важно:
- защищает production от случайной или некорректной конфигурации, которая ослабляет защитные лимиты.
4. Тест:
- `TestLoad_ClampsSecurityCriticalNumericConfig` в `backend/internal/config/config_test.go`.

### 9.4 Verification status

1. `go test ./...` — PASS.
2. `go vet ./...` — PASS.
3. `idea-plugin ./gradlew.bat test --console=plain` — PASS.

## 10. Login/API fan-out optimization pass (2026-05-06, phase 3)

### 10.1 Problem statement

1. В UI мог наблюдаться шум из повторных одинаковых GET-запросов при быстром mount/remount (включая dev StrictMode) и при переходах после логина.
2. Это не всегда означает backend-bug, но создает лишнюю нагрузку и визуально выглядит как “шторм запросов”.

### 10.2 What was changed

1. В `frontend/src/api/client.ts` добавлен централизованный слой:
- in-flight deduplication для одинаковых GET (`inFlightGet`);
- короткий TTL-кэш для read endpoints (`readCache`) с управляемыми TTL.
2. Кэш применяется только к idempotent-read endpoint’ам (`/me`, `/courses`, `/courses/:id`, `/lessons/:id`, `/tasks/:id`, `/me/submission-history`, `/leaderboard`, `/plans`, `/subscription`, `admin metrics` и т.д.).
3. Для polling endpoint’а `/submissions/:submissionID` кэш **не включался**, чтобы не ломать live-статус проверки.
4. При `saveTokens` и `clearTokens` read-кэш очищается принудительно, чтобы исключить stale-данные между сессиями/пользователями.
5. В `frontend/src/store/auth.ts` добавлена дедупликация `bootstrap` через `bootstrapPromise`, чтобы повторный вызов `apiMe` не раздувал сетевой трафик.

### 10.3 Why it is implemented this way

1. Dedupe + TTL дают эффект сразу на всех экранах без переписывания каждого компонента.
2. Это снижает нагрузку на backend и убирает “ложные” пики в DevTools без изменения бизнес-логики.
3. Разделение на cacheable-read и non-cacheable-polling сохраняет корректность статусов задач и очередей.

### 10.4 Verification

1. `frontend npm.cmd test` — PASS.
2. `frontend npm.cmd run build` — PASS.

## 11. Plugin statement panel hotfix (2026-05-06, phase 4)

### 11.1 Observed production symptom

1. В tool window список задач загружался, но правая панель материалов оставалась визуально пустой.
2. При открытии шагов возникали ошибки загрузки из-за конкуренции с фоновым prefetch и короткого сетевого таймаута.

### 11.2 Root causes

1. Агрессивный prefetch lesson-material выполнялся на большой выборке уроков (до 120 за refresh), что создавало лишние параллельные запросы и повышало риск таймаутов на открытии задачи.
2. Для HTML-рендера statement panel не был зафиксирован контрастный foreground/background стиль; при темной теме содержимое могло быть практически невидимым.
3. При ошибке `openTask` UI показывал notification, но не заполнял правую панель явным текстом ошибки.

### 11.3 Implemented fix

1. В `idea-plugin/src/main/kotlin/com/leonovcare/plugin/task/TaskManager.kt`:
- `requestTimeoutMillis` увеличен до `12s`;
- `maxLessonPrefetchPerRefresh` снижен до `24`;
- prefetch ограничен только задачами выбранного курса + startup lesson, вместо fan-out по всем курсам.
2. В `idea-plugin/src/main/kotlin/com/leonovcare/plugin/ui/TaskStatementPanel.kt`:
- добавлены theme-aware foreground/background для `JEditorPane`;
- добавлены состояния `showLoading(...)` и `showError(...)`.
3. В `idea-plugin/src/main/kotlin/com/leonovcare/plugin/ui/MarkdownHtmlRenderer.kt`:
- HTML шаблон получает явные `color` и `background-color`.
4. В `idea-plugin/src/main/kotlin/com/leonovcare/plugin/ui/PlatformToolWindowPanel.kt`:
- при выборе задачи сразу показывается loading-состояние;
- при ошибке открытия задачи правая панель заполняется явным error-текстом.

### 11.4 Verification

1. `idea-plugin ./gradlew.bat test --console=plain` — PASS.

## 12. Plugin/backend request-storm and blank-materials stabilization (2026-05-06, phase 5)

### 12.1 Observed production symptom

1. После логина и открытия задач плагин отправлял повторные серии запросов:
- дубли `GET /api/v1/tasks/:taskID`;
- дубли `GET /api/v1/tasks/:taskID/template`;
- цепочки `POST /api/v1/tasks/:taskID/progress/*` с постоянным `404`.
2. В результате правая панель могла долго оставаться в состоянии загрузки/пустой зоны, а в логах IDE и backend появлялся выраженный шум.

### 12.2 Root cause analysis

1. `TaskManager.openTask` выполнял `markTaskInProgress(...)` **до** вызова `onOpened(...)`, поэтому UI-обновление задерживалось на сетевой хвост.
2. Плагин не отсеивал конкурентные дубли открытия одной и той же задачи.
3. `HttpPlatformApiClient.markTaskInProgress` пробовал fallback-цепочку endpoint-ов при каждом вызове и при `404` не отключал probing.
4. `PlatformApiClientFactory` создавал новый `HttpPlatformApiClient` на каждый вызов, поэтому capability-cache не мог сохраняться между операциями.
5. На backend отсутствовал endpoint `POST /tasks/:taskID/progress/in-progress`, поэтому client fallback неизбежно попадал в `404`.

### 12.3 Implemented fix

1. `idea-plugin/src/main/kotlin/com/leonovcare/plugin/task/TaskManager.kt`:
- добавлена дедупликация `openTask` по `taskId` (concurrent in-flight guard);
- если задача уже открыта и overwrite не нужен, используется текущий context без повторного network/file цикла;
- `onOpened(context)` вызывается до `markTaskInProgress`, чтобы UI показывал материалы сразу;
- `markTaskInProgress` запускается только для `NEW` задач и не блокирует показ контента.
2. `idea-plugin/src/main/kotlin/com/leonovcare/plugin/api/HttpPlatformApiClient.kt`:
- добавлен discovery-cache рабочего progress endpoint;
- при полном `404/405/501` по всем кандидатам probing отключается для сессии клиента;
- повторные вызовы не шлют лишние fallback-запросы.
3. `idea-plugin/src/main/kotlin/com/leonovcare/plugin/api/PlatformApiClientFactory.kt`:
- фабрика переиспользует один `HttpPlatformApiClient` на текущий `apiBaseUrl`, чтобы capability-cache и HTTP connection reuse реально работали.
4. Backend:
- добавлен endpoint `POST /api/v1/tasks/:taskID/progress/in-progress`;
- endpoint записывает факт открытия задачи в `user_task_open_progress`;
- `GetPluginBootstrap` и `GetCourseTasksCatalog` учитывают `user_task_open_progress` вместе с submissions при вычислении статуса `IN_PROGRESS`;
- `ResetTaskProgress` очищает и submissions, и open-progress запись;
- добавлена миграция `backend/migrations/034_plugin_task_open_progress.sql`;
- в `App.New` активирован auto-migrate путь через `internal/db.ApplyMigrations(...)` (используется advisory lock), чтобы новые миграции гарантированно применялись при старте.

### 12.4 Why this architecture

1. Сдвиг `onOpened` перед progress-mark убирает UI latency без изменения бизнес-логики.
2. Дедупликация по `taskId` устраняет конкурентные двойные открытия и уменьшает нагрузку на backend и файловую подсистему IDE.
3. Capability-cache + singleton client дают предсказуемое поведение: либо один рабочий endpoint, либо controlled disable, без постоянного 404 probing.
4. Backend endpoint и отдельная таблица open-progress дают наблюдаемую и восстанавливаемую модель статуса `IN_PROGRESS` до первой отправки решения.
5. Автомиграции при старте устраняют риск частичного деплоя схемы при обновлении runtime.

### 12.5 Verification

1. IDE plugin unit-tests: `idea-plugin ./gradlew.bat test --console=plain`.
2. IDE plugin artifact build: `idea-plugin ./gradlew.bat clean buildPlugin --console=plain`.
3. Backend tests: `backend go test ./...`.
4. Server runtime smoke:
- `GET /healthz` -> `200`;
- `GET /readyz` -> `200`;
- повторные открытия задач не должны генерировать fallback-шторм `progress/*` с `404`.
