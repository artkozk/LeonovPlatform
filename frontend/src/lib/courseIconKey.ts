export type CourseIconKey = "python" | "java" | "go" | "frontend" | "default";

export type CourseMeta = {
  direction?: string | null;
  track?: string | null;
  language?: string | null;
  slug?: string | null;
  title?: string | null;
  description?: string | null;
};

function normalizeToken(value?: string | null): string {
  return String(value ?? "").trim().toLowerCase();
}

function detectFromSource(source: string): CourseIconKey | null {
  if (!source) return null;

  if (/\b(frontend|front-end|web|html|css|javascript|java-script|js|typescript|type-script|ts|react)\b/i.test(source)) {
    return "frontend";
  }

  if (/\bjava\b/i.test(source) && !/\b(javascript|java-script)\b/i.test(source)) {
    return "java";
  }

  if (/\b(python|py)\b/i.test(source)) {
    return "python";
  }

  if (/\b(go|golang)\b/i.test(source)) {
    return "go";
  }

  return null;
}

function mergeTitleAndDescription(meta?: CourseMeta): string {
  const title = normalizeToken(meta?.title);
  const description = normalizeToken(meta?.description);
  return `${title} ${description}`.trim();
}

function pickByPriority(meta?: CourseMeta): CourseIconKey | null {
  const sources = [
    normalizeToken(meta?.direction),
    normalizeToken(meta?.track),
    normalizeToken(meta?.language),
    normalizeToken(meta?.slug),
    mergeTitleAndDescription(meta),
  ];

  for (const source of sources) {
    const key = detectFromSource(source);
    if (key) return key;
  }

  return null;
}

function hasPythonSlugHint(slug: string): boolean {
  return slug.includes("python");
}

function hasGoSlugHint(slug: string): boolean {
  return slug.includes("go-") || slug.includes("go_") || slug === "go";
}

function hasJavaSlugHint(slug: string): boolean {
  return slug === "java" || slug.startsWith("java-") || slug.startsWith("java_");
}

function hasFrontendSlugHint(slug: string): boolean {
  return slug.includes("frontend") || slug.includes("front-end") || slug.includes("html") || slug.includes("javascript") || slug.includes("typescript");
}

function fallbackBySlug(meta?: CourseMeta): CourseIconKey | null {
  const slug = normalizeToken(meta?.slug);
  if (!slug) return null;

  if (hasFrontendSlugHint(slug)) return "frontend";
  if (hasJavaSlugHint(slug) && !/\b(javascript|java-script)\b/i.test(slug)) return "java";
  if (hasPythonSlugHint(slug)) return "python";
  if (hasGoSlugHint(slug)) return "go";

  return null;
}

function fallbackByMergedContent(meta?: CourseMeta): CourseIconKey | null {
  const merged = mergeTitleAndDescription(meta);
  if (!merged) return null;

  if (/\b(spring|jdk|jdbc)\b/i.test(merged)) return "java";
  if (/\b(golang|concurrency|goroutine)\b/i.test(merged)) return "go";
  if (/\bpython\b/i.test(merged)) return "python";
  return null;
}

export function resolveCourseIconKey(meta?: CourseMeta): CourseIconKey {
  const priorityMatch = pickByPriority(meta);
  if (priorityMatch) return priorityMatch;

  const slugFallback = fallbackBySlug(meta);
  if (slugFallback) return slugFallback;

  const contentFallback = fallbackByMergedContent(meta);
  if (contentFallback) return contentFallback;

  return "default";
}
