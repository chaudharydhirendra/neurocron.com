/**
 * NeuroCron Authentication Library
 * Handles login, register, logout, and token management
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.neurocron.com";

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

// Token storage keys
const ACCESS_TOKEN_KEY = "neurocron_access_token";
const REFRESH_TOKEN_KEY = "neurocron_refresh_token";
const USER_KEY = "neurocron_user";

/**
 * Store tokens in localStorage
 */
export function storeTokens(tokens: AuthTokens): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

/**
 * Get access token from localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Get refresh token from localStorage
 */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Store user data in localStorage
 */
export function storeUser(user: User): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/**
 * Get user from localStorage
 */
export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Clear all auth data from localStorage
 */
export function clearAuth(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

/**
 * Make authenticated API request
 */
export async function authFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getAccessToken();
  
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  // If unauthorized, try to refresh token
  if (response.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry with new token
      (headers as Record<string, string>)["Authorization"] = `Bearer ${getAccessToken()}`;
      return fetch(`${API_URL}${endpoint}`, { ...options, headers });
    } else {
      // Refresh failed, clear auth and redirect to login
      clearAuth();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
  }
  
  return response;
}

/**
 * Login user
 */
export async function login(credentials: LoginCredentials): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });
    
    if (!response.ok) {
      const error = await response.json();
      return { success: false, error: error.detail || "Login failed" };
    }
    
    const tokens: AuthTokens = await response.json();
    storeTokens(tokens);
    
    return { success: true };
  } catch (error) {
    return { success: false, error: "Network error. Please try again." };
  }
}

/**
 * Register new user
 */
export async function register(data: RegisterData): Promise<{ success: boolean; error?: string; user?: User }> {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      return { success: false, error: error.detail || "Registration failed" };
    }
    
    const user: User = await response.json();
    
    // Auto-login after registration
    const loginResult = await login({ email: data.email, password: data.password });
    if (!loginResult.success) {
      return { success: true, user }; // Registration succeeded but login failed
    }
    
    storeUser(user);
    return { success: true, user };
  } catch (error) {
    return { success: false, error: "Network error. Please try again." };
  }
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  try {
    await authFetch("/api/v1/auth/logout", { method: "POST" });
  } catch {
    // Ignore errors on logout
  }
  clearAuth();
}

/**
 * Refresh access token
 */
export async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;
  
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    
    if (!response.ok) return false;
    
    const tokens: AuthTokens = await response.json();
    storeTokens(tokens);
    return true;
  } catch {
    return false;
  }
}

/**
 * Get current user from API
 */
export async function getCurrentUser(): Promise<User | null> {
  try {
    const response = await authFetch("/api/v1/auth/me");
    if (!response.ok) return null;
    
    const user: User = await response.json();
    storeUser(user);
    return user;
  } catch {
    return null;
  }
}

