"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  MousePointer2,
  Eye,
  Clock,
  TrendingDown,
  Smartphone,
  Monitor,
  Tablet,
  Search,
  Filter,
  Loader2,
  Play,
  ChevronRight,
  Layers,
  ArrowDown,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface BehaviorOverview {
  period_days: number;
  total_sessions: number;
  unique_visitors: number;
  avg_session_duration: number;
  bounce_rate: number;
  avg_scroll_depth: number;
  top_pages: Array<{ path: string; views: number; avg_time: number }>;
  devices: Record<string, number>;
}

interface Session {
  id: string;
  visitor_id: string;
  page_path: string;
  page_title: string;
  device_type: string;
  browser: string;
  country: string;
  duration_seconds: number;
  scroll_depth: number;
  clicks_count: number;
  is_bounce: boolean;
  started_at: string;
}

export default function BehaviorPage() {
  const { organization } = useAuth();
  const [overview, setOverview] = useState<BehaviorOverview | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "heatmaps" | "recordings">("overview");
  const [selectedPage, setSelectedPage] = useState("/");

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [overviewRes, sessionsRes] = await Promise.all([
        authFetch(`/api/v1/behavior/analytics/overview?org_id=${organization.id}&days=30`),
        authFetch(`/api/v1/behavior/sessions?org_id=${organization.id}&limit=20`),
      ]);

      if (overviewRes.ok) {
        const data = await overviewRes.json();
        setOverview(data);
      }
      if (sessionsRes.ok) {
        const data = await sessionsRes.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error("Failed to fetch behavior data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case "mobile":
        return Smartphone;
      case "tablet":
        return Tablet;
      default:
        return Monitor;
    }
  };

  const totalDevices = overview
    ? Object.values(overview.devices).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
              <MousePointer2 className="w-5 h-5 text-white" />
            </div>
            BehaviorMind
          </h1>
          <p className="text-white/60 mt-1">
            User behavior analytics, heatmaps & session recordings
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {[
          { id: "overview", label: "Overview", icon: Eye },
          { id: "heatmaps", label: "Heatmaps", icon: Layers },
          { id: "recordings", label: "Recordings", icon: Play },
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
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <Eye className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {overview.total_sessions.toLocaleString()}
                    </div>
                    <div className="text-xs text-white/50">Sessions (30d)</div>
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
                  <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {formatDuration(overview.avg_session_duration)}
                    </div>
                    <div className="text-xs text-white/50">Avg Duration</div>
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
                  <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                    <TrendingDown className="w-5 h-5 text-red-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {overview.bounce_rate}%
                    </div>
                    <div className="text-xs text-white/50">Bounce Rate</div>
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
                    <ArrowDown className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {overview.avg_scroll_depth}%
                    </div>
                    <div className="text-xs text-white/50">Avg Scroll Depth</div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="card p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-electric/10 flex items-center justify-center">
                    <MousePointer2 className="w-5 h-5 text-electric" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {overview.unique_visitors.toLocaleString()}
                    </div>
                    <div className="text-xs text-white/50">Unique Visitors</div>
                  </div>
                </div>
              </motion.div>
            </div>
          )}

          {/* Two Column Layout */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Top Pages */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4">Top Pages</h3>
              <div className="space-y-3">
                {overview?.top_pages.map((page, index) => (
                  <div
                    key={page.path}
                    className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 cursor-pointer transition-colors"
                    onClick={() => setSelectedPage(page.path)}
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full bg-electric/20 text-electric text-xs flex items-center justify-center">
                        {index + 1}
                      </span>
                      <span className="font-mono text-sm">{page.path}</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-white/60">
                      <span>{page.views.toLocaleString()} views</span>
                      <span>{formatDuration(page.avg_time)} avg</span>
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Device Breakdown */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4">Device Breakdown</h3>
              <div className="space-y-4">
                {overview &&
                  Object.entries(overview.devices).map(([device, count]) => {
                    const Icon = getDeviceIcon(device);
                    const percentage = totalDevices > 0 ? (count / totalDevices) * 100 : 0;
                    return (
                      <div key={device} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Icon className="w-4 h-4 text-white/60" />
                            <span className="capitalize">{device}</span>
                          </div>
                          <span className="text-white/60">
                            {count.toLocaleString()} ({percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            className="h-full bg-electric rounded-full"
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </>
      ) : activeTab === "heatmaps" ? (
        <div className="card p-6">
          <div className="text-center py-12">
            <Layers className="w-16 h-16 mx-auto mb-4 text-white/20" />
            <h3 className="text-xl font-semibold mb-2">Heatmap Visualization</h3>
            <p className="text-white/50 mb-6 max-w-md mx-auto">
              Click heatmaps show where users click most. Select a page to view its heatmap.
            </p>
            <div className="max-w-md mx-auto">
              <select
                value={selectedPage}
                onChange={(e) => setSelectedPage(e.target.value)}
                className="input w-full"
              >
                {overview?.top_pages.map((page) => (
                  <option key={page.path} value={page.path}>
                    {page.path}
                  </option>
                ))}
              </select>
            </div>
            <div className="mt-8 p-8 bg-white/5 rounded-xl border border-dashed border-white/20">
              <div className="text-white/40">
                Heatmap visualization for{" "}
                <span className="font-mono text-electric">{selectedPage}</span>
              </div>
              <p className="text-sm text-white/30 mt-2">
                Add the BehaviorMind tracking script to your website to collect click data
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-white/10">
            <h3 className="font-semibold">Session Recordings</h3>
            <p className="text-sm text-white/50">Watch how users interact with your site</p>
          </div>
          {sessions.length === 0 ? (
            <div className="text-center py-12">
              <Play className="w-12 h-12 mx-auto mb-4 text-white/20" />
              <h3 className="text-lg font-medium mb-2">No recordings yet</h3>
              <p className="text-white/50">Sessions will appear here once tracking is enabled</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {sessions.map((session) => {
                const DeviceIcon = getDeviceIcon(session.device_type);
                return (
                  <div
                    key={session.id}
                    className="p-4 hover:bg-white/5 cursor-pointer transition-colors flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center">
                        <DeviceIcon className="w-5 h-5 text-white/60" />
                      </div>
                      <div>
                        <div className="font-medium flex items-center gap-2">
                          <span className="font-mono text-sm">{session.page_path}</span>
                          {session.is_bounce && (
                            <span className="px-2 py-0.5 text-xs bg-red-500/20 text-red-400 rounded">
                              Bounce
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-white/50">
                          {session.browser} • {session.country || "Unknown"} •{" "}
                          {formatDate(session.started_at)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6 text-sm">
                      <div className="text-center">
                        <div className="font-medium">{formatDuration(session.duration_seconds)}</div>
                        <div className="text-white/50 text-xs">Duration</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium">{session.scroll_depth}%</div>
                        <div className="text-white/50 text-xs">Scroll</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium">{session.clicks_count}</div>
                        <div className="text-white/50 text-xs">Clicks</div>
                      </div>
                      <button className="btn-secondary py-2 px-3 text-sm flex items-center gap-1">
                        <Play className="w-4 h-4" />
                        Watch
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

