package app

import "time"

// ============================================================================
// Support chat DTO + invariants (2026-05-16).
//
// Реализация blueprint:
//   docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md
//
// Зачем отдельный файл:
//   1. Чтобы API-контракт (что отдаём JSON-ом) был в одном месте — это
//      упрощает аудит и поддержание API_SPEC.yaml.
//   2. Чтобы не размывать handlers_support_*.go служебной структурой.
// ============================================================================

const (
	SupportStatusOpen     = "open"
	SupportStatusResolved = "resolved"
	SupportStatusClosed   = "closed"

	SupportSenderStudent = "student"
	SupportSenderAdmin   = "admin"
	SupportSenderSystem  = "system"

	SupportMsgStatusSent      = "sent"
	SupportMsgStatusDelivered = "delivered"
	SupportMsgStatusRead      = "read"

	SupportEventCreated      = "created"
	SupportEventMessageSent  = "message_sent"
	SupportEventAssigned     = "assigned"
	SupportEventReassigned   = "reassigned"
	SupportEventUnassigned   = "unassigned"
	SupportEventResolved     = "resolved"
	SupportEventReopened     = "reopened"
	SupportEventClosed       = "closed"
)

// SupportAttachmentDTO — публичное представление вложения.
type SupportAttachmentDTO struct {
	ID           string    `json:"id"`
	MessageID    string    `json:"messageId"`
	OriginalName string    `json:"originalName"`
	MimeType     string    `json:"mimeType"`
	SizeBytes    int64     `json:"sizeBytes"`
	DownloadURL  string    `json:"downloadUrl"`
	CreatedAt    time.Time `json:"createdAt"`
}

// SupportMessageDTO — публичное представление сообщения.
type SupportMessageDTO struct {
	ID             string                  `json:"id"`
	ConversationID string                  `json:"conversationId"`
	SenderUserID   string                  `json:"senderUserId"`
	SenderRole     string                  `json:"senderRole"`
	BodyText       string                  `json:"bodyText"`
	Status         string                  `json:"status"`
	DeliveredAt    *time.Time              `json:"deliveredAt,omitempty"`
	ReadAt         *time.Time              `json:"readAt,omitempty"`
	HasAttachments bool                    `json:"hasAttachments"`
	Attachments    []SupportAttachmentDTO  `json:"attachments,omitempty"`
	CreatedAt      time.Time               `json:"createdAt"`
}

// SupportConversationDTO — публичное представление диалога.
type SupportConversationDTO struct {
	ID                     string     `json:"id"`
	StudentUserID          string     `json:"studentUserId"`
	StudentDisplayName     string     `json:"studentDisplayName,omitempty"`
	StudentEmail           string     `json:"studentEmail,omitempty"`
	Status                 string     `json:"status"`
	AssignedAdminUserID    string     `json:"assignedAdminUserId,omitempty"`
	AssignedAdminName      string     `json:"assignedAdminName,omitempty"`
	ResolutionNote         string     `json:"resolutionNote,omitempty"`
	ResolvedAt             *time.Time `json:"resolvedAt,omitempty"`
	ClosedAt               *time.Time `json:"closedAt,omitempty"`
	LastMessageAt          *time.Time `json:"lastMessageAt,omitempty"`
	LastMessagePreview     string     `json:"lastMessagePreview,omitempty"`
	LastMessageSenderRole  string     `json:"lastMessageSenderRole,omitempty"`
	StudentUnreadCount     int        `json:"studentUnreadCount"`
	AdminUnreadCount       int        `json:"adminUnreadCount"`
	CreatedAt              time.Time  `json:"createdAt"`
	UpdatedAt              time.Time  `json:"updatedAt"`
}

// SupportEventDTO — публичное представление события диалога.
type SupportEventDTO struct {
	ID             string                 `json:"id"`
	ConversationID string                 `json:"conversationId"`
	EventType      string                 `json:"eventType"`
	ActorUserID    string                 `json:"actorUserId,omitempty"`
	ActorName      string                 `json:"actorName,omitempty"`
	Payload        map[string]any         `json:"payload,omitempty"`
	CreatedAt      time.Time              `json:"createdAt"`
}
