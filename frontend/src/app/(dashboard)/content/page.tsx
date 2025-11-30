"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  FileEdit,
  Sparkles,
  Loader2,
  Copy,
  Check,
  RefreshCw,
  MessageSquare,
  Mail,
  Megaphone,
  FileText,
  Layout,
  Instagram,
  Twitter,
  Linkedin,
  Facebook,
  Lightbulb,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface ContentVariation {
  content: string;
  hashtags?: string[];
  call_to_action?: string;
}

interface ContentIdea {
  title: string;
  description: string;
  content_type: string;
  suggested_platforms: string[];
}

const contentTypes = [
  { id: "social_post", name: "Social Post", icon: MessageSquare },
  { id: "blog", name: "Blog Article", icon: FileText },
  { id: "email", name: "Email", icon: Mail },
  { id: "ad_copy", name: "Ad Copy", icon: Megaphone },
  { id: "landing_page", name: "Landing Page", icon: Layout },
];

const platforms = [
  { id: "instagram", name: "Instagram", icon: Instagram },
  { id: "twitter", name: "Twitter/X", icon: Twitter },
  { id: "linkedin", name: "LinkedIn", icon: Linkedin },
  { id: "facebook", name: "Facebook", icon: Facebook },
];

const tones = [
  "professional",
  "casual",
  "humorous",
  "inspiring",
  "educational",
  "persuasive",
];

export default function ContentPage() {
  const { organization } = useAuth();
  const [activeTab, setActiveTab] = useState<"generate" | "ideas">("generate");
  
  // Generate form
  const [contentType, setContentType] = useState("social_post");
  const [platform, setPlatform] = useState("");
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("professional");
  const [targetAudience, setTargetAudience] = useState("");
  const [keywords, setKeywords] = useState("");
  const [additionalInstructions, setAdditionalInstructions] = useState("");
  
  // Results
  const [variations, setVariations] = useState<ContentVariation[]>([]);
  const [ideas, setIdeas] = useState<ContentIdea[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleGenerate = async () => {
    if (!topic.trim() || !organization) return;
    
    setIsLoading(true);
    setVariations([]);
    
    try {
      const response = await authFetch(
        `/api/v1/content/generate?org_id=${organization.id}&variations=3`,
        {
          method: "POST",
          body: JSON.stringify({
            content_type: contentType,
            topic,
            platform: platform || undefined,
            tone,
            target_audience: targetAudience || undefined,
            keywords: keywords ? keywords.split(",").map((k) => k.trim()) : undefined,
            additional_instructions: additionalInstructions || undefined,
          }),
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setVariations(data.variations);
      }
    } catch (error) {
      console.error("Failed to generate content:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateIdeas = async () => {
    if (!organization) return;
    
    setIsLoading(true);
    setIdeas([]);
    
    try {
      const response = await authFetch(
        `/api/v1/content/ideas?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            topic: topic || undefined,
            target_audience: targetAudience || undefined,
            count: 5,
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
      setIsLoading(false);
    }
  };

  const handleCopy = async (index: number, content: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleUseIdea = (idea: ContentIdea) => {
    setTopic(idea.title);
    setContentType(idea.content_type === "social_post" ? "social_post" : "blog");
    setActiveTab("generate");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
            <FileEdit className="w-5 h-5 text-purple-400" />
          </div>
          ContentForge
        </h1>
        <p className="text-white/60 mt-1">
          AI-powered content generation for all your marketing channels
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("generate")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors",
            activeTab === "generate"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          Generate Content
        </button>
        <button
          onClick={() => setActiveTab("ideas")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "ideas"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <Lightbulb className="w-4 h-4" />
          Get Ideas
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="card space-y-6">
          {activeTab === "generate" ? (
            <>
              {/* Content Type */}
              <div>
                <label className="block text-sm text-white/60 mb-3">
                  Content Type *
                </label>
                <div className="flex flex-wrap gap-2">
                  {contentTypes.map((type) => (
                    <button
                      key={type.id}
                      onClick={() => setContentType(type.id)}
                      className={cn(
                        "flex items-center gap-2 px-4 py-2 rounded-xl border text-sm transition-all",
                        contentType === type.id
                          ? "border-electric bg-electric/10 text-electric"
                          : "border-white/10 hover:border-white/20 text-white/60"
                      )}
                    >
                      <type.icon className="w-4 h-4" />
                      {type.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Platform (for social posts) */}
              {contentType === "social_post" && (
                <div>
                  <label className="block text-sm text-white/60 mb-3">
                    Platform
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {platforms.map((p) => (
                      <button
                        key={p.id}
                        onClick={() =>
                          setPlatform(platform === p.id ? "" : p.id)
                        }
                        className={cn(
                          "flex items-center gap-2 px-4 py-2 rounded-xl border text-sm transition-all",
                          platform === p.id
                            ? "border-electric bg-electric/10 text-electric"
                            : "border-white/10 hover:border-white/20 text-white/60"
                        )}
                      >
                        <p.icon className="w-4 h-4" />
                        {p.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Topic */}
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Topic *
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., Product launch announcement, Industry trends..."
                  className="input"
                />
              </div>

              {/* Tone */}
              <div>
                <label className="block text-sm text-white/60 mb-2">Tone</label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="input"
                >
                  {tones.map((t) => (
                    <option key={t} value={t}>
                      {t.charAt(0).toUpperCase() + t.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Target Audience */}
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Target Audience
                </label>
                <input
                  type="text"
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  placeholder="e.g., Marketing professionals, small business owners..."
                  className="input"
                />
              </div>

              {/* Keywords */}
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Keywords (comma-separated)
                </label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g., AI, automation, marketing"
                  className="input"
                />
              </div>

              {/* Additional Instructions */}
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Additional Instructions
                </label>
                <textarea
                  value={additionalInstructions}
                  onChange={(e) => setAdditionalInstructions(e.target.value)}
                  placeholder="Any specific requirements or style preferences..."
                  className="input min-h-[80px] resize-none"
                />
              </div>

              <button
                onClick={handleGenerate}
                disabled={!topic.trim() || isLoading}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generate Content
                  </>
                )}
              </button>
            </>
          ) : (
            <>
              {/* Ideas Form */}
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Topic or Industry
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., SaaS, E-commerce, Healthcare..."
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Target Audience
                </label>
                <input
                  type="text"
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  placeholder="e.g., Startup founders, Marketing teams..."
                  className="input"
                />
              </div>

              <button
                onClick={handleGenerateIdeas}
                disabled={isLoading}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Lightbulb className="w-5 h-5" />
                    Generate Ideas
                  </>
                )}
              </button>
            </>
          )}
        </div>

        {/* Results */}
        <div className="space-y-4">
          {activeTab === "generate" && variations.length > 0 && (
            <>
              <h3 className="text-lg font-semibold">Generated Content</h3>
              {variations.map((variation, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card relative group"
                >
                  <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                    <button
                      onClick={() => handleCopy(index, variation.content)}
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                      title="Copy"
                    >
                      {copiedIndex === index ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4 text-white/60" />
                      )}
                    </button>
                  </div>

                  <div className="text-xs text-white/40 mb-2">
                    Variation {index + 1}
                  </div>
                  <div className="whitespace-pre-wrap text-sm">
                    {variation.content}
                  </div>

                  {variation.hashtags && variation.hashtags.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-white/10">
                      <div className="flex flex-wrap gap-2">
                        {variation.hashtags.map((tag, i) => (
                          <span
                            key={i}
                            className="text-xs px-2 py-1 rounded-lg bg-electric/10 text-electric"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </>
          )}

          {activeTab === "ideas" && ideas.length > 0 && (
            <>
              <h3 className="text-lg font-semibold">Content Ideas</h3>
              {ideas.map((idea, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card group cursor-pointer hover:border-electric/30 transition-colors"
                  onClick={() => handleUseIdea(idea)}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium group-hover:text-electric transition-colors">
                        {idea.title}
                      </h4>
                      <p className="text-sm text-white/60 mt-1">
                        {idea.description}
                      </p>
                    </div>
                    <span className="text-xs px-2 py-1 rounded-lg bg-white/5 text-white/40 capitalize">
                      {idea.content_type.replace("_", " ")}
                    </span>
                  </div>
                  <div className="flex gap-2 mt-3">
                    {idea.suggested_platforms.map((p, i) => (
                      <span
                        key={i}
                        className="text-xs px-2 py-1 rounded-lg bg-purple-500/10 text-purple-400"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-electric mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    Click to use this idea →
                  </div>
                </motion.div>
              ))}
            </>
          )}

          {/* Empty State */}
          {((activeTab === "generate" && variations.length === 0) ||
            (activeTab === "ideas" && ideas.length === 0)) &&
            !isLoading && (
              <div className="card text-center py-12">
                <Sparkles className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <h3 className="font-medium mb-2">
                  {activeTab === "generate"
                    ? "Ready to create"
                    : "Ready for ideas"}
                </h3>
                <p className="text-sm text-white/60">
                  {activeTab === "generate"
                    ? "Fill in the form and click Generate to create content"
                    : "Enter a topic to get fresh content ideas"}
                </p>
              </div>
            )}
        </div>
      </div>
    </div>
  );
}

