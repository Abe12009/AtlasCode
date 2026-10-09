import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { MotionConfig } from 'framer-motion';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoadingFallback } from './components/LoadingFallback';
import { lazy, Suspense, useEffect } from 'react';
import { useTranslation } from './hooks/useTranslation';
import { RouteErrorBoundary } from './components/RouteErrorBoundary';

const Landing = lazy(() => import('./pages/Landing').then(m => ({ default: m.Landing })));
const Login = lazy(() => import('./pages/Login').then(m => ({ default: m.Login })));
const Register = lazy(() => import('./pages/Register').then(m => ({ default: m.Register })));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword').then(m => ({ default: m.ForgotPassword })));
const ResetPassword = lazy(() => import('./pages/ResetPassword').then(m => ({ default: m.ResetPassword })));
const Privacy = lazy(() => import('./pages/Privacy').then(m => ({ default: m.Privacy })));
const Terms = lazy(() => import('./pages/Terms').then(m => ({ default: m.Terms })));
const Contact = lazy(() => import('./pages/Contact').then(m => ({ default: m.Contact })));
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const Courses = lazy(() => import('./pages/Courses').then(m => ({ default: m.Courses })));
const CourseDetail = lazy(() => import('./pages/CourseDetail').then(m => ({ default: m.CourseDetail })));
const LessonDetail = lazy(() => import('./pages/LessonDetail').then(m => ({ default: m.LessonDetail })));
const Projects = lazy(() => import('./pages/Projects').then(m => ({ default: m.Projects })));
const ProjectDetail = lazy(() => import('./pages/ProjectDetail').then(m => ({ default: m.ProjectDetail })));
const Profile = lazy(() => import('./pages/Profile').then(m => ({ default: m.Profile })));
const Cody = lazy(() => import('./pages/Cody').then(m => ({ default: m.Cody })));
const PublicProfile = lazy(() => import('./pages/PublicProfile').then(m => ({ default: m.PublicProfile })));
const VisualProgrammingPage = lazy(() => import('./pages/VisualProgramming').then(m => ({ default: m.VisualProgrammingPage })));
const DuelLobby = lazy(() => import('./pages/DuelLobby').then(m => ({ default: m.DuelLobby })));
const DuelArena = lazy(() => import('./pages/DuelArena').then(m => ({ default: m.DuelArena })));

const Layout = lazy(() => import('./components/Layout').then(m => ({ default: m.Layout })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingFallback />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingFallback />;
  }

  if (user) {
    return <Navigate to="/app/dashboard" replace />;
  }

  return <>{children}</>;
}

/**
 * Every lazy route's element: Suspense for the import, RouteErrorBoundary for
 * a render throw.
 *
 * Suspense alone only covers loading. A component that throws while rendering
 * unmounts the tree and leaves a blank page served with a 200 -- the failure
 * mode Visual Programming hit, and one all 21 lazy routes shared.
 *
 * `key={pathname}` is load-bearing. An error boundary keeps its error state
 * until it unmounts, and a parameterised route (lessons/:lessonId,
 * courses/:courseId, ...) reuses the same element instance across param
 * changes -- so without the key, one bad lesson would leave every later
 * lesson showing the error page until a full reload. Keying on the path
 * remounts the boundary per navigation.
 *
 * The providers (QueryClient, Auth, MotionConfig) live above <AppRoutes/>, so
 * none of them is unmounted by a route error: the session and the query cache
 * survive, and for /app routes the Layout chrome stays rendered so the user
 * can navigate away.
 */
function GuardedRoute({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  return (
    <RouteErrorBoundary key={pathname}>
      <Suspense fallback={<LoadingFallback />}>{children}</Suspense>
    </RouteErrorBoundary>
  );
}

function AppRoutes() {
  const { currentLanguage, isRTL } = useTranslation();

  useEffect(() => {
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = currentLanguage;
  }, [currentLanguage, isRTL]);

  return (
    <Routes>
      <Route path="/" element={<GuardedRoute><Landing /></GuardedRoute>} />
      <Route path="/login" element={<PublicRoute><GuardedRoute><Login /></GuardedRoute></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><GuardedRoute><Register /></GuardedRoute></PublicRoute>} />
      <Route path="/forgot-password" element={<PublicRoute><GuardedRoute><ForgotPassword /></GuardedRoute></PublicRoute>} />
      <Route path="/reset-password" element={<PublicRoute><GuardedRoute><ResetPassword /></GuardedRoute></PublicRoute>} />
      <Route path="/privacy" element={<GuardedRoute><Privacy /></GuardedRoute>} />
      <Route path="/terms" element={<GuardedRoute><Terms /></GuardedRoute>} />
      <Route path="/contact" element={<GuardedRoute><Contact /></GuardedRoute>} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <GuardedRoute>
              <Layout />
            </GuardedRoute>
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/app/dashboard" replace />} />
        <Route path="dashboard" element={<GuardedRoute><Dashboard /></GuardedRoute>} />
        <Route path="courses" element={<GuardedRoute><Courses /></GuardedRoute>} />
        <Route path="courses/:courseId" element={<GuardedRoute><CourseDetail /></GuardedRoute>} />
        <Route path="lessons/:lessonId" element={<GuardedRoute><LessonDetail /></GuardedRoute>} />
        <Route
          path="visual/:exerciseId"
          element={
            <GuardedRoute>
              <VisualProgrammingPage />
            </GuardedRoute>
          }
        />
        <Route path="duels" element={<GuardedRoute><DuelLobby /></GuardedRoute>} />
        <Route path="duels/:duelId" element={<GuardedRoute><DuelArena /></GuardedRoute>} />
        <Route path="projects" element={<GuardedRoute><Projects /></GuardedRoute>} />
        <Route path="projects/:projectId" element={<GuardedRoute><ProjectDetail /></GuardedRoute>} />
        <Route path="profile" element={<GuardedRoute><Profile /></GuardedRoute>} />
        <Route path="cody" element={<GuardedRoute><Cody /></GuardedRoute>} />
        <Route path="u/:username" element={<GuardedRoute><PublicProfile /></GuardedRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MotionConfig reducedMotion="user">
        <AuthProvider>
          <Suspense fallback={<LoadingFallback />}>
            <AppRoutes />
          </Suspense>
        </AuthProvider>
      </MotionConfig>
    </QueryClientProvider>
  );
}

export default App;