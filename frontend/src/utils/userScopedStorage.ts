const USER_SCOPED_PREFIXES = [
  "lc_lesson_progress_",
  "lc_courses_screen_cache_",
  "lc_task_draft_",
  "lc_lesson_code_drafts_",
];

function normalizeUserId(userId?: string | null): string {
  const trimmed = String(userId ?? "").trim();
  return trimmed || "anon";
}

export function buildLessonProgressKey(userId: string | null | undefined, lessonId: string): string {
  return `lc_lesson_progress_${normalizeUserId(userId)}_${lessonId}`;
}

export function buildCoursesScreenCacheKey(userId: string | null | undefined): string {
  return `lc_courses_screen_cache_${normalizeUserId(userId)}_v3`;
}

export function clearAllUserScopedStorage() {
  if (typeof window === "undefined") return;
  try {
    const keysToDelete: string[] = [];
    for (let index = 0; index < localStorage.length; index += 1) {
      const key = localStorage.key(index);
      if (key && USER_SCOPED_PREFIXES.some((prefix) => key.startsWith(prefix))) {
        keysToDelete.push(key);
      }
    }
    keysToDelete.forEach((key) => localStorage.removeItem(key));
  } catch {
    // ignore storage access issues
  }
}
