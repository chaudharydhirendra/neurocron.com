"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Megaphone,
  Target,
  DollarSign,
  Calendar,
  Loader2,
  Sparkles,
  Zap,
  Users,
  Mail,
  Share2,
  Search,
  ShoppingBag,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

const campaignTypes = [
  {
    id: "awareness",
    name: "Brand Awareness",
    description: "Increase visibility and recognition",
    icon: Megaphone,
    color: "electric",
  },
  {
    id: "lead_generation",
    name: "Lead Generation",
    description: "Capture potential customer information",
    icon: Users,
    color: "purple",
  },
  {
    id: "conversion",
    name: "Conversions",
    description: "Drive purchases and sign-ups",
    icon: ShoppingBag,
    color: "green",
  },
  {
    id: "traffic",
    name: "Website Traffic",
    description: "Drive visitors to your website",
    icon: Zap,
    color: "orange",
  },
  {
    id: "engagement",
    name: "Engagement",
    description: "Increase likes, comments, and shares",
    icon: Share2,
    color: "pink",
  },
  {
    id: "email",
    name: "Email Campaign",
    description: "Nurture leads with email sequences",
    icon: Mail,
    color: "cyan",
  },
];

const channels = [
  { id: "google", name: "Google Ads" },
  { id: "meta", name: "Meta (Facebook/Instagram)" },
  { id: "linkedin", name: "LinkedIn" },
  { id: "twitter", name: "Twitter/X" },
  { id: "tiktok", name: "TikTok" },
  { id: "email", name: "Email" },
  { id: "seo", name: "SEO/Content" },
];

export default function NewCampaignPage() {
  const router = useRouter();
  const { organization } = useAuth();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Form data
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [campaignType, setCampaignType] = useState("");
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const [budget, setBudget] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [goals, setGoals] = useState("");

  const toggleChannel = (channelId: string) => {
    setSelectedChannels((prev) =>
      prev.includes(channelId)
        ? prev.filter((c) => c !== channelId)
        : [...prev, channelId]
    );
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return name.length >= 3 && campaignType;
      case 2:
        return selectedChannels.length > 0;
      case 3:
        return true; // Budget is optional
      default:
        return false;
    }
  };

  const handleSubmit = async () => {
    if (!organization) return;
    
    setIsLoading(true);
    setError("");

    try {
      const response = await authFetch(
        `/api/v1/campaigns/?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            name,
            description: description || undefined,
            campaign_type: campaignType,
            channels: selectedChannels,
            budget: budget ? parseFloat(budget) : undefined,
            start_date: startDate || undefined,
            end_date: endDate || undefined,
            target_audience: targetAudience || undefined,
            goals: goals ? [goals] : undefined,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to create campaign");
      }

      const campaign = await response.json();
      router.push(`/dashboard/campaigns/${campaign.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      handleSubmit();
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link
          href="/dashboard/campaigns"
          className="p-2 rounded-xl hover:bg-white/5 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Create Campaign</h1>
          <p className="text-white/60 text-sm">
            Step {step} of 3 — {step === 1 ? "Basics" : step === 2 ? "Channels" : "Budget & Goals"}
          </p>
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2 mb-8">
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            className={cn(
              "h-1.5 rounded-full flex-1 transition-all duration-300",
              s <= step ? "bg-electric" : "bg-white/10"
            )}
          />
        ))}
      </div>

      {/* Form Steps */}
      <div className="card">
        {step === 1 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm text-white/60 mb-2">
                Campaign name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Summer Sale 2024"
                className="input"
                autoFocus
              />
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-2">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Briefly describe your campaign objectives..."
                className="input min-h-[100px] resize-none"
              />
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-3">
                Campaign type *
              </label>
              <div className="grid grid-cols-2 gap-3">
                {campaignTypes.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setCampaignType(type.id)}
                    className={cn(
                      "p-4 rounded-xl border text-left transition-all",
                      campaignType === type.id
                        ? "border-electric bg-electric/10"
                        : "border-white/10 hover:border-white/20"
                    )}
                  >
                    <type.icon
                      className={cn(
                        "w-6 h-6 mb-2",
                        campaignType === type.id ? "text-electric" : "text-white/40"
                      )}
                    />
                    <div className="font-medium">{type.name}</div>
                    <div className="text-xs text-white/50 mt-0.5">
                      {type.description}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm text-white/60 mb-3">
                Select marketing channels *
              </label>
              <div className="grid grid-cols-2 gap-3">
                {channels.map((channel) => (
                  <button
                    key={channel.id}
                    onClick={() => toggleChannel(channel.id)}
                    className={cn(
                      "p-4 rounded-xl border text-left transition-all flex items-center gap-3",
                      selectedChannels.includes(channel.id)
                        ? "border-electric bg-electric/10"
                        : "border-white/10 hover:border-white/20"
                    )}
                  >
                    <div
                      className={cn(
                        "w-5 h-5 rounded-md border-2 flex items-center justify-center transition-colors",
                        selectedChannels.includes(channel.id)
                          ? "border-electric bg-electric"
                          : "border-white/30"
                      )}
                    >
                      {selectedChannels.includes(channel.id) && (
                        <svg
                          className="w-3 h-3 text-midnight"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={3}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>
                    <span className="font-medium">{channel.name}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-2">
                Target audience
              </label>
              <input
                type="text"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="e.g., Tech-savvy millennials aged 25-35"
                className="input"
              />
            </div>
          </motion.div>
        )}

        {step === 3 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Start date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  End date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="input"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-2">
                Budget (USD)
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                <input
                  type="number"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  placeholder="5000"
                  className="input pl-11"
                  min="0"
                  step="100"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-white/60 mb-2">
                Primary goal
              </label>
              <input
                type="text"
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                placeholder="e.g., Increase website traffic by 30%"
                className="input"
              />
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                {error}
              </div>
            )}
          </motion.div>
        )}

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
                {step === 3 ? "Create Campaign" : "Continue"}
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

