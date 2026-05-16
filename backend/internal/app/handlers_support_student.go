package app

import (
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

// ============================================================================
// Support chat — student-facing handlers (2026-05-16).
//
// Контракт см. в blueprint §8.1 и в API_SPEC.yaml (append-only раздел
// "Support Chat (2026-05-16)").
//
// Все handler'ы предполагают, что middleware `authMiddleware()` уже
// проставил UserContext (см. middleware.go).
//
// Запреты, которые здесь жестко зашиты (blueprint §13, §14):
//   1. У ученика всегда один диалог; нельзя обращаться к чужому conversationID.
//   2. Пустое сообщение без вложений → 400.
//   3. Больше N файлов (по умолчанию 5) → 400.
//   4. Файл больше MaxAttachmentBytes → 413.
//   5. Доступ к чужому вложению → 403/404.
//   6. Filename санитизируется, путь записи строится из storage_key, а не
//      из original_name, поэтому path traversal невозможен.
// ============================================================================

// supportEnsureEnabled — отказывает в обслуживании, если feature flag
// SUPPORT_CHAT_ENABLED=false. Возвращает true, если можно продолжать.
func (a *App) supportEnsureEnabled(c *gin.Context) bool {
	if !a.Cfg.SupportChatEnabled {
		c.AbortWithStatusJSON(http.StatusNotFound, APIError{Error: "support chat disabled"})
		return false
	}
	return true
}

// GetSupportConversation: GET /api/v1/support/conversation
//
// Возвращает (или лениво создаёт) общий диалог ученика. Гарантирует, что
// у ученика всегда не больше одного диалога.
func (a *App) GetSupportConversation(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	uctx, ok := userFromContext(c)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "unauthorized"})
		return
	}
	if uctx.Role == "admin" {
		// Админ не имеет «своего» студенческого чата. Возвращаем 404,
		// чтобы UI понимал: пускать админа в /support не нужно.
		c.JSON(http.StatusNotFound, APIError{Error: "support conversation is for students"})
		return
	}
	conv, err := a.getOrCreateStudentConversation(c.Request.Context(), uctx.ID)
	if err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, conv)
}

// ListSupportMessages: GET /api/v1/support/conversation/messages?cursor=&limit=
//
// Пагинация назад: cursor — это created_at в RFC3339 от которого нужно
// идти в прошлое. UI вызывает рекурсивно при scroll up.
func (a *App) ListSupportMessages(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	uctx, ok := userFromContext(c)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "unauthorized"})
		return
	}
	if uctx.Role == "admin" {
		c.JSON(http.StatusNotFound, APIError{Error: "support conversation is for students"})
		return
	}
	conv, err := a.getOrCreateStudentConversation(c.Request.Context(), uctx.ID)
	if err != nil {
		internalServerError(c, err)
		return
	}

	cursorStr := strings.TrimSpace(c.Query("cursor"))
	var before *time.Time
	if cursorStr != "" {
		t, err := time.Parse(time.RFC3339Nano, cursorStr)
		if err == nil {
			before = &t
		}
	}
	limit := parseLimitOr(c.Query("limit"), 50)

	msgs, err := a.listMessages(c.Request.Context(), conv.ID, limit, before)
	if err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"conversation": conv,
		"messages":     msgs,
	})
}

// PostSupportMessage: POST /api/v1/support/conversation/messages
// (multipart/form-data: body=<text>, files=[<file1>...<file5>])
func (a *App) PostSupportMessage(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	uctx, ok := userFromContext(c)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "unauthorized"})
		return
	}
	if uctx.Role == "admin" {
		c.JSON(http.StatusNotFound, APIError{Error: "support conversation is for students"})
		return
	}
	conv, err := a.getOrCreateStudentConversation(c.Request.Context(), uctx.ID)
	if err != nil {
		internalServerError(c, err)
		return
	}

	// Жёсткий лимит payload, чтобы не упереться позже в http.MaxBytesReader.
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

	msg, autoReopened, err := a.createSupportMessage(c.Request.Context(), conv.ID, uctx.ID, SupportSenderStudent, body, files, c.SaveUploadedFile)
	if err != nil {
		internalServerError(c, err)
		return
	}

	// Publish to admin (assigned) + back to student (for cross-device sync).
	a.publishMessageEvent(c.Request.Context(), conv.ID, msg, autoReopened)

	c.JSON(http.StatusCreated, msg)
}

// MarkSupportRead: POST /api/v1/support/conversation/read
//
// Помечает все входящие (admin/system) сообщения как прочитанные
// и сбрасывает student_unread_count в 0.
func (a *App) MarkSupportRead(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	uctx, ok := userFromContext(c)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "unauthorized"})
		return
	}
	if uctx.Role == "admin" {
		c.JSON(http.StatusNotFound, APIError{Error: "support conversation is for students"})
		return
	}
	conv, err := a.getOrCreateStudentConversation(c.Request.Context(), uctx.ID)
	if err != nil {
		internalServerError(c, err)
		return
	}

	updated, err := a.markIncomingAsRead(c.Request.Context(), conv.ID, SupportSenderStudent)
	if err != nil {
		internalServerError(c, err)
		return
	}

	// Уведомить админа (если есть) — у его сообщений сменились галочки.
	a.publishStatusUpdate(c.Request.Context(), conv.ID, updated)

	c.JSON(http.StatusOK, gin.H{"updatedMessages": len(updated)})
}

// SupportStream: GET /api/v1/support/stream
//
// SSE-stream realtime событий. Для студента — события его собственного
// диалога. Для админа — события всех диалогов.
func (a *App) SupportStream(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	uctx, ok := userFromContext(c)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "unauthorized"})
		return
	}

	w := c.Writer
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache, no-transform")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("X-Accel-Buffering", "no") // nginx должен не буферизовать
	w.WriteHeaderNow()

	flusher, ok := w.(http.Flusher)
	if !ok {
		c.AbortWithStatusJSON(http.StatusInternalServerError, APIError{Error: "streaming unsupported"})
		return
	}

	ch, cancel := a.SupportHub.Subscribe(uctx.ID)
	defer cancel()

	// Сообщаем клиенту, что поток открыт.
	writeSSE(w, flusher, SupportSSEEvent{Type: "hello", Data: gin.H{"userId": uctx.ID, "ts": time.Now().UTC()}, ID: MakeEventID()})

	heartbeat := time.NewTicker(25 * time.Second)
	defer heartbeat.Stop()

	for {
		select {
		case <-c.Request.Context().Done():
			return
		case event, ok := <-ch:
			if !ok {
				return
			}
			writeSSE(w, flusher, event)
		case <-heartbeat.C:
			writeSSE(w, flusher, SupportSSEEvent{Type: "ping", Data: gin.H{"ts": time.Now().UTC()}, ID: MakeEventID()})
		}
	}
}

// GetSupportAttachment: GET /api/v1/support/attachments/:attachmentID
//
// Отдаёт файл, проверив, что текущий пользователь — участник conversation
// (student или admin). Для админа дополнительная проверка роли.
func (a *App) GetSupportAttachment(c *gin.Context) {
	if !a.supportEnsureEnabled(c) {
		return
	}
	uctx, ok := userFromContext(c)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "unauthorized"})
		return
	}
	attID := strings.TrimSpace(c.Param("attachmentID"))
	if _, err := uuid.Parse(attID); err != nil {
		c.AbortWithStatusJSON(http.StatusBadRequest, APIError{Error: "invalid attachment id"})
		return
	}

	var (
		conversationID string
		studentID      string
		storageKey     string
		originalName   string
		mimeType       string
		sizeBytes      int64
	)
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT a.conversation_id, c.student_user_id, a.storage_key,
		       a.original_name, a.mime_type, a.size_bytes
		FROM support_message_attachments a
		JOIN support_conversations c ON c.id = a.conversation_id
		WHERE a.id = $1
	`, attID).Scan(&conversationID, &studentID, &storageKey, &originalName, &mimeType, &sizeBytes); err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			c.AbortWithStatusJSON(http.StatusNotFound, APIError{Error: "attachment not found"})
			return
		}
		internalServerError(c, err)
		return
	}

	// Авторизация: только student-владелец или admin.
	if uctx.Role != "admin" && uctx.ID != studentID {
		c.AbortWithStatusJSON(http.StatusForbidden, APIError{Error: "forbidden"})
		return
	}

	// Защищаемся от любых выскальзываний storage_key за пределы корня.
	fullPath, err := safeStoragePath(a.Cfg.SupportChatStorageDir, storageKey)
	if err != nil {
		internalServerError(c, fmt.Errorf("resolve storage path: %w", err))
		return
	}
	f, err := os.Open(fullPath)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			c.AbortWithStatusJSON(http.StatusNotFound, APIError{Error: "attachment file missing"})
			return
		}
		internalServerError(c, err)
		return
	}
	defer f.Close()

	c.Header("Content-Type", mimeType)
	c.Header("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, sanitizeContentDispositionFilename(originalName)))
	c.Header("X-Content-Type-Options", "nosniff")
	c.Header("Content-Length", fmt.Sprintf("%d", sizeBytes))
	if _, err := io.Copy(c.Writer, f); err != nil {
		// Если клиент отвалился — не паникуем.
		return
	}
}

// ----------------------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------------------

func parseLimitOr(raw string, fallback int) int {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return fallback
	}
	n := 0
	for _, ch := range raw {
		if ch < '0' || ch > '9' {
			return fallback
		}
		n = n*10 + int(ch-'0')
		if n > 1000 {
			return fallback
		}
	}
	if n <= 0 {
		return fallback
	}
	if n > 200 {
		return 200
	}
	return n
}

