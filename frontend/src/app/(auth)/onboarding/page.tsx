"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Building2,
  Globe,
  Users,
  Briefcase,
  ArrowRight,
  ArrowLeft,
  Loader2,
  Sparkles,
  Check,
} from "lucide-react";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

const industries = [
  "E-commerce",
  "SaaS / Technology",
  "Healthcare",
  "Finance & Banking",
  "Education",
  "Real Estate",
  "Travel & Hospitality",
  "Food & Beverage",
  "Media & Entertainment",
  "Professional Services",
  "Manufacturing",
  "Other",
];

const companySizes = [
  { label: "Just me", value: "1" },
  { label: "2-10 employees", value: "2-10" },
  { label: "11-50 employees", value: "11-50" },
  { label: "51-200 employees", value: "51-200" },
  { label: "201-500 employees", value: "201-500" },
  { label: "500+ employees", value: "500+" },
];

const marketingGoals = [
  { id: "awareness", label: "Brand Awareness", icon: Sparkles },
  { id: "leads", label: "Lead Generation", icon: Users },
  { id: "sales", label: "Direct Sales", icon: Briefcase },
  { id: "retention", label: "Customer Retention", icon: Building2 },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Form data
  const [companyName, setCompanyName] = useState("");
  const [website, setWebsite] = useState("");
  const [industry, setIndustry] = useState("");
  const [companySize, setCompanySize] = useState("");
  const [goals, setGoals] = useState<string[]>([]);

  const totalSteps = 3;

  const toggleGoal = (goalId: string) => {
    setGoals((prev) =>
      prev.includes(goalId)
        ? prev.filter((g) => g !== goalId)
        : [...prev, goalId]
    );
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return companyName.length >= 2;
      case 2:
        return industry && companySize;
      case 3:
        return goals.length > 0;
      default:
        return false;
    }
  };

  const handleSubmit = async () => {
    if (isLoading) return;
    setIsLoading(true);
    setError("");

    try {
      const response = await authFetch("/api/v1/organizations/", {
        method: "POST",
        body: JSON.stringify({
          name: companyName,
          website: website || undefined,
          industry,
          company_size: companySize,
          settings: { goals },
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to create organization");
      }

      // Success - redirect to dashboard
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-midnight neural-bg flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 justify-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-neural-gradient flex items-center justify-center">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <span className="text-2xl font-bold">NeuroCron</span>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={cn(
                "h-1.5 rounded-full transition-all duration-300",
                s === step
                  ? "w-12 bg-electric"
                  : s < step
                  ? "w-8 bg-electric/50"
                  : "w-8 bg-white/10"
              )}
            />
          ))}
        </div>

        {/* Card */}
        <div className="card">
          <AnimatePresence mode="wait">
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h1 className="text-2xl font-bold text-center mb-2">
                  Welcome to NeuroCron
                </h1>
                <p className="text-white/60 text-center mb-8">
                  Let&apos;s set up your marketing command center
                </p>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-white/60 mb-2">
                      Company name *
                    </label>
                    <div className="relative">
                      <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                      <input
                        type="text"
                        value={companyName}
                        onChange={(e) => setCompanyName(e.target.value)}
                        placeholder="Acme Inc."
                        className="input pl-11"
                        autoFocus
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-white/60 mb-2">
                      Website (optional)
                    </label>
                    <div className="relative">
                      <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                      <input
                        type="url"
                        value={website}
                        onChange={(e) => setWebsite(e.target.value)}
                        placeholder="https://acme.com"
                        className="input pl-11"
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h1 className="text-2xl font-bold text-center mb-2">
                  Tell us about your business
                </h1>
                <p className="text-white/60 text-center mb-8">
                  This helps NeuroCron personalize your marketing strategy
                </p>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm text-white/60 mb-3">
                      Industry *
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {industries.map((ind) => (
                        <button
                          key={ind}
                          onClick={() => setIndustry(ind)}
                          className={cn(
                            "p-3 rounded-xl border text-sm text-left transition-all",
                            industry === ind
                              ? "border-electric bg-electric/10 text-electric"
                              : "border-white/10 hover:border-white/20 text-white/60 hover:text-white"
                          )}
                        >
                          {ind}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-white/60 mb-3">
                      Company size *
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {companySizes.map((size) => (
                        <button
                          key={size.value}
                          onClick={() => setCompanySize(size.value)}
                          className={cn(
                            "p-3 rounded-xl border text-sm text-left transition-all",
                            companySize === size.value
                              ? "border-electric bg-electric/10 text-electric"
                              : "border-white/10 hover:border-white/20 text-white/60 hover:text-white"
                          )}
                        >
                          {size.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h1 className="text-2xl font-bold text-center mb-2">
                  What are your marketing goals?
                </h1>
                <p className="text-white/60 text-center mb-8">
                  Select all that apply
                </p>

                <div className="grid grid-cols-2 gap-4">
                  {marketingGoals.map((goal) => {
                    const isSelected = goals.includes(goal.id);
                    return (
                      <button
                        key={goal.id}
                        onClick={() => toggleGoal(goal.id)}
                        className={cn(
                          "p-6 rounded-xl border text-left transition-all relative group",
                          isSelected
                            ? "border-electric bg-electric/10"
                            : "border-white/10 hover:border-white/20"
                        )}
                      >
                        {isSelected && (
                          <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-electric flex items-center justify-center">
                            <Check className="w-3 h-3 text-midnight" />
                          </div>
                        )}
                        <goal.icon
                          className={cn(
                            "w-8 h-8 mb-3 transition-colors",
                            isSelected ? "text-electric" : "text-white/40 group-hover:text-white/60"
                          )}
                        />
                        <div
                          className={cn(
                            "font-medium transition-colors",
                            isSelected ? "text-electric" : "text-white/80"
                          )}
                        >
                          {goal.label}
                        </div>
                      </button>
                    );
                  })}
                </div>

                {error && (
                  <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                    {error}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/5">
            <button
              onClick={() => step > 1 && setStep(step - 1)}
              disabled={step === 1}
              className={cn(
                "flex items-center gap-2 text-sm transition-colors",
                step === 1
                  ? "text-white/20 cursor-not-allowed"
                  : "text-white/60 hover:text-white"
              )}
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>

            <button
              onClick={handleNext}
              disabled={!canProceed() || isLoading}
              className={cn(
                "btn-primary flex items-center gap-2",
                (!canProceed() || isLoading) && "opacity-50 cursor-not-allowed"
              )}
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  {step === totalSteps ? "Launch NeuroCron" : "Continue"}
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Skip option */}
        <p className="text-center text-sm text-white/40 mt-6">
          Need help?{" "}
          <a href="mailto:support@neurocron.com" className="text-electric hover:underline">
            Contact support
          </a>
        </p>
      </motion.div>
    </div>
  );
}

