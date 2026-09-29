"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { User, LoginPayload, RegisterPayload } from "@/types";
import { authApi } from "@/lib/api/auth";
import { authStorage } from "@/lib/auth/storage";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children?: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCurrentUser = useCallback(async () => {
    const token = authStorage.getToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
      authStorage.setUser(currentUser);
    } catch {
      // If token expired or invalid
      authStorage.clear();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial check from storage / API
    const cachedUser = authStorage.getUser();
    if (cachedUser) {
      setUser(cachedUser);
    }
    fetchCurrentUser();

    // Listen to unauthorized events from Axios interceptor
    const handleUnauthorized = () => {
      setUser(null);
      authStorage.clear();
    };

    window.addEventListener("marketmind:unauthorized", handleUnauthorized);
    return () => {
      window.removeEventListener("marketmind:unauthorized", handleUnauthorized);
    };
  }, [fetchCurrentUser]);

  const login = async (payload: LoginPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokens = await authApi.login(payload);
      authStorage.setToken(tokens.access_token);
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
      authStorage.setUser(currentUser);
    } catch (err: unknown) {
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Authentication failed. Please check your credentials.";
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (payload: RegisterPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.register(payload);
      // Auto-login after successful registration
      await login({ username: payload.username, password: payload.password });
    } catch (err: unknown) {
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Registration failed. Please try again.";
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authStorage.clear();
    setUser(null);
    setError(null);
  };

  const refreshUser = async () => {
    await fetchCurrentUser();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
