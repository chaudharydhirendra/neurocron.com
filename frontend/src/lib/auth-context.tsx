"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import {
  User,
  login as authLogin,
  register as authRegister,
  logout as authLogout,
  getStoredUser,
  isAuthenticated,
  getCurrentUser,
  authFetch,
  storeUser,
  LoginCredentials,
  RegisterData,
} from "./auth";

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
}

interface AuthContextType {
  user: User | null;
  organization: Organization | null;
  isLoading: boolean;
  isLoggedIn: boolean;
  login: (credentials: LoginCredentials) => Promise<{ success: boolean; error?: string }>;
  register: (data: RegisterData) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  // Check user organizations
  const checkOrganizations = async (): Promise<Organization | null> => {
    try {
      const response = await authFetch("/api/v1/organizations/");
      if (response.ok) {
        const orgs = await response.json();
        if (orgs.length > 0) {
          return orgs[0]; // Return first org
        }
      }
    } catch {
      // Ignore errors
    }
    return null;
  };

  // Check auth status on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (isAuthenticated()) {
        const storedUser = getStoredUser();
        if (storedUser) {
          setUser(storedUser);
          // Check for organizations
          const org = await checkOrganizations();
          setOrganization(org);
        } else {
          // Try to fetch user from API
          const apiUser = await getCurrentUser();
          if (apiUser) {
            setUser(apiUser);
            const org = await checkOrganizations();
            setOrganization(org);
          }
        }
      }
      setIsLoading(false);
    };
    
    checkAuth();
  }, []);

  const refreshUser = useCallback(async () => {
    const apiUser = await getCurrentUser();
    if (apiUser) {
      setUser(apiUser);
      storeUser(apiUser);
    }
    const org = await checkOrganizations();
    setOrganization(org);
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setIsLoading(true);
    const result = await authLogin(credentials);
    
    if (result.success) {
      // Fetch full user profile
      const apiUser = await getCurrentUser();
      if (apiUser) {
        setUser(apiUser);
        storeUser(apiUser);
        
        // Check if user has organizations
        const org = await checkOrganizations();
        setOrganization(org);
        
        if (org) {
          router.push("/dashboard");
        } else {
          router.push("/onboarding");
        }
      } else {
        // Fallback if /me endpoint fails
        const basicUser: User = {
          id: "temp",
          email: credentials.email,
          full_name: credentials.email.split("@")[0],
          is_active: true,
          is_verified: false,
        };
        setUser(basicUser);
        router.push("/onboarding");
      }
    }
    
    setIsLoading(false);
    return result;
  }, [router]);

  const register = useCallback(async (data: RegisterData) => {
    setIsLoading(true);
    const result = await authRegister(data);
    
    if (result.success) {
      // Fetch full user profile or use returned user
      const apiUser = await getCurrentUser();
      if (apiUser) {
        setUser(apiUser);
        storeUser(apiUser);
      } else if (result.user) {
        setUser(result.user);
        storeUser(result.user);
      }
      // New users always go to onboarding
      router.push("/onboarding");
    }
    
    setIsLoading(false);
    return result;
  }, [router]);

  const logout = useCallback(async () => {
    await authLogout();
    setUser(null);
    setOrganization(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        organization,
        isLoading,
        isLoggedIn: !!user,
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

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

