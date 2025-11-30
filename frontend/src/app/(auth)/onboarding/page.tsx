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
  Target,
  TrendingUp,
  Megaphone,
  Mail,
  BarChart3,
  Zap,
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
  { id: "awareness", label: "Brand Awareness", icon: Megaphone, description: "Get your brand noticed" },
  { id: "leads", label: "Lead Generation", icon: Target, description: "Capture quality leads" },
  { id: "sales", label: "Direct Sales", icon: TrendingUp, description: "Drive revenue growth" },
  { id: "retention", label: "Customer Retention", icon: Users, description: "Keep customers engaged" },
];

const marketingChannels = [
  { id: "social", label: "Social Media", icon: Users },
  { id: "email", label: "Email Marketing", icon: Mail },
  { id: "ads", label: "Paid Advertising", icon: Megaphone },
  { id: "seo", label: "SEO & Content", icon: BarChart3 },
];

const budgetRanges = [
  { label: "Less than $1,000/mo", value: "under_1k" },
  { label: "$1,000 - $5,000/mo", value: "1k_5k" },
  { label: "$5,000 - $20,000/mo", value: "5k_20k" },
  { label: "$20,000 - $50,000/mo", value: "20k_50k" },
  { label: "More than $50,000/mo", value: "over_50k" },
  { label: "Not sure yet", value: "unknown" },
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
  const [channels, setChannels] = useState<string[]>([]);
  const [budget, setBudget] = useState("");

  const totalSteps = 5;

  const toggleGoal = (goalId: string) => {
    setGoals((prev) =>
      prev.includes(goalId)
        ? prev.filter((g) => g !== goalId)
        : [...prev, goalId]
    );
  };

  const toggleChannel = (channelId: string) => {
    setChannels((prev) =>
      prev.includes(channelId)
        ? prev.filter((c) => c !== channelId)
        : [...prev, channelId]
    );
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return true; // Welcome step
      case 2:
        return companyName.length >= 2;
      case 3:
        return industry && companySize;
      case 4:
        return goals.length > 0;
      case 5:
        return channels.length > 0 && budget;
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
          settings: { 
            goals, 
            channels, 
            budget,
            onboarding_completed: true,
          },
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
    <div className="min-h-screen bg-midnight neural-bg flex items-center justify-center p-4 md:p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 justify-center mb-6 md:mb-8">
          <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-neural-gradient flex items-center justify-center">
            <Brain className="w-6 h-6 md:w-7 md:h-7 text-white" />
          </div>
          <span className="text-xl md:text-2xl font-bold">NeuroCron</span>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-center gap-1 md:gap-2 mb-6 md:mb-8">
          {[1, 2, 3, 4, 5].map((s) => (
            <div
              key={s}
              className={cn(
                "h-1 md:h-1.5 rounded-full transition-all duration-300",
                s === step
                  ? "w-8 md:w-12 bg-electric"
                  : s < step
                  ? "w-6 md:w-8 bg-electric/50"
                  : "w-6 md:w-8 bg-white/10"
              )}
            />
          ))}
        </div>

        {/* Card */}
        <div className="card">
          <AnimatePresence mode="wait">
            {/* Step 1: Welcome */}
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="text-center py-4 md:py-8"
              >
                <div className="w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-neural-gradient flex items-center justify-center mx-auto mb-4 md:mb-6">
                  <Zap className="w-8 h-8 md:w-10 md:h-10 text-white" />
                </div>
                <h1 className="text-2xl md:text-3xl font-bold mb-2 md:mb-3">
                  Welcome to NeuroCron
                </h1>
                <p className="text-white/60 mb-6 md:mb-8 max-w-md mx-auto text-sm md:text-base">
                  You're about to set up the world's most advanced AI marketing platform. 
                  Let's personalize it for your business in just a few steps.
                </p>
                
                <div className="grid grid-cols-3 gap-3 md:gap-4 max-w-md mx-auto">
                  {[
                    { icon: Brain, label: "AI Strategy" },
                    { icon: Megaphone, label: "Automation" },
                    { icon: BarChart3, label: "Analytics" },
                  ].map((item, i) => (
                    <div key={i} className="p-3 md:p-4 rounded-xl bg-white/5 border border-white/10">
                      <item.icon className="w-5 h-5 md:w-6 md:h-6 text-electric mx-auto mb-1 md:mb-2" />
                      <div className="text-xs md:text-sm text-white/60">{item.label}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Step 2: Company Info */}
            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h1 className="text-xl md:text-2xl font-bold text-center mb-2">
                  Let's set up your workspace
                </h1>
                <p className="text-white/60 text-center mb-6 md:mb-8 text-sm md:text-base">
                  Tell us about your company
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

            {/* Step 3: Business Details */}
            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h1 className="text-xl md:text-2xl font-bold text-center mb-2">
                  Tell us about your business
                </h1>
                <p className="text-white/60 text-center mb-6 md:mb-8 text-sm md:text-base">
                  This helps NeuroCron personalize your experience
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
                            "p-2.5 md:p-3 rounded-xl border text-xs md:text-sm text-left transition-all",
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
                            "p-2.5 md:p-3 rounded-xl border text-xs md:text-sm text-left transition-all",
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

            {/* Step 4: Marketing Goals */}
            {step === 4 && (
              <motion.div
                key="step4"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h1 className="text-xl md:text-2xl font-bold text-center mb-2">
                  What are your marketing goals?
                </h1>
                <p className="text-white/60 text-center mb-6 md:mb-8 text-sm md:text-base">
                  Select all that apply
                </p>

                <div className="grid grid-cols-2 gap-3 md:gap-4">
                  {marketingGoals.map((goal) => {
                    const isSelected = goals.includes(goal.id);
                    return (
                      <button
                        key={goal.id}
                        onClick={() => toggleGoal(goal.id)}
                        className={cn(
                          "p-4 md:p-6 rounded-xl border text-left transition-all relative group",
                          isSelected
                            ? "border-electric bg-electric/10"
                            : "border-white/10 hover:border-white/20"
                        )}
                      >
                        {isSelected && (
                          <div className="absolute top-2 right-2 md:top-3 md:right-3 w-5 h-5 rounded-full bg-electric flex items-center justify-center">
                            <Check className="w-3 h-3 text-midnight" />
                          </div>
                        )}
                        <goal.icon
                          className={cn(
                            "w-6 h-6 md:w-8 md:h-8 mb-2 md:mb-3 transition-colors",
                            isSelected ? "text-electric" : "text-white/40 group-hover:text-white/60"
                          )}
                        />
                        <div
                          className={cn(
                            "font-medium text-sm md:text-base transition-colors",
                            isSelected ? "text-electric" : "text-white/80"
                          )}
                        >
                          {goal.label}
                        </div>
                        <div className="text-xs text-white/40 mt-1 hidden md:block">
                          {goal.description}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {/* Step 5: Channels & Budget */}
            {step === 5 && (
              <motion.div
                key="step5"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <h1 className="text-xl md:text-2xl font-bold text-center mb-2">
                  Almost there!
                </h1>
                <p className="text-white/60 text-center mb-6 md:mb-8 text-sm md:text-base">
                  Tell us about your marketing channels and budget
                </p>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm text-white/60 mb-3">
                      Which channels do you use? *
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {marketingChannels.map((channel) => {
                        const isSelected = channels.includes(channel.id);
                        return (
                          <button
                            key={channel.id}
                            onClick={() => toggleChannel(channel.id)}
                            className={cn(
                              "p-3 rounded-xl border text-sm text-left transition-all flex items-center gap-3",
                              isSelected
                                ? "border-electric bg-electric/10 text-electric"
                                : "border-white/10 hover:border-white/20 text-white/60 hover:text-white"
                            )}
                          >
                            <channel.icon className="w-5 h-5" />
                            {channel.label}
                            {isSelected && <Check className="w-4 h-4 ml-auto" />}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-white/60 mb-3">
                      Monthly marketing budget *
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {budgetRanges.map((range) => (
                        <button
                          key={range.value}
                          onClick={() => setBudget(range.value)}
                          className={cn(
                            "p-2.5 md:p-3 rounded-xl border text-xs md:text-sm text-left transition-all",
                            budget === range.value
                              ? "border-electric bg-electric/10 text-electric"
                              : "border-white/10 hover:border-white/20 text-white/60 hover:text-white"
                          )}
                        >
                          {range.label}
                        </button>
                      ))}
                    </div>
                  </div>
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
          <div className="flex items-center justify-between mt-6 md:mt-8 pt-4 md:pt-6 border-t border-white/5">
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
                  {step === totalSteps ? "Launch NeuroCron" : step === 1 ? "Get Started" : "Continue"}
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Skip option */}
        <p className="text-center text-xs md:text-sm text-white/40 mt-4 md:mt-6">
          Need help?{" "}
          <a href="mailto:support@neurocron.com" className="text-electric hover:underline">
            Contact support
          </a>
        </p>
      </motion.div>
    </div>
  );
}
