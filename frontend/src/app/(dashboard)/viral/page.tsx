"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Share2,
  Users,
  Trophy,
  Gift,
  Link2,
  Copy,
  Check,
  Loader2,
  Plus,
  Play,
  ChevronRight,
  Medal,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface ReferralProgram {
  id: string;
  name: string;
  status: string;
  referrer_reward: string;
  referred_reward: string;
  total_referrals: number;
  successful_referrals: number;
  total_rewards_given: number;
}

interface Contest {
  id: string;
  name: string;
  prize_name: string;
  prize_value: number;
  status: string;
  total_entries: number;
  starts_at: string;
  ends_at: string;
}

interface ReferralStats {
  total_referrals: number;
  successful_conversions: number;
  conversion_rate: number;
  total_clicks: number;
  total_rewards_given: number;
  viral_coefficient: number;
}

interface LeaderboardEntry {
  rank: number;
  customer_id: string;
  name: string;
  value: number;
  metric: string;
}

export default function ViralPage() {
  const { organization } = useAuth();
  const [programs, setPrograms] = useState<ReferralProgram[]>([]);
  const [contests, setContests] = useState<Contest[]>([]);
  const [stats, setStats] = useState<ReferralStats | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "referrals" | "contests" | "gamification">("overview");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [programsRes, contestsRes, statsRes, leaderboardRes] = await Promise.all([
        authFetch(`/api/v1/viral/referral/programs?org_id=${organization.id}`),
        authFetch(`/api/v1/viral/contests?org_id=${organization.id}`),
        authFetch(`/api/v1/viral/referral/stats?org_id=${organization.id}`),
        authFetch(`/api/v1/viral/leaderboard?org_id=${organization.id}&metric=referrals`),
      ]);

      if (programsRes.ok) {
        const data = await programsRes.json();
        setPrograms(data.programs || []);
      }
      if (contestsRes.ok) {
        const data = await contestsRes.json();
        setContests(data.contests || []);
      }
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      }
      if (leaderboardRes.ok) {
        const data = await leaderboardRes.json();
        setLeaderboard(data.leaderboard || []);
      }
    } catch (error) {
      console.error("Failed to fetch viral data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const copyLink = () => {
    navigator.clipboard.writeText("https://neurocron.com/ref/EXAMPLE123");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Medal className="w-5 h-5 text-yellow-400" />;
      case 2:
        return <Medal className="w-5 h-5 text-gray-300" />;
      case 3:
        return <Medal className="w-5 h-5 text-amber-600" />;
      default:
        return <span className="w-5 text-center text-white/40">{rank}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center">
              <Share2 className="w-5 h-5 text-white" />
            </div>
            ViralEngine
          </h1>
          <p className="text-white/60 mt-1">
            Referral programs, contests, and gamification
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Program
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {[
          { id: "overview", label: "Overview", icon: TrendingUp },
          { id: "referrals", label: "Referrals", icon: Share2 },
          { id: "contests", label: "Contests", icon: Gift },
          { id: "gamification", label: "Gamification", icon: Trophy },
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
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <Users className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {stats.total_referrals}
                    </div>
                    <div className="text-xs text-white/50">Total Referrals</div>
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
                    <Check className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-400">
                      {stats.conversion_rate}%
                    </div>
                    <div className="text-xs text-white/50">Conversion Rate</div>
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
                  <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {stats.viral_coefficient}x
                    </div>
                    <div className="text-xs text-white/50">Viral Coefficient</div>
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
                  <div className="w-10 h-10 rounded-lg bg-electric/10 flex items-center justify-center">
                    <Gift className="w-5 h-5 text-electric" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {formatCurrency(stats.total_rewards_given)}
                    </div>
                    <div className="text-xs text-white/50">Rewards Given</div>
                  </div>
                </div>
              </motion.div>
            </div>
          )}

          {/* Two Column Layout */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Active Programs */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4">Active Programs</h3>
              {programs.length === 0 ? (
                <div className="text-center py-8">
                  <Share2 className="w-10 h-10 mx-auto mb-3 text-white/20" />
                  <p className="text-white/50 mb-4">No referral programs yet</p>
                  <button className="btn-primary text-sm">Create Program</button>
                </div>
              ) : (
                <div className="space-y-3">
                  {programs.map((program) => (
                    <div
                      key={program.id}
                      className="p-3 bg-white/5 rounded-lg hover:bg-white/10 cursor-pointer transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{program.name}</div>
                          <div className="text-sm text-white/50">
                            {program.referrer_reward} / {program.referred_reward}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-electric">
                            {program.successful_referrals}
                          </div>
                          <div className="text-xs text-white/50">conversions</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Leaderboard */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4">Top Referrers</h3>
              {leaderboard.length === 0 ? (
                <div className="text-center py-8">
                  <Trophy className="w-10 h-10 mx-auto mb-3 text-white/20" />
                  <p className="text-white/50">No referrals yet</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {leaderboard.map((entry) => (
                    <div
                      key={entry.customer_id}
                      className={cn(
                        "flex items-center gap-3 p-3 rounded-lg",
                        entry.rank <= 3 ? "bg-white/5" : "bg-transparent"
                      )}
                    >
                      {getRankIcon(entry.rank)}
                      <div className="flex-1">
                        <div className="font-medium">{entry.name}</div>
                      </div>
                      <div className="text-right">
                        <span className="text-lg font-bold">{entry.value}</span>
                        <span className="text-white/50 text-sm ml-1">referrals</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      ) : activeTab === "referrals" ? (
        <div className="space-y-6">
          {/* Quick Share */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Share Your Referral Link</h3>
            <div className="flex gap-2">
              <div className="flex-1 flex items-center gap-3 px-4 py-3 bg-white/5 rounded-lg border border-white/10">
                <Link2 className="w-5 h-5 text-white/40" />
                <span className="text-white/60 font-mono text-sm">
                  https://neurocron.com/ref/EXAMPLE123
                </span>
              </div>
              <button
                onClick={copyLink}
                className="btn-primary flex items-center gap-2"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
          </div>

          {/* Programs List */}
          <div className="card">
            <div className="p-4 border-b border-white/10 flex justify-between items-center">
              <h3 className="font-semibold">Referral Programs</h3>
              <button className="btn-secondary text-sm py-2">
                <Plus className="w-4 h-4 mr-1" />
                New Program
              </button>
            </div>
            {programs.length === 0 ? (
              <div className="text-center py-12">
                <Share2 className="w-12 h-12 mx-auto mb-4 text-white/20" />
                <h3 className="text-lg font-medium mb-2">No referral programs</h3>
                <p className="text-white/50 mb-4">Create your first referral program to start growing virally</p>
                <button className="btn-primary">Create Program</button>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {programs.map((program) => (
                  <div key={program.id} className="p-4 hover:bg-white/5 transition-colors">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium flex items-center gap-2">
                          {program.name}
                          <span className={cn(
                            "px-2 py-0.5 text-xs rounded",
                            program.status === "active"
                              ? "bg-green-500/20 text-green-400"
                              : "bg-white/10 text-white/50"
                          )}>
                            {program.status}
                          </span>
                        </div>
                        <div className="text-sm text-white/50 mt-1">
                          Referrer gets {program.referrer_reward} • New user gets {program.referred_reward}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-center">
                          <div className="text-lg font-bold">{program.total_referrals}</div>
                          <div className="text-xs text-white/50">Total</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold text-green-400">{program.successful_referrals}</div>
                          <div className="text-xs text-white/50">Converted</div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-white/30" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : activeTab === "contests" ? (
        <div className="space-y-6">
          <div className="flex justify-end">
            <button className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Contest
            </button>
          </div>
          
          {contests.length === 0 ? (
            <div className="card p-6 text-center">
              <Gift className="w-12 h-12 mx-auto mb-4 text-white/20" />
              <h3 className="text-lg font-medium mb-2">No contests yet</h3>
              <p className="text-white/50 mb-4">Create a contest or giveaway to boost engagement</p>
              <button className="btn-primary">Create Contest</button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-4">
              {contests.map((contest) => (
                <div key={contest.id} className="card p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold">{contest.name}</h3>
                      <p className="text-sm text-white/50">{contest.prize_name}</p>
                    </div>
                    <span className={cn(
                      "px-2 py-1 text-xs rounded",
                      contest.status === "active"
                        ? "bg-green-500/20 text-green-400"
                        : "bg-white/10 text-white/50"
                    )}>
                      {contest.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <div className="text-2xl font-bold">{contest.total_entries}</div>
                      <div className="text-xs text-white/50">Entries</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{formatCurrency(contest.prize_value)}</div>
                      <div className="text-xs text-white/50">Prize Value</div>
                    </div>
                  </div>
                  <button className="btn-secondary w-full">View Details</button>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-6">
          <div className="card p-6 text-center">
            <Trophy className="w-12 h-12 mx-auto mb-4 text-yellow-400" />
            <h3 className="text-xl font-bold mb-2">Leaderboards</h3>
            <p className="text-white/50 mb-4">Create competitive rankings to drive engagement</p>
            <button className="btn-primary">Configure</button>
          </div>
          <div className="card p-6 text-center">
            <Medal className="w-12 h-12 mx-auto mb-4 text-purple-400" />
            <h3 className="text-xl font-bold mb-2">Badges</h3>
            <p className="text-white/50 mb-4">Award achievements for milestones and actions</p>
            <button className="btn-secondary">Set Up Badges</button>
          </div>
          <div className="card p-6 text-center">
            <Sparkles className="w-12 h-12 mx-auto mb-4 text-electric" />
            <h3 className="text-xl font-bold mb-2">Points System</h3>
            <p className="text-white/50 mb-4">Reward users with points for every action</p>
            <button className="btn-secondary">Configure Points</button>
          </div>
        </div>
      )}
    </div>
  );
}

