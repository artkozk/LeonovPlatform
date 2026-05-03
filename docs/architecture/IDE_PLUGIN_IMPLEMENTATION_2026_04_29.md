# IntelliJ IDEA Plugin Implementation Notes (2026-04-29)

## 1. Контекст и цель

Документ фиксирует фактически реализованную основу IntelliJ IDEA plugin-клиента для Leonov Care Platform в подпроекте `idea-plugin`.

Плагин реализован как отдельный Gradle-модуль, чтобы:

1. Не ломать текущий backend/frontend production pipeline.
2. Сохранить независимую сборку/тестирование и выпуск plugin distribution.
3. Упростить дальнейшую интеграцию с backend API без рискованных изменений в web части.

## 2. Определенные параметры

1. `PLATFORM_NAME`: `Leonov Care Platform`.
2. `PLUGIN_DISPLAY_NAME`: `Leonov Care Platform Plugin`.
3. `PACKAGE_NAME`: `com.leonovcare.plugin`.
4. `API_BASE_URL` по умолчанию: `http://localhost:8080/api/v1`.

Почему так:

1. Название платформы взято из `README.md`, `backend/.env.example` (`APP_NAME`) и OpenAPI (`API_SPEC.yaml`).
2. Базовый URL подтвержден в `frontend/.env.example` (`VITE_API_URL`) и OpenAPI servers.
3. В репозитории не было Java/Kotlin namespace, поэтому выбран совместимый технический namespace по доменному имени проекта.

## 3. Что было в репозитории до реализации

1. Не было `plugin.xml`, Gradle IntelliJ сборки и Kotlin plugin-кода.
2. Был backend API (Go/Gin) и frontend React/Vite.
3. Реальные backend endpoints частично отличались от целевого контракта plugin-клиента.

## 4. Реализованная структура

Создан подпроект:

`C:/prog/Comercial/LeonovCarePlatform/idea-plugin`

Ключевые пакеты:

1. `auth`: `AuthService`, `AuthState`, `CredentialsStorage`, `LoginDialog`, `CurrentUserService`.
2. `api`: `PlatformApiClient`, `HttpPlatformApiClient`, `MockPlatformApiClient`, модели, ошибки.
3. `settings`: `PlatformSettings` (`PersistentStateComponent`), `PlatformSettingsConfigurable`.
4. `task`: `TaskManager`, `TaskFileService`, `TaskMetadata`, `TaskStatus`, `TaskType`, `CurrentTaskService`.
5. `submission`: `SubmissionService`, `SubmissionFileCollector`, `SubmissionResultPanel`.
6. `analysis`: `CodeStyleAnalysisService`, `LocalInspectionRunner`.
7. `run`: `TaskRunConfigurationService`, `LanguageRunConfigurationProvider`, `JavaRunConfigurationProvider`.
8. `sync`: `SyncService`, `SyncStatusMerger`.
9. `project`: `ProjectStructureService`, `ProjectRestoreService`.
10. `ui`: ToolWindow и панели (`PlatformToolWindowFactory`, `PlatformToolWindowPanel`, `TaskListPanel`, `TaskStatementPanel`, `TaskResultPanel`, `ReferenceSolutionViewer`).
11. `actions`: Login/Logout/Sync/Open/Run/Debug/Submit/Analyze/Reference/Restore/Settings actions.
12. `notifications`: notification groups helper.
13. `i18n`: resource bundle loader + RU/EN properties.

## 5. Безопасность и хранение данных

1. Токен хранится только через `PasswordSafe` (`PasswordSafeCredentialsStorage`).
2. Токен не пишется в логи и не хранится в plain settings.
3. Генерация task-files защищена от path traversal:
- нормализация путей;
- запрет выхода за `taskDir`.
4. В `SubmissionFileCollector` исключены служебные и build-артефакты:
- `.idea`, `.gradle`, `build`, `target`, `out`, `.class`, `.jar`, `.platform-task.json`.
5. При восстановлении/перезаписи editable-файлов создается backup `*.bak-YYYYMMDD-HHMMSS`.

## 6. Как адаптированы endpoint’ы

### 6.1 Реальные endpoint’ы backend (обнаружены)

1. `GET /me`
2. `GET /courses`
3. `GET /courses/{courseID}`
4. `GET /lessons/{lessonID}`
5. `GET /tasks/{taskID}`
6. `POST /tasks/{taskID}/submissions`
7. `GET /submissions/{submissionID}`
8. `POST /tasks/{taskID}/run`

### 6.2 Что ожидалось в целевом контракте, но отсутствует сейчас

1. `GET /courses/{courseId}/tasks`
2. `GET /tasks/{taskId}/template`
3. `POST /tasks/{taskId}/attempts` + `GET /tasks/{taskId}/attempts/{attemptId}` (вместо текущего submissions формата)
4. `POST /tasks/{taskId}/style-check`
5. `GET /tasks/{taskId}/reference-solution`
6. `POST /tasks/{taskId}/progress/reset`
7. `POST /sync`

### 6.3 Как это решено в текущем коде

1. Слой `HttpPlatformApiClient` использует endpoint mapping и fallback-поведение.
2. Список задач курса строится через `course -> lessons -> tasks`.
3. Шаблон задачи строится fallback’ом из `starterCode`, если endpoint template отсутствует.
4. Style-check, reference-solution, reset-progress, sync обрабатываются как optional endpoint’ы с корректной деградацией.

## 7. UI и функциональность

Реализовано:

1. ToolWindow состояния: unauthorized/loading/ready/error.
2. Авторизация по токену с валидацией через `/me`.
3. Загрузка курсов/задач, выбор курса, фильтры и поиск.
4. Открытие задачи и генерация локальной структуры:
- `platform-tasks/course-{id}/task-{id}`.
5. Отображение statement.
6. Run/Debug локально для Java.
7. Submit + polling verdict.
8. Панель результата проверки.
9. Local style analysis + optional server style analysis.
10. Reference solution viewer (read-only split view).
11. Ручная и автоматическая sync.
12. Restore project structure.

Функции сообщества/форума/чатов намеренно не реализованы.

## 8. Тесты

Добавлены unit-тесты:

1. `AuthServiceTest`.
2. `TaskStatusMappingTest`.
3. `TaskFileServiceTest`.
4. `SubmissionFileCollectorTest`.
5. `HttpPlatformApiClientTest`.
6. `PlatformSettingsStateTest`.
7. `SyncStatusMergerTest`.

## 9. Команды проверки

1. `./gradlew test`
2. `./gradlew buildPlugin`

Обе команды проходят в `idea-plugin`.

## 10. Что нужно доделать на backend для полного контракта plugin-клиента

1. Выдать endpoint `GET /courses/{courseId}/tasks` с task status/order/lock прямо в одном ответе.
2. Добавить endpoint `GET /tasks/{taskId}/template` с файловым шаблоном.
3. Ввести dedicated attempts API c расширенным `SubmissionResult` (tests/style/time/memory).
4. Добавить `POST /tasks/{taskId}/style-check`.
5. Добавить `GET /tasks/{taskId}/reference-solution` с ACL и `unavailableReason`.
6. Добавить `POST /tasks/{taskId}/progress/reset`.
7. Добавить `POST /sync` с инкрементальной синхронизацией и changed statuses.
8. Добавить API marker `task status` уровня курса/пользователя, чтобы убрать эвристики plugin-side.

## 11. Почему сделано именно так

1. Плагин реализован модульно и тестируемо, чтобы не превратить первую версию в нерефакторируемый monolith.
2. Функциональность выстроена вокруг обязательного учебного цикла (получить задачу -> решить локально -> проверить -> синхронизировать).
3. Backend-несоответствия закрыты адаптером API вместо хардкода в UI, чтобы быстрее перейти на реальный контракт без массовых переписываний.
4. Безопасность (token storage, path traversal, file filtering, backups) вынесена в явные сервисы и покрыта тестами, чтобы ревью мог проверить это детерминированно.

## 12. Update 2026-04-30 — production auth flow linkage

1. В auth-контур добавлена поддержка `email/password` login (`POST /auth/login`) и refresh (`POST /auth/refresh`).
2. `CredentialsStorage` расширен до хранения пары `accessToken + refreshToken` с PasswordSafe миграцией от legacy single token.
3. `AuthService.withAuthorizedToken` стал единой точкой выполнения авторизованных API-запросов:
- перехватывает `401`;
- делает refresh;
- повторяет исходный запрос с новым access token.
4. При невозможности refresh:
- auth state переводится в `requiresReLogin=true`;
- локальный task cache сохраняется для offline continuity;
- токены удаляются из secure storage.
5. Default API base URL обновлен на production endpoint проекта:
- `http://85.198.82.221:8510/api/v1`;
- URL по-прежнему настраивается в plugin settings.

Почему это важно:

1. Текущий backend платформы не поддерживает production-поток “вечного” static token, он построен на ротации JWT.
2. Без централизованного refresh plugin быстро деградирует в “частые re-login” при активной учебной сессии.
3. Сохранение локального кэша при re-login снижает риск потери контекста у ученика при сетевых/auth сбоях.

## 13. Update 2026-05-03 — PyCharm target for Python course

1. Целевой продукт для plugin-сборки переключен с IDEA Community на PyCharm Community (`2025.1`).
2. В Gradle-dependencies добавлен обязательный `PythonCore`, чтобы plugin-контур соответствовал PyCharm API требованиям.
3. В `plugin.xml` обязательная модульная зависимость переведена на `com.intellij.modules.python`.
4. Java plugin dependency переведена в optional через `config-file`:
- `<depends optional="true" config-file="leonovcare-with-java.xml">com.intellij.java</depends>`.

Почему это нужно:

1. Основной пользовательский поток в текущем запросе: Python-курс внутри PyCharm.
2. Жесткая Java-dependency в main descriptor ограничивает plugin только Java-ориентированными IDE и делает PyCharm rollout недоступным.
3. Optional dependency сохраняет обратную совместимость Java-path там, где Java plugin действительно присутствует.

5. Изменение run-сервиса:
- `TaskRunConfigurationService` больше не держит hard initialization `JavaRunConfigurationProvider()` в поле providers;
- Java provider загружается через reflection по class name и добавляется только если класс успешно инстанцируется;
- если Java API недоступно, сервис автоматически работает через fallback provider и выдает controlled user-facing ошибку вместо startup crash.

Почему так:

1. Это убирает class-loading риск в PyCharm при отсутствии Java plugin classloader parent.
2. Плагин не теряет Java-run функциональность полностью: она остается доступной в IDE с Java plugin.
3. Поведение в Python-потоке становится предсказуемым: open/edit/submit/sync/AI доступны независимо от Java runtime слоя.

6. Что проверять в валидации PyCharm:

1. Установка плагина из `build/distributions/*.zip` проходит без dependency error.
2. Tool Window открывается, login работает.
3. Загружаются курсы/задачи, Python-задача открывается в `platform-tasks/...`.
4. `Submit` и polling verdict работают.
5. `AI-подсказка` получает ответ через `POST /api/v1/ai/task-hint`.
6. `Run/Debug` для unsupported language дает ожидаемую ошибку без падения UI.

## 14. Update 2026-05-03 — correction after Gradle verification

1. Во время фактического прогона build на PyCharm target выявлено:
- `bundledPlugin("com.intellij.java")` не доступен как bundled dependency для выбранного PyCharm runtime.

2. В результате финальная конфигурация скорректирована:
- Java dependency убрана из Gradle/plugin.xml;
- optional descriptor для Java слоя удален;
- run-service оставлен в fallback-модели без Java provider.
- `instrumentCode` task отключен в Gradle, чтобы обойти environment-specific падение ant instrumentation (`...\\jdk-17...\\Packages does not exist`) и не блокировать выпуск plugin zip.

3. Причина коррекции:
- сохранить реальную собираемость и устанавливаемость plugin в PyCharm для Python-курса важнее, чем частичная поддержка Java local runner в этой же сборке.

4. Operational effect:
- PyCharm installability и Python submit-flow сохраняются;
- локальный run/debug через plugin недоступен и должен показывать controlled unsupported-path сообщение.
