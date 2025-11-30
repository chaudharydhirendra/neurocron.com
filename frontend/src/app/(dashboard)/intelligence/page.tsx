"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Swords,
  TrendingUp,
  Shield,
  Loader2,
  Plus,
  ExternalLink,
  AlertTriangle,
  Eye,
  Target,
  Zap,
  ThumbsUp,
  ThumbsDown,
  Minus,
  MessageSquare,
  Activity,
  Globe,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Competitor {
  id: string;
  name: string;
  website: string;
  description?: string;
  health_score: number;
  threat_level: string;
  metrics: {
    website_traffic: string;
    social_followers: string;
    domain_authority: number;
    ad_spend_estimate: string;
  };
}

interface Insight {
  id: string;
  competitor_name: string;
  type: string;
  title: string;
  description: string;
  detected_at: string;
  impact: string;
  action_recommended?: string;
}

interface Trend {
  id: string;
  topic: string;
  category: string;
  velocity: string;
  growth_24h: number;
  volume: number;
  sentiment: string;
  relevance_score: number;
  opportunity: string;
}

interface BrandHealth {
  health_score: number;
  metrics: {
    sentiment_score: number;
    share_of_voice: number;
    brand_mentions_24h: number;
    positive_mentions: number;
    neutral_mentions: number;
    negative_mentions: number;
  };
}

export default function IntelligencePage() {
  const { organization } = useAuth();
  const [activeTab, setActiveTab] = useState<"competitors" | "trends" | "brand">("competitors");
  
  // BattleStation state
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [isLoadingCompetitors, setIsLoadingCompetitors] = useState(true);
  
  // TrendRadar state
  const [trends, setTrends] = useState<Trend[]>([]);
  const [isLoadingTrends, setIsLoadingTrends] = useState(true);
  
  // CrisisShield state
  const [brandHealth, setBrandHealth] = useState<BrandHealth | null>(null);
  const [isLoadingBrand, setIsLoadingBrand] = useState(true);

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization, activeTab]);

  const fetchData = async () => {
    if (!organization) return;
    
    if (activeTab === "competitors") {
      setIsLoadingCompetitors(true);
      try {
        const [compRes, insightRes] = await Promise.all([
          authFetch(`/api/v1/intelligence/competitors?org_id=${organization.id}`),
          authFetch(`/api/v1/intelligence/competitors/insights?org_id=${organization.id}`),
        ]);
        
        if (compRes.ok) {
          const data = await compRes.json();
          setCompetitors(data.competitors || []);
        }
        if (insightRes.ok) {
          const data = await insightRes.json();
          setInsights(data.insights || []);
        }
      } catch (error) {
        console.error("Failed to fetch competitors:", error);
      } finally {
        setIsLoadingCompetitors(false);
      }
    } else if (activeTab === "trends") {
      setIsLoadingTrends(true);
      try {
        const response = await authFetch(`/api/v1/intelligence/trends?org_id=${organization.id}`);
        if (response.ok) {
          const data = await response.json();
          setTrends(data.trends || []);
        }
      } catch (error) {
        console.error("Failed to fetch trends:", error);
      } finally {
        setIsLoadingTrends(false);
      }
    } else if (activeTab === "brand") {
      setIsLoadingBrand(true);
      try {
        const response = await authFetch(`/api/v1/intelligence/brand/health?org_id=${organization.id}`);
        if (response.ok) {
          const data = await response.json();
          setBrandHealth(data);
        }
      } catch (error) {
        console.error("Failed to fetch brand health:", error);
      } finally {
        setIsLoadingBrand(false);
      }
    }
  };

  const getThreatColor = (level: string) => {
    switch (level) {
      case "high": return "text-red-400 bg-red-400/10";
      case "medium": return "text-yellow-400 bg-yellow-400/10";
      case "low": return "text-green-400 bg-green-400/10";
      default: return "text-white/40 bg-white/5";
    }
  };

  const getVelocityColor = (velocity: string) => {
    switch (velocity) {
      case "viral": return "text-pink-400 bg-pink-400/10";
      case "rising": return "text-green-400 bg-green-400/10";
      case "stable": return "text-yellow-400 bg-yellow-400/10";
      case "declining": return "text-red-400 bg-red-400/10";
      default: return "text-white/40 bg-white/5";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center">
            <Eye className="w-5 h-5 text-red-400" />
          </div>
          Market Intelligence
        </h1>
        <p className="text-white/60 mt-1">
          Competitive tracking, trend monitoring, and brand protection
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("competitors")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "competitors"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <Swords className="w-4 h-4" />
          BattleStation
        </button>
        <button
          onClick={() => setActiveTab("trends")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "trends"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <TrendingUp className="w-4 h-4" />
          TrendRadar
        </button>
        <button
          onClick={() => setActiveTab("brand")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "brand"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <Shield className="w-4 h-4" />
          CrisisShield
        </button>
      </div>

      {activeTab === "competitors" ? (
        <div className="space-y-6">
          {isLoadingCompetitors ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : (
            <>
              {/* Competitors Grid */}
              <div className="grid md:grid-cols-3 gap-4">
                {competitors.map((comp, index) => (
                  <motion.div
                    key={comp.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="card"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-semibold">{comp.name}</h3>
                        <a href={comp.website} target="_blank" rel="noopener noreferrer" 
                           className="text-sm text-white/50 hover:text-electric flex items-center gap-1">
                          {comp.website.replace("https://", "")}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                      <span className={cn("px-2 py-1 rounded-lg text-xs uppercase", getThreatColor(comp.threat_level))}>
                        {comp.threat_level}
                      </span>
                    </div>

                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-white/60">Health Score</span>
                        <span className="font-medium">{comp.health_score}/100</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className={cn(
                            "h-full rounded-full",
                            comp.health_score >= 80 ? "bg-green-400" :
                            comp.health_score >= 60 ? "bg-yellow-400" : "bg-red-400"
                          )}
                          style={{ width: `${comp.health_score}%` }}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <div className="text-white/40">Traffic</div>
                        <div className="font-medium">{comp.metrics.website_traffic}</div>
                      </div>
                      <div>
                        <div className="text-white/40">Social</div>
                        <div className="font-medium">{comp.metrics.social_followers}</div>
                      </div>
                      <div>
                        <div className="text-white/40">Domain Auth</div>
                        <div className="font-medium">{comp.metrics.domain_authority}</div>
                      </div>
                      <div>
                        <div className="text-white/40">Ad Spend</div>
                        <div className="font-medium">{comp.metrics.ad_spend_estimate}</div>
                      </div>
                    </div>
                  </motion.div>
                ))}
                
                <motion.button
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card border-dashed flex items-center justify-center min-h-[200px] hover:border-electric/50 transition-colors"
                >
                  <div className="text-center">
                    <Plus className="w-8 h-8 text-white/20 mx-auto mb-2" />
                    <span className="text-white/50">Add Competitor</span>
                  </div>
                </motion.button>
              </div>

              {/* Insights */}
              <div>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-400" />
                  Latest Intelligence
                </h2>
                <div className="space-y-3">
                  {insights.map((insight, index) => (
                    <motion.div
                      key={insight.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={cn(
                        "card p-4 border-l-4",
                        insight.impact === "negative" ? "border-l-red-400" :
                        insight.impact === "positive" ? "border-l-green-400" : "border-l-yellow-400"
                      )}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs px-2 py-0.5 rounded-lg bg-white/5 capitalize">
                              {insight.type.replace("_", " ")}
                            </span>
                            <span className="text-xs text-white/40">{insight.competitor_name}</span>
                          </div>
                          <h3 className="font-medium mb-1">{insight.title}</h3>
                          <p className="text-sm text-white/60">{insight.description}</p>
                          {insight.action_recommended && (
                            <div className="mt-2 p-2 rounded-lg bg-electric/5 border border-electric/20 text-sm">
                              <span className="text-electric font-medium">Recommended: </span>
                              {insight.action_recommended}
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      ) : activeTab === "trends" ? (
        <div className="space-y-4">
          {isLoadingTrends ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : (
            trends.map((trend, index) => (
              <motion.div
                key={trend.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="card"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-lg">{trend.topic}</h3>
                      <span className={cn("px-2 py-0.5 rounded-lg text-xs capitalize", getVelocityColor(trend.velocity))}>
                        {trend.velocity}
                      </span>
                    </div>
                    <span className="text-sm text-white/50 capitalize">{trend.category}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-electric">{trend.relevance_score}%</div>
                    <div className="text-xs text-white/40">Relevance</div>
                  </div>
                </div>

                <div className="grid md:grid-cols-4 gap-4 mb-4">
                  <div className="p-3 rounded-lg bg-white/5">
                    <div className="text-xs text-white/40 mb-1">24h Growth</div>
                    <div className={cn(
                      "font-semibold",
                      trend.growth_24h > 0 ? "text-green-400" : "text-red-400"
                    )}>
                      {trend.growth_24h > 0 ? "+" : ""}{trend.growth_24h}%
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-white/5">
                    <div className="text-xs text-white/40 mb-1">Volume</div>
                    <div className="font-semibold">{(trend.volume / 1000).toFixed(0)}K</div>
                  </div>
                  <div className="p-3 rounded-lg bg-white/5">
                    <div className="text-xs text-white/40 mb-1">Sentiment</div>
                    <div className="flex items-center gap-1 capitalize">
                      {trend.sentiment === "positive" ? <ThumbsUp className="w-4 h-4 text-green-400" /> :
                       trend.sentiment === "negative" ? <ThumbsDown className="w-4 h-4 text-red-400" /> :
                       <Minus className="w-4 h-4 text-yellow-400" />}
                      {trend.sentiment}
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-electric/5 border border-electric/20">
                    <div className="text-xs text-electric mb-1">Opportunity</div>
                    <div className="text-sm">{trend.opportunity}</div>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {isLoadingBrand ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : brandHealth && (
            <>
              {/* Health Score Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card bg-gradient-to-br from-green-500/10 to-transparent"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold mb-2">Brand Health Score</h2>
                    <p className="text-white/60">Your brand reputation is strong</p>
                  </div>
                  <div className="text-right">
                    <div className="text-5xl font-bold text-green-400">{brandHealth.health_score}</div>
                    <div className="text-sm text-white/50">/100</div>
                  </div>
                </div>
              </motion.div>

              {/* Metrics Grid */}
              <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="card text-center"
                >
                  <div className="text-3xl font-bold">{brandHealth.metrics.sentiment_score}</div>
                  <div className="text-sm text-white/50">Sentiment Score</div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15 }}
                  className="card text-center"
                >
                  <div className="text-3xl font-bold">{brandHealth.metrics.share_of_voice}%</div>
                  <div className="text-sm text-white/50">Share of Voice</div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="card text-center"
                >
                  <div className="text-3xl font-bold">{brandHealth.metrics.brand_mentions_24h}</div>
                  <div className="text-sm text-white/50">Mentions (24h)</div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.25 }}
                  className="card text-center"
                >
                  <div className="text-3xl font-bold text-green-400">{brandHealth.metrics.positive_mentions}</div>
                  <div className="text-sm text-white/50">Positive</div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="card text-center"
                >
                  <div className="text-3xl font-bold text-yellow-400">{brandHealth.metrics.neutral_mentions}</div>
                  <div className="text-sm text-white/50">Neutral</div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.35 }}
                  className="card text-center"
                >
                  <div className="text-3xl font-bold text-red-400">{brandHealth.metrics.negative_mentions}</div>
                  <div className="text-sm text-white/50">Negative</div>
                </motion.div>
              </div>

              {/* Status Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="card"
              >
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-green-400" />
                  Crisis Status
                </h3>
                <div className="p-4 rounded-xl bg-green-400/5 border border-green-400/20 text-center">
                  <div className="text-green-400 font-medium mb-1">All Clear</div>
                  <div className="text-sm text-white/50">No active crises detected. Brand protection is active.</div>
                </div>
              </motion.div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

