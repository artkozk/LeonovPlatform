-- 004_tasks_unique_lesson_title.sql
--
-- Purpose:
-- 1) Remove duplicate tasks produced by repeated seed runs.
-- 2) Enforce idempotency for future seed/admin inserts by lesson/title.

WITH ranked_tasks AS (
    SELECT
        id,
        lesson_id,
        title,
        ROW_NUMBER() OVER (
            PARTITION BY lesson_id, title
            ORDER BY updated_at DESC, created_at DESC, id DESC
        ) AS rn
    FROM tasks
),
duplicates AS (
    SELECT id FROM ranked_tasks WHERE rn > 1
)
DELETE FROM task_test_cases tc
USING duplicates d
WHERE tc.task_id = d.id;

WITH ranked_tasks AS (
    SELECT
        id,
        lesson_id,
        title,
        ROW_NUMBER() OVER (
            PARTITION BY lesson_id, title
            ORDER BY updated_at DESC, created_at DESC, id DESC
        ) AS rn
    FROM tasks
)
DELETE FROM tasks t
USING ranked_tasks rt
WHERE t.id = rt.id AND rt.rn > 1;

CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_unique_lesson_title
    ON tasks(lesson_id, title);
