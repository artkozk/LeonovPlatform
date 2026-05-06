-- 034_plugin_task_open_progress.sql
-- Stores user "task opened" intent from IDE plugin so catalog can mark tasks as IN_PROGRESS
-- even before the first submission is sent.

CREATE TABLE IF NOT EXISTS user_task_open_progress (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, task_id)
);

CREATE INDEX IF NOT EXISTS idx_user_task_open_progress_user_opened
    ON user_task_open_progress (user_id, opened_at DESC);
