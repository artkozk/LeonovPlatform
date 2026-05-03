import axios, { AxiosHeaders, InternalAxiosRequestConfig } from "axios";
import { API_URL, LoginPayload, RegisterPayload } from "./types";

const tokenKey = "lc_access_token";
const refreshKey = "lc_refresh_token";
const authRoute = "/auth";

export const http = axios.create({
  baseURL: API_URL,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(tokenKey);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function saveTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(tokenKey, accessToken);
  localStorage.setItem(refreshKey, refreshToken);
}

export function clearTokens() {
  localStorage.removeItem(tokenKey);
  localStorage.removeItem(refreshKey);
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
    const { data } = await axios.post(`${API_URL}/auth/refresh`, { refreshToken });
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
  const { data } = await http.get("/me");
  return data;
}

export async function listCourses() {
  const { data } = await http.get("/courses");
  return data.items as Array<Record<string, unknown>>;
}

export async function getCourse(courseId: string) {
  const { data } = await http.get(`/courses/${courseId}`);
  return data;
}

export async function getLesson(lessonId: string) {
  const { data } = await http.get(`/lessons/${lessonId}`);
  return data;
}

export async function checkLessonQuiz(lessonId: string, blockId: string, answers: Record<string, string>) {
  const { data } = await http.post(`/lessons/${lessonId}/quiz-check`, { blockId, answers });
  return data;
}

export async function getTask(taskId: string) {
  const { data } = await http.get(`/tasks/${taskId}`);
  return data;
}

export async function submitTask(taskId: string, sourceCode: string) {
  const { data } = await http.post(`/tasks/${taskId}/submissions`, { sourceCode });
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
  const { data } = await http.get("/me/submission-history");
  return data.items;
}

export async function leaderboard() {
  const { data } = await http.get("/leaderboard");
  return data.items;
}

export async function achievements() {
  const { data } = await http.get("/me/achievements");
  return data.items;
}

export async function plans() {
  const { data } = await http.get("/plans");
  return data.items;
}

export async function subscription() {
  const { data } = await http.get("/subscription");
  return data;
}

export async function checkout(planCode: string) {
  const { data } = await http.post("/subscription/checkout", { planCode });
  return data;
}

export async function cancelSubscription() {
  const { data } = await http.post("/subscription/cancel");
  return data;
}

export async function subscriptionPaymentStatus(paymentId: string, sync = false) {
  const { data } = await http.get(`/subscription/payments/${paymentId}`, {
    params: sync ? { sync: true } : undefined,
  });
  return data;
}

export async function adminMetrics() {
  const { data } = await http.get("/admin/metrics/overview");
  return data;
}

export async function adminExportCSV(from?: string, to?: string) {
  const { data } = await http.get("/admin/metrics/export", {
    params: { from, to },
    responseType: "blob",
  });
  return data;
}
