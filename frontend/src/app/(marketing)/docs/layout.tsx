"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Zap,
  Layers,
  Globe,
  Code,
  Brain,
  Shield,
  ChevronDown,
  ChevronRight,
  Menu,
  X,
  Search,
  Bot,
  BarChart3,
  FileEdit,
  Megaphone,
  Users,
  Target,
  Radar,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  title: string;
  href?: string;
  icon?: React.ElementType;
  children?: NavItem[];
}

const navigation: NavItem[] = [
  {
    title: "Getting Started",
    icon: Zap,
    children: [
      { title: "Quick Start Guide", href: "/docs/quick-start" },
      { title: "Account Setup", href: "/docs/account-setup" },
      { title: "Connecting Integrations", href: "/docs/integrations" },
      { title: "Your First Campaign", href: "/docs/first-campaign" },
    ],
  },
  {
    title: "Core Modules",
    icon: Layers,
    children: [
      { title: "NeuroPlan", href: "/docs/neuroplan" },
      { title: "AutoCron", href: "/docs/autocron" },
      { title: "ContentForge", href: "/docs/contentforge" },
      { title: "InsightCortex", href: "/docs/insightcortex" },
      { title: "FlowBuilder", href: "/docs/flowbuilder" },
      { title: "NeuroCopilot", href: "/docs/neurocopilot" },
      { title: "AudienceGenome", href: "/docs/audiencegenome" },
      { title: "AdPilot", href: "/docs/adpilot" },
      { title: "BattleStation", href: "/docs/battlestation" },
      { title: "TrendRadar", href: "/docs/trendradar" },
    ],
  },
  {
    title: "Integrations",
    icon: Globe,
    children: [
      { title: "Overview", href: "/docs/integrations" },
      { title: "Google Ads", href: "/docs/integrations/google-ads" },
      { title: "Meta Ads", href: "/docs/integrations/meta" },
      { title: "LinkedIn", href: "/docs/integrations/linkedin" },
      { title: "Twitter/X", href: "/docs/integrations/twitter" },
      { title: "HubSpot", href: "/docs/integrations/hubspot" },
      { title: "Salesforce", href: "/docs/integrations/salesforce" },
      { title: "Shopify", href: "/docs/integrations/shopify" },
    ],
  },
  {
    title: "API Reference",
    icon: Code,
    children: [
      { title: "Authentication", href: "/docs/api/auth" },
      { title: "Campaigns API", href: "/docs/api/campaigns" },
      { title: "Content API", href: "/docs/api/content" },
      { title: "Analytics API", href: "/docs/api/analytics" },
      { title: "Webhooks", href: "/docs/api/webhooks" },
      { title: "Rate Limits", href: "/docs/api/rate-limits" },
    ],
  },
  {
    title: "Best Practices",
    icon: Brain,
    children: [
      { title: "AI Optimization", href: "/docs/best-practices/ai-optimization" },
      { title: "Campaign Strategy", href: "/docs/best-practices/campaigns" },
      { title: "Content Guidelines", href: "/docs/best-practices/content" },
      { title: "Automation Workflows", href: "/docs/best-practices/automation" },
    ],
  },
  {
    title: "Security",
    icon: Shield,
    children: [
      { title: "Overview", href: "/docs/security" },
      { title: "GDPR Compliance", href: "/docs/security/gdpr" },
      { title: "SOC 2 Certification", href: "/docs/security/soc2" },
      { title: "Data Handling", href: "/docs/security/data" },
    ],
  },
];

function NavSection({ item, pathname }: { item: NavItem; pathname: string }) {
  const hasActiveChild = item.children?.some((child) => pathname.startsWith(child.href || "")) ?? false;
  const [isOpen, setIsOpen] = useState<boolean>(hasActiveChild || true);

  const Icon = item.icon;

  return (
    <div className="mb-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full py-2 text-sm font-medium text-white/80 hover:text-white transition"
      >
        <span className="flex items-center gap-2">
          {Icon && <Icon className="w-4 h-4" />}
          {item.title}
        </span>
        {isOpen ? (
          <ChevronDown className="w-4 h-4" />
        ) : (
          <ChevronRight className="w-4 h-4" />
        )}
      </button>
      {isOpen && item.children && (
        <ul className="mt-1 ml-6 space-y-1 border-l border-white/10 pl-4">
          {item.children.map((child) => (
            <li key={child.href}>
              <Link
                href={child.href || "#"}
                className={cn(
                  "block py-1.5 text-sm transition",
                  pathname === child.href
                    ? "text-electric font-medium"
                    : "text-white/60 hover:text-white"
                )}
              >
                {child.title}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Don't show sidebar on main docs page
  if (pathname === "/docs") {
    return <>{children}</>;
  }

  return (
    <div className="pt-20 min-h-screen">
      {/* Mobile sidebar toggle */}
      <button
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        className="fixed bottom-6 right-6 z-50 lg:hidden w-14 h-14 rounded-full bg-electric flex items-center justify-center shadow-lg"
      >
        {isSidebarOpen ? (
          <X className="w-6 h-6 text-midnight" />
        ) : (
          <Menu className="w-6 h-6 text-midnight" />
        )}
      </button>

      <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex">
          {/* Sidebar */}
          <aside
            className={cn(
              "fixed inset-y-0 left-0 z-40 w-72 bg-midnight border-r border-white/10 pt-24 pb-8 px-6 overflow-y-auto transition-transform lg:relative lg:translate-x-0 lg:pt-8",
              isSidebarOpen ? "translate-x-0" : "-translate-x-full"
            )}
          >
            {/* Search */}
            <div className="relative mb-6">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
              <input
                type="text"
                placeholder="Search docs..."
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none text-sm"
              />
            </div>

            {/* Navigation */}
            <nav>
              {navigation.map((item) => (
                <NavSection key={item.title} item={item} pathname={pathname} />
              ))}
            </nav>
          </aside>

          {/* Overlay */}
          {isSidebarOpen && (
            <div
              className="fixed inset-0 bg-black/50 z-30 lg:hidden"
              onClick={() => setIsSidebarOpen(false)}
            />
          )}

          {/* Main content */}
          <main className="flex-1 min-w-0 py-8 lg:pl-8">
            <div className="max-w-3xl">{children}</div>
          </main>

          {/* Table of contents - future enhancement */}
          <aside className="hidden xl:block w-64 flex-shrink-0 pl-8">
            <div className="sticky top-24">
              <h4 className="text-sm font-medium mb-4 text-white/60">On this page</h4>
              {/* TOC would be dynamically generated */}
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

