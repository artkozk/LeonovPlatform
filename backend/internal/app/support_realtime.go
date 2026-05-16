package app

import (
	"encoding/json"
	"sync"
	"time"
)

// ============================================================================
// Support chat realtime hub (in-memory pub/sub for SSE) — 2026-05-16.
//
// Почему именно так (см. blueprint §6 «Архитектура realtime»):
//
//   1. На старте достаточно SSE: один админ, ограниченное число одновременных
//      учеников. Полноценный WS-брокер был бы overengineering.
//
//   2. Хаб держит подписчиков в памяти процесса. У нас один API процесс
//      (`leonovcare-api` под pm2), поэтому in-memory fan-out безопасен.
//      Если когда-нибудь будет горизонтальная репликация — replace this
//      hub'ом на Redis Pub/Sub без смены публичного API SupportHub.
//
//   3. Подписчики хранят буферизированный chan, чтобы медленный клиент
//      не блокировал отправителя. Если буфер переполнен — событие
//      отбрасывается, а клиент сам перезатягивает состояние через
//      обычные REST endpoints (см. blueprint §6 «Серверные события
//      должны быть idempotent»).
//
//   4. У каждого подписчика есть `userID` (адресат) — так мы аккуратно
//      разделяем bus студента и админский bus. Сообщение всегда
//      адресуется конкретному получателю; admin (assignedAdmin) и student
//      получают одни и те же события независимыми каналами.
// ============================================================================

// SupportSSEEvent — единица realtime потока.
//
// Поля:
//   Type     — короткое имя события: "message_created" / "message_status" /
//              "conversation_updated" / "ping".
//   Data     — произвольный JSON-сериализуемый payload (DTO).
//   ID       — опциональный SSE id (для возможного `Last-Event-ID` в
//              будущем); пока используется только monotonic timestamp.
type SupportSSEEvent struct {
	Type string
	Data any
	ID   string
}

// supportSubscriber — один подключенный SSE-клиент.
type supportSubscriber struct {
	id     int64
	userID string
	ch     chan SupportSSEEvent
}

// SupportHub — фронт реалтайм-доставки.
type SupportHub struct {
	mu          sync.RWMutex
	nextSubID   int64
	subscribers map[int64]*supportSubscriber
}

// NewSupportHub создаёт новый хаб.
func NewSupportHub() *SupportHub {
	return &SupportHub{
		subscribers: make(map[int64]*supportSubscriber),
	}
}

// Subscribe регистрирует слушателя для конкретного userID.
// Возвращает канал для чтения, функцию отписки и id подписки.
// Канал буферизирован, чтобы один медленный клиент не блокировал хаб.
func (h *SupportHub) Subscribe(userID string) (<-chan SupportSSEEvent, func()) {
	h.mu.Lock()
	h.nextSubID++
	sub := &supportSubscriber{
		id:     h.nextSubID,
		userID: userID,
		ch:     make(chan SupportSSEEvent, 32),
	}
	h.subscribers[sub.id] = sub
	h.mu.Unlock()

	cancel := func() {
		h.mu.Lock()
		if existing, ok := h.subscribers[sub.id]; ok {
			delete(h.subscribers, sub.id)
			close(existing.ch)
		}
		h.mu.Unlock()
	}
	return sub.ch, cancel
}

// Publish отправляет событие всем подписчикам, чей userID есть в recipients.
// Если recipients пуст — событие никому не отправляется.
func (h *SupportHub) Publish(event SupportSSEEvent, recipients ...string) {
	if len(recipients) == 0 {
		return
	}
	recipientSet := make(map[string]struct{}, len(recipients))
	for _, r := range recipients {
		if r == "" {
			continue
		}
		recipientSet[r] = struct{}{}
	}
	if len(recipientSet) == 0 {
		return
	}

	h.mu.RLock()
	defer h.mu.RUnlock()

	for _, sub := range h.subscribers {
		if _, ok := recipientSet[sub.userID]; !ok {
			continue
		}
		select {
		case sub.ch <- event:
		default:
			// Канал переполнен. Дропаем событие — клиент re-fetch'ом
			// восстановит состояние при reconnect / при следующем
			// успешном событии.
		}
	}
}

// MakeEventID — детерминированный id события из timestamp + counter.
// Используется как SSE event id (на будущее под Last-Event-ID).
func MakeEventID() string {
	return time.Now().UTC().Format("20060102T150405.000000000Z")
}

// MarshalSSEData — безопасная сериализация payload в JSON для SSE-фрейма.
func MarshalSSEData(v any) []byte {
	b, err := json.Marshal(v)
	if err != nil {
		return []byte("{}")
	}
	return b
}
