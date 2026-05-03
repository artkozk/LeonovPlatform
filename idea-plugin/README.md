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
