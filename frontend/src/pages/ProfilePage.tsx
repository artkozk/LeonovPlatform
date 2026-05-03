import { CreditCard, ShieldCheck, Trophy, UserRound } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../store/auth";

export function ProfilePage() {
  const user = useAuthStore((s) => s.user);

  const fullName = `${user?.firstName ?? ""} ${user?.lastName ?? ""}`.trim() || user?.nickname || "Пользователь";
  const initials = fullName
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("") || "LC";

  return (
    <div className="profile-page page-stack">
      <section className="surface profile-hero-card">
        <div className="profile-identity">
          <span className="profile-initials" aria-hidden="true">{initials}</span>
          <div>
            <h1>{fullName}</h1>
            <p>{user?.email ?? "Email не указан"}</p>
          </div>
        </div>
        <div className="profile-meta">
          <span className="badge badge-blue">{user?.planCode?.toUpperCase() ?? "FREE"} • L{user?.level ?? 1}</span>
          <span className="badge badge-neutral">XP {user?.xp ?? 0}</span>
        </div>
      </section>

      <section className="stats-grid">
        <article className="surface compact-stat-card">
          <span className="stat-icon"><UserRound size={16} strokeWidth={1.9} /></span>
          <p>Публичный ID</p>
          <strong>{user?.publicId ?? "—"}</strong>
        </article>
        <article className="surface compact-stat-card">
          <span className="stat-icon"><Trophy size={16} strokeWidth={1.9} /></span>
          <p>Уровень</p>
          <strong>L{user?.level ?? 1}</strong>
        </article>
        <article className="surface compact-stat-card">
          <span className="stat-icon"><ShieldCheck size={16} strokeWidth={1.9} /></span>
          <p>Роль</p>
          <strong>{user?.role === "admin" ? "Admin" : "Student"}</strong>
        </article>
        <article className="surface compact-stat-card">
          <span className="stat-icon"><CreditCard size={16} strokeWidth={1.9} /></span>
          <p>План</p>
          <strong>{user?.planCode?.toUpperCase() ?? "FREE"}</strong>
        </article>
      </section>

      <section className="surface profile-links-card">
        <div className="section-head">
          <div>
            <h2>Управление аккаунтом</h2>
            <p>Переход к управлению подпиской.</p>
          </div>
        </div>

        <div className="profile-links">
          <Link to="/billing" className="profile-link-row">
            <span className="profile-link-icon" aria-hidden="true"><CreditCard size={16} strokeWidth={1.9} /></span>
            <div>
              <strong>Подписка</strong>
              <p>Текущий план, оплата и история платежей.</p>
            </div>
          </Link>
        </div>
      </section>
    </div>
  );
}
