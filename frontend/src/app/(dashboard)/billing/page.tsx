"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  CreditCard,
  Check,
  Sparkles,
  Zap,
  Building2,
  Loader2,
  ExternalLink,
  Download,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Plan {
  id: string;
  name: string;
  price_monthly: number | null;
  price_yearly: number | null;
  features: string[];
  limits: Record<string, number>;
  is_custom: boolean;
}

interface Subscription {
  plan: string;
  plan_name: string;
  status: string;
  limits: Record<string, number>;
  features: string[];
  current_period_end: string;
}

interface Usage {
  used: number;
  limit: number;
}

export default function BillingPage() {
  const { organization } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [usage, setUsage] = useState<Record<string, Usage>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [billingInterval, setBillingInterval] = useState<"month" | "year">("month");

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [plansRes, subRes, usageRes] = await Promise.all([
        authFetch("/api/v1/billing/plans"),
        authFetch(`/api/v1/billing/subscription?org_id=${organization.id}`),
        authFetch(`/api/v1/billing/usage?org_id=${organization.id}`),
      ]);

      if (plansRes.ok) {
        const data = await plansRes.json();
        setPlans(data.plans);
      }
      if (subRes.ok) {
        const data = await subRes.json();
        setSubscription(data);
      }
      if (usageRes.ok) {
        const data = await usageRes.json();
        setUsage(data.usage);
      }
    } catch (error) {
      console.error("Failed to fetch billing data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpgrade = async (planId: string) => {
    if (!organization) return;

    try {
      const response = await authFetch(
        `/api/v1/billing/checkout?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            plan: planId,
            interval: billingInterval,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        // In production, redirect to Stripe checkout
        window.open(data.checkout_url, "_blank");
      }
    } catch (error) {
      console.error("Failed to create checkout:", error);
    }
  };

  const handleManageBilling = async () => {
    if (!organization) return;

    try {
      const response = await authFetch(
        `/api/v1/billing/portal?org_id=${organization.id}`,
        { method: "POST" }
      );

      if (response.ok) {
        const data = await response.json();
        window.open(data.portal_url, "_blank");
      }
    } catch (error) {
      console.error("Failed to open billing portal:", error);
    }
  };

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case "free":
        return Sparkles;
      case "starter":
        return Zap;
      case "growth":
        return CreditCard;
      case "enterprise":
        return Building2;
      default:
        return Sparkles;
    }
  };

  const formatLimit = (value: number) => {
    if (value === -1) return "Unlimited";
    if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
    return value.toString();
  };

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === -1) return 0;
    return Math.min((used / limit) * 100, 100);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-electric" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center">
            <CreditCard className="w-5 h-5 text-electric" />
          </div>
          Billing & Plans
        </h1>
        <p className="text-white/60 mt-1">
          Manage your subscription and view usage
        </p>
      </div>

      {/* Current Plan & Usage */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Current Plan */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Current Plan</h2>
          {subscription && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold capitalize">
                    {subscription.plan_name}
                  </div>
                  <div className="text-sm text-white/50">
                    {subscription.status === "active" ? (
                      <span className="text-green-400">Active</span>
                    ) : (
                      subscription.status
                    )}
                  </div>
                </div>
                <button
                  onClick={handleManageBilling}
                  className="btn-secondary text-sm py-2 flex items-center gap-2"
                >
                  Manage
                  <ExternalLink className="w-4 h-4" />
                </button>
              </div>
              <div className="pt-4 border-t border-white/10">
                <div className="text-sm text-white/50 mb-2">
                  Current period ends
                </div>
                <div>
                  {new Date(subscription.current_period_end).toLocaleDateString()}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Usage */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Usage This Month</h2>
          <div className="space-y-4">
            {Object.entries(usage).map(([key, value]) => (
              <div key={key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="capitalize">{key.replace("_", " ")}</span>
                  <span>
                    {value.used.toLocaleString()} / {formatLimit(value.limit)}
                  </span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all",
                      getUsagePercentage(value.used, value.limit) > 80
                        ? "bg-red-400"
                        : getUsagePercentage(value.used, value.limit) > 50
                        ? "bg-yellow-400"
                        : "bg-electric"
                    )}
                    style={{
                      width: `${getUsagePercentage(value.used, value.limit)}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Billing Toggle */}
      <div className="flex justify-center">
        <div className="inline-flex items-center gap-2 p-1 bg-white/5 rounded-xl">
          <button
            onClick={() => setBillingInterval("month")}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              billingInterval === "month"
                ? "bg-electric text-midnight"
                : "text-white/60 hover:text-white"
            )}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingInterval("year")}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              billingInterval === "year"
                ? "bg-electric text-midnight"
                : "text-white/60 hover:text-white"
            )}
          >
            Yearly
            <span className="ml-2 px-2 py-0.5 bg-green-400/20 text-green-400 text-xs rounded-full">
              Save 20%
            </span>
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid md:grid-cols-4 gap-6">
        {plans.map((plan, index) => {
          const Icon = getPlanIcon(plan.id);
          const isCurrentPlan = subscription?.plan === plan.id;
          const price =
            billingInterval === "year"
              ? plan.price_yearly
              : plan.price_monthly;

          return (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "card relative",
                isCurrentPlan && "ring-2 ring-electric",
                plan.id === "growth" && "bg-gradient-to-b from-electric/10 to-transparent"
              )}
            >
              {plan.id === "growth" && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-electric text-midnight text-xs font-bold rounded-full">
                  POPULAR
                </div>
              )}

              <div className="mb-6">
                <div
                  className={cn(
                    "w-12 h-12 rounded-xl flex items-center justify-center mb-4",
                    plan.id === "free"
                      ? "bg-white/10"
                      : plan.id === "starter"
                      ? "bg-blue-500/10"
                      : plan.id === "growth"
                      ? "bg-electric/10"
                      : "bg-purple-500/10"
                  )}
                >
                  <Icon
                    className={cn(
                      "w-6 h-6",
                      plan.id === "free"
                        ? "text-white/60"
                        : plan.id === "starter"
                        ? "text-blue-400"
                        : plan.id === "growth"
                        ? "text-electric"
                        : "text-purple-400"
                    )}
                  />
                </div>
                <h3 className="text-xl font-bold">{plan.name}</h3>
                <div className="mt-2">
                  {plan.is_custom ? (
                    <span className="text-2xl font-bold">Custom</span>
                  ) : (
                    <>
                      <span className="text-3xl font-bold">
                        ${billingInterval === "year" ? Math.round((price || 0) / 12) : price}
                      </span>
                      <span className="text-white/50">/mo</span>
                    </>
                  )}
                </div>
                {billingInterval === "year" && !plan.is_custom && price && (
                  <div className="text-sm text-white/50">
                    ${price} billed yearly
                  </div>
                )}
              </div>

              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                    {feature}
                  </li>
                ))}
              </ul>

              {isCurrentPlan ? (
                <button
                  disabled
                  className="w-full py-2 px-4 rounded-xl bg-white/10 text-white/50 text-sm font-medium"
                >
                  Current Plan
                </button>
              ) : plan.is_custom ? (
                <a
                  href="mailto:sales@neurocron.com"
                  className="block w-full py-2 px-4 rounded-xl bg-purple-500 text-white text-center text-sm font-medium hover:bg-purple-600 transition-colors"
                >
                  Contact Sales
                </a>
              ) : (
                <button
                  onClick={() => handleUpgrade(plan.id)}
                  className={cn(
                    "w-full py-2 px-4 rounded-xl text-sm font-medium transition-colors",
                    plan.id === "growth"
                      ? "bg-electric text-midnight hover:bg-electric/90"
                      : "bg-white/10 text-white hover:bg-white/20"
                  )}
                >
                  {subscription?.plan === "free" ? "Upgrade" : "Switch Plan"}
                </button>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Invoices */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Recent Invoices</h2>
        <div className="text-center py-8 text-white/50">
          <Download className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>No invoices yet</p>
          <p className="text-sm">Invoices will appear here after your first payment</p>
        </div>
      </div>
    </div>
  );
}

