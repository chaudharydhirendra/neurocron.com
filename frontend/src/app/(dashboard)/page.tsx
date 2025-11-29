"use client";

import { motion } from "framer-motion";
import {
  TrendingUp,
  TrendingDown,
  Users,
  DollarSign,
  MousePointer,
  Eye,
  Target,
  Zap,
  MessageSquare,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";

const stats = [
  {
    name: "Total Spend",
    value: "$12,450",
    change: "+12.5%",
    trend: "up",
    icon: DollarSign,
  },
  {
    name: "Impressions",
    value: "2.4M",
    change: "+8.2%",
    trend: "up",
    icon: Eye,
  },
  {
    name: "Clicks",
    value: "45.2K",
    change: "-2.1%",
    trend: "down",
    icon: MousePointer,
  },
  {
    name: "Conversions",
    value: "1,234",
    change: "+15.3%",
    trend: "up",
    icon: Target,
  },
];

const recentCampaigns = [
  { name: "Black Friday Sale", status: "active", spent: "$2,450", conversions: 234 },
  { name: "Product Launch Q4", status: "active", spent: "$1,890", conversions: 167 },
  { name: "Brand Awareness", status: "paused", spent: "$890", conversions: 45 },
];

const suggestions = [
  "Increase budget for 'Black Friday Sale' — it's outperforming by 23%",
  "3 ad creatives are underperforming. Want me to generate new variants?",
  "Your competitor launched a new campaign. View analysis?",
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Command Center</h1>
          <p className="text-white/60 mt-1">
            Welcome back! Here&apos;s your marketing overview.
          </p>
        </div>
        <div className="text-sm text-white/50">
          Last updated: Just now
        </div>
      </div>

      {/* NeuroCopilot Suggestions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-4 border-electric/20"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-neural-gradient flex items-center justify-center">
            <MessageSquare className="w-4 h-4" />
          </div>
          <span className="font-medium">NeuroCopilot Suggestions</span>
        </div>
        <div className="space-y-2">
          {suggestions.map((suggestion, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors cursor-pointer group"
            >
              <div className="flex items-center gap-3">
                <Zap className="w-4 h-4 text-electric" />
                <span className="text-sm text-white/80">{suggestion}</span>
              </div>
              <ArrowRight className="w-4 h-4 text-white/40 group-hover:text-electric transition-colors" />
            </div>
          ))}
        </div>
        <Link
          href="/dashboard/copilot"
          className="flex items-center gap-2 mt-4 text-sm text-electric hover:underline"
        >
          Ask NeuroCopilot anything
          <ArrowRight className="w-4 h-4" />
        </Link>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="p-2 rounded-lg bg-white/5">
                <stat.icon className="w-5 h-5 text-white/60" />
              </div>
              <div
                className={`flex items-center gap-1 text-sm ${
                  stat.trend === "up" ? "text-green-400" : "text-red-400"
                }`}
              >
                {stat.trend === "up" ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                {stat.change}
              </div>
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm text-white/50 mt-1">{stat.name}</div>
          </motion.div>
        ))}
      </div>

      {/* Recent Campaigns */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold">Active Campaigns</h2>
          <Link
            href="/dashboard/campaigns"
            className="text-sm text-electric hover:underline"
          >
            View all
          </Link>
        </div>
        <div className="space-y-3">
          {recentCampaigns.map((campaign, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div
                  className={`w-2 h-2 rounded-full ${
                    campaign.status === "active" ? "bg-green-400" : "bg-yellow-400"
                  }`}
                />
                <div>
                  <div className="font-medium">{campaign.name}</div>
                  <div className="text-sm text-white/50 capitalize">
                    {campaign.status}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-8">
                <div className="text-right">
                  <div className="font-medium">{campaign.spent}</div>
                  <div className="text-sm text-white/50">Spent</div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{campaign.conversions}</div>
                  <div className="text-sm text-white/50">Conversions</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

