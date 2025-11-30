"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Rocket,
  Calendar,
  DollarSign,
  Tag,
  ArrowRight,
  Loader2,
  Check,
  Zap,
  Gift,
  Users,
  Megaphone,
  Smartphone,
  Target,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Template {
  id: string;
  name: string;
  category: string;
  description: string;
  duration_days: number;
  estimated_budget: { min: number; max: number };
  channels: string[];
}

interface TemplateDetail extends Template {
  components: Record<string, { name: string; tasks: string[] }>;
  content_templates: { type: string; name: string }[];
  kpis: string[];
}

const categoryIcons: Record<string, any> = {
  launch: Rocket,
  seasonal: Gift,
  lead_gen: Target,
  branding: Megaphone,
};

const categoryColors: Record<string, string> = {
  launch: "bg-electric/10 text-electric",
  seasonal: "bg-red-400/10 text-red-400",
  lead_gen: "bg-green-400/10 text-green-400",
  branding: "bg-purple-400/10 text-purple-400",
};

export default function LaunchPadPage() {
  const { organization } = useAuth();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLaunching, setIsLaunching] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        let url = "/api/v1/launchpad/";
        if (categoryFilter) {
          url += `?category=${categoryFilter}`;
        }
        const response = await authFetch(url);
        if (response.ok) {
          const data = await response.json();
          setTemplates(data);
        }
      } catch (error) {
        console.error("Failed to fetch templates:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTemplates();
  }, [categoryFilter]);

  const handleSelectTemplate = async (templateId: string) => {
    try {
      const response = await authFetch(`/api/v1/launchpad/${templateId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedTemplate(data);
      }
    } catch (error) {
      console.error("Failed to fetch template:", error);
    }
  };

  const handleLaunch = async () => {
    if (!selectedTemplate || !organization) return;
    
    setIsLaunching(true);
    try {
      const response = await authFetch(
        `/api/v1/launchpad/${selectedTemplate.id}/launch?org_id=${organization.id}`,
        { method: "POST" }
      );
      if (response.ok) {
        const data = await response.json();
        alert(`Campaign created! ${data.tasks_created} tasks generated.`);
        setSelectedTemplate(null);
      }
    } catch (error) {
      console.error("Failed to launch:", error);
    } finally {
      setIsLaunching(false);
    }
  };

  const formatBudget = (min: number, max: number) => {
    return `$${(min / 1000).toFixed(0)}k - $${(max / 1000).toFixed(0)}k`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center">
            <Rocket className="w-5 h-5 text-orange-400" />
          </div>
          LaunchPad
        </h1>
        <p className="text-white/60 mt-1">
          Pre-built campaign blueprints for instant launch
        </p>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setCategoryFilter(null)}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors",
            !categoryFilter
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          All Templates
        </button>
        {[
          { id: "launch", name: "Product Launch" },
          { id: "seasonal", name: "Seasonal" },
          { id: "lead_gen", name: "Lead Generation" },
          { id: "branding", name: "Brand Awareness" },
        ].map((cat) => (
          <button
            key={cat.id}
            onClick={() => setCategoryFilter(cat.id)}
            className={cn(
              "px-4 py-2 rounded-xl text-sm font-medium transition-colors",
              categoryFilter === cat.id
                ? "bg-electric text-midnight"
                : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
            )}
          >
            {cat.name}
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Template List */}
        <div className="lg:col-span-2 space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-4">
              {templates.map((template, index) => {
                const Icon = categoryIcons[template.category] || Zap;
                return (
                  <motion.button
                    key={template.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => handleSelectTemplate(template.id)}
                    className={cn(
                      "card text-left group transition-all",
                      selectedTemplate?.id === template.id
                        ? "ring-2 ring-electric"
                        : "hover:border-white/20"
                    )}
                  >
                    <div className="flex items-start gap-4">
                      <div
                        className={cn(
                          "w-12 h-12 rounded-xl flex items-center justify-center",
                          categoryColors[template.category]
                        )}
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium group-hover:text-electric transition-colors">
                          {template.name}
                        </h3>
                        <p className="text-sm text-white/50 mt-1 line-clamp-2">
                          {template.description}
                        </p>
                        <div className="flex items-center gap-4 mt-3 text-xs text-white/40">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {template.duration_days} days
                          </span>
                          <span className="flex items-center gap-1">
                            <DollarSign className="w-3 h-3" />
                            {formatBudget(
                              template.estimated_budget.min,
                              template.estimated_budget.max
                            )}
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          )}
        </div>

        {/* Template Detail */}
        <div className="lg:col-span-1">
          {selectedTemplate ? (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="card sticky top-24"
            >
              <h2 className="text-xl font-bold mb-4">{selectedTemplate.name}</h2>
              <p className="text-sm text-white/60 mb-6">
                {selectedTemplate.description}
              </p>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 rounded-xl bg-white/5">
                  <div className="text-2xl font-bold">
                    {selectedTemplate.duration_days}
                  </div>
                  <div className="text-xs text-white/50">Days</div>
                </div>
                <div className="p-3 rounded-xl bg-white/5">
                  <div className="text-2xl font-bold">
                    {Object.values(selectedTemplate.components).reduce(
                      (acc, phase) => acc + phase.tasks.length,
                      0
                    )}
                  </div>
                  <div className="text-xs text-white/50">Tasks</div>
                </div>
              </div>

              {/* Channels */}
              <div className="mb-6">
                <h4 className="text-sm text-white/60 mb-2">Channels</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.channels.map((channel) => (
                    <span
                      key={channel}
                      className="px-2 py-1 rounded-lg bg-white/5 text-xs capitalize"
                    >
                      {channel.replace("_", " ")}
                    </span>
                  ))}
                </div>
              </div>

              {/* Phases */}
              <div className="mb-6">
                <h4 className="text-sm text-white/60 mb-2">Campaign Phases</h4>
                <div className="space-y-3">
                  {Object.entries(selectedTemplate.components).map(
                    ([key, phase]) => (
                      <div key={key} className="p-3 rounded-xl bg-white/5">
                        <div className="font-medium text-sm mb-2">
                          {phase.name}
                        </div>
                        <div className="space-y-1">
                          {phase.tasks.slice(0, 3).map((task, i) => (
                            <div
                              key={i}
                              className="flex items-center gap-2 text-xs text-white/50"
                            >
                              <Check className="w-3 h-3 text-green-400" />
                              {task}
                            </div>
                          ))}
                          {phase.tasks.length > 3 && (
                            <div className="text-xs text-white/30">
                              +{phase.tasks.length - 3} more tasks
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Content Templates */}
              <div className="mb-6">
                <h4 className="text-sm text-white/60 mb-2">
                  Included Content ({selectedTemplate.content_templates.length})
                </h4>
                <div className="space-y-1">
                  {selectedTemplate.content_templates.map((ct, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm">
                      <Tag className="w-3 h-3 text-electric" />
                      {ct.name}
                    </div>
                  ))}
                </div>
              </div>

              {/* KPIs */}
              <div className="mb-6">
                <h4 className="text-sm text-white/60 mb-2">Success Metrics</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.kpis.map((kpi) => (
                    <span
                      key={kpi}
                      className="px-2 py-1 rounded-lg bg-electric/10 text-electric text-xs capitalize"
                    >
                      {kpi.replace("_", " ")}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={handleLaunch}
                disabled={isLaunching}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {isLaunching ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Rocket className="w-5 h-5" />
                    Launch Campaign
                  </>
                )}
              </button>
            </motion.div>
          ) : (
            <div className="card text-center py-12">
              <Rocket className="w-12 h-12 text-white/20 mx-auto mb-4" />
              <h3 className="font-medium mb-2">Select a Template</h3>
              <p className="text-sm text-white/50">
                Choose a campaign template to see details and launch
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

