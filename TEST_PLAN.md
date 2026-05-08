# Leonov Care Platform — Test Plan (Launch)

## 1. Цель

Определить набор проверок для релиза платформы в production-профиле перед запуском когорты ~200 учеников.

## 2. Контур тестирования

1. Backend unit/integration (`go test ./...`).
2. Frontend unit (`vitest`).
3. Frontend production build (`vite build`).
4. Smoke-сценарий API.
5. Ручная E2E проверка ключевых пользовательских сценариев.

## 3. Матрица проверок

### 3.1 Auth

1. Регистрация:
- успешная регистрация с `firstName`, `lastName`, `nickname`, `email`, `password`.
- ошибка при дублирующем `nickname`.
- ошибка при дублирующем `email`.
- успешная регистрация с кириллическим `nickname` (`Иван Петров` -> `иван_петров`), потому что текущий русскоязычный UI не должен требовать латинский алиас.
- ошибка при `nickname`, который после нормализации короче 3 символов; это защищает БД от мусорных значений вроде `a..`.

2. Логин:
- успешный вход по email/password.
- ошибка `401` при неверном пароле.

3. Refresh:
- успешная ротация access/refresh.
- отказ при просроченном refresh.

### 3.1.1 Auth hotfix regression (2026-05-02)

1. Проверить backend unit:
- `go test ./internal/app -run TestNormalizeNickname`
- ожидаемый результат: кириллица сохраняется, Latin-flow не ломается, длина режется по rune, а не по byte.

2. Проверить production smoke:
- `POST /api/v1/auth/register` с `nickname="Иван Петров"`;
- ожидаемый результат: `201 Created`, токены в `tokens.accessToken/tokens.refreshToken`;
- далее `GET /api/v1/me` должен вернуть `nickname="иван_петров"` или уникальное значение, если такой ник уже занят.

Почему это добавлено:

1. До исправления backend удалял все не-latin символы из nickname, и обычный русский ник превращался в пустую строку.
2. Для пользователя ошибка выглядела как неработающая регистрация, хотя email/password были корректны.
3. Регресс-тест нужен именно на нормализацию, потому что регистрационный контракт зависит от неё до записи в `users`.

### 3.2 Profile

1. `GET /me` возвращает:
- `publicId`;
- `nickname`;
- `firstName`;
- `lastName`.

2. `PATCH /me/settings` обновляет пользовательские настройки editor/theme.

### 3.3 Learning + Queue

1. Создание submission:
- статус `queued`.

2. Worker обработка:
- переход в `processing`, затем в финальный статус.

3. Retry logic:
- искусственно вызвать ошибку judge;
- убедиться, что `processing_attempts` увеличивается;
- после лимита статус `failed`.

### 3.4 Billing

1. Checkout:
- `pending_config` при неполном Cardlink конфиге.

2. Webhook security:
- `401` при неверном `X-Cardlink-Token`;
- `401` при неверной `X-Cardlink-Signature` (если `CARDLINK_REQUIRE_SIGNATURE=true`).

3. Webhook idempotency:
- повторный `paid` не создает дублирующие активные подписки.

### 3.5 Frontend UX

1. Auth page:
- отсутствуют Google/GitHub кнопки.
- доступны только нужные пользователю поля.

2. Settings:
- отображается `publicId`.

3. Courses:
- нет искусственных locked/completed статусов без фактических данных.

4. Dashboard:
- нет фиксированной синтетической «общей статистики» достижений.

### 3.6 Актуализация от 2026-05-02: Settings удалён, UI только светлый

1. Frontend navigation:
- в profile-menu нет пункта `Настройки`;
- на `/profile` нет карточки перехода в настройки;
- прямой переход на `/settings` попадает под wildcard router и возвращает пользователя на `/dashboard`.
2. Theme:
- `workspace-shell` не содержит `data-theme="dark"`;
- в собранном CSS нет активного блока `[data-theme="dark"]`;
- редактор Monaco на страницах урока и задачи получает только `theme="light"`.
3. Backend compatibility:
- `GET /me` возвращает `theme: "light"`;
- `PATCH /me/settings` может остаться для legacy-клиентов, но любое значение `theme` должно сохраняться как `light`;
- миграция `024_light_theme_only.sql` меняет default и существующие строки `user_settings.theme` на `light`.
4. Почему это проверяется отдельно:
- функциональность настроек удалена из UI намеренно, поэтому отсутствие ссылок является ожидаемым результатом, а не регрессией;
- dark-mode был снят из продукта, поэтому любые новые зависимости от `user.theme === "dark"` должны считаться ошибкой.

## 4. Минимальный набор команд

1. Frontend:
```bash
cd frontend
npm ci
npm run test
npm run build
```

2. Backend:
```bash
cd backend
go mod tidy
go test ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker
```

3. Smoke:
```bash
cd tests
bash smoke.sh
```

## 5. Критерии приемки релиза

1. Все автоматические тесты green.
2. Нет утечки demo токенов в API при `EXPOSE_DEMO_TOKENS=false`.
3. В production UI нет OAuth входа.
4. Launch migration применена без ошибок.
5. Health endpoints и PM2 процессы стабильны после деплоя.

## 6. Риски

1. Отсутствие docker в production при `JUDGE_MODE=docker`.
2. Неправильно заданные runtime secrets.
3. Миграции на уже заполненной БД без backup.

## 7. UI regression-check: Monaco caret/overlay alignment (добавлено 2026-05-04)

### 7.1 Что проверяем

1. Отсутствие смещения каретки в Monaco:
- каретка должна отображаться строго между символами, а не внутри символа;
- на строках с `"` и `()` каретка не должна визуально «заезжать» на глиф.

2. Отсутствие смещения полупрозрачных overlay-слоёв:
- подсветка парных скобок должна покрывать только целевой символ;
- подсветка не должна перекрывать соседние символы на 1+ позицию.

3. Поведение после UI-изменений:
- после любых изменений шрифтов, typography-токенов, CSS reset, `text-rendering`, `letter-spacing`, layout-контейнеров редактора и визуальных тем нужно подтвердить, что смещение не вернулось.

### 7.2 Когда проверяем

1. После каждого изменения интерфейса, которое потенциально влияет на текстовые метрики или контейнер редактора.
2. Перед каждым production deploy, если в релизе есть правки в `frontend/src/styles/*`, `TaskPage`, `LessonPage`, подключении шрифтов или Monaco options.

### 7.3 Как проверяем (ручной smoke)

1. Открыть страницу с редактором задачи (`/tasks/:taskId`).
2. Ввести в первой строке:
- `print("")`
- `print("()")`
3. Клавишами стрелок поставить каретку:
- между `"` и `"`;
- перед `)` и после `)`;
- между `(` и `)`.
4. Визуально подтвердить:
- каретка в корректной позиции;
- подсветка парных скобок не смещена.
5. Повторить пункты 1–4 на странице урока (`/lessons/:lessonId`) в practice-блоке.

### 7.4 Критерий PASS/FAIL

1. PASS: каретка и overlay-слои Monaco совпадают с фактическими позициями символов на `TaskPage` и `LessonPage`.
2. FAIL: каретка рисуется внутри символа или bracket overlay наезжает на соседние символы; релиз в production не выпускать до исправления.

### 7.5 Почему это обязательно

1. Дефект не ломает backend, но напрямую ломает базовый UX ввода кода и восприятие результата пользователем.
2. Регресс может возвращаться после «безобидных» UI-правок (шрифты/рендеринг/spacing), поэтому проверка должна быть системной и повторяемой.

## 8. P0/P1/P2 hardening gate (append-only, 2026-05-05)

### 8.1 Как было

1. Нагрузочный путь материалов включал N+1-запросы (`getLesson` fanout на страницы курсов/задач).
2. Не было обязательного runtime-gate по `readyz`.
3. Refresh-токен мог использоваться повторно после refresh (без one-time rotation).

### 8.2 Как стало

1. `CoursesPage` использует `GET /courses/:courseID` с `lessons[].blockCount` без массового `getLesson`.
2. `TasksPage` использует `GET /courses/:courseID/tasks-catalog` вместо `Promise.allSettled(getLesson[])`.
3. Добавлен `GET /readyz` как обязательная проверка перед traffic switch.
4. Refresh-токен: one-time rotation + revoke старого токена.
5. `reset-password` и `block_user` делают массовый revoke refresh-токенов пользователя.
6. 5xx-ответы возвращают безопасный envelope с `requestId`, без внутреннего stack/db текста.

### 8.3 Почему это важно

1. Это напрямую закрывает главную жалобу по «долгой работе с материалами» за счет сокращения количества запросов и объема данных.
2. One-time refresh и revoke закрывают класс атак повторного использования refresh-токенов.
3. Без `readyz` orchestrator может отправлять трафик на инстанс без готовых зависимостей.

### 8.4 Обязательные проверки перед релизом

1. Backend unit:
```bash
cd backend
go test ./internal/judge -run "TestSQLEngineEvaluate|TestDockerModeFailsClosedWhenDockerUnavailable"
go test ./internal/app -run "TestEvaluateTaskByPolicyRejectsSourcePolicyViolation|TestIDECheckerCommandAllowedInProduction"
```

2. Backend full test + build:
```bash
cd backend
go test ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker
go build -o bin/leonovcare-migrator ./cmd/migrator
```

3. Frontend regression (ключевая проверка на отсутствие N+1):
- `CoursesPage`: только `listCourses + getCourse`, без массовых `getLesson`.
- `TasksPage`: `getCourse + tasks-catalog`, без `Promise.allSettled(getLesson[])`.

4. API smoke:
```bash
curl -fsS http://127.0.0.1:8510/readyz
curl -fsS -H "Authorization: Bearer <token>" http://127.0.0.1:8510/api/v1/courses/<course-id>
curl -fsS -H "Authorization: Bearer <token>" http://127.0.0.1:8510/api/v1/courses/<course-id>/tasks-catalog
```

5. Performance gate (обязательный):
- SLA: `P95 < 2s` для открытия `CoursesPage`, `TasksPage`, `LessonPage` на актуальном объеме контента и нормальной сети.
- Релиз блокируется при нарушении SLA.

### 8.5 Дополнение по очереди сабмитов

1. Проверить, что после рестарта worker незавершенные payload остаются в `processing` и не теряются.
2. Проверить, что requeue происходит при recoverable error и ограничивается `SUBMISSION_MAX_ATTEMPTS`.
3. Проверить, что reconciler поднимает зависшие `queued` записи обратно в Redis main queue.

## 9. Backend + IDEA plugin full audit regression gate (append-only, 2026-05-06)

### 9.1 Auth fail-closed regression

1. Проверить, что protected endpoint не пропускает запрос при неконсистентном user context:
- если пользователь не найден по `claims.UserID`, middleware должен вернуть `401`, а не продолжать запрос.
2. Проверить, что при DB-ошибке чтения user context middleware возвращает `500`, а не `free`-fallback.

### 9.2 Submission queue anti-duplication regression

1. Для `queued` submissions reconciler не должен безусловно добавлять payload повторно в Redis.
2. Перед `RPUSH` должна выполняться проверка присутствия payload в:
- `mainQueue`;
- `processingQueue`.
3. Критерий PASS: при повторных циклах reconciler объем очереди не растет за счет дубликатов одного и того же `submissionId`.

### 9.3 Checker command/path hardening regression

1. Unit checks (backend):
```bash
cd backend
go test ./internal/app -run "TestIDECheckerCommandAllowedInProductionDefaultSafeSet|TestNormalizePathForWorkspaceRejectsAbsoluteVolumePath"
```
2. Ожидаемое:
- `python main.py & whoami` блокируется;
- `python main.py | cat` блокируется;
- volume path (`C:/...`) отклоняется.

### 9.4 IDEA plugin lesson material rendering regression

1. Unit checks (plugin):
```bash
cd idea-plugin
./gradlew.bat test --console=plain
```
2. Проверка по `LessonMaterialFormatterTest`:
- итоговый markdown содержит lesson theory + lesson blocks;
- содержит отдельный раздел `Практическое задание`;
- fallback без lesson не ломает отображение statement.

### 9.5 Full command set после изменений

1. Backend:
```bash
cd backend
go test ./...
go vet ./...
```
2. IDEA plugin:
```bash
cd idea-plugin
./gradlew.bat check --console=plain
./gradlew.bat test --console=plain
```
3. Примечание:
- `go test -race` в текущем Windows-окружении требует `gcc` для CGO; без него шаг считается environment-blocked и фиксируется в release notes.

## 10. Hardening phase 2 regression gate (append-only, 2026-05-06)

### 10.1 JWT signing method policy

1. Проверка:
```bash
cd backend
go test ./internal/security -run TestParseTokenRejectsUnexpectedSigningMethod
```
2. Ожидаемое:
- токен с `HS512` (или другим отличным от `HS256`) отвергается.

### 10.2 Auth email normalization

1. Проверка:
```bash
cd backend
go test ./internal/app -run TestNormalizeEmailTrimsAndLowercases
```
2. Ожидаемое:
- e-mail нормализуется в `trim + lowercase` и используется единообразно в auth endpoint’ах.

### 10.3 Unsafe env numeric overrides

1. Проверка:
```bash
cd backend
go test ./internal/config -run TestLoad_ClampsSecurityCriticalNumericConfig
```
2. Ожидаемое:
- отрицательные/нулевые значения security-критичных параметров не отключают ограничения, а клампятся на безопасные defaults.

## 11. Full remediation release gate (append-only, 2026-05-08)

### 11.1 Backend quality gate

1. Обязательные команды:
```bash
cd backend
go test ./...
go vet ./...
go build -o bin/leonovcare-api ./cmd/server
go build -o bin/leonovcare-worker ./cmd/worker
go build -o bin/leonovcare-migrator ./cmd/migrator
```
2. Критерий PASS:
- тесты green;
- `vet` без ошибок;
- все три бинаря успешно собраны.

### 11.2 Frontend quality gate

1. Обязательные команды:
```bash
cd frontend
npm ci
npm run test
npm run lint
npm run build
npm audit
```
2. Критерий PASS:
- `npm audit` без `high/critical`;
- moderate уязвимости закрыты обновлением зависимостей или явно зафиксированы как upstream-blocked риск.

### 11.3 IDEA plugin quality gate

1. Обязательные команды:
```bash
cd idea-plugin
./gradlew.bat test --console=plain
./gradlew.bat buildPlugin --console=plain
```
2. Критерий PASS:
- тесты и сборка plugin-artifact проходят без ошибок.

### 11.4 Обновлённый smoke-контракт после деплоя

1. Обязательная цепочка:
- `register(firstName,lastName,nickname,email,password)`
- `login` и получение access token
- `GET /courses`
- `GET /courses/:courseID/tasks-catalog`
- `POST /tasks/:taskID/submissions`

2. Технический smoke-скрипт:
- `tests/smoke.sh` синхронизирован с текущим auth-контрактом (без legacy `username`).

3. Критерий PASS:
- каждый шаг цепочки возвращает ожидаемый success-статус;
- submit возвращает `submissionId` и не падает на контрактной ошибке.

### 11.5 Production post-release gate

1. Обязательные проверки:
```bash
curl -fsS http://127.0.0.1:8510/healthz
curl -fsS http://127.0.0.1:8510/readyz
pm2 status --no-color
redis-cli LLEN submission_jobs
redis-cli LLEN submission_jobs_processing
```
2. Критерий PASS:
- процессы LeonovCare online и без restart-loop;
- `healthz=200`, `readyz=200`;
- очередь Redis не уходит в неограниченный рост.
