// ============================================================================
// Support chat — student page (2026-05-16).
//
// Реализация blueprint:
//   docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md
//
// Поведение страницы (соответствует blueprint §11):
//   1. На mount — получаем один общий conversation и историю.
//   2. Открываем SSE-поток; на каждое event перепроверяем стейт.
//   3. При фокусе/scroll-в-низ помечаем входящие как прочитанные.
//   4. Отправка — multipart (текст + до 5 файлов). Кнопка disabled пока
//      идёт отправка, чтобы избежать дубликатов.
//   5. Галочки показываем только для своих исходящих сообщений
//      (blueprint §11.3.3): sent → одна, delivered → две, read → две акцентные.
//   6. Время — в локальной зоне пользователя (blueprint §11.3.1).
//   7. Long uploads → disabled state у кнопки отправки (blueprint §11.3.4).
//
// Почему не используется глобальный cachedGet:
//   blueprint §11.2 запрещает «долгий» кэш чтения для чатов — он легко
//   маскирует реальные realtime-события.
// ============================================================================

import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  SupportConversation,
  SupportMessage,
  SupportStreamEvent,
  getSupportConversation,
  listSupportMessages,
  markSupportRead,
  openSupportStream,
  postSupportMessage,
} from "../api/support";
import { openAttachment } from "../api/supportAttachments";
import { useAuthStore } from "../store/auth";

const MAX_FILES = 5;

function formatTime(iso?: string): string {
  if (!iso) return "";
  try {
    const date = new Date(iso);
    return date.toLocaleString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit",
    });
  } catch {
    return "";
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function statusTicks(message: SupportMessage, ownUserId: string): string {
  if (message.senderUserId !== ownUserId) return "";
  switch (message.status) {
    case "sent":
      return "✓";
    case "delivered":
      return "✓✓";
    case "read":
      return "✓✓✓"; // акцентируем третьей галочкой; в CSS можно покрасить
    default:
      return "";
  }
}

export function SupportPage() {
  const user = useAuthStore((s) => s.user);
  const userId = user?.id ?? "";

  const [conversation, setConversation] = useState<SupportConversation | null>(null);
  const [messages, setMessages] = useState<SupportMessage[]>([]);
  const [body, setBody] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const scrollerRef = useRef<HTMLDivElement | null>(null);

  const refresh = useCallback(async () => {
    try {
      const res = await listSupportMessages({ limit: 100 });
      setConversation(res.conversation);
      setMessages(res.messages ?? []);
      setError(null);
    } catch (e: any) {
      setError(e?.response?.data?.error ?? "Не удалось загрузить чат поддержки.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load + SSE subscription.
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        await getSupportConversation();
        if (cancelled) return;
        await refresh();
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.response?.data?.error ?? "Не удалось открыть чат поддержки.");
          setLoading(false);
        }
      }
    })();

    const closeStream = openSupportStream((event: SupportStreamEvent) => {
      // Любое событие — повод аккуратно подтянуть свежее состояние.
      // Это idempotent re-fetch (blueprint §6 «idempotent»).
      if (event.type === "ping") return;
      void refresh();
    });

    return () => {
      cancelled = true;
      closeStream();
    };
  }, [refresh]);

  // Mark as read when there are unread incoming messages and the page is visible.
  useEffect(() => {
    if (!conversation) return;
    if ((conversation.studentUnreadCount ?? 0) <= 0) return;
    if (document.hidden) return;
    void markSupportRead();
  }, [conversation]);

  // Auto-scroll to bottom on new messages.
  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages.length]);

  const onFilesChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files ?? []);
    if (selected.length === 0) return;
    setFiles((prev) => {
      const next = [...prev, ...selected].slice(0, MAX_FILES);
      return next;
    });
    e.target.value = "";
  };

  const removeFileAt = (idx: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (sending) return;
    if (!body.trim() && files.length === 0) return;
    if (files.length > MAX_FILES) {
      setError(`Можно отправить не более ${MAX_FILES} файлов за одно сообщение.`);
      return;
    }
    setSending(true);
    try {
      const created = await postSupportMessage(body, files);
      // Optimistic-ish: добавляем созданное сообщение немедленно.
      setMessages((prev) => [...prev, created]);
      setBody("");
      setFiles([]);
      setError(null);
    } catch (e: any) {
      const msg = e?.response?.data?.error ?? "Не удалось отправить сообщение.";
      setError(msg);
    } finally {
      setSending(false);
    }
  };

  const headerLine = useMemo(() => {
    if (!conversation) return "Чат поддержки";
    if (conversation.status === "resolved") {
      return "Чат поддержки · обращение помечено решённым";
    }
    if (conversation.status === "closed") {
      return "Чат поддержки · обращение закрыто";
    }
    return "Чат поддержки";
  }, [conversation]);

  if (loading) {
    return (
      <div className="support-page">
        <div className="support-header"><h2>Чат поддержки</h2></div>
        <div className="support-empty">Загрузка…</div>
      </div>
    );
  }

  return (
    <div className="support-page">
      <header className="support-header">
        <h2>{headerLine}</h2>
        {conversation?.assignedAdminName && (
          <p className="support-subheader">Оператор: {conversation.assignedAdminName}</p>
        )}
        {conversation?.status === "resolved" && conversation.resolutionNote && (
          <p className="support-resolution-note">Комментарий поддержки: {conversation.resolutionNote}</p>
        )}
      </header>

      {error && <div className="support-error" role="alert">{error}</div>}

      <div className="support-messages" ref={scrollerRef}>
        {messages.length === 0 ? (
          <div className="support-empty">Напишите нам — оператор скоро ответит.</div>
        ) : (
          messages.map((m) => (
            <div
              key={m.id}
              className={`support-message support-message-${m.senderRole === "student" ? "outgoing" : "incoming"}`}
            >
              {m.bodyText && <div className="support-message-body">{m.bodyText}</div>}
              {m.attachments && m.attachments.length > 0 && (
                <ul className="support-message-attachments">
                  {m.attachments.map((att) => (
                    <li key={att.id}>
                      {/*
                        Аутентифицированный клик: см. ../api/supportAttachments.ts.
                        Простой <a href> не работает — браузер не пошлёт Bearer.
                      */}
                      <button
                        type="button"
                        className="support-attachment-link"
                        onClick={() => {
                          openAttachment(att).catch((err: unknown) => {
                            setError(err instanceof Error ? err.message : "Не удалось открыть файл.");
                          });
                        }}
                      >
                        {att.originalName}
                      </button>{" "}
                      <span className="support-attachment-size">({formatSize(att.sizeBytes)})</span>
                    </li>
                  ))}
                </ul>
              )}
              <div className="support-message-meta">
                <span>{formatTime(m.createdAt)}</span>
                <span className="support-message-status" aria-label={`Статус: ${m.status}`}>
                  {statusTicks(m, userId)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      <form className="support-composer" onSubmit={onSubmit}>
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Опишите проблему…"
          rows={3}
          aria-label="Текст сообщения"
          onKeyDown={(e) => {
            // Enter — отправить, Shift+Enter — новая строка (blueprint §11.4).
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void onSubmit(e as unknown as FormEvent);
            }
          }}
        />
        <div className="support-composer-row">
          <label className="support-attach-btn">
            📎 Прикрепить
            <input
              type="file"
              multiple
              hidden
              onChange={onFilesChange}
              aria-label="Прикрепить файл"
            />
          </label>
          <div className="support-attach-list">
            {files.map((f, i) => (
              <span key={`${f.name}-${i}`} className="support-attach-chip">
                {f.name} ({formatSize(f.size)})
                <button
                  type="button"
                  className="support-attach-remove"
                  onClick={() => removeFileAt(i)}
                  aria-label={`Убрать ${f.name}`}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <button
            type="submit"
            className="support-send-btn"
            disabled={sending || (!body.trim() && files.length === 0)}
          >
            {sending ? "Отправляем…" : "Отправить"}
          </button>
        </div>
        <p className="support-composer-hint">
          До {MAX_FILES} файлов за сообщение. Enter — отправить, Shift+Enter — новая строка.
        </p>
      </form>
    </div>
  );
}
