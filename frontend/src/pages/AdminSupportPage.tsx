// ============================================================================
// Support chat — admin page (2026-05-16).
//
// Реализация blueprint §2.3 (Telegram-like) и §8.2 (admin API):
//   - левая колонка: список диалогов с превью + временем + unread.
//   - правая колонка: окно переписки выбранного диалога.
//   - кнопки операций над диалогом (assign-self, resolve, reopen, close).
//
// Realtime — общий SSE-поток, события conversation_updated / message_created /
// message_status триггерят целевые refetch'и без ломки UX.
// ============================================================================

import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  SupportConversation,
  SupportMessage,
  SupportStreamEvent,
  adminGetSupportConversation,
  adminListSupportConversations,
  adminListSupportMessages,
  adminMarkSupportRead,
  adminPatchSupportConversation,
  adminPostSupportMessage,
  openSupportStream,
} from "../api/support";
import { useAuthStore } from "../store/auth";

const MAX_FILES = 5;

function formatTime(iso?: string): string {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString(undefined, {
      hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit",
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

export function AdminSupportPage() {
  const user = useAuthStore((s) => s.user);
  const adminUserId = user?.id ?? "";

  const [conversations, setConversations] = useState<SupportConversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [activeConv, setActiveConv] = useState<SupportConversation | null>(null);
  const [messages, setMessages] = useState<SupportMessage[]>([]);
  const [body, setBody] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [sending, setSending] = useState(false);
  const [actionBusy, setActionBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resolveNote, setResolveNote] = useState("");

  const scrollerRef = useRef<HTMLDivElement | null>(null);

  const refreshList = useCallback(async () => {
    try {
      const res = await adminListSupportConversations({ limit: 200 });
      setConversations(res.items ?? []);
    } catch (e: any) {
      setError(e?.response?.data?.error ?? "Не удалось загрузить список обращений.");
    }
  }, []);

  const refreshActive = useCallback(async (convId: string) => {
    try {
      const [conv, msgs] = await Promise.all([
        adminGetSupportConversation(convId),
        adminListSupportMessages(convId, { limit: 200 }),
      ]);
      setActiveConv(conv);
      setMessages(msgs.messages ?? []);
    } catch (e: any) {
      setError(e?.response?.data?.error ?? "Не удалось загрузить диалог.");
    }
  }, []);

  useEffect(() => {
    void refreshList();
    const closeStream = openSupportStream((event: SupportStreamEvent) => {
      if (event.type === "ping") return;
      void refreshList();
      if (selectedId && (event.type === "message_created" || event.type === "message_status" || event.type === "conversation_updated")) {
        void refreshActive(selectedId);
      }
    });
    return () => closeStream();
  }, [refreshList, refreshActive, selectedId]);

  useEffect(() => {
    if (!selectedId) {
      setActiveConv(null);
      setMessages([]);
      return;
    }
    void refreshActive(selectedId);
  }, [selectedId, refreshActive]);

  useEffect(() => {
    if (!selectedId || !activeConv) return;
    if ((activeConv.adminUnreadCount ?? 0) > 0 && !document.hidden) {
      void adminMarkSupportRead(selectedId);
    }
  }, [selectedId, activeConv]);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages.length, selectedId]);

  const onFilesChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files ?? []);
    if (selected.length === 0) return;
    setFiles((prev) => [...prev, ...selected].slice(0, MAX_FILES));
    e.target.value = "";
  };

  const removeFileAt = (idx: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedId || sending) return;
    if (!body.trim() && files.length === 0) return;
    setSending(true);
    try {
      const created = await adminPostSupportMessage(selectedId, body, files);
      setMessages((prev) => [...prev, created]);
      setBody("");
      setFiles([]);
      setError(null);
    } catch (e: any) {
      setError(e?.response?.data?.error ?? "Не удалось отправить сообщение.");
    } finally {
      setSending(false);
    }
  };

  const handleAssignSelf = async () => {
    if (!selectedId || actionBusy) return;
    setActionBusy(true);
    try {
      await adminPatchSupportConversation(selectedId, { action: "assign", adminUserId });
      await refreshActive(selectedId);
      await refreshList();
    } catch (e: any) {
      setError(e?.response?.data?.error ?? "Не удалось назначить оператора.");
    } finally {
      setActionBusy(false);
    }
  };

  const handleResolve = async () => {
    if (!selectedId || actionBusy) return;
    const note = resolveNote.trim();
    if (!note) {
      setError("Укажите краткий комментарий о решении.");
      return;
    }
    setActionBusy(true);
    try {
      await adminPatchSupportConversation(selectedId, { action: "resolve", resolutionNote: note });
      setResolveNote("");
      await refreshActive(selectedId);
      await refreshList();
    } catch (e: any) {
      setError(e?.response?.data?.error ?? "Не удалось пометить решённым.");
    } finally {
      setActionBusy(false);
    }
  };

  const handleClose = async () => {
    if (!selectedId || actionBusy) return;
    setActionBusy(true);
    try {
      await adminPatchSupportConversation(selectedId, { action: "close" });
      await refreshActive(selectedId);
      await refreshList();
    } catch (e: any) {
      setError(e?.response?.data?.error ?? "Не удалось закрыть.");
    } finally {
      setActionBusy(false);
    }
  };

  const handleReopen = async () => {
    if (!selectedId || actionBusy) return;
    setActionBusy(true);
    try {
      await adminPatchSupportConversation(selectedId, { action: "reopen" });
      await refreshActive(selectedId);
      await refreshList();
    } catch (e: any) {
      setError(e?.response?.data?.error ?? "Не удалось переоткрыть.");
    } finally {
      setActionBusy(false);
    }
  };

  const visibleConversations = useMemo(() => {
    return [...conversations].sort((a, b) => {
      const la = a.lastMessageAt ? new Date(a.lastMessageAt).getTime() : 0;
      const lb = b.lastMessageAt ? new Date(b.lastMessageAt).getTime() : 0;
      return lb - la;
    });
  }, [conversations]);

  return (
    <div className="admin-support-page">
      <aside className="admin-support-list">
        <h2>Обращения</h2>
        {error && <div className="support-error" role="alert">{error}</div>}
        {visibleConversations.length === 0 ? (
          <div className="support-empty">Пока нет обращений.</div>
        ) : (
          <ul>
            {visibleConversations.map((c) => (
              <li
                key={c.id}
                className={`admin-support-list-item ${selectedId === c.id ? "is-active" : ""} status-${c.status}`}
                onClick={() => setSelectedId(c.id)}
              >
                <div className="admin-support-list-item-row1">
                  <span className="admin-support-list-name">
                    {c.studentDisplayName || c.studentEmail || c.studentUserId.slice(0, 8)}
                  </span>
                  <span className="admin-support-list-time">{formatTime(c.lastMessageAt)}</span>
                </div>
                <div className="admin-support-list-item-row2">
                  <span className="admin-support-list-preview">
                    {c.lastMessagePreview || "—"}
                  </span>
                  {(c.adminUnreadCount ?? 0) > 0 && (
                    <span className="admin-support-list-unread">{c.adminUnreadCount}</span>
                  )}
                </div>
                <div className="admin-support-list-status">{c.status}</div>
              </li>
            ))}
          </ul>
        )}
      </aside>

      <section className="admin-support-thread">
        {!activeConv ? (
          <div className="support-empty">Выберите обращение слева.</div>
        ) : (
          <>
            <header className="admin-support-thread-header">
              <div>
                <h3>{activeConv.studentDisplayName || activeConv.studentEmail || activeConv.studentUserId}</h3>
                <p className="admin-support-thread-sub">
                  Статус: <strong>{activeConv.status}</strong>
                  {activeConv.assignedAdminName && <> · Оператор: {activeConv.assignedAdminName}</>}
                </p>
              </div>
              <div className="admin-support-thread-actions">
                {activeConv.assignedAdminUserId !== adminUserId && (
                  <button type="button" onClick={handleAssignSelf} disabled={actionBusy}>Взять в работу</button>
                )}
                {activeConv.status === "open" && (
                  <>
                    <input
                      type="text"
                      placeholder="Комментарий о решении"
                      value={resolveNote}
                      onChange={(e) => setResolveNote(e.target.value)}
                      aria-label="Комментарий о решении"
                    />
                    <button type="button" onClick={handleResolve} disabled={actionBusy}>Решено</button>
                  </>
                )}
                {activeConv.status === "resolved" && (
                  <button type="button" onClick={handleClose} disabled={actionBusy}>Закрыть</button>
                )}
                {(activeConv.status === "resolved" || activeConv.status === "closed") && (
                  <button type="button" onClick={handleReopen} disabled={actionBusy}>Открыть заново</button>
                )}
              </div>
            </header>

            <div className="support-messages" ref={scrollerRef}>
              {messages.length === 0 ? (
                <div className="support-empty">История пуста.</div>
              ) : (
                messages.map((m) => (
                  <div
                    key={m.id}
                    className={`support-message support-message-${m.senderRole === "admin" ? "outgoing" : "incoming"}`}
                  >
                    {m.bodyText && <div className="support-message-body">{m.bodyText}</div>}
                    {m.attachments && m.attachments.length > 0 && (
                      <ul className="support-message-attachments">
                        {m.attachments.map((att) => (
                          <li key={att.id}>
                            <a href={att.downloadUrl} target="_blank" rel="noopener noreferrer">
                              {att.originalName}
                            </a>{" "}
                            <span className="support-attachment-size">({formatSize(att.sizeBytes)})</span>
                          </li>
                        ))}
                      </ul>
                    )}
                    <div className="support-message-meta">
                      <span>{formatTime(m.createdAt)}</span>
                      {m.senderRole === "admin" && (
                        <span className="support-message-status" aria-label={`Статус: ${m.status}`}>
                          {m.status === "sent" ? "✓" : m.status === "delivered" ? "✓✓" : "✓✓✓"}
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            <form className="support-composer" onSubmit={onSubmit}>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Ответ пользователю…"
                rows={3}
                aria-label="Текст ответа"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void onSubmit(e as unknown as FormEvent);
                  }
                }}
              />
              <div className="support-composer-row">
                <label className="support-attach-btn">
                  📎 Прикрепить
                  <input type="file" multiple hidden onChange={onFilesChange} aria-label="Прикрепить файл" />
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
                До {MAX_FILES} файлов за сообщение.
              </p>
            </form>
          </>
        )}
      </section>
    </div>
  );
}
