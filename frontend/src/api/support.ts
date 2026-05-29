// ============================================================================
// Support chat — frontend API client (2026-05-16).
//
// Реализация blueprint:
//   docs/architecture/SUPPORT_CHAT_IMPLEMENTATION_BLUEPRINT_2026_05_16.md
//
// Почему отдельный файл, а не дополнение client.ts:
//   1. client.ts уже большой; support-чат это самостоятельная фича со
//      своими SSE-методами, тип-defs, multipart. Изоляция повышает
//      читаемость и упрощает удаление при rollback feature flag.
//
//   2. Чтобы один раз импортнуть SupportConversation/SupportMessage и
//      использовать в двух разных страницах (/support, /admin/support)
//      без дублирования типов.
//
// SSE-логика (см. blueprint §6 «guardrail»):
//   - reconnect c backoff (1s → 2s → 4s → 8s, capped at 8s);
//   - heartbeat от сервера 'ping' каждые ~25s; на клиенте мы их
//     используем как live-check, но не действуем — само EventSource
//     уже умеет reconnect.
//   - после reconnect мы делаем full re-fetch состояния, потому что
//     сервер не отправляет историю (как и просит blueprint §6 «idempotent»).
// ============================================================================

import { API_URL } from "./types";
import { getAccessToken, http } from "./client";

export type SupportStatus = "open" | "resolved" | "closed";
export type SupportSender = "student" | "admin" | "system";
export type SupportMessageStatus = "sent" | "delivered" | "read";

export interface SupportAttachment {
  id: string;
  messageId: string;
  originalName: string;
  mimeType: string;
  sizeBytes: number;
  downloadUrl: string;
  createdAt: string;
}

export interface SupportMessage {
  id: string;
  conversationId: string;
  senderUserId: string;
  senderRole: SupportSender;
  bodyText: string;
  status: SupportMessageStatus;
  deliveredAt?: string;
  readAt?: string;
  hasAttachments: boolean;
  attachments?: SupportAttachment[];
  createdAt: string;
}

export interface SupportConversation {
  id: string;
  studentUserId: string;
  studentDisplayName?: string;
  studentEmail?: string;
  status: SupportStatus;
  assignedAdminUserId?: string;
  assignedAdminName?: string;
  resolutionNote?: string;
  resolvedAt?: string;
  closedAt?: string;
  lastMessageAt?: string;
  lastMessagePreview?: string;
  lastMessageSenderRole?: SupportSender;
  studentUnreadCount: number;
  adminUnreadCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface SupportEvent {
  id: string;
  conversationId: string;
  eventType: string;
  actorUserId?: string;
  actorName?: string;
  payload?: Record<string, unknown>;
  createdAt: string;
}

// ---------------------------------------------------------------------------
// Student API
// ---------------------------------------------------------------------------

export async function getSupportConversation(): Promise<SupportConversation> {
  const { data } = await http.get<SupportConversation>("/support/conversation");
  return data;
}

export interface ListSupportMessagesResponse {
  conversation: SupportConversation;
  messages: SupportMessage[];
}

export async function listSupportMessages(opts?: { cursor?: string; limit?: number }): Promise<ListSupportMessagesResponse> {
  const { data } = await http.get<ListSupportMessagesResponse>("/support/conversation/messages", {
    params: { cursor: opts?.cursor, limit: opts?.limit ?? 50 },
  });
  return data;
}

export async function postSupportMessage(body: string, files: File[]): Promise<SupportMessage> {
  const form = new FormData();
  if (body && body.trim()) form.append("body", body);
  for (const f of files) form.append("files", f, f.name);
  const { data } = await http.post<SupportMessage>("/support/conversation/messages", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function markSupportRead(): Promise<void> {
  await http.post("/support/conversation/read");
}

// ---------------------------------------------------------------------------
// Admin API
// ---------------------------------------------------------------------------

export interface ListAdminSupportConversationsResponse {
  items: SupportConversation[];
}

export async function adminListSupportConversations(opts?: { status?: SupportStatus; limit?: number }): Promise<ListAdminSupportConversationsResponse> {
  const { data } = await http.get<ListAdminSupportConversationsResponse>("/admin/support/conversations", {
    params: { status: opts?.status, limit: opts?.limit ?? 100 },
  });
  return data;
}

export async function adminGetSupportConversation(conversationId: string): Promise<SupportConversation> {
  const { data } = await http.get<SupportConversation>(`/admin/support/conversations/${conversationId}`);
  return data;
}

export async function adminListSupportMessages(conversationId: string, opts?: { cursor?: string; limit?: number }): Promise<{ messages: SupportMessage[] }> {
  const { data } = await http.get<{ messages: SupportMessage[] }>(`/admin/support/conversations/${conversationId}/messages`, {
    params: { cursor: opts?.cursor, limit: opts?.limit ?? 50 },
  });
  return data;
}

export async function adminPostSupportMessage(conversationId: string, body: string, files: File[]): Promise<SupportMessage> {
  const form = new FormData();
  if (body && body.trim()) form.append("body", body);
  for (const f of files) form.append("files", f, f.name);
  const { data } = await http.post<SupportMessage>(`/admin/support/conversations/${conversationId}/messages`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function adminMarkSupportRead(conversationId: string): Promise<void> {
  await http.post(`/admin/support/conversations/${conversationId}/read`);
}

export type SupportPatchAction = "assign" | "unassign" | "resolve" | "reopen" | "close";

export async function adminPatchSupportConversation(
  conversationId: string,
  payload: { action: SupportPatchAction; adminUserId?: string; resolutionNote?: string },
): Promise<SupportConversation> {
  const { data } = await http.patch<SupportConversation>(`/admin/support/conversations/${conversationId}`, payload);
  return data;
}

export async function adminListSupportEvents(conversationId: string): Promise<{ items: SupportEvent[] }> {
  const { data } = await http.get<{ items: SupportEvent[] }>(`/admin/support/conversations/${conversationId}/events`);
  return data;
}

// ---------------------------------------------------------------------------
// SSE stream
// ---------------------------------------------------------------------------

export interface SupportStreamEvent {
  type: "hello" | "ping" | "message_created" | "message_status" | "conversation_updated";
  data: any;
}

export type SupportStreamHandler = (event: SupportStreamEvent) => void;

/**
 * openSupportStream — открывает SSE-канал. Возвращает функцию закрытия.
 *
 * Особенности (см. blueprint §6):
 *  - native EventSource не умеет посылать кастомные заголовки, поэтому
 *    мы передаём токен как query-parameter `access_token`. Backend
 *    middleware читает Bearer из Authorization; без него EventSource
 *    не подойдёт. ВАЖНО: текущая авторизация требует Bearer в Authorization
 *    header. Поэтому реализуем через `fetch` + ReadableStream, а не
 *    EventSource — это даёт нам Authorization header.
 *
 *  - Reconnect c backoff (1s → 2s → 4s → 8s) реализован вручную.
 *  - На каждый reconnect handler получает синтетическое событие
 *    `{ type: 'hello', data: { reconnected: true } }`, чтобы UI смог
 *    повторно затянуть состояние (idempotent re-fetch).
 */
export function openSupportStream(onEvent: SupportStreamHandler): () => void {
  let cancelled = false;
  let abortController: AbortController | null = null;
  let reconnectDelay = 1000;

  async function connect() {
    if (cancelled) return;
    abortController = new AbortController();
    const token = getAccessToken();
    if (!token) {
      // Без токена не подключаемся; UI пусть сам пробует позже.
      return;
    }

    try {
      const response = await fetch(`${API_URL}/support/stream`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "text/event-stream",
        },
        signal: abortController.signal,
      });
      if (!response.ok || !response.body) {
        throw new Error(`stream failed: ${response.status}`);
      }
      reconnectDelay = 1000;
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      while (!cancelled) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let sep: number;
        while ((sep = buffer.indexOf("\n\n")) !== -1) {
          const frame = buffer.slice(0, sep);
          buffer = buffer.slice(sep + 2);
          handleFrame(frame, onEvent);
        }
      }
    } catch {
      if (cancelled) return;
    } finally {
      try {
        abortController?.abort();
      } catch {
        // ignore
      }
    }

    if (cancelled) return;
    setTimeout(() => {
      reconnectDelay = Math.min(reconnectDelay * 2, 8000);
      onEvent({ type: "hello", data: { reconnected: true } });
      void connect();
    }, reconnectDelay);
  }

  void connect();

  return () => {
    cancelled = true;
    try {
      abortController?.abort();
    } catch {
      // ignore
    }
  };
}

function handleFrame(frame: string, onEvent: SupportStreamHandler) {
  const lines = frame.split("\n");
  let event = "message";
  let dataRaw = "";
  for (const line of lines) {
    if (line.startsWith(":")) continue;
    if (line.startsWith("event:")) {
      event = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      dataRaw += line.slice(5).replace(/^\s/, "") + "\n";
    }
  }
  dataRaw = dataRaw.trimEnd();
  let data: any = null;
  if (dataRaw) {
    try {
      data = JSON.parse(dataRaw);
    } catch {
      data = dataRaw;
    }
  }
  if (event === "hello" || event === "ping" || event === "message_created" || event === "message_status" || event === "conversation_updated") {
    onEvent({ type: event as SupportStreamEvent["type"], data });
  }
}
