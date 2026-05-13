# Архитектура Leonov Care

## 1. Общая схема

- `frontend` (React): UI для ученика и админа.
- `backend/cmd/server` (Go/Gin): REST API.
- `backend/cmd/worker` (Go): обработка очереди submission.
- `PostgreSQL`: доменные данные.
- `Redis`: очередь задач проверки.

## 2. Поток проверки решения

1. Пользователь отправляет код (`POST /tasks/:id/submissions`).
2. API валидирует лимиты тарифа и attempts.
3. Submission создается со статусом `queued`.
4. Job помещается в Redis queue `submission_jobs`.
5. Worker забирает job и запускает Java check.
6. Worker обновляет submission (status/score/feedback).
7. При `accepted` начисляет XP и проверяет ачивки.
8. Frontend опрашивает `GET /submissions/:id` и показывает результат.

## 3. Поток подписки

1. Пользователь выбирает тариф.
2. API создает payment запись.
3. При отсутствии merchant id ставит `pending_config`.
4. После webhook `paid` активируется выбранный план.

## 4. Поток AI-подсказки (OpenAI)

1. Пользователь на странице задачи нажимает `AI подсказка`.
2. Frontend отправляет `POST /api/v1/ai/task-hint` с `taskId` и текущим кодом.
3. Backend проверяет entitlement тарифа (`has_personal_hints`) и роль пользователя.
4. При доступе формируется педагогический prompt (без выдачи полного готового решения).
5. Запрос отправляется в OpenAI Chat Completions API.
6. Ответ и usage логируются в `ai_hint_requests`.
7. Подсказка возвращается в UI.

## 5. Модель масштабирования

1. Горизонтально масштабируем API.
2. Добавляем воркеры по CPU.
3. Redis гарантирует decoupling API/execute.
4. При росте нагрузки Java checker выносится в отдельный isolated runner-контур.

## 6. Почему решения именно такие

- Воркеры и очередь выбраны, чтобы API оставался быстрым при тяжелых проверках.
- PostgreSQL + Redis закрывают транзакционность и realtime-очереди с минимальным операционным риском.
- Четкий API-контракт одинаково обслуживает Web и IntelliJ plugin.
- AI-подсказки не вшиты в judge-пайплайн, чтобы сохранить независимость критического пути проверки решений от внешнего LLM API.

## 7. Auth и прогресс

1. OAuth Google:
- backend валидирует Google `id_token` через `tokeninfo`
- требует `email_verified=true`
- связывает аккаунт через `oauth_accounts(provider, provider_user_id)`.

2. Хранение прогресса:
- `submissions` — история попыток по задачам
- `xp_events` — начисления XP
- `users.level/xp/streak` — агрегированное состояние ученика
- `user_achievements` — открытые достижения.

## 8. UI архитектура и design system

1. Корневой UI-каркас построен вокруг top-header shell (без тяжелого постоянного sidebar).
2. Светлая/темная темы реализуются через единые токены (`data-theme` + CSS variables), а не точечные перекрасы страниц.
3. Детальная спецификация токенов, компонентных правил и responsive-логики вынесена в:
- `docs/architecture/DESIGN_SYSTEM_V3_2026_04_23.md`

## 9. Launch профиль (2026-04-29)

1. OAuth входы удалены из active router и выключены на уровне пользовательского UI.
2. Модель аккаунта расширена:
- `first_name`
- `last_name`
- `nickname` (unique)
- `public_id`
3. Демо Java-курс `java-start` удален, auto-seed по умолчанию выключен.
4. Почему это сделано:
- запуск на реальных учениках требует реальных метрик и предсказуемой auth-модели без частично настроенного OAuth.

## 10. Актуализация от 2026-05-02: light-only UI без Settings screen

1. Историческая запись в разделе 8 про светлую/темную тему оставлена как контекст прошлой реализации. Текущее состояние продукта: поддерживается только светлая тема.
2. Причина изменения:
- dark-mode выглядел визуально хуже основной темы;
- поддержка двух палитр увеличивала риск регрессий без пользы для учебного сценария;
- настройки были вторичным экраном и отвлекали от обучения, задач, проверок и подписки.
3. Frontend теперь не содержит маршрута `/settings`, ссылки `Настройки` в profile-menu и карточки `Настройки` на `/profile`.
4. Backend сохраняет поле `theme` в профиле ради совместимости API, но возвращает и сохраняет только `light`.
5. Миграция `024_light_theme_only.sql` приводит существующие записи и default `user_settings.theme` к `light`, чтобы production-данные не могли снова включить тёмную ветку.

## 11. Актуализация от 2026-05-13: прогресс обучения и счётчики (фактическая модель)

1. Историческая запись раздела 7 про “хранение прогресса” не удаляется, но для учебного lesson/block прогресса она неполная.
2. Фактическое текущее поведение:
- lesson/block completion в web-UI хранится преимущественно в `localStorage` (`lc_lesson_progress_*`);
- backend endpoint `GET /lessons/:lessonID` не возвращает готовый completion-state пользователя по блокам;
- `quiz-check` проверяет ответы, но не пишет durable progress-state в БД.
3. Из-за этого разные экраны (`Lesson`, `Courses`, `Dashboard`) используют разные вычисления и источники данных для “прогресса”.
4. Дополнительный важный факт:
- при очистке auth-токенов frontend удаляет user-scoped storage, включая lesson progress.
5. Текущая реализация `users.streak` в backend отражает серию accepted-submission подряд, а не календарную серию дней.
6. Подробный разбор причин и следствий зафиксирован в:
- `docs/operations/CRITICAL_LEARNING_ROOT_CAUSE_AUDIT_2026_05_13.md`.

## 12. Актуализация от 2026-05-13: canonical progress model (после remediation)

1. Историческая запись раздела 11 остаётся как фиксация состояния до исправления.
2. Текущее целевое состояние после remediation:
- completion lesson block хранится в БД в `user_lesson_block_progress`;
- `GET /lessons/:lessonID` возвращает `progress` snapshot и `blocks[].completed`;
- `GET /courses/:courseID` возвращает per-lesson `completedBlocks/totalBlocks/progressPercent`.
3. Worker и quiz flow синхронизированы с canonical model:
- accepted submission пишет completion через server-side upsert;
- quiz pass фиксирует completion через тот же доменный модуль.
4. Web UI (`Lesson/Courses/Dashboard/Tasks`) убран с localStorage completion и использует серверные статусы и агрегаты.
5. Семантика streak нормализована:
- streak считается как серия календарных дней активности;
- добавлено поле `users.streak_last_active_day`;
- stale streak не показывается как активный.
6. Подробный поэтапный отчёт по симптомам, причинам и системным решениям:
- `docs/operations/CANONICAL_PROGRESS_REMEDIATION_2026_05_13.md`.
