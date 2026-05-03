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
