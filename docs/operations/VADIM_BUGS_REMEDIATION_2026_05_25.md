# Vadim Bugs Remediation — 2026-05-25

## Scope and Rules

- В работу взяты только репорты Вадима из support с визуальными артефактами.
- Сообщение про рост уровня (L1/L2) за баг не принято по продуктному правилу.
- Исправления выполнены так, чтобы не было формулировок, перекладывающих ответственность на «систему проверки».

## Ticket-by-ticket Verdict

### 1) Повреждённый title урока и поломанный practice-блок Java-курса

- Verdict: **реальный баг**.
- Симптом:
  - lesson title аномальной длины (до 8128 символов) с навигационным хвостом (`Последнее обновление`, `Назад/Содержание/Вперед`);
  - в practice-секции ломался `Коротко` (вставлялся повреждённый title).
- Root cause:
  - в импорт попал служебный хвост страницы при парсинге;
  - валидация на длину/маркеры заголовка и порчу `Коротко` была недостаточной.
- Fix:
  - усилена санитизация заголовков и practice short-intro в генераторе;
  - добавлена data-remediation миграция `040_java_zero_core_content_remediation.sql` для прод-исправления уже загруженных данных;
  - обновлён `материалы/java_metanit_v1/course_import.json`.

### 2) Ссылки на источник в theory

- Verdict: **реальный баг**.
- Симптом:
  - в student-facing theory присутствовали строки `Источник: ...`.
- Root cause:
  - regex удаления source-строк покрывал не все варианты markdown-обрамления (`**Источник:**`).
- Fix:
  - поправлены regex в генераторе, валидаторе и фронтовой нормализации markdown;
  - массово очищены source-строки в `course_import.json`;
  - в prod добавлена SQL-remediation в миграции `040`.

### 3) Квиз: список ответов не закрывался корректно / визуальная геометрия dropdown

- Verdict: **реальный баг**.
- Симптом:
  - список мог зависать в открытом состоянии при пользовательских сценариях;
  - визуально список воспринимался уже trigger-блока.
- Root cause:
  - нестабильная комбинация поведения кастомного select + геометрии контейнера меню.
- Fix:
  - сохранено требуемое поведение «варианты поверх вопросов»;
  - скорректирована геометрия `.custom-select-menu` и `.custom-select-option` (ширина меню = ширине trigger, корректные radius/padding);
  - сохранено закрытие по outside-click / Escape / toggle.

### 4) Тексты ошибок проверки с намёком «не в системе проверки»

- Verdict: **реальный UX-баг**.
- Симптом:
  - формулировка выглядела как оправдание платформы.
- Root cause:
  - слишком категоричный текст в UI-слое ошибок.
- Fix:
  - в текущей реализации используются нейтральные формулировки без противопоставления «ваш код vs система»;
  - проверено поиском по коду: таких текстов в runtime-страницах нет.

### 5) AI-подсказка «не работает» после завершения проверки

- Verdict: **реальный баг UX/контракта**.
- Симптом:
  - для Free-пользователя при `upgrade_required` показывался общий текст «Не удалось получить AI-подсказку», вместо явного Premium-gate.
- Root cause:
  - frontend проверял только `error`-строку, а признак `upgrade_required` приходит в поле `status`.
- Fix:
  - обработка ошибок AI-hint обновлена в `TaskPage` и `LessonPage`: учитываются и `status`, и текст ошибки;
  - теперь пользователь получает корректное сообщение про Premium.

### 6) «Даунгрейд» support-функционала

- Verdict: **реальный баг релизной линии**.
- Симптом:
  - в текущей линии отсутствовали core backend/frontend части support, несмотря на ожидание прод-функционала.
- Root cause:
  - ветка разошлась с `main` до коммита feature support и не подтянула этот срез полностью.
- Fix:
  - support-функционал восстановлен точечным переносом модулей backend/frontend + миграция `039_support_chat_core.sql` + маршрутизация + конфиг + lifecycle hub.

## Implemented Artifacts

- Data and generation:
  - `материалы/java_metanit_v1/course_import.json`
  - `материалы/java_metanit_v1/build_course.py`
  - `материалы/java_metanit_v1/validate_course.py` (через validate_course из build_course)
  - `backend/tools/validate_java_metanit_v1_import.js`
  - `backend/tools/generate_java_metanit_v1_migration.js`
- Migrations:
  - `backend/migrations/039_support_chat_core.sql`
  - `backend/migrations/040_java_zero_core_content_remediation.sql`
- Frontend UX:
  - `frontend/src/pages/LessonPage.tsx`
  - `frontend/src/pages/TaskPage.tsx`
  - `frontend/src/styles/global.css`
- Support recovery:
  - `backend/internal/app/handlers_support_admin.go`
  - `backend/internal/app/handlers_support_student.go`
  - `backend/internal/app/support_messages.go`
  - `backend/internal/app/support_store.go`
  - `backend/internal/app/support_types.go`
  - `backend/internal/app/support_realtime.go`
  - `backend/internal/app/router.go`
  - `backend/internal/app/middleware.go`
  - `backend/internal/app/types.go`
  - `backend/internal/config/config.go`
  - `frontend/src/pages/SupportPage.tsx`
  - `frontend/src/pages/AdminSupportPage.tsx`
  - `frontend/src/api/support.ts`
  - `frontend/src/api/supportAttachments.ts`
  - `frontend/src/App.tsx`
  - `frontend/src/components/AppLayout.tsx`

## Anti-regression Validation

### Automated

- `python материалы/java_metanit_v1/validate_course.py` — PASS.
- `node backend/tools/validate_java_metanit_v1_import.js` — PASS.
- `go test ./...` (backend) — PASS.
- `npm test -- --watch=false` (frontend) — PASS.
- `npm run build` (frontend) — PASS.

### Data sanity (Java)

- Проверка `course_import.json`:
  - `badTitle = 0`
  - `badTheory source lines = 0`
  - `badPractice = 0`

## Why this implementation

- Исправление выполнено по первопричине (данные + генерация + валидации + прод-remediation), а не только косметикой UI.
- Для support возвращён полный контракт feature, чтобы исключить частично-рабочее состояние.
- Проверки собраны так, чтобы зафиксировать отсутствие регрессий до деплоя.
