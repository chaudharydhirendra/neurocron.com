"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Brain,
  LayoutDashboard,
  Megaphone,
  BarChart3,
  MessageSquare,
  Settings,
  Users,
  Folder,
  LogOut,
  ChevronDown,
  Bell,
  Search,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Command Center", href: "/dashboard", icon: LayoutDashboard },
  { name: "NeuroCopilot", href: "/dashboard/copilot", icon: MessageSquare },
  { name: "Campaigns", href: "/dashboard/campaigns", icon: Megaphone },
  { name: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { name: "Audiences", href: "/dashboard/audiences", icon: Users },
  { name: "Content", href: "/dashboard/content", icon: Folder },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-midnight flex">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 bottom-0 w-64 bg-midnight-100 border-r border-white/5 flex flex-col">
        {/* Logo */}
        <div className="p-6">
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-neural-gradient flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold">NeuroCron</span>
          </Link>
        </div>

        {/* NeuroCopilot Quick Access */}
        <div className="px-4 mb-4">
          <Link
            href="/dashboard/copilot"
            className="flex items-center gap-3 p-3 rounded-xl bg-neural-gradient/10 border border-electric/20 hover:bg-neural-gradient/20 transition-colors group"
          >
            <Sparkles className="w-5 h-5 text-electric group-hover:scale-110 transition-transform" />
            <span className="text-sm font-medium">Ask NeuroCopilot</span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors",
                  isActive
                    ? "bg-electric/10 text-electric"
                    : "text-white/60 hover:text-white hover:bg-white/5"
                )}
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User */}
        <div className="p-4 border-t border-white/5">
          <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer">
            <div className="w-9 h-9 rounded-full bg-neural-gradient flex items-center justify-center text-sm font-medium">
              JD
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">John Doe</div>
              <div className="text-xs text-white/50 truncate">john@company.com</div>
            </div>
            <ChevronDown className="w-4 h-4 text-white/50" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 ml-64">
        {/* Top Bar */}
        <header className="sticky top-0 z-40 h-16 bg-midnight-100/80 backdrop-blur-xl border-b border-white/5 flex items-center justify-between px-6">
          {/* Search */}
          <div className="flex items-center gap-3 flex-1 max-w-xl">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
              <input
                type="text"
                placeholder="Search campaigns, content, analytics..."
                className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-sm focus:outline-none focus:border-electric transition-colors"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-4">
            <button className="relative p-2 rounded-xl hover:bg-white/5 transition-colors">
              <Bell className="w-5 h-5 text-white/60" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-electric rounded-full" />
            </button>
            <button className="btn-primary text-sm py-2">
              New Campaign
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

