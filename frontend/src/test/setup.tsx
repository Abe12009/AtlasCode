import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import { createTestI18n } from './i18n-test';
import { AuthProvider } from '../contexts/AuthContext';
import { LessonDetail } from '../pages/LessonDetail';
import { ProjectDetail } from '../pages/ProjectDetail';
import { VisualProgrammingPage } from '../pages/VisualProgramming';

vi.mock('../api/client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    patch: vi.fn(),
    setAuthToken: vi.fn((token: string | null) => {
      if (token) {
        localStorage.setItem('access_token', token);
      } else {
        localStorage.removeItem('access_token');
      }
    }),
    getAuthToken: vi.fn(() => localStorage.getItem('access_token')),
  },
}));

vi.mock('../api/services', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    getMe: vi.fn(),
    getProfile: vi.fn(),
    updateMe: vi.fn(),
    getConfig: vi.fn().mockResolvedValue({ firebase_enabled: true, password_login_enabled: true }),
    loginWithFirebase: vi.fn(),
  },
  coursesApi: {
    getAll: vi.fn(),
    getById: vi.fn(),
    getProgress: vi.fn(),
  },
  lessonsApi: {
    getById: vi.fn(),
    // A real default: the Micro-Quest reads lesson progress to decide whether
    // the backend already considers the lesson complete, and react-query
    // treats an undefined resolution as an error.
    getProgress: vi.fn().mockResolvedValue({
      id: 1,
      lesson_id: 1,
      status: 'in_progress',
      completed_at: null,
      xp_earned: 0,
      current_block: 0,
    }),
    start: vi.fn().mockResolvedValue({}),
  },
  exercisesApi: {
    getById: vi.fn(),
    run: vi.fn(),
    submit: vi.fn(),
    getAttempts: vi.fn(),
  },
  projectsApi: {
    getAll: vi.fn(),
    getById: vi.fn(),
    getProgress: vi.fn(),
    start: vi.fn(),
    submitTask: vi.fn(),
  },
  dashboardApi: {
    get: vi.fn(),
  },
  visualApi: {
    compile: vi.fn(),
    run: vi.fn(),
    submit: vi.fn(),
    getStarter: vi.fn(),
  },
  notificationsApi: {
    list: vi.fn().mockResolvedValue([]),
    getUnreadCount: vi.fn().mockResolvedValue({ count: 0 }),
    markRead: vi.fn(),
    markAllRead: vi.fn(),
  },
}));

export async function renderWithProviders(
  ui: React.ReactElement,
  options?: {
    initialLanguage?: string;
    authToken?: string;
    user?: { id: number; email: string; username: string; preferred_language: string };
    profile?: { user_id: number; xp: number; level: number; streak: number; completed_lessons: number; completed_projects: number };
    lessonId?: string;
    projectId?: string;
    exerciseId?: string;
  }
) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  // Create a fresh i18n instance for each test to ensure isolation
  const testI18n = await createTestI18n();
  if (options?.initialLanguage) {
    await testI18n.changeLanguage(options.initialLanguage);
  }

  if (options?.authToken) {
    localStorage.setItem('access_token', options.authToken);
  }

  // Build the initial path based on provided IDs
  let initialPath = '/';
  if (options?.lessonId) {
    initialPath = `/lessons/${options.lessonId}`;
  } else if (options?.projectId) {
    initialPath = `/projects/${options.projectId}`;
  } else if (options?.exerciseId) {
    initialPath = `/exercises/${options.exerciseId}/visual`;
  }

  const TestRoutes = () => (
    <Routes>
      <Route path="/lessons/:lessonId" element={<LessonDetail />} />
      <Route path="/projects/:projectId" element={<ProjectDetail />} />
      <Route path="/exercises/:exerciseId/visual" element={<VisualProgrammingPage />} />
      <Route path="*" element={ui} />
    </Routes>
  );

  return {
    ...render(<TestRoutes />, {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={[initialPath]}>
            <I18nextProvider i18n={testI18n}>
              <AuthProvider>
                {children}
              </AuthProvider>
            </I18nextProvider>
          </MemoryRouter>
        </QueryClientProvider>
      ),
    }),
    queryClient,
  };
}

export const mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  preferred_language: 'en',
  is_active: true,
  created_at: new Date().toISOString(),
};

export const mockProfile = {
  id: 1,
  user_id: 1,
  name: 'Test User',
  xp: 150,
  level: 2,
  streak: 5,
  completed_lessons: 3,
  completed_projects: 1,
  current_mission_id: null,
};

export const mockCourses = [
  {
    id: 1,
    slug: 'python-basics',
    order: 1,
    translations: [
      { language: 'en', title: 'Python Foundations', description: 'Learn Python basics', skills: 'Variables, Functions, Loops' },
      { language: 'fr', title: 'Fondamentaux de Python', description: 'Apprenez les bases de Python', skills: 'Variables, Fonctions, Boucles' },
      { language: 'ar', title: 'أساسيات بايثون', description: 'تعلم أساسيات بايثون', skills: 'المتغيرات، الدوال، الحلقات' },
    ],
    modules: [
      {
        id: 1,
        slug: 'getting-started',
        order: 1,
        translations: [{ language: 'en', title: 'Getting Started', description: 'Start here' }],
        lessons: [
          { id: 1, slug: 'what-is-programming', order: 1, difficulty: 'beginner', estimated_minutes: 30, xp_reward: 50, is_project: false, translations: [{ language: 'en', title: 'What Is Programming?', story: 'Learn what programming is' }], blocks: [], exercises: [] },
          { id: 2, slug: 'variables-and-values', order: 2, difficulty: 'beginner', estimated_minutes: 30, xp_reward: 50, is_project: false, translations: [{ language: 'en', title: 'Variables and Values', story: 'Learn about variables' }], blocks: [], exercises: [] },
        ],
      },
    ],
  },
];

export const mockLessons = [
  {
    id: 1,
    slug: 'what-is-programming',
    order: 1,
    module_id: 1,
    difficulty: 'beginner',
    estimated_minutes: 30,
    xp_reward: 50,
    is_project: false,
    translations: [{ language: 'en', title: 'What Is Programming?', story: 'Discover what programming is', objective: 'Understand programming', skills: 'Programming concepts' }],
    blocks: [
      { id: 1, block_type: 'text', order: 1, content: 'Programming is giving instructions to a computer.', code_example: null, translations: [] },
      { id: 2, block_type: 'code', order: 2, content: 'Your first program:', code_example: 'print("Hello, World!")', translations: [] },
      { id: 3, block_type: 'text', order: 3, content: 'Try changing the text inside the quotes to say something different!', code_example: null, translations: [] },
    ],
    exercises: [
      {
        id: 1,
        exercise_type: 'code_writing',
        order: 1,
        xp_reward: 10,
        starter_code: 'print("Hello, World!")',
        translations: [{ language: 'en', prompt: 'Write a program that prints "Hello, World!"', hint: 'Use print()', explanation: 'print() outputs text' }],
        options: [],
      },
      {
        id: 2,
        exercise_type: 'code_writing',
        order: 2,
        xp_reward: 10,
        starter_code: 'print("Hello, World!")\nprint("Welcome to AtlasCode!")',
        translations: [{ language: 'en', prompt: 'Write a program that prints "Hello, World!" and "Welcome to AtlasCode!"', hint: 'Use two print() statements', explanation: 'Each print() outputs text on a new line' }],
        options: [],
      },
      {
        id: 3,
        exercise_type: 'prediction',
        order: 3,
        xp_reward: 10,
        starter_code: 'print("Hello")\nprint("World")',
        solution_code: 'Hello\nWorld',
        test_code: '',
        validation_config: '{"expected_output": "Hello\\nWorld"}',
        translations: [{ language: 'en', prompt: 'What will this code print?', hint: 'Each print() creates a new line', explanation: 'Each print() outputs text on a new line' }],
        options: [],
      },
    ],
  },
];

export const mockProjects = [
  {
    id: 1,
    slug: 'calculator',
    order: 1,
    difficulty: 'beginner',
    xp_reward: 200,
    prerequisite_lesson_id: 5,
    prerequisite_project_id: null,
    translations: [
      { language: 'en', title: 'Build a CLI Calculator', story: 'Create a command-line calculator', objective: 'Build a working calculator', skills: 'Functions, Conditionals, User Input', guide: 'Complete all tasks' },
      { language: 'fr', title: 'Construire une Calculatrice CLI', story: 'Créez une calculatrice', objective: 'Construire une calculatrice', skills: 'Fonctions', guide: 'Terminez toutes les tâches' },
      { language: 'ar', title: 'بناء آلة حاسبة', story: 'أنشئ آلة حاسبة', objective: 'بناء آلة حاسبة', skills: 'الدوال', guide: 'أكمل جميع المهام' },
    ],
    tasks: [
      { id: 1, order: 1, starter_code: 'def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return "Error: Division by zero"\n\nprint(add(5, 3))', translations: [{ language: 'en', title: 'Implement Basic Operations', description: 'Create functions for add, subtract, multiply, and divide', hint: 'Remember to handle division by zero' }] },
      { id: 2, order: 2, starter_code: 'def calculate(choice, num1, num2):\n    """Perform calculation based on choice.\n    choice: "1"=add, "2"=subtract, "3"=multiply, "4"=divide\n    Returns result or error string.\n    """\n    # TODO: Implement calculator logic\n    pass\n\n# Test your function\nprint(calculate("1", 10, 5))  # Should print 15\nprint(calculate("4", 10, 0))  # Should print error message', translations: [{ language: 'en', title: 'Build the Calculator Menu', description: 'Create a menu that lets the user choose an operation', hint: 'Use if-elif-else to handle the user\'s choice' }] },
      { id: 3, order: 3, starter_code: 'def process_operations(operations):\n    """Process a list of operations.\n    operations: list of tuples (choice, num1, num2)\n    choice: "1"=add, "2"=subtract, "3"=multiply, "4"=divide, "5"=exit\n    Returns list of results. Stops processing when choice is "5".\n    """\n    results = []\n    for choice, num1, num2 in operations:\n        # TODO: Implement logic\n        # If choice == "5": break\n        # Else: calculate and append result\n        pass\n    return results\n\n# Test\nops = [("1", 10, 5), ("2", 10, 5), ("5", 0, 0), ("1", 5, 5)]\nprint(process_operations(ops))', translations: [{ language: 'en', title: 'Add Continuous Operation Loop', description: 'Allow the user to perform multiple calculations until they choose to exit', hint: 'Use a while True loop with a break condition' }] },
      { id: 4, order: 4, starter_code: 'def safe_calculate(choice, num1, num2):\n    """Safely perform calculation with input validation.\n    Returns (success: bool, result: float|str)\n    """\n    # Validate choice\n    if choice not in ["1", "2", "3", "4"]:\n        return (False, "Invalid choice! Please enter 1, 2, 3, or 4.")\n    \n    # Validate numbers\n    try:\n        num1 = float(num1)\n        num2 = float(num2)\n    except (ValueError, TypeError):\n        return (False, "Invalid input! Please enter valid numbers.")\n    \n    # Perform calculation\n    if choice == "1":\n        return (True, num1 + num2)\n    elif choice == "2":\n        return (True, num1 - num2)\n    elif choice == "3":\n        return (True, num1 * num2)\n    elif choice == "4":\n        if num2 == 0:\n            return (False, "Error: Division by zero")\n        return (True, num1 / num2)\n\n# Test\nprint(safe_calculate("1", "10", "5"))\nprint(safe_calculate("5", "10", "5"))\nprint(safe_calculate("1", "abc", "5"))\nprint(safe_calculate("4", "10", "0"))', translations: [{ language: 'en', title: 'Add Input Validation', description: 'Handle invalid menu choices and non-numeric input gracefully', hint: 'Use try-except blocks for ValueError and check if choice is in valid options' }] },
    ],
  },
];

export const mockVisualProgrammingExercise = {
  id: 1,
  exercise_type: 'visual_programming',
  order: 1,
  xp_reward: 50,
  starter_code: null,
  translations: [{ language: 'en', prompt: 'Build a visual program', hint: 'Connect nodes', explanation: 'Visual programming' }],
  options: [],
  course_id: 1,
  course_title: 'Python Foundations',
  lesson_id: 1,
  lesson_title: 'What Is Programming?',
};