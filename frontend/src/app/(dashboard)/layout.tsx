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
  Search,
  Sparkles,
  Target,
  GitBranch,
  Rocket,
  Lightbulb,
  Inbox,
  Swords,
  Shield,
  Menu,
  X,
  CreditCard,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ProtectedRoute } from "@/components/protected-route";
import { useAuth } from "@/lib/auth-context";
import { NotificationProvider } from "@/lib/notifications";
import { NotificationBell } from "@/components/notification-bell";
import { useState, useEffect } from "react";

const navigation = [
  { name: "Command Center", href: "/dashboard", icon: LayoutDashboard },
  { name: "NeuroCopilot", href: "/copilot", icon: MessageSquare },
  { name: "Campaigns", href: "/dashboard/campaigns", icon: Megaphone },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Content", href: "/content", icon: Folder },
  { name: "Strategy", href: "/strategy", icon: Lightbulb },
  { name: "FlowBuilder", href: "/flows", icon: GitBranch },
  { name: "LaunchPad", href: "/launchpad", icon: Rocket },
  { name: "Audiences", href: "/audiences", icon: Users },
  { name: "AdPilot", href: "/ads", icon: Target },
  { name: "Inbox", href: "/inbox", icon: Inbox },
  { name: "Intelligence", href: "/intelligence", icon: Swords },
  { name: "Audit", href: "/audit", icon: Shield },
  { name: "Team", href: "/team", icon: Users },
  { name: "Billing", href: "/billing", icon: CreditCard },
  { name: "Profile", href: "/profile", icon: User },
  { name: "Settings", href: "/settings", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  // Close mobile menu on resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Get user initials
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <ProtectedRoute>
      <NotificationProvider>
        <div className="min-h-screen bg-midnight flex">
          {/* Mobile Overlay */}
          {mobileMenuOpen && (
            <div
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
              onClick={() => setMobileMenuOpen(false)}
            />
          )}

          {/* Sidebar - Desktop always visible, Mobile slide-in */}
          <aside
            className={cn(
              "fixed left-0 top-0 bottom-0 w-64 bg-midnight-100 border-r border-white/5 flex flex-col z-50 transition-transform duration-300 lg:translate-x-0",
              mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
            )}
          >
            {/* Logo */}
            <div className="p-4 lg:p-6 flex items-center justify-between">
              <Link href="/dashboard" className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-neural-gradient flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold">NeuroCron</span>
              </Link>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-2 hover:bg-white/10 rounded-lg lg:hidden"
              >
                <X className="w-5 h-5" />
              </button>
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

            {/* Navigation - Scrollable */}
            <nav className="flex-1 px-4 space-y-1 overflow-y-auto scrollbar-thin">
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
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    <span className="truncate">{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* User */}
            <div className="p-4 border-t border-white/5 relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors"
              >
                <div className="w-9 h-9 rounded-full bg-neural-gradient flex items-center justify-center text-sm font-medium flex-shrink-0">
                  {user ? getInitials(user.full_name) : "??"}
                </div>
                <div className="flex-1 min-w-0 text-left">
                  <div className="text-sm font-medium truncate">
                    {user?.full_name || "User"}
                  </div>
                  <div className="text-xs text-white/50 truncate">
                    {user?.email || ""}
                  </div>
                </div>
                <ChevronDown
                  className={cn(
                    "w-4 h-4 text-white/50 transition-transform flex-shrink-0",
                    showUserMenu && "rotate-180"
                  )}
                />
              </button>

              {/* User Menu Dropdown */}
              {showUserMenu && (
                <div className="absolute bottom-full left-4 right-4 mb-2 bg-midnight-100 border border-white/10 rounded-xl shadow-xl overflow-hidden">
                  <Link
                    href="/profile"
                    className="flex items-center gap-3 px-4 py-3 text-sm text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <User className="w-4 h-4" />
                    Profile
                  </Link>
                  <Link
                    href="/settings"
                    className="flex items-center gap-3 px-4 py-3 text-sm text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <Settings className="w-4 h-4" />
                    Settings
                  </Link>
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      logout();
                    }}
                    className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 transition-colors border-t border-white/5"
                  >
                    <LogOut className="w-4 h-4" />
                    Log out
                  </button>
                </div>
              )}
            </div>
          </aside>

          {/* Main Content */}
          <div className="flex-1 lg:ml-64">
            {/* Top Bar */}
            <header className="sticky top-0 z-40 h-14 lg:h-16 bg-midnight-100/80 backdrop-blur-xl border-b border-white/5 flex items-center justify-between px-4 lg:px-6">
              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="p-2 hover:bg-white/10 rounded-lg lg:hidden"
              >
                <Menu className="w-5 h-5" />
              </button>

              {/* Search - Hidden on mobile */}
              <div className="hidden md:flex items-center gap-3 flex-1 max-w-xl">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                  <input
                    type="text"
                    placeholder="Search campaigns, content, analytics..."
                    className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-sm focus:outline-none focus:border-electric transition-colors"
                  />
                </div>
              </div>

              {/* Mobile Logo */}
              <Link href="/dashboard" className="flex items-center gap-2 lg:hidden">
                <div className="w-8 h-8 rounded-lg bg-neural-gradient flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="font-bold">NeuroCron</span>
              </Link>

              {/* Actions */}
              <div className="flex items-center gap-2 lg:gap-4">
                <NotificationBell />
                <Link
                  href="/dashboard/campaigns/new"
                  className="btn-primary text-xs lg:text-sm py-1.5 lg:py-2 px-3 lg:px-4 hidden sm:inline-flex"
                >
                  <span className="hidden lg:inline">New Campaign</span>
                  <span className="lg:hidden">New</span>
                </Link>
              </div>
            </header>

            {/* Page Content */}
            <main className="p-4 lg:p-6">{children}</main>
          </div>
        </div>
      </NotificationProvider>
    </ProtectedRoute>
  );
}
