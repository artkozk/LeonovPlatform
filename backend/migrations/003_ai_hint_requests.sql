-- 003_ai_hint_requests.sql

CREATE TABLE IF NOT EXISTS ai_hint_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    plan_code TEXT NOT NULL,
    status TEXT NOT NULL,
    model TEXT,
    source_code_length INTEGER NOT NULL DEFAULT 0,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    response_text TEXT,
    error_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_hint_requests_user_created
    ON ai_hint_requests(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_hint_requests_task_created
    ON ai_hint_requests(task_id, created_at DESC);
