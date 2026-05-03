import { resolveCourseIconKey, type CourseMeta, type CourseIconKey } from "./courseIconKey";

export type CoursePresentationMeta = CourseMeta & {
  displayTitle?: string | null;
  shortTitle?: string | null;
  shortDescription?: string | null;
};

const TITLE_BY_ICON: Record<CourseIconKey, string> = {
  python: "Python Backend",
  frontend: "Frontend с нуля",
  java: "Java Backend",
  go: "Go Backend",
  default: "",
};

const DESCRIPTION_BY_ICON: Partial<Record<CourseIconKey, string>> = {
  python: "Python Core, Git, ООП, SQL, FastAPI, Docker и финальный backend-проект.",
  frontend: "HTML, CSS, JavaScript, TypeScript, React и практические проекты.",
  java: "Java Core, ООП, SQL, Spring Boot и DevOps-практика.",
  go: "Go Core, concurrency, SQL, HTTP и backend-практика.",
};

const INTERNAL_VERSION_PATTERN = /\b(?:v(?:ersion)?\s*\d+(?:\.\d+)*|v\d+(?:\.\d+)*)\b/gi;
const INTERNAL_NOISE_PATTERN = /\b(?:polished|internal|debug|draft|staging|hotfix|preview|beta)\b/gi;

function normalizeText(value?: string | null): string {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function trimDescription(value: string, maxLength = 116): string {
  if (value.length <= maxLength) return value;
  const shortened = value.slice(0, maxLength);
  const spaceIndex = shortened.lastIndexOf(" ");
  const safe = spaceIndex > 60 ? shortened.slice(0, spaceIndex) : shortened;
  return `${safe.trim()}...`;
}

export function stripInternalCourseTitle(rawTitle?: string | null): string {
  const normalized = normalizeText(rawTitle);
  if (!normalized) return "";

  const compact = normalized
    .replace(/\s*(?:\(|\[|\{).*(?:\)|\]|\})\s*$/g, " ")
    .replace(INTERNAL_VERSION_PATTERN, " ")
    .replace(INTERNAL_NOISE_PATTERN, " ")
    .replace(/\s*(?:—|-)\s*(?:version|build|release)\b.*$/i, " ")
    .replace(/\s{2,}/g, " ")
    .replace(/\s*(?:—|-)\s*$/g, "")
    .trim();

  if (compact) return compact;
  return normalized.split(/[—-]/)[0]?.trim() || normalized;
}

function deriveDisplayTitle(course: CoursePresentationMeta): string {
  const iconKey = resolveCourseIconKey(course);
  const mappedTitle = TITLE_BY_ICON[iconKey];
  if (mappedTitle) return mappedTitle;

  const stripped = stripInternalCourseTitle(course.title);
  if (stripped) {
    const beforeDash = stripped.split(/[—-]/)[0]?.trim();
    return beforeDash || stripped;
  }
  return "Курс";
}

export function getCourseDisplayTitle(course: CoursePresentationMeta): string {
  const displayTitle = normalizeText(course.displayTitle);
  if (displayTitle) return displayTitle;

  const shortTitle = normalizeText(course.shortTitle);
  if (shortTitle) return shortTitle;

  return deriveDisplayTitle(course);
}

export function getCourseShortTitle(course: CoursePresentationMeta): string {
  const shortTitle = normalizeText(course.shortTitle);
  if (shortTitle) return shortTitle;

  const displayTitle = normalizeText(course.displayTitle);
  if (displayTitle) return displayTitle;

  return deriveDisplayTitle(course);
}

export function getCourseShortDescription(course: CoursePresentationMeta): string {
  const explicit = normalizeText(course.shortDescription);
  if (explicit) return explicit;

  const description = normalizeText(course.description);
  if (!description) {
    return DESCRIPTION_BY_ICON[resolveCourseIconKey(course)] ?? "";
  }

  const cleaned = description
    .replace(INTERNAL_VERSION_PATTERN, " ")
    .replace(INTERNAL_NOISE_PATTERN, " ")
    .replace(/\s{2,}/g, " ")
    .replace(/\s*[—-]\s*version\b.*$/i, "")
    .trim();

  if (!cleaned) {
    return DESCRIPTION_BY_ICON[resolveCourseIconKey(course)] ?? "";
  }

  return trimDescription(cleaned);
}
