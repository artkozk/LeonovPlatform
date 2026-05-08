const RUNTIME_FALLBACK_API_URL =
  typeof window !== "undefined" && window.location.hostname
    ? `http://${window.location.hostname}:8510/api/v1`
    : "http://85.198.82.221:8510/api/v1";

export const API_URL = import.meta.env.VITE_API_URL ?? RUNTIME_FALLBACK_API_URL;

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
