-- 014_python_task_copy_cleanup_for_variables.sql
--
-- Purpose:
-- 1) Align lesson copy with the updated UX (no misleading inline "formula/value chips").
-- 2) Make fixed variable values explicit in human-readable form.
-- 3) Update the "Анкета" sample age to 25 consistently in statement/solution/tests.

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero'
      AND m.position = 1
      AND l.position = 1
)
UPDATE tasks t
SET statement_md = $$
Задай значения переменных:

Имя - Анна
Возраст - 25
Город - Москва

Выведи анкету в формате:
Имя: Анна
Возраст: 25
Город: Москва
$$,
    solution_code = E'name = "Анна"\nage = 25\ncity = "Москва"\n\nprint("Имя:", name)\nprint("Возраст:", age)\nprint("Город:", city)\n',
    updated_at = NOW()
FROM lesson_ref lr
WHERE t.lesson_id = lr.lesson_id
  AND t.title = 'Анкета';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = current_schema()
          AND table_name = 'task_tests'
    ) THEN
        WITH lesson_ref AS (
            SELECT l.id AS lesson_id
            FROM lessons l
            JOIN modules m ON m.id = l.module_id
            JOIN courses c ON c.id = m.course_id
            WHERE c.slug = 'python-zero'
              AND m.position = 1
              AND l.position = 1
        )
        UPDATE task_tests tt
        SET expected_output = E'Имя: Анна\nВозраст: 25\nГород: Москва'
        FROM tasks t
        JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
        WHERE tt.task_id = t.id
          AND t.title = 'Анкета';
    END IF;
END $$;

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero'
      AND m.position = 1
      AND l.position = 1
)
UPDATE tasks t
SET statement_md = $$
В стартовом коде программа выводит слово `name` вместо значения переменной.

Даны значения переменных:
Имя - Анна

Исправьте программу. Итоговый вывод:
Привет, Анна
$$,
    updated_at = NOW()
FROM lesson_ref lr
WHERE t.lesson_id = lr.lesson_id
  AND t.title = 'Переменная или текст?';

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero'
      AND m.position = 1
      AND l.position = 1
)
UPDATE lesson_blocks lb
SET content_md = $$
Исправьте программу. Итоговый вывод должен быть: `Привет, Анна`.
$$,
    updated_at = NOW()
FROM lesson_ref lr
WHERE lb.lesson_id = lr.lesson_id
  AND lb.position = 12
  AND lb.block_type = 'practice';
