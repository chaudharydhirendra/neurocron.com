"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Megaphone,
  TrendingUp,
  DollarSign,
  PauseCircle,
  FileEdit,
  Activity,
  ArrowUpRight,
  Plus,
  Sparkles,
  Clock,
  Zap,
  Target,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface DashboardStats {
  total_campaigns: number;
  active_campaigns: number;
  paused_campaigns: number;
  draft_campaigns: number;
  total_budget: number;
  active_budget: number;
}

interface RecentCampaign {
  id: string;
  name: string;
  status: string;
  budget: number | null;
  created_at: string;
}

interface DashboardData {
  stats: DashboardStats;
  recent_campaigns: RecentCampaign[];
  organization_name: string;
}

export default function DashboardPage() {
  const { organization, user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      if (!organization) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await authFetch(
          `/api/v1/dashboard/?org_id=${organization.id}`
        );
        if (response.ok) {
          const dashboardData = await response.json();
          setData(dashboardData);
        } else {
          setError("Failed to load dashboard");
        }
      } catch {
        setError("Network error");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboard();
  }, [organization]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-400 bg-green-400/10";
      case "paused":
        return "text-yellow-400 bg-yellow-400/10";
      case "draft":
        return "text-white/40 bg-white/5";
      case "completed":
        return "text-electric bg-electric/10";
      default:
        return "text-white/40 bg-white/5";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-pulse text-white/60">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Welcome back{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}
          </h1>
          <p className="text-white/60 mt-1">
            Here&apos;s what&apos;s happening with your marketing
          </p>
        </div>
        <Link href="/dashboard/campaigns/new" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Campaign
        </Link>
      </div>

      {/* NeuroCopilot Prompt */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card bg-neural-gradient/5 border-electric/20"
      >
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-neural-gradient flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-1">Ask NeuroCopilot</h3>
            <p className="text-white/60 text-sm mb-3">
              Get instant insights, launch campaigns, or optimize your marketing with AI
            </p>
            <div className="flex gap-2 flex-wrap">
              {[
                "Create a holiday campaign",
                "Analyze last month's performance",
                "Suggest content ideas",
              ].map((suggestion) => (
                <Link
                  key={suggestion}
                  href={`/dashboard/copilot?q=${encodeURIComponent(suggestion)}`}
                  className="text-sm px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-electric/30 transition-colors"
                >
                  {suggestion}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-white/60 text-sm">Total Campaigns</p>
              <p className="text-3xl font-bold mt-1">
                {data?.stats.total_campaigns ?? 0}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center">
              <Megaphone className="w-5 h-5 text-electric" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-white/60 text-sm">Active Campaigns</p>
              <p className="text-3xl font-bold mt-1 text-green-400">
                {data?.stats.active_campaigns ?? 0}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-green-400/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-green-400" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-white/60 text-sm">Total Budget</p>
              <p className="text-3xl font-bold mt-1">
                {formatCurrency(data?.stats.total_budget ?? 0)}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-purple-400/10 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-purple-400" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-white/60 text-sm">Active Budget</p>
              <p className="text-3xl font-bold mt-1 text-electric">
                {formatCurrency(data?.stats.active_budget ?? 0)}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-electric" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Campaigns */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="lg:col-span-2 card"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Recent Campaigns</h2>
            <Link
              href="/dashboard/campaigns"
              className="text-sm text-electric hover:underline flex items-center gap-1"
            >
              View all
              <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>

          {data?.recent_campaigns && data.recent_campaigns.length > 0 ? (
            <div className="space-y-3">
              {data.recent_campaigns.map((campaign) => (
                <Link
                  key={campaign.id}
                  href={`/dashboard/campaigns/${campaign.id}`}
                  className="flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-neural-gradient/20 flex items-center justify-center">
                      <Megaphone className="w-5 h-5 text-electric" />
                    </div>
                    <div>
                      <h3 className="font-medium group-hover:text-electric transition-colors">
                        {campaign.name}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span
                          className={cn(
                            "text-xs px-2 py-0.5 rounded-full capitalize",
                            getStatusColor(campaign.status)
                          )}
                        >
                          {campaign.status}
                        </span>
                        {campaign.budget && (
                          <span className="text-xs text-white/40">
                            {formatCurrency(campaign.budget)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <ArrowUpRight className="w-5 h-5 text-white/20 group-hover:text-electric transition-colors" />
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Megaphone className="w-12 h-12 text-white/20 mx-auto mb-4" />
              <h3 className="font-medium mb-2">No campaigns yet</h3>
              <p className="text-white/60 text-sm mb-4">
                Create your first campaign to get started
              </p>
              <Link href="/dashboard/campaigns/new" className="btn-primary">
                Create Campaign
              </Link>
            </div>
          )}
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <h2 className="text-lg font-semibold mb-6">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              href="/dashboard/campaigns/new"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-electric/10 transition-colors group"
            >
              <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center group-hover:bg-electric/20 transition-colors">
                <Zap className="w-5 h-5 text-electric" />
              </div>
              <div>
                <h3 className="font-medium">Launch Campaign</h3>
                <p className="text-xs text-white/40">Create a new marketing campaign</p>
              </div>
            </Link>

            <Link
              href="/dashboard/content"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-purple-500/10 transition-colors group"
            >
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
                <FileEdit className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h3 className="font-medium">Generate Content</h3>
                <p className="text-xs text-white/40">Create AI-powered content</p>
              </div>
            </Link>

            <Link
              href="/dashboard/audiences"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-green-500/10 transition-colors group"
            >
              <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center group-hover:bg-green-500/20 transition-colors">
                <Target className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <h3 className="font-medium">Build Audience</h3>
                <p className="text-xs text-white/40">Create target segments</p>
              </div>
            </Link>

            <Link
              href="/dashboard/analytics"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-orange-500/10 transition-colors group"
            >
              <div className="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center group-hover:bg-orange-500/20 transition-colors">
                <TrendingUp className="w-5 h-5 text-orange-400" />
              </div>
              <div>
                <h3 className="font-medium">View Analytics</h3>
                <p className="text-xs text-white/40">Check performance metrics</p>
              </div>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

