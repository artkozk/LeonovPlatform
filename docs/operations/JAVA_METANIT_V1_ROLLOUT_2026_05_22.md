# Java Metanit v1 Rollout — 2026-05-22

## Что сделано

1. Добавлен новый воспроизводимый пакет материалов `материалы/java_metanit_v1`.
2. Реализован краулер Metanit (`build_course.py`) с browser-like headers для обхода защиты 403.
3. Краулер стартует с `https://metanit.com/java/tutorial/1.2.php` и обходит все ссылки формата `/java/tutorial/<chapter>.<page>.php`.
4. По итогам текущего snapshot собрано:
- 16 модулей (главы 1-16)
- 154 урока (страницы Metanit)
- 462 шага (по 3 шага на урок: theory, quiz, practice)
5. Для каждого урока автоматически созданы:
- подробный theory-step с очищенным контентом и кодовыми фрагментами
- quiz-step с structured questions и checker `quiz_single`
- practice-step на Java с checker `java_stdout`, public/hidden tests, AI hint config и подсказками
6. Сгенерирован импортный JSON:
- `материалы/java_metanit_v1/course_import.json`
7. Сгенерирована SQL-миграция:
- `backend/migrations/038_reseed_java_zero_core_metanit_v1.sql`
8. Добавлены скрипты backend/tools:
- `generate_java_metanit_v1_migration.js`
- `validate_java_metanit_v1_import.js`
9. Добавлен отчёт валидации структуры импорта:
- `docs/operations/JAVA_METANIT_V1_IMPORT_VALIDATION_2026_05_22.md`

## Контракт и совместимость

1. Публичные API backend/frontend не менялись.
2. Изменён только контент курса `java-zero-core` через reseed-миграцию.
3. Для Java practice используется язык `java` и автотесты через `task_test_cases`.
4. `source_policy` сохранён в задачах для AI hints и сопровождения checker-контекста.

## Почему сделано именно так

1. Импорт через `course_import.json` обязателен, потому что только JSON хранит структурированные quiz/checker/hints/AI поля.
2. Генерация SQL из JSON снижает риск ручных ошибок и даёт повторяемый релизный процесс.
3. Модель 3 шага на урок (theory + quiz + practice) обеспечивает одновременно подробное объяснение и измеримую проверку прогресса.
4. Очистка промо/канальных вставок из теории нужна, чтобы студент видел только учебный контент и не получал внешние отвлечения.
5. Отдельный validation report фиксирует соответствие между содержимым JSON и SQL-миграцией и помогает ревьюеру быстро проверить полноту переноса.

## Локальная валидация

1. `python материалы/java_metanit_v1/build_course.py` — PASS.
2. `python материалы/java_metanit_v1/validate_course.py` — PASS.
3. `node backend/tools/generate_java_metanit_v1_migration.js` — PASS.
4. `node backend/tools/validate_java_metanit_v1_import.js` — PASS.

## Технические метрики текущего snapshot

- modules: 16
- lessons: 154
- steps: 462
- practice tasks: 154
- quiz steps: 154
- executable java tests: 616

## Деплой и post-deploy checks

1. Миграция `038_reseed_java_zero_core_metanit_v1.sql` должна применяться через `backend/cmd/migrator`.
2. После деплоя необходимо проверить:
- `/healthz`
- `/readyz`
- открытие курса `java-zero-core`
- прохождение одного quiz-step и одного practice-step
- работу AI hint на Java practice.

## Ограничения текущей версии

1. Практические задания сгенерированы автоматически и требуют последующей педагогической полировки по аналитике первых сдач.
2. Теория извлекается из HTML-структуры страницы; при изменении DOM на стороне источника нужно перегенерировать пакет и повторно проверить выборочный quality audit.
