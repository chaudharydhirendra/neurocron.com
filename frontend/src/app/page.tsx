"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Brain,
  Zap,
  BarChart3,
  Target,
  Sparkles,
  ArrowRight,
  Check,
  Play,
  ChevronRight,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "NeuroPlan",
    description: "AI generates your complete 12-month marketing strategy automatically.",
    color: "from-purple-500 to-pink-500",
  },
  {
    icon: Zap,
    title: "AutoCron",
    description: "Executes campaigns across all platforms without human intervention.",
    color: "from-electric to-cyan-400",
  },
  {
    icon: BarChart3,
    title: "InsightCortex",
    description: "Unified analytics from all channels with predictive intelligence.",
    color: "from-green-400 to-emerald-500",
  },
  {
    icon: Target,
    title: "AudienceGenome",
    description: "Deep customer personas built from millions of data points.",
    color: "from-orange-400 to-red-500",
  },
];

const modules = [
  { name: "NeuroPlan", category: "Strategy" },
  { name: "AudienceGenome", category: "Strategy" },
  { name: "BrainSpark", category: "Creative" },
  { name: "TrendRadar", category: "Intelligence" },
  { name: "BattleStation", category: "Competitive" },
  { name: "SimulatorX", category: "Prediction" },
  { name: "AutoCron", category: "Execution" },
  { name: "ContentForge", category: "Content" },
  { name: "AdPilot", category: "Advertising" },
  { name: "FlowBuilder", category: "Automation" },
  { name: "AuditX", category: "Analytics" },
  { name: "InsightCortex", category: "Analytics" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-midnight neural-bg">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-neural-gradient flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold">NeuroCron</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-white/70 hover:text-white transition">
              Features
            </Link>
            <Link href="#modules" className="text-white/70 hover:text-white transition">
              Modules
            </Link>
            <Link href="#pricing" className="text-white/70 hover:text-white transition">
              Pricing
            </Link>
          </div>
          
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-white/70 hover:text-white transition">
              Log in
            </Link>
            <Link href="/register" className="btn-primary text-sm">
              Start Free Trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 bg-hero-glow opacity-50" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-electric/10 rounded-full blur-[120px]" />
        
        <div className="relative max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8">
              <Sparkles className="w-4 h-4 text-electric" />
              <span className="text-sm">The Future of Marketing is Autonomous</span>
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
          >
            The Autonomous
            <br />
            <span className="gradient-text">Marketing Brain</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-white/60 mb-10 max-w-2xl mx-auto text-balance"
          >
            AI that plans, executes, audits, and optimizes your entire marketing — automatically.
            One platform. Zero vendor portals. Infinite possibilities.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link href="/register" className="btn-primary flex items-center gap-2 text-lg">
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </Link>
            <button className="btn-secondary flex items-center gap-2 text-lg">
              <Play className="w-5 h-5" />
              Watch Demo
            </button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto"
          >
            {[
              { value: "32", label: "AI Modules" },
              { value: "24/7", label: "Autonomous" },
              { value: "∞", label: "Scalability" },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-3xl font-bold gradient-text">{stat.value}</div>
                <div className="text-white/50 text-sm mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Marketing Shouldn&apos;t Feel Like This
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mt-10">
            {[
              "Jumping between 10+ dashboards daily",
              "Manually creating and scheduling content",
              "Guessing what campaigns will work",
              "Spending hours on reports",
              "Missing optimization opportunities",
              "Paying for disconnected tools",
            ].map((problem, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20"
              >
                <div className="w-2 h-2 rounded-full bg-red-500" />
                <span className="text-white/80">{problem}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              NeuroCron <span className="gradient-text">Replaces It All</span>
            </h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              One login. Zero vendor portals. Marketing that runs itself.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="card group hover:border-electric/30 transition-all duration-300"
              >
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-white/60">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Modules Grid */}
      <section id="modules" className="py-20 px-6 bg-midnight-50/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              32 <span className="gradient-text">Powerful Modules</span>
            </h2>
            <p className="text-white/60">
              Every module works together autonomously to run your marketing.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-3">
            {modules.map((module, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.03 }}
                className="px-4 py-2 rounded-xl glass hover:border-electric/30 transition-all cursor-pointer group"
              >
                <span className="text-white/80 group-hover:text-white transition">
                  {module.name}
                </span>
                <span className="ml-2 text-xs text-white/40">{module.category}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Connect", desc: "Link your ad accounts, social profiles, and tools in one click." },
              { step: "2", title: "Configure", desc: "Tell NeuroCron your goals. Our AI creates your strategy." },
              { step: "3", title: "Watch It Work", desc: "NeuroCron executes, optimizes, and reports automatically." },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="text-center"
              >
                <div className="w-16 h-16 mx-auto rounded-full bg-neural-gradient flex items-center justify-center text-2xl font-bold mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-white/60">{item.desc}</p>
                {i < 2 && (
                  <ChevronRight className="hidden md:block w-6 h-6 text-white/30 absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="card text-center p-12 neural-glow"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready for <span className="gradient-text">Autonomous Marketing</span>?
            </h2>
            <p className="text-white/60 mb-8 max-w-xl mx-auto">
              Join the future of marketing. Let AI handle the execution while you focus on growth.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/register" className="btn-primary flex items-center gap-2 text-lg">
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link href="/demo" className="btn-secondary flex items-center gap-2 text-lg">
                Book a Demo
              </Link>
            </div>
            <div className="flex items-center justify-center gap-6 mt-8 text-sm text-white/50">
              <span className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-400" />
                14-day free trial
              </span>
              <span className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-400" />
                No credit card required
              </span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-neural-gradient flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold">NeuroCron</span>
            </div>
            <div className="flex items-center gap-8 text-sm text-white/50">
              <Link href="/privacy" className="hover:text-white transition">Privacy</Link>
              <Link href="/terms" className="hover:text-white transition">Terms</Link>
              <Link href="/contact" className="hover:text-white transition">Contact</Link>
            </div>
            <div className="text-sm text-white/30">
              © 2024 NeuroCron. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

