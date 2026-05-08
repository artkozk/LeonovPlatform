import { ArrowRight, BookOpenText, Code2, FileText, Gauge, TimerReset, TrendingUp } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getCourse, getLesson, listCourses, submissionHistory } from "../api/client";
import { useAuthStore } from "../store/auth";

type SubmissionItem = {
  id: string;
  taskId?: string;
  taskTitle: string;
  score: number;
  status: string;
};

type CurrentCourseCard = {
  lessonId: string;
  lessonTitle: string;
  moduleTitle: string;
  nextStepTitle: string;
  stepCurrent: number;
  stepTotal: number;
  progressPercent: number;
};

function submissionStatusLabel(status?: string) {
  const value = String(status ?? "").trim().toLowerCase();
  if (value === "accepted") return "Принято";
  if (value === "queued") return "В очереди";
  if (value === "wrong_answer") return "Нужна правка";
  if (value === "compile_error") return "Ошибка компиляции";
  if (value === "runtime_error") return "Ошибка выполнения";
  if (value === "time_limit") return "Лимит времени";
  if (value === "failed") return "Сбой проверки";
  return "Неизвестно";
}

function submissionStatusClass(status?: string) {
  const value = String(status ?? "").trim().toLowerCase();
  if (value === "accepted") return "badge badge-success";
  if (value === "queued") return "badge badge-warning";
  if (value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit" || value === "failed") {
    return "badge badge-error";
  }
  return "badge badge-neutral";
}

function buildFallbackCourse(): CurrentCourseCard {
  return {
    lessonId: "",
    lessonTitle: "Урок 1. Первый код на Python",
    moduleTitle: "Модуль 1. Базовый синтаксис",
    nextStepTitle: "Практика: Периметр прямоугольника",
    stepCurrent: 20,
    stepTotal: 25,
    progressPercent: 80,
  };
}

function parseReviewTopic(status?: string) {
  const value = String(status ?? "").trim().toLowerCase();
  if (value === "runtime_error") return "Преобразование типов";
  if (value === "compile_error") return "Синтаксис и отступы";
  if (value === "wrong_answer") return "Арифметические выражения";
  if (value === "time_limit") return "Оптимизация решения";
  if (value === "failed") return "Повторная отправка после сбоя";
  return "";
}

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const [history, setHistory] = useState<SubmissionItem[]>([]);
  const [currentCourse, setCurrentCourse] = useState<CurrentCourseCard>(buildFallbackCourse());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");

    Promise.allSettled([submissionHistory(), listCourses()])
      .then(async ([historyResult, coursesResult]) => {
        if (historyResult.status === "fulfilled") {
          setHistory((historyResult.value ?? []) as SubmissionItem[]);
        } else {
          setHistory([]);
          setError("Не удалось загрузить историю отправок.");
        }

        if (coursesResult.status !== "fulfilled") {
          setCurrentCourse(buildFallbackCourse());
          setError((prev) => (prev ? `${prev} Не удалось загрузить текущий курс.` : "Не удалось загрузить текущий курс."));
          return;
        }

        try {
          const courses = (coursesResult.value ?? []) as Array<{ id: string }>;
          const firstCourse = courses[0];
          if (!firstCourse?.id) {
            setCurrentCourse(buildFallbackCourse());
            return;
          }

          const courseData = await getCourse(String(firstCourse.id));
          const firstLesson = Array.isArray(courseData?.lessons) ? courseData.lessons[0] : null;
          if (!firstLesson?.id) {
            setCurrentCourse(buildFallbackCourse());
            return;
          }

          const lessonData = await getLesson(String(firstLesson.id));
          const blocks = Array.isArray(lessonData?.blocks)
            ? lessonData.blocks
                .map((block: any, index: number) => ({
                  id: String(block.id ?? ""),
                  title: String(block.title ?? `Шаг ${index + 1}`),
                }))
                .filter((block: { id: string }) => block.id.length > 0)
            : [];

          const progressKey = `lc_lesson_progress_${String(firstLesson.id)}`;
          let completed: Record<string, boolean> = {};
          try {
            const raw = localStorage.getItem(progressKey);
            if (raw) {
              const parsed = JSON.parse(raw);
              if (parsed && typeof parsed === "object") {
                completed = parsed as Record<string, boolean>;
              }
            }
          } catch {
            completed = {};
          }

          const stepTotal = blocks.length || 25;
          const completedCount = blocks.filter((block: { id: string }) => completed[block.id]).length;
          const nextBlock = blocks.find((block: { id: string }) => !completed[block.id]);
          const stepCurrent = Math.min(stepTotal, Math.max(1, completedCount + 1));
          const progressPercent = stepTotal > 0 ? Math.round((completedCount / stepTotal) * 100) : 0;

          setCurrentCourse({
            lessonId: String(firstLesson.id),
            lessonTitle: String(firstLesson.title ?? "Урок"),
            moduleTitle: String(firstLesson.moduleTitle ?? "Модуль"),
            nextStepTitle: String(nextBlock?.title ?? blocks[blocks.length - 1]?.title ?? "Продолжить урок"),
            stepCurrent,
            stepTotal,
            progressPercent,
          });
        } catch {
          setCurrentCourse(buildFallbackCourse());
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const level = Number(user?.level ?? 1);
  const xp = Number(user?.xp ?? 0);
  const streak = Number(user?.streak ?? 0);

  const xpInLevel = useMemo(() => {
    const remainder = xp % 100;
    return remainder === 0 && xp > 0 ? 100 : remainder;
  }, [xp]);

  const xpToNextLevel = useMemo(() => {
    if (xpInLevel === 100) return 100;
    return 100 - xpInLevel;
  }, [xpInLevel]);

  const levelTarget = level + 1;

  const reviewTopics = useMemo(() => {
    const map = new Map<string, number>();
    history.forEach((item) => {
      const topic = parseReviewTopic(item.status);
      if (!topic) return;
      map.set(topic, (map.get(topic) ?? 0) + 1);
    });
    return Array.from(map.entries())
      .map(([topic, count]) => ({ topic, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 4);
  }, [history]);

  return (
    <div className="dashboard-page page-stack">
      <section className="surface current-course-card">
        <div className="current-course-main">
          <span className="section-kicker">Текущий курс</span>
          <h1>{currentCourse.lessonTitle}</h1>
          <p>{currentCourse.moduleTitle}</p>

          <div className="next-step-block">
            <span>Следующий шаг</span>
            {currentCourse.lessonId ? (
              <Link to={`/lessons/${currentCourse.lessonId}`} className="next-step-link">
                <Code2 size={16} strokeWidth={1.9} />
                <span>{currentCourse.nextStepTitle}</span>
                <ArrowRight size={16} strokeWidth={2} />
              </Link>
            ) : (
              <div className="next-step-link next-step-link-static">
                <Code2 size={16} strokeWidth={1.9} />
                <span>{currentCourse.nextStepTitle}</span>
                <ArrowRight size={16} strokeWidth={2} />
              </div>
            )}
          </div>
        </div>

        <div className="current-course-progress">
          <span className="badge badge-blue">Шаг {currentCourse.stepCurrent} из {currentCourse.stepTotal}</span>
          <strong>Прогресс урока {currentCourse.progressPercent}%</strong>
          <div className="progress-track" aria-hidden="true">
            <span style={{ width: `${currentCourse.progressPercent}%` }} />
          </div>
          <p>Осталось {Math.max(0, currentCourse.stepTotal - currentCourse.stepCurrent)} шагов до завершения урока</p>
        </div>
      </section>

      <section className="stats-grid">
        <article className="surface compact-stat-card">
          <span className="stat-icon"><Gauge size={16} strokeWidth={1.9} /></span>
          <p>Уровень</p>
          <strong>{level}</strong>
        </article>
        <article className="surface compact-stat-card">
          <span className="stat-icon"><TrendingUp size={16} strokeWidth={1.9} /></span>
          <p>XP</p>
          <strong>{xpInLevel} / 100</strong>
        </article>
        <article className="surface compact-stat-card">
          <span className="stat-icon"><TimerReset size={16} strokeWidth={1.9} /></span>
          <p>Серия</p>
          <strong>{streak} дней</strong>
        </article>
        <article className="surface compact-stat-card">
          <span className="stat-icon"><BookOpenText size={16} strokeWidth={1.9} /></span>
          <p>До L{levelTarget}</p>
          <strong>{xpToNextLevel} XP</strong>
        </article>
      </section>

      {error && <div className="status-box status-box-error">{error}</div>}

      <section className="dashboard-main-grid">
        <article className="surface">
          <div className="section-head">
            <div>
              <h2>Последние отправки</h2>
            </div>
            <Link to="/checks" className="text-link">Все проверки</Link>
          </div>

          {loading ? (
            <div className="skeleton-list">
              <span className="skeleton-line" />
              <span className="skeleton-line" />
              <span className="skeleton-line" />
            </div>
          ) : null}

          {!loading && history.length === 0 ? (
            <div className="empty-state empty-state-centered">
              <h3>Отправок пока нет</h3>
              <p>После первой проверки здесь появятся последние попытки.</p>
            </div>
          ) : null}

          {!loading && history.length > 0 ? (
            <div className="clean-list">
              {history.slice(0, 5).map((item) => (
                <Link
                  key={item.id}
                  to={item.taskId ? `/tasks/${item.taskId}?submissionId=${item.id}` : "/tasks"}
                  className="clean-list-row clean-list-link"
                  aria-label={`Открыть задачу: ${item.taskTitle}`}
                >
                  <div className="clean-list-main">
                    <span className="clean-list-icon" aria-hidden="true">
                      <FileText size={15} strokeWidth={1.9} />
                    </span>
                    <div>
                      <strong>{item.taskTitle}</strong>
                      <p>Score {item.score}</p>
                    </div>
                  </div>
                  <span className={submissionStatusClass(item.status)}>{submissionStatusLabel(item.status)}</span>
                </Link>
              ))}
            </div>
          ) : null}
        </article>

        <article className="surface">
          <div className="section-head">
            <div>
              <h2>Что разобрать</h2>
            </div>
          </div>

          {reviewTopics.length === 0 ? (
            <div className="empty-state empty-state-centered">
              <span className="empty-state-icon" aria-hidden="true">
                <BookOpenText size={20} strokeWidth={1.8} />
              </span>
              <h3>Ошибок пока нет</h3>
              <p>После первых проверок здесь появятся темы для повторения.</p>
            </div>
          ) : (
            <div className="clean-list">
              {reviewTopics.map((topic) => (
                <Link key={topic.topic} to="/courses" className="clean-list-row clean-list-link">
                  <div className="clean-list-main">
                    <span className="topic-dot" aria-hidden="true" />
                    <div>
                      <strong>{topic.topic}</strong>
                      <p>{topic.count} ошибок</p>
                    </div>
                  </div>
                  <ArrowRight size={16} strokeWidth={2} />
                </Link>
              ))}
            </div>
          )}
        </article>
      </section>
    </div>
  );
}
