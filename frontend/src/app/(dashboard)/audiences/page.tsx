"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Users,
  Sparkles,
  Loader2,
  Target,
  Heart,
  AlertTriangle,
  Zap,
  MessageSquare,
  ShoppingBag,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Persona {
  id: string;
  name: string;
  age_range: string;
  occupation: string;
  income_level: string;
  location: string;
  bio: string;
  goals: string[];
  pain_points: string[];
  motivations: string[];
  objections: string[];
  preferred_channels: string[];
  buying_triggers: string[];
  content_preferences: string[];
  brand_affinity: string[];
  psychographic_profile: string;
}

export default function AudiencesPage() {
  const { organization } = useAuth();
  const [businessType, setBusinessType] = useState("");
  const [targetMarket, setTargetMarket] = useState("");
  const [productsServices, setProductsServices] = useState("");
  const [personaCount, setPersonaCount] = useState(3);
  const [isGenerating, setIsGenerating] = useState(false);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [expandedPersona, setExpandedPersona] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);

  const handleGenerate = async () => {
    if (!organization || !businessType || !targetMarket || !productsServices) return;
    
    setIsGenerating(true);
    try {
      const response = await authFetch(
        `/api/v1/personas/generate?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            business_type: businessType,
            target_market: targetMarket,
            products_services: productsServices,
            count: personaCount,
          }),
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setPersonas(data.personas);
        setRecommendations(data.targeting_recommendations);
      }
    } catch (error) {
      console.error("Failed to generate personas:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
            <Users className="w-5 h-5 text-green-400" />
          </div>
          AudienceGenome
        </h1>
        <p className="text-white/60 mt-1">
          AI-powered customer persona & segmentation engine
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Generator Form */}
        <div className="lg:col-span-1">
          <div className="card sticky top-24">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-electric" />
              Generate Personas
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Business Type *
                </label>
                <input
                  type="text"
                  value={businessType}
                  onChange={(e) => setBusinessType(e.target.value)}
                  placeholder="e.g., B2B SaaS, E-commerce, Agency"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Target Market *
                </label>
                <textarea
                  value={targetMarket}
                  onChange={(e) => setTargetMarket(e.target.value)}
                  placeholder="Describe your ideal customers..."
                  className="input min-h-[80px] resize-none"
                />
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Products/Services *
                </label>
                <textarea
                  value={productsServices}
                  onChange={(e) => setProductsServices(e.target.value)}
                  placeholder="What do you offer?"
                  className="input min-h-[80px] resize-none"
                />
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Number of Personas: {personaCount}
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={personaCount}
                  onChange={(e) => setPersonaCount(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating || !businessType || !targetMarket || !productsServices}
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
                    Generate Personas
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="lg:col-span-2 space-y-4">
          {personas.length === 0 ? (
            <div className="card text-center py-12">
              <Users className="w-12 h-12 text-white/20 mx-auto mb-4" />
              <h3 className="font-medium mb-2">No personas yet</h3>
              <p className="text-sm text-white/50">
                Fill in your business details and click Generate to create AI-powered personas
              </p>
            </div>
          ) : (
            <>
              {/* Recommendations */}
              {recommendations.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card bg-electric/5 border-electric/20"
                >
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Target className="w-5 h-5 text-electric" />
                    Targeting Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <Zap className="w-4 h-4 text-electric flex-shrink-0 mt-0.5" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              )}

              {/* Personas */}
              {personas.map((persona, index) => (
                <motion.div
                  key={persona.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card"
                >
                  <button
                    onClick={() =>
                      setExpandedPersona(
                        expandedPersona === persona.id ? null : persona.id
                      )
                    }
                    className="w-full flex items-start justify-between text-left"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-electric to-purple-500 flex items-center justify-center text-xl font-bold">
                        {persona.name.charAt(0)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{persona.name}</h3>
                        <p className="text-sm text-white/60">
                          {persona.occupation}
                        </p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-white/40">
                          <span>{persona.age_range}</span>
                          <span>{persona.income_level}</span>
                          <span>{persona.location}</span>
                        </div>
                      </div>
                    </div>
                    {expandedPersona === persona.id ? (
                      <ChevronUp className="w-5 h-5 text-white/40" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-white/40" />
                    )}
                  </button>

                  {expandedPersona === persona.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="mt-6 pt-6 border-t border-white/10 space-y-6"
                    >
                      <p className="text-white/70">{persona.bio}</p>

                      <div className="grid md:grid-cols-2 gap-6">
                        {/* Goals */}
                        <div>
                          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                            <Target className="w-4 h-4 text-green-400" />
                            Goals
                          </h4>
                          <ul className="space-y-1">
                            {persona.goals.map((goal, i) => (
                              <li key={i} className="text-sm text-white/60">
                                • {goal}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Pain Points */}
                        <div>
                          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 text-red-400" />
                            Pain Points
                          </h4>
                          <ul className="space-y-1">
                            {persona.pain_points.map((pain, i) => (
                              <li key={i} className="text-sm text-white/60">
                                • {pain}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Motivations */}
                        <div>
                          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                            <Heart className="w-4 h-4 text-pink-400" />
                            Motivations
                          </h4>
                          <ul className="space-y-1">
                            {persona.motivations.map((mot, i) => (
                              <li key={i} className="text-sm text-white/60">
                                • {mot}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Buying Triggers */}
                        <div>
                          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                            <ShoppingBag className="w-4 h-4 text-yellow-400" />
                            Buying Triggers
                          </h4>
                          <ul className="space-y-1">
                            {persona.buying_triggers.map((trigger, i) => (
                              <li key={i} className="text-sm text-white/60">
                                • {trigger}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {/* Channels */}
                      <div>
                        <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                          <MessageSquare className="w-4 h-4 text-electric" />
                          Preferred Channels
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {persona.preferred_channels.map((channel, i) => (
                            <span
                              key={i}
                              className="px-3 py-1 rounded-lg bg-electric/10 text-electric text-sm"
                            >
                              {channel}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Psychographic Profile */}
                      <div className="p-4 rounded-xl bg-white/5">
                        <h4 className="text-sm font-medium mb-2">
                          Psychographic Profile
                        </h4>
                        <p className="text-sm text-white/60">
                          {persona.psychographic_profile}
                        </p>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

