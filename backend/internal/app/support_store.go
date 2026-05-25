package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
)

// ============================================================================
// Support chat store — все SQL-операции по support_* таблицам.
//
// Зачем отдельный файл (а не «всё в handlers»):
//   1. Чтобы handlers были тонкие: проверка прав → store → DTO → SSE.
//   2. Чтобы все запросы по чату были в одном месте и видно было, что
//      именно индексируется (см. план в blueprint §10 «P95» и
//      anti-N+1 чеклист в §13 п.7).
//
// Inviolable invariants enforced here:
//   1. Список диалогов админу собирается одним запросом с JOIN на users —
//      никакого N+1 (blueprint §13).
//   2. История сообщений в диалоге выгружается одним запросом + один
//      запрос на все вложения этих сообщений (тоже без N+1).
//   3. preview сообщения обрезается на 240 символов — этого хватает для
//      Telegram-style списка, а INSERT/UPDATE остаются дешёвыми.
// ============================================================================

const supportPreviewMaxRunes = 240

func supportPreviewFromBody(body string, hasAttachments bool) string {
	trimmed := strings.TrimSpace(body)
	if trimmed == "" {
		if hasAttachments {
			return "📎 вложение"
		}
		return ""
	}
	runes := []rune(trimmed)
	if len(runes) > supportPreviewMaxRunes {
		runes = runes[:supportPreviewMaxRunes]
	}
	return string(runes)
}

// SupportStudentDisplayNamer определяет, как формировать displayName ученика
// для админского списка. Сейчас просто email/username; вынесено в отдельный
// helper, чтобы избежать дублирования в нескольких запросах.
func supportDisplayName(firstName, lastName, username, email string) string {
	full := strings.TrimSpace(firstName + " " + lastName)
	if full != "" {
		return full
	}
	if u := strings.TrimSpace(username); u != "" {
		return u
	}
	return strings.TrimSpace(email)
}

// ----------------------------------------------------------------------------
// Conversation lookup / creation
// ----------------------------------------------------------------------------

// getOrCreateStudentConversation возвращает (создаёт) общий диалог для
// данного студента. Гарантирует один диалог на ученика (UNIQUE constraint).
//
// Параллельная гонка двух запросов от одного клиента разруливается через
// `ON CONFLICT DO UPDATE` с `RETURNING` — мы всегда получаем актуальный
// id, даже если строка уже была создана.
func (a *App) getOrCreateStudentConversation(ctx context.Context, studentUserID string) (SupportConversationDTO, error) {
	var id string
	if err := a.DB.QueryRow(ctx, `
		INSERT INTO support_conversations (student_user_id)
		VALUES ($1)
		ON CONFLICT (student_user_id) DO UPDATE
		   SET updated_at = support_conversations.updated_at
		RETURNING id
	`, studentUserID).Scan(&id); err != nil {
		return SupportConversationDTO{}, fmt.Errorf("upsert support conversation: %w", err)
	}

	// Если это первая вставка — событие 'created'. Проверяем по отсутствию
	// 'created' event'а; cheap, и сразу гарантирует идемпотентность.
	_, _ = a.DB.Exec(ctx, `
		INSERT INTO support_conversation_events (conversation_id, event_type, actor_user_id, payload)
		SELECT $1, 'created', $2, '{}'::jsonb
		WHERE NOT EXISTS (
			SELECT 1 FROM support_conversation_events
			WHERE conversation_id = $1 AND event_type = 'created'
		)
	`, id, studentUserID)

	return a.loadConversationByID(ctx, id)
}

// loadConversationByID — выгружает диалог с join'ом на users (для
// display name администратора и студента).
func (a *App) loadConversationByID(ctx context.Context, conversationID string) (SupportConversationDTO, error) {
	row := a.DB.QueryRow(ctx, `
		SELECT
			c.id,
			c.student_user_id,
			COALESCE(stu.first_name, ''),
			COALESCE(stu.last_name, ''),
			COALESCE(stu.username, ''),
			COALESCE(stu.email, ''),
			c.status,
			COALESCE(c.assigned_admin_user_id::text, ''),
			COALESCE(adm.first_name, '') AS admin_first,
			COALESCE(adm.last_name, '')  AS admin_last,
			COALESCE(adm.username, '')   AS admin_username,
			COALESCE(adm.email, '')      AS admin_email,
			COALESCE(c.resolution_note, ''),
			c.resolved_at,
			c.closed_at,
			c.last_message_at,
			COALESCE(c.last_message_preview, ''),
			COALESCE(c.last_message_sender_role, ''),
			c.student_unread_count,
			c.admin_unread_count,
			c.created_at,
			c.updated_at
		FROM support_conversations c
		LEFT JOIN users stu ON stu.id = c.student_user_id
		LEFT JOIN users adm ON adm.id = c.assigned_admin_user_id
		WHERE c.id = $1
	`, conversationID)

	var (
		dto         SupportConversationDTO
		studFirst   string
		studLast    string
		studUser    string
		studEmail   string
		adminFirst  string
		adminLast   string
		adminUser   string
		adminEmail  string
	)
	if err := row.Scan(
		&dto.ID,
		&dto.StudentUserID,
		&studFirst,
		&studLast,
		&studUser,
		&studEmail,
		&dto.Status,
		&dto.AssignedAdminUserID,
		&adminFirst,
		&adminLast,
		&adminUser,
		&adminEmail,
		&dto.ResolutionNote,
		&dto.ResolvedAt,
		&dto.ClosedAt,
		&dto.LastMessageAt,
		&dto.LastMessagePreview,
		&dto.LastMessageSenderRole,
		&dto.StudentUnreadCount,
		&dto.AdminUnreadCount,
		&dto.CreatedAt,
		&dto.UpdatedAt,
	); err != nil {
		return SupportConversationDTO{}, fmt.Errorf("load support conversation: %w", err)
	}
	dto.StudentDisplayName = supportDisplayName(studFirst, studLast, studUser, studEmail)
	dto.StudentEmail = studEmail
	if dto.AssignedAdminUserID != "" {
		dto.AssignedAdminName = supportDisplayName(adminFirst, adminLast, adminUser, adminEmail)
	}
	return dto, nil
}

// listAdminConversations возвращает админский список диалогов:
//   - JOIN на users для display name студента,
//   - сортировка по last_message_at DESC (NULLS LAST).
// Никакого N+1 — один запрос.
func (a *App) listAdminConversations(ctx context.Context, statusFilter string, limit int) ([]SupportConversationDTO, error) {
	if limit <= 0 || limit > 200 {
		limit = 100
	}
	args := []any{limit}
	statusCondition := ""
	if statusFilter != "" {
		args = append(args, statusFilter)
		statusCondition = "WHERE c.status = $2"
	}

	rows, err := a.DB.Query(ctx, fmt.Sprintf(`
		SELECT
			c.id,
			c.student_user_id,
			COALESCE(stu.first_name, ''),
			COALESCE(stu.last_name, ''),
			COALESCE(stu.username, ''),
			COALESCE(stu.email, ''),
			c.status,
			COALESCE(c.assigned_admin_user_id::text, ''),
			COALESCE(adm.first_name, '') AS admin_first,
			COALESCE(adm.last_name, '')  AS admin_last,
			COALESCE(adm.username, '')   AS admin_username,
			COALESCE(adm.email, '')      AS admin_email,
			COALESCE(c.resolution_note, ''),
			c.resolved_at,
			c.closed_at,
			c.last_message_at,
			COALESCE(c.last_message_preview, ''),
			COALESCE(c.last_message_sender_role, ''),
			c.student_unread_count,
			c.admin_unread_count,
			c.created_at,
			c.updated_at
		FROM support_conversations c
		LEFT JOIN users stu ON stu.id = c.student_user_id
		LEFT JOIN users adm ON adm.id = c.assigned_admin_user_id
		%s
		ORDER BY c.last_message_at DESC NULLS LAST, c.created_at DESC
		LIMIT $1
	`, statusCondition), args...)
	if err != nil {
		return nil, fmt.Errorf("list support conversations: %w", err)
	}
	defer rows.Close()

	var out []SupportConversationDTO
	for rows.Next() {
		var (
			dto         SupportConversationDTO
			studFirst   string
			studLast    string
			studUser    string
			studEmail   string
			adminFirst  string
			adminLast   string
			adminUser   string
			adminEmail  string
		)
		if err := rows.Scan(
			&dto.ID,
			&dto.StudentUserID,
			&studFirst,
			&studLast,
			&studUser,
			&studEmail,
			&dto.Status,
			&dto.AssignedAdminUserID,
			&adminFirst,
			&adminLast,
			&adminUser,
			&adminEmail,
			&dto.ResolutionNote,
			&dto.ResolvedAt,
			&dto.ClosedAt,
			&dto.LastMessageAt,
			&dto.LastMessagePreview,
			&dto.LastMessageSenderRole,
			&dto.StudentUnreadCount,
			&dto.AdminUnreadCount,
			&dto.CreatedAt,
			&dto.UpdatedAt,
		); err != nil {
			return nil, fmt.Errorf("scan support conversation row: %w", err)
		}
		dto.StudentDisplayName = supportDisplayName(studFirst, studLast, studUser, studEmail)
		dto.StudentEmail = studEmail
		if dto.AssignedAdminUserID != "" {
			dto.AssignedAdminName = supportDisplayName(adminFirst, adminLast, adminUser, adminEmail)
		}
		out = append(out, dto)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate support conversation rows: %w", err)
	}
	return out, nil
}

// ----------------------------------------------------------------------------
// Messages
// ----------------------------------------------------------------------------

// listMessages — последние N сообщений с прикреплёнными вложениями.
// Алгоритм anti-N+1:
//   1. Один SELECT по support_messages с LIMIT/cursor.
//   2. Один SELECT по support_message_attachments WHERE message_id = ANY(...).
//   3. Сшиваем в Go.
func (a *App) listMessages(ctx context.Context, conversationID string, limit int, beforeCursor *time.Time) ([]SupportMessageDTO, error) {
	if limit <= 0 || limit > 200 {
		limit = 50
	}

	args := []any{conversationID, limit}
	cursorCond := ""
	if beforeCursor != nil {
		args = append(args, *beforeCursor)
		cursorCond = "AND created_at < $3"
	}

	rows, err := a.DB.Query(ctx, fmt.Sprintf(`
		SELECT id, conversation_id, sender_user_id, sender_role,
		       COALESCE(body_text, ''), status, delivered_at, read_at,
		       has_attachments, created_at
		FROM support_messages
		WHERE conversation_id = $1 %s
		ORDER BY created_at DESC, id DESC
		LIMIT $2
	`, cursorCond), args...)
	if err != nil {
		return nil, fmt.Errorf("list support messages: %w", err)
	}
	defer rows.Close()

	var msgs []SupportMessageDTO
	var ids []string
	for rows.Next() {
		var m SupportMessageDTO
		if err := rows.Scan(
			&m.ID, &m.ConversationID, &m.SenderUserID, &m.SenderRole,
			&m.BodyText, &m.Status, &m.DeliveredAt, &m.ReadAt,
			&m.HasAttachments, &m.CreatedAt,
		); err != nil {
			return nil, fmt.Errorf("scan support message row: %w", err)
		}
		msgs = append(msgs, m)
		ids = append(ids, m.ID)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate support message rows: %w", err)
	}

	if len(ids) == 0 {
		return reverseMessages(msgs), nil
	}

	// Загружаем все вложения этих сообщений одним запросом.
	atts, err := a.listAttachmentsForMessages(ctx, ids)
	if err != nil {
		return nil, err
	}
	for i := range msgs {
		if attsForMsg, ok := atts[msgs[i].ID]; ok {
			msgs[i].Attachments = attsForMsg
		}
	}

	return reverseMessages(msgs), nil
}

func reverseMessages(in []SupportMessageDTO) []SupportMessageDTO {
	out := make([]SupportMessageDTO, len(in))
	for i, m := range in {
		out[len(in)-1-i] = m
	}
	return out
}

func (a *App) listAttachmentsForMessages(ctx context.Context, messageIDs []string) (map[string][]SupportAttachmentDTO, error) {
	rows, err := a.DB.Query(ctx, `
		SELECT id, message_id, original_name, mime_type, size_bytes, created_at
		FROM support_message_attachments
		WHERE message_id = ANY($1)
		ORDER BY created_at ASC
	`, messageIDs)
	if err != nil {
		return nil, fmt.Errorf("list support attachments: %w", err)
	}
	defer rows.Close()
	out := make(map[string][]SupportAttachmentDTO)
	for rows.Next() {
		var att SupportAttachmentDTO
		if err := rows.Scan(&att.ID, &att.MessageID, &att.OriginalName, &att.MimeType, &att.SizeBytes, &att.CreatedAt); err != nil {
			return nil, fmt.Errorf("scan support attachment row: %w", err)
		}
		att.DownloadURL = "/api/v1/support/attachments/" + att.ID
		out[att.MessageID] = append(out[att.MessageID], att)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate support attachment rows: %w", err)
	}
	return out, nil
}

// loadMessage — выгружает одно сообщение с вложениями (используется после insert).
func (a *App) loadMessage(ctx context.Context, messageID string) (SupportMessageDTO, error) {
	var m SupportMessageDTO
	if err := a.DB.QueryRow(ctx, `
		SELECT id, conversation_id, sender_user_id, sender_role,
		       COALESCE(body_text, ''), status, delivered_at, read_at,
		       has_attachments, created_at
		FROM support_messages WHERE id = $1
	`, messageID).Scan(
		&m.ID, &m.ConversationID, &m.SenderUserID, &m.SenderRole,
		&m.BodyText, &m.Status, &m.DeliveredAt, &m.ReadAt,
		&m.HasAttachments, &m.CreatedAt,
	); err != nil {
		return SupportMessageDTO{}, fmt.Errorf("load support message: %w", err)
	}
	if m.HasAttachments {
		atts, err := a.listAttachmentsForMessages(ctx, []string{m.ID})
		if err != nil {
			return SupportMessageDTO{}, err
		}
		if perMsg, ok := atts[m.ID]; ok {
			m.Attachments = perMsg
		}
	}
	return m, nil
}

// ----------------------------------------------------------------------------
// Events / audit trail
// ----------------------------------------------------------------------------

// recordEvent создаёт запись в support_conversation_events. Используется
// при assign/reassign/resolve/reopen/close. См. blueprint §4.3, §13 п.4.
func (a *App) recordEvent(ctx context.Context, conversationID, eventType, actorUserID string, payload map[string]any) error {
	if payload == nil {
		payload = map[string]any{}
	}
	pj, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal support event payload: %w", err)
	}
	if _, err := a.DB.Exec(ctx, `
		INSERT INTO support_conversation_events (conversation_id, event_type, actor_user_id, payload)
		VALUES ($1, $2, NULLIF($3, '')::uuid, $4::jsonb)
	`, conversationID, eventType, actorUserID, string(pj)); err != nil {
		return fmt.Errorf("insert support event: %w", err)
	}
	return nil
}

// ----------------------------------------------------------------------------
// Validation helpers
// ----------------------------------------------------------------------------

var errSupportConversationNotFound = errors.New("support conversation not found")

// supportIsNoRows — pgx-aware вариант http_helpers.isNoRows (тот опирается
// на database/sql). Используется внутри support-store, чтобы не зависеть
// от внешних SQL-драйверов.
func supportIsNoRows(err error) bool {
	return errors.Is(err, pgx.ErrNoRows)
}
