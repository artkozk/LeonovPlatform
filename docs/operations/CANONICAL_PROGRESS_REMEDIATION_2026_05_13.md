# Canonical Progress Remediation (2026-05-13)

## 1. Цель

1. Закрыть класс критичных багов прогресса обучения системно, а не точечно.
2. Убрать дубли источников истины между backend, frontend и локальным хранилищем.
3. Зафиксировать архитектурные решения и их проверку в формате, пригодном для ревью и дальнейшей поддержки.

## 2. Целевая архитектура единого прогресса

### 2.1 Canonical source of truth

1. Источник истины для completion урока: `user_lesson_block_progress`.
2. Источник истины для статусов задач на каталоге задач: backend `tasks-catalog.status`.
3. Источник истины для streak: модель последовательных календарных дней (`streak + streak_last_active_day`), не цепочка сабмитов.

### 2.2 Принцип агрегации UI

1. `Lesson`, `Courses`, `Dashboard` получают пользовательский прогресс только с сервера.
2. Локальное хранилище оставлено только для черновиков кода (`lc_lesson_drafts_*`), не для completion.
3. Любые fallback-состояния с фиктивными цифрами запрещены; используются только честные `loading/empty/error`.

### 2.3 Контракт API после remediation

1. `GET /courses/:courseID` возвращает по урокам:
- `blockCount`, `totalBlocks`, `completedBlocks`, `progressPercent`.
2. `GET /lessons/:lessonID` возвращает:
- `blocks[].completed`;
- `progress.completedBlockIds/completedBlocks/totalBlocks/progressPercent`.
3. Новый endpoint:
- `POST /lessons/:lessonID/blocks/:blockID/complete`.
4. `POST /lessons/:lessonID/quiz-check` возвращает:
- `correctQuestions`, `totalQuestions`, `scorePercent`, `minScorePercent`, `progress`.
5. `GET /submissions/history` расширен контекстом:
- `lessonId`, `lessonTitle`, `courseId`, `courseTitle`.

## 3. Реализация по этапам

### Этап 1. Canonical completion модель в backend и данных

#### Симптом

1. Прогресс шага и урока расходится между экранами и может «теряться».

#### Корневая причина

1. Не было durable server-side модели completion на уровне `user + lesson_block`.
2. Факт принятия решения (`accepted`) не связывался системно с completion lesson block.

#### Архитектурное решение

1. Добавлена таблица `user_lesson_block_progress` миграцией `036_user_lesson_block_progress.sql`.
2. Добавлен backfill из исторических `accepted` submissions в canonical таблицу.
3. В backend добавлен общий модуль:
- `backend/internal/app/progress_model.go`.
4. Добавлен endpoint `POST /lessons/:lessonID/blocks/:blockID/complete`.
5. `GET /lessons/:lessonID` и `GET /courses/:courseID` теперь отдают серверный completion snapshot.

#### Почему решение системное

1. Проблема закрыта на уровне доменной модели, а не на уровне одного экрана.
2. Любой канал (web, worker, quiz, plugin flow) пишет в одну каноническую таблицу.
3. UI перестал вычислять completion из локальных разрозненных источников.

#### Риски и проверка

1. Риск: потеря исторического прогресса при переходе на новую модель.
2. Контрмера: backfill по `accepted` submissions в миграции.
3. Проверка:
- backend тесты `go test ./...` зелёные;
- проверен ответ `GET /lessons/:lessonID` на наличие `progress` и `blocks[].completed`.

### Этап 2. Устранение разрыва state-machine проверки в lesson flow

#### Симптом

1. Проверка «зависает» визуально: решение принято, но completion/галочки не фиксируются.

#### Корневая причина

1. Polling на клиенте завершался на `processing`, а не ждал финального статуса.

#### Архитектурное решение

1. В `LessonPage` polling продолжает ожидание, пока статус `queued` или `processing`.
2. При финальном `accepted` completion фиксируется через серверный endpoint `complete`.
3. В worker на accepted добавлен server-side upsert completion по связанному lesson block.

#### Почему решение системное

1. Закрыт класс гонок между async worker и UI.
2. Completion фиксируется независимо от того, успел ли пользователь остаться на экране.

#### Риски и проверка

1. Риск: двойные side-effects при повторном poll.
2. Контрмера: idempotent upsert в canonical progress + idempotent XP via `xp_events`.
3. Проверка:
- unit/интеграционные backend тесты;
- ручная проверка сценария queued -> processing -> accepted.

### Этап 3. Выравнивание квиз-контракта с контентом (`minScorePercent`)

#### Симптом

1. Квизы оценивались не по правилу контента, а по жёсткому «100% правильных».

#### Корневая причина

1. Поле `minScorePercent` игнорировалось в backend parser/validator.

#### Архитектурное решение

1. В `quiz_handlers.go` добавлен parser `minScorePercent` с нормализацией.
2. Статус correct/wrong рассчитывается по порогу:
- `correctQuestions * 100 >= minScorePercent * totalQuestions`.
3. При успешном прохождении квиза completion пишется в canonical progress.
4. Контракт ответа расширен фактическими метриками (`scorePercent`, `minScorePercent`, `progress`).

#### Почему решение системное

1. Система теперь уважает педагогический контракт материалов, а не локальное UI-правило.
2. Completion квиза и прогресс урока связаны через общую доменную модель.

#### Риски и проверка

1. Риск: несовместимость старых payload.
2. Контрмера: поддержка и single-question, и multi-question формата + default 100%.
3. Проверка:
- `quiz_handlers_test.go` обновлён под `minScorePercent`;
- `go test ./...` зелёные.

### Этап 4. Согласование Tasks/Courses/Dashboard с серверной моделью

#### Симптом

1. Статусы задач и проценты прогресса противоречили факту и между экранами.

#### Корневая причина

1. `TasksPage` пересобирал статус из `submissionHistory LIMIT 100`.
2. `CoursesPage` и `DashboardPage` частично опирались на localStorage/fallback-данные.

#### Архитектурное решение

1. `TasksPage` переведён на server status из `tasks-catalog`.
2. `CoursesPage` переведён на backend `completedBlocks/progressPercent`.
3. `DashboardPage` убраны фиктивные fallback-цифры; контекст строится по серверным данным.
4. `submissionHistory` расширен `lesson/course` полями для корректного контекста.

#### Почему решение системное

1. Все три экрана читают один и тот же источник истины.
2. Убрана зависимость от ограниченной истории отправок и локальных эвристик.

#### Риски и проверка

1. Риск: пустой контекст у новых пользователей без истории.
2. Контрмера: честный empty state вместо фиктивного прогресса.
3. Проверка:
- frontend тесты (`npm run test`) зелёные;
- `npm run build` успешен.

### Этап 5. Устойчивость auth lifecycle к transient сбоям

#### Симптом

1. При сетевых/auth сбоях сессия сбрасывалась агрессивно и приводила к потере клиентского состояния.

#### Корневая причина

1. `bootstrap` и `refreshProfile` вызывали `clearTokens()` на широкий класс ошибок, не только auth-invalid.

#### Архитектурное решение

1. В `frontend/src/store/auth.ts` введено правило:
- очищать сессию только при `401/403` или отсутствии токена;
- при transient ошибках сохранять сессию и показывать диагностическое состояние.

#### Почему решение системное

1. Убран класс ложных logout и каскадных потерь состояния из-за временной нестабильности сети/API.
2. Логика жизненного цикла auth стала статус-ориентированной.

#### Риски и проверка

1. Риск: «подвешенная» сессия при невалидном токене с нетипичным кодом.
2. Контрмера: централизованный `shouldClearAuthSession` и явный кодовый путь.
3. Проверка:
- ручной прогон bootstrap/refresh в dev;
- frontend тесты зелёные.

### Этап 6. Нормализация счетчиков (streak daily semantics)

#### Симптом

1. `streak` не совпадал с пользовательским ожиданием «дней подряд».

#### Корневая причина

1. Модель была «цепочка принятых сабмитов без ошибок», а не календарная серия дней.

#### Архитектурное решение

1. Миграция `037_user_streak_daily_semantics.sql`:
- добавляет `users.streak_last_active_day`;
- backfill streak как длину актуальной последовательности дней.
2. В worker accepted-path:
- streak обновляется функцией `applyAcceptedSubmissionStreak`.
3. В read-модели (`Me`) stale streak скрывается через `streak_visible` semantics.
4. При reset task progress streak не обнуляется слепо, а пересчитывается функцией `recomputeUserStreakFromAcceptedSubmissions`.

#### Почему решение системное

1. Семантика streak зафиксирована на уровне данных и серверного домена.
2. UI получает уже корректную интерпретацию без локальных эвристик.

#### Риски и проверка

1. Риск: edge-cases по UTC границам суток.
2. Контрмера: единый `startOfUTCDay` и UTC-based SQL.
3. Проверка:
- добавлены `progress_model_test.go`;
- backend тесты зелёные.

### Этап 7. UX-согласованность lesson navigation

#### Симптом

1. Кнопка «Дальше» открывала шаг внизу страницы у блока кода.

#### Корневая причина

1. Не было scroll/focus reset при смене lesson block.

#### Архитектурное решение

1. В `LessonPage` добавлен reset scroll для `.lesson-step-content` и `window` при `activeBlockIndex` изменении.

#### Почему решение системное

1. Поведение исправлено на уровне lifecycle перехода шага, независимо от типа блока.

#### Риски и проверка

1. Риск: конфликт с кастомными скролл-контейнерами.
2. Контрмера: двойной reset (container + window) без плавной анимации.
3. Проверка:
- ручной прогон переходов между theory/practice/project шагами.

## 4. Сводная проверка качества

1. `go test ./...` (backend) — успешно.
2. `npm run test` (frontend) — успешно.
3. `npm run build` (frontend) — успешно (есть только non-blocking warning по bundle size).

## 5. Что сознательно не делалось в этом цикле

1. Не вносились контентные правки project-инструкций по web/CLI разделению.
2. Не менялись текстовые локализации премиум-подсказки в backend `handlers_ai.go`.
3. Эти задачи выделяются в следующий отдельный этап, чтобы не смешивать доменную remediation прогресса с content/localization релизом.

## 6. Root-Cause Report (финальный срез по классу багов)

1. Класс ошибки «дубли источников истины прогресса» закрыт переносом completion в server-side canonical model.
2. Класс ошибки «асинхронная гонка статусов проверки» закрыт state-machine выравниванием (`queued/processing/accepted`).
3. Класс ошибки «контракт контента != контракт проверки» закрыт внедрением `minScorePercent`.
4. Класс ошибки «ложные UI-агрегаты» закрыт переходом на серверные статусы/агрегаты и отказом от фиктивных fallback-чисел.
5. Класс ошибки «потеря устойчивости при auth transient» закрыт статусно-ориентированным lifecycle очистки сессии.
6. Класс ошибки «семантическая рассинхронизация счётчиков» закрыт daily streak model и backfill миграцией.

## 7. История документа

1. v1.0 (2026-05-13): полный remediation-документ по canonical progress architecture, backend/frontend/API/data/test/UX изменениям.
