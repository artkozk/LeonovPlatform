-- 036_user_lesson_block_progress.sql
-- Canonical lesson/block completion model for web + plugin + worker flows.

CREATE TABLE IF NOT EXISTS user_lesson_block_progress (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    block_id UUID NOT NULL REFERENCES lesson_blocks(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'completed',
    source TEXT NOT NULL DEFAULT 'manual',
    submission_id UUID REFERENCES submissions(id) ON DELETE SET NULL,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, block_id),
    CONSTRAINT chk_user_lesson_block_progress_status CHECK (status IN ('completed')),
    CONSTRAINT chk_user_lesson_block_progress_source CHECK (source IN ('manual', 'quiz', 'submission', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_user_lesson_block_progress_user_lesson
    ON user_lesson_block_progress (user_id, lesson_id);

CREATE INDEX IF NOT EXISTS idx_user_lesson_block_progress_user_updated
    ON user_lesson_block_progress (user_id, updated_at DESC);

-- Backfill completion from already accepted submissions so historical progress is not lost.
INSERT INTO user_lesson_block_progress(
    user_id,
    lesson_id,
    block_id,
    status,
    source,
    submission_id,
    completed_at,
    created_at,
    updated_at
)
SELECT
    s.user_id,
    lb.lesson_id,
    lb.id,
    'completed',
    'submission',
    s.id,
    COALESCE(s.updated_at, s.created_at, NOW()),
    NOW(),
    NOW()
FROM submissions s
JOIN lesson_blocks lb ON lb.task_id = s.task_id
WHERE s.status = 'accepted'
ON CONFLICT (user_id, block_id) DO UPDATE
SET lesson_id = EXCLUDED.lesson_id,
    status = 'completed',
    source = CASE
        WHEN user_lesson_block_progress.source = 'quiz' THEN user_lesson_block_progress.source
        ELSE EXCLUDED.source
    END,
    submission_id = COALESCE(user_lesson_block_progress.submission_id, EXCLUDED.submission_id),
    completed_at = COALESCE(user_lesson_block_progress.completed_at, EXCLUDED.completed_at, NOW()),
    updated_at = NOW();
