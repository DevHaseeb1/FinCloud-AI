"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import type { User } from "@/types/apiTypes";
import {
  getStoredToken,
  setStoredToken,
  clearStoredToken,
  login as apiLogin,
  signup as apiSignup,
  getCurrentUser,
  logout as apiLogout,
} from "@/services/authService";

export type AuthContextValue = {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
};

export const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [token, setToken] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const router = useRouter();

  React.useEffect(() => {
    const init = async () => {
      const stored = getStoredToken();
      if (!stored) {
        setIsLoading(false);
        return;
      }
      try {
        setToken(stored);
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        clearStoredToken();
        setToken(null);
      } finally {
        setIsLoading(false);
      }
    };
    init();
  }, []);

  const loginFn = React.useCallback(
    async (email: string, password: string) => {
      const res = await apiLogin(email, password);
      setStoredToken(res.token.access_token);
      setToken(res.token.access_token);
      setUser(res.user);
      router.push("/");
    },
    [router],
  );

  const signupFn = React.useCallback(
    async (name: string, email: string, password: string) => {
      const res = await apiSignup(name, email, password);
      setStoredToken(res.token.access_token);
      setToken(res.token.access_token);
      setUser(res.user);
      router.push("/");
    },
    [router],
  );

  const logoutFn = React.useCallback(async () => {
    await apiLogout();
    clearStoredToken();
    setToken(null);
    setUser(null);
    router.push("/login");
  }, [router]);

  const value = React.useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: !!user && !!token,
      isLoading,
      login: loginFn,
      signup: signupFn,
      logout: logoutFn,
    }),
    [user, token, isLoading, loginFn, signupFn, logoutFn],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
