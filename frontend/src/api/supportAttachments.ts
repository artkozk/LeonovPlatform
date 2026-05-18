// ============================================================================
// Authenticated attachment opener (2026-05-17).
//
// Проблема, которую этот модуль решает:
//   `/api/v1/support/attachments/:id` требует Bearer-токен. Браузерный
//   тег `<a href="...">` НЕ отправляет Authorization — он живёт только
//   в JS-памяти (axios interceptor). Поэтому прямой клик по ссылке
//   ушёл бы без токена и получил 401 «missing authorization header».
//
// Решение:
//   1. fetch() с Bearer-токеном.
//   2. Получить Blob, создать `URL.createObjectURL(blob)`.
//   3. Для inline-MIME (image/video/audio/pdf) — открыть в новой
//      вкладке и просмотреть прямо там.
//   4. Для всего остального — программно дёрнуть `<a download>` с
//      original filename, чтобы скачать с правильным именем.
//   5. Через 60 секунд `revokeObjectURL` — освобождаем память.
//
// Альтернативы и почему не выбраны:
//   - Cookie-based auth → большой refactor JWT + middleware на серверной
//     стороне, плюс CSRF-проблемы.
//   - Presigned-token URL (`?t=<hmac>`) → лучше для больших файлов
//     (Range requests), отложено в blueprint §9 «production evolution».
//   - Загружать сразу в `<img src>` через Object URL — пришлось бы
//     fetch'ить каждое сообщение при рендере, что дорого. Делаем
//     lazy: только когда юзер кликнул.
// ============================================================================

import { API_URL } from "./types";
import { getAccessToken } from "./client";
import type { SupportAttachment } from "./support";

const inlineMimePrefixes = ["image/", "video/", "audio/"];
const inlineMimeExacts = new Set(["application/pdf"]);

function isInlineSafe(mime: string): boolean {
  const m = (mime ?? "").toLowerCase().split(";")[0].trim();
  if (m === "image/svg+xml") return false; // SVG может нести <script>
  if (inlineMimePrefixes.some((p) => m.startsWith(p))) return true;
  return inlineMimeExacts.has(m);
}

/**
 * openAttachment — кликнул юзер по вложению.
 *
 * Поведение:
 *  - image/video/audio/pdf → откроется в новой вкладке (inline-просмотр).
 *  - всё остальное → сохранится как файл с original filename.
 *
 * Возвращает Promise<void>; ошибки превращает в человекочитаемый
 * Error, чтобы UI мог показать тост.
 */
export async function openAttachment(att: SupportAttachment): Promise<void> {
  const token = getAccessToken();
  if (!token) {
    throw new Error("Сессия истекла — войдите заново.");
  }
  const url = `${API_URL}${att.downloadUrl.replace(/^\/api\/v1/, "")}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    if (res.status === 401) throw new Error("Сессия истекла — войдите заново.");
    if (res.status === 403) throw new Error("Нет доступа к этому файлу.");
    if (res.status === 404) throw new Error("Файл не найден.");
    throw new Error(`Не удалось загрузить файл (HTTP ${res.status}).`);
  }
  const blob = await res.blob();
  const blobUrl = URL.createObjectURL(blob);

  const safeMime = blob.type || att.mimeType;
  if (isInlineSafe(safeMime)) {
    // Открыть просмотр в новой вкладке.
    const w = window.open(blobUrl, "_blank", "noopener,noreferrer");
    if (!w) {
      // Браузер заблокировал popup — fallback на download.
      triggerDownload(blobUrl, att.originalName);
    }
  } else {
    // Скачать с правильным именем.
    triggerDownload(blobUrl, att.originalName);
  }

  // Через минуту освобождаем blob (новая вкладка/скачивание уже
  // успело подхватить данные).
  setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000);
}

function triggerDownload(url: string, filename: string) {
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
