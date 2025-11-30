"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  ShieldAlert,
  TrendingDown,
  DollarSign,
  Users,
  Mail,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  ChevronRight,
  Play,
  Plus,
  Gift,
  Star,
  Trophy,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface ChurnPrediction {
  customer_id: string;
  customer_name: string;
  customer_email: string;
  risk_score: number;
  risk_level: string;
  risk_factors: Array<{ factor: string; weight: number; description: string }>;
  days_since_activity: number;
  computed_at: string;
}

interface RetentionOverview {
  risk_distribution: Record<string, number>;
  at_risk_customers: number;
  revenue_at_risk: number;
  retention_rate: number;
  churn_rate: number;
  campaigns: {
    total_sent: number;
    total_converted: number;
    conversion_rate: number;
  };
}

export default function RetentionPage() {
  const { organization } = useAuth();
  const [overview, setOverview] = useState<RetentionOverview | null>(null);
  const [predictions, setPredictions] = useState<ChurnPrediction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "predictions" | "campaigns" | "loyalty">("overview");

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [overviewRes, predictionsRes] = await Promise.all([
        authFetch(`/api/v1/retention/analytics/overview?org_id=${organization.id}`),
        authFetch(`/api/v1/retention/predictions?org_id=${organization.id}&limit=20`),
      ]);

      if (overviewRes.ok) {
        const data = await overviewRes.json();
        setOverview(data);
      }
      if (predictionsRes.ok) {
        const data = await predictionsRes.json();
        setPredictions(data.predictions || []);
      }
    } catch (error) {
      console.error("Failed to fetch retention data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case "critical":
        return "text-red-500 bg-red-500/10";
      case "high":
        return "text-orange-500 bg-orange-500/10";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10";
      default:
        return "text-green-500 bg-green-500/10";
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            RetentionAI
          </h1>
          <p className="text-white/60 mt-1">
            Predict churn, automate retention campaigns, manage loyalty
          </p>
        </div>
        <button
          onClick={() => authFetch(`/api/v1/retention/predictions/compute?org_id=${organization?.id}`, { method: "POST" }).then(fetchData)}
          className="btn-primary flex items-center gap-2"
        >
          <Play className="w-4 h-4" />
          Compute Predictions
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {[
          { id: "overview", label: "Overview", icon: ShieldAlert },
          { id: "predictions", label: "At-Risk Customers", icon: AlertTriangle },
          { id: "campaigns", label: "Campaigns", icon: Mail },
          { id: "loyalty", label: "Loyalty Program", icon: Gift },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-colors",
              activeTab === tab.id
                ? "bg-electric text-white"
                : "text-white/60 hover:text-white hover:bg-white/5"
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-electric" />
        </div>
      ) : activeTab === "overview" ? (
        <>
          {/* Stats Grid */}
          {overview && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-400">
                      {overview.retention_rate}%
                    </div>
                    <div className="text-xs text-white/50">Retention Rate</div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="card p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                    <TrendingDown className="w-5 h-5 text-red-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-red-400">
                      {overview.churn_rate}%
                    </div>
                    <div className="text-xs text-white/50">Churn Rate</div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="card p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
                    <Users className="w-5 h-5 text-orange-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {overview.at_risk_customers}
                    </div>
                    <div className="text-xs text-white/50">At-Risk Customers</div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="card p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <DollarSign className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {formatCurrency(overview.revenue_at_risk)}
                    </div>
                    <div className="text-xs text-white/50">Revenue at Risk</div>
                  </div>
                </div>
              </motion.div>
            </div>
          )}

          {/* Risk Distribution */}
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
              <div className="space-y-4">
                {overview && Object.entries(overview.risk_distribution).map(([level, count]) => {
                  const total = Object.values(overview.risk_distribution).reduce((a, b) => a + b, 0);
                  const percentage = total > 0 ? (count / total) * 100 : 0;
                  return (
                    <div key={level} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className={cn("px-2 py-0.5 rounded text-sm capitalize", getRiskColor(level))}>
                          {level}
                        </span>
                        <span className="text-white/60">{count} customers ({percentage.toFixed(0)}%)</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          className={cn(
                            "h-full rounded-full",
                            level === "critical" ? "bg-red-500" :
                            level === "high" ? "bg-orange-500" :
                            level === "medium" ? "bg-yellow-500" : "bg-green-500"
                          )}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4">Campaign Performance</h3>
              {overview && (
                <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold">{overview.campaigns.total_sent}</div>
                      <div className="text-sm text-white/50">Total Sent</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-green-400">{overview.campaigns.total_converted}</div>
                      <div className="text-sm text-white/50">Converted</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-electric">{overview.campaigns.conversion_rate}%</div>
                      <div className="text-sm text-white/50">Rate</div>
                    </div>
                  </div>
                  <button className="btn-secondary w-full">View All Campaigns</button>
                </div>
              )}
            </div>
          </div>
        </>
      ) : activeTab === "predictions" ? (
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-white/10 flex items-center justify-between">
            <div>
              <h3 className="font-semibold">At-Risk Customers</h3>
              <p className="text-sm text-white/50">Customers predicted to churn</p>
            </div>
          </div>
          {predictions.length === 0 ? (
            <div className="text-center py-12">
              <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-white/20" />
              <h3 className="text-lg font-medium mb-2">No predictions yet</h3>
              <p className="text-white/50 mb-4">Run the prediction model to identify at-risk customers</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {predictions.map((prediction) => (
                <div
                  key={prediction.customer_id}
                  className="p-4 hover:bg-white/5 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={cn(
                        "w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold",
                        getRiskColor(prediction.risk_level)
                      )}>
                        {prediction.risk_score}
                      </div>
                      <div>
                        <div className="font-medium">{prediction.customer_name || prediction.customer_email}</div>
                        <div className="text-sm text-white/50">{prediction.customer_email}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={cn("px-3 py-1 rounded-full text-sm capitalize", getRiskColor(prediction.risk_level))}>
                        {prediction.risk_level}
                      </span>
                      <button className="btn-secondary py-2 px-3 text-sm">
                        Take Action
                      </button>
                    </div>
                  </div>
                  {prediction.risk_factors.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {prediction.risk_factors.map((factor, i) => (
                        <span key={i} className="px-2 py-1 bg-white/5 rounded text-xs text-white/60">
                          {factor.description}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ) : activeTab === "campaigns" ? (
        <div className="space-y-6">
          <div className="flex justify-end">
            <button className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Campaign
            </button>
          </div>
          <div className="card p-6 text-center">
            <Mail className="w-12 h-12 mx-auto mb-4 text-white/20" />
            <h3 className="text-lg font-medium mb-2">Retention Campaigns</h3>
            <p className="text-white/50 mb-4">Create automated campaigns to win back at-risk customers</p>
            <button className="btn-primary">Create First Campaign</button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid md:grid-cols-3 gap-4">
            <div className="card p-6 text-center">
              <Star className="w-12 h-12 mx-auto mb-4 text-yellow-400" />
              <h3 className="text-xl font-bold mb-2">Loyalty Program</h3>
              <p className="text-white/50 mb-4">Reward your best customers with points and perks</p>
              <button className="btn-primary">Configure Program</button>
            </div>
            <div className="card p-6 text-center">
              <Trophy className="w-12 h-12 mx-auto mb-4 text-purple-400" />
              <h3 className="text-xl font-bold mb-2">Tier System</h3>
              <p className="text-white/50 mb-4">Create Bronze, Silver, Gold tiers with exclusive benefits</p>
              <button className="btn-secondary">Set Up Tiers</button>
            </div>
            <div className="card p-6 text-center">
              <Gift className="w-12 h-12 mx-auto mb-4 text-green-400" />
              <h3 className="text-xl font-bold mb-2">Rewards Catalog</h3>
              <p className="text-white/50 mb-4">Define rewards customers can redeem with their points</p>
              <button className="btn-secondary">Add Rewards</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

