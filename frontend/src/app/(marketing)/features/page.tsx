import { Metadata } from "next";
import Link from "next/link";
import {
  Brain,
  Zap,
  BarChart3,
  Target,
  Users,
  FileEdit,
  Megaphone,
  Layers,
  Bot,
  Radar,
  Lightbulb,
  Shield,
  Globe,
  LineChart,
  MessageSquare,
  TrendingUp,
  Calendar,
  Mail,
  Search,
  Eye,
  ArrowRight,
} from "lucide-react";
import { FeatureGrid } from "@/components/marketing/feature-showcase";
import { CTASection } from "@/components/marketing/cta-section";

export const metadata: Metadata = {
  title: "Features",
  description: "Explore all 32 AI-powered modules in NeuroCron. From strategy generation to autonomous execution, discover how NeuroCron transforms your marketing.",
  openGraph: {
    title: "Features | NeuroCron",
    description: "Explore all 32 AI-powered modules that make up the autonomous marketing brain.",
  },
};

const suites = [
  {
    id: "strategy",
    name: "Strategy & Planning Suite",
    description: "AI-powered strategy generation and audience intelligence",
    icon: Brain,
    color: "from-purple-500 to-pink-500",
    modules: [
      {
        id: "neuroplan",
        icon: Brain,
        title: "NeuroPlan",
        description: "Automatically builds complete 12-month marketing strategies with quarterly goals, budget allocations, and channel priorities.",
        color: "from-purple-500 to-pink-500",
      },
      {
        id: "audiencegenome",
        icon: Users,
        title: "AudienceGenome",
        description: "Creates deep customer personas with motivations, pain points, and buying triggers based on real behavioral data.",
        color: "from-blue-500 to-cyan-400",
      },
      {
        id: "brainspark",
        icon: Lightbulb,
        title: "BrainSpark",
        description: "Generates creative campaign concepts, slogans, ad angles, and content ideas tailored to your audience.",
        color: "from-yellow-400 to-orange-500",
      },
      {
        id: "trendradar",
        icon: Radar,
        title: "TrendRadar",
        description: "Monitors real-time trends across social platforms and automatically triggers relevant campaigns.",
        color: "from-green-400 to-teal-500",
      },
      {
        id: "battlestation",
        icon: Target,
        title: "BattleStation",
        description: "Tracks competitors' marketing moves, analyzes their strategies, and generates counter-positioning.",
        color: "from-red-500 to-pink-500",
      },
      {
        id: "simulatorx",
        icon: LineChart,
        title: "SimulatorX",
        description: "Predicts campaign outcomes before you spend. Run what-if scenarios to optimize budget allocation.",
        color: "from-indigo-500 to-purple-500",
      },
    ],
  },
  {
    id: "execution",
    name: "Execution & Automation Suite",
    description: "Autonomous campaign execution across all channels",
    icon: Zap,
    color: "from-electric to-cyan-400",
    modules: [
      {
        id: "autocron",
        icon: Zap,
        title: "AutoCron",
        description: "The core execution engine. Runs campaigns, posts content, optimizes ads, and adjusts budgets 24/7 without intervention.",
        color: "from-electric to-cyan-400",
      },
      {
        id: "contentforge",
        icon: FileEdit,
        title: "ContentForge",
        description: "Full AI content studio. Creates blogs, social posts, emails, ad copy, and landing pages with your brand voice.",
        color: "from-orange-400 to-red-500",
      },
      {
        id: "adpilot",
        icon: Megaphone,
        title: "AdPilot",
        description: "Creates, publishes, and optimizes ads across Google, Meta, LinkedIn, and TikTok automatically.",
        color: "from-purple-400 to-indigo-500",
      },
      {
        id: "flowbuilder",
        icon: Layers,
        title: "FlowBuilder",
        description: "Visual drag-and-drop automation builder for customer journeys, lead nurturing, and lifecycle campaigns.",
        color: "from-pink-400 to-rose-500",
      },
      {
        id: "channelpulse",
        icon: Globe,
        title: "ChannelPulse",
        description: "Unified control center for all channels. Manage social, ads, and email from a single dashboard.",
        color: "from-blue-400 to-indigo-500",
      },
      {
        id: "launchpad",
        icon: Calendar,
        title: "LaunchPad",
        description: "Pre-built campaign templates for product launches, holidays, and common marketing scenarios.",
        color: "from-green-400 to-emerald-500",
      },
    ],
  },
  {
    id: "analytics",
    name: "Analytics & Intelligence Suite",
    description: "Unified insights and predictive analytics",
    icon: BarChart3,
    color: "from-green-400 to-emerald-500",
    modules: [
      {
        id: "insightcortex",
        icon: BarChart3,
        title: "InsightCortex",
        description: "Unified analytics hub that aggregates data from all platforms with predictive forecasting.",
        color: "from-green-400 to-emerald-500",
      },
      {
        id: "auditx",
        icon: Search,
        title: "AuditX",
        description: "One-click marketing audit. Analyzes SEO, ads, content, and campaigns with actionable fixes.",
        color: "from-yellow-400 to-amber-500",
      },
      {
        id: "scoreboard",
        icon: TrendingUp,
        title: "ScoreBoard",
        description: "Automated executive reporting. Generates weekly, monthly, and quarterly reports automatically.",
        color: "from-blue-400 to-cyan-500",
      },
      {
        id: "customerdna",
        icon: Eye,
        title: "CustomerDNA",
        description: "Unified customer data platform. Single view of every customer touchpoint and interaction.",
        color: "from-purple-400 to-pink-500",
      },
      {
        id: "revenuelink",
        icon: LineChart,
        title: "RevenueLink",
        description: "Marketing-to-revenue attribution. See exactly which campaigns drive actual business results.",
        color: "from-green-500 to-teal-500",
      },
      {
        id: "behaviormind",
        icon: Users,
        title: "BehaviorMind",
        description: "Deep user behavior analytics with heatmaps, session replays, and conversion path analysis.",
        color: "from-orange-400 to-red-500",
      },
    ],
  },
  {
    id: "intelligence",
    name: "Platform Intelligence Suite",
    description: "AI assistants and brand protection",
    icon: Bot,
    color: "from-electric to-purple-500",
    modules: [
      {
        id: "neurocopilot",
        icon: Bot,
        title: "NeuroCopilot",
        description: "ChatGPT-like interface for your entire marketing. Ask questions, give commands, get insights.",
        color: "from-electric to-purple-500",
      },
      {
        id: "crisisshield",
        icon: Shield,
        title: "CrisisShield",
        description: "Real-time brand monitoring. Detects sentiment shifts and auto-pauses campaigns during PR issues.",
        color: "from-red-500 to-orange-500",
      },
      {
        id: "globalreach",
        icon: Globe,
        title: "GlobalReach",
        description: "Multi-language campaign management with AI translation and cultural adaptation.",
        color: "from-blue-400 to-cyan-500",
      },
      {
        id: "retentionai",
        icon: Users,
        title: "RetentionAI",
        description: "Predicts churn risk and automatically triggers retention campaigns for at-risk customers.",
        color: "from-green-400 to-teal-500",
      },
      {
        id: "viralengine",
        icon: TrendingUp,
        title: "ViralEngine",
        description: "Built-in referral program and gamification tools to turn customers into advocates.",
        color: "from-pink-400 to-purple-500",
      },
      {
        id: "projecthub",
        icon: Layers,
        title: "ProjectHub",
        description: "AI-powered marketing project management with auto-prioritization and team coordination.",
        color: "from-indigo-400 to-blue-500",
      },
    ],
  },
];

export default function FeaturesPage() {
  return (
    <div className="pt-32">
      {/* Hero */}
      <section className="py-16 px-6 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            32 <span className="gradient-text">Powerful Modules</span>
          </h1>
          <p className="text-xl text-white/60 mb-8">
            Every module works together autonomously to plan, execute, and optimize
            your marketing. No more tool sprawl. No more manual work.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/register" className="btn-primary flex items-center gap-2">
              Start Free Trial
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/demo" className="btn-secondary">
              Watch Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Suites */}
      {suites.map((suite) => (
        <section
          key={suite.id}
          id={suite.id}
          className="py-24 px-6 scroll-mt-24"
        >
          <div className="max-w-7xl mx-auto">
            {/* Suite Header */}
            <div className="flex items-center gap-4 mb-4">
              <div
                className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${suite.color} flex items-center justify-center`}
              >
                <suite.icon className="w-7 h-7 text-white" />
              </div>
              <div>
                <h2 className="text-3xl font-bold">{suite.name}</h2>
                <p className="text-white/60">{suite.description}</p>
              </div>
            </div>

            {/* Module Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
              {suite.modules.map((module) => (
                <div
                  key={module.id}
                  className="card group hover:border-electric/30 transition-all duration-300"
                >
                  <div
                    className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${module.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                  >
                    <module.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{module.title}</h3>
                  <p className="text-white/60">{module.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      ))}

      {/* Integrations */}
      <section className="py-24 px-6 bg-midnight-50/30">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4">
            50+ <span className="gradient-text">Integrations</span>
          </h2>
          <p className="text-xl text-white/60 mb-12">
            Connect all your marketing tools in one click
          </p>

          <div className="grid grid-cols-4 md:grid-cols-8 gap-4">
            {[
              "Google Ads",
              "Meta Ads",
              "LinkedIn",
              "Twitter",
              "TikTok",
              "HubSpot",
              "Salesforce",
              "Shopify",
              "Mailchimp",
              "Stripe",
              "Slack",
              "Zapier",
              "Analytics",
              "YouTube",
              "Pinterest",
              "WordPress",
            ].map((integration) => (
              <div
                key={integration}
                className="aspect-square rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-xs text-white/60 hover:border-electric/30 hover:text-white transition-all"
              >
                {integration}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        variant="gradient"
        title="Experience the Full Platform"
        subtitle="Start your 14-day free trial and see all modules in action"
        primaryCta={{ text: "Start Free Trial", href: "/register" }}
        secondaryCta={{ text: "Book a Demo", href: "/demo" }}
        features={["All 32 modules included", "No credit card required", "Full support"]}
      />
    </div>
  );
}

