"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Loader2, Brain } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isLoggedIn, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isLoggedIn) {
      router.push("/login");
    }
  }, [isLoggedIn, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-midnight flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-xl bg-neural-gradient flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Brain className="w-9 h-9 text-white" />
          </div>
          <Loader2 className="w-8 h-8 text-electric animate-spin mx-auto mb-3" />
          <p className="text-white/60">Loading NeuroCron...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return null;
  }

  return <>{children}</>;
}

