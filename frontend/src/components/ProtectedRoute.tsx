import { Navigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

// ProtectedRoute защищает любой маршрут, требующий валидной сессии.
//
// Важная деталь (исправлено 2026-05-12, см. docs/operations/AUTH_BOOTSTRAP_FLASH_FIX_2026_05_12.md):
// первый render приложения происходит до того, как успевает завершиться
// `bootstrap()` (вызов GET /me). Если в этот момент уже отрендерить
// `<Navigate to="/auth">` — пользователь со включённой сессией на долю
// секунды видит форму логина, после чего его перебрасывает обратно.
//
// Чтобы избежать этой "вспышки", мы:
//   1. Ждём, пока auth-store выставит `bootstrapped: true`.
//      До этого момента показываем пустой плейсхолдер (а не редирект).
//   2. Только после `bootstrapped: true` принимаем решение —
//      рендерить контент или редиректить на /auth.
//
// Если токена в localStorage нет, `bootstrapped` инициализируется как
// `true` сразу (см. store/auth.ts), и редирект работает мгновенно — без
// бесполезной задержки.
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const bootstrapped = useAuthStore((s) => s.bootstrapped);

  if (!bootstrapped) {
    // Сессия ещё проверяется. Не рендерим ничего, чтобы избежать
    // короткой "вспышки" формы /auth (см. шапку файла).
    return null;
  }

  if (!user) {
    return <Navigate to="/auth" replace />;
  }
  return <>{children}</>;
}
