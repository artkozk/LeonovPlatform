import { ChevronRight, FileCode2, Inbox } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { submissionHistory } from "../api/client";

type SubmissionItem = {
  id: string;
  taskId?: string;
  taskTitle: string;
  score: number;
  status: string;
  createdAt?: string;
};

type CheckFilter = "all" | "queued" | "accepted" | "needs_fix";

function normalizeStatus(value?: string) {
  return String(value ?? "").trim().toLowerCase();
}

function statusLabel(status?: string) {
  const value = normalizeStatus(status);
  if (value === "accepted") return "Принято";
  if (value === "queued") return "В очереди";
  if (value === "failed") return "Сбой проверки";
  return "Нужна правка";
}

function statusClass(status?: string) {
  const value = normalizeStatus(status);
  if (value === "accepted") return "badge badge-success";
  if (value === "queued") return "badge badge-warning";
  if (value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit" || value === "failed") {
    return "badge badge-error";
  }
  return "badge badge-neutral";
}

function isNeedsFix(status?: string) {
  const value = normalizeStatus(status);
  return value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit" || value === "failed";
}

function shortResult(status?: string) {
  const value = normalizeStatus(status);
  if (value === "accepted") return "Решение принято автопроверкой";
  if (value === "queued") return "Отправка ожидает выполнения";
  if (value === "compile_error") return "Найдены ошибки компиляции";
  if (value === "runtime_error") return "Ошибка во время выполнения";
  if (value === "wrong_answer") return "Результат не совпал с эталоном";
  if (value === "time_limit") return "Превышен лимит времени";
  if (value === "failed") return "Сбой проверки на сервере, отправьте решение повторно";
  return "Требуется правка решения";
}

export function ChecksPage() {
  const [items, setItems] = useState<SubmissionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<CheckFilter>("all");

  useEffect(() => {
    setLoading(true);
    setError("");
    submissionHistory()
      .then((history) => {
        setItems((history ?? []) as SubmissionItem[]);
      })
      .catch((e: any) => {
        setItems([]);
        setError(e?.response?.data?.error ?? "Не удалось загрузить историю отправок.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const visibleItems = useMemo(() => {
    if (filter === "all") return items;
    if (filter === "queued") return items.filter((item) => normalizeStatus(item.status) === "queued");
    if (filter === "accepted") return items.filter((item) => normalizeStatus(item.status) === "accepted");
    return items.filter((item) => isNeedsFix(item.status));
  }, [items, filter]);

  return (
    <div className="checks-page page-stack">
      <section className="surface">
        <div className="page-title-block">
          <h1>Проверки</h1>
          <p>История отправок и статусы автопроверки.</p>
        </div>

        <div className="checks-toolbar" role="tablist" aria-label="Фильтры проверок">
          <button type="button" className={`filter-chip ${filter === "all" ? "active" : ""}`} onClick={() => setFilter("all")}>Все</button>
          <button type="button" className={`filter-chip ${filter === "queued" ? "active" : ""}`} onClick={() => setFilter("queued")}>В очереди</button>
          <button type="button" className={`filter-chip ${filter === "accepted" ? "active" : ""}`} onClick={() => setFilter("accepted")}>Принято</button>
          <button type="button" className={`filter-chip ${filter === "needs_fix" ? "active" : ""}`} onClick={() => setFilter("needs_fix")}>Нужна правка</button>
        </div>
      </section>

      {error && <div className="status-box status-box-error">{error}</div>}

      <section className="surface checks-history-card">
        {loading && (
          <div className="skeleton-list">
            <span className="skeleton-line" />
            <span className="skeleton-line" />
            <span className="skeleton-line" />
          </div>
        )}

        {!loading && visibleItems.length === 0 && (
          <div className="empty-state empty-state-centered">
            <span className="empty-state-icon" aria-hidden="true">
              <Inbox size={20} strokeWidth={1.9} />
            </span>
            <h3>Отправок пока нет</h3>
            <p>После отправки решения здесь появится история проверок.</p>
          </div>
        )}

        {!loading && visibleItems.length > 0 && (
          <div className="checks-history-list">
            {visibleItems.map((item) => (
              <div key={item.id} className="checks-history-row">
                <div className="checks-main">
                  <span className="checks-task-icon" aria-hidden="true">
                    <FileCode2 size={16} strokeWidth={1.9} />
                  </span>
                  <div>
                    <strong>{item.taskTitle}</strong>
                    <p>{shortResult(item.status)}</p>
                  </div>
                </div>

                <div className="checks-meta">
                  <span className="checks-score">Score {item.score}</span>
                  <span className={statusClass(item.status)}>{statusLabel(item.status)}</span>
                  {item.createdAt ? <span className="checks-date">{new Date(item.createdAt).toLocaleString("ru-RU")}</span> : null}
                  <ChevronRight size={16} strokeWidth={2} aria-hidden="true" />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
