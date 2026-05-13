# Critical Platform Similar Bugs Audit (2026-05-13)

## 1. Цель

1. Проверить платформу на наличие **аналогичных критичных багов** того же класса:
- рассинхрон источников истины;
- неверная state-machine обработки статусов;
- ложное отображение прогресса/статусов;
- разрушение прогресса из-за auth lifecycle.
2. Исправления кода в этом цикле не вносились. Выполнен только root-cause аудит.

## 2. Подтверждённые критичные баги

### 2.1 Lesson submission polling обрывается на `processing`

1. `LessonPage` прекращает polling, когда статус не `queued`:
- [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:869).
2. Worker штатно переводит submission в `processing` до финального результата:
- [worker.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\worker.go:251).
3. Последствие:
- финальный `accepted` может прийти после остановки polling;
- `markBlockCompleted` не вызывается;
- шаг/галочка/процент остаются в ложном состоянии.

### 2.2 Контракт квизов `minScorePercent` не реализован

1. В контенте курса массово используется `minScorePercent` (на момент аудита: `3021` вхождение по миграциям).
2. В модели проверки квиза backend поле порога не парсится:
- [quiz_handlers.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\quiz_handlers.go:26).
3. Логика проверки жёстко требует отсутствие любых `failedQuestionIds`:
- [quiz_handlers.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\quiz_handlers.go:150).
4. Последствие:
- фактическое правило прохождения квиза расходится с педагогическим контрактом материалов;
- платформа системно показывает другой критерий успеха, чем задан в контенте.

### 2.3 Tasks page игнорирует серверный статус и строит состояние из урезанной истории

1. Backend `tasks-catalog` рассчитывает и возвращает `status` на каждую задачу (SOLVED/IN_PROGRESS/NEW):
- [handlers_learning.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_learning.go:504),
- [handlers_learning.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_learning.go:537).
2. Frontend в `TasksPage` не использует это поле и пересобирает статус из `submissionHistory`:
- [TasksPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\TasksPage.tsx:133),
- [TasksPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\TasksPage.tsx:182).
3. `submissionHistory` на backend ограничен `LIMIT 100`:
- [handlers_learning.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_learning.go:1172).
4. Последствие:
- при росте числа задач статусы на `TasksPage` становятся неполными/ложными;
- реальные solved/in-progress задачи могут отображаться как `idle`.

### 2.4 Dashboard подменяет факт фиктивным прогрессом при ошибках данных

1. В fallback-карточке захардкожены не-нулевые значения прогресса (`20/25`, `80%`):
- [DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:54),
- [DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:56).
2. Fallback используется при отсутствии/ошибке course/lesson данных:
- [DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:101).
3. Последствие:
- пользователь получает заведомо ложное состояние обучения вместо честного `no data/error`;
- это критично для доверия к метрикам платформы.

### 2.5 Dashboard выбирает «первый курс/урок», а не реальный текущий контекст пользователя

1. В `DashboardPage` используется первый курс из списка и первый урок в курсе:
- [DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:99),
- [DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:106).
2. Последствие:
- карточка «Текущий курс» системно может не соответствовать фактической траектории пользователя;
- прогресс в dashboard становится структурно недостоверным.

### 2.6 Auth lifecycle по-прежнему может разрушать прогресс обучения

1. При bootstrap/auth refresh сбое вызывается `clearTokens()`:
- [auth.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\store\auth.ts:67),
- [client.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\api\client.ts:247).
2. `clearTokens()` удаляет user-scoped storage, включая lesson progress:
- [client.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\api\client.ts:206),
- [userScopedStorage.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\utils\userScopedStorage.ts:21).
3. Последствие:
- transient auth/network failure способен снова приводить к потере клиентского прогресса.

## 3. Критичный вероятностный баг (требует production-trace)

### 3.1 Persisted cache для user-specific endpoint без user-scope ключа

1. Cache key строится из URL/params, без user ID:
- [client.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\api\client.ts:122).
2. `getCourseTasksCatalog` (user-specific по статусам задач) кэшируется с `persist: true`:
- [client.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\api\client.ts:325).
3. При `saveTokens()` persistent cache не очищается:
- [client.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\api\client.ts:195).
4. Риск:
- при сценариях смены аккаунта на той же машине возможна подмешка устаревшего user-specific статуса задач.
5. Статус: гипотеза высокого риска; нужен целевой production/E2E trace для детерминированного подтверждения.

## 4. Итог

1. Найдены дополнительные критичные баги того же класса: не локальные UI-ошибки, а архитектурные рассинхроны модели прогресса и статусов.
2. Ключевой паттерн повторяется: frontend показывает derived/local/cached state вместо канонического серверного.

## 5. История документа

1. v1.0 (2026-05-13): первичный аудит похожих критичных багов после root-cause отчёта по исходным 7 инцидентам.

## 6. Статус после remediation (v1.1, 2026-05-13)

1. `Lesson submission polling` на `processing` закрыт (poll продолжает ожидание до финального статуса).
2. `minScorePercent` в квизах закрыт backend-реализацией порога и согласованием контракта ответа.
3. `Tasks page` больше не пересобирает статусы из `submissionHistory`, использует `tasks-catalog.status`.
4. `Dashboard` больше не показывает фиктивный fallback progress; используется честный empty/error state.
5. `Dashboard context` больше не берётся как «первый курс/урок» безусловно; контекст строится из серверных данных.
6. `Auth lifecycle` смягчён для transient сбоев: session clear ограничен auth-invalid сценариями.
7. Детали реализации/проверки:
- `docs/operations/CANONICAL_PROGRESS_REMEDIATION_2026_05_13.md`.
