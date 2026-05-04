import { Check, ChevronRight, Plus } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { getCourse, listCourses } from "../api/client";
import { CourseTrackIcon } from "../components/icons/CourseTrackIcon";
import { resolveCourseIconKey } from "../lib/courseIconKey";
import { getCourseDisplayTitle, getCourseShortDescription, getCourseShortTitle } from "../lib/coursePresentation";

type CourseSummary = {
  id: string;
  slug: string;
  title: string;
  description: string;
  displayTitle?: string;
  shortTitle?: string;
  shortDescription?: string;
  direction?: string;
  track?: string;
  language?: string;
};

type CourseLesson = {
  id: string;
  title: string;
  moduleTitle: string;
  totalBlocks: number;
  completedBlocks: number;
  progressPercent: number;
};

type CourseDetail = {
  course: CourseSummary | null;
  lessons: CourseLesson[];
};

type CourseModule = {
  title: string;
  lessons: CourseLesson[];
  totalBlocks: number;
  completedBlocks: number;
  progressPercent: number;
};

type CoursesScreenCache = {
  courses: CourseSummary[];
  selectedCourse: CourseDetail | null;
  courseDetails: Record<string, CourseDetail>;
  savedAt: string;
};

const COURSES_SCREEN_CACHE_KEY = "lc_courses_screen_cache_v2_python_v10_hotfix";

function readLessonProgress(lessonId: string, totalBlocksHint: number) {
  const key = `lc_lesson_progress_${lessonId}`;
  let stored: Record<string, boolean> = {};

  try {
    const raw = localStorage.getItem(key);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") {
        stored = parsed as Record<string, boolean>;
      }
    }
  } catch {
    stored = {};
  }

  const totalBlocks = Number.isFinite(totalBlocksHint) && totalBlocksHint > 0 ? totalBlocksHint : 0;
  const completedFromStorage = Object.values(stored).reduce((count, done) => count + (done ? 1 : 0), 0);
  const completedBlocks = Math.min(completedFromStorage, totalBlocks || completedFromStorage);
  const progressPercent = totalBlocks > 0 ? Math.round((completedBlocks / totalBlocks) * 100) : 0;

  return {
    totalBlocks,
    completedBlocks: Math.min(completedBlocks, totalBlocks),
    progressPercent,
  };
}

function normalizeOptionalString(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  const normalized = value.trim();
  return normalized || undefined;
}

function calculateCourseProgressPercent(detail?: CourseDetail | null): number | null {
  if (!detail) return null;
  const totalBlocks = detail.lessons.reduce((sum, lesson) => sum + lesson.totalBlocks, 0);
  if (totalBlocks <= 0) return null;
  const completedBlocks = detail.lessons.reduce((sum, lesson) => sum + lesson.completedBlocks, 0);
  return Math.round((completedBlocks / totalBlocks) * 100);
}

function normalizeCourseSummary(value: unknown): CourseSummary | null {
  if (!value || typeof value !== "object") return null;
  const item = value as Record<string, unknown>;
  const idRaw = item.id;
  const id = typeof idRaw === "string" ? idRaw : typeof idRaw === "number" ? String(idRaw) : "";
  if (!id) return null;

  const titleRaw = item.title;
  const title = typeof titleRaw === "string" && titleRaw.trim() ? titleRaw : "Курс";
  const slug = typeof item.slug === "string" ? item.slug : "";
  const description = typeof item.description === "string" ? item.description : "Описание курса";

  return {
    id,
    slug,
    title,
    description,
    displayTitle: normalizeOptionalString(item.displayTitle ?? item.display_title),
    shortTitle: normalizeOptionalString(item.shortTitle ?? item.short_title),
    shortDescription: normalizeOptionalString(item.shortDescription ?? item.short_description),
    direction: normalizeOptionalString(item.direction),
    track: normalizeOptionalString(item.track),
    language: normalizeOptionalString(item.language),
  };
}

function normalizeCourseLesson(value: unknown): CourseLesson | null {
  if (!value || typeof value !== "object") return null;
  const item = value as Record<string, unknown>;
  const idRaw = item.id;
  const id = typeof idRaw === "string" ? idRaw : typeof idRaw === "number" ? String(idRaw) : "";
  if (!id) return null;

  const totalBlocksRaw = Number(item.totalBlocks ?? 0);
  const completedBlocksRaw = Number(item.completedBlocks ?? 0);
  const progressPercentRaw = Number(item.progressPercent ?? 0);
  const totalBlocks = Number.isFinite(totalBlocksRaw) && totalBlocksRaw > 0 ? totalBlocksRaw : 0;
  const completedBlocks = Number.isFinite(completedBlocksRaw) && completedBlocksRaw > 0 ? Math.min(completedBlocksRaw, totalBlocks || completedBlocksRaw) : 0;
  const progressPercent = Number.isFinite(progressPercentRaw)
    ? Math.min(Math.max(progressPercentRaw, 0), 100)
    : totalBlocks > 0
      ? Math.round((completedBlocks / totalBlocks) * 100)
      : 0;

  return {
    id,
    title: typeof item.title === "string" && item.title.trim() ? item.title : "Урок",
    moduleTitle: typeof item.moduleTitle === "string" && item.moduleTitle.trim() ? item.moduleTitle : "Модуль",
    totalBlocks,
    completedBlocks,
    progressPercent,
  };
}

function normalizeCourseDetail(value: unknown): CourseDetail | null {
  if (!value || typeof value !== "object") return null;
  const detail = value as Record<string, unknown>;
  const course = normalizeCourseSummary(detail.course);
  if (!course) return null;
  const lessonsRaw = Array.isArray(detail.lessons) ? detail.lessons : [];
  const lessons = lessonsRaw.map(normalizeCourseLesson).filter((lesson): lesson is CourseLesson => Boolean(lesson));
  return { course, lessons };
}

function readCoursesScreenCache(): CoursesScreenCache | null {
  try {
    const raw = localStorage.getItem(COURSES_SCREEN_CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as CoursesScreenCache;
    if (!parsed || typeof parsed !== "object") return null;

    const rawCourses = Array.isArray(parsed.courses) ? parsed.courses : [];
    const courses = rawCourses
      .map(normalizeCourseSummary)
      .filter((course): course is CourseSummary => Boolean(course));

    const selectedCourse = normalizeCourseDetail(parsed.selectedCourse);
    const courseDetails: Record<string, CourseDetail> = {};

    if (parsed.courseDetails && typeof parsed.courseDetails === "object") {
      const entries = Object.values(parsed.courseDetails as Record<string, unknown>);
      entries.forEach((entry) => {
        const detail = normalizeCourseDetail(entry);
        if (detail?.course?.id) {
          courseDetails[detail.course.id] = detail;
        }
      });
    }

    if (selectedCourse?.course?.id) {
      courseDetails[selectedCourse.course.id] = selectedCourse;
    }

    if (courses.length === 0 && !selectedCourse && Object.keys(courseDetails).length === 0) {
      return null;
    }

    return {
      courses,
      selectedCourse,
      courseDetails,
      savedAt: typeof parsed.savedAt === "string" ? parsed.savedAt : new Date().toISOString(),
    };
  } catch {
    return null;
  }
}

function writeCoursesScreenCache(payload: CoursesScreenCache) {
  try {
    localStorage.setItem(COURSES_SCREEN_CACHE_KEY, JSON.stringify(payload));
  } catch {
    // ignore localStorage quota/access errors
  }
}

export function CoursesPage() {
  const cachedScreen = useMemo(() => readCoursesScreenCache(), []);
  const [courses, setCourses] = useState<CourseSummary[]>(() => cachedScreen?.courses ?? []);
  const [selectedCourse, setSelectedCourse] = useState<CourseDetail | null>(() => cachedScreen?.selectedCourse ?? null);
  const [courseDetails, setCourseDetails] = useState<Record<string, CourseDetail>>(() => {
    const source = cachedScreen?.courseDetails ?? {};
    if (cachedScreen?.selectedCourse?.course?.id) {
      return {
        ...source,
        [cachedScreen.selectedCourse.course.id]: cachedScreen.selectedCourse,
      };
    }
    return source;
  });
  const [coursesLoading, setCoursesLoading] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState("");
  const [expandedModules, setExpandedModules] = useState<Record<string, boolean>>({});
  const initialCachedCourseCountRef = useRef(cachedScreen?.courses.length ?? 0);
  const initialSelectedCourseIDRef = useRef(cachedScreen?.selectedCourse?.course?.id ?? "");
  const selectedCourseRef = useRef<CourseDetail | null>(cachedScreen?.selectedCourse ?? null);
  const courseDetailsRef = useRef<Record<string, CourseDetail>>(cachedScreen?.courseDetails ?? {});

  useEffect(() => {
    selectedCourseRef.current = selectedCourse;
  }, [selectedCourse]);

  useEffect(() => {
    courseDetailsRef.current = courseDetails;
  }, [courseDetails]);

  useEffect(() => {
    if (courses.length === 0 && !selectedCourse && Object.keys(courseDetails).length === 0) return;
    writeCoursesScreenCache({
      courses,
      selectedCourse,
      courseDetails,
      savedAt: new Date().toISOString(),
    });
  }, [courses, selectedCourse, courseDetails]);

  const openCourse = useCallback(async (courseId: string, options?: { silent?: boolean }) => {
    const cachedDetail = courseDetailsRef.current[courseId];
    if (cachedDetail) {
      setSelectedCourse(cachedDetail);
    }
    const hasCurrentCachedDetail = Boolean(cachedDetail);
    setLoadingDetail(!options?.silent && !hasCurrentCachedDetail);
    setError("");

    try {
      const data = await getCourse(courseId);
      const normalized: CourseDetail = {
        course: normalizeCourseSummary(data?.course),
        lessons: Array.isArray(data?.lessons)
          ? data.lessons.map((lesson: any) => ({
              id: String(lesson.id),
              title: String(lesson.title ?? "Урок"),
              moduleTitle: String(lesson.moduleTitle ?? "Модуль"),
              totalBlocks: Number(lesson.blockCount ?? 0),
              completedBlocks: 0,
              progressPercent: 0,
            }))
          : [],
      };

      const lessonsWithProgress = normalized.lessons.map((lesson) => ({
        ...lesson,
        ...readLessonProgress(lesson.id, lesson.totalBlocks),
      }));

      const detail = { ...normalized, lessons: lessonsWithProgress };
      setSelectedCourse(detail);
      setCourseDetails((prev) => {
        const next = { ...prev, [courseId]: detail };
        courseDetailsRef.current = next;
        return next;
      });
      setExpandedModules({});
    } catch (e: any) {
      if (!selectedCourseRef.current) {
        setSelectedCourse(null);
      }
      setError(e?.response?.data?.error ?? "Не удалось открыть курс.");
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  useEffect(() => {
    setCoursesLoading(initialCachedCourseCountRef.current === 0);
    listCourses()
      .then((items) => {
        const normalized = (items ?? [])
          .map(normalizeCourseSummary)
          .filter((course): course is CourseSummary => Boolean(course));
        setCourses(normalized);

        const preferredCourseId = initialSelectedCourseIDRef.current;
        const nextCourseId = normalized.find((course) => course.id === preferredCourseId)?.id ?? normalized[0]?.id;
        if (nextCourseId) {
          void openCourse(nextCourseId, { silent: true });
        }
      })
      .catch((e: any) => {
        setError(e?.response?.data?.error ?? "Не удалось загрузить курсы.");
      })
      .finally(() => {
        setCoursesLoading(false);
      });
  }, [openCourse]);

  const lessons = useMemo(() => selectedCourse?.lessons ?? [], [selectedCourse]);

  const overall = useMemo(() => {
    const totalBlocks = lessons.reduce((sum, lesson) => sum + lesson.totalBlocks, 0);
    const completedBlocks = lessons.reduce((sum, lesson) => sum + lesson.completedBlocks, 0);
    const percent = totalBlocks > 0 ? Math.round((completedBlocks / totalBlocks) * 100) : 0;
    return { totalBlocks, completedBlocks, percent };
  }, [lessons]);

  const modules = useMemo<CourseModule[]>(() => {
    const map = new Map<string, CourseModule>();
    lessons.forEach((lesson) => {
      const moduleTitle = lesson.moduleTitle || "Модуль";
      const existing = map.get(moduleTitle);
      if (existing) {
        existing.lessons.push(lesson);
        existing.totalBlocks += lesson.totalBlocks;
        existing.completedBlocks += lesson.completedBlocks;
        existing.progressPercent = existing.totalBlocks > 0 ? Math.round((existing.completedBlocks / existing.totalBlocks) * 100) : 0;
        return;
      }
      map.set(moduleTitle, {
        title: moduleTitle,
        lessons: [lesson],
        totalBlocks: lesson.totalBlocks,
        completedBlocks: lesson.completedBlocks,
        progressPercent: lesson.totalBlocks > 0 ? Math.round((lesson.completedBlocks / lesson.totalBlocks) * 100) : 0,
      });
    });
    return Array.from(map.values());
  }, [lessons]);

  const nextLesson = useMemo(() => lessons.find((lesson) => lesson.progressPercent < 100) ?? lessons[0], [lessons]);
  const heroLessonText = nextLesson
    ? `${nextLesson.completedBlocks} из ${nextLesson.totalBlocks || 0} шагов`
    : `${overall.completedBlocks} из ${overall.totalBlocks || 0} шагов`;
  const selectedCourseIconKey = useMemo(
    () => resolveCourseIconKey(selectedCourse?.course ?? {}),
    [selectedCourse?.course]
  );
  const selectedCourseDisplayTitle = useMemo(
    () => getCourseDisplayTitle(selectedCourse?.course ?? {}),
    [selectedCourse?.course]
  );
  const selectedCourseShortDescription = useMemo(
    () => getCourseShortDescription(selectedCourse?.course ?? {}),
    [selectedCourse?.course]
  );
  const courseProgressByID = useMemo(() => {
    const result: Record<string, number> = {};
    Object.values(courseDetails).forEach((detail) => {
      const courseID = detail.course?.id;
      if (!courseID) return;
      const percent = calculateCourseProgressPercent(detail);
      if (typeof percent === "number") {
        result[courseID] = percent;
      }
    });
    return result;
  }, [courseDetails]);

  return (
    <div className="courses-page page-stack">
      <section className="page-title-block">
        <h1>Обучение</h1>
        <p>Ваши курсы, модули и уроки с прогрессом по шагам.</p>
      </section>

      {selectedCourse?.course && (
        <section className="surface course-hero-card">
          <div className="course-hero-icon-wrap">
            <CourseTrackIcon iconKey={selectedCourseIconKey} size={80} />
          </div>

          <div className="course-hero-copy">
            <span className="badge badge-blue course-hero-badge">Текущий курс</span>
            <h2 className="course-hero-title">{selectedCourseDisplayTitle}</h2>
            <p className="course-hero-description">{selectedCourseShortDescription}</p>
          </div>

          <div className="course-hero-progress">
            <span>Прогресс курса</span>
            <strong>{overall.percent}%</strong>
            <div className="progress-track" aria-hidden="true">
              <span style={{ width: `${overall.percent}%` }} />
            </div>
            <p>{heroLessonText}</p>
          </div>

          <div className="course-hero-action">
            {nextLesson ? (
              <Link to={`/lessons/${nextLesson.id}`} className="btn btn-primary">Продолжить обучение</Link>
            ) : (
              <button type="button" className="btn btn-primary" disabled>Продолжить обучение</button>
            )}
          </div>
        </section>
      )}

      {error && <div className="status-box status-box-error">{error}</div>}

      <section className="courses-layout-grid">
        <aside className="surface courses-sidebar-card">
          <div className="section-head">
            <div>
              <h2>Мои курсы</h2>
              <p>Выберите трек обучения.</p>
            </div>
            <span className="badge badge-neutral">{courses.length}</span>
          </div>

          {coursesLoading ? (
            <div className="skeleton-list">
              <span className="skeleton-line" />
              <span className="skeleton-line" />
            </div>
          ) : null}

          {!coursesLoading && courses.length === 0 ? (
            <div className="empty-state">
              <h3>Курсы не опубликованы</h3>
              <p>Проверьте публикацию контента в админке.</p>
            </div>
          ) : null}

          {!coursesLoading && courses.length > 0 ? (
            <div className="courses-list-items">
              {courses.map((course) => {
                const active = selectedCourse?.course?.id === course.id;
                const iconKey = resolveCourseIconKey(course);
                const title = getCourseShortTitle(course);
                const description = getCourseShortDescription(course);
                const inactivePercent = courseProgressByID[course.id];
                const percent = active ? overall.percent : inactivePercent;
                return (
                  <button
                    key={course.id}
                    className={`course-list-item ${active ? "active" : ""}`}
                    onClick={() => openCourse(course.id)}
                    disabled={loadingDetail}
                  >
                    <div className="course-list-item-icon">
                      <CourseTrackIcon iconKey={iconKey} size={44} />
                    </div>
                    <div className="course-list-item-copy">
                      <strong className="course-list-item__title">{title}</strong>
                      <p className="course-list-item__description">{description}</p>
                    </div>
                    {typeof percent === "number" ? (
                      <span className={`badge ${active ? "badge-blue" : "badge-neutral"}`}>{percent}%</span>
                    ) : null}
                  </button>
                );
              })}

              <button type="button" className="course-add-row" disabled>
                <Plus size={16} strokeWidth={2} />
                Добавить курс
              </button>
            </div>
          ) : null}
        </aside>

        <article className="surface courses-detail-card">
          {!selectedCourse && !loadingDetail ? (
            <div className="empty-state">
              <h3>Курс не выбран</h3>
              <p>Выберите курс слева, чтобы открыть уроки.</p>
            </div>
          ) : null}

          {loadingDetail ? (
            <div className="skeleton-list">
              <span className="skeleton-line" />
              <span className="skeleton-line" />
              <span className="skeleton-line" />
            </div>
          ) : null}

          {selectedCourse && !loadingDetail ? (
            <>
              <div className="section-head">
                <div>
                  <h2 className="course-detail-title">{selectedCourseDisplayTitle}</h2>
                  <p className="course-detail-description">{selectedCourseShortDescription || "Описание недоступно."}</p>
                </div>
                <span className="badge badge-blue">{overall.percent}%</span>
              </div>

              {lessons.length === 0 ? (
                <div className="empty-state">
                  <h3>Уроков пока нет</h3>
                  <p>Контент этого курса еще не опубликован.</p>
                </div>
              ) : (
                <div className="course-modules">
                  {modules.map((moduleItem, moduleIndex) => {
                    const visibleLessons = expandedModules[moduleItem.title] ? moduleItem.lessons : moduleItem.lessons.slice(0, 5);
                    const hasMore = moduleItem.lessons.length > 5;

                    return (
                      <section key={moduleItem.title} className="course-module-card">
                        <div className="course-module-head">
                          <div>
                            <h3>{`Модуль ${moduleIndex + 1}. ${moduleItem.title.replace(/^Модуль\s*\d+\.?\s*/i, "")}`}</h3>
                            <p>{moduleItem.completedBlocks} из {moduleItem.totalBlocks || 0} шагов</p>
                          </div>
                          <span className="badge badge-neutral">{moduleItem.progressPercent}%</span>
                        </div>

                        <div className="progress-track" aria-hidden="true">
                          <span style={{ width: `${moduleItem.progressPercent}%` }} />
                        </div>

                        <div className="curriculum-list" role="list">
                          {visibleLessons.map((lesson) => {
                            const absoluteIndex = moduleItem.lessons.findIndex((l) => l.id === lesson.id) + 1;
                            const isDone = lesson.progressPercent >= 100;
                            const isCurrent = !isDone && nextLesson?.id === lesson.id;
                            const status = isDone ? "Завершён" : isCurrent ? "Текущий урок" : "Не начат";

                            return (
                              <Link
                                key={lesson.id}
                                to={`/lessons/${lesson.id}`}
                                className={`curriculum-row ${isCurrent ? "active" : ""} ${isDone ? "done" : ""}`}
                                role="listitem"
                              >
                                <span className="curriculum-number" aria-hidden="true">
                                  {String(absoluteIndex).padStart(2, "0")}
                                </span>
                                <div className="curriculum-copy">
                                  <strong>{lesson.title}</strong>
                                  <p>{lesson.completedBlocks} из {lesson.totalBlocks || 0} шагов</p>
                                </div>
                                <div className="curriculum-side">
                                  <span className={`curriculum-status ${isDone ? "done" : isCurrent ? "active" : "idle"}`}>
                                    {isDone ? <Check size={14} strokeWidth={2.4} /> : null}
                                    {status}
                                  </span>
                                  <ChevronRight size={16} strokeWidth={2} />
                                </div>
                              </Link>
                            );
                          })}
                        </div>

                        {hasMore ? (
                          <button
                            type="button"
                            className="module-show-more"
                            onClick={() => setExpandedModules((prev) => ({ ...prev, [moduleItem.title]: !prev[moduleItem.title] }))}
                          >
                            {expandedModules[moduleItem.title] ? "Свернуть уроки модуля" : "Показать все уроки модуля"}
                            <ChevronRight size={15} strokeWidth={2.1} className={expandedModules[moduleItem.title] ? "rotate" : ""} />
                          </button>
                        ) : null}
                      </section>
                    );
                  })}
                </div>
              )}
            </>
          ) : null}
        </article>
      </section>
    </div>
  );
}


