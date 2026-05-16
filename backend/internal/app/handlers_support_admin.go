package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

// ============================================================================
// Support chat — admin-facing handlers (2026-05-16).
//
// Контракт см. в blueprint §8.2. Все handler'ы предполагают, что
// middleware `authMiddleware()` + `adminOnly()` уже отработали.
//
// Жизненный цикл (blueprint §4.2):
//   open  → resolved   (admin, with resolution_note)
//   resolved → open    (auto, при student-сообщении; см. support_messages.go)
//   resolved → closed  (admin)
//   closed → open      (admin, восстановление кейса)
//
// Каждая смена статуса/оператора фиксируется в support_conversation_events
// и в admin_audit_log.
// ============================================================================

// ListAdminSupportConversations: GET /api/v1/admin/support/conversations?status=&limit=
func (a *App) ListAdminSupportConversations(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	statusFilter := strings.TrimSpace(c.Query("status"))
	if statusFilter != "" && !isValidSupportStatus(statusFilter) {
		c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "invalid status filter"})
		return
	}
	limit := parseLimitOr(c.Query("limit"), 100)
	items, err := a.listAdminConversations(c.Request.Context(), statusFilter, limit)
	if err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"items": items})
}

// GetAdminSupportConversation: GET /api/v1/admin/support/conversations/:conversationID
func (a *App) GetAdminSupportConversation(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	conversationID, ok := requireConversationID(c)
	if !ok {
		return
	}
	conv, err := a.loadConversationByID(c.Request.Context(), conversationID)
	if err != nil {
		if supportIsNoRows(err) || errors.Is(err, pgx.ErrNoRows) {
			c.AbortWithStatusJSON(http.StatusNotFound, APIError{Error: "conversation not found"})
			return
		}
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, conv)
}

// ListAdminSupportMessages: GET /api/v1/admin/support/conversations/:conversationID/messages
func (a *App) ListAdminSupportMessages(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	conversationID, ok := requireConversationID(c)
	if !ok {
		return
	}
	if exists, err := a.conversationExists(c.Request.Context(), conversationID); err != nil {
		internalServerError(c, err)
		return
	} else if !exists {
		c.AbortWithStatusJSON(http.StatusNotFound, APIError{Error: "conversation not found"})
		return
	}

	cursorStr := strings.TrimSpace(c.Query("cursor"))
	var before *time.Time
	if cursorStr != "" {
		if t, err := time.Parse(time.RFC3339Nano, cursorStr); err == nil {
			before = &t
		}
	}
	limit := parseLimitOr(c.Query("limit"), 50)

	msgs, err := a.listMessages(c.Request.Context(), conversationID, limit, before)
	if err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"messages": msgs})
}

// PostAdminSupportMessage: POST /api/v1/admin/support/conversations/:conversationID/messages
func (a *App) PostAdminSupportMessage(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	uctx, ok := userFromContext(c)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "unauthorized"})
		return
	}
	conversationID, ok := requireConversationID(c)
	if !ok {
		return
	}
	if exists, err := a.conversationExists(c.Request.Context(), conversationID); err != nil {
		internalServerError(c, err)
		return
	} else if !exists {
		c.AbortWithStatusJSON(http.StatusNotFound, APIError{Error: "conversation not found"})
		return
	}

	c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, a.Cfg.SupportChatMaxMessagePayloadBytes)
	if err := c.Request.ParseMultipartForm(a.Cfg.SupportChatMaxMessagePayloadBytes); err != nil {
		c.AbortWithStatusJSON(http.StatusRequestEntityTooLarge, APIError{Error: "request too large"})
		return
	}
	body := strings.TrimSpace(c.PostForm("body"))
	files := c.Request.MultipartForm.File["files"]
	if len(files) > a.Cfg.SupportChatMaxAttachmentsPerMessage {
		c.AbortWithStatusJSON(http.StatusBadRequest, APIError{
			Error: fmt.Sprintf("attachments limit exceeded: maximum %d files per message", a.Cfg.SupportChatMaxAttachmentsPerMessage),
		})
		return
	}
	if body == "" && len(files) == 0 {
		c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "message body or attachment required"})
		return
	}
	for _, fh := range files {
		if fh.Size > a.Cfg.SupportChatMaxAttachmentBytes {
			c.AbortWithStatusJSON(http.StatusRequestEntityTooLarge, APIError{
				Error: fmt.Sprintf("attachment %q too large", filepath.Base(fh.Filename)),
			})
			return
		}
	}

	msg, _, err := a.createSupportMessage(c.Request.Context(), conversationID, uctx.ID, SupportSenderAdmin, body, files, c.SaveUploadedFile)
	if err != nil {
		internalServerError(c, err)
		return
	}
	a.publishMessageEvent(c.Request.Context(), conversationID, msg, false)

	c.JSON(http.StatusCreated, msg)
}

// PatchAdminSupportConversation: PATCH /api/v1/admin/support/conversations/:conversationID
//
// Тело: { "action": "assign|unassign|resolve|reopen|close", ... }
//   - assign: { "action":"assign", "adminUserId":"<uuid>" }    (можно reassign)
//   - unassign: { "action":"unassign" }
//   - resolve: { "action":"resolve", "resolutionNote":"<text>" }
//   - reopen:  { "action":"reopen" }                             (admin-driven reopen из closed)
//   - close:   { "action":"close" }                              (только из resolved)
//
// Все переходы валидируются на backend. Любая попытка некорректного
// перехода → 409 Conflict.
type supportPatchRequest struct {
	Action         string `json:"action"`
	AdminUserID    string `json:"adminUserId"`
	ResolutionNote string `json:"resolutionNote"`
}

func (a *App) PatchAdminSupportConversation(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	uctx, ok := userFromContext(c)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "unauthorized"})
		return
	}
	conversationID, ok := requireConversationID(c)
	if !ok {
		return
	}

	var req supportPatchRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "invalid json"})
		return
	}
	action := strings.ToLower(strings.TrimSpace(req.Action))

	ctx := c.Request.Context()
	tx, err := a.DB.Begin(ctx)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(ctx)

	var (
		currentStatus       string
		currentAssignedRaw  *string
	)
	if err := tx.QueryRow(ctx, `
		SELECT status, assigned_admin_user_id::text
		FROM support_conversations WHERE id = $1 FOR UPDATE
	`, conversationID).Scan(&currentStatus, &currentAssignedRaw); err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			c.AbortWithStatusJSON(http.StatusNotFound, APIError{Error: "conversation not found"})
			return
		}
		internalServerError(c, err)
		return
	}
	currentAssigned := ""
	if currentAssignedRaw != nil {
		currentAssigned = *currentAssignedRaw
	}

	auditDetails := map[string]any{
		"conversationId": conversationID,
		"action":         action,
		"previousStatus": currentStatus,
	}

	switch action {
	case "assign":
		newAdminID := strings.TrimSpace(req.AdminUserID)
		if _, err := uuid.Parse(newAdminID); err != nil {
			c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "adminUserId required"})
			return
		}
		// Проверяем, что назначаемый — действительно админ.
		var role string
		if err := tx.QueryRow(ctx, `SELECT role FROM users WHERE id = $1`, newAdminID).Scan(&role); err != nil {
			c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "target user not found"})
			return
		}
		if role != "admin" {
			c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "target user is not admin"})
			return
		}
		if _, err := tx.Exec(ctx, `
			UPDATE support_conversations
			SET assigned_admin_user_id = $2::uuid, updated_at = NOW()
			WHERE id = $1
		`, conversationID, newAdminID); err != nil {
			internalServerError(c, err)
			return
		}
		evt := SupportEventAssigned
		if currentAssigned != "" && currentAssigned != newAdminID {
			evt = SupportEventReassigned
		}
		if err := insertEventTx(ctx, tx, conversationID, evt, uctx.ID, map[string]any{
			"adminUserId":      newAdminID,
			"previousAdminId":  currentAssigned,
		}); err != nil {
			internalServerError(c, err)
			return
		}
		auditDetails["newAdminUserId"] = newAdminID
		auditDetails["previousAdminUserId"] = currentAssigned

	case "unassign":
		if _, err := tx.Exec(ctx, `
			UPDATE support_conversations
			SET assigned_admin_user_id = NULL, updated_at = NOW()
			WHERE id = $1
		`, conversationID); err != nil {
			internalServerError(c, err)
			return
		}
		if err := insertEventTx(ctx, tx, conversationID, SupportEventUnassigned, uctx.ID, map[string]any{
			"previousAdminId": currentAssigned,
		}); err != nil {
			internalServerError(c, err)
			return
		}
		auditDetails["previousAdminUserId"] = currentAssigned

	case "resolve":
		if currentStatus != SupportStatusOpen {
			c.AbortWithStatusJSON(http.StatusConflict, APIError{Error: "resolve allowed only from open"})
			return
		}
		note := strings.TrimSpace(req.ResolutionNote)
		if note == "" {
			c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "resolutionNote is required"})
			return
		}
		if _, err := tx.Exec(ctx, `
			UPDATE support_conversations
			SET status = 'resolved',
			    resolved_at = NOW(),
			    resolved_by_user_id = $2,
			    resolution_note = $3,
			    updated_at = NOW()
			WHERE id = $1
		`, conversationID, uctx.ID, note); err != nil {
			internalServerError(c, err)
			return
		}
		if err := insertEventTx(ctx, tx, conversationID, SupportEventResolved, uctx.ID, map[string]any{
			"resolutionNote": note,
		}); err != nil {
			internalServerError(c, err)
			return
		}
		auditDetails["resolutionNote"] = note

	case "reopen":
		// admin-driven reopen — допустим из resolved или closed.
		if currentStatus == SupportStatusOpen {
			c.AbortWithStatusJSON(http.StatusConflict, APIError{Error: "conversation already open"})
			return
		}
		if _, err := tx.Exec(ctx, `
			UPDATE support_conversations
			SET status = 'open',
			    resolved_at = NULL, resolved_by_user_id = NULL, resolution_note = NULL,
			    closed_at = NULL, closed_by_user_id = NULL,
			    updated_at = NOW()
			WHERE id = $1
		`, conversationID); err != nil {
			internalServerError(c, err)
			return
		}
		if err := insertEventTx(ctx, tx, conversationID, SupportEventReopened, uctx.ID, map[string]any{
			"reason":         "admin_action",
			"previousStatus": currentStatus,
		}); err != nil {
			internalServerError(c, err)
			return
		}

	case "close":
		if currentStatus != SupportStatusResolved {
			c.AbortWithStatusJSON(http.StatusConflict, APIError{Error: "close allowed only from resolved"})
			return
		}
		if _, err := tx.Exec(ctx, `
			UPDATE support_conversations
			SET status = 'closed',
			    closed_at = NOW(),
			    closed_by_user_id = $2,
			    updated_at = NOW()
			WHERE id = $1
		`, conversationID, uctx.ID); err != nil {
			internalServerError(c, err)
			return
		}
		if err := insertEventTx(ctx, tx, conversationID, SupportEventClosed, uctx.ID, nil); err != nil {
			internalServerError(c, err)
			return
		}

	default:
		c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "unknown action"})
		return
	}

	// admin_audit_log запись для всех ops (blueprint §13 п.4 «audit trail»).
	if _, err := tx.Exec(ctx, `
		INSERT INTO admin_audit_log (admin_user_id, action, entity_type, entity_id, details)
		VALUES ($1, $2, 'support_conversation', $3, $4::jsonb)
	`, uctx.ID, "support_"+action, conversationID, jsonMarshal(auditDetails)); err != nil {
		internalServerError(c, err)
		return
	}

	if err := tx.Commit(ctx); err != nil {
		internalServerError(c, err)
		return
	}

	a.publishConversationUpdate(ctx, conversationID)

	conv, err := a.loadConversationByID(ctx, conversationID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, conv)
}

// MarkAdminSupportRead: POST /api/v1/admin/support/conversations/:conversationID/read
func (a *App) MarkAdminSupportRead(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	conversationID, ok := requireConversationID(c)
	if !ok {
		return
	}
	updated, err := a.markIncomingAsRead(c.Request.Context(), conversationID, SupportSenderAdmin)
	if err != nil {
		internalServerError(c, err)
		return
	}
	a.publishStatusUpdate(c.Request.Context(), conversationID, updated)
	c.JSON(http.StatusOK, gin.H{"updatedMessages": len(updated)})
}

// ListSupportEvents: GET /api/v1/admin/support/conversations/:conversationID/events
//
// Возвращает audit-trail диалога (assigned/reopened/resolved/closed/message_sent).
// Это позволяет ревьюить операторскую работу и расследовать инциденты.
func (a *App) ListAdminSupportEvents(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	conversationID, ok := requireConversationID(c)
	if !ok {
		return
	}
	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT e.id, e.conversation_id, e.event_type,
		       COALESCE(e.actor_user_id::text, ''),
		       COALESCE(u.first_name, ''), COALESCE(u.last_name, ''),
		       COALESCE(u.username, ''), COALESCE(u.email, ''),
		       e.payload, e.created_at
		FROM support_conversation_events e
		LEFT JOIN users u ON u.id = e.actor_user_id
		WHERE e.conversation_id = $1
		ORDER BY e.created_at ASC, e.id ASC
	`, conversationID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()
	var out []SupportEventDTO
	for rows.Next() {
		var (
			dto       SupportEventDTO
			payloadJS []byte
			first, last, uname, email string
		)
		if err := rows.Scan(&dto.ID, &dto.ConversationID, &dto.EventType, &dto.ActorUserID,
			&first, &last, &uname, &email,
			&payloadJS, &dto.CreatedAt,
		); err != nil {
			internalServerError(c, err)
			return
		}
		dto.ActorName = supportDisplayName(first, last, uname, email)
		dto.Payload = unmarshalPayload(payloadJS)
		out = append(out, dto)
	}
	if err := rows.Err(); err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"items": out})
}

// ----------------------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------------------

func isValidSupportStatus(s string) bool {
	return s == SupportStatusOpen || s == SupportStatusResolved || s == SupportStatusClosed
}

func requireConversationID(c *gin.Context) (string, bool) {
	id := strings.TrimSpace(c.Param("conversationID"))
	if _, err := uuid.Parse(id); err != nil {
		c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "invalid conversation id"})
		return "", false
	}
	return id, true
}

func (a *App) conversationExists(ctx context.Context, conversationID string) (bool, error) {
	var exists bool
	if err := a.DB.QueryRow(ctx, `
		SELECT EXISTS(SELECT 1 FROM support_conversations WHERE id = $1)
	`, conversationID).Scan(&exists); err != nil {
		return false, err
	}
	return exists, nil
}

func insertEventTx(ctx context.Context, tx pgx.Tx, conversationID, eventType, actorUserID string, payload map[string]any) error {
	if payload == nil {
		payload = map[string]any{}
	}
	_, err := tx.Exec(ctx, `
		INSERT INTO support_conversation_events (conversation_id, event_type, actor_user_id, payload)
		VALUES ($1, $2, NULLIF($3, '')::uuid, $4::jsonb)
	`, conversationID, eventType, actorUserID, jsonMarshal(payload))
	return err
}

func unmarshalPayload(raw []byte) map[string]any {
	if len(raw) == 0 {
		return nil
	}
	out := map[string]any{}
	if err := json.Unmarshal(raw, &out); err != nil {
		return nil
	}
	return out
}
