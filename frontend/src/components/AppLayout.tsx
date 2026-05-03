import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, LogOut, ShieldCheck } from "lucide-react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

type MenuItem = {
  to: string;
  label: string;
  isActive: (pathname: string) => boolean;
};

const menu: MenuItem[] = [
  { to: "/dashboard", label: "Главная", isActive: (pathname) => pathname.startsWith("/dashboard") },
  {
    to: "/courses",
    label: "Обучение",
    isActive: (pathname) => pathname.startsWith("/courses") || pathname.startsWith("/lessons/"),
  },
  { to: "/tasks", label: "Задачи", isActive: (pathname) => pathname.startsWith("/tasks") },
  { to: "/checks", label: "Проверки", isActive: (pathname) => pathname.startsWith("/checks") },
  { to: "/leaderboard", label: "Рейтинг", isActive: (pathname) => pathname.startsWith("/leaderboard") },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement | null>(null);

  const currentPlan = useMemo(() => `${user?.planCode?.toUpperCase() ?? "FREE"} • L${user?.level ?? 1}`, [user?.planCode, user?.level]);
  const displayName = useMemo(() => {
    const fullName = `${user?.firstName ?? ""} ${user?.lastName ?? ""}`.trim();
    if (fullName) return fullName;
    return user?.nickname ?? "Пользователь";
  }, [user?.firstName, user?.lastName, user?.nickname]);

  useEffect(() => {
    setProfileMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!profileMenuOpen) return;

    function handleClickOutside(event: MouseEvent) {
      const target = event.target as Node | null;
      if (!target) return;
      if (profileMenuRef.current?.contains(target)) return;
      setProfileMenuOpen(false);
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setProfileMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [profileMenuOpen]);

  return (
    <div className="workspace-shell">
      <header className="app-header">
        <div className="app-header-inner">
          <Link className="app-brand" to="/dashboard" aria-label="Leonov Care">
            <span className="app-brand-title">Leonov Care</span>
          </Link>

          <nav className="app-nav" aria-label="Основная навигация">
            {menu.map((item) => {
              const active = item.isActive(location.pathname);
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={`app-nav-link ${active ? "active" : ""}`}
                  aria-current={active ? "page" : undefined}
                >
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>

          <div className="app-user-zone">
            <div className="app-user-meta">
              <span className="app-user-name">{displayName}</span>
              <span className="app-user-plan">{currentPlan}</span>
            </div>

            <div className="profile-menu" ref={profileMenuRef}>
              <button
                type="button"
                className="btn btn-secondary btn-sm profile-menu-trigger"
                aria-label="Открыть меню профиля"
                aria-expanded={profileMenuOpen}
                onClick={() => setProfileMenuOpen((prev) => !prev)}
              >
                Профиль
                <ChevronDown size={15} strokeWidth={2} className={profileMenuOpen ? "profile-menu-chevron open" : "profile-menu-chevron"} />
              </button>

              {profileMenuOpen && (
                <div className="profile-menu-panel">
                  <Link to="/profile" className="profile-menu-link" onClick={() => setProfileMenuOpen(false)}>Профиль</Link>
                  <Link to="/billing" className="profile-menu-link" onClick={() => setProfileMenuOpen(false)}>Подписка</Link>
                  {user?.role === "admin" && (
                    <Link to="/admin" className="profile-menu-link profile-menu-link-admin" onClick={() => setProfileMenuOpen(false)}>
                      <ShieldCheck size={14} strokeWidth={2} />
                      Админ
                    </Link>
                  )}
                </div>
              )}
            </div>

            <button
              className="btn btn-ghost btn-sm"
              onClick={() => {
                logout();
                navigate("/auth");
              }}
            >
              <LogOut size={15} strokeWidth={2} />
              Выйти
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        <section className="app-main-inner">{children}</section>
      </main>
    </div>
  );
}
