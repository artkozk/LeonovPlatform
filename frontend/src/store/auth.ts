import { create } from "zustand";
import { clearTokens, getAccessToken, login as apiLogin, me as apiMe, register as apiRegister } from "../api/client";
import { UserProfile } from "../api/types";

let bootstrapPromise: Promise<UserProfile | null> | null = null;

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
      set({ loading: false, error: e?.response?.data?.error ?? "Не удалось выполнить вход" });
    }
  },

  register: async (payload) => {
    set({ loading: true, error: null });
    try {
      await apiRegister(payload);
      const profile = await apiMe();
      set({ user: profile, loading: false, error: null });
    } catch (e: any) {
      set({ loading: false, error: e?.response?.data?.error ?? "Не удалось создать аккаунт" });
    }
  },

  logout: () => {
    clearTokens();
    set({ user: null, error: null });
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
