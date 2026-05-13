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
  // `bootstrapped` — true только после того, как мы реально проверили текущую
  // сессию (вызвали /me либо убедились, что токена нет). Используется
  // защищёнными роутами и страницей логина, чтобы не показывать форму
  // авторизации тем, у кого валидный токен ещё проверяется. Добавлено
  // 2026-05-12 для устранения "вспышки" /auth при загрузке.
  bootstrapped: boolean;
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

// Если в localStorage нет access-токена, мы и так знаем, что юзер
// разлогинен — нет смысла блокировать UI ожиданием bootstrap. Поэтому
// `bootstrapped` стартует `true` для безсессионных загрузок, и
// переключается в `false` ровно на время первого /me, если токен есть.
const hasInitialToken = typeof window !== "undefined" && Boolean(getAccessToken());

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  loading: false,
  error: null,
  bootstrapped: !hasInitialToken,

  bootstrap: async () => {
    if (!getAccessToken()) {
      // Нет токена — фронт уже знает, что юзер разлогинен.
      set({ bootstrapped: true });
      return;
    }
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
        // logout случился пока ждали ответ — игнорируем результат.
        set({ user: null, loading: false, error: null, bootstrapped: true });
        return;
      }
      if (!profile) {
        clearTokens();
        set({ user: null, loading: false, error: null, bootstrapped: true });
        return;
      }
      set({ user: profile, loading: false, error: null, bootstrapped: true });
    } catch {
      clearTokens();
      set({ user: null, loading: false, error: null, bootstrapped: true });
    }
  },

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      await apiLogin({ email, password });
      const profile = await apiMe();
      set({ user: profile, loading: false, error: null, bootstrapped: true });
    } catch (e: any) {
      set({ loading: false, error: resolveAuthError(e, "Не удалось выполнить вход") });
    }
  },

  register: async (payload) => {
    set({ loading: true, error: null });
    try {
      await apiRegister(payload);
      const profile = await apiMe();
      set({ user: profile, loading: false, error: null, bootstrapped: true });
    } catch (e: any) {
      set({ loading: false, error: resolveAuthError(e, "Не удалось создать аккаунт") });
    }
  },

  logout: () => {
    bootstrapPromise = null;
    clearTokens();
    // После logout мы по-прежнему "bootstrapped" — просто разлогиненный.
    set({ user: null, error: null, loading: false, bootstrapped: true });
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
