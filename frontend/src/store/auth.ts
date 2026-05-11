import { create } from "zustand";
import { clearTokens, getAccessToken, login as apiLogin, me as apiMe, register as apiRegister } from "../api/client";
import { UserProfile } from "../api/types";

let bootstrapPromise: Promise<UserProfile | null> | null = null;

function resolveAuthError(error: any, fallback: string) {
  const responseError = error?.response?.data?.error;
  if (typeof responseError === "string" && responseError.trim() !== "") {
    return responseError;
  }

  const code = String(error?.code ?? "").toUpperCase();
  if (code === "ECONNABORTED") {
    return "Сервер долго не отвечает. Проверьте подключение к платформе и повторите попытку.";
  }

  const message = String(error?.message ?? "").toLowerCase();
  if (message.includes("network error") || message.includes("failed to fetch")) {
    return "Не удаётся подключиться к серверу авторизации. Проверьте интернет/VPN и адрес платформы.";
  }

  return fallback;
}

type AuthStore = {
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
  bootstrap: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: {
    email: string;
    firstName: string;
    lastName: string;
    nickname: string;
    password: string;
  }) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
};

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  loading: false,
  error: null,

  bootstrap: async () => {
    if (!getAccessToken()) return;
    set({ loading: true, error: null });
    try {
      if (!bootstrapPromise) {
        bootstrapPromise = apiMe()
          .then((profile) => profile as UserProfile)
          .catch(() => null)
          .finally(() => {
            bootstrapPromise = null;
          });
      }

      const profile = await bootstrapPromise;
      if (!getAccessToken()) {
        set({ user: null, loading: false, error: null });
        return;
      }
      if (!profile) {
        clearTokens();
        set({ user: null, loading: false, error: null });
        return;
      }
      set({ user: profile, loading: false, error: null });
    } catch {
      clearTokens();
      set({ user: null, loading: false, error: null });
    }
  },

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      await apiLogin({ email, password });
      const profile = await apiMe();
      set({ user: profile, loading: false, error: null });
    } catch (e: any) {
      set({ loading: false, error: resolveAuthError(e, "Не удалось выполнить вход") });
    }
  },

  register: async (payload) => {
    set({ loading: true, error: null });
    try {
      await apiRegister(payload);
      const profile = await apiMe();
      set({ user: profile, loading: false, error: null });
    } catch (e: any) {
      set({ loading: false, error: resolveAuthError(e, "Не удалось создать аккаунт") });
    }
  },

  logout: () => {
    bootstrapPromise = null;
    clearTokens();
    set({ user: null, error: null, loading: false });
  },

  refreshProfile: async () => {
    try {
      const profile = await apiMe();
      set({ user: profile });
    } catch {
      set({ user: null });
    }
  },
}));
