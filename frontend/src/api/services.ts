import { apiClient } from './client';
import type {
  User,
  StudentProfile,
  Course,
  Lesson,
  Exercise,
  ExerciseSubmitRequest,
  ExerciseSubmitResponse,
  LessonProgress,
  CourseProgress,
  Project,
  ProjectProgress,
  DashboardData,
  VisualProgramRequest,
  VisualProgramResponse,
  Notification,
  PublicProfile,
  Section,
} from '../types';

export const authApi = {
  register: (data: { email: string; username: string; password: string; preferred_language: string }) =>
    apiClient.post<{ access_token: string; token_type: string }>('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    apiClient.post<{ access_token: string; token_type: string }>('/auth/login', data),

  getMe: () => apiClient.get<User>('/auth/me'),

  updateMe: (data: {
    username?: string;
    preferred_language?: string;
    profile_visibility?: 'public' | 'private';
    avatar_type?: 'upload' | 'generated';
    avatar_config?: string;
  }) => apiClient.patch<User>('/auth/me', data),

  uploadAvatar: (dataUrl: string) => apiClient.post<User>('/auth/me/avatar', { data_url: dataUrl }),

  changePassword: (data: { current_password: string; new_password: string }) =>
    apiClient.post<void>('/auth/change-password', data),

  getProfile: () => apiClient.get<StudentProfile>('/auth/profile'),

  getConfig: () =>
    apiClient.get<{ firebase_enabled: boolean; password_login_enabled: boolean }>('/auth/config'),

  loginWithFirebase: (data: { id_token: string; preferred_language?: string; timezone_offset_minutes?: number }) =>
    apiClient.post<{ access_token: string; token_type: string }>('/auth/firebase', data),
};

export const usersApi = {
  getPublicProfile: (username: string) => apiClient.get<PublicProfile>(`/users/${encodeURIComponent(username)}`),
};

export const coursesApi = {
  getAll: (language: string = 'en') =>
    apiClient.get<Course[]>('/courses', { language }),

  getById: (courseId: number, language: string = 'en') =>
    apiClient.get<Course>(`/courses/${courseId}`, { language }),

  getProgress: (courseId: number) =>
    apiClient.get<CourseProgress>(`/courses/${courseId}/progress`),
};

export const sectionsApi = {
  getAll: (language: string = 'en') =>
    apiClient.get<Section[]>('/sections', { language }),
};

export const lessonsApi = {
  getById: (lessonId: number, language: string = 'en') =>
    apiClient.get<Lesson>(`/lessons/${lessonId}`, { language }),

  getProgress: (lessonId: number) =>
    apiClient.get<LessonProgress>(`/lessons/${lessonId}/progress`),

  start: (lessonId: number) =>
    apiClient.post<LessonProgress>(`/lessons/${lessonId}/start`),
};

export const exercisesApi = {
  getById: (exerciseId: number, language: string = 'en') =>
    apiClient.get<Exercise>(`/exercises/${exerciseId}`, { language }),

  run: (exerciseId: number, data: ExerciseSubmitRequest) =>
    apiClient.post<ExerciseSubmitResponse>(`/exercises/${exerciseId}/run`, data),

  submit: (exerciseId: number, data: ExerciseSubmitRequest) =>
    apiClient.post<ExerciseSubmitResponse>(`/exercises/${exerciseId}/submit`, data),

  getAttempts: (exerciseId: number) =>
    apiClient.get<ExerciseSubmitResponse[]>(`/exercises/${exerciseId}/attempts`),
};

export const projectsApi = {
  getAll: (language: string = 'en') =>
    apiClient.get<Project[]>('/projects', { language }),

  getById: (projectId: number, language: string = 'en') =>
    apiClient.get<Project>(`/projects/${projectId}`, { language }),

  getProgress: (projectId: number) =>
    apiClient.get<ProjectProgress>(`/projects/${projectId}/progress`),

  start: (projectId: number) =>
    apiClient.post<ProjectProgress>(`/projects/${projectId}/start`),

  submitTask: (projectId: number, taskId: number, code: string) =>
    apiClient.post<{ success: boolean; progress: ProjectProgress }>(
      `/projects/${projectId}/submit-task`,
      { task_id: taskId, code }
    ),
};

export const dashboardApi = {
  get: () => apiClient.get<DashboardData>('/dashboard'),
};

export const notificationsApi = {
  list: (limit: number = 20) =>
    apiClient.get<Notification[]>('/notifications', { limit }),

  getUnreadCount: () =>
    apiClient.get<{ count: number }>('/notifications/unread-count'),

  markRead: (notificationId: number) =>
    apiClient.post<Notification>(`/notifications/${notificationId}/read`),

  markAllRead: () =>
    apiClient.post<{ success: boolean }>('/notifications/read-all'),
};

export const visualApi = {
  compile: (data: VisualProgramRequest) =>
    apiClient.post<VisualProgramResponse>('/visual/compile', data),

  run: (exerciseId: number, data: ExerciseSubmitRequest) =>
    apiClient.post<ExerciseSubmitResponse>(`/visual/${exerciseId}/run`, data),

  submit: (exerciseId: number, data: ExerciseSubmitRequest) =>
    apiClient.post<ExerciseSubmitResponse>(`/visual/${exerciseId}/submit`, data),

  getStarter: (exerciseId: number) =>
    apiClient.get<Record<string, unknown>>(`/visual/${exerciseId}/starter`),
};