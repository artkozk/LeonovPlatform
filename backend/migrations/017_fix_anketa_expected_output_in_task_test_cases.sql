-- 017_fix_anketa_expected_output_in_task_test_cases.sql
--
-- Purpose:
-- 1) Fix inconsistent checker expectation for lesson 1 task "Анкета":
--    statement/solution use age=25, but some deployed DBs still keep test expected_output with age=16.
-- 2) Update canonical test table task_test_cases.
-- 3) Keep backward compatibility for legacy installations that may still have task_tests.

WITH lesson_ref AS (
    SELECT l.id AS lesson_id
    FROM lessons l
    JOIN modules m ON m.id = l.module_id
    JOIN courses c ON c.id = m.course_id
    WHERE c.slug = 'python-zero'
      AND m.position = 1
      AND l.position = 1
)
UPDATE task_test_cases tc
SET expected_output = E'Имя: Анна\nВозраст: 25\nГород: Москва'
FROM tasks t
JOIN lesson_ref lr ON lr.lesson_id = t.lesson_id
WHERE tc.task_id = t.id
  AND t.title = 'Анкета'
  AND tc.position = 1;

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
