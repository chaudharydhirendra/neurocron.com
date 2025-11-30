"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  FolderKanban,
  Plus,
  Search,
  Filter,
  Loader2,
  Calendar,
  Users,
  CheckCircle,
  Clock,
  AlertCircle,
  ChevronRight,
  Sparkles,
  LayoutList,
  LayoutGrid,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Project {
  id: string;
  name: string;
  description: string;
  project_type: string;
  status: string;
  start_date: string;
  target_date: string;
  progress: number;
  budget: number;
  spent: number;
  color: string;
  tags: string[];
}

interface ProjectAnalytics {
  projects: Record<string, number>;
  tasks: Record<string, number>;
  overdue_tasks: number;
  total_projects: number;
  total_tasks: number;
}

export default function ProjectsPage() {
  const { organization } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [analytics, setAnalytics] = useState<ProjectAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [projectsRes, analyticsRes] = await Promise.all([
        authFetch(`/api/v1/projects/projects?org_id=${organization.id}`),
        authFetch(`/api/v1/projects/analytics/overview?org_id=${organization.id}`),
      ]);

      if (projectsRes.ok) {
        const data = await projectsRes.json();
        setProjects(data.projects || []);
      }
      if (analyticsRes.ok) {
        const data = await analyticsRes.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error("Failed to fetch projects:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "in_progress":
        return "bg-blue-500/20 text-blue-400";
      case "completed":
        return "bg-green-500/20 text-green-400";
      case "on_hold":
        return "bg-yellow-500/20 text-yellow-400";
      case "cancelled":
        return "bg-red-500/20 text-red-400";
      default:
        return "bg-white/10 text-white/60";
    }
  };

  const getStatusLabel = (status: string) => {
    return status.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center">
              <FolderKanban className="w-5 h-5 text-white" />
            </div>
            ProjectHub
          </h1>
          <p className="text-white/60 mt-1">
            AI-powered project management for marketing teams
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Project
        </button>
      </div>

      {/* Stats */}
      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <FolderKanban className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <div className="text-2xl font-bold">{analytics.total_projects}</div>
                <div className="text-xs text-white/50">Total Projects</div>
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
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <div className="text-2xl font-bold">{analytics.tasks.done || 0}</div>
                <div className="text-xs text-white/50">Completed Tasks</div>
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
              <div className="w-10 h-10 rounded-lg bg-electric/10 flex items-center justify-center">
                <Clock className="w-5 h-5 text-electric" />
              </div>
              <div>
                <div className="text-2xl font-bold">{analytics.tasks.in_progress || 0}</div>
                <div className="text-xs text-white/50">In Progress</div>
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
              <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <div className="text-2xl font-bold text-red-400">{analytics.overdue_tasks}</div>
                <div className="text-xs text-white/50">Overdue</div>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search projects..."
            className="input pl-10 w-full"
          />
        </div>
        <div className="flex gap-2">
          {["all", "planning", "in_progress", "completed"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status === "all" ? null : status)}
              className={cn(
                "px-3 py-2 rounded-lg text-sm transition-colors capitalize",
                (statusFilter === status || (status === "all" && !statusFilter))
                  ? "bg-electric text-white"
                  : "bg-white/5 text-white/60 hover:text-white"
              )}
            >
              {status.replace("_", " ")}
            </button>
          ))}
        </div>
        <div className="flex gap-1 bg-white/5 rounded-lg p-1">
          <button
            onClick={() => setViewMode("list")}
            className={cn(
              "p-2 rounded transition-colors",
              viewMode === "list" ? "bg-electric text-white" : "text-white/60"
            )}
          >
            <LayoutList className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode("grid")}
            className={cn(
              "p-2 rounded transition-colors",
              viewMode === "grid" ? "bg-electric text-white" : "text-white/60"
            )}
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Projects */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-electric" />
        </div>
      ) : projects.length === 0 ? (
        <div className="card p-12 text-center">
          <FolderKanban className="w-16 h-16 mx-auto mb-4 text-white/20" />
          <h3 className="text-xl font-semibold mb-2">No projects yet</h3>
          <p className="text-white/50 mb-6">Create your first project to get started</p>
          <button className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            Create Project
          </button>
        </div>
      ) : viewMode === "list" ? (
        <div className="card divide-y divide-white/5">
          {projects
            .filter((p) => !statusFilter || p.status === statusFilter)
            .map((project) => (
              <div
                key={project.id}
                className="p-4 hover:bg-white/5 cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div
                      className="w-3 h-12 rounded-full"
                      style={{ backgroundColor: project.color || "#0066FF" }}
                    />
                    <div>
                      <div className="font-medium">{project.name}</div>
                      <div className="text-sm text-white/50">
                        {project.project_type} • {formatDate(project.target_date)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="w-32">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-white/50">Progress</span>
                        <span className="font-medium">{project.progress}%</span>
                      </div>
                      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-electric rounded-full"
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                    </div>
                    <span className={cn("px-3 py-1 rounded-full text-xs", getStatusColor(project.status))}>
                      {getStatusLabel(project.status)}
                    </span>
                    <ChevronRight className="w-4 h-4 text-white/30" />
                  </div>
                </div>
              </div>
            ))}
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-4">
          {projects
            .filter((p) => !statusFilter || p.status === statusFilter)
            .map((project) => (
              <div key={project.id} className="card p-6 cursor-pointer hover:border-electric/50 transition-colors">
                <div className="flex items-center gap-3 mb-4">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: project.color || "#0066FF" }}
                  />
                  <span className={cn("px-2 py-0.5 rounded text-xs", getStatusColor(project.status))}>
                    {getStatusLabel(project.status)}
                  </span>
                </div>
                <h3 className="font-semibold mb-2">{project.name}</h3>
                <p className="text-sm text-white/50 mb-4 line-clamp-2">
                  {project.description || "No description"}
                </p>
                <div className="flex items-center justify-between text-sm mb-3">
                  <span className="text-white/50">Progress</span>
                  <span className="font-medium">{project.progress}%</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mb-4">
                  <div
                    className="h-full bg-electric rounded-full"
                    style={{ width: `${project.progress}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-sm text-white/50">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {formatDate(project.target_date)}
                  </div>
                  <div className="flex items-center gap-1">
                    <Sparkles className="w-4 h-4" />
                    AI-managed
                  </div>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

