package app

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
	"unicode"

	"github.com/gin-gonic/gin"
)

// ============================================================================
// Support chat — sending messages and attachment storage (2026-05-16).
//
// Этот файл — единственное место, где пишутся support_messages и
// support_message_attachments. Это позволяет:
//   1. Гарантировать симметричное поведение между student/admin handlers
//      (один и тот же путь записи, только sender_role меняется).
//   2. Содержать всю логику безопасности файлов в одном месте:
//      санитизация имени, проверка размера/количества, генерация
//      storage_key вне web-root.
//   3. Гарантировать запись события `message_sent` в audit trail
//      одновременно с insert'ом сообщения.
//   4. Обрабатывать auto-reopen (resolved → open при сообщении ученика,
//      см. blueprint §4.2 п.2).
// ============================================================================

// supportFileSaver — функция, способная сохранить uploaded file по
// пути назначения. В production это `gin.Context.SaveUploadedFile`.
// Параметризуем — это упрощает тесты (можно подсунуть фейк).
type supportFileSaver func(file *multipart.FileHeader, dst string) error

// createSupportMessage — единая точка записи. Возвращает DTO нового сообщения
// и признак auto-reopen.
//
// Алгоритм:
//   1. Готовим conversation state (auto-reopen, если status != 'open' и
//      sender_role == 'student').
//   2. INSERT message.
//   3. Для каждого attachment: записать файл в безопасное место →
//      INSERT support_message_attachments.
//   4. UPDATE conversation: last_message_at, preview, unread counters.
//   5. INSERT audit-событие.
//
// Транзакция: всё в одной транзакции. Если запись файла на диск удалась,
// а INSERT упал — файлы остаются orphan'ами, их можно собирать отдельным
// retention-cron'ом (blueprint §9 «retention-политика»).
func (a *App) createSupportMessage(
	ctx context.Context,
	conversationID string,
	senderUserID string,
	senderRole string,
	bodyText string,
	files []*multipart.FileHeader,
	saver supportFileSaver,
) (SupportMessageDTO, bool, error) {
	bodyText = strings.TrimSpace(bodyText)
	hasAttachments := len(files) > 0
	if bodyText == "" && !hasAttachments {
		return SupportMessageDTO{}, false, fmt.Errorf("empty message")
	}

	tx, err := a.DB.Begin(ctx)
	if err != nil {
		return SupportMessageDTO{}, false, fmt.Errorf("begin tx: %w", err)
	}
	defer tx.Rollback(ctx)

	// 1. Загружаем текущий статус и определяем auto-reopen.
	var (
		currentStatus string
		assignedAdmin string
	)
	if err := tx.QueryRow(ctx, `
		SELECT status, COALESCE(assigned_admin_user_id::text, '')
		FROM support_conversations WHERE id = $1 FOR UPDATE
	`, conversationID).Scan(&currentStatus, &assignedAdmin); err != nil {
		return SupportMessageDTO{}, false, fmt.Errorf("lock conversation: %w", err)
	}

	autoReopened := false
	if senderRole == SupportSenderStudent && currentStatus != SupportStatusOpen {
		// blueprint §4.2 п.2: student-сообщение → resolved/closed → open.
		if _, err := tx.Exec(ctx, `
			UPDATE support_conversations
			SET status = 'open',
			    resolved_at = NULL,
			    resolved_by_user_id = NULL,
			    resolution_note = NULL,
			    closed_at = NULL,
			    closed_by_user_id = NULL,
			    updated_at = NOW()
			WHERE id = $1
		`, conversationID); err != nil {
			return SupportMessageDTO{}, false, fmt.Errorf("auto-reopen: %w", err)
		}
		autoReopened = true
	}

	// 2. INSERT message.
	now := time.Now().UTC()
	var msgID string
	if err := tx.QueryRow(ctx, `
		INSERT INTO support_messages (
			conversation_id, sender_user_id, sender_role,
			body_text, status, has_attachments,
			created_at, updated_at
		)
		VALUES ($1, $2, $3, NULLIF($4, ''), 'sent', $5, $6, $6)
		RETURNING id
	`, conversationID, senderUserID, senderRole, bodyText, hasAttachments, now).Scan(&msgID); err != nil {
		return SupportMessageDTO{}, false, fmt.Errorf("insert message: %w", err)
	}

	// 3. Attachments.
	var savedFiles []string
	for _, fh := range files {
		storageKey, fullPath, err := a.allocateAttachmentPath(conversationID, msgID, fh.Filename)
		if err != nil {
			return SupportMessageDTO{}, false, err
		}
		if err := saver(fh, fullPath); err != nil {
			cleanupTempFiles(savedFiles)
			return SupportMessageDTO{}, false, fmt.Errorf("save uploaded file: %w", err)
		}
		savedFiles = append(savedFiles, fullPath)

		mimeType := strings.TrimSpace(fh.Header.Get("Content-Type"))
		if mimeType == "" {
			mimeType = "application/octet-stream"
		}
		if _, err := tx.Exec(ctx, `
			INSERT INTO support_message_attachments (
				message_id, conversation_id, storage_key,
				original_name, mime_type, size_bytes
			)
			VALUES ($1, $2, $3, $4, $5, $6)
		`, msgID, conversationID, storageKey, sanitizeFilename(fh.Filename), mimeType, fh.Size); err != nil {
			cleanupTempFiles(savedFiles)
			return SupportMessageDTO{}, false, fmt.Errorf("insert attachment: %w", err)
		}
	}

	// 4. Update conversation aggregates. Unread counter увеличивается только
	//    у получателя.
	previewText := supportPreviewFromBody(bodyText, hasAttachments)
	studentUnreadInc := 0
	adminUnreadInc := 0
	if senderRole == SupportSenderStudent {
		adminUnreadInc = 1
	} else if senderRole == SupportSenderAdmin {
		studentUnreadInc = 1
	}
	if _, err := tx.Exec(ctx, `
		UPDATE support_conversations
		SET last_message_at         = $2,
		    last_message_preview    = $3,
		    last_message_sender_role= $4,
		    student_unread_count    = student_unread_count + $5,
		    admin_unread_count      = admin_unread_count + $6,
		    updated_at              = NOW()
		WHERE id = $1
	`, conversationID, now, previewText, senderRole, studentUnreadInc, adminUnreadInc); err != nil {
		cleanupTempFiles(savedFiles)
		return SupportMessageDTO{}, false, fmt.Errorf("update conversation aggregates: %w", err)
	}

	// 5. Audit-событие message_sent.
	eventPayload := map[string]any{
		"messageId":      msgID,
		"hasAttachments": hasAttachments,
		"autoReopened":   autoReopened,
	}
	pj := jsonMarshal(eventPayload)
	if _, err := tx.Exec(ctx, `
		INSERT INTO support_conversation_events (conversation_id, event_type, actor_user_id, payload)
		VALUES ($1, 'message_sent', $2, $3::jsonb)
	`, conversationID, senderUserID, pj); err != nil {
		cleanupTempFiles(savedFiles)
		return SupportMessageDTO{}, false, fmt.Errorf("insert message_sent event: %w", err)
	}

	if autoReopened {
		if _, err := tx.Exec(ctx, `
			INSERT INTO support_conversation_events (conversation_id, event_type, actor_user_id, payload)
			VALUES ($1, 'reopened', $2, $3::jsonb)
		`, conversationID, senderUserID, jsonMarshal(map[string]any{"reason": "student_message", "previousStatus": currentStatus})); err != nil {
			cleanupTempFiles(savedFiles)
			return SupportMessageDTO{}, false, fmt.Errorf("insert reopened event: %w", err)
		}
	}

	if err := tx.Commit(ctx); err != nil {
		cleanupTempFiles(savedFiles)
		return SupportMessageDTO{}, false, fmt.Errorf("commit: %w", err)
	}

	msg, err := a.loadMessage(ctx, msgID)
	if err != nil {
		return SupportMessageDTO{}, false, err
	}
	return msg, autoReopened, nil
}

// markIncomingAsRead помечает все непрочитанные сообщения от ОТПРАВИТЕЛЕЙ
// НЕ-readerRole как 'read'. Возвращает обновлённые сообщения для
// realtime-уведомления.
func (a *App) markIncomingAsRead(ctx context.Context, conversationID string, readerRole string) ([]SupportMessageDTO, error) {
	// readerRole — кто читает. Помечаем как read то, что прислал «другой»:
	//   student читает admin/system; admin читает student.
	exclude := SupportSenderAdmin
	resetCol := "student_unread_count"
	if readerRole == SupportSenderAdmin {
		exclude = SupportSenderStudent
		resetCol = "admin_unread_count"
	}

	rows, err := a.DB.Query(ctx, `
		UPDATE support_messages
		SET status = 'read',
		    delivered_at = COALESCE(delivered_at, NOW()),
		    read_at = NOW(),
		    updated_at = NOW()
		WHERE conversation_id = $1
		  AND sender_role <> $2
		  AND status <> 'read'
		RETURNING id
	`, conversationID, exclude)
	if err != nil {
		return nil, fmt.Errorf("mark read: %w", err)
	}
	defer rows.Close()
	var updatedIDs []string
	for rows.Next() {
		var id string
		if err := rows.Scan(&id); err != nil {
			return nil, fmt.Errorf("scan updated message id: %w", err)
		}
		updatedIDs = append(updatedIDs, id)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate updated message ids: %w", err)
	}

	if _, err := a.DB.Exec(ctx, fmt.Sprintf(`
		UPDATE support_conversations SET %s = 0, updated_at = NOW() WHERE id = $1
	`, resetCol), conversationID); err != nil {
		return nil, fmt.Errorf("reset unread counter: %w", err)
	}

	if len(updatedIDs) == 0 {
		return nil, nil
	}
	return a.loadMessagesByIDs(ctx, updatedIDs)
}

// loadMessagesByIDs — выгружает несколько сообщений (для realtime
// status update). Не подгружает вложения — для status broadcast
// они не нужны.
func (a *App) loadMessagesByIDs(ctx context.Context, ids []string) ([]SupportMessageDTO, error) {
	rows, err := a.DB.Query(ctx, `
		SELECT id, conversation_id, sender_user_id, sender_role,
		       COALESCE(body_text, ''), status, delivered_at, read_at,
		       has_attachments, created_at
		FROM support_messages
		WHERE id = ANY($1)
	`, ids)
	if err != nil {
		return nil, fmt.Errorf("load messages by ids: %w", err)
	}
	defer rows.Close()
	var out []SupportMessageDTO
	for rows.Next() {
		var m SupportMessageDTO
		if err := rows.Scan(
			&m.ID, &m.ConversationID, &m.SenderUserID, &m.SenderRole,
			&m.BodyText, &m.Status, &m.DeliveredAt, &m.ReadAt,
			&m.HasAttachments, &m.CreatedAt,
		); err != nil {
			return nil, err
		}
		out = append(out, m)
	}
	return out, rows.Err()
}

// markDeliveredOnReceive помечает сообщения как delivered у получателя,
// когда тот получает их через SSE. Это soft-update: если read_at уже
// проставлен — не трогаем.
func (a *App) markDeliveredOnReceive(ctx context.Context, conversationID string, receiverRole string) ([]string, error) {
	exclude := SupportSenderAdmin
	if receiverRole == SupportSenderAdmin {
		exclude = SupportSenderStudent
	}
	rows, err := a.DB.Query(ctx, `
		UPDATE support_messages
		SET status = 'delivered',
		    delivered_at = NOW(),
		    updated_at = NOW()
		WHERE conversation_id = $1
		  AND sender_role <> $2
		  AND status = 'sent'
		RETURNING id
	`, conversationID, exclude)
	if err != nil {
		return nil, fmt.Errorf("mark delivered: %w", err)
	}
	defer rows.Close()
	var ids []string
	for rows.Next() {
		var id string
		if err := rows.Scan(&id); err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}
	return ids, rows.Err()
}

// ----------------------------------------------------------------------------
// Attachment storage layout & safety
// ----------------------------------------------------------------------------

// allocateAttachmentPath — выдаёт пару (storage_key, fullPath) для записи.
//
// Layout: <root>/conv/<convID>/msg/<msgID>/<random>-<safeName>
// - root: вне frontend/dist (blueprint §9 «Хранилище файлов вне web-root»);
// - имя файла санитизируется;
// - prefix-random гарантирует уникальность даже при одинаковом filename
//   в нескольких сообщениях.
func (a *App) allocateAttachmentPath(conversationID, messageID, originalName string) (storageKey, fullPath string, err error) {
	root := a.Cfg.SupportChatStorageDir
	dir := filepath.Join(root, "conv", conversationID, "msg", messageID)
	if err := os.MkdirAll(dir, 0o750); err != nil {
		return "", "", fmt.Errorf("mkdir storage: %w", err)
	}
	randHex := make([]byte, 6)
	if _, err := rand.Read(randHex); err != nil {
		return "", "", fmt.Errorf("random: %w", err)
	}
	safe := sanitizeFilename(originalName)
	fname := fmt.Sprintf("%s-%s", hex.EncodeToString(randHex), safe)
	full := filepath.Join(dir, fname)
	// storage_key храним относительно root, для безопасности и переноса.
	rel, err := filepath.Rel(root, full)
	if err != nil {
		return "", "", fmt.Errorf("rel storage: %w", err)
	}
	return filepath.ToSlash(rel), full, nil
}

func cleanupTempFiles(paths []string) {
	for _, p := range paths {
		_ = os.Remove(p)
	}
}

// sanitizeFilename — убирает path traversal, контрольные символы и
// длинные имена. Не пытается транслировать unicode в ASCII; разрешает
// кириллицу. Запасное имя если всё вычистили — "file".
//
// Замечание о Windows-style разделителях:
//   filepath.Base считает path separator только нативный для текущей ОС:
//   `\` на Windows и `/` на Linux. Браузер же может прислать имя
//   `..\..\..\etc\passwd` независимо от того, на чём бежит сервер.
//   Чтобы стабильно вырубать backslash-path traversal на любой ОС,
//   нормализуем `\` → `/` ДО вызова filepath.Base.
func sanitizeFilename(name string) string {
	normalized := strings.ReplaceAll(name, "\\", "/")
	base := filepath.Base(normalized) // отбрасывает любой path-prefix
	base = strings.TrimSpace(base)
	if base == "" || base == "." || base == ".." {
		return "file"
	}
	var b strings.Builder
	for _, r := range base {
		switch {
		case r == 0:
			continue
		case unicode.IsControl(r):
			continue
		case r == '/' || r == '\\':
			continue
		case r == ':' || r == '*' || r == '?' || r == '"' || r == '<' || r == '>' || r == '|':
			b.WriteRune('_')
		default:
			b.WriteRune(r)
		}
	}
	out := b.String()
	if out == "" {
		out = "file"
	}
	// Ограничим длину, чтобы файловые системы не падали.
	if len([]rune(out)) > 180 {
		r := []rune(out)
		out = string(r[:180])
	}
	return out
}

// sanitizeContentDispositionFilename — для заголовка Content-Disposition.
// Убирает кавычки и control-символы.
func sanitizeContentDispositionFilename(name string) string {
	name = sanitizeFilename(name)
	name = strings.ReplaceAll(name, `"`, `_`)
	return name
}

// safeStoragePath — резолвит storage_key относительно SupportChatStorageDir
// и проверяет, что результирующий путь не выскальзывает за пределы корня.
func safeStoragePath(root, storageKey string) (string, error) {
	if root == "" {
		return "", fmt.Errorf("empty storage root")
	}
	if strings.Contains(storageKey, "..") {
		return "", fmt.Errorf("invalid storage key")
	}
	absRoot, err := filepath.Abs(root)
	if err != nil {
		return "", err
	}
	full := filepath.Join(absRoot, filepath.FromSlash(storageKey))
	fullClean := filepath.Clean(full)
	if !strings.HasPrefix(fullClean, absRoot+string(filepath.Separator)) && fullClean != absRoot {
		return "", fmt.Errorf("storage key escapes root")
	}
	return fullClean, nil
}

// ----------------------------------------------------------------------------
// SSE writers
// ----------------------------------------------------------------------------

func writeSSE(w http.ResponseWriter, flusher http.Flusher, event SupportSSEEvent) {
	// id (optional) + event + data\n\n
	if event.ID != "" {
		fmt.Fprintf(w, "id: %s\n", event.ID)
	}
	if event.Type != "" {
		fmt.Fprintf(w, "event: %s\n", event.Type)
	}
	fmt.Fprintf(w, "data: %s\n\n", MarshalSSEData(event.Data))
	flusher.Flush()
}

// ----------------------------------------------------------------------------
// Realtime publishing
// ----------------------------------------------------------------------------

// publishMessageEvent — рассылает событие 'message_created' всем
// заинтересованным.
//
// Получатели:
//   - student (всегда, для синка между девайсами и для своих галочек);
//   - assigned admin (если есть);
//   - все админы (broadcast по userID невозможен — admin-stream получают
//     только подключенные админы; см. SupportStream).
//
// Так как сейчас один админ, упрощение: помимо assigned, рассылаем
// admin-bus просто всем подписчикам с role=admin через отдельный
// generic broadcast — для этого хаб смотрит userID. Решено в роутере:
// admin SSE подключается под своим userID, и сюда мы публикуем по
// списку всех known admin userID'ов.
func (a *App) publishMessageEvent(ctx context.Context, conversationID string, msg SupportMessageDTO, autoReopened bool) {
	studentID, adminIDs, err := a.lookupConversationParticipants(ctx, conversationID)
	if err != nil {
		a.Log.Error("support publish message: lookup participants", "err", err.Error())
		return
	}

	payload := gin.H{
		"message":       msg,
		"autoReopened":  autoReopened,
	}
	event := SupportSSEEvent{Type: "message_created", Data: payload, ID: MakeEventID()}

	recipients := append([]string{studentID}, adminIDs...)
	a.SupportHub.Publish(event, recipients...)
}

// publishStatusUpdate — рассылает обновлённые статусы сообщений (delivered/read).
func (a *App) publishStatusUpdate(ctx context.Context, conversationID string, updated []SupportMessageDTO) {
	if len(updated) == 0 {
		return
	}
	studentID, adminIDs, err := a.lookupConversationParticipants(ctx, conversationID)
	if err != nil {
		a.Log.Error("support publish status: lookup participants", "err", err.Error())
		return
	}
	event := SupportSSEEvent{Type: "message_status", Data: gin.H{"messages": updated, "conversationId": conversationID}, ID: MakeEventID()}
	recipients := append([]string{studentID}, adminIDs...)
	a.SupportHub.Publish(event, recipients...)
}

// publishConversationUpdate — для смены статуса/оператора.
func (a *App) publishConversationUpdate(ctx context.Context, conversationID string) {
	conv, err := a.loadConversationByID(ctx, conversationID)
	if err != nil {
		return
	}
	studentID, adminIDs, err := a.lookupConversationParticipants(ctx, conversationID)
	if err != nil {
		a.Log.Error("support publish conv: lookup participants", "err", err.Error())
		return
	}
	event := SupportSSEEvent{Type: "conversation_updated", Data: gin.H{"conversation": conv}, ID: MakeEventID()}
	recipients := append([]string{studentID}, adminIDs...)
	a.SupportHub.Publish(event, recipients...)
}

// lookupConversationParticipants — возвращает (studentID, []adminID-всех-админов).
// В первую версию все админы получают realtime по всем чатам — это
// соответствует Telegram-like админскому UX в blueprint §2.3 («список
// чатов как в ТГ»).
func (a *App) lookupConversationParticipants(ctx context.Context, conversationID string) (string, []string, error) {
	var studentID string
	if err := a.DB.QueryRow(ctx, `
		SELECT student_user_id::text FROM support_conversations WHERE id = $1
	`, conversationID).Scan(&studentID); err != nil {
		return "", nil, err
	}
	rows, err := a.DB.Query(ctx, `
		SELECT id::text FROM users WHERE role = 'admin' AND is_blocked = FALSE
	`)
	if err != nil {
		return studentID, nil, err
	}
	defer rows.Close()
	var adminIDs []string
	for rows.Next() {
		var id string
		if err := rows.Scan(&id); err != nil {
			return studentID, nil, err
		}
		adminIDs = append(adminIDs, id)
	}
	return studentID, adminIDs, rows.Err()
}
