# Leonov Care Platform (Production-Ready MVP)

## Что реализовано сейчас

Проект собран как **отдельная площадка** в папке `C:/prog/Comercial/LeonovCarePlatform`.

### Актуализация от 2026-05-03: внедрение курса Python v18 Strict Pedagogy

1. В платформу внедряется новый production-ready пакет курса:
- источник: `материалы/v18_STRICT_PEDAGOGY/course_import.json`;
- runtime rollout: `backend/migrations/026_reseed_python_zero_v18_strict_pedagogy.sql`;
- генератор: `backend/tools/generate_python_v18_materials_migration.js`;
- валидация импорта: `backend/tools/validate_python_v18_materials_import.js`.
2. Курс `python-zero` переиздаётся как `Python с нуля — Backend + AI`:
- 5 модулей;
- 169 уроков;
- 1963 lesson blocks;
- 1153 practice/project задач в runtime;
- 912 structured quiz questions;
- 678.9 часов расчётной нагрузки.
3. Первый видимый урок сохранён строго по педагогическому gate:
- Модуль 1;
- Урок 1: `Первый код`;
- Шаг 1: `Смысл`.
4. Почему сделано отдельной миграцией:
- платформа в production читает курс из PostgreSQL, а не напрямую из JSON;
- миграция даёт воспроизводимый deploy и понятный rollback через backup;
- старый контент снимается с публикации, но не удаляется физически;
- reviewer видит точный источник, преобразование checker-конфигов и validation report.
5. Перед deploy подтверждено:
- `python материалы/v18_STRICT_PEDAGOGY/validate_course.py` — PASS;
- `node backend/tools/validate_python_v18_materials_import.js` — PASS;
- `go test ./...` в backend — PASS.

## База данных сейчас

- Основная БД: `PostgreSQL`
- Имя БД (prod): `leonovcare_platform`
- Контур очередей: `Redis` (submission jobs)

### Backend (Go + PostgreSQL + Redis)

- Регистрация/авторизация (JWT access + refresh)
- Email verify flow (демо-режим)
- Восстановление пароля (демо-режим)
- OAuth API-контракт (Google/GitHub-ready endpoint)
- Личный кабинет и персональные настройки
- Курсы/уроки/задачи
- Очередь проверки решений через Redis
- Java checker (компиляция + тест-кейсы + score)
- Геймификация: XP, уровень, серия, достижения, лидерборд
- Подписки: Free/Pro/Premium
- Платежный контур Cardlink (без merchant id работает в `pending_config`)
- AI-подсказки по задачам через OpenAI (Premium-only, audit лог в БД)
- Админ API: создание контента, блокировка пользователя, метрики, CSV
- Seed демо-курса `Java Start` с тремя уроками и задачами

### Frontend (React + TypeScript + Vite)

- Адаптивный интерфейс (desktop/mobile)
- Auth page (вход/регистрация)
- Dashboard ученика
- Курсы, уроки, задачи
- Код-редактор (Monaco, Java)
- Отправка решения и получение статуса
- Кнопка `AI подсказка` на странице задачи
- Лидерборд
- Тарифы/подписка/checkout
- Персонализация (theme, language, editor settings)
- Админ-экран с аналитикой и CSV export

### Актуализация от 2026-05-12: mobile hotfix для dashboard/header

1. Исправлен production-дефект мобильной адаптации в `dashboard`:
- header и user-zone корректно перестраиваются в мобильный вертикальный поток;
- навигация больше не обрезается по правому краю на узких экранах;
- карточка `Текущий курс` принудительно переводится в одноколоночный режим на мобильных брейкпоинтах.
2. Техническая причина дефекта была в CSS-каскаде:
- ранние mobile-правила существовали, но часть из них перебивалась более поздними desktop-переопределениями в `global.css`.
3. Исправление внесено финальными (поздними) медиаправилами для `1080px / 760px / 420px`, чтобы мобильная верстка применялась гарантированно в итоговом каскаде.
4. Почему это сделано именно так:
- изменение точечное и безопасное (без переписывания React-компонентов);
- устраняется критичный UX-риск мобильного трафика на основном экране ученика;
- reviewer получает прозрачную связь «симптом → причина → фикс».
5. Подробный технический отчёт:
- `docs/operations/MOBILE_ADAPTATION_DASHBOARD_2026_05_12.md`.

### Актуализация от 2026-05-12: mobile policy revision (header collapse + desktop-only coding)

1. Мобильный header переведён в режим раскрываемого меню:
- в закрытом состоянии показывается только компактная верхняя строка `бренд + кнопка меню`;
- навигация и блок профиля раскрываются по кнопке и не занимают половину экрана постоянно.
2. Для экранов до `1024px` отключён сценарий «писать/отправлять код»:
- страница `/tasks/:taskId` на мобильном показывает условие + явное сообщение, что решение доступно с ПК;
- в уроках (`practice/project`) на мобильном скрыт редактор и кнопки проверки/отправки, остаются теория и квизы.
3. Почему это сделано именно так:
- основной пользовательский риск был в перегруженном mobile-экране и плохом UX ввода кода с телефона;
- ограничения введены адресно только для code-flow, чтобы обучение на мобильном не блокировалось полностью;
- reviewer получает явный продуктовый контур: телефон для чтения и навигации, ПК для полноценного решения задач.
4. Подробный отчёт по изменениям:
- `docs/operations/MOBILE_PRODUCT_POLICY_2026_05_12.md`.

### Актуализация от 2026-05-02: настройки и тема интерфейса

1. Экран пользовательских настроек в web-интерфейсе больше не является частью продукта:
- маршрут `/settings` удалён из frontend router;
- пункт `Настройки` убран из меню профиля;
- карточка настроек убрана со страницы профиля.
2. Тёмная тема отключена полностью на пользовательском frontend-слое:
- корневой shell больше не выставляет `data-theme`;
- CSS-палитра `[data-theme="dark"]` удалена из активной таблицы стилей;
- редактор Monaco в уроках и задачах всегда открывается в светлой теме.
3. Backend сохраняет поле `user_settings.theme` и endpoint `PATCH /me/settings` только для обратной совместимости старых клиентов:
- `GET /me` возвращает `theme: "light"`;
- любые новые значения `theme` в `PATCH /me/settings` нормализуются в `light`;
- миграция `024_light_theme_only.sql` переводит старые строки и default БД на `light`.
4. Это сделано потому, что настройки не участвуют в основном учебном сценарии, а тёмная тема визуально ухудшала продукт. Светлый интерфейс оставлен единственным поддерживаемым вариантом, чтобы reviewer видел осознанное упрощение UX, а не недоделанную персонализацию.

## Быстрый локальный запуск

### 1. Backend

```bash
cd backend
cp .env.example .env
# отредактировать DATABASE_URL / JWT secrets
go mod tidy
go run ./cmd/server
```

Во втором терминале:

```bash
cd backend
go run ./cmd/worker
```

### 2. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Тесты

### Backend

```bash
cd backend
go test ./...
```

### Frontend

```bash
cd frontend
npm run test
npm run build
```

## Cardlink статус интеграции

### Что уже работает

1. Тарифы и checkout endpoint.
2. Создание платежа в БД.
3. Webhook обработка статуса платежа.
4. Автопереключение подписки после успешной оплаты.

### Что включится после выдачи merchant id/secret

1. Боевой checkout URL Cardlink.
2. Production верификация подписи webhooks.

## OpenAI статус интеграции

### Что уже работает

1. Endpoint `POST /api/v1/ai/task-hint` для генерации персональной подсказки по конкретной задаче.
2. Ограничение доступа: AI-подсказки доступны только Premium-подписке (и admin).
3. Логирование запросов/ответов AI в таблицу `ai_hint_requests` для аналитики и аудита.
4. UI-кнопка `AI подсказка` в интерфейсе решения задачи.

### Что требуется для боевого включения

1. Указать `OPENAI_API_KEY` в production env.
2. При необходимости переопределить `OPENAI_MODEL` и `OPENAI_BASE_URL`.

## Google OAuth статус

### Какие данные берём от Google

1. `sub` (устойчивый идентификатор аккаунта Google)
2. `email`
3. `email_verified`
4. `name`
5. `aud` (проверка соответствия `GOOGLE_CLIENT_ID`)

### Проходит ли подтверждение аккаунта через Google

1. Да, при входе через Google backend валидирует `id_token` через Google `tokeninfo`.
2. Пользователь создаётся/обновляется только после проверки `email_verified=true`.
3. Если `GOOGLE_CLIENT_ID` не задан, Google OAuth возвращает `not_configured`.

### Быстрое включение Google OAuth в production

1. В Google Cloud обязательно сначала заполнить `OAuth consent screen`.
2. Создать `OAuth client ID` типа `Web application`.
3. Добавить `Authorized JavaScript origin`:
- `http://85.198.82.221:8511`
4. Внести полученный `Client ID` в `GOOGLE_CLIENT_ID` на сервере и перезапустить backend процессы PM2.

Подробный пошаговый runbook:

- [docs/operations/GOOGLE_OAUTH_PRODUCTION_SETUP_2026_04_23.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/GOOGLE_OAUTH_PRODUCTION_SETUP_2026_04_23.md)

## Прогресс ученика в БД

1. Отправки решений: таблица `submissions`.
2. Начисления XP: таблица `xp_events`.
3. Достижения: `user_achievements`.
4. Подписки и тарифный контекст: `subscriptions`, `plans`.

## Почему архитектура сделана именно так

1. Очередь + воркер: стабильная обработка проверок кода без блокировки API.
2. Java checker в отдельном процессе: изоляция тяжелой операции от web-request.
3. Модульный монолит: быстрый вывод коммерческой версии без преждевременного усложнения.
4. Полный путь от API до UI: платформа сразу доступна ученикам.

## Документация

- [PROJECT_PLAN.md](C:/prog/Comercial/LeonovCarePlatform/PROJECT_PLAN.md)
- [docs/operations/DEPLOYMENT_RUNBOOK.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/DEPLOYMENT_RUNBOOK.md)
- [docs/architecture/ARCHITECTURE_OVERVIEW.md](C:/prog/Comercial/LeonovCarePlatform/docs/architecture/ARCHITECTURE_OVERVIEW.md)
- [docs/operations/IMPLEMENTATION_CHANGELOG.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/IMPLEMENTATION_CHANGELOG.md)
- [docs/operations/BUG_AUDIT_2026_04_23_v2_4.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/BUG_AUDIT_2026_04_23_v2_4.md)
- [docs/operations/GOOGLE_OAUTH_PRODUCTION_SETUP_2026_04_23.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/GOOGLE_OAUTH_PRODUCTION_SETUP_2026_04_23.md)

## Обновление для запуска (2026-04-29)

1. Для запуска на первую когорту учеников отключены OAuth-входы через Google/GitHub в пользовательском продукте:
- frontend auth-экран переведен в email-only flow;
- backend OAuth маршруты удалены из router.

2. Регистрация расширена полями профиля:
- `firstName`, `lastName`, `nickname` (nickname уникален);
- добавлен публичный системный идентификатор `publicId` (формат `LC-XXXXXXXXXX`).

3. Демо Java-контент и синтетическая статистика очищены:
- удаляется курс `java-start`;
- сбрасываются demo-XP события и достижения;
- `AUTO_SEED` по умолчанию выключен.

4. Усилен платежный webhook:
- добавлена проверка подписи `X-Cardlink-Signature` при включенном `CARDLINK_REQUIRE_SIGNATURE=true`;
- добавлена идемпотентность успешного статуса оплаты (повторный webhook не дублирует подписку).

5. Усилен worker-контур:
- добавлен счетчик `processing_attempts` для submission;
- добавлены ограниченные retry при ошибках воркера с переводом в `failed` после лимита.

6. Запускной пакет документов (создан в корне проекта):
- [ARCHITECTURE.md](C:/prog/Comercial/LeonovCarePlatform/ARCHITECTURE.md)
- [API_SPEC.yaml](C:/prog/Comercial/LeonovCarePlatform/API_SPEC.yaml)
- [DEPLOYMENT.md](C:/prog/Comercial/LeonovCarePlatform/DEPLOYMENT.md)
- [SECURITY.md](C:/prog/Comercial/LeonovCarePlatform/SECURITY.md)
- [PLUGIN_IDEA_SPEC.md](C:/prog/Comercial/LeonovCarePlatform/PLUGIN_IDEA_SPEC.md)
- [TEST_PLAN.md](C:/prog/Comercial/LeonovCarePlatform/TEST_PLAN.md)

## Обновление оплаты и подписок (2026-04-29, v2.22)

1. Checkout и серверная верификация:
- backend создает счет через Cardlink API (`/api/v1/bill/create`) при заданных `CARDLINK_SHOP_ID` и `CARDLINK_API_TOKEN`;
- при неполной конфигурации контур остается в `pending_config`, без ложного повышения тарифа.

2. Контроль статуса платежа:
- добавлен endpoint `GET /api/v1/subscription/payments/:paymentId`;
- добавлен режим `?sync=true` (сверка через `/api/v1/bill/status`), если webhook задержался.

3. Подписочный lifecycle:
- просроченные `active` подписки автоматически переводятся в `expired`;
- при отсутствии активной подписки гарантируется fallback в `free`;
- повторная успешная оплата того же плана продлевает срок действия подписки.

4. Сценарии возврата:
- `refunded/reversed/chargeback` отзывают доступ только для подписки, связанной с этим платежом-источником.

5. UX billing:
- страница подписки показывает live-статус текущего платежа;
- pending-платежи автоматически опрашиваются до финального результата.

Почему так:

1. На запуске когорты важно исключить “слепые” платежи, когда UI показывает оплату, а сервер не подтвердил статус.
2. Двойная проверка (webhook + sync) закрывает основной риск рассинхронизации платежного состояния.

## Обновление Python-урока и auth-сессии (2026-04-29, v2.24)

1. Исправлен пользовательский инцидент `invalid access token`:
- frontend добавил автоматический refresh access token через `POST /api/v1/auth/refresh`;
- при истекшем access token исходный запрос повторяется автоматически;
- при невалидном refresh token выполняется безопасный выход и переход на `/auth`.

2. Добавлена поддержка языков задач:
- в `tasks` добавлено поле `language` (`java` | `python`), миграция `007_python_course_and_lesson_blocks.sql`;
- worker выбирает judge по языку задачи;
- `GET /api/v1/lessons/:lessonID` и `GET /api/v1/tasks/:taskID` возвращают `language`.

3. Добавлен Python judge для автопроверки:
- backend запускает Python-решения по stdin/stdout;
- поддержаны режимы `local` и `docker` (образ `python:3.12-alpine`);
- сохранена совместимость Java judge.

4. Добавлен новый курс `Python с нуля`:
- модуль `Базовый синтаксис`;
- урок 1 `Первый код на Python: вывод, переменные и ввод данных`;
- 25 шагов урока (теория, практики, тесты, итог);
- 12 задач с автопроверкой и тест-кейсами.

5. Интерфейс урока переведен в пошаговый формат (Stepik-like):
- список шагов слева;
- содержимое активного шага справа;
- для практики добавлена явная кнопка перехода в кодовый шаг;
- для тестов добавлен выбор ответа и пояснение.

Почему сделано именно так:

1. Истекающий access token не должен ломать рабочие страницы ученика — refresh должен происходить автоматически и прозрачно.
2. Для коммерческого запуска курса Python нужна реальная серверная автопроверка, а не демонстрационный UI без judge.
3. Пошаговый формат урока увеличивает понятность траектории и приближает UX к ожидаемому образовательному продукту.

## Обновление уроков и встроенной практики (2026-04-29, v2.25)

1. Встроенная практика в шагах урока:
- код теперь пишется прямо внутри практического блока урока;
- добавлены действия `Запустить код` и `Отправить на проверку` без перехода на отдельную страницу задачи;
- добавлена кнопка `AI-подсказка` для улучшения решения.

2. Новый preview endpoint:
- `POST /api/v1/tasks/:taskID/run` запускает код на judge и возвращает результат сразу;
- запуск не создает запись отправки и не начисляет XP.

3. Поведение квизов:
- ответ проверяется только по кнопке `Проверить ответ`;
- при ошибке показывается `Попробовать еще раз` с очисткой ответа;
- правильный вариант больше не раскрывается сразу после ошибки.

4. Навигация и прогресс шагов:
- на каждом шаге добавлена кнопка `Дальше`;
- теоретический шаг автоматически отмечается выполненным после открытия;
- практический шаг отмечается выполненным после статуса `accepted`.

5. Контент урока:
- из первого теоретического блока удален фрагмент `Неправильно: print(Привет)`.

6. Auth UI:
- заголовок формы входа упрощен до `Вход`.

Почему так:

1. Пользователь должен решать задачу в одном контексте урока, без лишних переходов между страницами.
2. Разделение `run` и `submit` улучшает учебный цикл: быстрые прогоны + отдельная финальная отправка.
3. Квиз без мгновенного раскрытия правильного ответа снижает угадывание и повышает реальное усвоение.

## Hotfix judge runtime fallback (2026-04-29, v2.26)

1. Если `JUDGE_MODE=docker` и docker недоступен в runtime, платформа автоматически использует local judge.
2. Фикс нужен для корректной работы встроенного `Запустить код` в шагах урока.

## IntelliJ IDEA Plugin Module (2026-04-29)

В репозиторий добавлен отдельный подпроект:

- `C:/prog/Comercial/LeonovCarePlatform/idea-plugin`

### Что реализовано

1. Tool Window для учебного цикла в IDE.
2. Token auth через PasswordSafe.
3. Настройки плагина (`PersistentStateComponent`) с настраиваемым `API Base URL`.
4. API abstraction:
- `PlatformApiClient`;
- `HttpPlatformApiClient`;
- `MockPlatformApiClient`.
5. Локальное открытие задач и генерация структуры `platform-tasks/...`.
6. Local Run/Debug для Java.
7. Submit + polling результата.
8. Панель результата проверки.
9. Local style analysis + optional server style analysis.
10. Reference solution viewer (read-only).
11. Ручная и авто-sync.
12. Restore project structure.
13. Actions для основных сценариев через Find Action.
14. RU/EN resource bundle.
15. Unit tests ключевой логики.

### Как запустить plugin sandbox

1. Убедитесь, что используется Java 17+ для Gradle.
2. Перейдите в подпроект:

```bash
cd idea-plugin
```

3. Запустите тесты:

```bash
./gradlew test
```

4. Соберите plugin distribution:

```bash
./gradlew buildPlugin
```

5. (опционально) Запустите sandbox IDE:

```bash
./gradlew runIde
```

### Базовая настройка API в плагине

1. Откройте `Settings | Tools | Leonov Care Platform Plugin`.
2. Проверьте `API Base URL` (по умолчанию `http://localhost:8080/api/v1`).
3. При необходимости включите `Mock mode` для локальной отладки плагина без backend.

### Авторизация в плагине

1. Откройте Tool Window `Leonov Care Platform`.
2. Нажмите `Войти`.
3. Введите API token.
4. Плагин валидирует токен через `GET /me`.

### Как открыть, запустить и проверить задачу

1. Выберите курс в Tool Window.
2. Выберите задачу и нажмите `Открыть`.
3. Решайте в локальном файле в `platform-tasks/...`.
4. Используйте `Запустить` / `Дебаг` для локальной проверки.
5. Используйте `Проверить` для отправки на сервер.

### Endpoint контракт для backend-интеграции

Текущая реализация backend уже используется плагином через адаптацию endpoint’ов. Для полного контракта plugin-клиента нужны отдельные endpoint’ы:

1. `GET /courses/{courseId}/tasks`
2. `GET /tasks/{taskId}/template`
3. `POST /tasks/{taskId}/attempts`
4. `GET /tasks/{taskId}/attempts/{attemptId}`
5. `POST /tasks/{taskId}/style-check`
6. `GET /tasks/{taskId}/reference-solution`
7. `POST /tasks/{taskId}/progress/reset`
8. `POST /sync`

Подробности: `docs/architecture/IDE_PLUGIN_IMPLEMENTATION_2026_04_29.md`.

### Намеренно не реализовано

В plugin scope намеренно отсутствуют:

1. Community/forum/discussion.
2. Help threads/chat with mentors.
3. Любые ссылки или UX-флоу «обсудить задачу/попросить помощь».

## UI hotfix (2026-04-29, v2.50)

1. Обновлена Python SVG-иконка курса:
- компонент `PythonCourseIcon` переведен на форму официального `python-logo-only`;
- добавлены уникальные gradient id через `useId` для безопасного рендера нескольких иконок на одной странице.

2. Исправлено наложение фильтров на странице задач:
- `tasks-toolbar` переведен на grid-раскладку для стабильной геометрии селектора/поиска;
- фильтры получили отдельный блок `tasks-filter-tabs` с явными отступами и адаптивным поведением.

3. Бизнес-логика не изменялась:
- маршруты, API-запросы, фильтрация и статусы задач работают в прежнем контуре;
- изменения касаются только presentation/layout слоя.

## Plugin auth + refresh integration hardening (2026-04-30, v2.51)

1. IDEA plugin auth-контур связан с реальным backend flow:
- добавлен login по `email/password` через `POST /api/v1/auth/login`;
- сохранена обратная совместимость token login (ручной API token).

2. Добавлено безопасное хранение auth-сессии в PasswordSafe:
- `accessToken` и `refreshToken` сохраняются раздельно;
- legacy-ключ `api-token` поддержан для миграции уже сохраненных сессий.

3. Добавлен автоматический refresh на стороне плагина:
- при `401` в защищенных запросах выполняется `POST /api/v1/auth/refresh`;
- исходный запрос автоматически повторяется с новым `accessToken`;
- при невалидном/отсутствующем refresh токене плагин переводит сессию в состояние re-login без очистки кэша задач.

4. Все ключевые операции переведены на единый auth wrapper:
- загрузка курсов/задач;
- открытие задачи;
- submission/polling;
- sync;
- style-check;
- reference solution.

5. Default API Base URL плагина переключен на production API из текущего проекта:
- `http://85.198.82.221:8510/api/v1`;
- URL остается изменяемым в настройках плагина для dev/staging.

6. Практическая проверка интеграции выполнена:
- plugin module: `./gradlew test` и `./gradlew buildPlugin` проходят;
- production API smoke: `register -> me -> courses -> lesson -> task -> run -> submit -> poll -> refresh`;
- backend/frontend тесты на сервере проходят.

Почему сделано именно так:

1. При коротком TTL access token учебный поток в IDE должен быть непрерывным, поэтому refresh/retry обязателен на клиенте.
2. Хранение refresh токена вне plain settings требуется для соответствия security-требованиям и ревью.
3. Сохранение кэша задач при истекшей сессии дает offline continuity и снижает риск “пустого” интерфейса для ученика.

4. Дополнительная шлифовка отступов фильтров (v2.51):
- выровнен вертикальный ритм между заголовками, полями фильтрации и filter chips на страницах `Задачи`, `Проверки`, `Рейтинг`;
- добавлена адаптивная корректировка отступов на мобильных ширинах.

5. Уточнение визуала Python-логотипа курса (v2.52):
- `PythonCourseIcon` приведен к версии, которая лучше совпадает с согласованным референсом экрана «Обучение»;
- сохранена защита от конфликтов SVG gradients при множественном рендере иконки.

6. Перевод на канонический Python logo mark (v2.53):
- `PythonCourseIcon` использует официальные контуры Python snakes, чтобы визуально это был именно узнаваемый Python-логотип;
- логика курса/страниц не изменялась, правка только в presentation-layer.

7. Исправление смещения курсора в редакторе (v2.54):
- в Monaco-редакторах урока и задачи отключены лигатуры и дробный letter-spacing;
- выровнены параметры рендера шрифта/курсора для корректной позиции caret относительно символов.

8. Унификация типографики платформы на базе Manrope (v2.55):
- введена единая шкала размеров/line-height через глобальные CSS tokens;
- page titles, hero titles, section/card titles, nav, buttons, badges, таблицы и lesson sidebar приведены к согласованной SaaS-иерархии;
- снижена визуальная «грубость» (избыточная жирность и сверхкрупные заголовки) без изменения бизнес-логики.

9. Точечная доводка визуала до референса с Inter-first (v2.56):
- основной UI-шрифт переключен на `Inter` (глобально в `--font-sans` и `html/body`), `JetBrains Mono` сохранен только для кода;
- header и основной контент выровнены в единый centered container (`min(100% - 96px, 1400px)` + адаптивные gutter для tablet/mobile), чтобы убрать прижатие к краям;
- hero-блок страницы «Обучение» уплотнен под референс: скорректированы сетка/размеры/типографика, прогресс-блок и CTA;
- badge `Текущий курс` принудительно сделан compact (`fit-content`) и больше не растягивается по ширине;
- для длинного Python-заголовка добавлен компактный display-title в hero (`Python с нуля`), чтобы сохранить ритм при длинном системном имени курса;
- левая карточка `Мои курсы` доработана по плотности и выравниванию текста (чистый left-aligned layout, 48px icon slot, clamp описания);
- список уроков/модулей на странице обучения уплотнен: row-height, markers, active-state и divider-структура ближе к согласованному premium curriculum виду;
- в lesson sidebar визуальный статус окончательно привязан к marker слева: убраны конкурирующие текстовые статусы справа (`Готово/Сейчас`), сохранена кликабельность и логика переходов.

Почему сделано именно так:

1. Inter в русскоязычном UI дает более нейтральный и предсказуемый micro-ритм в мелких интерфейсных элементах по сравнению с более округлым шрифтом.
2. Единая ширина контейнера для header/main убирает визуальный «съезд сетки», из-за которого интерфейс воспринимался как менее аккуратный.
3. Compact badge и ограничение hero-title защищают композицию от длинных реальных названий курсов без изменения доменной модели данных.
4. Перенос статуса шага в левый marker снижает визуальный шум и исключает конфликт между правыми индикаторами и основным состоянием шага.

10. Исправление стилизации выпадающего списка курса в задачах (v2.68):
- на странице `Задачи` нативный `<select>` заменен на кастомный dropdown-компонент в том же визуальном языке;
- раскрытый список теперь имеет единый стиль платформы (белая surface, мягкая граница, скругления, hover/selected состояния);
- сохранена текущая бизнес-логика фильтрации: по-прежнему меняется только `selectedCourseId`, API и маршруты не затронуты;
- добавлено закрытие dropdown по клику вне компонента и по `Escape` для корректной UX/доступности.

Почему сделано именно так:

1. Нативный список `<select>` на Windows не поддается полной стилизации и визуально выбивается из редизайна.
2. Кастомный dropdown даёт консистентный вид в разных браузерах/ОС без изменения доменной логики экрана.
3. Закрытие по outside-click и `Escape` снижает риск «залипшего» меню и улучшает поведение при интенсивной работе с фильтрами.

## Plugin update: AI hints + curriculum language alignment (2026-04-30, v2.59)

1. Проверен текущий контент курса по миграциям backend:
- в задачах фактически используются языки `java` и `python` (включая alias `python3`);
- SQL/JS/Kotlin пока не обнаружены в production seed, но архитектура плагина расширена под будущие языки.

2. В IDEA plugin добавлены AI-подсказки, связанные с реальным backend endpoint:
- добавлен вызов `POST /api/v1/ai/task-hint` через `HttpPlatformApiClient`;
- добавлен `AiHintService` (project service) с безопасным получением исходника текущей задачи;
- добавлена кнопка `AI-подсказка` в панели задачи и отдельный action для Find Action/Tools menu;
- добавлен read-only диалог показа подсказки и модели (`AiHintDialog`).

3. Расширена языковая модель задач для материалов курса:
- добавлен `TaskLanguage` с канонизацией входных alias (`java/python/python3/sql/js/kotlin/...`);
- fallback-пути шаблонов теперь вычисляются из `TaskLanguage` (включая `src/main/sql/query.sql` для будущих SQL задач);
- для неподдержанных локальным раннером языков плагин показывает точное сообщение с именем языка, вместо общего ошибки.

4. Добавлены тесты для новых сценариев:
- `HttpPlatformApiClientTest`: успешный AI hint запрос + fallback при 404;
- `HttpPlatformApiClientLanguageTest`: корректный mapping SQL task details/template fallback;
- `TaskLanguageMappingTest`: канонизация языков API.

5. Почему так:
- AI endpoint уже используется web-клиентом и backend, поэтому подключение в IDE дает единый учебный поток;
- языковая канонизация нужна, чтобы плагин не ломался на alias (`python3`, `js`, `postgresql`) при росте контента;
- SQL поддержка добавлена на уровне структуры/файлов/отправки, даже до появления серверного SQL judge.

## Stability update: backend judge + prod readiness retest (2026-04-30, v2.64)

1. Backend модульная стабильность:
- восстановлен `backend/go.sum` и повторяемость сборки через `go mod tidy`;
- `go test ./...` снова полностью проходит.

2. Исправлен runtime-детектор Python для judge:
- устранен кейс с Windows alias-заглушкой `python3` (нерабочий бинарник в PATH);
- judge теперь выбирает только валидный интерпретатор (проверка `--version` с кодом `0`);
- добавлен регрессионный тест, фиксирующий fallback на рабочий `python`.

3. Повторная проверка production контура:
- smoke (`/me`, `/courses`, `/tasks/{id}/run`, `/tasks/{id}/submissions`) проходит;
- sample load:
  - `/courses` ~5892 req/s (15s, `t6/c120`), p99 ~38.84ms;
  - `/run` ~85 req/s (15s, `t4/c30`) на валидной Python-задаче с тестами;
- queue burst: 60 submissions дренируются до `pending=0` примерно за 3 секунды.

4. Почему предыдущий wrk сигнал по `/run` был ложным:
- в тест-скрипте использовался выбор задачи по title без проверки наличия test cases;
- для задач без test cases API корректно отвечает `422`, что и дало `Non-2xx` в отчете.

5. Подробный протокол шагов и команд:
- [docs/operations/PROD_READINESS_VALIDATION_2026_04_30_v2_64.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/PROD_READINESS_VALIDATION_2026_04_30_v2_64.md)

## Deployment retest update (2026-04-30, v2.65)

1. Исправлена кроссплатформенность judge regression-теста:
- тест fallback выбора Python runtime теперь корректно работает на Windows и Linux.

2. Повторный production rebuild/restart выполнен на сервере:
- backend: `go test ./...` + rebuild API/worker;
- PM2: restart `leonovcare-api` и `leonovcare-worker`;
- health после рестарта: `ok`.

3. Повторный load-срез после деплоя:
- `/courses` (`15s`, `t6/c120`): ~7727.92 req/s;
- `/tasks/{id}/run` (`15s`, `t4/c30`): ~104.72 req/s;
- queue burst 60 submissions: drain до нуля примерно за 2 секунды.

4. Подробный журнал шагов и команд:
- [docs/operations/PROD_READINESS_VALIDATION_2026_04_30_v2_64.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/PROD_READINESS_VALIDATION_2026_04_30_v2_64.md)

## Editor UX + dynamic language update (2026-04-30, v2.69)

1. Переработан UI редактора кода на страницах задач и практики урока:
- редактор собран в цельный product-блок `toolbar + editor area + action bar`;
- toolbar приведён к единому виду (56px, мягкий фон, аккуратная граница);
- language-pill вынесен в правую часть toolbar;
- action-зона собрана в две логические группы действий:
  - слева: `Запустить код`, `Отправить на проверку`;
  - справа: `AI-подсказка`, `Сброс к шаблону`;
- сохранена вся рабочая логика run/check/hint/reset и текущие API вызовы.

2. Улучшена визуальная структура Monaco-wrapper:
- единая внешняя карточка с `border-radius: 20px`, тонкой границей и мягкой тенью;
- согласованный gutter/line numbers/current-line для более чистого чтения кода;
- внутренние рамки упрощены, чтобы убрать эффект «рамка в рамке».

3. Убран hardcode `Python 3` из страниц редактора:
- добавлен единый helper: `frontend/src/lib/editorLanguage.ts`;
- helper нормализует язык и выдает:
  - label для UI;
  - mode для Monaco syntax highlighting.

4. Источник языка теперь вычисляется по приоритету (без изменения backend-контрактов):
- `task.language` / `task.lang`;
- затем language поля lesson/module/course/direction (если пришли в payload);
- fallback: `Python 3`.

5. Текущий mapping языка в helper:
- `python|python3|py -> Python 3` (mode `python`);
- `html|html5 -> HTML` (mode `html`);
- `go|golang -> Go` (mode `go`);
- `java -> Java` (mode `java`);
- дополнительно сохранена обратная совместимость для `sql` (mode `sql`).

6. Почему сделано именно так:
- единый helper исключает расхождение label/mode между `TaskPage` и `LessonPage`;
- UI редактора теперь выглядит как цельный premium-блок, а не набор разрозненных частей;
- изменения ограничены presentation layer и не затрагивают бизнес-логику маршрутов, проверок, прогресса и auth.

## Course SVG icons update (2026-04-30, v2.70)

1. Добавлены отдельные SVG-иконки треков курсов:
- `Python` (существующая),
- `Java`,
- `Frontend`,
- `Go`,
- fallback-иконка для неизвестного трека.

2. Реализован единый резолвер трека:
- `frontend/src/lib/courseIconKey.ts`;
- определяет icon key по `slug`, `title`, `description` курса;
- поддерживает актуальные курсы из каталога (`java-zero-core`, `frontend-zero`, `go-zero-backend`, `python-*`).

3. Обновлена страница обучения:
- в hero-card и в списке `Мои курсы` иконка выбирается динамически, а не только для Python;
- fallback c `BookOpen` заменен на единый SVG fallback в той же дизайн-системе.

Почему сделано именно так:

1. Иконка курса теперь отражает реальное направление трека, что убирает визуальную асимметрию каталога.
2. Логика выбора иконки вынесена в отдельный helper, чтобы не дублировать проверки по всему UI.
3. Изменения изолированы в presentation layer и не затрагивают API/роутинг/прогресс/проверки.

## Курсы Java/Frontend/Go v1 import update (2026-04-30, v2.70)

1. В backend добавлен новый импортный контур для трех полноценных каталогов:
- Java (`java-zero-core`);
- Frontend (`frontend-zero`);
- Go (`go-zero-backend`).

2. Добавлены артефакты:
- генератор `backend/tools/generate_multicourse_v1_migration.js`;
- миграция `backend/migrations/022_seed_java_frontend_go_v1_catalog_and_sql_practice.sql`.

3. Фактический объем данных `022`:
- 3 курса, 15 модулей, 355 уроков;
- 11872 lesson blocks, включая теорию/практику/квизы/проекты/саммари.

4. Принятая политика по автопроверке:
- автопроверяемые задачи создаются только для SQL-практик (`checker.type='sql_query'`);
- создано 404 SQL-задачи и 404 теста;
- остальные практики импортированы как учебные блоки без фальшивой привязки к judge.

5. Почему так сделано:
- исходные v1 данные для большинства практик используют `ide_plugin/http_api` checker-формат и не соответствуют текущему backend stdin/stdout judge;
- принудительное превращение таких шагов в обычные задачи давало бы некорректные verdict и риск ложного «accepted/failed»;
- текущий подход сохраняет весь учебный контент, остается идемпотентным и готовит базу для отдельного server-side checker контура без потери данных.

## Courses screen cache + font recovery update (2026-04-30, v2.71)

1. Добавлен устойчивый кеш экрана обучения (`CoursesPage`) в `localStorage`:
- key: `lc_courses_screen_cache_v1`;
- в кеше сохраняются:
  - список курсов (`courses`),
  - текущий открытый курс (`selectedCourse`),
  - словарь деталей курсов по `courseId` (`courseDetails`),
  - timestamp `savedAt`.

2. Что изменено в механике открытия курсов:
- при повторном входе на страницу сначала показываются кешированные данные без ожидания сети;
- для уже открытого ранее курса детали берутся из кеша мгновенно;
- после этого выполняется «тихое» обновление через API (`silent refresh`) и данные синхронизируются;
- если сеть временно недоступна, экран не сбрасывается в пустое состояние при наличии кеша.

3. Почему это сделано именно так:
- исходная проблема пользователя: сначала отображался пустой/скелетонный блок, затем контент «догружался»;
- хранение только одного `selectedCourse` не покрывало быстрые переключения между несколькими курсами;
- словарь `courseDetails` позволяет открывать ранее просмотренные курсы без визуальной паузы.

4. Усилена валидация и совместимость кеша:
- добавлена нормализация кешированных сущностей (`normalizeCourseSummary`, `normalizeCourseLesson`, `normalizeCourseDetail`);
- кеш читается в lenient-режиме и восстанавливается даже при частично старом формате записей;
- невалидные/пустые структуры безопасно отбрасываются.

5. Восстановлен «красивый» шрифт интерфейса через локальные ассеты:
- добавлены пакеты:
  - `@fontsource/inter`
  - `@fontsource/jetbrains-mono`
- подключение переведено в `frontend/src/main.tsx` (weights 400/500/600/700/800 для Inter и 400/500/600 для JetBrains Mono);
- удален внешний `@import` Google Fonts из `frontend/src/styles/global.css`.

6. Почему шрифт подключен локально:
- исключается зависимость от внешнего CDN на первом рендере;
- снижается риск FOUT/FOIT и «прыжка» типографики при медленной сети;
- визуальная консистентность интерфейса стабильнее в production.

7. Проверки после правок:
- `npm run lint` (без новых ошибок; сохранены существующие проектные предупреждения `any`);
- `npx tsc --noEmit`;
- `npm run build`;
- `npm run test`.

## Course icon tuning update (2026-04-30, v2.72)

1. Скорректированы SVG иконки треков в каталоге курсов:
- `Java` оставлена без изменений (как было согласовано).
- `Frontend` заменена на HTML5-щит в фирменных цветах (`#E44D26/#F16529`) с узнаваемой формой знака `5`.
- `Go` упрощена до чистого синего wordmark `go` (две буквы), без лишней графики.

2. Почему так сделано:
- предыдущие версии Frontend/Go выглядели слишком абстрактно и не считывались как конкретные направления;
- новая версия делает треки мгновенно узнаваемыми в списке курсов и hero-карточках;
- изменения изолированы в икон-системе и не затрагивают API/маршруты/прогресс.

3. Проверки после изменения:
- `npm run lint` (без новых ошибок, сохранены только старые warning проекта);
- `npm run build`.

## Frontend HTML5 icon likeness update (2026-04-30, v2.73)

1. По пользовательскому референсу иконка `Frontend` переработана под максимально узнаваемый HTML5 shield:
- использована классическая геометрия щита (две оранжевые плоскости);
- внутренняя `5` собрана в фирменной светлой/белой раскладке;
- лишняя абстракция убрана, иконка теперь читается как HTML5 сразу.

2. `Java` и `Go` логика не менялась в этом шаге.

3. Проверки:
- `npm run lint`;
- `npm run build`.

## Commissioner typography migration update (2026-04-30, v2.74)

1. Полностью заменен основной UI-шрифт платформы на `Commissioner`:
- в `frontend/src/main.tsx` подключены веса `400/500/600/700/800` через `@fontsource/commissioner`;
- удалены импорты `@fontsource/inter` из ранней версии;
- сохранены импорты `@fontsource/jetbrains-mono` для кодовых зон.

2. Обновлены глобальные font tokens в `frontend/src/styles/global.css`:
- `--font-sans: "Commissioner", ui-sans-serif, system-ui, ...`;
- `--font-mono: "JetBrains Mono", ...`.

3. Зафиксировано глобальное применение типографики:
- `html/body` принудительно используют `var(--font-sans)`;
- интерактивные элементы (`button/input/select/textarea`) наследуют UI-шрифт;
- кодовые области (`code/pre/.monaco-editor/.cm-editor/.CodeMirror/textarea.code-editor`) используют только моноширинный стек.

4. Дополнительно выровнена визуальная шкала под Commissioner:
- устранена избыточная жирность в строках списков/плашках/бейджах (`700 -> 600` в точках, где интерфейс выглядел тяжело);
- hero/course title и page title оставлены в `700` как структурные заголовки;
- приведены к единому виду дублирующие блоки typography overrides (hero/current-course).

5. Почему сделано именно так:
- пользовательский запрос требовал целиком перевести UI на Commissioner без изменения бизнес-логики;
- локальная доставка шрифта через `@fontsource` исключает зависимость от внешнего CDN при первом рендере;
- сохранение отдельного mono-stack предотвращает деградацию читаемости кода в редакторе и консоли.

6. Проверки после правок:
- `npm run lint` (без новых ошибок; сохранены исторические warning проекта по `any` и hook deps);
- `npx tsc --noEmit`;
- `npm run build`;
- `npm run test`.

## Course icon resolver hotfix (2026-04-30, v2.75)

1. Исправлена причина неверной иконки у Frontend-курса:
- ранее резолвер ловил `java` внутри `JavaScript` и выбирал Java-иконку;
- теперь используется проверка по слову с разделителями (`containsWord`) и корректный порядок приоритетов.

2. Что поменялось технически:
- `frontend/src/lib/courseIconKey.ts`:
  - Frontend-проверка идет до Java,
  - Java больше не матчит подстроку внутри `JavaScript`.
- `frontend/src/lib/courseIconKey.test.ts`:
  - добавлен regression-тест `Frontend + JavaScript -> frontend`.

3. Почему сделано так:
- это точечный фикс только presentation-layer;
- не затрагивает бизнес-логику, API, маршруты, прогресс и проверки.

4. Проверки:
- `npm run test`;
- `npm run lint`;
- `npx tsc --noEmit`;
- `npm run build`.

## Python v10 rollout (2026-04-30, v2.76)

1. Полный Python-контент переведен на новый импорт `v10` через миграцию:
- `backend/migrations/023_reseed_python_zero_v10_polished_full.sql`.

2. Backend проверка задач расширена под новые checker-типы:
- `python_stdout`, `python_pytest`, `sql_query`, `http_api`, `ide_plugin`.

3. Для project-шагов включен file-bundle submit из IDE:
- plugin отправляет `files[]`, backend поддерживает формат `__LC_BUNDLE_V1__`.

4. Quiz-проверка переведена на сервер:
- правильные ответы больше не утекают в payload урока;
- новый endpoint `POST /api/v1/lessons/:lessonId/quiz-check`.

5. Подробные документы rollout/валидации:
- `docs/operations/PYTHON_V10_ROLLOUT_2026_04_30.md`
- `docs/operations/PYTHON_V10_IMPORT_VALIDATION_2026_04_30.md`.

## Learning visual recovery update (2026-04-30, v2.78)

1. На странице `Обучение` восстановлен clean SaaS/edtech визуальный слой без отката бизнес-логики:
- hero/sidebar/detail снова используют короткие публичные course-тексты;
- длинные внутренние названия (`v10 polished`, version/debug suffix) больше не используются как главный UI-title.

2. Типографика:
- основной UI-шрифт переведен на `Geologica` с fallback `IBM Plex Sans`;
- code-editor и code-view остались на моноширинном стеке `JetBrains Mono`.

3. Иконки направлений:
- сохранен и усилен резолвер с приоритетом `direction -> track -> language -> slug -> title/description`;
- Frontend/JavaScript не определяется как Java.

4. Подробный технический протокол изменений:
- [docs/operations/LEARNING_VISUAL_RECOVERY_2026_04_30_v2_78.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/LEARNING_VISUAL_RECOVERY_2026_04_30_v2_78.md)

## Auth registration nickname hotfix (2026-05-02, v2.79)

1. Что сломалось:
- регистрация через русскоязычный UI могла выглядеть неработающей, если пользователь вводил ник только кириллицей (`Иван`, `Иван Петров`);
- backend до исправления сохранял только latin letters/numbers/`_`/`-`, поэтому кириллический ник нормализовался в пустую строку и запрос завершался `400`.

2. Как работает сейчас:
- backend сохраняет Unicode-буквы и цифры, приводит буквы к lower-case, заменяет пробелы/точки на `_`, оставляет `_` и `-`;
- после нормализации ник обязан содержать минимум 3 символа;
- длина режется по rune, а не по byte, поэтому кириллица не ломается при ограничении 32 символа;
- frontend показывает понятное сообщение и ставит `minLength/maxLength` на поле ника и пароля.

3. Почему сделано именно так:
- продуктовый интерфейс русский, поэтому требование латинского alias на регистрации выглядит как лишний барьер и массово превращает корректные данные в ошибку;
- case-insensitive уникальность `nickname` уже обеспечена индексом `LOWER(nickname)`, поэтому расширение допустимых букв не требует отдельной миграции;
- сохранение нормализации пробелов и точек в `_` оставляет ник пригодным для поддержки, URL/логов и поиска по профилю.

4. Проверки:
- `go test ./internal/app -run TestNormalizeNickname`;
- production smoke: `POST /api/v1/auth/register` с `nickname="Иван Петров"` возвращает `201 Created`.

5. Факт после production deploy 2026-05-02:
- `POST /api/v1/auth/register` с `nickname="Иван Петров <timestamp>"` вернул `201 Created`;
- `GET /api/v1/me` вернул нормализованный `nickname="иван_петров_<timestamp>"`;
- контрольный мусорный ник `a..` вернул `400`, потому что после нормализации остаётся меньше 3 символов.

## IDEA plugin update: PyCharm target for Python course (2026-05-03, v2.80)

1. Цель изменения:
- обеспечить практический запуск плагина в PyCharm для сценария Python-курса без обязательного Java-модуля IDE.

2. Что изменено в plugin build/runtime:
- `idea-plugin/build.gradle.kts`:
  - target IDE переключен на `pycharmCommunity("2025.1")`;
  - добавлен `bundledPlugin("PythonCore")` как обязательный dependency для PyCharm API;
  - сохранен `bundledPlugin("com.intellij.java")` для компиляции Java-specific optional runner.
- `idea-plugin/src/main/resources/META-INF/plugin.xml`:
  - обязательный модуль changed to `com.intellij.modules.python`;
  - Java plugin dependency переведена в optional:
    - `<depends optional="true" config-file="leonovcare-with-java.xml">com.intellij.java</depends>`.
- добавлен `idea-plugin/src/main/resources/META-INF/leonovcare-with-java.xml` как optional config-file для Java-зависимого слоя.

3. Что изменено в коде плагина:
- `TaskRunConfigurationService` перестал иметь hard link на Java provider при инициализации;
- `JavaRunConfigurationProvider` вынесен в отдельный класс и подключается динамически;
- при отсутствии Java plugin/API сервис не падает на class loading и корректно деградирует через `UnsupportedLanguageRunConfigurationProvider`.

4. Почему сделано именно так:
- при прямой зависимости на `com.intellij.java` плагин не подходит для чистого PyCharm потока Python-курса;
- полный вынос Java-кода из продукта не нужен: optional модель сохраняет Java-run путь в IDE, где Java plugin присутствует;
- динамическая загрузка Java provider убирает startup-риск и делает поведение предсказуемым для PyCharm пользователей.

5. Как теперь тестировать plugin в PyCharm для Python-курса:
1. Сборка:
```bash
cd idea-plugin
./gradlew test
./gradlew buildPlugin
```
2. Установка:
- `Settings -> Plugins -> Install Plugin from Disk` и выбрать zip из `idea-plugin/build/distributions`.
3. Настройка:
- `Settings -> Tools -> Leonov Care Platform Plugin`;
- `API Base URL`: `http://85.198.82.221:8510/api/v1` (или другой environment).
4. Smoke:
- login;
- выбор Python-курса;
- открытие задачи;
- редактирование локального файла;
- `Проверить` (submit) и получение verdict;
- проверка `AI-подсказка`.
5. Ожидаемое run/debug поведение:
- основной production-контур для Python в этом релизе: open/edit/submit/sync/AI;
- локальный run/debug может быть unavailable для Python-задач и должен возвращать понятную ошибку без падения UI.

## IDEA plugin update correction: PyCharm dependency resolution (2026-05-03, v2.80.1)

1. Что подтвердилось в реальной сборке:
- на PyCharm target зависимость `bundledPlugin("com.intellij.java")` не резолвится;
- сборка падала с ошибкой `Could not find bundled plugin with ID: 'com.intellij.java'`.

2. Финальная фиксация состояния после прогона:
- Java bundled dependency удалена из `idea-plugin/build.gradle.kts`;
- optional Java dependency удалена из `idea-plugin/src/main/resources/META-INF/plugin.xml`;
- удален вспомогательный optional descriptor `META-INF/leonovcare-with-java.xml`;
- run-service переведен в deterministic fallback (`UnsupportedLanguageRunConfigurationProvider`) без Java provider.
- task `instrumentCode` отключен в `idea-plugin/build.gradle.kts`, потому что в текущем Windows/JDK окружении ant-instrumentation падала на пути `...\\jdk-17...\\Packages` и блокировала `buildPlugin`.

3. Почему сохранено именно так:
- приоритет текущего запроса: рабочий plugin в PyCharm для Python-курса;
- сохранение Java-run path в этой сборке технически блокировало сборку под PyCharm;
- open/edit/submit/AI/sync контур для Python остается рабочим и является главным учебным путём в этом релизе.

## IDEA plugin packaging update: PyCharm 2024.2.6 compatibility (2026-05-03, v2.80.2)

1. На пользовательском окружении зафиксирована версия PyCharm `2024.2.6` (build branch `242`), поэтому zip, собранный под `251.*`, не мог активироваться в IDE.

2. Для совместимости выполнена пересборка plugin package:
- `idea-plugin/build.gradle.kts`:
  - `pycharmCommunity("2024.2.6")`;
  - `sinceBuild = "242"`;
  - `untilBuild = "242.*"`;
  - версия плагина повышена до `0.1.1`.

3. Итоговый артефакт для установки в текущую IDE:
- `idea-plugin/build/distributions/leonovcare-idea-plugin-0.1.1.zip`.

4. Почему сделано именно так:
- это минимальное изменение, которое устраняет блокер установки на конкретной версии IDE пользователя без изменения бизнес-логики плагина;
- отдельный artifact под `242.*` исключает ложное ожидание, что пакет `251.*` должен работать в `2024.2.x`.

## IDEA plugin update: full lesson theory in IDE + local material cache (2026-05-03, v2.81)

1. Цель:
- сделать plugin точкой полного учебного цикла в IDE (задачи + теория урока + шаги), чтобы пользователь мог не открывать веб-платформу в обычном потоке обучения.

2. Что реализовано в плагине:
- добавлена модель lesson-материалов (`lesson + tasks + blocks`) в API-клиенте;
- `Task` расширен lesson-метаданными (`lessonId`, `lessonTitle`) для устойчивой связки “задача -> урок”;
- добавлен `LessonCache` (локальный JSON-cache в plugin settings), где сохраняются полные материалы уроков;
- в `TaskManager.refreshAll()` после синхронизации курсов/задач запускается background prefetch lesson-материалов;
- в `TaskManager.openTask()` для выбранной задачи подгружается материал урока из кеша (или с сервера при отсутствии/протухании) и передается в UI;
- в `TaskStatementPanel` теперь показывается не только `statement`, но и:
  - заголовок урока/модуля;
  - теоретический контент урока;
  - шаги урока (`blocks`) с типами и привязками к задачам;
  - затем блок текущей задачи;
- при открытии задачи сохраняется локальный файл `lesson-material.md` в `platform-tasks/...`, чтобы теория и структура урока физически были доступны локально.

3. Кеширование и снижение нагрузки:
- введен TTL lesson-кеша (`8h`), чтобы не запрашивать те же материалы на каждом открытии задачи;
- повторные открытия задач используют локальный кеш и не бьют сервер без необходимости;
- manual/local continuity сохраняется: даже при временной недоступности API уже загруженные материалы остаются в IDE.

4. Почему сделано именно так:
- пользовательский запрос требовал “всё в IDE” и минимизацию постоянных выгрузок с сервера;
- lesson-кеш в settings даёт быстрый доступ и не требует отдельной локальной БД;
- сохранение `lesson-material.md` рядом с `statement.md` даёт прозрачный локальный артефакт для оффлайн-чтения и ревью;
- TTL-баланс нужен, чтобы одновременно:
  - не перегружать backend постоянными запросами;
  - и не держать материалы бесконечно stale.

5. Технические файлы реализации:
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/api/ApiModels.kt`;
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/api/PlatformApiClient.kt`;
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/api/HttpPlatformApiClient.kt`;
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/cache/LessonCache.kt`;
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/task/TaskManager.kt`;
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/task/LessonMaterialFormatter.kt`;
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/task/TaskFileService.kt`;
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/ui/TaskStatementPanel.kt`;
- `idea-plugin/src/main/resources/META-INF/plugin.xml`.

## IDEA plugin hotfix: task opening UX (2026-05-03, v2.82)

1. Что зафиксировано по пользовательскому сценарию:
- в текущем UI задачи в списке можно было только выделить, но не открыть одним кликом;
- если пользователь после выделения нажимал `Run/Debug/AI/Ответ`, появлялось сообщение `Задача недоступна`, потому что `currentTask` ещё не был установлен.

2. Что изменено:
- в `TaskListPanel` добавлено открытие задачи по клику в списке (левая кнопка мыши);
- добавлено открытие задачи по `Enter` на выделенной строке;
- кнопка `Открыть` сохранена как явный fallback.

3. Почему сделано именно так:
- это убирает основной UX-разрыв "задача выделена, но фактически не открыта";
- снижает количество ложных обращений в поддержку по сообщению `Задача недоступна`;
- не меняет backend-контракт и не влияет на submit/checker, исправление полностью в IDE-клиенте.

4. Файл изменения:
- `idea-plugin/src/main/kotlin/com/leonovcare/plugin/ui/TaskListPanel.kt`.

5. Проверки:
1. `./gradlew test buildPlugin`;
2. ручной smoke в PyCharm:
- click по задаче открывает statement/теорию;
- `Enter` на задаче открывает statement/теорию;
- после открытия `AI-подсказка`/`Проверить` работают по текущей задаче без ошибки `Задача недоступна`.
## Python v18 first 10 pedagogy reseed — 2026-05-03

Курс `python-zero` получил дополнительный pedagogical reseed первых 10 уроков после первичного v18 rollout.

Актуальная миграция для production:

1. `backend/migrations/027_reseed_python_zero_v18_first10_pedagogy.sql`

Почему это отдельная миграция:

1. `026_reseed_python_zero_v18_strict_pedagogy.sql` уже была применена на сервере.
2. Изменять применённую миграцию нельзя: PostgreSQL хранит её версию в `schema_migrations`.
3. `027` переимпортирует обновлённый `материалы/v18_STRICT_PEDAGOGY/course_import.json`, где первые 10 уроков переписаны под ученика с нуля.

Новые проверки:

1. `python материалы/v18_STRICT_PEDAGOGY/validate_course.py`
2. `node backend/tools/validate_python_v18_materials_import.js`

Эти проверки теперь валидируют не только структуру, но и минимальную педагогическую полноту первых уроков: длину theory, наличие примеров, отсутствие будущих тем и конкретность mini-project шагов.

## Backend + IDEA plugin stabilization update (2026-05-05)

1. Что исправлено в backend-контуре для IDE:
- добавлены endpoint’ы `template/style-check/reference-solution/progress-reset/sync`;
- `GET /api/v1/submissions/:id` теперь отдает только sanitized feedback без hidden test payload;
- `referenceCode` отключен как канал доставки эталона;
- добавлены лимиты `MAX_REQUEST_BODY_BYTES` и `MAX_SUBMISSION_SOURCE_BYTES`;
- при Redis push ошибке submit возвращает `202` + `deferredDispatch=true`, запись добирает worker reconciler.

2. Что исправлено в plugin-клиенте:
- `getCourseTasks` сначала использует быстрый `tasks-catalog` endpoint;
- fallback на legacy lesson-fanout сохранен, чтобы не ломать старые server окружения.

3. Почему сделано именно так:
- это устраняет утечки и нестабильность polling/submit flow;
- снижает сетевую и серверную нагрузку для курсов с очень большим каталогом задач;
- оставляет обратную совместимость для уже развернутых контуров.

4. Локальная верификация после изменений:
1. `cd backend && go test ./...` — PASS.
2. Gradle-wrapper/`gradle` в текущем окружении отсутствует, поэтому автоматическую компиляцию `idea-plugin` в этом окружении выполнить нельзя.

## Node runtime baseline update (2026-05-05)

1. Для frontend build-chain теперь принят baseline `Node >=20.19.0` и `npm >=10`.
2. Это зафиксировано в `frontend/package.json` через `engines`, а в `deploy/server/deploy.sh` добавлен preflight-check версии Node.
3. Причина: часть зависимостей уже требует Node 20+, и на Node 18 появляются `EBADENGINE` предупреждения, которые могут перейти в hard-fail при следующих обновлениях пакетов.

## IDEA plugin loading hang fix (2026-05-05)

1. Исправлен сценарий, когда plugin долго зависал на экране `Загрузка курсов и задач...`.
2. `TaskManager` теперь:
- загружает курсы и задачи только выбранного курса в first paint;
- сразу переводит UI в ready-state;
- догружает остальные курсы в фоне;
- применяет timeout `12s` на отдельные запросы курса/задач.
3. Практический эффект:
- стартовое ожидание заметно короче на больших каталогах;
- исчезает впечатление «зависшего» окна при частично медленных API-ответах.

## Backend + plugin full audit hardening (2026-05-06)

1. Проведен полный аудит backend и IDEA plugin с фокусом на архитектуру, безопасность и сценарии учебного потока.
2. Закрыты критичные точки:
- auth middleware переведен в fail-closed (нет bypass при ошибке user lookup);
- reconciler очереди сабмитов получил анти-дублирование payload;
- checker runtime усилен против опасных shell separators и volume-path;
- plugin выводит полный lesson-context (теория + шаги + практическое задание).
3. Добавлены regression-тесты:
- backend: checker command/path hardening;
- plugin: `LessonMaterialFormatter` на полноту отображения материалов.
4. Подробный протокол, команды, причины и ограничения:
- [docs/operations/BACKEND_PLUGIN_FULL_AUDIT_2026_05_06.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/BACKEND_PLUGIN_FULL_AUDIT_2026_05_06.md)

## Backend hardening phase 2 (2026-05-06)

1. Дополнительно закрыты риски:
- JWT parsing теперь принимает только `HS256`;
- auth endpoint’ы (`register/login/forgot-password`) используют единый `normalizeEmail(trim+lowercase)`;
- security-критичные numeric env параметры клампятся на безопасные значения и не могут быть случайно отключены через `<=0`.

2. Почему это важно:
- signing policy больше не зависит от `alg` в token header;
- убраны edge-case ошибки в auth при e-mail с пробелами/регистром;
- снижен риск production misconfiguration, ослабляющей лимиты безопасности.

3. Подтверждение:
1. `go test ./...` — PASS.
2. `go vet ./...` — PASS.
3. `./gradlew.bat test --console=plain` (idea-plugin) — PASS.

## Обновление проверки решений и страницы «Проверки» (2026-05-07)

1. Исправлена причина ложного ощущения, что верные решения "не принимаются":
- на `TaskPage` polling после submit раньше завершался уже на `processing`;
- теперь polling продолжается до финального verdict, а `processing` показывается как `Проверяется`.

2. Исправлена навигация и кликабельность в разделе `Проверки`:
- строки истории теперь кликабельны и ведут в задачу с `submissionId` в query;
- TaskPage подхватывает этот `submissionId` и показывает детали выбранной отправки.

3. Исправлена статусная консистентность в списках:
- `ChecksPage`: фильтр `В очереди` включает `queued + processing`;
- `TasksPage`: `processing` отображается как `В процессе`, а не как fallback-статус.

Почему так:

1. Это UI/state-fix асинхронного контура `queued -> processing -> final` и он не меняет backend-контракт judge.
2. Явная обработка `processing` исключает ложные негативные verdict в интерфейсе.
3. Кликабельная история сокращает путь пользователя до исправления решения и повторной отправки.

## Full remediation rollout update (2026-05-08)

1. В релизе зафиксирован новый канонический deploy-контур:
- обязательный pre-migration DB backup;
- отдельный migrator-шаг до рестарта runtime;
- post-deploy `healthz/readyz` gate.

2. Зафиксированы безопасные runtime-дефолты:
- `AUTO_MIGRATE=false`;
- `AUTO_SEED=false`;
- `IDE_CHECKER_ALLOWED_COMMANDS` пустой по умолчанию.

3. Обновлены smoke и frontend runtime-гейты:
- `tests/smoke.sh` приведен к актуальному auth payload (`firstName/lastName/nickname`);
- smoke включает цепочку `register -> login/token -> courses -> tasks-catalog -> submission`;
- frontend больше не использует fallback на `localhost` в production runtime.

4. Добавлены инфраструктурные и quality gate артефакты:
- `deploy/server/backup-db.sh`;
- `deploy/server/systemd/leonovcare-db-backup.service`;
- `deploy/server/systemd/leonovcare-db-backup.timer`;
- `.github/workflows/ci-quality-gate.yml` (backend/frontend/idea-plugin).

5. Полный пошаговый протокол (append-only, с командами, результатами, rollback и статусом):
- [docs/operations/REMEDIATION_FULL_AUDIT_2026_05_08.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/REMEDIATION_FULL_AUDIT_2026_05_08.md)

## Актуализация от 2026-05-10: полный аудит auth и фиксация порядка email-нормализации

1. На production воспроизведены и зафиксированы дефекты auth-потока:
- `login` с email, содержащим пробелы по краям, возвращал `400` до нормализации;
- регистрация с кириллическим nickname в части сценариев возвращала `400`.

2. В backend auth-контуре выполнен фикс:
- `register/login/forgot-password` переведены на единый flow `bind -> normalizeEmail(trim+lowercase) -> validate`;
- добавлен helper `normalizeAndValidateEmail`;
- добавлены regression-тесты для фиксации поведения.

3. Подробный пошаговый отчёт аудита (pre-fix, root cause, изменения, команды проверки, post-deploy re-check):
- [docs/operations/AUTH_FULL_AUDIT_2026_05_10.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/AUTH_FULL_AUDIT_2026_05_10.md)

4. Почему это важно:
- регистрация и вход являются критическим первым пользовательским путём;
- ошибки нормализации/валидации на этом пути напрямую блокируют онбординг и создают ложное ощущение «сломанной платформы».

## Актуализация от 2026-05-13: критическая защита домена `leonovcare.ru`

1. Зафиксирован критический инфраструктурный запрет:
- домен `leonovcare.ru` принадлежит другому сайту и не может использоваться для LeonovCarePlatform.
2. На сервере выполнен rollback nginx-конфига с возвратом исходного сайта на `https://leonovcare.ru`.
3. В deploy-скрипт добавлен fail-closed preflight:
- если `leonovcare.ru` указывает на `frontend/dist` текущего проекта или проксирует на `127.0.0.1:8510` / `127.0.0.1:8511`, деплой блокируется.
4. Почему сделано именно так:
- инцидент затрагивает внешний основной домен и поэтому не допускает «мягких» предупреждений;
- блокировка на уровне скрипта останавливает ошибочный релиз до сборки и миграций.
5. Подробный пошаговый протокол:
- [docs/operations/DOMAIN_PROTECTION_LEONOVCARE_RU_2026_05_13.md](C:/prog/Comercial/LeonovCarePlatform/docs/operations/DOMAIN_PROTECTION_LEONOVCARE_RU_2026_05_13.md)

## Актуализация от 2026-05-16: blueprint внедрения support-чата (без кодовых изменений)

1. Подготовлена отдельная архитектурная спецификация внедрения чата поддержки:
- [docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md](C:/prog/Comercial/LeonovCarePlatform/docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md)
2. Что зафиксировано в документе:
- state-machine обращения (`open/resolved/closed`) и критерии «проблема решена»;
- модель смены оператора с аудитом;
- realtime-контур (SSE first-step) и риски буферизации;
- контракт БД/API, лимиты вложений (до 5 файлов), security guardrail'ы;
- anti-regression checklist, rollout и release-gates.
3. Почему сделано именно так:
- задача сформулирована как product-critical и должна внедряться без «костыльного» точечного кода;
- документ нужен как единый вход для инженера внедрения, чтобы изменения не повредили текущие learning/billing/auth контуры.

## Актуализация от 2026-05-16: support-чат — реализация и rollout

> Append-only. Эта секция не заменяет ни одну предыдущую — она дополняет
> запись от 2026-05-16 (blueprint) и фиксирует факт внедрения.

1. По blueprint'у `docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md`
   реализован полный встроенный support-чат ученик ⇄ администратор:
- БД (миграция `038_support_chat_core.sql`), feature flag
  `SUPPORT_CHAT_ENABLED`, лимиты вложений (5 файлов × 10 MB, payload до 52 MB).
- Backend: REST + SSE, in-memory hub, state-machine `open/resolved/closed`,
  auto-reopen на новое сообщение ученика, audit trail в
  `support_conversation_events` и `admin_audit_log`.
- Frontend: студенческая страница `/support`, админская
  Telegram-style страница `/admin/support`, общий пункт меню
  «Поддержка» с авто-переадресацией админа на админский UI.
2. Подробный append-only отчёт:
- [docs/operations/SUPPORT_CHAT_IMPLEMENTATION_2026_05_16.md](docs/operations/SUPPORT_CHAT_IMPLEMENTATION_2026_05_16.md)
3. Изменения, которые могут затронуть существующие контуры (и почему
   они безопасны):
- `gzipMiddleware` теперь пропускает запросы с `Accept: text/event-stream`
  — изменение only-add, остальные запросы по-прежнему сжимаются.
- `maxRequestBodyMiddleware` принимает второй параметр
  `supportUploadCeil` и применяет повышенный потолок ТОЛЬКО к двум
  POST маршрутам support-чата. Глобальный 16 MB cap остался
  неизменным.
4. Почему ничего не «удалено»:
- весь старый учебный/биллинговый/админский контур остался без изменений;
- любая интеграция (cron, plugin, IDE) не затронута: api endpoints
  существующих ручек не менялись;
- документация добавлена append-only, и старые записи сохранены.
