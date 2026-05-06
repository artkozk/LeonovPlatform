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
