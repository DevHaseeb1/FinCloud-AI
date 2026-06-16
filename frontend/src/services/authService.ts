import { api, getData, postData } from "./api";
import type { AuthResponse, User } from "@/types/apiTypes";

const TOKEN_KEY = "fincloud_token";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export async function signup(
  name: string,
  email: string,
  password: string,
): Promise<AuthResponse> {
  const res = await postData<AuthResponse>("/auth/signup", {
    name,
    email,
    password,
    confirm_password: password,
  });
  return res as AuthResponse;
}

export async function login(
  email: string,
  password: string,
): Promise<AuthResponse> {
  const res = await postData<AuthResponse>("/auth/login", { email, password });
  return res as AuthResponse;
}

export async function getCurrentUser(): Promise<User> {
  const res = await getData<{ user: User }>("/auth/me");
  return (res as { user: User }).user;
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout");
  } catch {
    // Ignore errors — token will be cleared client-side anyway
  }
}
