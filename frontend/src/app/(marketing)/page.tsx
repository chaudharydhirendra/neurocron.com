"use client";

import { motion } from "framer-motion";
import {
  Brain,
  Zap,
  BarChart3,
  Target,
  Sparkles,
  Megaphone,
  FileEdit,
  Users,
  Shield,
  TrendingUp,
  Clock,
  Bot,
  LineChart,
  Layers,
  Globe,
  MessageSquare,
  Lightbulb,
  Radar,
} from "lucide-react";
import {
  Hero,
  FeatureShowcase,
  FeatureGrid,
  Testimonials,
  LogoCloud,
  Stats,
  FAQ,
  ComparisonTable,
  TimeSavings,
  CTASection,
  HowItWorks,
} from "@/components/marketing";
import { AppScreenshot } from "@/components/app-screenshot";

// Feature data
const mainFeatures = [
  {
    id: "neuroplan",
    icon: Brain,
    title: "NeuroPlan",
    description: "AI generates your complete 12-month marketing strategy automatically. No more guesswork.",
    color: "from-purple-500 to-pink-500",
    highlights: [
      "12-month marketing roadmap",
      "Competitor analysis included",
      "Budget allocation suggestions",
      "Quarterly goals & KPIs",
    ],
    screenshot: "/screenshots/strategy.png",
  },
  {
    id: "autocron",
    icon: Zap,
    title: "AutoCron",
    description: "Executes campaigns across all platforms 24/7 without human intervention.",
    color: "from-electric to-cyan-400",
    highlights: [
      "Multi-platform execution",
      "Automatic optimization",
      "Real-time adjustments",
      "Zero manual work",
    ],
    screenshot: "/screenshots/dashboard.png",
  },
  {
    id: "insightcortex",
    icon: BarChart3,
    title: "InsightCortex",
    description: "Unified analytics from all channels with predictive intelligence.",
    color: "from-green-400 to-emerald-500",
    highlights: [
      "Cross-channel dashboards",
      "Predictive analytics",
      "Anomaly detection",
      "Custom reports",
    ],
    screenshot: "/screenshots/analytics.png",
  },
  {
    id: "contentforge",
    icon: FileEdit,
    title: "ContentForge",
    description: "AI content studio that creates, optimizes, and publishes across all channels.",
    color: "from-orange-400 to-red-500",
    highlights: [
      "Blog articles & social posts",
      "Email campaigns",
      "Ad creatives",
      "SEO optimization",
    ],
    screenshot: "/screenshots/content.png",
  },
];

const allModules = [
  { id: "neuroplan", icon: Brain, title: "NeuroPlan", description: "AI strategy generator", color: "from-purple-500 to-pink-500" },
  { id: "audiencegenome", icon: Users, title: "AudienceGenome", description: "Persona & segmentation engine", color: "from-blue-500 to-cyan-400" },
  { id: "brainspark", icon: Lightbulb, title: "BrainSpark", description: "Creative idea generator", color: "from-yellow-400 to-orange-500" },
  { id: "trendradar", icon: Radar, title: "TrendRadar", description: "Real-time trend monitoring", color: "from-green-400 to-teal-500" },
  { id: "battlestation", icon: Target, title: "BattleStation", description: "Competitive intelligence", color: "from-red-500 to-pink-500" },
  { id: "autocron", icon: Zap, title: "AutoCron", description: "Autonomous execution engine", color: "from-electric to-cyan-400" },
  { id: "contentforge", icon: FileEdit, title: "ContentForge", description: "AI content manufacturing", color: "from-orange-400 to-red-500" },
  { id: "adpilot", icon: Megaphone, title: "AdPilot", description: "Automated ad management", color: "from-purple-400 to-indigo-500" },
  { id: "flowbuilder", icon: Layers, title: "FlowBuilder", description: "Customer journey automation", color: "from-pink-400 to-rose-500" },
  { id: "insightcortex", icon: BarChart3, title: "InsightCortex", description: "Unified analytics hub", color: "from-green-400 to-emerald-500" },
  { id: "channelpulse", icon: Globe, title: "ChannelPulse", description: "Cross-channel control center", color: "from-blue-400 to-indigo-500" },
  { id: "neurocopilot", icon: Bot, title: "NeuroCopilot", description: "AI chat assistant", color: "from-electric to-purple-500" },
];

const testimonials = [
  {
    id: "1",
    content: "NeuroCron replaced our entire MarTech stack. We went from 8 tools to 1, and our results improved by 3x. The AI strategy generation alone saved us months of planning.",
    author: {
      name: "Sarah Chen",
      role: "VP of Marketing",
      company: "TechScale Inc.",
    },
    rating: 5,
  },
  {
    id: "2",
    content: "The autonomous execution is game-changing. I used to spend 20 hours a week on campaign management. Now NeuroCron handles it while I focus on strategy.",
    author: {
      name: "Marcus Johnson",
      role: "Growth Lead",
      company: "StartupFlow",
    },
    rating: 5,
  },
  {
    id: "3",
    content: "Finally, a platform that actually delivers on AI promises. The content generation is remarkably on-brand, and the analytics insights are actionable.",
    author: {
      name: "Elena Rodriguez",
      role: "CMO",
      company: "Elevate Media",
    },
    rating: 5,
  },
];

const integrationLogos = [
  { name: "Google", logo: <div className="text-2xl font-bold">Google</div> },
  { name: "Meta", logo: <div className="text-2xl font-bold">Meta</div> },
  { name: "LinkedIn", logo: <div className="text-2xl font-bold">LinkedIn</div> },
  { name: "HubSpot", logo: <div className="text-2xl font-bold">HubSpot</div> },
  { name: "Salesforce", logo: <div className="text-2xl font-bold">Salesforce</div> },
  { name: "Shopify", logo: <div className="text-2xl font-bold">Shopify</div> },
];

const comparisonRows = [
  { feature: "AI Strategy Generation", traditional: false, neurocron: true },
  { feature: "Autonomous Execution", traditional: false, neurocron: true },
  { feature: "Unified Analytics", traditional: "partial", neurocron: true },
  { feature: "Content Generation", traditional: "partial", neurocron: true },
  { feature: "24/7 Optimization", traditional: false, neurocron: true },
  { feature: "Single Dashboard", traditional: false, neurocron: true },
  { feature: "No Manual Work", traditional: false, neurocron: true },
  { feature: "Predictive Insights", traditional: "partial", neurocron: true },
];

const timeSavings = [
  { task: "Campaign Planning", traditional: "40 hours/month", neurocron: "2 hours/month", savings: "38 hours" },
  { task: "Content Creation", traditional: "30 hours/month", neurocron: "5 hours/month", savings: "25 hours" },
  { task: "Report Generation", traditional: "15 hours/month", neurocron: "0 hours/month", savings: "15 hours" },
  { task: "Platform Management", traditional: "20 hours/month", neurocron: "1 hour/month", savings: "19 hours" },
];

const faqs = [
  {
    question: "How does NeuroCron's AI actually work?",
    answer: "NeuroCron uses advanced language models to understand your business, analyze your data, and make intelligent marketing decisions. It learns from your past campaigns, industry benchmarks, and real-time market signals to continuously optimize performance.",
  },
  {
    question: "Can NeuroCron really replace my entire marketing team?",
    answer: "NeuroCron handles the execution, optimization, and analysis that typically require a team. However, you still need human oversight for strategic direction and creative approval. Think of it as multiplying your team's capacity by 10x, not replacing them entirely.",
  },
  {
    question: "How long does it take to see results?",
    answer: "Most customers see measurable improvements within the first 2 weeks. The AI needs about 7 days to learn your patterns and optimize accordingly. By month 2, you'll typically see 30-50% improvement in key metrics.",
  },
  {
    question: "Is my data secure with NeuroCron?",
    answer: "Absolutely. We're SOC 2 Type II certified, GDPR compliant, and use enterprise-grade encryption. Your data is never shared or used to train our models. We offer data residency options for enterprise customers.",
  },
  {
    question: "What platforms does NeuroCron integrate with?",
    answer: "We integrate with 50+ platforms including Google Ads, Meta Ads, LinkedIn, Twitter, HubSpot, Salesforce, Shopify, and more. All integrations use OAuth for secure, one-click connections.",
  },
  {
    question: "Can I try NeuroCron before committing?",
    answer: "Yes! We offer a 14-day free trial with full access to all features. No credit card required. You can also book a personalized demo with our team to see how NeuroCron would work for your specific use case.",
  },
];

const howItWorksSteps = [
  {
    step: "1",
    title: "Connect",
    description: "Link your ad accounts, social profiles, and marketing tools in one click with secure OAuth.",
  },
  {
    step: "2",
    title: "Configure",
    description: "Tell NeuroCron your goals and constraints. Our AI creates a personalized marketing strategy.",
  },
  {
    step: "3",
    title: "Automate",
    description: "Watch NeuroCron execute, optimize, and report automatically. Just review and approve.",
  },
];

export default function HomePage() {
  return (
    <>
      {/* Hero Section */}
      <Hero
        badge="The Future of Marketing is Autonomous"
        title={
          <>
            The Autonomous
            <br />
            <span className="gradient-text">Marketing Brain</span>
          </>
        }
        subtitle="AI that plans, executes, audits, and optimizes your entire marketing — automatically. One platform. Zero vendor portals. Infinite possibilities."
        primaryCta={{ text: "Start Free Trial", href: "/register" }}
        secondaryCta={{ text: "Watch Demo", href: "/demo" }}
        stats={[
          { value: "32", label: "AI Modules" },
          { value: "24/7", label: "Autonomous" },
          { value: "50+", label: "Integrations" },
        ]}
      />

      {/* Logo Cloud */}
      <LogoCloud
        title="Integrates with the tools you already use"
        logos={integrationLogos}
      />

      {/* Problem Section */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Marketing Shouldn&apos;t Feel Like This
            </h2>
            <p className="text-xl text-white/60">
              Sound familiar?
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-4">
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
                className="flex items-center gap-3 p-5 rounded-xl bg-red-500/10 border border-red-500/20"
              >
                <div className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
                <span className="text-white/80">{problem}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Showcase */}
      <FeatureShowcase
        title="NeuroCron Replaces It All"
        subtitle="One login. Zero vendor portals. Marketing that runs itself."
        features={mainFeatures}
        ctaText="Explore All 32 Modules"
        ctaHref="/features"
      />

      {/* Product Screenshot */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              See It In Action
            </h2>
            <p className="text-xl text-white/60">
              A unified command center for all your marketing
            </p>
          </motion.div>

          <AppScreenshot
            src="/screenshots/dashboard.png"
            alt="NeuroCron Dashboard"
            priority
            glowColor="electric"
          />
        </div>
      </section>

      {/* Stats */}
      <Stats
        stats={[
          { value: "10x", label: "Faster Execution", description: "vs manual workflows" },
          { value: "40+", label: "Hours Saved", description: "per month average" },
          { value: "3x", label: "Better ROAS", description: "with AI optimization" },
          { value: "99.9%", label: "Uptime", description: "enterprise reliability" },
        ]}
      />

      {/* All Modules Grid */}
      <FeatureGrid
        title="32 Powerful Modules"
        subtitle="Every module works together autonomously to run your marketing"
        features={allModules}
      />

      {/* How It Works */}
      <HowItWorks
        title="How It Works"
        steps={howItWorksSteps}
      />

      {/* Comparison Table */}
      <ComparisonTable
        title="NeuroCron vs Traditional Marketing"
        subtitle="See why teams are switching to autonomous marketing"
        rows={comparisonRows}
      />

      {/* Time Savings */}
      <TimeSavings
        title="Save 40+ Hours Every Month"
        subtitle="See how much time NeuroCron saves on common marketing tasks"
        savings={timeSavings}
      />

      {/* Testimonials */}
      <Testimonials
        title="Loved by Marketing Teams"
        subtitle="See what our customers are saying"
        testimonials={testimonials}
      />

      {/* Security Section */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-green-500/10 mb-6">
              <Shield className="w-8 h-8 text-green-400" />
            </div>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Enterprise-Grade Security
            </h2>
            <p className="text-xl text-white/60">
              Your data is protected with bank-level security
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { title: "SOC 2 Type II", description: "Certified compliant with rigorous security standards" },
              { title: "GDPR Ready", description: "Full compliance with European data protection regulations" },
              { title: "256-bit Encryption", description: "All data encrypted at rest and in transit" },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="card text-center"
              >
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-white/60">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <FAQ faqs={faqs} />

      {/* Final CTA */}
      <CTASection
        variant="gradient"
        title="Ready for Autonomous Marketing?"
        subtitle="Join 500+ marketing teams who've already made the switch. Start your free trial today."
        primaryCta={{ text: "Start Free Trial", href: "/register" }}
        secondaryCta={{ text: "Book a Demo", href: "/demo" }}
        features={["14-day free trial", "No credit card required", "Cancel anytime"]}
      />
    </>
  );
}

