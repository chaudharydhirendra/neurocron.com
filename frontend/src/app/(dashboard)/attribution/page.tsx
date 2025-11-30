"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  GitMerge,
  DollarSign,
  TrendingUp,
  ArrowRight,
  Loader2,
  BarChart3,
  PieChart,
  RefreshCw,
  Info,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface ChannelData {
  channel: string;
  revenue: number;
  conversions: number;
}

interface CampaignData {
  campaign: string;
  revenue: number;
  conversions: number;
}

interface AttributionOverview {
  period_days: number;
  attribution_model: string;
  summary: {
    total_revenue: number;
    total_conversions: number;
    avg_order_value: number;
  };
  by_channel: ChannelData[];
  top_campaigns: CampaignData[];
}

interface ConversionPath {
  path: string[];
  conversions: number;
  revenue: number;
  avg_touchpoints: number;
}

export default function AttributionPage() {
  const { organization } = useAuth();
  const [overview, setOverview] = useState<AttributionOverview | null>(null);
  const [paths, setPaths] = useState<ConversionPath[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState("last_touch");
  const [activeTab, setActiveTab] = useState<"overview" | "channels" | "journeys">("overview");

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization, selectedModel]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [overviewRes, pathsRes] = await Promise.all([
        authFetch(`/api/v1/attribution/analytics/overview?org_id=${organization.id}&model=${selectedModel}`),
        authFetch(`/api/v1/attribution/analytics/journey?org_id=${organization.id}`),
      ]);

      if (overviewRes.ok) {
        const data = await overviewRes.json();
        setOverview(data);
      }
      if (pathsRes.ok) {
        const data = await pathsRes.json();
        setPaths(data.conversion_paths || []);
      }
    } catch (error) {
      console.error("Failed to fetch attribution data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const models = [
    { id: "last_touch", label: "Last Touch", description: "100% credit to last interaction" },
    { id: "first_touch", label: "First Touch", description: "100% credit to first interaction" },
    { id: "linear", label: "Linear", description: "Equal credit across all touchpoints" },
    { id: "time_decay", label: "Time Decay", description: "More credit to recent touchpoints" },
    { id: "data_driven", label: "Data-Driven", description: "AI-optimized attribution" },
  ];

  const totalChannelRevenue = overview?.by_channel.reduce((sum, c) => sum + c.revenue, 0) || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
              <GitMerge className="w-5 h-5 text-white" />
            </div>
            RevenueLink
          </h1>
          <p className="text-white/60 mt-1">
            Multi-touch attribution and revenue tracking
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="input py-2"
          >
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.label}
              </option>
            ))}
          </select>
          <button
            onClick={fetchData}
            className="btn-secondary p-2"
          >
            <RefreshCw className={cn("w-5 h-5", isLoading && "animate-spin")} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {[
          { id: "overview", label: "Overview", icon: BarChart3 },
          { id: "channels", label: "Channels", icon: PieChart },
          { id: "journeys", label: "Journeys", icon: GitMerge },
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
          {/* Stats */}
          {overview && (
            <div className="grid grid-cols-3 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-6"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                    <DollarSign className="w-6 h-6 text-green-400" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold">
                      {formatCurrency(overview.summary.total_revenue)}
                    </div>
                    <div className="text-white/50">Total Revenue</div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="card p-6"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold">
                      {overview.summary.total_conversions}
                    </div>
                    <div className="text-white/50">Conversions</div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="card p-6"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                    <BarChart3 className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <div className="text-3xl font-bold">
                      {formatCurrency(overview.summary.avg_order_value)}
                    </div>
                    <div className="text-white/50">Avg Order Value</div>
                  </div>
                </div>
              </motion.div>
            </div>
          )}

          {/* Top Campaigns */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Top Campaigns by Revenue</h3>
            {overview?.top_campaigns.length === 0 ? (
              <div className="text-center py-8 text-white/50">
                No campaign data available
              </div>
            ) : (
              <div className="space-y-3">
                {overview?.top_campaigns.map((campaign, index) => (
                  <div
                    key={campaign.campaign}
                    className="flex items-center gap-4 p-3 bg-white/5 rounded-lg"
                  >
                    <span className="w-8 h-8 rounded-full bg-electric/20 text-electric flex items-center justify-center font-bold text-sm">
                      {index + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{campaign.campaign}</div>
                      <div className="text-sm text-white/50">
                        {campaign.conversions} conversions
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-green-400">
                        {formatCurrency(campaign.revenue)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      ) : activeTab === "channels" ? (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Revenue by Channel</h3>
          {overview?.by_channel.length === 0 ? (
            <div className="text-center py-12 text-white/50">
              No channel data available
            </div>
          ) : (
            <div className="space-y-4">
              {overview?.by_channel.map((channel) => {
                const percentage = (channel.revenue / totalChannelRevenue) * 100;
                return (
                  <div key={channel.channel} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{channel.channel}</span>
                      <div className="flex items-center gap-4">
                        <span className="text-white/50">
                          {channel.conversions} conversions
                        </span>
                        <span className="font-bold">
                          {formatCurrency(channel.revenue)}
                        </span>
                      </div>
                    </div>
                    <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        className="h-full bg-gradient-to-r from-electric to-purple-500 rounded-full"
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Top Conversion Paths</h3>
          <div className="space-y-4">
            {paths.map((path, index) => (
              <div key={index} className="p-4 bg-white/5 rounded-lg">
                <div className="flex items-center gap-2 mb-3 flex-wrap">
                  {path.path.map((step, stepIndex) => (
                    <div key={stepIndex} className="flex items-center gap-2">
                      <span className="px-3 py-1 bg-electric/20 text-electric rounded-full text-sm">
                        {step}
                      </span>
                      {stepIndex < path.path.length - 1 && (
                        <ArrowRight className="w-4 h-4 text-white/30" />
                      )}
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <div>
                    <span className="text-white/50">Conversions: </span>
                    <span className="font-medium">{path.conversions}</span>
                  </div>
                  <div>
                    <span className="text-white/50">Revenue: </span>
                    <span className="font-medium text-green-400">
                      {formatCurrency(path.revenue)}
                    </span>
                  </div>
                  <div>
                    <span className="text-white/50">Avg Touchpoints: </span>
                    <span className="font-medium">{path.avg_touchpoints}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Insights */}
          <div className="mt-6 p-4 bg-electric/10 border border-electric/30 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Info className="w-5 h-5 text-electric" />
              <span className="font-medium">AI Insights</span>
            </div>
            <ul className="space-y-1 text-sm text-white/80">
              <li>• Multi-touch journeys convert 2.3x more than single-touch</li>
              <li>• Email is present in 60% of high-value conversions</li>
              <li>• Paid Search is the most common entry point</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

