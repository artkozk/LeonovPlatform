export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8080/api/v1";

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
