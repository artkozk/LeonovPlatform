const LOCAL_HOSTNAMES = new Set(["localhost", "127.0.0.1", "::1", "[::1]"]);
const HARD_FALLBACK_API_URL = "http://127.0.0.1:8510/api/v1";

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function resolveRuntimeApiUrl(): string {
  if (typeof window === "undefined") {
    return HARD_FALLBACK_API_URL;
  }

  const { hostname, origin, protocol } = window.location;
  if (LOCAL_HOSTNAMES.has(hostname)) {
    return `${protocol}//${hostname}:8510/api/v1`;
  }

  // В production за reverse-proxy API должен идти через тот же origin.
  return `${trimTrailingSlash(origin)}/api/v1`;
}

const envApiUrl = String(import.meta.env.VITE_API_URL ?? "").trim();
export const API_URL = envApiUrl !== "" ? trimTrailingSlash(envApiUrl) : resolveRuntimeApiUrl();

export type LoginPayload = { email: string; password: string };
export type RegisterPayload = {
  email: string;
  firstName: string;
  lastName: string;
  nickname: string;
  password: string;
};

export type UserProfile = {
  id: string;
  publicId: string;
  email: string;
  firstName: string;
  lastName: string;
  nickname: string;
  role: "student" | "admin";
  level: number;
  xp: number;
  streak: number;
  emailVerified: boolean;
  theme: "light";
  language: string;
  notificationsEmail: boolean;
  codeFontSize: number;
  editorTabSize: number;
  editorWordWrap: boolean;
  planCode: string;
};
