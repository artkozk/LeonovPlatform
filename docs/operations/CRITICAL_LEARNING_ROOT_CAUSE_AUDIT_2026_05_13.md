# Critical Learning Root-Cause Audit (2026-05-13)

## 1. Цель и границы

1. Цель этого документа: дать **системный root-cause анализ** по 7 критичным багам обучения без точечных костылей.
2. Исправления кода в этом цикле **не выполнялись**. Выполнен только технический аудит причин и архитектурных разрывов.
3. Источники фактов:
- сообщения пользователя и скриншоты от 2026-05-12 и 2026-05-13;
- frontend/backend/migrations текущей ветки;
- текущая архитектурная и операционная документация проекта.

## 2. Нормализованный список багов (в общей формулировке)

1. Прогресс обучения слетает (нестабилен между сессиями/днями/устройствами).
2. Счётчики обучения работают некорректно (серия, XP-прогресс до уровня и related metrics).
3. Результаты тестовых шагов не фиксируются как устойчиво завершённые.
4. Визуальная фиксация прохождения шагов (галочки/статусы) расходится с фактом приёмки решений.
5. Процентные индикаторы прогресса не отражают реальное состояние обучения.
6. Переход на следующий шаг не управляет фокусом/scroll-позицией и ломает сценарий чтения.
7. Тексты и сигналы интерфейса местами не соответствуют каналу пользователя (язык/видимость/контекст шага project).

## 3. Главный архитектурный вывод

1. В системе нет единого источника истины для прогресса урока.
2. Прогресс одного и того же учебного состояния распилен на независимые контуры:
- `submissions/xp/users.streak` в БД (backend);
- `completedBlocks` в `localStorage` (frontend lesson/courses/dashboard);
- отдельные plugin endpoints (`/tasks/:taskID/progress/in-progress`, `/sync`), которые web-frontend не использует.
3. Из-за этого любые симптомы выглядят “случайными”, но причина общая: разные экраны показывают разные модели “прогресса”.

## 4. Фактическая карта реализации (как работает сейчас)

### 4.1 Lesson completion хранится на клиенте

1. В `LessonPage` completion шагов хранится и читается из `localStorage`:
- `progressStorageKey` и `localStorage.getItem(progressStorageKey)` в [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:493), [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:505);
- запись completion через `localStorage.setItem(progressStorageKey, ...)` в [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:535).
2. Серверный endpoint урока не возвращает state completion:
- `GET /lessons/:lessonID` возвращает только `lesson/tasks/blocks` в [handlers_learning.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_learning.go:677).

### 4.2 Quiz результат не персистится на backend

1. `POST /lessons/:lessonID/quiz-check` только проверяет и возвращает статус/failed IDs:
- [quiz_handlers.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\quiz_handlers.go:90), [quiz_handlers.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\quiz_handlers.go:154).
2. Нет записи результата квиза в БД (нет таблицы progress по block/lesson и нет side-effect записи в `CheckLessonQuiz`).

### 4.3 Dashboard/Courses считают прогресс тоже из localStorage

1. `CoursesPage` читает прогресс урока через `readLessonProgress` из browser storage:
- [CoursesPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\CoursesPage.tsx:53), [CoursesPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\CoursesPage.tsx:58).
2. `DashboardPage` строит “Текущий курс” по `buildLessonProgressKey` + `localStorage.getItem(...)`:
- [DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:122), [DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:125).

### 4.4 Очистка токенов удаляет весь клиентский прогресс

1. `clearTokens()` очищает не только auth, но и user-scoped storage с прогрессом:
- [client.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\api\client.ts:201), [client.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\api\client.ts:206), [userScopedStorage.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\utils\userScopedStorage.ts:21).
2. В `auth.bootstrap` при неуспешном `apiMe` выполняется `clearTokens()`:
- [auth.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\store\auth.ts:66), [auth.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\store\auth.ts:73).
3. Следствие: любой auth-сбой/refresh-fail/проблема сети может снести локальный lesson-progress полностью.

### 4.5 Серия (`streak`) реализована как “серия сабмитов”, не “серия дней”

1. В worker при `accepted` делается `streak = streak + 1`:
- [worker.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\worker.go:332).
2. При любом не-accepted результате делается `streak = 0`:
- [worker.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\worker.go:340).
3. Это математически не “дни подряд”, а “успешные проверки подряд без единой ошибки”.

### 4.6 Прогресс-бары считают разные сущности

1. В side-stepper lesson прогресс-бар считает позицию активного шага, а не completion:
- `sidebarProgressPercent` через `activeStepNumber` в [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:761), [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:764).
2. При этом рядом показывается `completedStepsCount`, то есть в одном блоке сразу две разные модели прогресса:
- [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:757), [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:1016).

### 4.7 Контент project-шага ориентирован на file-workflow, а web-экран даёт single-file editor

1. Шаг `Три строки` требует `main.py` + `README.md` и описывает запуск через CLI:
- [035_reseed...sql](C:\prog\Comercial\LeonovCarePlatform\backend\migrations\035_reseed_python_zero_v18_http_api_alignment.sql:752), [035_reseed...sql](C:\prog\Comercial\LeonovCarePlatform\backend\migrations\035_reseed_python_zero_v18_http_api_alignment.sql:755).
2. Source policy для той же задачи: `checker_type=ide_plugin`, required files `main.py`, `README.md`:
- [035_reseed...sql](C:\prog\Comercial\LeonovCarePlatform\backend\migrations\035_reseed_python_zero_v18_http_api_alignment.sql:461).
3. Web-страницы `LessonPage/TaskPage` не предоставляют файловый workspace и multi-file UX.
4. Backend частично “достраивает” обязательные файлы автоматически:
- [handlers_learning.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_learning.go:930), [handlers_learning.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_learning.go:1041), [handlers_learning.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_learning.go:1094).
5. Это маскирует mismatch и усиливает непонимание у новичка (“что/где запускать”).

## 5. Разбор 7 багов по root cause

### 5.1 Прогресс слетает

1. Прямая причина: уроковый прогресс клиентский (`localStorage`), не серверный.
2. Усилитель дефекта: при `clearTokens()` очищается `lc_lesson_progress_*`.
3. Архитектурный дефект: отсутствие durable server-side lesson progress модели.
4. Зона риска шире одного бага: любой метрик/экран, читающий lesson progress из storage, подвержен тем же потерям.

### 5.2 Счётчики обучения сломаны

1. `streak` в backend реализован как серия принятых сабмитов, а не серия календарных дней.
2. Любая неуспешная попытка обнуляет `streak`, даже если в тот же день пользователь продуктивно учился.
3. В dashboard `xpInLevel = xp % 100` и `xpToNextLevel = 100 - xpInLevel` ([DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:162), [DashboardPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\DashboardPage.tsx:167)) не совпадает с backend-формулой level в worker (`sqrt((xp + reward)/120)`), что создаёт несогласованность счётчиков.

### 5.3 Результаты тестов не сохраняются

1. `quiz-check` не сохраняет server-side completion, только возвращает ответ в runtime.
2. В `LessonPage` при загрузке урока quiz-состояния сбрасываются:
- `setQuizAnswers({})`, `setQuizCheckState({})` в [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:551), [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:552).
3. Итог: даже корректно пройденный тест не имеет устойчивого источника статуса.

### 5.4 Нет галочек на части шагов при принятых заданиях

1. Галочка шага зависит от локального `completedBlocks[block.id]` в `LessonPage`.
2. Если задача решена вне этого контекста (например, через `/tasks`) или accepted получен позже после выхода из шага, lesson-step marker не синхронизируется с БД submissions.
3. Backend знает факт accepted в `submissions`, но lesson UI его не использует.
4. Это не дефект “конкретно шагов 4..10”, это дефект модели связи `submission -> lesson_block completion`.

### 5.5 Процентная шкала не отражает реальное состояние

1. В Lesson side-stepper полоса прогресса строится по **активному шагу**, а не по завершённым шагам.
2. В Courses percent округляется до целого по большим denominator (`Math.round`), поэтому ранний прогресс может визуально давать `0%` длительное время.
3. Между экранами используются разные semantics процента, поэтому пользователь видит противоречивые цифры.

### 5.6 Переход “Дальше” открывает низ страницы

1. На `onClick` Next изменяется только индекс шага:
- [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:1474).
2. Нет `scrollTo`/focus-reset к началу контента нового шага.
3. В результате при переходе с code-блока пользователь остаётся в нижней части нового шага.

### 5.7 Английское premium-сообщение и неочевидный project-шаг

1. Backend отдает `error: "ai hints are available only for Premium plan"`:
- [handlers_ai.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_ai.go:122).
2. Frontend переводит только паттерн `upgrade_required`, а не весь error contract, поэтому в ряде путей англоязычный текст доходит до UI.
3. Project-step контент написан в терминах file/CLI/README, но web-flow визуально single-editor; канал-ориентированной адаптации контента нет.

## 6. Что не удалось детерминированно подтвердить в этом цикле

1. Не проведён live E2E прогон на production-базе с реальным аккаунтом пользователя для каждого скрина-перехода.
2. Для кейса “с 4 по 10” есть подтверждённый архитектурный разрыв, но конкретный триггер конкретной сессии мог быть:
- очистка auth/storage;
- решение задач в другом экране;
- завершение проверки после выхода со страницы;
- комбинация всех трёх факторов.
3. Эти гипотезы не включаются в будущий prompt как “факт”, пока не подтверждены production trace.

## 7. Архитектурный масштаб дефекта (почему это критично)

1. Дефекты не изолированы в одном компоненте: они сквозные между `LessonPage`, `CoursesPage`, `DashboardPage`, auth lifecycle, worker scoring и content seed.
2. Точечные правки в одном месте дадут временный эффект и новые рассинхроны.
3. Нужна единая прогресс-модель уровня платформы, иначе любые новые курсы/экраны будут воспроизводить тот же класс багов.

## 8. Что считать “искоренением” (критерии для следующего этапа исправлений)

1. Один canonical progress source-of-truth на backend для lesson/block/task/quiz completion.
2. Явные агрегаторы для dashboard/courses/lesson, которые читают только canonical model.
3. Счётчики day-streak отделены от submission streak и считаются по календарным правилам.
4. Контент project-типов разведен по каналам (web vs IDE-plugin) с валидатором совместимости.
5. Localization contract для пользовательских ошибок должен быть строгим и одноязычным.
6. Навигация по шагам должна принудительно восстанавливать focus/scroll к началу нового контента.

## 9. История документа

1. v1.0 (2026-05-13): первичный root-cause аудит по 7 критичным багам обучения, без внесения кодовых исправлений.

## 10. Дополнительная верификация (v1.1, 2026-05-13)

### 10.1 Подтверждённый дефект state-machine отправки в LessonPage

1. `LessonPage` завершает polling, когда статус submission становится любым, кроме `queued`:
- [LessonPage.tsx](C:\prog\Comercial\LeonovCarePlatform\frontend\src\pages\LessonPage.tsx:869).
2. Worker штатно переводит статус `queued -> processing` до финализации проверки:
- [worker.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\worker.go:251).
3. Следствие:
- на статусе `processing` LessonPage преждевременно прекращает ожидание;
- `markBlockCompleted` вызывается только при немедленном `accepted` в рамках этого же цикла;
- если финальный `accepted` приходит позже, галочка и локальный completion не фиксируются.
4. Это объясняет класс симптомов “решение принято, но шаг/процент не обновились”.

### 10.2 Подтверждённый разрыв каналов web и plugin для прогресса задач

1. Backend имеет отдельные endpoint'ы progress-контракта (`in-progress`, `reset`, `sync`):
- [router.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\router.go:89),
- [handlers_plugin_contract.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_plugin_contract.go:163).
2. Этот контур пишет в `user_task_open_progress` (таблица плагинного прогресса):
- [034_plugin_task_open_progress.sql](C:\prog\Comercial\LeonovCarePlatform\backend\migrations\034_plugin_task_open_progress.sql:5).
3. Web Lesson/Courses/Dashboard не используют этот контур и опираются на `localStorage` completion map.
4. Следствие:
- прогресс plugin-канала и прогресс web-канала не сводятся в единый источник истины;
- визуальные статусы зависят от канала, в котором был выполнен шаг.

### 10.3 Подтверждённый дефект агрессивной очистки progress при auth-сбоях

1. При bootstrap любой неуспешный `apiMe` ведёт к `clearTokens()`:
- [auth.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\store\auth.ts:67),
- [auth.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\store\auth.ts:73).
2. `clearTokens()` удаляет не только токены, но и user-scoped storage c lesson progress:
- [client.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\api\client.ts:201),
- [userScopedStorage.ts](C:\prog\Comercial\LeonovCarePlatform\frontend\src\utils\userScopedStorage.ts:21).
3. Следствие:
- transient auth/network/bootstrap инцидент может вызвать “слёт прогресса” даже без ошибки пользователя.

### 10.4 Гипотеза, требующая production-trace (не помечается как факт)

1. Refresh token в backend одноразово ротируется (старый удаляется при refresh):
- [handlers_auth.go](C:\prog\Comercial\LeonovCarePlatform\backend\internal\app\handlers_auth.go:273).
2. При multi-tab сценариях одна вкладка может успеть обновить refresh token раньше другой; отстающая вкладка получит `401` на refresh и вызовет `forceAuthRedirect -> clearTokens`.
3. Эта гипотеза не утверждается как основной факт по инциденту без production логов, но технически согласуется с observed-классом “прогресс исчез”.

### 10.5 Обновлённый статус документа

1. v1.1 (2026-05-13): добавлены дополнительные подтверждения по state-machine submission, каналам прогресса и auth lifecycle; гипотеза multi-tab refresh помечена отдельно как непроверенная.

## 11. Статус после системного remediation (v2.0, 2026-05-13)

### 11.1 Что закрыто системно

1. Отсутствие единого source of truth для lesson progress закрыто canonical таблицей `user_lesson_block_progress`.
2. Разрыв state-machine polling (`processing`) закрыт в lesson flow и worker-side completion sync.
3. Разрыв контракта квизов по `minScorePercent` закрыт на backend parser/scoring уровне.
4. Разрыв Tasks/Courses/Dashboard по источникам данных закрыт переходом на серверные статусы и агрегаты.
5. Разрушение прогресса при transient auth/network инцидентах сокращено статусно-ориентированным lifecycle очистки сессии.
6. Семантика streak переведена на модель календарных дней (`streak_last_active_day` + daily logic).

### 11.2 Что осталось вне scope этого remediation

1. Канальная адаптация project-контента (web vs IDE plugin) и onboarding-инструкции для нулевого пользователя.
2. Унификация текста premium-сообщений на backend error-contract уровне.

### 11.3 Подробная реализация и верификация

1. Детальный этапный отчёт вынесен в:
- `docs/operations/CANONICAL_PROGRESS_REMEDIATION_2026_05_13.md`.
