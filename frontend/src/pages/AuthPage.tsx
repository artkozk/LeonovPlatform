import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

function humanAuthError(raw?: string) {
  const text = (raw ?? "").toLowerCase();
  if (!text) return "";
  if (text.includes("nickname must contain at least 3")) return "Ник должен содержать минимум 3 буквы или цифры.";
  if (text.includes("nickname must contain letters")) return "Ник должен содержать буквы, цифры, подчёркивание или дефис.";
  if (text.includes("registerrequest.nickname") && text.includes("min")) return "Ник должен содержать минимум 3 символа.";
  if (text.includes("registerrequest.password") && text.includes("min")) return "Пароль должен быть не короче 8 символов.";
  if (text.includes("invalid credentials")) return "Неверный email или пароль.";
  if (text.includes("user already exists")) return "Пользователь с таким email уже существует.";
  if (text.includes("nickname already exists")) return "Этот ник уже занят.";
  if (text.includes("account blocked")) return "Аккаунт заблокирован. Обратитесь в поддержку.";
  if (text.includes("unauthorized")) return "Сессия истекла. Выполните вход заново.";
  return raw ?? "";
}

export function AuthPage() {
  const navigate = useNavigate();
  const { login, register, loading, error, user } = useAuthStore();
  // bootstrapped — флаг, что первая проверка сессии (GET /me) уже выполнена.
  // Подробнее: docs/operations/AUTH_BOOTSTRAP_FLASH_FIX_2026_05_12.md.
  // Нужен, чтобы залогиненный юзер, открывший /auth напрямую, не видел
  // "вспышку" формы логина до того, как успеет сработать редирект на /dashboard.
  const bootstrapped = useAuthStore((s) => s.bootstrapped);

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [nickname, setNickname] = useState("");

  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  // Пока bootstrap ещё идёт — не рендерим форму. Обоснование: см.
  // docs/operations/AUTH_BOOTSTRAP_FLASH_FIX_2026_05_12.md.
  if (!bootstrapped) {
    return null;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (mode === "login") {
      await login(email, password);
    } else {
      await register({ email, firstName, lastName, nickname, password });
    }

    if (useAuthStore.getState().user) {
      navigate("/dashboard");
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-layout auth-layout-single">
        <section className="auth-form-card">
          <div className="auth-brand-text">Leonov Care</div>

          <div className="auth-form-head">
            <h2>{mode === "login" ? "Вход" : "Регистрация"}</h2>
            <p>{mode === "login" ? "Введите email и пароль." : "Создайте аккаунт для доступа к обучению."}</p>
          </div>

          <div className="segment-switch">
            <button type="button" className={`segment-item ${mode === "login" ? "active" : ""}`} onClick={() => setMode("login")}>
              Вход
            </button>
            <button type="button" className={`segment-item ${mode === "register" ? "active" : ""}`} onClick={() => setMode("register")}>
              Регистрация
            </button>
          </div>

          <form className="auth-form-grid" onSubmit={onSubmit}>
            <label className="field">
              <span>Email</span>
              <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" required />
            </label>

            {mode === "register" && (
              <>
                <label className="field">
                  <span>Имя</span>
                  <input value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="Иван" required />
                </label>
                <label className="field">
                  <span>Фамилия</span>
                  <input value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="Иванов" required />
                </label>
                <label className="field">
                  <span>Ник</span>
                  <input
                    value={nickname}
                    onChange={(e) => setNickname(e.target.value)}
                    placeholder="иван_петров"
                    minLength={3}
                    maxLength={32}
                    required
                  />
                </label>
              </>
            )}

            <label className="field">
              <span>Пароль</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                minLength={mode === "register" ? 8 : undefined}
                maxLength={128}
                required
              />
            </label>

            <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
              {loading ? "Подождите..." : mode === "login" ? "Войти" : "Создать аккаунт"}
            </button>
          </form>

          {error && <div className="status-box status-box-error">{humanAuthError(error) || error}</div>}
        </section>
      </div>
    </div>
  );
}
