-- 030_backend_hardening_materials_perf.sql
--
-- Purpose:
-- 1) Speed up lessons/tasks catalog reads used by CoursesPage and TasksPage.
-- 2) Improve queue reconciler scans on queued submissions.
-- 3) Improve refresh-token user-wide revocation paths.

CREATE INDEX IF NOT EXISTS idx_lesson_blocks_lesson_published_position
    ON lesson_blocks(lesson_id, is_published, position);

CREATE INDEX IF NOT EXISTS idx_tasks_lesson_published_difficulty_title
    ON tasks(lesson_id, is_published, difficulty, title);

CREATE INDEX IF NOT EXISTS idx_submissions_status_updated_created
    ON submissions(status, updated_at, created_at);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_expires
    ON refresh_tokens(user_id, expires_at);
