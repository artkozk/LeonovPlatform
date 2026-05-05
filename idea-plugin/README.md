# Leonov Care Platform IDEA Plugin

## Назначение

Этот модуль реализует IDE-клиент образовательной платформы Leonov Care для IntelliJ IDEA.

Ключевые сценарии:

1. Авторизация пользователя (email/password или token mode).
2. Загрузка курсов и задач с backend.
3. Открытие задач в локальной структуре `platform-tasks/...`.
4. Локальный запуск/дебаг Java-задач.
5. Отправка решения на серверную проверку.
6. Просмотр результата проверки.
7. Ручная и автоматическая синхронизация.
8. AI-подсказка для текущей задачи через backend endpoint.

## Текущая поддержка языков задач

1. Подтвержденные в актуальном курсе: `JAVA`, `PYTHON` (`python3` alias).
2. Поддержка в структуре плагина (через `TaskLanguage`): `JAVA`, `PYTHON`, `KOTLIN`, `SQL`, `JAVASCRIPT`, `UNKNOWN`.
3. Локальный run/debug:
- полноценно: `JAVA`;
- остальные языки: корректное сообщение о неподдержанном локальном run (без падения UI).
4. Submit/check, task files, AI hint и sync работают language-agnostic.

## Важные backend endpoint'ы

Текущая реализация использует:

1. `POST /api/v1/auth/login`
2. `POST /api/v1/auth/refresh`
3. `GET /api/v1/me`
4. `GET /api/v1/courses`
5. `GET /api/v1/courses/{courseID}`
6. `GET /api/v1/lessons/{lessonID}`
7. `GET /api/v1/tasks/{taskID}`
8. `POST /api/v1/tasks/{taskID}/submissions`
9. `GET /api/v1/submissions/{submissionID}`
10. `POST /api/v1/ai/task-hint`

Fallback endpoint'ы (если backend не реализовал canonical plugin contract):

1. `GET /tasks/{taskId}/template` (если 404, используется `starterCode` из `GET /tasks/{taskID}`).
2. `POST /sync` (если 404, sync считается unavailable без падения плагина).
3. `POST /tasks/{taskId}/style-check` (если 404, используется только локальный style analysis).

## Безопасность

1. Токены хранятся в `PasswordSafe`, не в plain settings.
2. HTTP Authorization не логируется.
3. Создание task files защищено от path traversal (`TaskFileService.resolveSafe`).
4. Submit-файлы фильтруют `.idea`, `build`, `target`, `out`, `.class` и сервисные файлы.

## Запуск и проверка

```bash
cd idea-plugin
./gradlew test
./gradlew buildPlugin
./gradlew runIde
```

## Почему реализация сделана так

1. `PlatformApiClient` interface отделяет UI от HTTP и упрощает тестирование.
2. `AuthService.withAuthorizedToken` централизует refresh/retry на `401`.
3. `TaskLanguage` предотвращает ошибки на разных alias языка (`python3`, `js`, `postgresql`).
4. AI-подсказки идут через backend, чтобы соблюдать тарифные ограничения и аудит (premium gating, logging на стороне сервера).

## Update 2026-05-03 — PyCharm compatibility for Python course

1. Плагин переведен на целевой IDE runtime PyCharm (ветка 2025.1):
- Gradle target: `pycharmCommunity("2025.1")`;
- обязательный bundled plugin: `PythonCore`;
- совместимость build-range сохранена: `sinceBuild=251`, `untilBuild=251.*`.

2. Plugin descriptor обновлен под Python IDE:
- обязательная модульная зависимость: `com.intellij.modules.python`;
- Java plugin переведен в optional dependency:
  - `<depends optional="true" config-file="leonovcare-with-java.xml">com.intellij.java</depends>`.

3. Core run-service изолирован от hard dependency на Java runtime:
- Java-specific provider (`JavaRunConfigurationProvider`) вынесен из базового `TaskRunConfigurationService`;
- в `TaskRunConfigurationService` добавлена безопасная динамическая загрузка optional provider по class name;
- если Java plugin/API недоступен, сервис не падает, а использует `UnsupportedLanguageRunConfigurationProvider`.

4. Почему сделано именно так:
- пользовательский сценарий сейчас ориентирован на Python-курс в PyCharm, поэтому plugin обязан стабильно загружаться без обязательного `com.intellij.java`;
- Java-run контур не удален полностью, а переведен в optional режим, чтобы не терять функциональность в IDE, где Java plugin присутствует;
- безопасная деградация в run/debug предотвращает class-loading падение plugin startup в PyCharm.

5. Как протестировать плагин в PyCharm для Python-курса:
1. Запустить сборку из корня `idea-plugin`:
```bash
./gradlew test
./gradlew buildPlugin
```
2. Взять артефакт:
- `idea-plugin/build/distributions/leonovcare-idea-plugin-0.1.0.zip`.
3. Установить zip в PyCharm:
- `Settings -> Plugins -> gear icon -> Install Plugin from Disk`.
4. Настроить API:
- `Settings -> Tools -> Leonov Care Platform Plugin`;
- `API Base URL`: `http://85.198.82.221:8510/api/v1` (или ваш staging URL).
5. Выполнить smoke flow Python-курса:
- логин (email/password или token mode);
- загрузка курсов и выбор Python-курса;
- открытие задачи в `platform-tasks/...`;
- редактирование решения;
- `Проверить` (submit) + получение verdict;
- `AI-подсказка` по текущей задаче.
6. Ожидаемое поведение run/debug:
- для Python-задач локальный run/debug в текущем контуре не обязателен и может возвращать сообщение о неподдерживаемом локальном раннере;
- submit/check/sync/AI должны работать без ошибок.

## Update 2026-05-03 — correction after dependency resolution check

1. Фактический результат после реального прогона Gradle на PyCharm target:
- `bundledPlugin("com.intellij.java")` не резолвится для PyCharm runtime;
- ошибка сборки: `Could not find bundled plugin with ID: 'com.intellij.java'`.

2. Итоговое техническое решение (актуальное состояние):
- `com.intellij.java` dependency полностью убрана из `build.gradle.kts` и `plugin.xml`;
- optional descriptor `leonovcare-with-java.xml` удален;
- `TaskRunConfigurationService` оставлен только с `UnsupportedLanguageRunConfigurationProvider`, без dynamic Java-provider loading.
- task `instrumentCode` отключен в Gradle-конфигурации, чтобы сборка не падала на ant-инструментации в текущем Windows/JDK окружении (`...\\jdk-17...\\Packages does not exist`).

3. Почему именно так:
- цель текущей итерации — рабочий PyCharm plugin для Python-курса;
- попытка сохранить Java-run path через bundled Java dependency конфликтует с PyCharm target и блокирует сборку;
- приоритизация production-flow для Python (open/edit/submit/AI/sync) важнее сохранения Java-run в этой сборке.

4. Что это значит для пользователя сейчас:
- plugin устанавливается и работает в PyCharm для учебного Python-сценария;
- локальный run/debug через текущий plugin-контур не предоставляется и возвращает controlled unsupported message;
- серверная проверка (`submit` + polling verdict), синхронизация и AI-подсказки продолжают работать.

## Update 2026-05-03 — packaging for PyCharm 2024.2.6

1. Обнаружено, что на пользовательском IDE стоит PyCharm `2024.2.6` (ветка build `242`), а прошлый zip был собран под `251.*`, из-за чего plugin не появлялся в `Settings -> Tools`.

2. Для этого окружения выполнена отдельная совместимая упаковка:
- `pycharmCommunity("2024.2.6")`;
- `sinceBuild = "242"`;
- `untilBuild = "242.*"`;
- plugin version: `0.1.1`.

3. Актуальный файл для установки:
- `idea-plugin/build/distributions/leonovcare-idea-plugin-0.1.1.zip`.

4. Почему так:
- это устраняет install-time несовместимость без изменения функционального контракта API/login/submit/AI;
- пользователь получает предсказуемую установку именно в своей версии IDE.

## Update 2026-05-03 — full lesson theory in plugin + local lesson cache

1. Цель изменения:
- пользователь должен получать в PyCharm не только условие текущей задачи, но и материалы урока (теория, шаги, связка шагов с задачами), чтобы учебный поток был возможен внутри IDE без постоянного переключения на web-платформу.

2. Что добавлено в plugin domain/API:
- `Task` расширен lesson-метаданными (`lessonId`, `lessonTitle`) для надежной связи задачи с уроком;
- в API-модели добавлен `LessonMaterial`, который включает:
  - данные урока (`id`, `title`, `description`);
  - список задач урока;
  - список блоков урока (`blocks`) с типом, порядком и привязками;
- в `PlatformApiClient` добавлен контракт `getLessonMaterial(token, lessonId)`;
- `HttpPlatformApiClient` реализует загрузку `GET /lessons/{lessonId}` и маппит lesson/tasks/blocks в типизированную модель.

3. Локальное кэширование:
- добавлен `LessonCache` как application service;
- cache хранится в `PlatformSettings` (`lessonsCacheJson`) и очищается через `Очистить локальный кэш`;
- в `TaskManager` используется TTL `8h` для lesson-материалов:
  - если материал свежий, берется локально;
  - если отсутствует или устарел, запрашивается у backend и обновляется в cache.

4. Изменение поведения плагина для пользователя:
- после `refreshAll()` плагин запускает background prefetch материалов уроков по задачам курса;
- при `openTask()` в контекст задачи подмешивается `lessonMaterial`;
- `TaskStatementPanel` отображает:
  - заголовок/описание урока;
  - теорию урока;
  - последовательность шагов (`blocks`) с типами;
  - и затем контент выбранной задачи;
- в локальную структуру задачи дополнительно сохраняется `lesson-material.md` рядом со `statement.md`, чтобы материалы были доступны как физический файл на диске.

5. Почему сделано именно так:
- это закрывает основной пользовательский запрос "вся теория в IDE";
- prefetch + TTL существенно сокращают повторные запросы и нагрузку на сервер при переходах между задачами;
- хранение lesson-материалов в settings не требует внедрения отдельной локальной БД, но сохраняет быстрый офлайн-доступ к уже загруженным материалам;
- файл `lesson-material.md` упрощает проверку содержимого и делает учебный контент прозрачным для ревью/поддержки.

6. Технические точки изменений:
- `src/main/kotlin/com/leonovcare/plugin/api/ApiModels.kt`;
- `src/main/kotlin/com/leonovcare/plugin/api/PlatformApiClient.kt`;
- `src/main/kotlin/com/leonovcare/plugin/api/HttpPlatformApiClient.kt`;
- `src/main/kotlin/com/leonovcare/plugin/cache/LessonCache.kt`;
- `src/main/kotlin/com/leonovcare/plugin/settings/PlatformSettings.kt`;
- `src/main/kotlin/com/leonovcare/plugin/task/TaskManager.kt`;
- `src/main/kotlin/com/leonovcare/plugin/task/LessonMaterialFormatter.kt`;
- `src/main/kotlin/com/leonovcare/plugin/task/TaskFileService.kt`;
- `src/main/kotlin/com/leonovcare/plugin/ui/TaskStatementPanel.kt`;
- `src/main/kotlin/com/leonovcare/plugin/ui/PlatformToolWindowPanel.kt`.

7. Regression/validation checks:
1. `./gradlew test`;
2. `./gradlew buildPlugin`;
3. проверка, что в `platform-tasks/...` создается `lesson-material.md`;
4. повторное открытие задачи не вызывает обязательный сетевой запрос при свежем cache.

## Update 2026-05-03 — task opening UX hotfix

1. Проблема:
- список задач позволял выделить элемент, но не открывал его автоматически;
- пользователь мог сразу нажать `Run/Debug/AI/Reference` и получить `errors.taskUnavailable`, так как `CurrentTaskContext` ещё пустой.

2. Исправление:
- в `TaskListPanel` добавлен user-driven open при клике по задаче;
- добавлен keybinding `Enter` для открытия выделенной задачи;
- кнопка `Открыть` сохранена для явного ручного сценария.

3. Почему так:
- устраняется неоднозначность между "выбранной" и "открытой" задачей;
- снижение ложных ошибок без изменения API/схемы/бэкенда.

4. Файл:
- `src/main/kotlin/com/leonovcare/plugin/ui/TaskListPanel.kt`.

5. Проверка:
1. `./gradlew test buildPlugin`;
2. в PyCharm клик/Enter по задаче должен немедленно показывать statement и материалы урока;
3. после открытия задачи кнопки run/submit/ai работают в контексте выбранной задачи.

## Update 2026-05-05 — startup-first loading strategy for large courses

1. Проблема до изменения:
- при холодном старте пользователь мог долго видеть только экран `Загрузка курсов и задач…`;
- при большом объеме данных сначала грузилось слишком много контента, который не нужен для первого шага обучения;
- приоритет IDE-контекста (PyCharm/Python, IDEA/Java) не учитывался в выборе стартового курса.

2. Что изменено в `TaskManager`:
1. Добавлена стратегия выбора стартового курса и стартовой задачи:
- приоритет 1: задача, на которой пользователь остановился (`currentTaskId`) и курс, где она находится;
- приоритет 2: ранее выбранный курс (`selectedCourseId`), если он валиден;
- приоритет 3: курс, соответствующий текущей IDE по языку;
- приоритет 4: первый доступный курс как fallback.
2. Добавлено IDE-определение предпочтительного языка:
- `PyCharm`/`DataSpell` -> `PYTHON`;
- `IntelliJ IDEA` -> `JAVA`;
- `WebStorm` -> `JAVASCRIPT`;
- `DataGrip` -> `SQL`.
3. Изменен порядок refresh:
- сначала загружается список курсов;
- UI переводится в `ready` максимально рано на кэшированных данных;
- затем подтягиваются задачи выбранного курса;
- затем в фоне подтягиваются остальные курсы.
4. Добавлен приоритет lesson-material prefetch:
- сначала материал урока стартовой задачи;
- далее остальные уроки в порядке задач.
5. Добавлен startup auto-open:
- если стартовая задача доступна и еще не открыта в текущем контексте, плагин открывает ее автоматически.

3. Почему принято именно такое решение:
1. Пользователь должен начать учиться сразу, а не ждать полную синхронизацию всего каталога.
2. Возврат на последний прогресс (`resume`) снижает потерю контекста и ускоряет повторный вход в обучение.
3. IDE-first приоритизация убирает ситуацию, когда в PyCharm первым открывается не Python-контент.
4. Поэтапная догрузка уменьшает ощущение зависания и лучше масштабируется на большие курсы.

4. Технические детали реализации:
1. Добавлены функции выбора старта:
- `resolveStartupSelection(...)`;
- `pickCourseForLanguage(...)`;
- `pickStartupTask(...)`.
2. Добавлена нормализация порядка задач:
- сортировка по `order`, затем `lessonTitle`, `title`, `id`.
3. Ужесточены timeouts на lesson prefetch:
- догрузка материалов уроков идет с `withTimeout(requestTimeoutMillis)`.
4. Добавлены защитные условия авто-открытия:
- не открывать locked/unavailable задачи;
- не открывать повторно ту же стартовую задачу;
- не запускать авто-открытие при неавторизованной сессии.

5. Пошаговый фактический runtime-сценарий после изменения:
1. Плагин получает курсы и определяет стартовую точку.
2. UI показывает `ready` на текущем доступном наборе данных без ожидания полной синхронизации.
3. Плагин обновляет задачи выбранного курса.
4. Плагин открывает стартовую задачу (resume или первая подходящая).
5. Параллельно в фоне догружаются:
- задачи остальных курсов;
- материалы уроков по порядку.

6. Проверка:
1. `./gradlew test` — PASS.
2. `./gradlew buildPlugin` — PASS.

## Update 2026-05-05 — task context binding and module/lesson list grouping

1. Что было проблемой:
- в отдельных стартовых сценариях задача могла быть открыта фоново, но правая панель не обновлялась немедленно;
- пользователь видел пустой statement-блок и при нажатии `AI-подсказка` получал `Задача недоступна`;
- список задач отображался плоско, без явного визуального разделения на модули и уроки.

2. Что изменено:
1. `CurrentTaskService` расширен реактивным состоянием:
- добавлен `StateFlow<CurrentTaskContext?>`;
- `setCurrentTask(...)` теперь публикует обновление в поток;
- добавлен `clear()` для явной очистки состояния.
2. `PlatformToolWindowPanel` подписан на `CurrentTaskService.state()`:
- при любом изменении текущей задачи (включая auto-open) панель statement обновляется автоматически через `setTaskDetails(...)`.
3. `TaskManager.refreshAll()`:
- startup auto-open перенесен ближе к моменту готовности выбранного курса, до полной фоновой догрузки остальных курсов.
4. `TaskListPanel` и `TaskListRenderer`:
- список задач перестроен в иерархию `Модуль -> Урок -> Задачи`;
- добавлены header-элементы модулей и уроков;
- клик по пустой области/заголовкам не открывает задачу;
- открытие выполняется только для task-элементов.

3. Почему сделано именно так:
1. Реактивная привязка контекста задачи к UI исключает рассинхрон между background open и отображением.
2. Ранний startup auto-open уменьшает окно, в котором action-кнопки могут работать без выбранной задачи.
3. Иерархия списка повышает ориентируемость в длинных курсах и делает структуру обучения читаемой.

4. Проверка:
1. `./gradlew test` — PASS.
2. `./gradlew buildPlugin` — PASS.

## Update 2026-05-05 — remaining gap closure package (stability + scale + run/submit hardening)

1. Цель изменения:
- закрыть оставшиеся продуктовые пробелы после предыдущих фиксов;
- сделать поведение плагина устойчивым на больших курсах;
- убрать регресс-риск в прогрессе задач и в отправке решений.

2. Исправление статусов задач и прогресса:
1. В `HttpPlatformApiClient` исправлено маппирование `Task.status`:
- теперь статус берется из API-полей `status/taskStatus/progressStatus/state` и маппится через `TaskStatus.fromApi(...)`;
- `locked/unavailable` по-прежнему имеют приоритет и корректно пробрасываются в статус.
2. Добавлен best-effort `markTaskInProgress(...)`:
- сначала используется целевой endpoint `/tasks/{taskId}/progress/in-progress`;
- при `404/405/501` идет fallback на legacy-варианты (`/progress/start`, `/progress`, `/in-progress`, `/start`);
- при `401/403` ошибка не скрывается.

Почему так:
1. До фикса плагин часто показывал все задачи как `NEW`, что искажало прогресс.
2. Mark-in-progress ранее был заглушкой и не отправлял факт старта задачи на backend.

3. Масштабируемый cache-storage для больших курсов:
1. Добавлен `PluginCacheStorage` (disk-backed cache в системной директории IDE).
2. `CourseCache`, `TaskCache`, `LessonCache` переведены на файловый JSON:
- чтение сначала из file-cache;
- fallback на legacy JSON из `PlatformSettings` (для миграции старых установок);
- при успешной миграции legacy JSON очищается.
3. `PlatformSettings.clearLocalCache()` теперь очищает и disk-cache.

Почему так:
1. Хранение больших JSON в `PersistentState` увеличивает размер XML-настроек IDE и ухудшает скорость на курсах с большим числом задач/уроков.
2. File-cache снижает давление на XML storage и повышает устойчивость при больших объемах данных.

4. Hardening submit path:
1. В `SubmissionService` устранены silent-return сценарии:
- если нет auth или нет текущей задачи, `onResult` всегда получает явную ошибку.
2. Добавлена защита от дублированного submit:
- одновременно разрешен только один submit (`submissionInProgress` guard).
3. Добавлены timeout-контуры:
- `submitSolution` обернут в `withTimeout`;
- polling запросы также ограничены timeout.
4. Исправлена клиентская мета-информация submit:
- версия плагина теперь берется runtime из `PluginRuntimeInfo` (а не hardcoded `0.1.0`);
- platform name тоже runtime.
5. `SubmissionFileCollector` усилен лимитами:
- максимум файлов на отправку;
- лимит на размер одного файла;
- лимит на суммарный payload;
- порядок файлов детерминирован (sorted) для стабильного поведения.

Почему так:
1. До фикса можно было получить “зависшую кнопку” без обратной связи.
2. Для очень больших курсов/решений отсутствовали предохранители против oversized payload.

5. Hardening загрузки и sync:
1. `TaskManager.openTask()`:
- `getTaskDetails` и `getTaskTemplate` теперь ограничены timeout.
2. Фоновый prefetch lesson materials:
- добавлен лимит на число уроков за один refresh cycle, чтобы не создавать burst-нагрузку на больших курсах.
3. `TaskManager.loadRemainingCourseTasks()`:
- больше не перезаписывает user-selected курс эвристикой после фоновой догрузки.
4. `SyncService.startAutoSync()`:
- добавлен guard от повторного запуска автосинк-цикла.

Почему так:
1. Это убирает часть причин долгих “подвисаний” и непредсказуемых переключений курса.
2. Guard от повторного автоцикла предотвращает избыточные сетевые и CPU-циклы.

6. Local run path в PyCharm:
1. Добавлен `PythonRunConfigurationProvider`:
- для задач `PYTHON` создается Python Run Configuration через runtime-reflection API PyCharm;
- выставляются script path и рабочая директория задачи.
2. Если Python run-конфиг не может быть создан:
- пользователь получает controlled ошибку с причиной;
- fallback-поведение не приводит к падению ToolWindow.

Почему так:
1. Ранее run/debug всегда сваливался в unsupported-provider даже для Python.
2. Это возвращает рабочий локальный запуск для целевого сценария PyCharm + Python.

7. UI/auth consistency:
1. В `PlatformToolWindowPanel` при переходе в unauthorized состояние дополнительно очищается `CurrentTaskService`, чтобы не оставался stale task-context.

8. Технические файлы изменений:
1. `src/main/kotlin/com/leonovcare/plugin/api/HttpPlatformApiClient.kt`
2. `src/main/kotlin/com/leonovcare/plugin/api/PlatformEndpointMapping.kt`
3. `src/main/kotlin/com/leonovcare/plugin/cache/PluginCacheStorage.kt`
4. `src/main/kotlin/com/leonovcare/plugin/cache/CourseCache.kt`
5. `src/main/kotlin/com/leonovcare/plugin/cache/TaskCache.kt`
6. `src/main/kotlin/com/leonovcare/plugin/cache/LessonCache.kt`
7. `src/main/kotlin/com/leonovcare/plugin/settings/PlatformSettings.kt`
8. `src/main/kotlin/com/leonovcare/plugin/submission/SubmissionFileCollector.kt`
9. `src/main/kotlin/com/leonovcare/plugin/submission/SubmissionService.kt`
10. `src/main/kotlin/com/leonovcare/plugin/run/TaskRunConfigurationService.kt`
11. `src/main/kotlin/com/leonovcare/plugin/util/PluginRuntimeInfo.kt`
12. `src/main/kotlin/com/leonovcare/plugin/task/TaskManager.kt`
13. `src/main/kotlin/com/leonovcare/plugin/sync/SyncService.kt`
14. `src/main/kotlin/com/leonovcare/plugin/ui/PlatformToolWindowPanel.kt`
15. `src/main/resources/messages/PlatformBundle.properties`
16. `src/main/resources/messages/PlatformBundle_ru.properties`

9. Тесты:
1. `./gradlew test` — PASS.
2. `./gradlew buildPlugin` — PASS.
3. Добавлены/обновлены unit-tests:
- `HttpPlatformApiClientTest` (fallback mark-in-progress);
- `HttpPlatformApiClientLanguageTest` (status mapping from tasks-catalog);
- `SubmissionFileCollectorTest` (too-many-files guard).
