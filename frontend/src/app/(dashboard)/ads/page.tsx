"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Target,
  Sparkles,
  Loader2,
  TrendingUp,
  DollarSign,
  MousePointer,
  Eye,
  Zap,
  AlertCircle,
  ChevronRight,
  Play,
  Pause,
  BarChart3,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface AdVariant {
  id: string;
  headline: string;
  description: string;
  cta: string;
  predicted_ctr: number;
  predicted_conversion_rate: number;
  confidence_score: number;
}

interface Campaign {
  id: string;
  name: string;
  platform: string;
  status: string;
  budget: number;
  spent: number;
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number;
  roas: number;
}

interface Suggestion {
  id: string;
  type: string;
  priority: string;
  campaign: string;
  title: string;
  description: string;
  estimated_impact: string;
}

export default function AdsPage() {
  const { organization } = useAuth();
  const [activeTab, setActiveTab] = useState<"campaigns" | "generate" | "optimize">("campaigns");
  
  // Campaigns state
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoadingCampaigns, setIsLoadingCampaigns] = useState(true);
  
  // Generate state
  const [productName, setProductName] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [platform, setPlatform] = useState("google");
  const [adType, setAdType] = useState("search");
  const [goal, setGoal] = useState("conversion");
  const [isGenerating, setIsGenerating] = useState(false);
  const [variants, setVariants] = useState<AdVariant[]>([]);
  
  // Optimization state
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);

  useEffect(() => {
    if (organization) {
      fetchCampaigns();
    }
  }, [organization]);

  const fetchCampaigns = async () => {
    if (!organization) return;
    setIsLoadingCampaigns(true);
    try {
      const response = await authFetch(`/api/v1/ads/campaigns?org_id=${organization.id}`);
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data.campaigns || []);
      }
    } catch (error) {
      console.error("Failed to fetch campaigns:", error);
    } finally {
      setIsLoadingCampaigns(false);
    }
  };

  const fetchSuggestions = async () => {
    if (!organization) return;
    setIsLoadingSuggestions(true);
    try {
      const response = await authFetch(`/api/v1/ads/optimization-suggestions?org_id=${organization.id}`);
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error("Failed to fetch suggestions:", error);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  const handleGenerate = async () => {
    if (!organization || !productName || !productDescription || !targetAudience) return;
    
    setIsGenerating(true);
    try {
      const response = await authFetch(
        `/api/v1/ads/generate?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            product_name: productName,
            product_description: productDescription,
            target_audience: targetAudience,
            platform,
            ad_type: adType,
            goal,
            count: 3,
          }),
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setVariants(data.variants);
      }
    } catch (error) {
      console.error("Failed to generate ads:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (activeTab === "optimize" && organization) {
      fetchSuggestions();
    }
  }, [activeTab, organization]);

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case "google": return "text-blue-400 bg-blue-400/10";
      case "meta": return "text-indigo-400 bg-indigo-400/10";
      case "linkedin": return "text-cyan-400 bg-cyan-400/10";
      case "tiktok": return "text-pink-400 bg-pink-400/10";
      default: return "text-white/60 bg-white/5";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "text-green-400 bg-green-400/10";
      case "paused": return "text-yellow-400 bg-yellow-400/10";
      case "ended": return "text-white/40 bg-white/5";
      default: return "text-white/40 bg-white/5";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
            <Target className="w-5 h-5 text-blue-400" />
          </div>
          AdPilot
        </h1>
        <p className="text-white/60 mt-1">
          AI-powered ad creation and optimization
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("campaigns")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "campaigns"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <BarChart3 className="w-4 h-4" />
          Campaigns
        </button>
        <button
          onClick={() => setActiveTab("generate")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "generate"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <Sparkles className="w-4 h-4" />
          Generate Ads
        </button>
        <button
          onClick={() => setActiveTab("optimize")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "optimize"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <Zap className="w-4 h-4" />
          Optimize
        </button>
      </div>

      {activeTab === "campaigns" ? (
        <div className="space-y-4">
          {isLoadingCampaigns ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : campaigns.length === 0 ? (
            <div className="card text-center py-12">
              <Target className="w-12 h-12 text-white/20 mx-auto mb-4" />
              <h3 className="font-medium mb-2">No campaigns yet</h3>
              <p className="text-sm text-white/50 mb-4">
                Generate and launch your first ad campaign
              </p>
              <button
                onClick={() => setActiveTab("generate")}
                className="btn-primary"
              >
                Generate Ads
              </button>
            </div>
          ) : (
            <>
              {/* Summary Cards */}
              <div className="grid md:grid-cols-4 gap-4">
                <div className="card bg-gradient-to-br from-blue-500/10 to-transparent">
                  <div className="text-sm text-white/60 mb-1">Total Spend</div>
                  <div className="text-2xl font-bold">$5,730.75</div>
                </div>
                <div className="card bg-gradient-to-br from-green-500/10 to-transparent">
                  <div className="text-sm text-white/60 mb-1">Conversions</div>
                  <div className="text-2xl font-bold">196</div>
                </div>
                <div className="card bg-gradient-to-br from-purple-500/10 to-transparent">
                  <div className="text-sm text-white/60 mb-1">Avg ROAS</div>
                  <div className="text-2xl font-bold">4.03x</div>
                </div>
                <div className="card bg-gradient-to-br from-yellow-500/10 to-transparent">
                  <div className="text-sm text-white/60 mb-1">Active Campaigns</div>
                  <div className="text-2xl font-bold">{campaigns.filter(c => c.status === "active").length}</div>
                </div>
              </div>

              {/* Campaign List */}
              {campaigns.map((campaign, index) => (
                <motion.div
                  key={campaign.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="card"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={cn("px-2 py-1 rounded-lg text-xs uppercase", getPlatformColor(campaign.platform))}>
                        {campaign.platform}
                      </div>
                      <h3 className="font-semibold">{campaign.name}</h3>
                      <div className={cn("px-2 py-0.5 rounded-full text-xs capitalize", getStatusColor(campaign.status))}>
                        {campaign.status}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {campaign.status === "active" ? (
                        <button className="p-2 rounded-lg hover:bg-yellow-400/10 transition-colors">
                          <Pause className="w-4 h-4 text-yellow-400" />
                        </button>
                      ) : (
                        <button className="p-2 rounded-lg hover:bg-green-400/10 transition-colors">
                          <Play className="w-4 h-4 text-green-400" />
                        </button>
                      )}
                      <button className="btn-secondary text-sm py-2">
                        Edit
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                    <div>
                      <div className="text-xs text-white/40 mb-1 flex items-center gap-1">
                        <DollarSign className="w-3 h-3" />
                        Spent / Budget
                      </div>
                      <div className="font-medium">
                        ${campaign.spent.toLocaleString()} / ${campaign.budget.toLocaleString()}
                      </div>
                      <div className="mt-1 h-1 bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-electric rounded-full"
                          style={{ width: `${(campaign.spent / campaign.budget) * 100}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-white/40 mb-1 flex items-center gap-1">
                        <Eye className="w-3 h-3" />
                        Impressions
                      </div>
                      <div className="font-medium">{campaign.impressions.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-xs text-white/40 mb-1 flex items-center gap-1">
                        <MousePointer className="w-3 h-3" />
                        Clicks
                      </div>
                      <div className="font-medium">{campaign.clicks.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-xs text-white/40 mb-1">CTR</div>
                      <div className="font-medium">{campaign.ctr}%</div>
                    </div>
                    <div>
                      <div className="text-xs text-white/40 mb-1 flex items-center gap-1">
                        <Target className="w-3 h-3" />
                        Conversions
                      </div>
                      <div className="font-medium">{campaign.conversions}</div>
                    </div>
                    <div>
                      <div className="text-xs text-white/40 mb-1 flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        ROAS
                      </div>
                      <div className={cn(
                        "font-medium",
                        campaign.roas >= 3 ? "text-green-400" : campaign.roas >= 2 ? "text-yellow-400" : "text-red-400"
                      )}>
                        {campaign.roas}x
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </>
          )}
        </div>
      ) : activeTab === "generate" ? (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="lg:col-span-1">
            <div className="card sticky top-24">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-electric" />
                Generate Ads
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-2">Product Name *</label>
                  <input
                    type="text"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    className="input"
                    placeholder="Your product name"
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Description *</label>
                  <textarea
                    value={productDescription}
                    onChange={(e) => setProductDescription(e.target.value)}
                    className="input min-h-[80px] resize-none"
                    placeholder="What does your product do?"
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Target Audience *</label>
                  <input
                    type="text"
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                    className="input"
                    placeholder="e.g., Marketing managers at startups"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-white/60 mb-2">Platform</label>
                    <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="input">
                      <option value="google">Google Ads</option>
                      <option value="meta">Meta Ads</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="tiktok">TikTok</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-white/60 mb-2">Ad Type</label>
                    <select value={adType} onChange={(e) => setAdType(e.target.value)} className="input">
                      <option value="search">Search</option>
                      <option value="display">Display</option>
                      <option value="video">Video</option>
                      <option value="carousel">Carousel</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Goal</label>
                  <select value={goal} onChange={(e) => setGoal(e.target.value)} className="input">
                    <option value="awareness">Brand Awareness</option>
                    <option value="consideration">Consideration</option>
                    <option value="conversion">Conversion</option>
                  </select>
                </div>

                <button
                  onClick={handleGenerate}
                  disabled={isGenerating || !productName || !productDescription || !targetAudience}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Ads
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2 space-y-4">
            {variants.length === 0 ? (
              <div className="card text-center py-12">
                <Target className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <h3 className="font-medium mb-2">No ads generated yet</h3>
                <p className="text-sm text-white/50">
                  Fill in your product details to generate AI-powered ad variants
                </p>
              </div>
            ) : (
              variants.map((variant, index) => (
                <motion.div
                  key={variant.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="font-medium text-lg">Variant {index + 1}</div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-2 py-1 rounded-lg bg-green-400/10 text-green-400">
                        {(variant.confidence_score * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-white/5 mb-4">
                    <div className="text-electric font-medium text-lg mb-2">{variant.headline}</div>
                    <div className="text-white/70 mb-3">{variant.description}</div>
                    <button className="px-4 py-2 rounded-lg bg-electric text-midnight font-medium">
                      {variant.cta}
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded-lg bg-white/5">
                      <div className="text-xs text-white/40 mb-1">Predicted CTR</div>
                      <div className="text-xl font-bold text-electric">{variant.predicted_ctr}%</div>
                    </div>
                    <div className="p-3 rounded-lg bg-white/5">
                      <div className="text-xs text-white/40 mb-1">Predicted Conv. Rate</div>
                      <div className="text-xl font-bold text-green-400">{variant.predicted_conversion_rate}%</div>
                    </div>
                  </div>

                  <div className="flex gap-2 mt-4">
                    <button className="btn-primary flex-1">Use This Variant</button>
                    <button className="btn-secondary">Edit</button>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>
      ) : (
        /* Optimize Tab */
        <div className="space-y-4">
          {isLoadingSuggestions ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : suggestions.length === 0 ? (
            <div className="card text-center py-12">
              <Zap className="w-12 h-12 text-white/20 mx-auto mb-4" />
              <h3 className="font-medium mb-2">No suggestions available</h3>
              <p className="text-sm text-white/50">
                Run campaigns to get AI-powered optimization recommendations
              </p>
            </div>
          ) : (
            suggestions.map((suggestion, index) => (
              <motion.div
                key={suggestion.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={cn(
                  "card border-l-4",
                  suggestion.priority === "high" ? "border-l-red-400" : 
                  suggestion.priority === "medium" ? "border-l-yellow-400" : "border-l-blue-400"
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={cn(
                        "text-xs px-2 py-0.5 rounded-full uppercase",
                        suggestion.priority === "high" ? "bg-red-400/10 text-red-400" :
                        suggestion.priority === "medium" ? "bg-yellow-400/10 text-yellow-400" :
                        "bg-blue-400/10 text-blue-400"
                      )}>
                        {suggestion.priority}
                      </span>
                      <span className="text-xs text-white/40">{suggestion.campaign}</span>
                    </div>
                    <h3 className="font-semibold mb-1">{suggestion.title}</h3>
                    <p className="text-sm text-white/60 mb-3">{suggestion.description}</p>
                    <div className="flex items-center gap-2 text-sm">
                      <TrendingUp className="w-4 h-4 text-green-400" />
                      <span className="text-green-400">{suggestion.estimated_impact}</span>
                    </div>
                  </div>
                  <button className="btn-primary text-sm py-2 whitespace-nowrap">
                    Apply
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

