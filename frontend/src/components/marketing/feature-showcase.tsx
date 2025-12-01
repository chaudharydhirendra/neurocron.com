"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, LucideIcon } from "lucide-react";
import { AppScreenshot } from "@/components/app-screenshot";
import { cn } from "@/lib/utils";

interface Feature {
  id: string;
  icon: LucideIcon;
  title: string;
  description: string;
  screenshot?: string;
  color: string;
  highlights?: string[];
}

interface FeatureShowcaseProps {
  title: string;
  subtitle: string;
  features: Feature[];
  ctaText?: string;
  ctaHref?: string;
}

export function FeatureShowcase({
  title,
  subtitle,
  features,
  ctaText = "Explore All Features",
  ctaHref = "/features",
}: FeatureShowcaseProps) {
  const [activeFeature, setActiveFeature] = useState(features[0]);

  return (
    <section className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">{title}</h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">{subtitle}</p>
        </motion.div>

        {/* Feature Tabs + Screenshot */}
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Feature List */}
          <div className="space-y-4 order-2 lg:order-1">
            {features.map((feature, index) => (
              <motion.button
                key={feature.id}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                onClick={() => setActiveFeature(feature)}
                className={cn(
                  "w-full text-left p-6 rounded-2xl border transition-all duration-300",
                  activeFeature.id === feature.id
                    ? "bg-white/5 border-electric/30 shadow-lg shadow-electric/10"
                    : "bg-transparent border-white/5 hover:border-white/10"
                )}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={cn(
                      "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors",
                      activeFeature.id === feature.id
                        ? `bg-gradient-to-br ${feature.color}`
                        : "bg-white/5"
                    )}
                  >
                    <feature.icon
                      className={cn(
                        "w-6 h-6",
                        activeFeature.id === feature.id
                          ? "text-white"
                          : "text-white/60"
                      )}
                    />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold mb-1">{feature.title}</h3>
                    <p className="text-white/60 text-sm">{feature.description}</p>
                    
                    {/* Highlights */}
                    <AnimatePresence>
                      {activeFeature.id === feature.id && feature.highlights && (
                        <motion.ul
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-4 space-y-2"
                        >
                          {feature.highlights.map((highlight, i) => (
                            <li
                              key={i}
                              className="flex items-center gap-2 text-sm text-white/80"
                            >
                              <div className="w-1.5 h-1.5 rounded-full bg-electric" />
                              {highlight}
                            </li>
                          ))}
                        </motion.ul>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
              </motion.button>
            ))}

            {/* CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="pt-4"
            >
              <Link
                href={ctaHref}
                className="inline-flex items-center gap-2 text-electric hover:underline font-medium"
              >
                {ctaText}
                <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>
          </div>

          {/* Screenshot */}
          <div className="order-1 lg:order-2">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeFeature.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3 }}
              >
                {activeFeature.screenshot ? (
                  <AppScreenshot
                    src={activeFeature.screenshot}
                    alt={activeFeature.title}
                    animate={false}
                  />
                ) : (
                  <div className="aspect-video rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 flex items-center justify-center">
                    <div
                      className={cn(
                        "w-24 h-24 rounded-2xl bg-gradient-to-br flex items-center justify-center",
                        activeFeature.color
                      )}
                    >
                      <activeFeature.icon className="w-12 h-12 text-white" />
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
}

interface FeatureGridProps {
  title: string;
  subtitle: string;
  features: Feature[];
}

export function FeatureGrid({ title, subtitle, features }: FeatureGridProps) {
  return (
    <section className="py-24 px-6 bg-midnight-50/30">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">{title}</h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">{subtitle}</p>
        </motion.div>

        {/* Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              className="card group hover:border-electric/30 transition-all duration-300"
            >
              <div
                className={cn(
                  "w-14 h-14 rounded-2xl bg-gradient-to-br flex items-center justify-center mb-4 group-hover:scale-110 transition-transform",
                  feature.color
                )}
              >
                <feature.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-white/60">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

