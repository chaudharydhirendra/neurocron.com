"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  Sparkles,
  Loader2,
  Target,
  Calendar,
  DollarSign,
  TrendingUp,
  Shield,
  ChevronRight,
  Check,
  Lightbulb,
  Zap,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface QuarterlyPlan {
  quarter: string;
  theme: string;
  objectives: string[];
  key_initiatives: string[];
  budget_allocation: Record<string, number>;
  kpis: string[];
}

interface ChannelStrategy {
  channel: string;
  priority: string;
  tactics: string[];
  budget_percentage: number;
  expected_outcomes: string[];
}

interface Strategy {
  id: string;
  executive_summary: string;
  vision: string;
  mission: string;
  quarterly_plans: QuarterlyPlan[];
  channel_strategies: ChannelStrategy[];
  unique_selling_propositions: string[];
  success_metrics: string[];
  total_budget_estimate: string;
}

export default function StrategyPage() {
  const { organization } = useAuth();
  const [activeTab, setActiveTab] = useState<"neuroplan" | "brainspark">("neuroplan");
  
  // NeuroPlan state
  const [businessName, setBusinessName] = useState("");
  const [businessDescription, setBusinessDescription] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [goals, setGoals] = useState("");
  const [budgetRange, setBudgetRange] = useState("medium");
  const [timeline, setTimeline] = useState(12);
  const [isGenerating, setIsGenerating] = useState(false);
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  
  // BrainSpark state
  const [campaignGoal, setCampaignGoal] = useState("");
  const [ideaAudience, setIdeaAudience] = useState("");
  const [brandTone, setBrandTone] = useState("professional");
  const [channels, setChannels] = useState<string[]>([]);
  const [ideaCount, setIdeaCount] = useState(5);
  const [isGeneratingIdeas, setIsGeneratingIdeas] = useState(false);
  const [ideas, setIdeas] = useState<any[]>([]);

  const handleGenerateStrategy = async () => {
    if (!organization || !businessName || !businessDescription || !targetAudience || !goals) return;
    
    setIsGenerating(true);
    try {
      const response = await authFetch(
        `/api/v1/strategy/neuroplan/generate?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            business_name: businessName,
            business_description: businessDescription,
            target_audience: targetAudience,
            goals: goals.split(",").map(g => g.trim()),
            budget_range: budgetRange,
            timeline_months: timeline,
          }),
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setStrategy(data);
      }
    } catch (error) {
      console.error("Failed to generate strategy:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateIdeas = async () => {
    if (!organization || !campaignGoal || !ideaAudience) return;
    
    setIsGeneratingIdeas(true);
    try {
      const response = await authFetch(
        `/api/v1/strategy/brainspark/generate?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            campaign_goal: campaignGoal,
            target_audience: ideaAudience,
            brand_tone: brandTone,
            channels: channels.length > 0 ? channels : ["social", "email", "ads"],
            count: ideaCount,
          }),
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setIdeas(data.ideas);
      }
    } catch (error) {
      console.error("Failed to generate ideas:", error);
    } finally {
      setIsGeneratingIdeas(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center">
            <Brain className="w-5 h-5 text-indigo-400" />
          </div>
          Strategy & Ideas
        </h1>
        <p className="text-white/60 mt-1">
          AI-powered strategy generation and creative ideation
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("neuroplan")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "neuroplan"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <Target className="w-4 h-4" />
          NeuroPlan
        </button>
        <button
          onClick={() => setActiveTab("brainspark")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "brainspark"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <Lightbulb className="w-4 h-4" />
          BrainSpark
        </button>
      </div>

      {activeTab === "neuroplan" ? (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="lg:col-span-1">
            <div className="card sticky top-24">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-electric" />
                Generate Strategy
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-2">Business Name *</label>
                  <input
                    type="text"
                    value={businessName}
                    onChange={(e) => setBusinessName(e.target.value)}
                    className="input"
                    placeholder="Your company name"
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Description *</label>
                  <textarea
                    value={businessDescription}
                    onChange={(e) => setBusinessDescription(e.target.value)}
                    className="input min-h-[80px] resize-none"
                    placeholder="What does your business do?"
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Target Audience *</label>
                  <textarea
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                    className="input min-h-[60px] resize-none"
                    placeholder="Who are your ideal customers?"
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Goals (comma-separated) *</label>
                  <input
                    type="text"
                    value={goals}
                    onChange={(e) => setGoals(e.target.value)}
                    className="input"
                    placeholder="Increase leads, Build awareness..."
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Budget Range</label>
                  <select
                    value={budgetRange}
                    onChange={(e) => setBudgetRange(e.target.value)}
                    className="input"
                  >
                    <option value="low">Low ($5k-$50k/year)</option>
                    <option value="medium">Medium ($50k-$200k/year)</option>
                    <option value="high">High ($200k+/year)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    Timeline: {timeline} months
                  </label>
                  <input
                    type="range"
                    min="6"
                    max="24"
                    value={timeline}
                    onChange={(e) => setTimeline(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <button
                  onClick={handleGenerateStrategy}
                  disabled={isGenerating || !businessName || !businessDescription || !targetAudience || !goals}
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
                      Generate Strategy
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2 space-y-6">
            {!strategy ? (
              <div className="card text-center py-12">
                <Brain className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <h3 className="font-medium mb-2">No strategy yet</h3>
                <p className="text-sm text-white/50">
                  Fill in your business details to generate a comprehensive marketing strategy
                </p>
              </div>
            ) : (
              <>
                {/* Executive Summary */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card"
                >
                  <h2 className="text-xl font-bold mb-4">Executive Summary</h2>
                  <p className="text-white/70">{strategy.executive_summary}</p>
                  
                  <div className="mt-4 p-4 rounded-xl bg-electric/5 border border-electric/20">
                    <div className="font-medium text-electric mb-2">Recommended Budget</div>
                    <div className="text-lg">{strategy.total_budget_estimate}</div>
                  </div>
                </motion.div>

                {/* USPs */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="card"
                >
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    Unique Selling Propositions
                  </h3>
                  <div className="grid md:grid-cols-2 gap-3">
                    {strategy.unique_selling_propositions.map((usp, i) => (
                      <div key={i} className="flex items-start gap-2 p-3 rounded-lg bg-white/5">
                        <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{usp}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* Quarterly Plans */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="card"
                >
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-purple-400" />
                    Quarterly Roadmap
                  </h3>
                  <div className="space-y-4">
                    {strategy.quarterly_plans.map((quarter, i) => (
                      <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/10">
                        <div className="flex items-center justify-between mb-3">
                          <div className="font-medium">{quarter.quarter}: {quarter.theme}</div>
                        </div>
                        <div className="grid md:grid-cols-2 gap-4">
                          <div>
                            <div className="text-xs text-white/40 mb-2">Key Initiatives</div>
                            <ul className="space-y-1">
                              {quarter.key_initiatives.slice(0, 3).map((init, j) => (
                                <li key={j} className="text-sm text-white/70 flex items-center gap-2">
                                  <ChevronRight className="w-3 h-3" />
                                  {init}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <div className="text-xs text-white/40 mb-2">KPIs</div>
                            <ul className="space-y-1">
                              {quarter.kpis.map((kpi, j) => (
                                <li key={j} className="text-sm text-white/70 flex items-center gap-2">
                                  <Target className="w-3 h-3 text-electric" />
                                  {kpi}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* Channel Strategies */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="card"
                >
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-400" />
                    Channel Strategy
                  </h3>
                  <div className="space-y-3">
                    {strategy.channel_strategies.map((channel, i) => (
                      <div key={i} className="p-4 rounded-xl bg-white/5">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-medium">{channel.channel}</div>
                          <div className="flex items-center gap-2">
                            <span className={cn(
                              "px-2 py-0.5 rounded-full text-xs capitalize",
                              channel.priority === "high" 
                                ? "bg-green-400/10 text-green-400"
                                : "bg-yellow-400/10 text-yellow-400"
                            )}>
                              {channel.priority}
                            </span>
                            <span className="text-sm text-electric">
                              {channel.budget_percentage}% budget
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {channel.tactics.map((tactic, j) => (
                            <span key={j} className="px-2 py-1 rounded-lg bg-white/5 text-xs text-white/60">
                              {tactic}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </>
            )}
          </div>
        </div>
      ) : (
        /* BrainSpark Tab */
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="lg:col-span-1">
            <div className="card sticky top-24">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-400" />
                Generate Ideas
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-2">Campaign Goal *</label>
                  <input
                    type="text"
                    value={campaignGoal}
                    onChange={(e) => setCampaignGoal(e.target.value)}
                    className="input"
                    placeholder="e.g., Increase sign-ups by 50%"
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Target Audience *</label>
                  <input
                    type="text"
                    value={ideaAudience}
                    onChange={(e) => setIdeaAudience(e.target.value)}
                    className="input"
                    placeholder="e.g., Marketing managers at startups"
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">Brand Tone</label>
                  <select
                    value={brandTone}
                    onChange={(e) => setBrandTone(e.target.value)}
                    className="input"
                  >
                    <option value="professional">Professional</option>
                    <option value="playful">Playful</option>
                    <option value="bold">Bold</option>
                    <option value="elegant">Elegant</option>
                    <option value="friendly">Friendly</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    Ideas to Generate: {ideaCount}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={ideaCount}
                    onChange={(e) => setIdeaCount(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <button
                  onClick={handleGenerateIdeas}
                  disabled={isGeneratingIdeas || !campaignGoal || !ideaAudience}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {isGeneratingIdeas ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Ideas
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2 space-y-4">
            {ideas.length === 0 ? (
              <div className="card text-center py-12">
                <Lightbulb className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <h3 className="font-medium mb-2">No ideas yet</h3>
                <p className="text-sm text-white/50">
                  Describe your campaign goal to generate creative marketing ideas
                </p>
              </div>
            ) : (
              ideas.map((idea, index) => (
                <motion.div
                  key={idea.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <span className={cn(
                        "text-xs px-2 py-0.5 rounded-full uppercase",
                        "bg-purple-400/10 text-purple-400"
                      )}>
                        {idea.category}
                      </span>
                      <h3 className="font-semibold text-lg mt-2">{idea.title}</h3>
                    </div>
                    <div className="flex gap-2">
                      <span className={cn(
                        "text-xs px-2 py-1 rounded-lg",
                        idea.estimated_impact === "high" 
                          ? "bg-green-400/10 text-green-400"
                          : "bg-yellow-400/10 text-yellow-400"
                      )}>
                        {idea.estimated_impact} impact
                      </span>
                      <span className={cn(
                        "text-xs px-2 py-1 rounded-lg",
                        idea.difficulty === "easy" 
                          ? "bg-blue-400/10 text-blue-400"
                          : idea.difficulty === "medium"
                          ? "bg-yellow-400/10 text-yellow-400"
                          : "bg-red-400/10 text-red-400"
                      )}>
                        {idea.difficulty}
                      </span>
                    </div>
                  </div>

                  <p className="text-white/70 mb-4">{idea.description}</p>

                  <div className="p-3 rounded-lg bg-electric/5 border border-electric/20 mb-4">
                    <div className="text-xs text-electric mb-1">Hook</div>
                    <div className="font-medium">&quot;{idea.hook}&quot;</div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-white/40 mb-1">Timeline</div>
                      <div>{idea.timeline}</div>
                    </div>
                    <div>
                      <div className="text-white/40 mb-1">Target Emotion</div>
                      <div>{idea.target_emotion}</div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="text-xs text-white/40 mb-2">Resources Needed</div>
                    <div className="flex flex-wrap gap-2">
                      {idea.required_resources.map((resource: string, i: number) => (
                        <span key={i} className="px-2 py-1 rounded-lg bg-white/5 text-xs">
                          {resource}
                        </span>
                      ))}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

