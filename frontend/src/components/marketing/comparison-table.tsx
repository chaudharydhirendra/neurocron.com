"use client";

import { motion } from "framer-motion";
import { Check, X, Minus, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface ComparisonRow {
  feature: string;
  traditional: boolean | string | "partial";
  neurocron: boolean | string | "partial";
}

interface ComparisonTableProps {
  title?: string;
  subtitle?: string;
  rows: ComparisonRow[];
}

export function ComparisonTable({
  title = "NeuroCron vs Traditional Marketing",
  subtitle = "See why teams are switching to autonomous marketing",
  rows,
}: ComparisonTableProps) {
  const renderValue = (value: boolean | string | "partial", isNeurocron: boolean) => {
    if (value === true) {
      return (
        <div
          className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center",
            isNeurocron ? "bg-green-500/20" : "bg-green-500/10"
          )}
        >
          <Check
            className={cn(
              "w-5 h-5",
              isNeurocron ? "text-green-400" : "text-green-400/60"
            )}
          />
        </div>
      );
    }
    if (value === false) {
      return (
        <div className="w-8 h-8 rounded-full bg-red-500/10 flex items-center justify-center">
          <X className="w-5 h-5 text-red-400/60" />
        </div>
      );
    }
    if (value === "partial") {
      return (
        <div className="w-8 h-8 rounded-full bg-yellow-500/10 flex items-center justify-center">
          <Minus className="w-5 h-5 text-yellow-400/60" />
        </div>
      );
    }
    return <span className="text-white/60 text-sm">{value}</span>;
  };

  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">{title}</h2>
          <p className="text-xl text-white/60">{subtitle}</p>
        </motion.div>

        {/* Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="overflow-hidden rounded-2xl border border-white/10"
        >
          {/* Header Row */}
          <div className="grid grid-cols-3 bg-white/5">
            <div className="p-6 font-semibold">Feature</div>
            <div className="p-6 text-center font-semibold text-white/60">
              Traditional Tools
            </div>
            <div className="p-6 text-center font-semibold bg-electric/10 border-l border-electric/20">
              <div className="flex items-center justify-center gap-2">
                <Zap className="w-5 h-5 text-electric" />
                NeuroCron
              </div>
            </div>
          </div>

          {/* Rows */}
          {rows.map((row, index) => (
            <div
              key={index}
              className={cn(
                "grid grid-cols-3",
                index % 2 === 0 ? "bg-transparent" : "bg-white/[0.02]"
              )}
            >
              <div className="p-6 text-white/80">{row.feature}</div>
              <div className="p-6 flex items-center justify-center">
                {renderValue(row.traditional, false)}
              </div>
              <div className="p-6 flex items-center justify-center bg-electric/5 border-l border-electric/10">
                {renderValue(row.neurocron, true)}
              </div>
            </div>
          ))}
        </motion.div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 text-center"
        >
          <p className="text-white/60 mb-4">
            Ready to experience the difference?
          </p>
          <a
            href="/register"
            className="btn-primary inline-flex items-center gap-2"
          >
            Start Free Trial
          </a>
        </motion.div>
      </div>
    </section>
  );
}

interface TimeSavingsProps {
  title?: string;
  subtitle?: string;
  savings: {
    task: string;
    traditional: string;
    neurocron: string;
    savings: string;
  }[];
}

export function TimeSavings({
  title = "Save Hours Every Week",
  subtitle = "See how much time NeuroCron saves on common marketing tasks",
  savings,
}: TimeSavingsProps) {
  return (
    <section className="py-24 px-6 bg-midnight-50/30">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">{title}</h2>
          <p className="text-xl text-white/60">{subtitle}</p>
        </motion.div>

        {/* Savings Cards */}
        <div className="space-y-4">
          {savings.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="card flex flex-col md:flex-row items-center gap-6"
            >
              <div className="flex-1">
                <h3 className="font-semibold mb-1">{item.task}</h3>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-red-400/80 line-through">
                    {item.traditional}
                  </span>
                  <span className="text-white/40">→</span>
                  <span className="text-green-400">{item.neurocron}</span>
                </div>
              </div>
              <div className="text-center md:text-right">
                <div className="text-2xl font-bold gradient-text">
                  {item.savings}
                </div>
                <div className="text-white/50 text-sm">saved</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Total Savings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 p-8 rounded-2xl bg-neural-gradient/5 border border-electric/20 text-center"
        >
          <div className="text-5xl font-bold gradient-text mb-2">40+ hours</div>
          <div className="text-white/60">saved per month on average</div>
        </motion.div>
      </div>
    </section>
  );
}

