import { Medal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { leaderboard } from "../api/client";
import { useAuthStore } from "../store/auth";

type LeaderboardItem = {
  rank: number;
  nickname: string;
  firstName: string;
  lastName: string;
  xp: number;
  level: number;
};

type Period = "week" | "month" | "all";

export function LeaderboardPage() {
  const currentUser = useAuthStore((s) => s.user);
  const [items, setItems] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [period, setPeriod] = useState<Period>("week");

  useEffect(() => {
    setLoading(true);
    leaderboard()
      .then((rows) => {
        setItems((rows ?? []) as LeaderboardItem[]);
        setError("");
      })
      .catch((e: any) => {
        setItems([]);
        setError(e?.response?.data?.error ?? "Не удалось загрузить рейтинг.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const myRow = useMemo(() => items.find((item) => item.nickname === currentUser?.nickname), [items, currentUser?.nickname]);

  return (
    <div className="leaderboard-page page-stack">
      <section className="surface">
        <div className="page-title-block">
          <h1>Рейтинг</h1>
          <p>Лидеры по XP и уровню среди всех участников платформы.</p>
        </div>

        <div className="checks-toolbar" role="tablist" aria-label="Период рейтинга">
          <button type="button" className={`filter-chip ${period === "week" ? "active" : ""}`} onClick={() => setPeriod("week")}>Неделя</button>
          <button type="button" className={`filter-chip ${period === "month" ? "active" : ""}`} onClick={() => setPeriod("month")}>Месяц</button>
          <button type="button" className={`filter-chip ${period === "all" ? "active" : ""}`} onClick={() => setPeriod("all")}>Всё время</button>
        </div>
      </section>

      {error && <div className="status-box status-box-error">{error}</div>}

      <section className="surface leaderboard-card">
        {loading ? (
          <div className="skeleton-list">
            <span className="skeleton-line" />
            <span className="skeleton-line" />
            <span className="skeleton-line" />
          </div>
        ) : (
          <div className="leaderboard-table">
            <div className="leaderboard-row leaderboard-row-head">
              <span>Место</span>
              <span>Пользователь</span>
              <span>Уровень</span>
              <span>XP</span>
              <span>Принято</span>
            </div>

            {items.map((row) => {
              const isCurrentUser = row.nickname === currentUser?.nickname;
              const isTop3 = row.rank <= 3;
              const displayName = row.firstName || row.lastName ? `${row.firstName} ${row.lastName}`.trim() : `@${row.nickname}`;

              return (
                <div key={`${row.rank}-${row.nickname}`} className={`leaderboard-row ${isCurrentUser ? "is-me" : ""}`}>
                  <span className="rank-cell">
                    {isTop3 ? <Medal size={14} strokeWidth={1.9} /> : null}
                    #{row.rank}
                  </span>
                  <strong>{displayName}</strong>
                  <span>L{row.level}</span>
                  <span>{row.xp}</span>
                  <span>—</span>
                </div>
              );
            })}

            {!loading && items.length === 0 && (
              <div className="empty-state empty-state-centered">
                <h3>Рейтинг пока пуст</h3>
                <p>После первых отправок здесь появится таблица участников.</p>
              </div>
            )}
          </div>
        )}
      </section>

      {myRow && (
        <section className="surface">
          <div className="inline-metrics">
            <span className="badge badge-blue">Ваше место: #{myRow.rank}</span>
            <span className="badge badge-neutral">Уровень L{myRow.level}</span>
            <span className="badge badge-purple">{myRow.xp} XP</span>
          </div>
        </section>
      )}
    </div>
  );
}
