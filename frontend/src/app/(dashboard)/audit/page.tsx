"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  Globe,
  Loader2,
  CheckCircle,
  AlertTriangle,
  AlertCircle,
  Info,
  ArrowRight,
  RefreshCw,
  Download,
  ExternalLink,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface AuditIssue {
  category: string;
  severity: string;
  title: string;
  description: string;
  recommendation: string;
  impact?: string;
}

interface AuditScore {
  category: string;
  score: number;
  grade: string;
  issues_count: number;
}

interface AuditResult {
  url: string;
  overall_score: number;
  overall_grade: string;
  scores: AuditScore[];
  issues: AuditIssue[];
  recommendations: string[];
  audit_date: string;
}

const auditTypes = [
  { id: "seo", name: "SEO", description: "Search engine optimization" },
  { id: "performance", name: "Performance", description: "Page speed & Core Web Vitals" },
  { id: "social", name: "Social", description: "Social media integration" },
  { id: "content", name: "Content", description: "Content quality analysis" },
];

export default function AuditPage() {
  const { organization } = useAuth();
  const [url, setUrl] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<string[]>(["seo", "performance", "social"]);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AuditResult | null>(null);
  const [error, setError] = useState("");

  const toggleType = (type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const handleAudit = async () => {
    if (!url.trim() || !organization) return;

    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await authFetch(
        `/api/v1/audit/website?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            url: url.trim(),
            audit_types: selectedTypes,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to run audit");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case "A":
        return "text-green-400 bg-green-400/10 border-green-400/30";
      case "B":
        return "text-electric bg-electric/10 border-electric/30";
      case "C":
        return "text-yellow-400 bg-yellow-400/10 border-yellow-400/30";
      case "D":
        return "text-orange-400 bg-orange-400/10 border-orange-400/30";
      default:
        return "text-red-400 bg-red-400/10 border-red-400/30";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      default:
        return <Info className="w-5 h-5 text-electric" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-green-400";
    if (score >= 60) return "bg-yellow-400";
    if (score >= 40) return "bg-orange-400";
    return "bg-red-400";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center">
            <Search className="w-5 h-5 text-red-400" />
          </div>
          AuditX
        </h1>
        <p className="text-white/60 mt-1">
          Autonomous website and marketing audit engine
        </p>
      </div>

      {/* Audit Form */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Run Website Audit</h3>

        {/* URL Input */}
        <div className="mb-4">
          <label className="block text-sm text-white/60 mb-2">Website URL</label>
          <div className="relative">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="input pl-11"
              onKeyDown={(e) => e.key === "Enter" && handleAudit()}
            />
          </div>
        </div>

        {/* Audit Types */}
        <div className="mb-6">
          <label className="block text-sm text-white/60 mb-3">Audit Types</label>
          <div className="flex flex-wrap gap-2">
            {auditTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => toggleType(type.id)}
                className={cn(
                  "px-4 py-2 rounded-xl border text-sm transition-all",
                  selectedTypes.includes(type.id)
                    ? "border-electric bg-electric/10 text-electric"
                    : "border-white/10 text-white/60 hover:border-white/20"
                )}
              >
                {type.name}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handleAudit}
          disabled={!url.trim() || selectedTypes.length === 0 || isLoading}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Run Audit
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Overall Score */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold">Audit Results</h3>
                <p className="text-sm text-white/60 flex items-center gap-2 mt-1">
                  <ExternalLink className="w-4 h-4" />
                  {result.url}
                </p>
              </div>
              <button
                onClick={handleAudit}
                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                title="Re-run audit"
              >
                <RefreshCw className="w-5 h-5 text-white/60" />
              </button>
            </div>

            <div className="flex items-center gap-8">
              {/* Overall Grade */}
              <div
                className={cn(
                  "w-24 h-24 rounded-2xl border-2 flex items-center justify-center",
                  getGradeColor(result.overall_grade)
                )}
              >
                <span className="text-4xl font-bold">{result.overall_grade}</span>
              </div>

              {/* Score Details */}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-white/60">Overall Score</span>
                  <span className="text-2xl font-bold">{result.overall_score}/100</span>
                </div>
                <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${result.overall_score}%` }}
                    transition={{ duration: 0.5 }}
                    className={cn("h-full rounded-full", getScoreColor(result.overall_score))}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Category Scores */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {result.scores.map((score, index) => (
              <motion.div
                key={score.category}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-medium">{score.category}</span>
                  <span
                    className={cn(
                      "text-lg font-bold px-2 py-0.5 rounded-lg border",
                      getGradeColor(score.grade)
                    )}
                  >
                    {score.grade}
                  </span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden mb-2">
                  <div
                    className={cn("h-full rounded-full", getScoreColor(score.score))}
                    style={{ width: `${score.score}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/60">{score.score}/100</span>
                  <span className="text-white/40">{score.issues_count} issues</span>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Issues */}
          {result.issues.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">
                Issues Found ({result.issues.length})
              </h3>
              <div className="space-y-4">
                {result.issues.map((issue, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 rounded-xl bg-white/5 border border-white/10"
                  >
                    <div className="flex items-start gap-3">
                      {getSeverityIcon(issue.severity)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{issue.title}</h4>
                          <span
                            className={cn(
                              "text-xs px-2 py-0.5 rounded-full",
                              issue.severity === "critical"
                                ? "bg-red-400/10 text-red-400"
                                : issue.severity === "warning"
                                ? "bg-yellow-400/10 text-yellow-400"
                                : "bg-electric/10 text-electric"
                            )}
                          >
                            {issue.category}
                          </span>
                        </div>
                        <p className="text-sm text-white/60 mb-2">{issue.description}</p>
                        <div className="flex items-start gap-2 p-3 rounded-lg bg-electric/5 border border-electric/20">
                          <CheckCircle className="w-4 h-4 text-electric flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-electric">{issue.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Top Recommendations</h3>
              <div className="space-y-3">
                {result.recommendations.map((rec, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-3 p-3 rounded-xl bg-neural-gradient/10 border border-electric/20"
                  >
                    <ArrowRight className="w-5 h-5 text-electric flex-shrink-0" />
                    <span className="text-sm">{rec}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}

