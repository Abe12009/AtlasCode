import { Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoadingFallback } from './components/LoadingFallback';
import { lazy, Suspense, useEffect } from 'react';
import { useTranslation } from './hooks/useTranslation';

const Landing = lazy(() => import('./pages/Landing').then(m => ({ default: m.Landing })));
const Login = lazy(() => import('./pages/Login').then(m => ({ default: m.Login })));
const Register = lazy(() => import('./pages/Register').then(m => ({ default: m.Register })));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword').then(m => ({ default: m.ForgotPassword })));
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
const VisualProgrammingPage = lazy(() => import('./pages/VisualProgramming').then(m => ({ default: m.VisualProgrammingPage })));

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

function AppRoutes() {
  const { currentLanguage, isRTL } = useTranslation();

  useEffect(() => {
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = currentLanguage;
  }, [currentLanguage, isRTL]);

  return (
    <Routes>
      <Route path="/" element={<Suspense fallback={<LoadingFallback />}><Landing /></Suspense>} />
      <Route path="/login" element={<PublicRoute><Suspense fallback={<LoadingFallback />}><Login /></Suspense></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Suspense fallback={<LoadingFallback />}><Register /></Suspense></PublicRoute>} />
      <Route path="/forgot-password" element={<PublicRoute><Suspense fallback={<LoadingFallback />}><ForgotPassword /></Suspense></PublicRoute>} />
      <Route path="/privacy" element={<Suspense fallback={<LoadingFallback />}><Privacy /></Suspense>} />
      <Route path="/terms" element={<Suspense fallback={<LoadingFallback />}><Terms /></Suspense>} />
      <Route path="/contact" element={<Suspense fallback={<LoadingFallback />}><Contact /></Suspense>} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <Suspense fallback={<LoadingFallback />}>
              <Layout />
            </Suspense>
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/app/dashboard" replace />} />
        <Route path="dashboard" element={<Suspense fallback={<LoadingFallback />}><Dashboard /></Suspense>} />
        <Route path="courses" element={<Suspense fallback={<LoadingFallback />}><Courses /></Suspense>} />
        <Route path="courses/:courseId" element={<Suspense fallback={<LoadingFallback />}><CourseDetail /></Suspense>} />
        <Route path="lessons/:lessonId" element={<Suspense fallback={<LoadingFallback />}><LessonDetail /></Suspense>} />
        <Route path="visual/:exerciseId" element={<Suspense fallback={<LoadingFallback />}><VisualProgrammingPage /></Suspense>} />
        <Route path="projects" element={<Suspense fallback={<LoadingFallback />}><Projects /></Suspense>} />
        <Route path="projects/:projectId" element={<Suspense fallback={<LoadingFallback />}><ProjectDetail /></Suspense>} />
        <Route path="profile" element={<Suspense fallback={<LoadingFallback />}><Profile /></Suspense>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Suspense fallback={<LoadingFallback />}>
          <AppRoutes />
        </Suspense>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;