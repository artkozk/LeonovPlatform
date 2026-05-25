package app

import (
	"testing"
	"time"
)

// ============================================================================
// Support hub — unit tests for v2 (Redis-backed) in local-only mode.
//
// Тесты гоняем с `nil` Redis-клиентом — это путь, по которому Publish
// падает на чистый локальный fan-out. Этим достаточно покрыто:
//   - корректная адресация по recipients (только нужные подписчики получают);
//   - drop-on-full буфера не блокирует Publish;
//   - cancel-функция действительно убирает подписчика.
//
// Полноценный multi-process тест с реальным Redis выходит за рамки
// юнит-тестов; он покрывается прод smoke-сценарием в
// docs/operations/MULTI_INSTANCE_API_2026_05_16.md.
// ============================================================================

func TestSupportHubLocalDelivery(t *testing.T) {
	h := NewSupportHub(nil, nil)
	defer h.Close()

	ch, cancel := h.Subscribe("user-A")
	defer cancel()

	h.Publish(SupportSSEEvent{Type: "message_created", Data: "hello", ID: "1"}, "user-A")

	select {
	case ev := <-ch:
		if ev.Type != "message_created" || ev.ID != "1" {
			t.Errorf("unexpected event: %+v", ev)
		}
	case <-time.After(time.Second):
		t.Fatal("did not receive event within 1s")
	}
}

func TestSupportHubNotDeliveredToOtherUser(t *testing.T) {
	h := NewSupportHub(nil, nil)
	defer h.Close()

	chA, cancelA := h.Subscribe("user-A")
	defer cancelA()
	chB, cancelB := h.Subscribe("user-B")
	defer cancelB()

	h.Publish(SupportSSEEvent{Type: "x", Data: 1}, "user-A")

	select {
	case <-chA:
	case <-time.After(time.Second):
		t.Fatal("A should have received event")
	}
	// B must not receive anything in a reasonable window.
	select {
	case ev := <-chB:
		t.Fatalf("B should not have received event, got %+v", ev)
	case <-time.After(150 * time.Millisecond):
	}
}

func TestSupportHubCancelRemovesSubscriber(t *testing.T) {
	h := NewSupportHub(nil, nil)
	defer h.Close()

	ch, cancel := h.Subscribe("user-A")
	cancel()

	// After cancel, channel is closed.
	select {
	case _, ok := <-ch:
		if ok {
			t.Fatal("channel should be closed after cancel")
		}
	case <-time.After(time.Second):
		t.Fatal("channel did not close in time")
	}

	// Publish should be a no-op (no subscribers); must not panic.
	h.Publish(SupportSSEEvent{Type: "x"}, "user-A")
}

func TestSupportHubDropsOnFullBuffer(t *testing.T) {
	h := NewSupportHub(nil, nil)
	defer h.Close()

	_, cancel := h.Subscribe("slow-user")
	defer cancel()

	// Channel buffer is 32. Publish 100 events; we must not deadlock.
	done := make(chan struct{})
	go func() {
		defer close(done)
		for i := 0; i < 100; i++ {
			h.Publish(SupportSSEEvent{Type: "x", Data: i}, "slow-user")
		}
	}()
	select {
	case <-done:
	case <-time.After(2 * time.Second):
		t.Fatal("Publish path blocked on full buffer (regression)")
	}
}

func TestSupportHubIgnoresEmptyRecipients(t *testing.T) {
	h := NewSupportHub(nil, nil)
	defer h.Close()

	ch, cancel := h.Subscribe("user-A")
	defer cancel()

	// Empty recipients list — must not deliver anywhere.
	h.Publish(SupportSSEEvent{Type: "x"})
	// Just empty strings — must not deliver.
	h.Publish(SupportSSEEvent{Type: "x"}, "", "")

	select {
	case ev := <-ch:
		t.Fatalf("should not have received: %+v", ev)
	case <-time.After(150 * time.Millisecond):
	}
}
