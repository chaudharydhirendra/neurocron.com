"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Check, Sparkles, Calendar } from "lucide-react";

interface CTASectionProps {
  title: string;
  subtitle?: string;
  primaryCta: {
    text: string;
    href: string;
  };
  secondaryCta?: {
    text: string;
    href: string;
  };
  features?: string[];
  variant?: "default" | "gradient" | "minimal";
}

export function CTASection({
  title,
  subtitle,
  primaryCta,
  secondaryCta,
  features,
  variant = "default",
}: CTASectionProps) {
  if (variant === "minimal") {
    return (
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-4xl font-bold mb-6"
          >
            {title}
          </motion.h2>
          {subtitle && (
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-xl text-white/60 mb-8"
            >
              {subtitle}
            </motion.p>
          )}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              href={primaryCta.href}
              className="btn-primary flex items-center gap-2"
            >
              {primaryCta.text}
              <ArrowRight className="w-4 h-4" />
            </Link>
            {secondaryCta && (
              <Link
                href={secondaryCta.href}
                className="btn-secondary flex items-center gap-2"
              >
                {secondaryCta.text}
              </Link>
            )}
          </motion.div>
        </div>
      </section>
    );
  }

  if (variant === "gradient") {
    return (
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="relative overflow-hidden rounded-3xl bg-neural-gradient p-12 md:p-16 text-center"
          >
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `radial-gradient(circle at 2px 2px, white 1px, transparent 0)`,
                backgroundSize: '32px 32px',
              }} />
            </div>

            <div className="relative">
              <motion.div
                initial={{ scale: 0.8 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white/20 mb-8"
              >
                <Sparkles className="w-8 h-8 text-white" />
              </motion.div>

              <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
                {title}
              </h2>

              {subtitle && (
                <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
                  {subtitle}
                </p>
              )}

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
                <Link
                  href={primaryCta.href}
                  className="bg-white text-midnight px-8 py-4 rounded-xl font-medium hover:bg-white/90 transition flex items-center gap-2"
                >
                  {primaryCta.text}
                  <ArrowRight className="w-5 h-5" />
                </Link>
                {secondaryCta && (
                  <Link
                    href={secondaryCta.href}
                    className="bg-white/10 text-white px-8 py-4 rounded-xl font-medium hover:bg-white/20 transition border border-white/20 flex items-center gap-2"
                  >
                    <Calendar className="w-5 h-5" />
                    {secondaryCta.text}
                  </Link>
                )}
              </div>

              {features && (
                <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-white/80">
                  {features.map((feature, i) => (
                    <span key={i} className="flex items-center gap-2">
                      <Check className="w-4 h-4" />
                      {feature}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </section>
    );
  }

  // Default variant
  return (
    <section className="py-24 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="card text-center p-12 neural-glow"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            {title}
          </h2>
          {subtitle && (
            <p className="text-white/60 mb-8 max-w-xl mx-auto">
              {subtitle}
            </p>
          )}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href={primaryCta.href}
              className="btn-primary flex items-center gap-2 text-lg"
            >
              {primaryCta.text}
              <ArrowRight className="w-5 h-5" />
            </Link>
            {secondaryCta && (
              <Link
                href={secondaryCta.href}
                className="btn-secondary flex items-center gap-2 text-lg"
              >
                {secondaryCta.text}
              </Link>
            )}
          </div>
          {features && (
            <div className="flex items-center justify-center gap-6 mt-8 text-sm text-white/50">
              {features.map((feature, i) => (
                <span key={i} className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-400" />
                  {feature}
                </span>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </section>
  );
}

// How It Works section
interface HowItWorksProps {
  title?: string;
  steps: {
    step: string;
    title: string;
    description: string;
    icon?: React.ReactNode;
  }[];
}

export function HowItWorks({
  title = "How It Works",
  steps,
}: HowItWorksProps) {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-4xl md:text-5xl font-bold mb-16 text-center"
        >
          {title}
        </motion.h2>

        <div className="relative">
          {/* Connection line */}
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-electric/30 to-transparent -translate-y-1/2" />

          <div className="grid md:grid-cols-3 gap-12">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.15 }}
                className="relative text-center"
              >
                <div className="relative z-10 w-20 h-20 mx-auto rounded-full bg-neural-gradient flex items-center justify-center text-3xl font-bold mb-6 shadow-lg shadow-electric/20">
                  {step.icon || step.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-white/60">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

