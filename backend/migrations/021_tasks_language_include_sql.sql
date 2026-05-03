-- 021_tasks_language_include_sql.sql
--
-- Purpose:
-- 1) Guarantee SQL language availability in tasks checker schema.
-- 2) Keep backward compatibility for existing java/python task rows.

ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_tasks_language;

ALTER TABLE tasks
    ADD CONSTRAINT chk_tasks_language
    CHECK (language IN ('java', 'python', 'python3', 'py', 'sql'));
