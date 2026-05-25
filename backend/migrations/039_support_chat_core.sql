-- 039_support_chat_core.sql
--
-- ============================================================================
-- Support Chat Core (2026-05-16)
-- ============================================================================
--
-- Этой миграцией вводится встроенная поддержка ученика ⇄ администратора.
-- Реализована в строгом соответствии с blueprint:
--   docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md
--
-- Ключевые инварианты (см. blueprint §7):
--   1. У каждого ученика — один общий диалог. Уникальность гарантирует
--      `UNIQUE(student_user_id)`.
--   2. State machine: open / resolved / closed. Любые переходы — только через
--      backend handlers; БД лишь следит за чистотой значения через CHECK.
--   3. Каждое сообщение проходит статусы sent → delivered → read; нужны
--      колонки `delivered_at`, `read_at` (NULL пока не достигнут).
--   4. Вложения — отдельная таблица, чтобы лимит «не более 5 файлов» можно
--      было проверять на стороне приложения и не плодить JSONB-массивы.
--   5. История смен оператора / статусов хранится в отдельной таблице
--      событий, поэтому даже после reopen / reassign видно всю цепочку
--      ответственных.
--
-- Append-only обоснование выбора отдельных таблиц вместо «всё в JSONB»:
--   1. Индексы по `last_message_at`, `status`, `assigned_admin_user_id`
--      требуются для админского списка чатов (P95 < 400 ms) — JSONB
--      на это работает в разы медленнее.
--   2. Аудит событий нельзя положить в conversation.events JSONB, потому что
--      при reassign/reopen нам нужно надёжно дописывать новые записи без
--      гонок и пересчёта массивов.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Conversations
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS support_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'open',
    assigned_admin_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    resolved_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    resolution_note TEXT,
    closed_at TIMESTAMPTZ,
    closed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    last_message_at TIMESTAMPTZ,
    last_message_preview TEXT,
    last_message_sender_role TEXT,
    student_unread_count INTEGER NOT NULL DEFAULT 0,
    admin_unread_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT support_conversations_student_unique UNIQUE (student_user_id),
    CONSTRAINT chk_support_conversation_status
        CHECK (status IN ('open', 'resolved', 'closed')),
    CONSTRAINT chk_support_conversation_resolved_pair
        CHECK ((status <> 'resolved') OR (resolved_at IS NOT NULL)),
    CONSTRAINT chk_support_conversation_closed_pair
        CHECK ((status <> 'closed') OR (closed_at IS NOT NULL))
);

-- Сортировка списка чатов админом (последнее сообщение в работе сверху).
CREATE INDEX IF NOT EXISTS idx_support_conversations_status_last_msg
    ON support_conversations (status, last_message_at DESC NULLS LAST);

-- «Назначенные мне» для админа.
CREATE INDEX IF NOT EXISTS idx_support_conversations_admin_status
    ON support_conversations (assigned_admin_user_id, status, last_message_at DESC NULLS LAST)
    WHERE assigned_admin_user_id IS NOT NULL;

-- ----------------------------------------------------------------------------
-- 2. Messages
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS support_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES support_conversations(id) ON DELETE CASCADE,
    sender_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sender_role TEXT NOT NULL,
    body_text TEXT,
    status TEXT NOT NULL DEFAULT 'sent',
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    has_attachments BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_support_message_status
        CHECK (status IN ('sent', 'delivered', 'read')),
    CONSTRAINT chk_support_message_sender_role
        CHECK (sender_role IN ('student', 'admin', 'system')),
    -- В чате допустимы сообщения только с вложениями (body_text NULL/'' + has_attachments TRUE).
    -- Проверку «хотя бы что-то есть» делает backend, чтобы можно было различать 400 vs 500.
    CONSTRAINT chk_support_message_body_or_attachment
        CHECK (
            (body_text IS NOT NULL AND length(trim(body_text)) > 0)
            OR has_attachments = TRUE
            OR sender_role = 'system'
        )
);

-- Лента сообщений в диалоге — пагинация по created_at.
CREATE INDEX IF NOT EXISTS idx_support_messages_conv_created
    ON support_messages (conversation_id, created_at);

-- Быстрый поиск «непрочитанных входящих» получателем.
CREATE INDEX IF NOT EXISTS idx_support_messages_conv_status
    ON support_messages (conversation_id, status);

-- ----------------------------------------------------------------------------
-- 3. Attachments
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS support_message_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES support_messages(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES support_conversations(id) ON DELETE CASCADE,
    storage_key TEXT NOT NULL,
    original_name TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_support_attachment_size CHECK (size_bytes >= 0)
);

CREATE INDEX IF NOT EXISTS idx_support_attachments_message
    ON support_message_attachments (message_id);

CREATE INDEX IF NOT EXISTS idx_support_attachments_conv
    ON support_message_attachments (conversation_id);

-- ----------------------------------------------------------------------------
-- 4. Conversation events (audit trail)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS support_conversation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES support_conversations(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_support_event_type
        CHECK (event_type IN (
            'created',
            'message_sent',
            'assigned',
            'reassigned',
            'unassigned',
            'resolved',
            'reopened',
            'closed'
        ))
);

CREATE INDEX IF NOT EXISTS idx_support_events_conv_created
    ON support_conversation_events (conversation_id, created_at);
