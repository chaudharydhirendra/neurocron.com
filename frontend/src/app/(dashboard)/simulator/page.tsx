"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Beaker,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Play,
  Loader2,
  Plus,
  ChevronRight,
  Calendar,
  Target,
  Sparkles,
  AlertTriangle,
  CheckCircle,
  BarChart3,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Simulation {
  id: string;
  name: string;
  simulation_type: string;
  status: string;
  improvement_percentage: number;
  confidence_score: number;
  created_at: string;
}

interface QuickSimResult {
  scenario: any;
  prediction: any;
  recommendation: string;
}

export default function SimulatorPage() {
  const { organization } = useAuth();
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"quick" | "history" | "forecast">("quick");
  
  // Quick simulation state
  const [currentBudget, setCurrentBudget] = useState(10000);
  const [testBudget, setTestBudget] = useState(15000);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simResult, setSimResult] = useState<QuickSimResult | null>(null);

  useEffect(() => {
    if (organization) {
      fetchSimulations();
    }
  }, [organization]);

  const fetchSimulations = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const response = await authFetch(`/api/v1/simulator/simulations?org_id=${organization.id}`);
      if (response.ok) {
        const data = await response.json();
        setSimulations(data.simulations || []);
      }
    } catch (error) {
      console.error("Failed to fetch simulations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const runQuickSimulation = async () => {
    if (!organization) return;
    setIsSimulating(true);
    setSimResult(null);

    try {
      const response = await authFetch(
        `/api/v1/simulator/quick/budget?org_id=${organization.id}&current_budget=${currentBudget}&test_budget=${testBudget}`,
        { method: "POST" }
      );
      if (response.ok) {
        const data = await response.json();
        setSimResult(data);
      }
    } catch (error) {
      console.error("Simulation failed:", error);
    } finally {
      setIsSimulating(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat("en-US").format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
              <Beaker className="w-5 h-5 text-white" />
            </div>
            SimulatorX
          </h1>
          <p className="text-white/60 mt-1">
            Marketing what-if predictions and scenario planning
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Simulation
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {[
          { id: "quick", label: "Quick What-If", icon: Sparkles },
          { id: "history", label: "Simulations", icon: BarChart3 },
          { id: "forecast", label: "Forecasting", icon: Calendar },
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

      {activeTab === "quick" ? (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Input Panel */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-6">Budget What-If Analysis</h3>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-white/60 mb-2">
                  Current Monthly Budget
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                  <input
                    type="number"
                    value={currentBudget}
                    onChange={(e) => setCurrentBudget(Number(e.target.value))}
                    className="input pl-10 w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/60 mb-2">
                  Test Budget (What-If)
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                  <input
                    type="number"
                    value={testBudget}
                    onChange={(e) => setTestBudget(Number(e.target.value))}
                    className="input pl-10 w-full"
                  />
                </div>
              </div>

              <div className="p-4 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/60">Budget Change</span>
                  <span className={cn(
                    "font-medium",
                    testBudget > currentBudget ? "text-green-400" : "text-red-400"
                  )}>
                    {testBudget > currentBudget ? "+" : ""}
                    {formatCurrency(testBudget - currentBudget)} ({((testBudget - currentBudget) / currentBudget * 100).toFixed(0)}%)
                  </span>
                </div>
              </div>

              <button
                onClick={runQuickSimulation}
                disabled={isSimulating}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {isSimulating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Running Simulation...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Run Prediction
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Panel */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-6">Prediction Results</h3>
            
            {!simResult ? (
              <div className="text-center py-12">
                <Beaker className="w-12 h-12 mx-auto mb-4 text-white/20" />
                <p className="text-white/50">
                  Configure your scenario and run a prediction
                </p>
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Overall Result */}
                <div className={cn(
                  "p-4 rounded-lg border",
                  simResult.prediction.improvement_percentage > 0
                    ? "bg-green-500/10 border-green-500/30"
                    : "bg-red-500/10 border-red-500/30"
                )}>
                  <div className="flex items-center gap-3">
                    {simResult.prediction.improvement_percentage > 0 ? (
                      <TrendingUp className="w-8 h-8 text-green-400" />
                    ) : (
                      <TrendingDown className="w-8 h-8 text-red-400" />
                    )}
                    <div>
                      <div className="text-2xl font-bold">
                        {simResult.prediction.improvement_percentage > 0 ? "+" : ""}
                        {simResult.prediction.improvement_percentage}%
                      </div>
                      <div className="text-sm text-white/60">Predicted Revenue Change</div>
                    </div>
                  </div>
                </div>

                {/* Metrics Comparison */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-white/60 mb-3">Current Scenario</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-white/60">Impressions</span>
                        <span>{formatNumber(simResult.prediction.base_predicted.impressions)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-white/60">Clicks</span>
                        <span>{formatNumber(simResult.prediction.base_predicted.clicks)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-white/60">Conversions</span>
                        <span>{formatNumber(simResult.prediction.base_predicted.conversions)}</span>
                      </div>
                      <div className="flex justify-between font-medium">
                        <span className="text-white/60">Revenue</span>
                        <span>{formatCurrency(simResult.prediction.base_predicted.revenue)}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium text-white/60 mb-3">Test Scenario</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-white/60">Impressions</span>
                        <span className="text-electric">{formatNumber(simResult.prediction.test_predicted.impressions)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-white/60">Clicks</span>
                        <span className="text-electric">{formatNumber(simResult.prediction.test_predicted.clicks)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-white/60">Conversions</span>
                        <span className="text-electric">{formatNumber(simResult.prediction.test_predicted.conversions)}</span>
                      </div>
                      <div className="flex justify-between font-medium">
                        <span className="text-white/60">Revenue</span>
                        <span className="text-electric">{formatCurrency(simResult.prediction.test_predicted.revenue)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Confidence & Risk */}
                <div className="flex gap-4">
                  <div className="flex-1 p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <Target className="w-4 h-4 text-electric" />
                      <span className="text-sm text-white/60">Confidence</span>
                    </div>
                    <div className="text-xl font-bold">{simResult.prediction.confidence_score}%</div>
                  </div>
                  <div className="flex-1 p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertTriangle className="w-4 h-4 text-yellow-400" />
                      <span className="text-sm text-white/60">Risk Level</span>
                    </div>
                    <div className={cn(
                      "text-xl font-bold capitalize",
                      simResult.prediction.risk_level === "low" ? "text-green-400" :
                      simResult.prediction.risk_level === "medium" ? "text-yellow-400" : "text-red-400"
                    )}>
                      {simResult.prediction.risk_level}
                    </div>
                  </div>
                </div>

                {/* Recommendation */}
                <div className="p-4 bg-electric/10 border border-electric/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-electric" />
                    <span className="font-medium">Recommendation</span>
                  </div>
                  <p className="text-white/80">{simResult.recommendation}</p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      ) : activeTab === "history" ? (
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-white/10">
            <h3 className="font-semibold">Simulation History</h3>
          </div>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : simulations.length === 0 ? (
            <div className="text-center py-12">
              <Beaker className="w-12 h-12 mx-auto mb-4 text-white/20" />
              <h3 className="text-lg font-medium mb-2">No simulations yet</h3>
              <p className="text-white/50">Run your first what-if analysis</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {simulations.map((sim) => (
                <div key={sim.id} className="p-4 hover:bg-white/5 transition-colors cursor-pointer">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{sim.name}</div>
                      <div className="text-sm text-white/50 capitalize">{sim.simulation_type} simulation</div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className={cn(
                        "px-3 py-1 rounded-full text-sm font-medium",
                        sim.improvement_percentage > 0
                          ? "bg-green-500/20 text-green-400"
                          : "bg-red-500/20 text-red-400"
                      )}>
                        {sim.improvement_percentage > 0 ? "+" : ""}
                        {sim.improvement_percentage}%
                      </div>
                      <ChevronRight className="w-4 h-4 text-white/30" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="card p-6 text-center">
          <Calendar className="w-12 h-12 mx-auto mb-4 text-white/20" />
          <h3 className="text-lg font-medium mb-2">Marketing Forecasting</h3>
          <p className="text-white/50 mb-4 max-w-md mx-auto">
            Create long-term projections for your marketing performance based on historical data and assumptions.
          </p>
          <button className="btn-primary">Create Forecast</button>
        </div>
      )}
    </div>
  );
}

