import Editor from "@monaco-editor/react";
import Markdown from "react-markdown";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { getSubmission, getTask, runTask, submitTask, taskHint } from "../api/client";
import { useIsSmallViewport } from "../hooks/useIsSmallViewport";
import { analyzePythonStyleHints } from "../lib/codeStyleHints";
import { getEditorLanguageLabel, getEditorLanguageMode } from "../lib/editorLanguage";
import { stabilizeMonacoLayout } from "../lib/stabilizeMonacoLayout";
import { useAuthStore } from "../store/auth";

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

type SubmissionEntity = {
  id: string;
  status: string;
  score: number;
  compileOutput?: string | null;
  runLog?: string | null;
  feedback?: unknown;
  referenceCode?: string | null;
};

type RunEntity = {
  status: string;
  score: number;
  compileOutput?: string | null;
  runLog?: string | null;
  tests?: Array<{
    index: number;
    passed: boolean;
    input?: string;
    actual?: string;
    error?: string;
  }>;
};

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

function buildTaskDraftStorageKey(userId?: string, taskId?: string): string {
  const normalizedTaskId = String(taskId ?? "").trim();
  if (!normalizedTaskId) return "";
  const normalizedUserId = String(userId ?? "anon").trim() || "anon";
  return `lc_task_draft_${normalizedUserId}_${normalizedTaskId}`;
}

function readTaskDraft(storageKey: string): string | null {
  if (!storageKey) return null;
  try {
    const raw = localStorage.getItem(storageKey);
    if (raw === null) return null;
    return normalizeStarterCode(raw);
  } catch {
    return null;
  }
}

function ruError(raw?: string): string {
  const text = (raw ?? "").trim().toLowerCase();
  if (!text) return "Произошла ошибка. Повторите действие.";
  if (text.includes("internal server error")) return "Проверка не завершилась. Проверьте решение и отправьте снова.";
  if (text.includes("service unavailable")) return "Проверка временно недоступна. Проверьте решение и отправьте снова.";
  if (text.includes("bad gateway")) return "Проверка не завершилась. Проверьте решение и отправьте снова.";
  if (text.includes("timeout")) return "Время проверки истекло. Проверьте решение и отправьте снова.";
  if (text.includes("submission not found")) return "Отправка не найдена. Повторите отправку решения.";
  if (text.includes("task not found")) return "Задача не найдена.";
  if (text.includes("lesson not found")) return "Урок не найден.";
  if (text.includes("course not found")) return "Курс не найден.";
  if (text.includes("daily submission limit reached")) return "Дневной лимит отправок по вашему тарифу исчерпан.";
  if (text.includes("max attempts exceeded")) return "Вы исчерпали лимит попыток для этой задачи.";
  if (text.includes("unauthorized")) return "Сессия истекла. Выполните вход заново.";
  if (text.includes("forbidden")) return "Недостаточно прав для этого действия.";
  if (text.includes("upgrade_required")) return "AI-подсказка доступна только на тарифе Premium.";
  return "Произошла ошибка. Повторите действие.";
}

function normalizeSubmissionStatus(status?: string): string {
  return String(status ?? "").trim().toLowerCase();
}

function isSubmissionPendingStatus(status?: string): boolean {
  const value = normalizeSubmissionStatus(status);
  return value === "queued" || value === "processing";
}

function ruSubmissionStatus(status?: string): string {
  const value = normalizeSubmissionStatus(status);
  if (value === "ran") return "Код выполнен";
  if (value === "queued") return "В очереди";
  if (value === "processing") return "Проверяется";
  if (value === "accepted") return "Принято";
  if (value === "wrong_answer") return "Неверный ответ";
  if (value === "compile_error") return "Ошибка компиляции";
  if (value === "runtime_error") return "Ошибка выполнения";
  if (value === "time_limit") return "Превышен лимит времени";
  if (value === "failed") return "Сбой проверки";
  return status ?? "Неизвестно";
}

function submissionBadge(status?: string) {
  const value = normalizeSubmissionStatus(status);
  if (value === "ran") return "badge badge-success";
  if (value === "accepted") return "badge badge-success";
  if (value === "processing") return "badge badge-warning";
  if (value === "queued") return "badge badge-warning";
  if (value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit" || value === "failed") return "badge badge-error";
  return "badge badge-neutral";
}

function submissionOutcomeHint(status?: string): { text: string; className: string } | null {
  const value = normalizeSubmissionStatus(status);
  if (value === "wrong_answer" || value === "compile_error" || value === "runtime_error" || value === "time_limit") {
    return {
      text: "Это ошибка в вашем коде, а не в системе проверки. Исправьте решение по логу и отправьте снова.",
      className: "status-box status-box-error",
    };
  }
  if (value === "failed") {
    return {
      text: "Проверка не завершилась. Проверьте решение по логу и отправьте снова.",
      className: "status-box status-box-error",
    };
  }
  return null;
}

export function TaskPage() {
  const { taskId } = useParams();
  const [searchParams] = useSearchParams();
  const user = useAuthStore((s) => s.user);
  const isCodingLockedOnCurrentDevice = useIsSmallViewport(1024);

  const [task, setTask] = useState<TaskEntity | null>(null);
  const [code, setCode] = useState("");
  const [submission, setSubmission] = useState<SubmissionEntity | null>(null);
  const [runResult, setRunResult] = useState<RunEntity | null>(null);
  const [taskLoading, setTaskLoading] = useState(false);
  const [taskError, setTaskError] = useState("");
  const [polling, setPolling] = useState(false);
  const [runLoading, setRunLoading] = useState(false);
  const [hintLoading, setHintLoading] = useState(false);
  const [hint, setHint] = useState("");
  const [toast, setToast] = useState("");
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const decorationIDsRef = useRef<string[]>([]);
  const editorLayoutCleanupRef = useRef<(() => void) | null>(null);
  const submissionPollingAbortRef = useRef<boolean>(false);
  const taskDraftStorageKey = useMemo(() => buildTaskDraftStorageKey(user?.id, taskId), [user?.id, taskId]);
  const submissionIdFromQuery = useMemo(() => String(searchParams.get("submissionId") ?? "").trim(), [searchParams]);

  const loadTask = useCallback(async (currentTaskId: string) => {
    setTaskLoading(true);
    setTaskError("");
    try {
      const data = await getTask(currentTaskId);
      const normalized: TaskEntity = {
        id: String(data.task.id),
        title: String(data.task.title ?? "Задача"),
        statementMd: String(data.task.statementMd ?? ""),
        starterCode: normalizeStarterCode(data.task.starterCode),
        difficulty: Number(data.task.difficulty ?? 1),
        xpReward: Number(data.task.xpReward ?? 0),
        topic: String(data.task.topic ?? "General"),
        language: String(data.task.language ?? data.task.lang ?? ""),
        taskLanguage: String(data.task.language ?? data.task.lang ?? ""),
        lessonLanguage: String(data.lesson?.language ?? data.lesson?.lang ?? ""),
        moduleLanguage: String(data.module?.language ?? data.module?.lang ?? ""),
        courseLanguage: String(data.course?.language ?? data.course?.lang ?? ""),
        courseTrack: String(data.course?.track ?? data.course?.stack ?? ""),
        direction: String(data.direction ?? data.course?.direction ?? ""),
      };
      setTask(normalized);
      const savedDraft = readTaskDraft(buildTaskDraftStorageKey(user?.id, currentTaskId));
      setCode(savedDraft ?? normalized.starterCode);
      setSubmission(null);
      setRunResult(null);
      setHint("");
      setToast("");
    } catch (error: any) {
      setTask(null);
      setTaskError(ruError(error?.response?.data?.error ?? "Не удалось загрузить задачу"));
    } finally {
      setTaskLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    if (!taskId) return;
    void loadTask(taskId);
  }, [taskId, loadTask]);

  useEffect(() => {
    if (!taskId || !submissionIdFromQuery) return;

    let cancelled = false;

    async function loadSubmissionFromQuery() {
      try {
        const current = await getSubmission(submissionIdFromQuery);
        if (!cancelled) {
          setSubmission(current);
        }
      } catch {
        // ignore invalid/expired query submission id; task page remains usable
      }
    }

    void loadSubmissionFromQuery();
    return () => {
      cancelled = true;
    };
  }, [taskId, submissionIdFromQuery]);

  async function onRun() {
    if (!taskId) return;

    setRunLoading(true);
    setRunResult(null);
    setToast("");

    try {
      const result = (await runTask(taskId, code)) as RunEntity;
      setRunResult(result);
    } catch (error: any) {
      setToast(ruError(error?.response?.data?.error ?? "Не удалось запустить код"));
    } finally {
      setRunLoading(false);
    }
  }

  async function onSubmit() {
    if (!taskId) return;

    setSubmission(null);
    setRunResult(null);
    setToast("Решение отправлено в очередь проверки.");
    submissionPollingAbortRef.current = false;

    try {
      const queued = await submitTask(taskId, code);
      setPolling(true);
      let attempts = 0;

      while (attempts < 45) {
        if (submissionPollingAbortRef.current) return;
        const current = await getSubmission(queued.submissionId);
        if (submissionPollingAbortRef.current) return;
        setSubmission(current);

        if (!isSubmissionPendingStatus(current?.status)) {
          setPolling(false);
          return;
        }

        attempts += 1;
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }

      setPolling(false);
      setToast("Проверка заняла больше времени. Обновите страницу через несколько секунд.");
    } catch (error: any) {
      if (submissionPollingAbortRef.current) return;
      setPolling(false);
      setToast(ruError(error?.response?.data?.error ?? "Не удалось отправить решение"));
    }
  }

  async function onHint() {
    if (!taskId) return;
    setHintLoading(true);
    setToast("");

    try {
      const data = await taskHint(taskId, code);
      setHint(String(data?.hint ?? "Подсказка недоступна."));
    } catch (error: any) {
      setToast(ruError(error?.response?.data?.error ?? "Не удалось получить AI-подсказку"));
    } finally {
      setHintLoading(false);
    }
  }

  const updateCode = useCallback((nextCode: string) => {
    setCode(nextCode);
    setRunResult(null);
    setSubmission(null);
    setHint("");
    setToast("");
    if (taskDraftStorageKey) {
      try {
        localStorage.setItem(taskDraftStorageKey, nextCode);
      } catch {
        // ignore localStorage quota/access issues; editor state remains in memory
      }
    }
  }, [taskDraftStorageKey]);

  const editorTheme = "light";
  const languageSources = useMemo(
    () => [
      task?.taskLanguage,
      task?.language,
      task?.lessonLanguage,
      task?.moduleLanguage,
      task?.courseLanguage,
      task?.courseTrack,
      task?.direction,
    ],
    [task]
  );
  const editorLanguage = useMemo(() => getEditorLanguageMode(languageSources), [languageSources]);
  const editorLanguageLabel = useMemo(() => getEditorLanguageLabel(languageSources), [languageSources]);
  const editorCheckLabel = useMemo(() => {
    if (editorLanguage === "sql") return "автопроверка SQL по эталонному запросу";
    return "автопроверка через stdin → stdout";
  }, [editorLanguage]);

  const shouldShowStyleHints = useMemo(() => {
    const submitAccepted = String(submission?.status ?? "").toLowerCase() === "accepted";
    return submitAccepted;
  }, [submission?.status]);

  const styleHints = useMemo(() => {
    if (!shouldShowStyleHints) return [];
    if (editorLanguage !== "python") return [];
    return analyzePythonStyleHints(code);
  }, [shouldShowStyleHints, editorLanguage, code]);

  const applyStyleHintDecorations = useCallback(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    const model = editor?.getModel?.();
    if (!editor || !monaco || !model) return;

    if (!styleHints.length) {
      decorationIDsRef.current = editor.deltaDecorations(decorationIDsRef.current, []);
      return;
    }

    const nextDecorations = styleHints.map((hintItem) => ({
      range: new monaco.Range(hintItem.line, 1, hintItem.line, 1),
      options: {
        isWholeLine: true,
        glyphMarginClassName: "editor-style-hint-glyph",
        glyphMarginHoverMessage: { value: hintItem.message },
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
      submissionPollingAbortRef.current = true;
    };
  }, []);

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

  function onEditorMount(editor: any, monaco: any) {
    editorRef.current = editor;
    monacoRef.current = monaco;
    editorLayoutCleanupRef.current?.();
    editorLayoutCleanupRef.current = stabilizeMonacoLayout(editor, monaco);
    applyStyleHintDecorations();
  }

  if (taskLoading) {
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

  if (taskError) {
    return (
      <div className="page-stack">
        <section className="surface empty-state">
          <h3>Ошибка загрузки задачи</h3>
          <p>{taskError}</p>
          {taskId && (
            <button type="button" className="btn btn-primary" onClick={() => loadTask(taskId)}>
              Повторить
            </button>
          )}
        </section>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="page-stack">
        <section className="surface empty-state">
          <h3>Задача не найдена</h3>
          <p>Проверьте ссылку или откройте задачу из каталога.</p>
        </section>
      </div>
    );
  }

  if (isCodingLockedOnCurrentDevice) {
    return (
      <div className="task-page page-stack">
        <section className="surface coding-desktop-guard">
          <span className="section-kicker">Только ПК</span>
          <h1>Решение задач с кодом доступно с большого экрана</h1>
          <p>На телефоне редактор и отправка отключены. Это сделано, чтобы вы не теряли прогресс из-за неудобного ввода.</p>
          <div className="coding-desktop-guard-actions">
            <Link to="/tasks" className="btn btn-primary">К списку задач</Link>
            <Link to="/courses" className="btn btn-secondary">К курсам</Link>
          </div>
        </section>

        <section className="surface markdown-content">
          <h2>Условие задачи</h2>
          <Markdown>{task.statementMd}</Markdown>
        </section>
      </div>
    );
  }

  return (
    <div className="task-page page-stack">
      <section className="surface hero-surface task-hero">
        <div className="hero-copy">
          <span className="section-kicker">Code step</span>
          <h1>{task.title}</h1>
          <p>Решите задачу в редакторе справа и отправьте код на автоматическую проверку.</p>
        </div>
        <div className="hero-stats">
          <div className="hero-stat-item">
            <span>Сложность</span>
            <strong>{task.difficulty}</strong>
          </div>
          <div className="hero-stat-item">
            <span>Награда</span>
            <strong>{task.xpReward} XP</strong>
          </div>
          <div className="hero-stat-item">
            <span>Тема</span>
            <strong>{task.topic}</strong>
          </div>
        </div>
      </section>

      <section className="task-workspace">
        <article className="surface task-statement markdown-content">
          <h2>Условие</h2>
          <Markdown>{task.statementMd}</Markdown>
        </article>

        <article className="surface task-editor task-editor-shell">
          <div className="task-editor-toolbar">
            <div className="task-editor-toolbar-copy">
              <h2>Редактор решения</h2>
              <p>Напишите решение задачи</p>
            </div>
            <div className="task-editor-toolbar-right">
              <span className="task-editor-language-pill" aria-label={`Язык: ${editorLanguageLabel}`}>
                <span className="task-editor-language-dot" aria-hidden="true" />
                <span>{editorLanguageLabel}</span>
              </span>
            </div>
          </div>

          <div className="task-editor-canvas">
            <Editor
              height="420px"
              defaultLanguage={editorLanguage}
              language={editorLanguage}
              value={code}
              theme={editorTheme}
              onMount={onEditorMount}
              onChange={(v) => updateCode(v ?? "")}
              options={{
                fontSize: user?.codeFontSize ?? 14,
                fontFamily: "'JetBrains Mono', 'SFMono-Regular', 'Consolas', 'Liberation Mono', monospace",
                fontLigatures: false,
                fontWeight: "400",
                lineHeight: 22,
                letterSpacing: 0,
                disableMonospaceOptimizations: true,
                disableLayerHinting: true,
                minimap: { enabled: false },
                glyphMargin: true,
                tabSize: user?.editorTabSize ?? 4,
                wordWrap: user?.editorWordWrap ? "on" : "off",
                cursorSmoothCaretAnimation: "off",
                cursorBlinking: "blink",
                smoothScrolling: true,
                scrollBeyondLastLine: false,
              }}
            />
          </div>

          <div className="task-editor-actions" aria-label={`Проверка: ${editorCheckLabel}`}>
            <div className="task-editor-actions-group task-editor-actions-group-left">
              <button type="button" className="btn btn-secondary" onClick={onRun} disabled={polling || runLoading}>
                {runLoading ? "Запуск..." : "Запустить код"}
              </button>
              <button type="button" className="btn btn-primary" onClick={onSubmit} disabled={polling || runLoading}>
                {polling ? "Проверяем..." : "Отправить на проверку"}
              </button>
            </div>
            <div className="task-editor-actions-group task-editor-actions-group-right">
              <button type="button" className="btn btn-secondary" onClick={onHint} disabled={hintLoading || polling || runLoading}>
                {hintLoading ? "Готовим подсказку..." : "AI-подсказка"}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => updateCode(task.starterCode)} disabled={polling || runLoading}>
                Сброс к шаблону
              </button>
            </div>
          </div>
        </article>
      </section>

      {toast && <div className="status-box">{toast}</div>}

      {runResult && (
        <section className="surface task-results">
          <div className="section-head">
            <div>
              <h2>Результат запуска</h2>
              <p>Предпросмотр выполнения кода до отправки решения.</p>
            </div>
            <span className={submissionBadge(runResult.status)}>{ruSubmissionStatus(runResult.status)}</span>
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

      {submission && (
        <section className="surface task-results">
          <div className="section-head">
            <div>
              <h2>Результат проверки</h2>
              <p>Статус и технические детали выполнения.</p>
            </div>
            <span className={submissionBadge(submission.status)}>{ruSubmissionStatus(submission.status)}</span>
          </div>

          <div className="task-result-score">
            <span>Score</span>
            <strong>{submission.score}</strong>
          </div>

          {(() => {
            const hint = submissionOutcomeHint(submission.status);
            if (!hint) return null;
            return <div className={hint.className}>{hint.text}</div>;
          })()}

          {submission.compileOutput && String(submission.status ?? "").toLowerCase() === "wrong_answer" && (
            <div className="status-box">{submission.compileOutput}</div>
          )}

          {submission.compileOutput && String(submission.status ?? "").toLowerCase() !== "wrong_answer" && (
            <details className="result-block">
              <summary>Вывод компилятора</summary>
              <pre>{submission.compileOutput}</pre>
            </details>
          )}

          {submission.runLog && (
            <details className="result-block">
              <summary>Лог выполнения</summary>
              <pre>{submission.runLog}</pre>
            </details>
          )}

          {submission.feedback && (
            <details className="result-block">
              <summary>Детали проверки</summary>
              <pre>{typeof submission.feedback === "string" ? submission.feedback : JSON.stringify(submission.feedback, null, 2)}</pre>
            </details>
          )}

          {submission.referenceCode && String(submission.status ?? "").toLowerCase() === "accepted" && (
            <details className="result-block">
              <summary>Эталонный код</summary>
              <pre>{submission.referenceCode}</pre>
            </details>
          )}
        </section>
      )}

      {hint && (
        <section className="surface markdown-content">
          <div className="section-head">
            <div>
              <h2>AI-подсказка</h2>
              <p>Сфокусируйтесь на подходе, а не на готовом ответе.</p>
            </div>
          </div>
          <Markdown>{hint}</Markdown>
        </section>
      )}

      {styleHints.length > 0 && (
        <section className="surface style-hints-panel">
          <div className="section-head">
            <div>
              <h2>Подсказки по стилю</h2>
              <p>Наведите курсор на лампочку слева от строки в редакторе.</p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
