package app

import (
	"context"
	"encoding/json"
	"log/slog"
	"sync"
	"sync/atomic"
	"time"

	"github.com/redis/go-redis/v9"
)

// ============================================================================
// Support chat realtime hub — Redis Pub/Sub backed fan-out for SSE.
//
// История (append-only):
//   v1 (2026-05-16, blueprint §6): in-memory only fan-out, рассчитан на
//     один API-процесс. См. изначальный коммит 30bb920.
//
//   v2 (2026-05-16, этот файл, см. docs/operations/MULTI_INSTANCE_API_2026_05_16.md):
//     добавлен Redis Pub/Sub. Причина: подготовка к multi-instance API
//     (2+ pm2-инстанса за nginx upstream). Без Redis SSE-подписчики на
//     процессе A не получают события, опубликованные процессом B —
//     админ отвечает на одном бекенде, студент висит на другом.
//
// Дизайн v2:
//
//   1. Публичный API не изменился: `Subscribe(userID) -> (<-chan, cancel)`,
//      `Publish(event, recipients...)`. Handlers и тесты тронуты не были.
//
//   2. Каждый API-процесс хранит свои `subscribers map[int64]*supportSubscriber`
//      (это локальный набор открытых SSE-соединений именно этого процесса).
//
//   3. `Publish(...)` пишет событие в Redis-канал "support:events".
//      Каждый процесс (включая опубликовавшего) подписан на этот канал
//      через `runRedisSubscriber()` и при получении сообщения
//      доставляет его своим локальным подписчикам, чьи userID совпали
//      с recipients.
//
//   4. Если Redis недоступен (например, в unit-тестах хаб создаётся с
//      `nil` клиентом, или Redis временно лёг), `Publish` падает на
//      локальный fan-out — это гарантирует, что хотя бы свои-же
//      подписчики на этом же процессе получат событие.
//
//   5. Бэкофф подключения к Redis (500ms → 10s, cap) и непрерывное
//      переподключение — слежение за этим в `runRedisSubscriber`.
//
//   6. Сохранён принцип blueprint §6 «события идемпотентны»:
//      на reconnect-стороне клиент перетягивает состояние через REST,
//      на серверной стороне у нас тоже есть допуск к потере событий
//      (дроп при полном буфере, дроп при Redis сбое).
// ============================================================================

const supportRedisChannel = "support:events"

// SupportSSEEvent — единица realtime потока.
type SupportSSEEvent struct {
	Type string `json:"type"`
	Data any    `json:"data"`
	ID   string `json:"id,omitempty"`
}

// supportSubscriber — один подключенный SSE-клиент (локально на процессе).
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

	// Redis client. Может быть nil — тогда хаб работает только локально
	// (полезно в тестах и как fallback при сбое Redis).
	redis *redis.Client
	log   *slog.Logger

	// Управление background-сабом.
	stopCh   chan struct{}
	stopOnce sync.Once

	// Опциональные метрики (атомики, чтобы было что вывести в /readyz/debug).
	publishedTotal atomic.Uint64
	deliveredTotal atomic.Uint64
	droppedTotal   atomic.Uint64
	redisErrors    atomic.Uint64
}

// supportRedisEnvelope — то, что мы кладём в Redis (или в локальный
// fan-out при отсутствии Redis).
type supportRedisEnvelope struct {
	Recipients []string        `json:"recipients"`
	Event      SupportSSEEvent `json:"event"`
}

// NewSupportHub создаёт хаб. `client == nil` означает «без Redis,
// только локальный fan-out» (тесты + degraded mode).
func NewSupportHub(client *redis.Client, log *slog.Logger) *SupportHub {
	h := &SupportHub{
		subscribers: make(map[int64]*supportSubscriber),
		redis:       client,
		log:         log,
		stopCh:      make(chan struct{}),
	}
	if client != nil {
		go h.runRedisSubscriber()
	}
	return h
}

// Close корректно останавливает Redis subscriber. Безопасно вызывать
// несколько раз.
func (h *SupportHub) Close() {
	h.stopOnce.Do(func() { close(h.stopCh) })
}

// Subscribe регистрирует локального слушателя для userID.
// Возвращает канал и cancel-функцию (deregister + close).
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

// Publish публикует событие. На multi-process: отправка идёт через Redis
// и приходит обратно к нам через subscribe-loop. Если Redis отсутствует
// или сломан — fan-out выполняется локально (хотя бы свои подписчики
// получат).
func (h *SupportHub) Publish(event SupportSSEEvent, recipients ...string) {
	if len(recipients) == 0 {
		return
	}
	h.publishedTotal.Add(1)

	if h.redis == nil {
		// Нет Redis вообще — локальный режим (тесты).
		h.localFanout(event, recipients)
		return
	}

	envelope := supportRedisEnvelope{Recipients: recipients, Event: event}
	payload, err := json.Marshal(envelope)
	if err != nil {
		// Никогда не должно произойти — fallback на локал.
		h.redisErrors.Add(1)
		h.localFanout(event, recipients)
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	if err := h.redis.Publish(ctx, supportRedisChannel, payload).Err(); err != nil {
		if h.log != nil {
			h.log.Error("support pubsub publish", "err", err.Error())
		}
		h.redisErrors.Add(1)
		// Хотя бы свои подписчики получат событие — это лучше, чем
		// тишина для админа на том же процессе.
		h.localFanout(event, recipients)
	}
}

// localFanout — общая логика доставки на текущий процесс.
// Используется из локального Publish (нет Redis) и из Redis subscribe-loop.
func (h *SupportHub) localFanout(event SupportSSEEvent, recipients []string) {
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
			h.deliveredTotal.Add(1)
		default:
			// Канал переполнен — дропаем (см. шапку файла).
			h.droppedTotal.Add(1)
		}
	}
}

// runRedisSubscriber — long-lived goroutine. Подписывается на
// `support:events` и доставляет каждое полученное сообщение в
// локальный fan-out. При обрыве канала переподключается с
// экспоненциальным backoff'ом (cap 10s).
func (h *SupportHub) runRedisSubscriber() {
	backoff := 500 * time.Millisecond
	for {
		select {
		case <-h.stopCh:
			return
		default:
		}

		ctx, cancel := context.WithCancel(context.Background())
		sub := h.redis.Subscribe(ctx, supportRedisChannel)
		// Ждём подтверждения подписки, иначе при сбое мы тихо ловим nil-канал.
		if _, err := sub.Receive(ctx); err != nil {
			cancel()
			_ = sub.Close()
			h.redisErrors.Add(1)
			if h.log != nil {
				h.log.Warn("support pubsub subscribe failed; retrying", "err", err.Error(), "backoff", backoff.String())
			}
			if h.sleepOrStop(backoff) {
				return
			}
			backoff = nextBackoff(backoff)
			continue
		}
		backoff = 500 * time.Millisecond

		ch := sub.Channel()
		// Цикл пока канал жив или нас не остановили.
	inner:
		for {
			select {
			case <-h.stopCh:
				cancel()
				_ = sub.Close()
				return
			case msg, ok := <-ch:
				if !ok {
					// Канал закрыт — выйти из inner и переподключиться.
					break inner
				}
				var env supportRedisEnvelope
				if err := json.Unmarshal([]byte(msg.Payload), &env); err != nil {
					if h.log != nil {
						h.log.Warn("support pubsub: skip malformed envelope", "err", err.Error())
					}
					continue
				}
				h.localFanout(env.Event, env.Recipients)
			}
		}
		cancel()
		_ = sub.Close()
		// Reconnect.
		if h.sleepOrStop(backoff) {
			return
		}
		backoff = nextBackoff(backoff)
	}
}

func (h *SupportHub) sleepOrStop(d time.Duration) bool {
	select {
	case <-h.stopCh:
		return true
	case <-time.After(d):
		return false
	}
}

func nextBackoff(d time.Duration) time.Duration {
	d *= 2
	if d > 10*time.Second {
		d = 10 * time.Second
	}
	return d
}

// MakeEventID — детерминированный id события из timestamp.
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
