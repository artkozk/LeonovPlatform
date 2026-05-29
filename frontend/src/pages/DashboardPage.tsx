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
  lessonId?: string;
  lessonTitle?: string;
  courseId?: string;
  courseTitle?: string;
};

type CurrentCourseCard = {
  lessonId: string;
  lessonTitle: string;
  moduleTitle: string;
  nextStepTitle: string;
  stepCurrent: number;
  stepTotal: number;
  completedSteps: number;
  progressPercent: number;
};

function submissionStatusLabel(status?: string) {
  const value = String(status ?? "").trim().toLowerCase();
  if (value === "accepted") return "Принято";
  if (value === "queued") return "В очереди";
  if (value === "processing") return "Проверяется";
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
  if (value === "queued" || value === "processing") return "badge badge-warning";
  if (value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit" || value === "failed") {
    return "badge badge-error";
  }
  return "badge badge-neutral";
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

function dashboardErrorText(raw?: string, fallback = "Не удалось загрузить данные."): string {
  const text = String(raw ?? "").trim().toLowerCase();
  if (!text) return fallback;
  if (text.includes("active subscription required for course access") || text.includes("subscription_required")) {
    return "Для доступа к курсам нужна активная подписка. Перейдите в раздел «Подписка».";
  }
  if (text.includes("current plan does not include this course") || text.includes("course_not_in_plan")) {
    return "Текущий тариф не включает этот курс. Выберите более высокий тариф.";
  }
  if (text.includes("unauthorized")) {
    return "Сессия истекла. Выполните вход заново.";
  }
  return raw ?? fallback;
}

function extractCompletedBlockIds(payload: any): string[] {
  const out = new Set<string>();

  if (Array.isArray(payload?.progress?.completedBlockIds)) {
    payload.progress.completedBlockIds.forEach((item: unknown) => {
      const id = String(item ?? "").trim();
      if (id) out.add(id);
    });
  }

  if (Array.isArray(payload?.blocks)) {
    payload.blocks.forEach((block: any) => {
      const id = String(block?.id ?? "").trim();
      if (!id) return;
      if (block?.completed) out.add(id);
    });
  }

  return Array.from(out);
}

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const [history, setHistory] = useState<SubmissionItem[]>([]);
  const [currentCourse, setCurrentCourse] = useState<CurrentCourseCard | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      setError("");
      setCurrentCourse(null);

      const [historyResult, coursesResult] = await Promise.allSettled([submissionHistory(), listCourses()]);
      if (cancelled) return;

      let nextHistory: SubmissionItem[] = [];
      if (historyResult.status === "fulfilled") {
        const raw = Array.isArray(historyResult.value) ? historyResult.value : [];
        nextHistory = raw.map((item: any) => ({
          id: String(item?.id ?? ""),
          taskId: item?.taskId ? String(item.taskId) : undefined,
          taskTitle: String(item?.taskTitle ?? "Задача"),
          score: Number(item?.score ?? 0),
          status: String(item?.status ?? ""),
          lessonId: item?.lessonId ? String(item.lessonId) : undefined,
          lessonTitle: item?.lessonTitle ? String(item.lessonTitle) : undefined,
          courseId: item?.courseId ? String(item.courseId) : undefined,
          courseTitle: item?.courseTitle ? String(item.courseTitle) : undefined,
        }));
      } else {
        setError(dashboardErrorText(historyResult.reason?.response?.data?.error, "Не удалось загрузить историю отправок."));
      }
      setHistory(nextHistory);

      let contextCourseId = "";
      let contextLessonId = "";
      for (const item of nextHistory) {
        if (item.courseId && item.lessonId) {
          contextCourseId = item.courseId;
          contextLessonId = item.lessonId;
          break;
        }
      }

      if (!contextCourseId) {
        if (coursesResult.status === "rejected") {
          setError((prev) => {
            const message = dashboardErrorText(coursesResult.reason?.response?.data?.error, "Не удалось загрузить курсы.");
            return prev ? `${prev} ${message}` : message;
          });
        }
        setLoading(false);
        return;
      }

      try {
        const courseData = await getCourse(contextCourseId);
        if (cancelled) return;

        const lessons = Array.isArray(courseData?.lessons) ? courseData.lessons : [];
        const selectedLesson =
          lessons.find((lesson: any) => String(lesson?.id ?? "") === contextLessonId) ??
          lessons.find((lesson: any) => Number(lesson?.progressPercent ?? 0) < 100) ??
          lessons[0];

        if (!selectedLesson?.id) {
          setLoading(false);
          return;
        }

        const lessonData = await getLesson(String(selectedLesson.id));
        if (cancelled) return;

        const blocks = Array.isArray(lessonData?.blocks)
          ? lessonData.blocks
              .map((block: any, index: number) => ({
                id: String(block?.id ?? ""),
                title: String(block?.title ?? `Шаг ${index + 1}`),
              }))
              .filter((block: { id: string }) => block.id.length > 0)
          : [];

        const completedBlockIds = new Set(extractCompletedBlockIds(lessonData));
        const totalSteps = blocks.length;
        const completedSteps = Number.isFinite(Number(lessonData?.progress?.completedBlocks))
          ? Number(lessonData?.progress?.completedBlocks)
          : blocks.filter((block: { id: string }) => completedBlockIds.has(block.id)).length;
        const safeCompletedSteps = Math.max(0, Math.min(completedSteps, totalSteps));
        const progressPercent = Number.isFinite(Number(lessonData?.progress?.progressPercent))
          ? Math.max(0, Math.min(100, Number(lessonData?.progress?.progressPercent)))
          : totalSteps > 0
            ? Math.round((safeCompletedSteps / totalSteps) * 100)
            : 0;

        const firstIncompleteIndex = blocks.findIndex((block: { id: string }) => !completedBlockIds.has(block.id));
        const stepCurrent =
          totalSteps <= 0
            ? 0
            : firstIncompleteIndex >= 0
              ? firstIncompleteIndex + 1
              : totalSteps;
        const nextStepTitle =
          blocks[firstIncompleteIndex >= 0 ? firstIncompleteIndex : Math.max(0, blocks.length - 1)]?.title ??
          "Продолжить урок";

        setCurrentCourse({
          lessonId: String(selectedLesson.id),
          lessonTitle: String(selectedLesson.title ?? "Урок"),
          moduleTitle: String(selectedLesson.moduleTitle ?? "Модуль"),
          nextStepTitle,
          stepCurrent,
          stepTotal: totalSteps,
          completedSteps: safeCompletedSteps,
          progressPercent,
        });
      } catch (error: any) {
        setCurrentCourse(null);
        setError((prev) => {
          const message = dashboardErrorText(error?.response?.data?.error, "Не удалось загрузить текущий контекст обучения.");
          return prev ? `${prev} ${message}` : message;
        });
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDashboard();
    return () => {
      cancelled = true;
    };
  }, [user?.id]);

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
      {currentCourse ? (
        <section className="surface current-course-card">
          <div className="current-course-main">
            <span className="section-kicker">Текущий курс</span>
            <h1>{currentCourse.lessonTitle}</h1>
            <p>{currentCourse.moduleTitle}</p>

            <div className="next-step-block">
              <span>Следующий шаг</span>
              <Link to={`/lessons/${currentCourse.lessonId}`} className="next-step-link">
                <Code2 size={16} strokeWidth={1.9} />
                <span>{currentCourse.nextStepTitle}</span>
                <ArrowRight size={16} strokeWidth={2} />
              </Link>
            </div>
          </div>

          <div className="current-course-progress">
            <span className="badge badge-blue">Шаг {currentCourse.stepCurrent} из {currentCourse.stepTotal}</span>
            <strong>Прогресс урока {currentCourse.progressPercent}%</strong>
            <div className="progress-track" aria-hidden="true">
              <span style={{ width: `${currentCourse.progressPercent}%` }} />
            </div>
            <p>Осталось {Math.max(0, currentCourse.stepTotal - currentCourse.completedSteps)} шагов до завершения урока</p>
          </div>
        </section>
      ) : (
        <section className="surface current-course-card">
          <div className="current-course-main">
            <span className="section-kicker">Текущий курс</span>
            <h1>Контекст обучения не определён</h1>
            <p>Платформа не будет показывать фиктивный прогресс. Начните или продолжите курс, чтобы сформировать актуальный контекст.</p>
            <div className="next-step-block">
              <span>Действие</span>
              <Link to="/courses" className="next-step-link">
                <Code2 size={16} strokeWidth={1.9} />
                <span>Открыть обучение</span>
                <ArrowRight size={16} strokeWidth={2} />
              </Link>
            </div>
          </div>
          <div className="current-course-progress">
            <span className="badge badge-neutral">{loading ? "Загрузка" : "Нет данных"}</span>
            <strong>Прогресс урока не рассчитан</strong>
            <div className="progress-track" aria-hidden="true">
              <span style={{ width: "0%" }} />
            </div>
            <p>Когда появится реальный прогресс, блок обновится автоматически.</p>
          </div>
        </section>
      )}

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
