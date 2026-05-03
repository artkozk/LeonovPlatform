# Plugin Validation Report (2026-04-30, v2.59)

## 1. Цель проверки

Подтвердить, что IDEA plugin для Leonov Care Platform готов как рабочая основа для учебного потока, включая:

1. AI-подсказки в IDE.
2. Корректную работу с текущими материалами курса.
3. Сборку и тесты плагина.

## 2. Что проверено

### 2.1 Curriculum coverage (по фактическим миграциям)

Проверка миграций backend (`backend/migrations/*.sql`) показала:

1. Обнаруженные языки задач: `java`, `python` (включая alias `python3`).
2. SQL/JS/Kotlin в текущем seed курсе не обнаружены.

Технический вывод:

1. Production-контент сейчас реально Java+Python.
2. Плагин должен гарантированно работать на этих языках и не падать при появлении новых.

### 2.2 AI endpoint связка

По backend роутам подтвержден endpoint:

1. `POST /api/v1/ai/task-hint` (в `backend/internal/app/router.go`).

По plugin-коду подтверждена клиентская интеграция:

1. API слой: `PlatformApiClient.requestAiHint(...)`, `HttpPlatformApiClient`.
2. Сервис: `AiHintService`.
3. UI: кнопка `AI-подсказка` в task panel и action в меню.

## 3. Прогоны и результаты

### 3.1 IDEA plugin

Команды:

```bash
cd idea-plugin
./gradlew test
./gradlew buildPlugin
```

Результат:

1. `test`: SUCCESS.
2. `buildPlugin`: SUCCESS.

Примечание по окружению:

1. Для Gradle использован JDK 17 (`JAVA_HOME` на локальный JDK17), т.к. системный Java 8 несовместим с `org.jetbrains.intellij.platform` plugin.

### 3.2 Frontend

Команды:

```bash
cd frontend
npm run test -- --run
npm run build
```

Результат:

1. unit tests: PASSED.
2. production build: SUCCESS.

### 3.3 Backend

Команда:

```bash
cd backend
go test ./...
```

Результат:

1. Тестовый прогон в текущем локальном окружении упирается в dependency/setup issues:
- отсутствующие `go.sum` entries для части модулей;
- failure в python judge tests в текущем runtime.

Важно:

1. Это не блокирует сборку IDEA plugin.
2. Для backend CI нужно отдельно стабилизировать Go env + mod state в том же контуре, где происходит production сборка backend.

## 4. Capability summary плагина (текущее состояние)

Плагин сейчас умеет:

1. Авторизация: email/password + token mode, refresh, secure storage через PasswordSafe.
2. Курсы/задачи: загрузка, кэш, открытие в проекте, локальные metadata.
3. Решение: локальный run/debug для Java, submit/check для задач.
4. AI: запрос педагогической подсказки через backend endpoint из IDE.
5. Синхронизация: ручная + авто, offline-friendly cache behavior.
6. Reference solution/style-check/sync fallback поведение без падений при недоступных endpoint.

Ограничения текущего материала:

1. Полный локальный run/debug сейчас реализован для Java.
2. Python задачи поддерживаются в потоке открытия/редактирования/submit/AI.
3. SQL и другие языки добавлены как расширяемый слой маршрутизации (без fake runtime).

## 5. Риск-пометки перед запуском на 1500 учеников

1. Для backend отдельно нужен чистый CI прогон `go test` в production-like окружении.
2. Для Python-heavy потока желательно добавить отдельные plugin integration tests со сценариями `language=PYTHON`.
3. Для SQL-контента при появлении в курсе нужно добавить server judge/contract и локальный execution path в plugin.
