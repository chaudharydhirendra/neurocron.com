"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Brain, Mail, Lock, User, ArrowRight, Loader2, Check } from "lucide-react";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // TODO: Implement actual registration
    setTimeout(() => {
      setIsLoading(false);
      window.location.href = "/dashboard";
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-midnight neural-bg flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 justify-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-neural-gradient flex items-center justify-center">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <span className="text-2xl font-bold">NeuroCron</span>
        </Link>

        {/* Card */}
        <div className="card">
          <h1 className="text-2xl font-bold text-center mb-2">Create your account</h1>
          <p className="text-white/60 text-center mb-8">
            Start your 14-day free trial
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-white/60 mb-2">Full name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="input pl-11"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-2">Work email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="input pl-11"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input pl-11"
                  required
                  minLength={8}
                />
              </div>
              <p className="text-xs text-white/40 mt-1">Minimum 8 characters</p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Create account
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Benefits */}
          <div className="mt-6 space-y-2">
            {[
              "14-day free trial",
              "No credit card required",
              "Cancel anytime",
            ].map((benefit, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-white/50">
                <Check className="w-4 h-4 text-green-400" />
                {benefit}
              </div>
            ))}
          </div>

          <p className="text-center text-sm text-white/50 mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-electric hover:underline">
              Log in
            </Link>
          </p>

          <p className="text-center text-xs text-white/30 mt-4">
            By signing up, you agree to our{" "}
            <Link href="/terms" className="underline">Terms</Link> and{" "}
            <Link href="/privacy" className="underline">Privacy Policy</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}

