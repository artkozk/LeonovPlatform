import { Check, ChevronDown, ChevronRight, FileCode2 } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { getCourse, getCourseTasksCatalog, listCourses, submissionHistory } from "../api/client";

type CourseOption = {
  id: string;
  title: string;
};

type TaskCatalogItem = {
  id: string;
  title: string;
  difficulty: number;
  xpReward: number;
  topic: string;
  language: string;
  lessonId: string;
  lessonTitle: string;
  moduleTitle: string;
};

type SubmissionItem = {
  taskId?: string;
  taskTitle: string;
  status: string;
};

type TaskTab = "all" | "practice" | "tests" | "control" | "queued" | "done";

function classifyTaskType(task: TaskCatalogItem): "practice" | "tests" | "control" {
  const text = `${task.title} ${task.topic}`.toLowerCase();
  if (text.includes("контроль") || text.includes("экзам")) return "control";
  if (text.includes("тест") || text.includes("quiz")) return "tests";
  return "practice";
}

function normalizedStatus(raw?: string) {
  const value = String(raw ?? "").trim().toLowerCase();
  if (value === "accepted") return "accepted";
  if (value === "queued") return "queued";
  if (value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit" || value === "failed") {
    return "needs_fix";
  }
  return "idle";
}

function statusText(status: string) {
  if (status === "accepted") return "Принято";
  if (status === "queued") return "В очереди";
  if (status === "needs_fix") return "Нужна правка";
  if (status === "in_progress") return "В процессе";
  return "Не начато";
}

function statusClass(status: string) {
  if (status === "accepted") return "badge badge-success";
  if (status === "queued") return "badge badge-warning";
  if (status === "needs_fix") return "badge badge-red";
  if (status === "in_progress") return "badge badge-blue";
  return "badge badge-neutral";
}

function submissionTaskKey(taskId?: string, taskTitle?: string) {
  const normalizedTaskId = String(taskId ?? "").trim();
  if (normalizedTaskId) return `id:${normalizedTaskId}`;
  const normalizedTitle = String(taskTitle ?? "").trim().toLowerCase();
  if (normalizedTitle) return `title:${normalizedTitle}`;
  return "";
}

export function TasksPage() {
  const [courses, setCourses] = useState<CourseOption[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [tasks, setTasks] = useState<TaskCatalogItem[]>([]);
  const [history, setHistory] = useState<SubmissionItem[]>([]);

  const [query, setQuery] = useState("");
  const [tab, setTab] = useState<TaskTab>("all");
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [loadingTasks, setLoadingTasks] = useState(false);
  const [error, setError] = useState("");
  const [courseSelectOpen, setCourseSelectOpen] = useState(false);
  const courseSelectRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setLoadingCourses(true);
    listCourses()
      .then((items) => {
        const normalized = (items ?? []).map((item) => ({
          id: String(item.id),
          title: String(item.title),
        }));
        setCourses(normalized);
        if (normalized[0]) {
          setSelectedCourseId(normalized[0].id);
        }
      })
      .catch((e: any) => {
        setError(e?.response?.data?.error ?? "Не удалось загрузить список курсов.");
      })
      .finally(() => {
        setLoadingCourses(false);
      });

    submissionHistory()
      .then((items) => {
        setHistory((items ?? []) as SubmissionItem[]);
      })
      .catch(() => {
        setHistory([]);
      });
  }, []);

  useEffect(() => {
    if (!selectedCourseId) return;

    async function loadTasksForCourse() {
      setLoadingTasks(true);
      setError("");
      try {
        const [courseData, catalogData] = await Promise.all([
          getCourse(selectedCourseId),
          getCourseTasksCatalog(selectedCourseId),
        ]);
        if (!courseData?.course?.id) {
          throw new Error("course not found");
        }

        const catalogItems = Array.isArray(catalogData?.items) ? catalogData.items : [];
        const nextTasks: TaskCatalogItem[] = catalogItems
          .map((task: any) => ({
            id: String(task.taskId ?? task.id ?? ""),
            title: String(task.title ?? "Без названия"),
            difficulty: Number(task.difficulty ?? 1),
            xpReward: Number(task.xp ?? task.xpReward ?? 0),
            topic: String(task.topic ?? "General"),
            language: String(task.language ?? "python"),
            lessonId: String(task.lessonId ?? ""),
            lessonTitle: String(task.lessonTitle ?? "Урок"),
            moduleTitle: String(task.moduleTitle ?? "Модуль"),
          }))
          .filter((task) => task.id);

        setTasks(nextTasks);
      } catch (e: any) {
        setTasks([]);
        setError(e?.response?.data?.error ?? "Не удалось загрузить каталог задач.");
      } finally {
        setLoadingTasks(false);
      }
    }

    void loadTasksForCourse();
  }, [selectedCourseId]);

  useEffect(() => {
    if (!courseSelectOpen) return;

    function handleOutsideClick(event: MouseEvent) {
      const target = event.target as Node | null;
      if (!target) return;
      if (courseSelectRef.current?.contains(target)) return;
      setCourseSelectOpen(false);
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setCourseSelectOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [courseSelectOpen]);

  const taskStatusMap = useMemo(() => {
    const map = new Map<string, string>();
    history.forEach((entry) => {
      const key = submissionTaskKey(entry.taskId, entry.taskTitle);
      if (!key) return;
      if (!map.has(key)) {
        map.set(key, normalizedStatus(entry.status));
      }
    });
    return map;
  }, [history]);

  const filteredTasks = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return tasks.filter((task) => {
      const taskType = classifyTaskType(task);
      const taskKey = submissionTaskKey(task.id, task.title);
      const fallbackKey = submissionTaskKey(undefined, task.title);
      const rawStatus = taskStatusMap.get(taskKey) ?? taskStatusMap.get(fallbackKey) ?? "idle";

      const queryMatch =
        !normalizedQuery ||
        task.title.toLowerCase().includes(normalizedQuery) ||
        task.topic.toLowerCase().includes(normalizedQuery) ||
        task.lessonTitle.toLowerCase().includes(normalizedQuery);

      const tabMatch =
        tab === "all" ||
        (tab === "practice" && taskType === "practice") ||
        (tab === "tests" && taskType === "tests") ||
        (tab === "control" && taskType === "control") ||
        (tab === "queued" && rawStatus === "queued") ||
        (tab === "done" && rawStatus === "accepted");

      return queryMatch && tabMatch;
    });
  }, [query, tab, tasks, taskStatusMap]);

  const selectedCourseTitle = useMemo(
    () => courses.find((course) => course.id === selectedCourseId)?.title ?? "Курс не выбран",
    [courses, selectedCourseId]
  );
  const courseSelectDisabled = loadingCourses || courses.length === 0;

  return (
    <div className="tasks-page page-stack">
      <section className="surface">
        <div className="page-title-block">
          <h1>Задачи</h1>
          <p>Практика, тесты и контрольные задания.</p>
        </div>

        <div className="tasks-toolbar">
          <label className="field">
            <span>Курс</span>
            <div className="tasks-course-select" ref={courseSelectRef}>
              <button
                type="button"
                className={`tasks-course-select-trigger ${courseSelectOpen ? "open" : ""}`}
                aria-label="Выбор курса"
                aria-expanded={courseSelectOpen}
                disabled={courseSelectDisabled}
                onClick={() => setCourseSelectOpen((prev) => !prev)}
              >
                <span>{selectedCourseTitle}</span>
                <ChevronDown size={16} strokeWidth={2} aria-hidden="true" />
              </button>

              {!courseSelectDisabled && courseSelectOpen && (
                <div className="tasks-course-select-menu" role="listbox" aria-label="Список курсов">
                  {courses.map((course) => {
                    const selected = course.id === selectedCourseId;
                    return (
                      <button
                        key={course.id}
                        type="button"
                        role="option"
                        aria-selected={selected}
                        className={`tasks-course-select-option ${selected ? "selected" : ""}`}
                        onClick={() => {
                          setSelectedCourseId(course.id);
                          setCourseSelectOpen(false);
                        }}
                      >
                        <span>{course.title}</span>
                        {selected ? <Check size={14} strokeWidth={2.2} aria-hidden="true" /> : null}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </label>

          <label className="field field-grow">
            <span>Поиск</span>
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Название, тема или урок"
            />
          </label>
        </div>

        <div className="checks-toolbar tasks-filter-tabs" role="tablist" aria-label="Фильтры задач">
          <button type="button" className={`filter-chip ${tab === "all" ? "active" : ""}`} onClick={() => setTab("all")}>Все</button>
          <button type="button" className={`filter-chip ${tab === "practice" ? "active" : ""}`} onClick={() => setTab("practice")}>Практика</button>
          <button type="button" className={`filter-chip ${tab === "tests" ? "active" : ""}`} onClick={() => setTab("tests")}>Тесты</button>
          <button type="button" className={`filter-chip ${tab === "control" ? "active" : ""}`} onClick={() => setTab("control")}>Контрольные</button>
          <button type="button" className={`filter-chip ${tab === "queued" ? "active" : ""}`} onClick={() => setTab("queued")}>В очереди</button>
          <button type="button" className={`filter-chip ${tab === "done" ? "active" : ""}`} onClick={() => setTab("done")}>Завершённые</button>
        </div>
      </section>

      {error && <div className="status-box status-box-error">{error}</div>}

      <section className="surface task-list-card">
        {loadingTasks ? (
          <div className="skeleton-list">
            <span className="skeleton-line" />
            <span className="skeleton-line" />
            <span className="skeleton-line" />
          </div>
        ) : (
          <>
            <div className="task-list-head">
              <span>Задача</span>
              <span>Тип</span>
              <span>Сложность</span>
              <span>XP</span>
              <span>Статус</span>
              <span aria-hidden="true" />
            </div>

            {filteredTasks.length === 0 && (
              <div className="empty-state empty-state-centered">
                <h3>Задачи не найдены</h3>
                <p>Измените фильтры или выберите другой курс.</p>
              </div>
            )}

            {filteredTasks.map((task) => {
              const taskType = classifyTaskType(task);
              const taskKey = submissionTaskKey(task.id, task.title);
              const fallbackKey = submissionTaskKey(undefined, task.title);
              const rawStatus = taskStatusMap.get(taskKey) ?? taskStatusMap.get(fallbackKey) ?? "idle";
              const textStatus = rawStatus === "idle" && taskType !== "practice" ? "Не начато" : statusText(rawStatus);
              const visualStatus = rawStatus === "idle" && taskType !== "practice" ? "idle" : rawStatus;

              return (
                <Link key={task.id} to={`/tasks/${task.id}`} className="task-list-row">
                  <div className="task-list-main">
                    <span className="task-list-icon" aria-hidden="true">
                      <FileCode2 size={16} strokeWidth={1.9} />
                    </span>
                    <div>
                      <strong>{task.title}</strong>
                      <p>{task.moduleTitle} · {task.lessonTitle}</p>
                    </div>
                  </div>
                  <span className="badge badge-neutral">{taskType === "practice" ? "Практика" : taskType === "tests" ? "Тест" : "Контрольная"}</span>
                  <span className="task-list-cell">{task.difficulty}</span>
                  <span className="task-list-cell">{task.xpReward}</span>
                  <span className={statusClass(visualStatus)}>{textStatus}</span>
                  <span className="task-list-chevron" aria-hidden="true"><ChevronRight size={16} strokeWidth={2.1} /></span>
                </Link>
              );
            })}
          </>
        )}
      </section>
    </div>
  );
}
