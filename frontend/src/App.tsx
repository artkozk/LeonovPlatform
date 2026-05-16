import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AdminPage } from "./pages/AdminPage";
import { AdminSupportPage } from "./pages/AdminSupportPage";
import { AuthPage } from "./pages/AuthPage";
import { BillingPage } from "./pages/BillingPage";
import { ChecksPage } from "./pages/ChecksPage";
import { CoursesPage } from "./pages/CoursesPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LeaderboardPage } from "./pages/LeaderboardPage";
import { LessonPage } from "./pages/LessonPage";
import { ProfilePage } from "./pages/ProfilePage";
import { SupportPage } from "./pages/SupportPage";
import { TaskPage } from "./pages/TaskPage";
import { TasksPage } from "./pages/TasksPage";
import { useAuthStore } from "./store/auth";

function ShellPage({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <AppLayout>{children}</AppLayout>
    </ProtectedRoute>
  );
}

function AdminRoute() {
  const user = useAuthStore((s) => s.user);
  if (user?.role !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }
  return (
    <ShellPage>
      <AdminPage />
    </ShellPage>
  );
}

function AdminSupportRoute() {
  const user = useAuthStore((s) => s.user);
  if (user?.role !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }
  return (
    <ShellPage>
      <AdminSupportPage />
    </ShellPage>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/auth" element={<AuthPage />} />

      <Route path="/dashboard" element={<ShellPage><DashboardPage /></ShellPage>} />
      <Route path="/courses" element={<ShellPage><CoursesPage /></ShellPage>} />
      <Route path="/tasks" element={<ShellPage><TasksPage /></ShellPage>} />
      <Route path="/checks" element={<ShellPage><ChecksPage /></ShellPage>} />
      <Route path="/leaderboard" element={<ShellPage><LeaderboardPage /></ShellPage>} />
      <Route path="/lessons/:lessonId" element={<ShellPage><LessonPage /></ShellPage>} />
      <Route path="/tasks/:taskId" element={<ShellPage><TaskPage /></ShellPage>} />
      <Route path="/profile" element={<ShellPage><ProfilePage /></ShellPage>} />
      <Route path="/billing" element={<ShellPage><BillingPage /></ShellPage>} />
      <Route path="/support" element={<ShellPage><SupportPage /></ShellPage>} />
      <Route path="/admin" element={<AdminRoute />} />
      <Route path="/admin/support" element={<AdminSupportRoute />} />

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
    </ErrorBoundary>
  );
}
