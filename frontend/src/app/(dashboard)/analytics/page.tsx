"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Eye,
  MousePointer,
  DollarSign,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Filter,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  Legend,
} from "recharts";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

// Mock data for demonstration
const trafficData = [
  { date: "Mon", visits: 2400, pageViews: 4000, bounceRate: 35 },
  { date: "Tue", visits: 1398, pageViews: 3000, bounceRate: 42 },
  { date: "Wed", visits: 9800, pageViews: 15000, bounceRate: 28 },
  { date: "Thu", visits: 3908, pageViews: 6000, bounceRate: 38 },
  { date: "Fri", visits: 4800, pageViews: 7500, bounceRate: 32 },
  { date: "Sat", visits: 3800, pageViews: 5200, bounceRate: 45 },
  { date: "Sun", visits: 4300, pageViews: 6800, bounceRate: 40 },
];

const channelData = [
  { name: "Organic Search", value: 35, color: "#0066FF" },
  { name: "Paid Ads", value: 28, color: "#8B5CF6" },
  { name: "Social Media", value: 22, color: "#10B981" },
  { name: "Email", value: 10, color: "#F59E0B" },
  { name: "Direct", value: 5, color: "#EF4444" },
];

const campaignPerformance = [
  { name: "Product Launch", spend: 5000, revenue: 15000, roas: 3.0 },
  { name: "Brand Awareness", spend: 3000, revenue: 4500, roas: 1.5 },
  { name: "Retargeting", spend: 2000, revenue: 8000, roas: 4.0 },
  { name: "Newsletter", spend: 500, revenue: 2500, roas: 5.0 },
];

const conversionFunnel = [
  { stage: "Impressions", value: 100000, rate: 100 },
  { stage: "Clicks", value: 5000, rate: 5 },
  { stage: "Visitors", value: 4000, rate: 80 },
  { stage: "Leads", value: 400, rate: 10 },
  { stage: "Customers", value: 80, rate: 20 },
];

interface MetricCardProps {
  title: string;
  value: string;
  change: number;
  icon: React.ElementType;
  trend?: "up" | "down" | "neutral";
}

function MetricCard({ title, value, change, icon: Icon, trend = "neutral" }: MetricCardProps) {
  const isPositive = trend === "up" || (trend === "neutral" && change >= 0);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-white/60 text-sm">{title}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
          <div className={cn(
            "flex items-center gap-1 mt-2 text-sm",
            isPositive ? "text-green-400" : "text-red-400"
          )}>
            {isPositive ? (
              <ArrowUpRight className="w-4 h-4" />
            ) : (
              <ArrowDownRight className="w-4 h-4" />
            )}
            <span>{Math.abs(change)}%</span>
            <span className="text-white/40">vs last period</span>
          </div>
        </div>
        <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center">
          <Icon className="w-5 h-5 text-electric" />
        </div>
      </div>
    </motion.div>
  );
}

export default function AnalyticsPage() {
  const { organization } = useAuth();
  const [dateRange, setDateRange] = useState("7d");

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-midnight-100 border border-white/10 rounded-xl p-3 shadow-xl">
          <p className="font-medium mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value.toLocaleString()}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-electric" />
            </div>
            InsightCortex
          </h1>
          <p className="text-white/60 mt-1">
            Unified analytics across all your marketing channels
          </p>
        </div>

        {/* Date Range Selector */}
        <div className="flex items-center gap-2">
          {["24h", "7d", "30d", "90d"].map((range) => (
            <button
              key={range}
              onClick={() => setDateRange(range)}
              className={cn(
                "px-4 py-2 rounded-xl text-sm font-medium transition-colors",
                dateRange === range
                  ? "bg-electric text-midnight"
                  : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
              )}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Visitors"
          value="28.5K"
          change={12.5}
          icon={Users}
          trend="up"
        />
        <MetricCard
          title="Page Views"
          value="124.2K"
          change={8.3}
          icon={Eye}
          trend="up"
        />
        <MetricCard
          title="Conversion Rate"
          value="3.24%"
          change={-2.1}
          icon={Target}
          trend="down"
        />
        <MetricCard
          title="Revenue"
          value="$45,230"
          change={18.7}
          icon={DollarSign}
          trend="up"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Traffic Over Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 card"
        >
          <h3 className="text-lg font-semibold mb-4">Traffic Overview</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trafficData}>
                <defs>
                  <linearGradient id="colorVisits" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0066FF" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0066FF" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorPageViews" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis dataKey="date" stroke="#ffffff40" fontSize={12} />
                <YAxis stroke="#ffffff40" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="visits"
                  stroke="#0066FF"
                  fillOpacity={1}
                  fill="url(#colorVisits)"
                  name="Visits"
                />
                <Area
                  type="monotone"
                  dataKey="pageViews"
                  stroke="#8B5CF6"
                  fillOpacity={1}
                  fill="url(#colorPageViews)"
                  name="Page Views"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Traffic Sources */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">Traffic Sources</h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={channelData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {channelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-4">
            {channelData.map((channel) => (
              <div key={channel.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: channel.color }}
                  />
                  <span className="text-white/60">{channel.name}</span>
                </div>
                <span className="font-medium">{channel.value}%</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Campaign Performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">Campaign Performance</h3>
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={campaignPerformance} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis type="number" stroke="#ffffff40" fontSize={12} />
                <YAxis
                  dataKey="name"
                  type="category"
                  stroke="#ffffff40"
                  fontSize={12}
                  width={100}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar dataKey="spend" fill="#EF4444" name="Spend ($)" radius={[0, 4, 4, 0]} />
                <Bar dataKey="revenue" fill="#10B981" name="Revenue ($)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 pt-4 border-t border-white/10">
            <div className="flex items-center justify-between text-sm">
              <span className="text-white/60">Total ROAS</span>
              <span className="font-bold text-green-400">3.2x</span>
            </div>
          </div>
        </motion.div>

        {/* Conversion Funnel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">Conversion Funnel</h3>
          <div className="space-y-3">
            {conversionFunnel.map((stage, index) => {
              const widthPercent = (stage.value / conversionFunnel[0].value) * 100;
              return (
                <div key={stage.stage}>
                  <div className="flex items-center justify-between mb-1 text-sm">
                    <span className="text-white/60">{stage.stage}</span>
                    <span className="font-medium">
                      {stage.value.toLocaleString()}
                      <span className="text-white/40 ml-2">({stage.rate}%)</span>
                    </span>
                  </div>
                  <div className="h-8 bg-white/5 rounded-lg overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${widthPercent}%` }}
                      transition={{ delay: 0.5 + index * 0.1, duration: 0.5 }}
                      className="h-full bg-gradient-to-r from-electric to-purple-500 rounded-lg flex items-center justify-end pr-3"
                    >
                      {widthPercent > 20 && (
                        <span className="text-xs font-medium">
                          {widthPercent.toFixed(0)}%
                        </span>
                      )}
                    </motion.div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-4 pt-4 border-t border-white/10">
            <div className="flex items-center justify-between text-sm">
              <span className="text-white/60">Overall Conversion</span>
              <span className="font-bold text-electric">0.08%</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Top Content Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card"
      >
        <h3 className="text-lg font-semibold mb-4">Top Performing Content</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 text-sm text-white/60 font-medium">Content</th>
                <th className="text-right py-3 text-sm text-white/60 font-medium">Views</th>
                <th className="text-right py-3 text-sm text-white/60 font-medium">Engagement</th>
                <th className="text-right py-3 text-sm text-white/60 font-medium">Conversions</th>
                <th className="text-right py-3 text-sm text-white/60 font-medium">Trend</th>
              </tr>
            </thead>
            <tbody>
              {[
                { title: "10 Marketing Trends for 2024", views: 12450, engagement: "8.2%", conversions: 234, trend: 15 },
                { title: "Ultimate Guide to AI Marketing", views: 9823, engagement: "6.8%", conversions: 187, trend: 8 },
                { title: "Product Launch Campaign Results", views: 7654, engagement: "12.1%", conversions: 156, trend: -3 },
                { title: "Social Media Strategy Template", views: 6234, engagement: "9.4%", conversions: 98, trend: 22 },
                { title: "Email Marketing Best Practices", views: 5123, engagement: "7.6%", conversions: 76, trend: 5 },
              ].map((content, index) => (
                <tr key={index} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-3 font-medium">{content.title}</td>
                  <td className="py-3 text-right text-white/60">{content.views.toLocaleString()}</td>
                  <td className="py-3 text-right text-white/60">{content.engagement}</td>
                  <td className="py-3 text-right text-white/60">{content.conversions}</td>
                  <td className="py-3 text-right">
                    <span className={cn(
                      "inline-flex items-center gap-1",
                      content.trend >= 0 ? "text-green-400" : "text-red-400"
                    )}>
                      {content.trend >= 0 ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <TrendingDown className="w-4 h-4" />
                      )}
                      {Math.abs(content.trend)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}

