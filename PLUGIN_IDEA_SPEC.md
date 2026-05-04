# IntelliJ IDEA Plugin Spec (Launch Baseline)

## 1. Назначение

Документ фиксирует текущее состояние плагина IDEA в контексте launch-релиза платформы.

## 2. Текущее состояние на 2026-04-29

1. Отдельный production-ready модуль IntelliJ plugin в этом репозитории не реализован.
2. Backend API оставляет контрактную основу для будущего plugin-клиента:
- auth/login/refresh;
- чтение курсов/уроков/задач;
- отправка решений и получение verdict;
- профиль и прогресс.

Почему зафиксировано именно так:

1. Для запуска на 200 учеников выбран web-first scope.
2. Одновременный запуск веб-продукта и IDE-плагина повышает операционный риск релиза.

## 3. Минимальный scope V1 (после web launch)

1. Авторизация:
- login по email/password;
- refresh токена.

2. Каталог задач:
- список курсов/уроков/задач;
- просмотр условия задачи.

3. Проверка решения:
- отправка source-кода в `POST /tasks/{taskID}/submissions`;
- polling статуса `GET /submissions/{submissionID}`.

4. Профиль:
- чтение `publicId`, nickname, level, xp, streak.

## 4. UX-сценарий плагина

1. Пользователь логинится в tool window.
2. Открывает список задач.
3. Выбирает задачу и решает её в IDE.
4. Отправляет код на проверку.
5. Видит результат тестов и обновление XP.

## 5. Контрактные требования к API для плагина

1. Совместимость с JWT bearer auth.
2. Стабильные JSON-ключи:
- `publicId`
- `nickname`
- `submissionId`
- `status`
- `score`

## 6. Ограничения launch-релиза

1. OAuth вход отключен в production launch профиле.
2. Плагин V1 должен использовать email/password auth.

## 7. Критерии готовности plugin V1

1. Логин и refresh работают без ручной переавторизации.
2. Отправка решения и verdict корректны.
3. Ошибки сети и auth отображаются пользователю явно.

## 8. Update 2026-04-29 — реализован plugin foundation module

1. В репозитории создан отдельный подпроект `idea-plugin` с рабочей Gradle IntelliJ сборкой.
2. Реализованы базовые сервисы:
- `AuthService` + PasswordSafe storage;
- API layer (`PlatformApiClient`, `HttpPlatformApiClient`, `MockPlatformApiClient`);
- `PlatformSettings` (`PersistentStateComponent`);
- `TaskManager`, `TaskFileService`, `SubmissionService`, `SyncService`, `ProjectRestoreService`.
3. Реализован Tool Window с состояниями:
- unauthorized;
- loading;
- ready;
- error.
4. Реализован локальный цикл:
- открыть задачу;
- запустить/дебажить (Java);
- отправить на проверку;
- получить verdict;
- синхронизировать кэш.
5. Добавлены actions для Find Action / Tools Menu.
6. Добавлена локализация через resource bundle (`messages/PlatformBundle*.properties`).
7. Добавлены unit-тесты критичной логики (auth/task/status/submission/api/sync/settings).

Почему это зафиксировано именно так:

1. Модуль вынесен отдельно, чтобы plugin разработка не блокировала web-release контур и не вносила риски в runtime backend/frontend.
2. API клиента сделали через абстракцию и fallback-механизмы, потому что текущий backend контракт не полностью совпадает с целевым plugin-контрактом.
3. Security-блок (token storage + path safety + submission filtering) был реализован в первой итерации, чтобы исключить архитектурный технический долг до расширения feature set.

## 9. Endpoint gap list для полного plugin-контракта

Для закрытия всех сценариев IDE-клиента backend стороне нужно добавить/стабилизировать:

1. `GET /courses/{courseId}/tasks`
2. `GET /tasks/{taskId}/template`
3. `POST /tasks/{taskId}/attempts`
4. `GET /tasks/{taskId}/attempts/{attemptId}`
5. `POST /tasks/{taskId}/style-check`
6. `GET /tasks/{taskId}/reference-solution`
7. `POST /tasks/{taskId}/progress/reset`
8. `POST /sync`

Пояснение:

1. Эти endpoint’ы нужны, чтобы plugin перестал использовать адаптацию/фолбэки и работал на прямом контракте без промежуточного маппинга.
2. До появления этих endpoint’ов текущая реализация остается рабочей за счет `HttpPlatformApiClient` адаптеров.

## 10. Update 2026-04-30 — real backend auth flow wired (v2.51)

1. В plugin добавлена поддержка `email/password` login:
- диалог входа поддерживает два режима:
  - стандартный для платформы: email/password (`POST /auth/login`);
  - ручной token mode для dev/admin сценариев.

2. Реализован refresh контур в auth service:
- хранение `accessToken` + `refreshToken` через PasswordSafe;
- авто-refresh по `401` в сервисах задач/submit/sync/style/reference;
- повтор исходного запроса после обновления access token.

3. Поведение при истекшей сессии:
- active auth state сбрасывается в `requiresReLogin=true`;
- локальный cache задач не очищается автоматически, чтобы сохранить offline режим.

4. Production default API URL:
- `http://85.198.82.221:8510/api/v1` (взято из проектного API контракта);
- параметр остается конфигурируемым в settings.

Почему зафиксировано именно так:

1. Реальный backend проекта уже использует JWT access/refresh, поэтому token-only plugin режим недостаточен для production нагрузки.
2. Централизация refresh логики в `AuthService.withAuthorizedToken` убирает дублирование retry-кода и снижает риск race-condition в разных сервисах.

## 11. Update 2026-04-30 — practical verification for production cohort

1. Выполнена практическая проверка backend-связки по боевому API:
- login/refresh/me;
- courses/course/lesson/task;
- run/submissions/submission-status.

2. Выполнены build/test циклы после деплоя:
- plugin: `idea-plugin ./gradlew test buildPlugin`;
- backend: `go test ./...`;
- frontend: `npm run test -- --run` и `npm run build`.

3. Выполнен server-side load baseline:
- `GET /healthz`: ~124k req/s;
- auth `GET /courses`: ~11.6k req/s.

4. Зафиксирован operational вывод:
- текущий контур технически готов к первой волне до ~1500 учеников при текущем функциональном профиле;
- для более агрессивного роста нужно добавить отдельный soak-test и мониторинг p95/p99 в длительном окне.

Почему это зафиксировано:

1. Требование было проверить «на деле», поэтому документированы не только изменения кода, но и результаты практических прогонов.
2. Без числового baseline невозможно объективно говорить о готовности к пользовательской нагрузке.

## 12. Update 2026-04-30 — AI hints in IDE + language alignment with curriculum (v2.59)

1. Подключен AI hints flow в IDEA plugin:
- API-клиент поддерживает `POST /api/v1/ai/task-hint`;
- добавлен project-service `AiHintService` с вызовом backend через текущую auth-сессию;
- добавлен UI-контур: кнопка `AI-подсказка` в task panel + action в Tools/Find Action;
- добавлен read-only dialog `AiHintDialog` для отображения текста подсказки и модели.

2. Уточнена модель языков задач:
- добавлен `TaskLanguage` (JAVA, PYTHON, KOTLIN, SQL, JAVASCRIPT, UNKNOWN) с alias mapping;
- fallback `TaskTemplate` path определяется через языковую модель;
- для локального run unsupported language ошибка теперь содержит конкретное имя языка.

3. Проверка соответствия фактическим материалам курса:
- по миграциям backend в текущем контенте зафиксированы `java` и `python` (и alias `python3`);
- SQL/JS/Kotlin пока не обнаружены в seed, но структура plugin готова к добавлению таких задач без рефакторинга.

4. Добавленные тесты:
- `HttpPlatformApiClientTest`: AI hint success + endpoint-missing fallback;
- `HttpPlatformApiClientLanguageTest`: mapping SQL task details/template fallback;
- `TaskLanguageMappingTest`: canonical language mapping.

Почему зафиксировано именно так:

1. Пользовательский запрос требовал связать plugin с реальным курсом и AI-подсказками, поэтому зафиксирована проверка контента и фактические supported paths.
2. Поддержка SQL/других языков сделана как расширяемая основа: без fake-рантайма, но с корректной маршрутизацией файлов/шаблонов/submit.

## 13. Update 2026-05-05 — backend contract closure + large-course performance stabilization

1. Закрыты backend endpoint gaps для IDE-контракта:
- `GET /api/v1/tasks/{taskID}/template`;
- `POST /api/v1/tasks/{taskID}/style-check`;
- `GET /api/v1/tasks/{taskID}/reference-solution`;
- `POST /api/v1/tasks/{taskID}/progress/reset`;
- `POST /api/v1/sync`.

2. Ускорен массовый sync задач для больших курсов:
- `HttpPlatformApiClient.getCourseTasks(...)` теперь сначала использует `GET /api/v1/courses/{courseID}/tasks-catalog`;
- fallback на старый lesson-fanout сохранен для обратной совместимости и аварийного режима.

3. Устранены основные backend data-leaks в plugin-сценариях:
- `GET /api/v1/submissions/{submissionID}` возвращает sanitized `feedback` без `input/expected`;
- `referenceCode` больше не используется как канал выдачи эталонного решения;
- эталон отдается только через `GET /tasks/{taskID}/reference-solution` после `accepted` (или admin).

4. Усилена надежность submit при деградации Redis:
- при ошибке `RPush` backend не ломает UX `500`, а возвращает `202 Accepted` с `deferredDispatch=true`;
- queued submission гарантированно подхватывается reconciler-циклом worker.

5. Добавлены эксплуатационные лимиты для больших решений:
- `MAX_REQUEST_BODY_BYTES`;
- `MAX_SUBMISSION_SOURCE_BYTES`.

Почему это зафиксировано именно так:

1. Плагину нужна предсказуемая серверная спецификация, иначе на нагрузке и нестабильной сети проявляются race/fallback баги.
2. `tasks-catalog` как первичный путь — ключ к скорости на курсах с большим числом уроков и задач.
3. Разделение “вердикт сабмита” и “доступ к эталону” исключает утечки hidden-check логики.
