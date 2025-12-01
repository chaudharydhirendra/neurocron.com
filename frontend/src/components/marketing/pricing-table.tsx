"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Check, Sparkles, Building2, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PricingPlan {
  id: string;
  name: string;
  description: string;
  priceMonthly: number | null;
  priceYearly: number | null;
  features: string[];
  highlighted?: boolean;
  cta: {
    text: string;
    href: string;
  };
  badge?: string;
}

interface PricingTableProps {
  title?: string;
  subtitle?: string;
  plans: PricingPlan[];
}

export function PricingTable({
  title = "Simple, Transparent Pricing",
  subtitle = "Start free, upgrade when you need more power",
  plans,
}: PricingTableProps) {
  const [isYearly, setIsYearly] = useState(false);

  return (
    <section className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">{title}</h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">{subtitle}</p>
        </motion.div>

        {/* Billing Toggle */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="flex items-center justify-center gap-4 mb-16"
        >
          <span
            className={cn(
              "text-sm font-medium",
              !isYearly ? "text-white" : "text-white/50"
            )}
          >
            Monthly
          </span>
          <button
            onClick={() => setIsYearly(!isYearly)}
            className={cn(
              "relative w-14 h-7 rounded-full transition-colors",
              isYearly ? "bg-electric" : "bg-white/20"
            )}
          >
            <div
              className={cn(
                "absolute top-1 w-5 h-5 rounded-full bg-white transition-transform",
                isYearly ? "translate-x-8" : "translate-x-1"
              )}
            />
          </button>
          <span
            className={cn(
              "text-sm font-medium",
              isYearly ? "text-white" : "text-white/50"
            )}
          >
            Yearly
            <span className="ml-2 text-green-400 text-xs">Save 20%</span>
          </span>
        </motion.div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "relative rounded-2xl border p-6 flex flex-col",
                plan.highlighted
                  ? "bg-white/5 border-electric/30 shadow-lg shadow-electric/10"
                  : "bg-transparent border-white/10"
              )}
            >
              {/* Badge */}
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-electric text-xs font-medium">
                  {plan.badge}
                </div>
              )}

              {/* Plan Header */}
              <div className="mb-6">
                <h3 className="text-xl font-semibold mb-1">{plan.name}</h3>
                <p className="text-white/50 text-sm">{plan.description}</p>
              </div>

              {/* Price */}
              <div className="mb-6">
                {plan.priceMonthly !== null ? (
                  <>
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold">
                        ${isYearly && plan.priceYearly ? Math.round(plan.priceYearly / 12) : plan.priceMonthly}
                      </span>
                      <span className="text-white/50">/month</span>
                    </div>
                    {isYearly && plan.priceYearly && (
                      <div className="text-sm text-white/40 mt-1">
                        Billed ${plan.priceYearly} annually
                      </div>
                    )}
                  </>
                ) : (
                  <div className="flex items-center gap-2">
                    <Building2 className="w-6 h-6 text-white/60" />
                    <span className="text-2xl font-bold">Custom</span>
                  </div>
                )}
              </div>

              {/* CTA */}
              <Link
                href={plan.cta.href}
                className={cn(
                  "w-full text-center py-3 rounded-xl font-medium transition mb-6",
                  plan.highlighted
                    ? "bg-electric text-midnight hover:bg-electric/90"
                    : "bg-white/5 border border-white/10 hover:bg-white/10"
                )}
              >
                {plan.cta.text}
              </Link>

              {/* Features */}
              <ul className="space-y-3 flex-1">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm">
                    <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-white/70">{feature}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Enterprise CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-16 text-center"
        >
          <p className="text-white/60 mb-4">
            Need a custom solution for your enterprise?
          </p>
          <Link
            href="/contact"
            className="inline-flex items-center gap-2 text-electric hover:underline font-medium"
          >
            Contact our sales team
            <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>
      </div>
    </section>
  );
}

// Feature comparison for pricing page
interface FeatureComparisonProps {
  categories: {
    name: string;
    features: {
      name: string;
      free: boolean | string;
      starter: boolean | string;
      growth: boolean | string;
      enterprise: boolean | string;
    }[];
  }[];
}

export function FeatureComparison({ categories }: FeatureComparisonProps) {
  const renderValue = (value: boolean | string) => {
    if (value === true) {
      return <Check className="w-5 h-5 text-green-400 mx-auto" />;
    }
    if (value === false) {
      return <span className="text-white/30">—</span>;
    }
    return <span className="text-white/70 text-sm">{value}</span>;
  };

  return (
    <section className="py-16 px-6 border-t border-white/5">
      <div className="max-w-6xl mx-auto">
        <h3 className="text-2xl font-bold mb-8 text-center">
          Compare all features
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[800px]">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-4 pr-4 font-semibold">Feature</th>
                <th className="text-center py-4 px-4 font-semibold">Free</th>
                <th className="text-center py-4 px-4 font-semibold">Starter</th>
                <th className="text-center py-4 px-4 font-semibold bg-electric/5">
                  <div className="flex items-center justify-center gap-1">
                    <Sparkles className="w-4 h-4 text-electric" />
                    Growth
                  </div>
                </th>
                <th className="text-center py-4 pl-4 font-semibold">Enterprise</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((category, catIndex) => (
                <>
                  <tr key={`cat-${catIndex}`} className="bg-white/[0.02]">
                    <td
                      colSpan={5}
                      className="py-3 px-4 font-semibold text-white/80"
                    >
                      {category.name}
                    </td>
                  </tr>
                  {category.features.map((feature, featIndex) => (
                    <tr
                      key={`feat-${catIndex}-${featIndex}`}
                      className="border-b border-white/5"
                    >
                      <td className="py-4 pr-4 text-white/70">{feature.name}</td>
                      <td className="py-4 px-4 text-center">
                        {renderValue(feature.free)}
                      </td>
                      <td className="py-4 px-4 text-center">
                        {renderValue(feature.starter)}
                      </td>
                      <td className="py-4 px-4 text-center bg-electric/5">
                        {renderValue(feature.growth)}
                      </td>
                      <td className="py-4 pl-4 text-center">
                        {renderValue(feature.enterprise)}
                      </td>
                    </tr>
                  ))}
                </>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

