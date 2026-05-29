import axios, { AxiosHeaders, InternalAxiosRequestConfig } from "axios";
import { API_URL, LoginPayload, RegisterPayload } from "./types";
import { clearAllUserScopedStorage } from "../utils/userScopedStorage";

const tokenKey = "lc_access_token";
const refreshKey = "lc_refresh_token";
const authRoute = "/auth";
const CACHE_TTL_FAST_MS = 3_000;
const CACHE_TTL_SHORT_MS = 10_000;
const CACHE_TTL_PROFILE_MS = 5_000;
const CACHE_TTL_MATERIALS_MS = 6 * 60 * 60 * 1_000;
const REQUEST_TIMEOUT_MS = 15_000;
const PERSISTED_GET_CACHE_PREFIX = "lc_get_cache_v1::";
const MAX_PERSISTED_ENTRY_SIZE_BYTES = 350_000;

type CachedEntry = {
  expiresAt: number;
  data: unknown;
};

type CachedGetOptions = {
  params?: Record<string, unknown>;
  ttlMs?: number;
  cacheKey?: string;
  persist?: boolean;
};

const readCache = new Map<string, CachedEntry>();
const inFlightGet = new Map<string, Promise<unknown>>();

export const http = axios.create({
  baseURL: API_URL,
  timeout: REQUEST_TIMEOUT_MS,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(tokenKey);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function clearReadCaches() {
  readCache.clear();
  inFlightGet.clear();
}

function clearPersistedReadCaches() {
  if (typeof window === "undefined") return;
  try {
    const keysToDelete: string[] = [];
    for (let index = 0; index < localStorage.length; index += 1) {
      const key = localStorage.key(index);
      if (key?.startsWith(PERSISTED_GET_CACHE_PREFIX)) {
        keysToDelete.push(key);
      }
    }
    keysToDelete.forEach((key) => localStorage.removeItem(key));
  } catch {
    // ignore storage access issues
  }
}

function buildPersistentCacheStorageKey(cacheKey: string): string {
  return `${PERSISTED_GET_CACHE_PREFIX}${encodeURIComponent(cacheKey)}`;
}

function readPersistentCacheValue<T>(cacheKey: string): T | null {
  if (typeof window === "undefined") return null;
  const storageKey = buildPersistentCacheStorageKey(cacheKey);

  try {
    const raw = localStorage.getItem(storageKey);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as CachedEntry;
    if (!parsed || typeof parsed.expiresAt !== "number" || !("data" in parsed)) {
      localStorage.removeItem(storageKey);
      return null;
    }
    if (parsed.expiresAt <= Date.now()) {
      localStorage.removeItem(storageKey);
      return null;
    }
    readCache.set(cacheKey, parsed);
    return parsed.data as T;
  } catch {
    return null;
  }
}

function writePersistentCacheValue(cacheKey: string, data: unknown, ttlMs: number) {
  if (ttlMs <= 0 || typeof window === "undefined") return;

  const payload = {
    data,
    expiresAt: Date.now() + ttlMs,
  };

  try {
    const serialized = JSON.stringify(payload);
    if (serialized.length > MAX_PERSISTED_ENTRY_SIZE_BYTES) return;
    localStorage.setItem(buildPersistentCacheStorageKey(cacheKey), serialized);
  } catch {
    // ignore quota/storage errors; in-memory cache still works
  }
}

function serializeParamValue(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(serializeParamValue).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.entries(value as Record<string, unknown>)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, nested]) => `${key}:${serializeParamValue(nested)}`)
      .join(",")}}`;
  }
  return String(value);
}

function buildGetCacheKey(url: string, params?: Record<string, unknown>): string {
  if (!params) return url;
  const serializedParams = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null)
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([key, value]) => `${key}=${serializeParamValue(value)}`)
    .join("&");
  return serializedParams ? `${url}?${serializedParams}` : url;
}

function getCachedValue<T>(cacheKey: string): T | null {
  const now = Date.now();
  const entry = readCache.get(cacheKey);
  if (!entry) return null;
  if (entry.expiresAt <= now) {
    readCache.delete(cacheKey);
    return null;
  }
  return entry.data as T;
}

function setCachedValue(cacheKey: string, data: unknown, ttlMs: number) {
  if (ttlMs <= 0) return;
  readCache.set(cacheKey, {
    data,
    expiresAt: Date.now() + ttlMs,
  });
}

async function cachedGet<T>(url: string, options?: CachedGetOptions): Promise<T> {
  const params = options?.params;
  const ttlMs = options?.ttlMs ?? 0;
  const cacheKey = options?.cacheKey ?? buildGetCacheKey(url, params);
  const persist = options?.persist ?? false;

  if (ttlMs > 0) {
    const cached = getCachedValue<T>(cacheKey);
    if (cached !== null) {
      return cached;
    }
    if (persist) {
      const persisted = readPersistentCacheValue<T>(cacheKey);
      if (persisted !== null) {
        return persisted;
      }
    }
  }

  const inFlight = inFlightGet.get(cacheKey);
  if (inFlight) {
    return inFlight as Promise<T>;
  }

  const request = http
    .get(url, { params })
    .then((response) => {
      const data = response.data as T;
      if (ttlMs > 0) {
        setCachedValue(cacheKey, data, ttlMs);
        if (persist) {
          writePersistentCacheValue(cacheKey, data, ttlMs);
        }
      }
      return data;
    })
    .finally(() => {
      inFlightGet.delete(cacheKey);
    });

  inFlightGet.set(cacheKey, request);
  return request;
}

export function saveTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(tokenKey, accessToken);
  localStorage.setItem(refreshKey, refreshToken);
  clearReadCaches();
}

export function clearTokens() {
  localStorage.removeItem(tokenKey);
  localStorage.removeItem(refreshKey);
  clearReadCaches();
  clearPersistedReadCaches();
  clearAllUserScopedStorage();
}

export function getAccessToken() {
  return localStorage.getItem(tokenKey);
}

export function getRefreshToken() {
  return localStorage.getItem(refreshKey);
}

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }

  try {
    const { data } = await axios.post(`${API_URL}/auth/refresh`, { refreshToken }, { timeout: REQUEST_TIMEOUT_MS });
    const nextAccess = String(data?.accessToken ?? "");
    const nextRefresh = String(data?.refreshToken ?? "");
    if (!nextAccess || !nextRefresh) {
      return null;
    }
    saveTokens(nextAccess, nextRefresh);
    return nextAccess;
  } catch {
    return null;
  }
}

function shouldTryRefresh(status: number | undefined, url?: string) {
  if (status !== 401 || !url) {
    return false;
  }
  return !url.includes("/auth/login") && !url.includes("/auth/register") && !url.includes("/auth/refresh");
}

function forceAuthRedirect() {
  clearTokens();
  if (typeof window !== "undefined" && window.location.pathname !== authRoute) {
    window.location.assign(authRoute);
  }
}

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error?.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const status = error?.response?.status as number | undefined;
    const url = String(original?.url ?? "");

    if (!original || original._retry || !shouldTryRefresh(status, url)) {
      return Promise.reject(error);
    }

    original._retry = true;

    if (!refreshPromise) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
    }

    const nextAccessToken = await refreshPromise;
    if (!nextAccessToken) {
      forceAuthRedirect();
      return Promise.reject(error);
    }

    if (!original.headers) {
      original.headers = new AxiosHeaders();
    }

    if (original.headers instanceof AxiosHeaders) {
      original.headers.set("Authorization", `Bearer ${nextAccessToken}`);
    } else {
      const nextHeaders = new AxiosHeaders(original.headers);
      nextHeaders.set("Authorization", `Bearer ${nextAccessToken}`);
      original.headers = nextHeaders;
    }
    return http(original);
  }
);

export async function register(payload: RegisterPayload) {
  const { data } = await http.post("/auth/register", payload);
  if (data.tokens?.accessToken) {
    saveTokens(data.tokens.accessToken, data.tokens.refreshToken);
  }
  return data;
}

export async function login(payload: LoginPayload) {
  const { data } = await http.post("/auth/login", payload);
  if (data.accessToken) {
    saveTokens(data.accessToken, data.refreshToken);
  }
  return data;
}

export async function me() {
  return cachedGet("/me", { ttlMs: CACHE_TTL_PROFILE_MS });
}

export async function listCourses() {
  const data = await cachedGet<{ items: Array<Record<string, unknown>> }>("/courses", {
    ttlMs: CACHE_TTL_MATERIALS_MS,
    persist: true,
  });
  return data.items;
}

export async function getCourse(courseId: string) {
  return cachedGet(`/courses/${courseId}`, { ttlMs: CACHE_TTL_FAST_MS });
}

export async function getCourseTasksCatalog(courseId: string) {
  return cachedGet(`/courses/${courseId}/tasks-catalog`, { ttlMs: CACHE_TTL_FAST_MS });
}

export async function getLesson(lessonId: string) {
  return cachedGet(`/lessons/${lessonId}`, { ttlMs: CACHE_TTL_FAST_MS });
}

export async function checkLessonQuiz(lessonId: string, blockId: string, answers: Record<string, string>) {
  const { data } = await http.post(`/lessons/${lessonId}/quiz-check`, { blockId, answers });
  clearReadCaches();
  return data;
}

export async function completeLessonBlock(
  lessonId: string,
  blockId: string,
  payload?: { source?: string; submissionId?: string }
) {
  const { data } = await http.post(`/lessons/${lessonId}/blocks/${blockId}/complete`, payload ?? {});
  clearReadCaches();
  return data;
}

export async function getTask(taskId: string) {
  return cachedGet(`/tasks/${taskId}`, { ttlMs: CACHE_TTL_MATERIALS_MS, persist: true });
}

export async function submitTask(taskId: string, sourceCode: string) {
  const { data } = await http.post(`/tasks/${taskId}/submissions`, { sourceCode });
  clearReadCaches();
  return data;
}

export async function runTask(taskId: string, sourceCode: string) {
  const { data } = await http.post(`/tasks/${taskId}/run`, { sourceCode });
  return data;
}

export async function taskHint(taskId: string, sourceCode: string) {
  const { data } = await http.post("/ai/task-hint", { taskId, sourceCode });
  return data;
}

export async function getSubmission(submissionId: string) {
  const { data } = await http.get(`/submissions/${submissionId}`);
  return data;
}

export async function submissionHistory() {
  const data = await cachedGet<{ items: unknown[] }>("/me/submission-history", { ttlMs: CACHE_TTL_FAST_MS });
  return data.items;
}

export async function leaderboard() {
  const data = await cachedGet<{ items: unknown[] }>("/leaderboard", { ttlMs: CACHE_TTL_FAST_MS });
  return data.items;
}

export async function achievements() {
  const data = await cachedGet<{ items: unknown[] }>("/me/achievements", { ttlMs: CACHE_TTL_FAST_MS });
  return data.items;
}

export async function plans() {
  const data = await cachedGet<{ items: unknown[] }>("/plans", { ttlMs: CACHE_TTL_SHORT_MS });
  return data.items;
}

export async function subscription() {
  return cachedGet("/subscription", { ttlMs: CACHE_TTL_FAST_MS });
}

export async function checkout(planCode: string) {
  const { data } = await http.post("/subscription/checkout", { planCode });
  return data;
}

export async function applyPromoCode(code: string) {
  const { data } = await http.post("/subscription/promocode/apply", { code });
  clearReadCaches();
  return data;
}

export async function cancelSubscription() {
  const { data } = await http.post("/subscription/cancel");
  return data;
}

export async function subscriptionPaymentStatus(paymentId: string, sync = false) {
  if (sync) {
    const { data } = await http.get(`/subscription/payments/${paymentId}`, { params: { sync: true } });
    return data;
  }
  return cachedGet(`/subscription/payments/${paymentId}`, { ttlMs: CACHE_TTL_FAST_MS });
}

export async function adminMetrics() {
  return cachedGet("/admin/metrics/overview", { ttlMs: CACHE_TTL_FAST_MS });
}

export async function adminExportCSV(from?: string, to?: string) {
  const { data } = await http.get("/admin/metrics/export", {
    params: { from, to },
    responseType: "blob",
  });
  return data;
}
