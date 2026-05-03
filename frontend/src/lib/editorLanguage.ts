export type SupportedLanguage = "python" | "html" | "go" | "java";

export type EditorLanguageMode = SupportedLanguage | "sql" | "plaintext";

function cleanLanguageToken(input?: string | null): string {
  return String(input ?? "")
    .trim()
    .toLowerCase();
}

export function normalizeLanguage(input?: string | null): SupportedLanguage | null {
  const token = cleanLanguageToken(input);
  if (!token) return null;
  if (token === "python" || token === "python3" || token === "py") return "python";
  if (token === "html" || token === "html5") return "html";
  if (token === "go" || token === "golang") return "go";
  if (token === "java") return "java";
  return null;
}

function normalizeEditorMode(input?: string | null): EditorLanguageMode | null {
  const supported = normalizeLanguage(input);
  if (supported) return supported;

  const token = cleanLanguageToken(input);
  if (!token) return null;
  if (token === "sql" || token === "postgresql" || token === "postgres") return "sql";
  return null;
}

export function resolveEditorLanguage(values: Array<string | null | undefined>): EditorLanguageMode {
  for (const value of values) {
    const normalized = normalizeEditorMode(value);
    if (normalized) return normalized;
  }
  return "python";
}

export function getEditorLanguageMode(values: Array<string | null | undefined>): EditorLanguageMode {
  return resolveEditorLanguage(values);
}

export function getEditorLanguageLabel(values: Array<string | null | undefined>): string {
  const mode = resolveEditorLanguage(values);
  if (mode === "python") return "Python 3";
  if (mode === "html") return "HTML";
  if (mode === "go") return "Go";
  if (mode === "java") return "Java";
  if (mode === "sql") return "SQL";
  return "Код";
}
