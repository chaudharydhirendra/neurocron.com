import { Metadata } from "next";
import Link from "next/link";
import {
  BookOpen,
  Zap,
  Settings,
  Code,
  HelpCircle,
  ArrowRight,
  Search,
  FileText,
  Video,
  MessageSquare,
  Layers,
  Shield,
  Globe,
  Brain,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Documentation",
  description: "Learn how to get the most out of NeuroCron. Guides, tutorials, API reference, and best practices.",
  openGraph: {
    title: "Documentation | NeuroCron",
    description: "Comprehensive guides and API reference for NeuroCron.",
  },
};

interface DocLink {
  title: string;
  href: string;
  time?: string;
  badge?: string;
}

interface DocSection {
  title: string;
  icon: typeof Zap;
  description: string;
  color: string;
  links: DocLink[];
}

const sections: DocSection[] = [
  {
    title: "Getting Started",
    icon: Zap,
    description: "New to NeuroCron? Start here.",
    color: "from-electric to-cyan-400",
    links: [
      { title: "Quick Start Guide", href: "/docs/quick-start", time: "5 min" },
      { title: "Account Setup", href: "/docs/account-setup", time: "3 min" },
      { title: "Connecting Integrations", href: "/docs/integrations", time: "10 min" },
      { title: "Creating Your First Campaign", href: "/docs/first-campaign", time: "8 min" },
    ],
  },
  {
    title: "Core Modules",
    icon: Layers,
    description: "Deep dives into each NeuroCron module.",
    color: "from-purple-500 to-pink-500",
    links: [
      { title: "NeuroPlan: Strategy Generation", href: "/docs/neuroplan" },
      { title: "AutoCron: Autonomous Execution", href: "/docs/autocron" },
      { title: "ContentForge: AI Content Creation", href: "/docs/contentforge" },
      { title: "InsightCortex: Analytics Hub", href: "/docs/insightcortex" },
    ],
  },
  {
    title: "Integrations",
    icon: Globe,
    description: "Connect your marketing stack.",
    color: "from-green-400 to-emerald-500",
    links: [
      { title: "Google Ads Integration", href: "/docs/integrations/google-ads" },
      { title: "Meta Ads Integration", href: "/docs/integrations/meta" },
      { title: "LinkedIn Integration", href: "/docs/integrations/linkedin" },
      { title: "All Integrations", href: "/docs/integrations", badge: "50+" },
    ],
  },
  {
    title: "API Reference",
    icon: Code,
    description: "Build custom integrations.",
    color: "from-orange-400 to-red-500",
    links: [
      { title: "Authentication", href: "/docs/api/auth" },
      { title: "Campaigns API", href: "/docs/api/campaigns" },
      { title: "Content API", href: "/docs/api/content" },
      { title: "Webhooks", href: "/docs/api/webhooks" },
    ],
  },
  {
    title: "Best Practices",
    icon: Brain,
    description: "Get the most from NeuroCron.",
    color: "from-blue-400 to-indigo-500",
    links: [
      { title: "Optimizing AI Outputs", href: "/docs/best-practices/ai-optimization" },
      { title: "Campaign Strategy Tips", href: "/docs/best-practices/campaigns" },
      { title: "Content Quality Guidelines", href: "/docs/best-practices/content" },
      { title: "Automation Workflows", href: "/docs/best-practices/automation" },
    ],
  },
  {
    title: "Security & Compliance",
    icon: Shield,
    description: "Enterprise security documentation.",
    color: "from-red-400 to-pink-500",
    links: [
      { title: "Security Overview", href: "/docs/security" },
      { title: "GDPR Compliance", href: "/docs/security/gdpr" },
      { title: "SOC 2 Certification", href: "/docs/security/soc2" },
      { title: "Data Handling", href: "/docs/security/data" },
    ],
  },
];

const popularArticles = [
  { title: "Quick Start Guide", views: "12.5k", href: "/docs/quick-start" },
  { title: "API Authentication", views: "8.2k", href: "/docs/api/auth" },
  { title: "Connecting Google Ads", views: "6.8k", href: "/docs/integrations/google-ads" },
  { title: "NeuroPlan Strategy Generation", views: "5.4k", href: "/docs/neuroplan" },
  { title: "FlowBuilder Automations", views: "4.9k", href: "/docs/flowbuilder" },
];

export default function DocsPage() {
  return (
    <div className="pt-32">
      {/* Hero */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-electric/10 mb-6">
            <BookOpen className="w-8 h-8 text-electric" />
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="gradient-text">Documentation</span>
          </h1>
          <p className="text-xl text-white/60 mb-8">
            Everything you need to build and scale with NeuroCron
          </p>

          {/* Search */}
          <div className="relative max-w-xl mx-auto">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type="text"
              placeholder="Search documentation..."
              className="w-full pl-12 pr-4 py-4 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none focus:ring-1 focus:ring-electric/50 transition text-lg"
            />
            <kbd className="absolute right-4 top-1/2 -translate-y-1/2 px-2 py-1 rounded bg-white/10 text-xs text-white/40">
              ⌘K
            </kbd>
          </div>
        </div>
      </section>

      {/* Quick Links */}
      <section className="px-6 mb-16">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-4">
            <Link
              href="/docs/quick-start"
              className="card flex items-center gap-4 hover:border-electric/30 transition"
            >
              <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                <Zap className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <div className="font-semibold">Quick Start</div>
                <div className="text-sm text-white/50">Get up and running in 5 minutes</div>
              </div>
            </Link>
            <Link
              href="/docs/api"
              className="card flex items-center gap-4 hover:border-electric/30 transition"
            >
              <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center">
                <Code className="w-6 h-6 text-orange-400" />
              </div>
              <div>
                <div className="font-semibold">API Reference</div>
                <div className="text-sm text-white/50">Build custom integrations</div>
              </div>
            </Link>
            <Link
              href="/docs/tutorials"
              className="card flex items-center gap-4 hover:border-electric/30 transition"
            >
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                <Video className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <div className="font-semibold">Video Tutorials</div>
                <div className="text-sm text-white/50">Step-by-step walkthroughs</div>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Sections Grid */}
      <section className="px-6 pb-16">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sections.map((section) => (
              <div key={section.title} className="card">
                <div className="flex items-center gap-3 mb-4">
                  <div
                    className={`w-10 h-10 rounded-xl bg-gradient-to-br ${section.color} flex items-center justify-center`}
                  >
                    <section.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{section.title}</h3>
                    <p className="text-sm text-white/50">{section.description}</p>
                  </div>
                </div>
                <ul className="space-y-2">
                  {section.links.map((link) => (
                    <li key={link.href}>
                      <Link
                        href={link.href}
                        className="flex items-center justify-between py-2 text-white/70 hover:text-electric transition group"
                      >
                        <span className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          {link.title}
                        </span>
                        <span className="flex items-center gap-2">
                          {link.time && (
                            <span className="text-xs text-white/40">{link.time}</span>
                          )}
                          {link.badge && (
                            <span className="text-xs px-2 py-0.5 rounded bg-electric/10 text-electric">
                              {link.badge}
                            </span>
                          )}
                          <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all" />
                        </span>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Articles */}
      <section className="px-6 py-16 bg-midnight-50/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 text-center">Popular Articles</h2>
          <div className="space-y-3">
            {popularArticles.map((article, index) => (
              <Link
                key={article.href}
                href={article.href}
                className="flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 transition group"
              >
                <div className="flex items-center gap-4">
                  <span className="text-white/30 font-mono text-sm w-6">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className="font-medium group-hover:text-electric transition">
                    {article.title}
                  </span>
                </div>
                <span className="text-sm text-white/40">{article.views} views</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Help CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-purple-500/10 mb-6">
            <MessageSquare className="w-8 h-8 text-purple-400" />
          </div>
          <h2 className="text-3xl font-bold mb-4">Need Help?</h2>
          <p className="text-white/60 mb-8">
            Can&apos;t find what you&apos;re looking for? Our support team is here to help.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/contact" className="btn-primary flex items-center gap-2">
              Contact Support
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="https://community.neurocron.com"
              className="btn-secondary flex items-center gap-2"
            >
              Join Community
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}

