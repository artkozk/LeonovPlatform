// Same-origin relative base. После 2026-05-17 фронтенд раздаётся
// nginx'ом с того же домена (https://platform.ngix.leonovcare.ru),
// который проксирует /api/v1/* на бэкенд upstream. Жёсткий
// `http://host:8510/api/v1` ломал бы HTTPS-страницу через
// mixed-content и не работал бы из-под VPN, у которого нет
// маршрута до bare-IP. Same-origin path этих проблем не имеет:
// браузер сам подставит scheme/host/port текущей страницы.
//
// VITE_API_URL остаётся override'ом для dev-режима (когда фронт
// слушает vite на 5173, а бэк отдельно на 8510 — там нужна полная
// абсолютная URL с CORS).
const RUNTIME_FALLBACK_API_URL = "/api/v1";

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
