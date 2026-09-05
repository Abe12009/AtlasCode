import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authApi } from '../api/services';
import type { User, StudentProfile } from '../types';
import { apiClient } from '../api/client';

interface AuthContextType {
  user: User | null;
  profile: StudentProfile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; username: string; password: string; preferred_language: string }) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUser = async () => {
    const token = apiClient.getAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await authApi.getMe();
      setUser(userData);
      const profileData = await authApi.getProfile();
      setProfile(profileData);
    } catch {
      apiClient.setAuthToken(null);
      setUser(null);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUser();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authApi.login({ email, password });
    apiClient.setAuthToken(response.access_token);
    await loadUser();
  };

  const register = async (data: { email: string; username: string; password: string; preferred_language: string }) => {
    const response = await authApi.register(data);
    apiClient.setAuthToken(response.access_token);
    await loadUser();
  };

  const logout = () => {
    apiClient.setAuthToken(null);
    setUser(null);
    setProfile(null);
  };

  const refreshProfile = async () => {
    if (user) {
      const profileData = await authApi.getProfile();
      setProfile(profileData);
    }
  };

  return (
    <AuthContext.Provider value={{ user, profile, loading, login, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}