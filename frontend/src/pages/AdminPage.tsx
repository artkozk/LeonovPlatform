import { useEffect, useState } from "react";
import { adminExportCSV, adminMetrics } from "../api/client";

type AdminMetrics = {
  usersTotal: number;
  activePaidSubscriptions: number;
  conversionToPaidPercent: number;
};

export function AdminPage() {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setMsg("");
    try {
      const data = await adminMetrics();
      setMetrics(data);
    } catch (e: any) {
      setMsg(e?.response?.data?.error ?? "Не удалось загрузить метрики.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function exportCSV() {
    setLoading(true);
    try {
      const blob = await adminExportCSV();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "metrics.csv";
      a.click();
      URL.revokeObjectURL(url);
      setMsg("CSV-экспорт сформирован.");
    } catch (e: any) {
      setMsg(e?.response?.data?.error ?? "Не удалось сформировать CSV.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="admin-page page-stack">
      <section className="surface hero-surface">
        <div className="hero-copy">
          <span className="section-kicker">Admin analytics</span>
          <h1>Административная аналитика</h1>
          <p>Мониторинг конверсии и активности подписок в реальном времени.</p>
        </div>
        <div className="hero-actions">
          <button type="button" className="btn btn-secondary" onClick={load} disabled={loading}>Обновить</button>
          <button type="button" className="btn btn-primary" onClick={exportCSV} disabled={loading}>Экспорт CSV</button>
        </div>
      </section>

      {!metrics ? (
        <section className="surface empty-state">
          <h3>Метрики пока недоступны</h3>
          <p>{msg || "Повторите попытку позже."}</p>
          <button type="button" className="btn btn-primary" onClick={load} disabled={loading}>
            {loading ? "Загрузка..." : "Повторить"}
          </button>
        </section>
      ) : (
        <section className="kpi-grid">
          <article className="surface kpi-card">
            <span>Пользователи</span>
            <strong>{metrics.usersTotal}</strong>
            <p>Всего аккаунтов</p>
          </article>
          <article className="surface kpi-card">
            <span>Платные подписки</span>
            <strong>{metrics.activePaidSubscriptions}</strong>
            <p>Текущие платные тарифы</p>
          </article>
          <article className="surface kpi-card">
            <span>Конверсия в оплату</span>
            <strong>{metrics.conversionToPaidPercent.toFixed(2)}%</strong>
            <p>Отношение paid к активным пользователям</p>
          </article>
        </section>
      )}

      {msg && <div className="status-box">{msg}</div>}
    </div>
  );
}
