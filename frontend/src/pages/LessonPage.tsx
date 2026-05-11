import Editor from "@monaco-editor/react";
import {
  ArrowRight,
  BookOpen,
  Check,
  ChevronDown,
  ChevronRight,
  ClipboardCheck,
  Code2,
  Flag,
  GraduationCap,
  Maximize2,
  Minimize2,
} from "lucide-react";
import Markdown from "react-markdown";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { checkLessonQuiz, getLesson, getSubmission, getTask, runTask, submitTask, taskHint } from "../api/client";
import { analyzePythonStyleHints } from "../lib/codeStyleHints";
import { getEditorLanguageLabel, getEditorLanguageMode } from "../lib/editorLanguage";
import { stabilizeMonacoLayout } from "../lib/stabilizeMonacoLayout";
import { useAuthStore } from "../store/auth";
import { buildLessonProgressKey } from "../utils/userScopedStorage";

type LessonBlockQuizOption = {
  id: string;
  text: string;
};

type LessonBlockQuizQuestion = {
  id: string;
  question: string;
  options: LessonBlockQuizOption[];
  correctOptionId?: string;
  explanation?: string;
};

type LessonBlockQuiz = {
  question?: string;
  options?: LessonBlockQuizOption[];
  correctOptionId?: string;
  explanation?: string;
  questions?: LessonBlockQuizQuestion[];
};

type LessonBlock = {
  id: string;
  type: string;
  title: string;
  contentMd: string;
  position: number;
  taskId?: string;
  taskTitle?: string;
  quiz?: LessonBlockQuiz;
};

type TaskEntity = {
  id: string;
  title: string;
  statementMd: string;
  starterCode: string;
  difficulty: number;
  xpReward: number;
  topic: string;
  language?: string;
  taskLanguage?: string;
  lessonLanguage?: string;
  moduleLanguage?: string;
  courseLanguage?: string;
  courseTrack?: string;
  direction?: string;
};

type JudgeResult = {
  status: string;
  score: number;
  compileOutput?: string;
  runLog?: string;
  tests?: Array<{
    index: number;
    passed: boolean;
    input?: string;
    expected: string;
    actual: string;
    error?: string;
  }>;
};

type SubmissionResult = {
  id?: string;
  status: string;
  score: number;
  compileOutput?: string;
  runLog?: string;
  feedback?: unknown;
  referenceCode?: string;
};

type QuizCheckState = "idle" | "correct" | "wrong";

type StatementExample = {
  title: string;
  bodyMd: string;
};

type PracticeSection = {
  title: string;
  normalizedTitle: string;
  chunk: string;
};

const PRACTICE_VISIBLE_SECTION_ORDER = ["коротко", "условие", "вход", "выход"];

function normalizeStarterCode(raw?: string): string {
  const source = String(raw ?? "");
  let normalized = source;
  if (normalized.includes("\\r\\n")) normalized = normalized.replace(/\\r\\n/g, "\n");
  if (normalized.includes("\\r")) normalized = normalized.replace(/\\r/g, "\n");
  if (normalized.includes("\\n")) normalized = normalized.replace(/\\n/g, "\n");
  if (normalized.includes("\\t")) normalized = normalized.replace(/\\t/g, "\t");
  if (normalized.includes('\\"')) normalized = normalized.replace(/\\"/g, '"');
  return normalized;
}

function stripLeadingHeading(raw?: string): string {
  const text = String(raw ?? "").trim();
  if (!text) return "";
  return text.replace(/^\s{0,3}#{1,6}[^\n]*\n+/u, "").trim();
}

function normalizeSectionTitle(raw: string): string {
  return raw.trim().toLowerCase();
}

function collectPracticeSections(source: string): PracticeSection[] {
  const markerRegex =
    /^\s*(?:#{1,6}\s*|\*\*\s*)?(Коротко|Условие|Вход|Выход|Шаблон|Подсказки|Пример\s+\d+)(?:\s*\*\*)?\s*:?[ \t]*(.*)$/gimu;
  const markers = [...source.matchAll(markerRegex)];
  if (!markers.length) return [];

  return markers.map((match, index) => {
    const start = match.index ?? 0;
    const end = index + 1 < markers.length ? markers[index + 1].index ?? source.length : source.length;
    const chunk = source.slice(start, end).trim();
    const title = String(match[1] ?? "").trim();
    return {
      title,
      normalizedTitle: normalizeSectionTitle(title),
      chunk,
    };
  });
}

function extractExampleFromChunk(rawChunk: string, fallbackIndex: number): StatementExample | null {
  const chunk = rawChunk.trim();
  if (!chunk) return null;
  const titleMatch = chunk.match(/^\s*(?:#{1,6}\s*|\*\*\s*)?(Пример\s+\d+)(?:\s*\*\*)?\s*:?\s*/iu);
  const title = titleMatch?.[1]?.trim() || `Пример ${fallbackIndex + 1}`;
  const bodyMd = chunk
    .replace(/^\s*(?:#{1,6}\s*|\*\*\s*)?Пример\s+\d+(?:\s*\*\*)?\s*:?\s*/iu, "")
    .trim();
  if (!bodyMd) return null;
  return { title, bodyMd };
}

function parsePracticeStatement(raw?: string): { statementMd: string; examples: StatementExample[]; inlineHintsMd: string } {
  const source = stripLeadingHeading(raw).replace(/\r/g, "").trim();
  if (!source) return { statementMd: "", examples: [], inlineHintsMd: "" };

  const sections = collectPracticeSections(source);
  if (!sections.length) {
    const exampleRegex =
      /(?:^|\n)\s*(?:#{1,6}\s*|\*\*\s*)?(Пример\s+\d+)(?:\s*\*\*)?\s*:?[ \t]*(?:\n|$)([\s\S]*?)(?=\n\s*(?:#{1,6}\s*|\*\*\s*)?(?:Пример\s+\d+|Коротко|Условие|Вход|Выход|Шаблон|Подсказки)\b|$)/giu;
    const hintsRegex =
      /(?:^|\n)\s*(?:#{1,6}\s*|\*\*\s*)?Подсказки(?:\s*\*\*)?\s*:?[ \t]*(?:\n|$)([\s\S]*?)(?=\n\s*(?:#{1,6}\s*|\*\*\s*)?(?:Пример\s+\d+|Коротко|Условие|Вход|Выход|Шаблон|Подсказки)\b|$)/giu;
    const templateRegex =
      /(?:^|\n)\s*(?:#{1,6}\s*|\*\*\s*)?Шаблон(?:\s*\*\*)?\s*:?[ \t]*(?:\n|$)([\s\S]*?)(?=\n\s*(?:#{1,6}\s*|\*\*\s*)?(?:Пример\s+\d+|Коротко|Условие|Вход|Выход|Шаблон|Подсказки)\b|$)/giu;
    const matches = [...source.matchAll(exampleRegex)];
    const hintsMatch = source.match(hintsRegex);
    const inlineHintsMd = String(hintsMatch?.[1] ?? "").trim();

    const examples: StatementExample[] = matches
      .map((match, index) => {
        const title = String(match[1] ?? `Пример ${index + 1}`).trim();
        const bodyMd = String(match[2] ?? "").trim();
        if (!bodyMd) return null;
        return { title, bodyMd };
      })
      .filter((item): item is StatementExample => Boolean(item));

    const statementMd = source
      .replace(exampleRegex, "")
      .replace(hintsRegex, "")
      .replace(templateRegex, "")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
    return { statementMd, examples, inlineHintsMd };
  }

  const examples: StatementExample[] = [];
  const uniqueMainSections = new Map<string, PracticeSection>();
  const otherSections: PracticeSection[] = [];
  let inlineHintsMd = "";

  for (const section of sections) {
    if (/^пример\s+\d+/iu.test(section.normalizedTitle)) {
      const parsedExample = extractExampleFromChunk(section.chunk, examples.length);
      if (parsedExample) examples.push(parsedExample);
      continue;
    }

    if (section.normalizedTitle === "подсказки") {
      if (!inlineHintsMd) {
        inlineHintsMd = section.chunk
          .replace(/^\s*(?:#{1,6}\s*|\*\*\s*)?Подсказки(?:\s*\*\*)?\s*:?\s*/iu, "")
          .trim();
      }
      continue;
    }

    if (section.normalizedTitle === "шаблон") {
      continue;
    }

    if (PRACTICE_VISIBLE_SECTION_ORDER.includes(section.normalizedTitle)) {
      if (!uniqueMainSections.has(section.normalizedTitle)) uniqueMainSections.set(section.normalizedTitle, section);
      continue;
    }

    otherSections.push(section);
  }

  const normalizedChunks: string[] = [];
  for (const sectionName of PRACTICE_VISIBLE_SECTION_ORDER) {
    const section = uniqueMainSections.get(sectionName);
    if (section) normalizedChunks.push(section.chunk);
  }
  for (const section of otherSections) {
    normalizedChunks.push(section.chunk);
  }

  const statementMd = normalizedChunks.join("\n\n").replace(/\n{3,}/g, "\n\n").trim();

  return { statementMd, examples, inlineHintsMd };
}

function normalizeQuizQuestions(quiz?: LessonBlockQuiz): LessonBlockQuizQuestion[] {
  if (!quiz) return [];

  if (Array.isArray(quiz.questions) && quiz.questions.length > 0) {
    return quiz.questions.flatMap((item, index) => {
      const options = Array.isArray(item.options)
        ? item.options
            .map((opt) => ({
              id: String(opt?.id ?? "").trim(),
              text: String(opt?.text ?? "").trim(),
            }))
            .filter((opt) => opt.id !== "" && opt.text !== "")
        : [];

      const question = String(item.question ?? "").trim();
      const correctOptionId = String(item.correctOptionId ?? "").trim();
      if (!question || options.length === 0) return [];

      return [
        {
          id: String(item.id ?? `q${index + 1}`),
          question,
          options,
          correctOptionId: correctOptionId || undefined,
          explanation: item.explanation,
        },
      ];
    });
  }

  const fallbackQuestion = String(quiz.question ?? "").trim();
  const fallbackOptions = Array.isArray(quiz.options)
    ? quiz.options
        .map((opt) => ({
          id: String(opt?.id ?? "").trim(),
          text: String(opt?.text ?? "").trim(),
        }))
        .filter((opt) => opt.id !== "" && opt.text !== "")
    : [];
  const fallbackCorrect = String(quiz.correctOptionId ?? "").trim();
  if (!fallbackQuestion || fallbackOptions.length === 0) return [];

  return [
    {
      id: "q1",
      question: fallbackQuestion,
      options: fallbackOptions,
      correctOptionId: fallbackCorrect || undefined,
      explanation: quiz.explanation,
    },
  ];
}

function parseQuizQuestionsFromMarkdown(contentMd?: string): LessonBlockQuizQuestion[] {
  const source = String(contentMd ?? "").replace(/\r/g, "").trim();
  if (!source) return [];

  const questionMatch = source.match(/(?:\*\*\s*)?Вопрос(?:\s*\*\*)?\s*:\s*([^\n]+)/iu);
  const question = String(questionMatch?.[1] ?? "")
    .replace(/\*\*/g, "")
    .trim();

  const lineOptions = source
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.match(/^([A-ZА-Я])[.)]\s+(.+)$/iu))
    .filter((match): match is RegExpMatchArray => Boolean(match))
    .map((match) => ({
      id: String(match[1] ?? "").trim().toUpperCase(),
      text: String(match[2] ?? "").replace(/\*\*/g, "").trim(),
    }))
    .filter((option) => option.id && option.text);

  if (question && lineOptions.length >= 2) {
    return [{ id: "q1", question, options: lineOptions }];
  }

  const flat = source.replace(/\n/g, " ").replace(/\s+/g, " ").trim();
  const inlineOptions = [...flat.matchAll(/([A-ZА-Я])[.)]\s*(.*?)(?=\s+[A-ZА-Я][.)]\s+|$)/giu)]
    .map((match) => ({
      id: String(match[1] ?? "").trim().toUpperCase(),
      text: String(match[2] ?? "").replace(/\*\*/g, "").trim(),
    }))
    .filter((option) => option.id && option.text);

  if (question && inlineOptions.length >= 2) {
    return [{ id: "q1", question, options: inlineOptions }];
  }

  return [];
}

function blockTypeLabel(type: string) {
  const normalized = (type ?? "").toLowerCase();
  if (normalized === "practice") return "Практика";
  if (normalized === "project") return "Проект";
  if (normalized === "quiz") return "Тест";
  if (normalized === "summary") return "Итог";
  return "Теория";
}

function blockTypeClass(type: string) {
  const normalized = (type ?? "").toLowerCase();
  if (normalized === "practice") return "badge badge-accent";
  if (normalized === "project") return "badge badge-accent";
  if (normalized === "quiz") return "badge badge-warning";
  if (normalized === "summary") return "badge badge-success";
  return "badge badge-neutral";
}

function stepTypeIcon(type: string) {
  const normalized = (type ?? "").toLowerCase();
  if (normalized === "practice") return <Code2 size={14} strokeWidth={2} aria-hidden="true" />;
  if (normalized === "project") return <Code2 size={14} strokeWidth={2} aria-hidden="true" />;
  if (normalized === "quiz") return <ClipboardCheck size={14} strokeWidth={2} aria-hidden="true" />;
  if (normalized === "summary") return <Flag size={14} strokeWidth={2} aria-hidden="true" />;
  return <BookOpen size={14} strokeWidth={2} aria-hidden="true" />;
}

function ruSubmissionStatus(status?: string): string {
  const value = (status ?? "").trim().toLowerCase();
  if (value === "ran") return "Код выполнен";
  if (value === "queued") return "В очереди";
  if (value === "accepted") return "Принято";
  if (value === "wrong_answer") return "Неверный ответ";
  if (value === "compile_error") return "Ошибка компиляции";
  if (value === "runtime_error") return "Ошибка выполнения";
  if (value === "time_limit") return "Превышен лимит времени";
  if (value === "failed") return "Сбой проверки";
  return status ?? "Неизвестно";
}

function statusBadge(status?: string) {
  const value = String(status ?? "").toLowerCase();
  if (value === "ran") return "badge badge-success";
  if (value === "accepted") return "badge badge-success";
  if (value === "queued") return "badge badge-warning";
  if (value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit" || value === "failed") return "badge badge-error";
  return "badge badge-neutral";
}

function submissionOutcomeHint(status?: string): { text: string; className: string } | null {
  const value = String(status ?? "").toLowerCase();
  if (value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit") {
    return {
      text: "Это ошибка в вашем коде, а не в системе проверки. Исправьте решение по логу и отправьте снова.",
      className: "status-box status-box-error",
    };
  }
  if (value === "failed") {
    return {
      text: "Это сбой во время проверки на сервере. Попробуйте отправить решение повторно.",
      className: "status-box",
    };
  }
  return null;
}

function ruError(raw?: string) {
  const text = (raw ?? "").trim().toLowerCase();
  if (!text) return "Произошла ошибка. Повторите действие.";
  if (text.includes("unauthorized")) return "Сессия истекла. Выполните вход заново.";
  if (text.includes("task not found")) return "Задача не найдена.";
  if (text.includes("submission not found")) return "Результат отправки не найден.";
  if (text.includes("upgrade_required")) return "AI-подсказка доступна на Premium тарифе.";
  return raw ?? "Произошла ошибка. Повторите действие.";
}

function buildLessonDraftsStorageKey(userId?: string, lessonId?: string): string {
  const normalizedLessonId = String(lessonId ?? "").trim();
  if (!normalizedLessonId) return "";
  const normalizedUserId = String(userId ?? "anon").trim() || "anon";
  return `lc_lesson_code_drafts_${normalizedUserId}_${normalizedLessonId}`;
}

function readLessonDrafts(storageKey: string): Record<string, string> {
  if (!storageKey) return {};
  try {
    const raw = localStorage.getItem(storageKey);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return {};

    const next: Record<string, string> = {};
    for (const [key, value] of Object.entries(parsed as Record<string, unknown>)) {
      const taskID = String(key ?? "").trim();
      if (!taskID) continue;
      next[taskID] = normalizeStarterCode(String(value ?? ""));
    }
    return next;
  } catch {
    return {};
  }
}

function writeLessonDrafts(storageKey: string, drafts: Record<string, string>) {
  if (!storageKey) return;
  try {
    localStorage.setItem(storageKey, JSON.stringify(drafts));
  } catch {
    // ignore localStorage quota/access issues; lesson still keeps drafts in memory
  }
}

export function LessonPage() {
  const { lessonId } = useParams();
  const user = useAuthStore((s) => s.user);

  const [data, setData] = useState<any | null>(null);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeBlockIndex, setActiveBlockIndex] = useState(0);

  const [completedBlocks, setCompletedBlocks] = useState<Record<string, boolean>>({});

  const [quizAnswers, setQuizAnswers] = useState<Record<string, Record<string, string>>>({});
  const [quizCheckState, setQuizCheckState] = useState<Record<string, QuizCheckState>>({});
  const [quizFailedQuestions, setQuizFailedQuestions] = useState<Record<string, string[]>>({});
  const [openQuizSelect, setOpenQuizSelect] = useState<string | null>(null);
  const [quizCheckLoading, setQuizCheckLoading] = useState(false);

  const [taskCache, setTaskCache] = useState<Record<string, TaskEntity>>({});
  const [codeDrafts, setCodeDrafts] = useState<Record<string, string>>({});

  const [practiceTask, setPracticeTask] = useState<TaskEntity | null>(null);
  const [practiceCode, setPracticeCode] = useState("");
  const [isEditorExpanded, setIsEditorExpanded] = useState(false);
  const [practiceLoading, setPracticeLoading] = useState(false);
  const [practiceMessage, setPracticeMessage] = useState("");

  const [runLoading, setRunLoading] = useState(false);
  const [runResult, setRunResult] = useState<JudgeResult | null>(null);

  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitResult, setSubmitResult] = useState<SubmissionResult | null>(null);

  const [hintLoading, setHintLoading] = useState(false);
  const [hint, setHint] = useState("");
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const decorationIDsRef = useRef<string[]>([]);
  const editorLayoutCleanupRef = useRef<(() => void) | null>(null);

  const progressStorageKey = useMemo(
    () => (lessonId ? buildLessonProgressKey(user?.id, lessonId) : ""),
    [user?.id, lessonId]
  );
  const codeDraftsStorageKey = useMemo(() => buildLessonDraftsStorageKey(user?.id, lessonId), [user?.id, lessonId]);

  useEffect(() => {
    if (!progressStorageKey) {
      setCompletedBlocks({});
      return;
    }
    try {
      const raw = localStorage.getItem(progressStorageKey);
      if (!raw) {
        setCompletedBlocks({});
        return;
      }
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") {
        setCompletedBlocks(parsed as Record<string, boolean>);
      } else {
        setCompletedBlocks({});
      }
    } catch {
      setCompletedBlocks({});
    }
  }, [progressStorageKey]);

  useEffect(() => {
    if (!codeDraftsStorageKey) {
      setCodeDrafts({});
      return;
    }
    setCodeDrafts(readLessonDrafts(codeDraftsStorageKey));
  }, [codeDraftsStorageKey]);

  const markBlockCompleted = useCallback(
    (blockID: string) => {
      setCompletedBlocks((prev) => {
        if (prev[blockID]) return prev;
        const next = { ...prev, [blockID]: true };
        if (progressStorageKey) {
          localStorage.setItem(progressStorageKey, JSON.stringify(next));
        }
        return next;
      });
    },
    [progressStorageKey]
  );

  useEffect(() => {
    if (!lessonId) return;
    setLoading(true);
    getLesson(lessonId)
      .then((d) => {
        setData(d);
        setMsg("");
        setActiveBlockIndex(0);
        setQuizAnswers({});
        setQuizCheckState({});
        setQuizFailedQuestions({});
        setQuizCheckLoading(false);
        setTaskCache({});
        setPracticeTask(null);
        setPracticeCode("");
        setPracticeMessage("");
        setRunResult(null);
        setSubmitResult(null);
        setHint("");
      })
      .catch((e: any) => {
        setMsg(e?.response?.data?.error ?? "Не удалось загрузить урок.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [lessonId]);

  const blocks: LessonBlock[] = useMemo(() => {
    if (!Array.isArray(data?.blocks)) return [];
    return data.blocks
      .map((block: any) => ({
        id: String(block.id),
        type: String(block.type ?? "theory"),
        title: String(block.title ?? "Шаг"),
        contentMd: String(block.contentMd ?? "").replace(/\r/g, "").trim(),
        position: Number(block.position ?? 0),
        taskId: block.taskId ? String(block.taskId) : undefined,
        taskTitle: block.taskTitle ? String(block.taskTitle) : undefined,
        quiz: block.quiz,
      }))
      .sort((a, b) => a.position - b.position);
  }, [data?.blocks]);

  const activeBlock = blocks[activeBlockIndex] ?? null;
  const activeQuizQuestions = useMemo(() => {
    const fromPayload = normalizeQuizQuestions(activeBlock?.quiz);
    if (fromPayload.length > 0) return fromPayload;
    if ((activeBlock?.type ?? "").toLowerCase() !== "quiz") return [];
    return parseQuizQuestionsFromMarkdown(activeBlock?.contentMd);
  }, [activeBlock?.quiz, activeBlock?.type, activeBlock?.contentMd]);

  useEffect(() => {
    setOpenQuizSelect(null);
  }, [activeBlock?.id]);

  useEffect(() => {
    if (!openQuizSelect) return;

    function onOutsideClick(event: MouseEvent) {
      const target = event.target as HTMLElement | null;
      if (!target) return;
      if (target.closest("[data-quiz-select-root='true']")) return;
      setOpenQuizSelect(null);
    }

    function onEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpenQuizSelect(null);
      }
    }

    document.addEventListener("mousedown", onOutsideClick);
    document.addEventListener("keydown", onEscape);
    return () => {
      document.removeEventListener("mousedown", onOutsideClick);
      document.removeEventListener("keydown", onEscape);
    };
  }, [openQuizSelect]);

  useEffect(() => {
    if (!activeBlock) return;

    const normalizedType = activeBlock.type.toLowerCase();
    if (normalizedType === "theory" || normalizedType === "summary") {
      markBlockCompleted(activeBlock.id);
    }

    if (!activeBlock.taskId) {
      setPracticeTask(null);
      setPracticeCode("");
      setPracticeLoading(false);
      setPracticeMessage("");
      setRunResult(null);
      setSubmitResult(null);
      setHint("");
      return;
    }

    const taskID = activeBlock.taskId;
    setPracticeMessage("");
    setRunResult(null);
    setSubmitResult(null);
    setHint("");

    const cached = taskCache[taskID];
    if (cached) {
      setPracticeTask(cached);
      setPracticeCode(codeDrafts[taskID] ?? cached.starterCode);
      return;
    }

    let cancelled = false;
    setPracticeLoading(true);
    getTask(taskID)
      .then((payload) => {
        if (cancelled) return;
        const normalized: TaskEntity = {
          id: String(payload?.task?.id ?? taskID),
          title: String(payload?.task?.title ?? "Задача"),
          statementMd: String(payload?.task?.statementMd ?? "").replace(/\r/g, "").trim(),
          starterCode: normalizeStarterCode(payload?.task?.starterCode),
          difficulty: Number(payload?.task?.difficulty ?? 1),
          xpReward: Number(payload?.task?.xpReward ?? 0),
          topic: String(payload?.task?.topic ?? "General"),
          language: String(payload?.task?.language ?? payload?.task?.lang ?? ""),
          taskLanguage: String(payload?.task?.language ?? payload?.task?.lang ?? ""),
          lessonLanguage: String(
            payload?.lesson?.language ??
            payload?.lesson?.lang ??
            data?.lesson?.language ??
            data?.lesson?.lang ??
            ""
          ),
          moduleLanguage: String(payload?.module?.language ?? payload?.module?.lang ?? ""),
          courseLanguage: String(payload?.course?.language ?? payload?.course?.lang ?? ""),
          courseTrack: String(payload?.course?.track ?? payload?.course?.stack ?? ""),
          direction: String(payload?.direction ?? payload?.course?.direction ?? ""),
        };
        setTaskCache((prev) => ({ ...prev, [taskID]: normalized }));
        setPracticeTask(normalized);
        setPracticeCode(codeDrafts[taskID] ?? normalized.starterCode);
      })
      .catch((e: any) => {
        if (cancelled) return;
        setPracticeTask(null);
        setPracticeMessage(ruError(e?.response?.data?.error ?? "Не удалось загрузить задачу."));
      })
      .finally(() => {
        if (!cancelled) {
          setPracticeLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [activeBlock, data?.lesson?.language, data?.lesson?.lang, markBlockCompleted]);

  const updatePracticeCode = useCallback(
    (next: string) => {
      setPracticeCode(next);
      setRunResult(null);
      setSubmitResult(null);
      setHint("");
      if (practiceTask) {
        setCodeDrafts((prev) => {
          const nextDrafts = { ...prev, [practiceTask.id]: next };
          writeLessonDrafts(codeDraftsStorageKey, nextDrafts);
          return nextDrafts;
        });
      }
    },
    [practiceTask, codeDraftsStorageKey]
  );

  useEffect(() => {
    if (!practiceTask) return;
    const savedDraft = codeDrafts[practiceTask.id];
    if (typeof savedDraft !== "string") return;
    setPracticeCode((current) => (current === savedDraft ? current : savedDraft));
  }, [practiceTask, codeDrafts]);

  const editorTheme = "light";
  const languageSources = useMemo(
    () => [
      practiceTask?.taskLanguage,
      practiceTask?.language,
      practiceTask?.lessonLanguage,
      practiceTask?.moduleLanguage,
      practiceTask?.courseLanguage,
      practiceTask?.courseTrack,
      practiceTask?.direction,
      data?.lesson?.language,
      data?.lesson?.lang,
      data?.module?.language,
      data?.module?.lang,
      data?.course?.language,
      data?.course?.track,
      data?.course?.direction,
      data?.direction,
    ],
    [practiceTask, data]
  );
  const editorLanguage = useMemo(() => getEditorLanguageMode(languageSources), [languageSources]);
  const editorLanguageLabel = useMemo(() => getEditorLanguageLabel(languageSources), [languageSources]);
  const lessonEditorHeight = isEditorExpanded ? "560px" : "380px";

  const stepNumbers = useMemo(
    () => blocks.map((block, index) => (Number.isFinite(block.position) && block.position > 0 ? block.position : index + 1)),
    [blocks]
  );
  const activeStepNumber = stepNumbers[activeBlockIndex] ?? activeBlockIndex + 1;
  const totalSteps = stepNumbers.length > 0 ? Math.max(blocks.length, ...stepNumbers) : blocks.length;
  const completedStepsCount = useMemo(
    () => blocks.reduce((acc, block) => acc + (completedBlocks[block.id] ? 1 : 0), 0),
    [blocks, completedBlocks]
  );
  const sidebarProgressPercent = useMemo(() => {
    if (totalSteps <= 0) return 0;
    const current = Math.max(1, Math.min(activeStepNumber, totalSteps));
    return Math.round((current / totalSteps) * 100);
  }, [activeStepNumber, totalSteps]);

  const shouldShowStyleHints = useMemo(() => {
    const submitAccepted = String(submitResult?.status ?? "").toLowerCase() === "accepted";
    return submitAccepted;
  }, [submitResult?.status]);

  const styleHints = useMemo(() => {
    if (!shouldShowStyleHints) return [];
    if (editorLanguage !== "python") return [];
    return analyzePythonStyleHints(practiceCode);
  }, [shouldShowStyleHints, editorLanguage, practiceCode]);

  const parsedPracticeStatement = useMemo(() => parsePracticeStatement(practiceTask?.statementMd), [practiceTask?.statementMd]);
  const practiceStatementMd = parsedPracticeStatement.statementMd;
  const practiceInlineHintsMd = parsedPracticeStatement.inlineHintsMd;
  const practiceExamples = parsedPracticeStatement.examples;
  const visiblePracticeExamples = useMemo(() => {
    if (!practiceTask) return [] as StatementExample[];
    if (practiceTask.difficulty < 3) return [] as StatementExample[];
    return practiceExamples.slice(0, 1);
  }, [practiceExamples, practiceTask]);

  const applyStyleHintDecorations = useCallback(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    const model = editor?.getModel?.();
    if (!editor || !monaco || !model) return;

    if (!styleHints.length) {
      decorationIDsRef.current = editor.deltaDecorations(decorationIDsRef.current, []);
      return;
    }

    const nextDecorations = styleHints.map((hint) => ({
      range: new monaco.Range(hint.line, 1, hint.line, 1),
      options: {
        isWholeLine: true,
        glyphMarginClassName: "editor-style-hint-glyph",
        glyphMarginHoverMessage: { value: hint.message },
        linesDecorationsClassName: "editor-style-hint-line",
      },
    }));

    decorationIDsRef.current = editor.deltaDecorations(decorationIDsRef.current, nextDecorations);
  }, [styleHints]);

  useEffect(() => {
    applyStyleHintDecorations();
  }, [applyStyleHintDecorations]);

  useEffect(() => {
    return () => {
      editorLayoutCleanupRef.current?.();
      editorLayoutCleanupRef.current = null;
      const editor = editorRef.current;
      if (editor && decorationIDsRef.current.length) {
        decorationIDsRef.current = editor.deltaDecorations(decorationIDsRef.current, []);
      }
    };
  }, []);

  useEffect(() => {
    setIsEditorExpanded(false);
  }, [activeBlock?.id]);

  function onEditorMount(editor: any, monaco: any) {
    editorRef.current = editor;
    monacoRef.current = monaco;
    editorLayoutCleanupRef.current?.();
    editorLayoutCleanupRef.current = stabilizeMonacoLayout(editor, monaco);
    applyStyleHintDecorations();
  }

  async function onRunCode() {
    if (!practiceTask || !activeBlock?.taskId) return;
    setRunLoading(true);
    setPracticeMessage("");
    setRunResult(null);

    try {
      const result = (await runTask(practiceTask.id, practiceCode)) as JudgeResult;
      setRunResult(result);
    } catch (e: any) {
      setPracticeMessage(ruError(e?.response?.data?.error ?? "Не удалось выполнить код."));
    } finally {
      setRunLoading(false);
    }
  }

  async function onSubmitCode() {
    if (!practiceTask || !activeBlock?.taskId) return;
    setSubmitLoading(true);
    setPracticeMessage("");
    setSubmitResult(null);

    try {
      const queued = await submitTask(practiceTask.id, practiceCode);
      let attempts = 0;

      while (attempts < 45) {
        const current = (await getSubmission(String(queued?.submissionId ?? ""))) as SubmissionResult;
        setSubmitResult(current);

        if (String(current?.status ?? "").toLowerCase() !== "queued") {
          if (String(current?.status ?? "").toLowerCase() === "accepted") {
            markBlockCompleted(activeBlock.id);
          }
          setSubmitLoading(false);
          return;
        }

        attempts += 1;
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }

      setPracticeMessage("Проверка заняла больше времени. Попробуйте обновить шаг через несколько секунд.");
    } catch (e: any) {
      setPracticeMessage(ruError(e?.response?.data?.error ?? "Не удалось отправить решение."));
    } finally {
      setSubmitLoading(false);
    }
  }

  async function onHint() {
    if (!practiceTask) return;
    setHintLoading(true);
    setPracticeMessage("");

    try {
      const data = await taskHint(practiceTask.id, practiceCode);
      setHint(String(data?.hint ?? "Подсказка недоступна."));
    } catch (e: any) {
      setPracticeMessage(ruError(e?.response?.data?.error ?? "Не удалось получить подсказку."));
    } finally {
      setHintLoading(false);
    }
  }

  async function onCheckQuiz() {
    if (!lessonId || !activeBlock || activeBlock.type.toLowerCase() !== "quiz") return;
    setOpenQuizSelect(null);
    const questions = normalizeQuizQuestions(activeBlock.quiz);
    if (questions.length === 0) return;

    const answersForBlock = quizAnswers[activeBlock.id] ?? {};
    const hasUnanswered = questions.some((question) => !answersForBlock[question.id]);
    if (hasUnanswered) return;

    setQuizCheckLoading(true);
    setPracticeMessage("");
    try {
      const response = await checkLessonQuiz(lessonId, activeBlock.id, answersForBlock);
      const failed = Array.isArray(response?.failedQuestionIds)
        ? response.failedQuestionIds.map((item: unknown) => String(item))
        : [];
      const isCorrect = String(response?.status ?? "").toLowerCase() === "correct" && failed.length === 0;

      setQuizCheckState((prev) => ({
        ...prev,
        [activeBlock.id]: isCorrect ? "correct" : "wrong",
      }));
      setQuizFailedQuestions((prev) => ({
        ...prev,
        [activeBlock.id]: failed,
      }));

      if (isCorrect) {
        markBlockCompleted(activeBlock.id);
      }
    } catch (e: any) {
      setPracticeMessage(ruError(e?.response?.data?.error ?? "Не удалось проверить тест."));
      setQuizCheckState((prev) => ({
        ...prev,
        [activeBlock.id]: "wrong",
      }));
    } finally {
      setQuizCheckLoading(false);
    }
  }

  function onRetryQuiz() {
    if (!activeBlock || activeBlock.type.toLowerCase() !== "quiz") return;
    setOpenQuizSelect(null);
    setQuizCheckLoading(false);
    setQuizAnswers((prev) => ({ ...prev, [activeBlock.id]: {} }));
    setQuizCheckState((prev) => ({ ...prev, [activeBlock.id]: "idle" }));
    setQuizFailedQuestions((prev) => ({ ...prev, [activeBlock.id]: [] }));
  }

  const hasNextBlock = activeBlockIndex < blocks.length - 1;

  if (loading) {
    return (
      <div className="page-stack">
        <section className="surface">
          <div className="skeleton-list">
            <span className="skeleton-line" />
            <span className="skeleton-line" />
            <span className="skeleton-line" />
          </div>
        </section>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page-stack">
        <section className="surface empty-state">
          <h3>Урок недоступен</h3>
          <p>{msg || "Попробуйте открыть другой урок в карте обучения."}</p>
          <Link to="/courses" className="btn btn-primary">К курсам</Link>
        </section>
      </div>
    );
  }

  const lessonTitle = String(data?.lesson?.title ?? "Урок");
  const moduleTitle = String(data?.lesson?.moduleTitle ?? "");
  const blockComplete = activeBlock ? !!completedBlocks[activeBlock.id] : false;
  const activeBlockType = String(activeBlock?.type ?? "").toLowerCase();
  const isCodeTask = activeBlockType === "practice" || activeBlockType === "project";
  const isCodeTaskWithoutTask = !!activeBlock && isCodeTask && !activeBlock.taskId;

  return (
    <div className="lesson-page page-stack">
      <section className="surface lesson-overview-card">
        <span className="lesson-overview-icon" aria-hidden="true">
          <GraduationCap size={26} strokeWidth={1.9} />
        </span>
        <div className="lesson-overview-main">
          <div className="lesson-overview-copy">
            <h1>{lessonTitle}</h1>
            {moduleTitle && <p>{moduleTitle}</p>}
          </div>
        </div>
        {activeBlock && <span className="lesson-progress-pill">Шаг {activeStepNumber} из {totalSteps}</span>}
      </section>

      <section className="lesson-stepic-layout">
        <aside className="surface lesson-stepper">
          <div className="lesson-stepper-head">
            <span className="lesson-stepper-label">Навигация урока</span>
            <h2>{lessonTitle}</h2>
            <p className="lesson-stepper-meta">Шаг {activeStepNumber} из {totalSteps}</p>
            <div className="lesson-stepper-progress" aria-hidden="true">
              <span style={{ width: `${sidebarProgressPercent}%` }} />
            </div>
            <div className="lesson-stepper-meta-row">
              <span>{totalSteps} шагов</span>
              <span>{completedStepsCount} выполнено</span>
            </div>
          </div>

          <div className="lesson-stepper-list-wrap">
            <span className="lesson-stepper-list-label">Шаги</span>
            <div className="lesson-steps-list">
              {blocks.map((block, index) => {
                const stepNumber = stepNumbers[index] ?? index + 1;
                const isActive = index === activeBlockIndex;
                const isCompleted = !!completedBlocks[block.id];
                const type = blockTypeLabel(block.type);
                const rowStateClass = isActive
                  ? "lesson-step-item--active"
                  : isCompleted
                    ? "lesson-step-item--completed"
                    : "lesson-step-item--future";

                return (
                  <button
                    key={block.id}
                    className={`lesson-step-item ${rowStateClass}`}
                    onClick={() => setActiveBlockIndex(index)}
                    aria-current={isActive ? "step" : undefined}
                  >
                    <span
                      className={`lesson-step-item__marker ${isCompleted ? "lesson-step-item__marker--completed" : isActive ? "lesson-step-item__marker--active" : "lesson-step-item__marker--future"}`}
                      aria-hidden="true"
                    >
                      {isCompleted ? <Check size={13} strokeWidth={2.6} /> : String(stepNumber).padStart(2, "0")}
                    </span>

                    <div className="lesson-step-main">
                      <strong className="lesson-step-item__title">{block.title}</strong>
                      <span className="lesson-step-item__meta">{type}</span>
                    </div>

                    <span className="lesson-step-item__trail">
                      <ChevronRight size={16} strokeWidth={2} className="lesson-step-item__chevron" aria-hidden="true" />
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </aside>

        <article className="surface lesson-step-content">
          {!activeBlock ? (
            <div className="empty-state">
              <h3>Шаг не найден</h3>
              <p>Откройте другой шаг в списке урока.</p>
            </div>
          ) : (
            <>
              <div className="section-head lesson-step-headline">
                <div>
                  <div className="lesson-step-headline-title">
                    {stepTypeIcon(activeBlock.type)}
                    <h2>{activeBlock.title}</h2>
                  </div>
                  <p>Шаг {activeStepNumber} • {blockTypeLabel(activeBlock.type)}</p>
                </div>
                <span className={blockComplete ? "badge badge-success" : blockTypeClass(activeBlock.type)}>
                  {blockComplete ? "Выполнено" : blockTypeLabel(activeBlock.type)}
                </span>
              </div>

              {activeBlock.contentMd &&
                (!isCodeTask || isCodeTaskWithoutTask) &&
                !(activeBlock.type.toLowerCase() === "quiz" && activeQuizQuestions.length > 0) && (
                <div className="markdown-content lesson-step-markdown">
                  <Markdown>{activeBlock.contentMd}</Markdown>
                </div>
              )}

              {activeBlock.type.toLowerCase() === "quiz" && activeBlock.quiz && (
                <div className="lesson-quiz-block">
                  {activeQuizQuestions.length > 0 ? (
                    <div className="lesson-quiz-questions">
                      {activeQuizQuestions.map((question, questionIndex) => {
                        const failedQuestions = quizFailedQuestions[activeBlock.id] ?? [];
                        const isFailed = failedQuestions.includes(question.id);
                        const selectKey = `${activeBlock.id}:${question.id}`;
                        const isOpen = openQuizSelect === selectKey;
                        const selectedOptionId = quizAnswers[activeBlock.id]?.[question.id] ?? "";
                        const selectedOption = question.options.find((option) => option.id === selectedOptionId);
                        return (
                          <div
                            key={question.id}
                            className={`lesson-quiz-select-wrap ${isFailed ? "has-error" : ""}`}
                            data-quiz-select-root="true"
                          >
                            <span className="lesson-quiz-question-title">
                              {questionIndex + 1}. {question.question}
                            </span>
                            <button
                              type="button"
                              className={`custom-select-trigger ${isOpen ? "open" : ""}`}
                              aria-expanded={isOpen}
                              onClick={() => setOpenQuizSelect((prev) => (prev === selectKey ? null : selectKey))}
                            >
                              <span>{selectedOption ? `${selectedOption.id}. ${selectedOption.text}` : "Выберите вариант"}</span>
                              <ChevronDown size={16} strokeWidth={2} />
                            </button>

                            {isOpen && (
                              <div className="custom-select-menu">
                                <button
                                  type="button"
                                  className={`custom-select-option ${selectedOptionId === "" ? "selected" : ""}`}
                                  onClick={() => {
                                    setQuizAnswers((prev) => ({
                                      ...prev,
                                      [activeBlock.id]: {
                                        ...(prev[activeBlock.id] ?? {}),
                                        [question.id]: "",
                                      },
                                    }));
                                    setQuizCheckState((prev) => ({ ...prev, [activeBlock.id]: "idle" }));
                                    setQuizFailedQuestions((prev) => ({ ...prev, [activeBlock.id]: [] }));
                                    setOpenQuizSelect(null);
                                  }}
                                >
                                  Выберите вариант
                                </button>

                                {question.options.map((option) => (
                                  <button
                                    key={option.id}
                                    type="button"
                                    className={`custom-select-option ${selectedOptionId === option.id ? "selected" : ""}`}
                                    onClick={() => {
                                      setQuizAnswers((prev) => ({
                                        ...prev,
                                        [activeBlock.id]: {
                                          ...(prev[activeBlock.id] ?? {}),
                                          [question.id]: option.id,
                                        },
                                      }));
                                      setQuizCheckState((prev) => ({ ...prev, [activeBlock.id]: "idle" }));
                                      setQuizFailedQuestions((prev) => ({ ...prev, [activeBlock.id]: [] }));
                                      setOpenQuizSelect(null);
                                    }}
                                  >
                                    {option.id}. {option.text}
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="status-box status-box-error">Тест в этом шаге пока недоступен. Обратитесь к преподавателю.</div>
                  )}

                  <div className="lesson-step-actions">
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={onCheckQuiz}
                      disabled={
                        quizCheckLoading ||
                        activeQuizQuestions.length === 0 ||
                        activeQuizQuestions.some((question) => !quizAnswers[activeBlock.id]?.[question.id])
                      }
                    >
                      {quizCheckLoading ? "Проверяем..." : "Проверить ответ"}
                    </button>
                    {quizCheckState[activeBlock.id] === "wrong" && (
                      <button type="button" className="btn btn-secondary" onClick={onRetryQuiz} disabled={quizCheckLoading}>
                        Попробовать еще раз
                      </button>
                    )}
                  </div>

                  {quizCheckState[activeBlock.id] === "correct" && (
                    <div className="status-box">Ответ принят.</div>
                  )}
                  {quizCheckState[activeBlock.id] === "wrong" && (
                    <div className="status-box status-box-error">
                      Есть неточности в ответах. Нажмите «Попробовать еще раз», ответы сбросятся, и попробуйте заново.
                    </div>
                  )}
                </div>
              )}

              {isCodeTask && activeBlock.taskId && (
                <div className="lesson-practice-block">
                  {practiceLoading && (
                    <div className="skeleton-list">
                      <span className="skeleton-line" />
                      <span className="skeleton-line" />
                    </div>
                  )}

                  {!practiceLoading && practiceTask && (
                    <>
                      <section className="lesson-practice-shell">
                        <div className="lesson-practice-summary">
                          <div className="lesson-practice-badges">
                            <span className="lesson-topic-badge lesson-topic-python">{editorLanguageLabel}</span>
                            <span className="lesson-topic-badge lesson-topic-difficulty">Difficulty {practiceTask.difficulty}</span>
                            <span className="lesson-topic-badge lesson-topic-xp">{practiceTask.xpReward} XP</span>
                          </div>
                        </div>

                        {practiceStatementMd && (
                          <div className="markdown-content lesson-practice-statement">
                            <Markdown>{practiceStatementMd}</Markdown>
                          </div>
                        )}

                        {visiblePracticeExamples.map((example) => (
                          <details key={`${practiceTask.id}:${example.title}`} className="lesson-practice-example-toggle">
                            <summary>{example.title}</summary>
                            <div className="markdown-content lesson-practice-example-body">
                              <Markdown>{example.bodyMd}</Markdown>
                            </div>
                          </details>
                        ))}

                        {practiceInlineHintsMd && (
                          <details className="lesson-practice-inline-hints-toggle">
                            <summary>Подсказки</summary>
                            <div className="markdown-content lesson-practice-inline-hints-body">
                              <Markdown>{practiceInlineHintsMd}</Markdown>
                            </div>
                          </details>
                        )}

                        <div className="lesson-editor-shell">
                          <div className="lesson-editor-toolbar">
                            <div className="lesson-editor-toolbar-copy">
                              <strong>Редактор решения</strong>
                              <p>Напишите решение задачи</p>
                            </div>
                            <div className="lesson-editor-toolbar-right">
                              <span className="lesson-editor-lang-pill">
                                <span className="lesson-editor-lang-dot" aria-hidden="true" />
                                <span>{editorLanguageLabel}</span>
                              </span>
                              <button
                                type="button"
                                className="lesson-editor-expand-btn"
                                onClick={() => setIsEditorExpanded((prev) => !prev)}
                                aria-label={isEditorExpanded ? "Свернуть редактор" : "Развернуть редактор"}
                                title={isEditorExpanded ? "Свернуть редактор" : "Развернуть редактор"}
                              >
                                {isEditorExpanded ? <Minimize2 size={14} strokeWidth={2.2} /> : <Maximize2 size={14} strokeWidth={2.2} />}
                              </button>
                            </div>
                          </div>

                          <div className="task-editor-canvas lesson-editor-canvas">
                            <Editor
                              height={lessonEditorHeight}
                              language={editorLanguage}
                              value={practiceCode}
                              theme={editorTheme}
                              onMount={onEditorMount}
                              onChange={(value) => updatePracticeCode(value ?? "")}
                              options={{
                                fontSize: user?.codeFontSize ?? 15,
                                fontFamily: "'JetBrains Mono', 'SFMono-Regular', 'Consolas', 'Liberation Mono', monospace",
                                fontLigatures: false,
                                fontWeight: "400",
                                lineHeight: 23,
                                letterSpacing: 0,
                                disableMonospaceOptimizations: true,
                                disableLayerHinting: true,
                                padding: { top: 12, bottom: 12 },
                                minimap: { enabled: false },
                                glyphMargin: true,
                                automaticLayout: true,
                                lineNumbersMinChars: 3,
                                tabSize: user?.editorTabSize ?? 4,
                                wordWrap: user?.editorWordWrap ? "on" : "off",
                                renderLineHighlight: "all",
                                cursorSmoothCaretAnimation: "off",
                                cursorBlinking: "blink",
                                smoothScrolling: true,
                                scrollBeyondLastLine: false,
                              }}
                            />
                          </div>

                          <div className="lesson-editor-actions">
                            <div className="lesson-editor-actions-group lesson-editor-actions-group-left">
                              <button type="button" className="btn btn-secondary" onClick={onRunCode} disabled={runLoading || submitLoading}>
                                {runLoading ? "Запуск..." : "Запустить код"}
                              </button>
                              <button type="button" className="btn btn-primary lesson-submit-btn" onClick={onSubmitCode} disabled={runLoading || submitLoading}>
                                {submitLoading ? "Проверяем..." : "Отправить на проверку"}
                              </button>
                            </div>
                            <div className="lesson-editor-actions-group lesson-editor-actions-group-right">
                              <button type="button" className="btn btn-secondary" onClick={onHint} disabled={hintLoading || runLoading || submitLoading}>
                                {hintLoading ? "Готовим подсказку..." : "AI-подсказка"}
                              </button>
                              <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={() => updatePracticeCode(practiceTask.starterCode)}
                                disabled={runLoading || submitLoading}
                              >
                                Сброс к шаблону
                              </button>
                            </div>
                          </div>
                        </div>

                        {practiceMessage && <div className="status-box status-box-error">{practiceMessage}</div>}

                        {runResult && (
                          <section className="task-results">
                            <div className="section-head">
                              <div>
                                <h3>Результат запуска</h3>
                              </div>
                              <span className={statusBadge(runResult.status)}>{ruSubmissionStatus(runResult.status)}</span>
                            </div>

                            {runResult.compileOutput && (
                              <details className="result-block">
                                <summary>Вывод компиляции</summary>
                                <pre>{runResult.compileOutput}</pre>
                              </details>
                            )}

                            {runResult.runLog && (
                              <details className="result-block">
                                <summary>Лог выполнения</summary>
                                <pre>{runResult.runLog}</pre>
                              </details>
                            )}

                            <section className="result-block result-console-block">
                              <h4>Консоль (первый тест)</h4>
                              {Array.isArray(runResult.tests) && runResult.tests.length > 0 ? (
                                <div className="task-test-panel">
                                  <p className="task-test-label">stdin</p>
                                  <pre>{runResult.tests[0]?.input?.length ? runResult.tests[0].input : "(пусто)"}</pre>
                                  <p className="task-test-label">stdout</p>
                                  <pre>{runResult.tests[0]?.actual?.length ? runResult.tests[0].actual : "(пусто)"}</pre>
                                  {runResult.tests[0]?.error && (
                                    <>
                                      <p className="task-test-label">stderr</p>
                                      <pre>{runResult.tests[0].error}</pre>
                                    </>
                                  )}
                                </div>
                              ) : (
                                <p className="task-console-empty">Нет данных запуска. Проверьте код и попробуйте снова.</p>
                              )}
                            </section>
                          </section>
                        )}

                        {submitResult && (
                          <section className="task-results">
                            <div className="section-head">
                              <div>
                                <h3>Результат отправки</h3>
                              </div>
                              <span className={statusBadge(submitResult.status)}>{ruSubmissionStatus(submitResult.status)}</span>
                            </div>

                            <div className="task-result-score">
                              <span>Score</span>
                              <strong>{submitResult.score}</strong>
                            </div>

                            {(() => {
                              const hint = submissionOutcomeHint(submitResult.status);
                              if (!hint) return null;
                              return <div className={hint.className}>{hint.text}</div>;
                            })()}

                            {submitResult.compileOutput && String(submitResult.status ?? "").toLowerCase() === "wrong_answer" && (
                              <div className="status-box">{submitResult.compileOutput}</div>
                            )}

                            {submitResult.compileOutput && String(submitResult.status ?? "").toLowerCase() !== "wrong_answer" && (
                              <details className="result-block">
                                <summary>Вывод компиляции</summary>
                                <pre>{submitResult.compileOutput}</pre>
                              </details>
                            )}

                            {submitResult.runLog && (
                              <details className="result-block">
                                <summary>Лог выполнения</summary>
                                <pre>{submitResult.runLog}</pre>
                              </details>
                            )}

                            {submitResult.referenceCode && String(submitResult.status ?? "").toLowerCase() === "accepted" && (
                              <details className="result-block">
                                <summary>Эталонный код</summary>
                                <pre>{submitResult.referenceCode}</pre>
                              </details>
                            )}
                          </section>
                        )}

                        {hint && (
                          <section className="surface markdown-content">
                            <div className="section-head">
                              <div>
                                <h3>AI-подсказка</h3>
                              </div>
                            </div>
                            <Markdown>{hint}</Markdown>
                          </section>
                        )}

                        {styleHints.length > 0 && (
                          <section className="surface style-hints-panel">
                            <div className="section-head">
                              <div>
                                <h3>Подсказки по стилю</h3>
                                <p>Наведите курсор на лампочку слева от строки в редакторе.</p>
                              </div>
                            </div>
                          </section>
                        )}
                      </section>
                    </>
                  )}
                </div>
              )}

              {isCodeTaskWithoutTask && (
                <div className="status-box">
                  Для этого шага пока нет автопроверки. Используйте материал шага и переходите дальше.
                </div>
              )}

              <div className="lesson-step-footer">
                {hasNextBlock ? (
                  <button
                    type="button"
                    className="btn btn-primary lesson-next-btn"
                    onClick={() => setActiveBlockIndex((prev) => Math.min(prev + 1, blocks.length - 1))}
                  >
                    Дальше
                    <ArrowRight size={16} strokeWidth={2.4} />
                  </button>
                ) : (
                  <Link to="/courses" className="btn btn-primary lesson-next-btn">
                    К курсам
                    <ArrowRight size={16} strokeWidth={2.4} />
                  </Link>
                )}
              </div>
            </>
          )}
        </article>
      </section>
    </div>
  );
}
