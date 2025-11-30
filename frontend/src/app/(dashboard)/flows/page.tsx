"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  GitBranch,
  Plus,
  Play,
  Pause,
  MoreVertical,
  Search,
  Zap,
  Mail,
  Clock,
  Users,
  ArrowRight,
  Loader2,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface FlowTemplate {
  id: string;
  name: string;
  description: string;
  node_count: number;
}

interface Flow {
  id: string;
  name: string;
  description: string;
  status: string;
  total_executions: number;
  successful_executions: number;
}

export default function FlowsPage() {
  const { organization } = useAuth();
  const [flows, setFlows] = useState<Flow[]>([]);
  const [templates, setTemplates] = useState<FlowTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"flows" | "templates">("flows");

  useEffect(() => {
    const fetchData = async () => {
      if (!organization) return;

      try {
        const [flowsRes, templatesRes] = await Promise.all([
          authFetch(`/api/v1/flows/?org_id=${organization.id}`),
          authFetch("/api/v1/flows/templates"),
        ]);

        if (flowsRes.ok) {
          const data = await flowsRes.json();
          setFlows(data.flows || []);
        }

        if (templatesRes.ok) {
          const data = await templatesRes.json();
          setTemplates(data.templates || []);
        }
      } catch (error) {
        console.error("Failed to fetch flows:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [organization]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-400 bg-green-400/10";
      case "paused":
        return "text-yellow-400 bg-yellow-400/10";
      case "draft":
        return "text-white/50 bg-white/5";
      default:
        return "text-white/50 bg-white/5";
    }
  };

  const getTemplateIcon = (id: string) => {
    switch (id) {
      case "welcome_series":
        return Mail;
      case "abandoned_cart":
        return Clock;
      case "lead_nurturing":
        return Users;
      default:
        return Zap;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
              <GitBranch className="w-5 h-5 text-purple-400" />
            </div>
            FlowBuilder
          </h1>
          <p className="text-white/60 mt-1">
            Visual automation builder for customer journeys
          </p>
        </div>
        <Link href="/flows/new" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Create Flow
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("flows")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors",
            activeTab === "flows"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          My Flows
        </button>
        <button
          onClick={() => setActiveTab("templates")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors",
            activeTab === "templates"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          Templates
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-electric" />
        </div>
      ) : activeTab === "flows" ? (
        flows.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card text-center py-12"
          >
            <GitBranch className="w-12 h-12 text-white/20 mx-auto mb-4" />
            <h3 className="font-medium mb-2">No flows yet</h3>
            <p className="text-white/60 text-sm mb-4">
              Create your first automation flow or start from a template
            </p>
            <div className="flex gap-3 justify-center">
              <Link href="/flows/new" className="btn-primary">
                Create Flow
              </Link>
              <button
                onClick={() => setActiveTab("templates")}
                className="btn-secondary"
              >
                Browse Templates
              </button>
            </div>
          </motion.div>
        ) : (
          <div className="grid gap-4">
            {flows.map((flow, index) => (
              <motion.div
                key={flow.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="card p-4 flex items-center justify-between group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                    <GitBranch className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="font-medium">{flow.name}</h3>
                      <span
                        className={cn(
                          "text-xs px-2 py-0.5 rounded-full capitalize",
                          getStatusColor(flow.status)
                        )}
                      >
                        {flow.status}
                      </span>
                    </div>
                    {flow.description && (
                      <p className="text-sm text-white/50 mt-0.5">
                        {flow.description}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-1 text-xs text-white/40">
                      <span>{flow.total_executions} executions</span>
                      <span>
                        {flow.total_executions > 0
                          ? Math.round(
                              (flow.successful_executions /
                                flow.total_executions) *
                                100
                            )
                          : 0}
                        % success rate
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {flow.status === "active" ? (
                    <button className="p-2 rounded-lg hover:bg-yellow-400/10 transition-colors">
                      <Pause className="w-5 h-5 text-yellow-400" />
                    </button>
                  ) : (
                    <button className="p-2 rounded-lg hover:bg-green-400/10 transition-colors">
                      <Play className="w-5 h-5 text-green-400" />
                    </button>
                  )}
                  <Link
                    href={`/flows/${flow.id}`}
                    className="btn-primary text-sm py-2"
                  >
                    Edit
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        )
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template, index) => {
            const Icon = getTemplateIcon(template.id);
            return (
              <motion.div
                key={template.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card group hover:border-purple-500/30 transition-colors cursor-pointer"
              >
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-4 group-hover:bg-purple-500/20 transition-colors">
                  <Icon className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="font-medium mb-1">{template.name}</h3>
                <p className="text-sm text-white/50 mb-4">
                  {template.description}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-white/40">
                    {template.node_count} steps
                  </span>
                  <Link
                    href={`/flows/new?template=${template.id}`}
                    className="flex items-center gap-1 text-sm text-purple-400 group-hover:text-purple-300 transition-colors"
                  >
                    Use Template
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}

