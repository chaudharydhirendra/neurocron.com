"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Settings,
  User,
  Building2,
  Link2,
  Bell,
  Shield,
  CreditCard,
  Loader2,
  Check,
  ExternalLink,
  Unlink,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Integration {
  id: string;
  platform: string;
  name: string;
  status: string;
  connected_at?: string;
  account_name?: string;
}

const tabs = [
  { id: "profile", name: "Profile", icon: User },
  { id: "organization", name: "Organization", icon: Building2 },
  { id: "integrations", name: "Integrations", icon: Link2 },
  { id: "notifications", name: "Notifications", icon: Bell },
  { id: "security", name: "Security", icon: Shield },
  { id: "billing", name: "Billing", icon: CreditCard },
];

const platformLogos: Record<string, string> = {
  google: "🔍",
  meta: "📘",
  linkedin: "💼",
  twitter: "🐦",
};

export default function SettingsPage() {
  const { user, organization } = useAuth();
  const [activeTab, setActiveTab] = useState("integrations");
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [connecting, setConnecting] = useState<string | null>(null);

  useEffect(() => {
    if (activeTab === "integrations" && organization) {
      fetchIntegrations();
    }
  }, [activeTab, organization]);

  const fetchIntegrations = async () => {
    if (!organization) return;
    setIsLoading(true);
    try {
      const response = await authFetch(
        `/api/v1/integrations/?org_id=${organization.id}`
      );
      if (response.ok) {
        const data = await response.json();
        setIntegrations(data);
      }
    } catch (error) {
      console.error("Failed to fetch integrations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnect = async (platform: string) => {
    if (!organization) return;
    setConnecting(platform);
    try {
      const response = await authFetch(
        `/api/v1/integrations/connect?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({
            platform,
            callback_url: `${window.location.origin}/settings/integrations/callback`,
          }),
        }
      );
      if (response.ok) {
        const data = await response.json();
        // In production, redirect to OAuth URL
        alert(
          `Integration with ${platform} requires API credentials to be configured.\n\nOAuth URL: ${data.oauth_url}`
        );
      }
    } catch (error) {
      console.error("Failed to connect:", error);
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = async (integrationId: string) => {
    if (!organization || !confirm("Are you sure you want to disconnect this integration?")) return;
    
    try {
      const response = await authFetch(
        `/api/v1/integrations/${integrationId}?org_id=${organization.id}`,
        { method: "DELETE" }
      );
      if (response.ok) {
        fetchIntegrations();
      }
    } catch (error) {
      console.error("Failed to disconnect:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
            <Settings className="w-5 h-5 text-white/60" />
          </div>
          Settings
        </h1>
        <p className="text-white/60 mt-1">
          Manage your account and organization settings
        </p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-48 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm transition-colors",
                  activeTab === tab.id
                    ? "bg-electric/10 text-electric"
                    : "text-white/60 hover:text-white hover:bg-white/5"
                )}
              >
                <tab.icon className="w-5 h-5" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === "profile" && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-6">Profile Settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    defaultValue={user?.full_name}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    defaultValue={user?.email}
                    className="input"
                    disabled
                  />
                </div>
                <button className="btn-primary">Save Changes</button>
              </div>
            </div>
          )}

          {activeTab === "organization" && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-6">Organization Settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    Organization Name
                  </label>
                  <input
                    type="text"
                    defaultValue={organization?.name}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    Industry
                  </label>
                  <select className="input">
                    <option>E-commerce</option>
                    <option>SaaS / Technology</option>
                    <option>Healthcare</option>
                    <option>Finance</option>
                    <option>Other</option>
                  </select>
                </div>
                <button className="btn-primary">Save Changes</button>
              </div>
            </div>
          )}

          {activeTab === "integrations" && (
            <div className="space-y-4">
              <div className="card">
                <h2 className="text-lg font-semibold mb-2">
                  Platform Integrations
                </h2>
                <p className="text-sm text-white/60 mb-6">
                  Connect your marketing platforms for automated management
                </p>

                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-electric" />
                  </div>
                ) : (
                  <div className="space-y-3">
                    {integrations.map((integration) => (
                      <motion.div
                        key={integration.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10"
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center text-2xl">
                            {platformLogos[integration.platform] || "🔗"}
                          </div>
                          <div>
                            <h3 className="font-medium">{integration.name}</h3>
                            <p className="text-sm text-white/50">
                              {integration.status === "connected"
                                ? `Connected${integration.account_name ? ` • ${integration.account_name}` : ""}`
                                : "Not connected"}
                            </p>
                          </div>
                        </div>
                        <div>
                          {integration.status === "connected" ? (
                            <div className="flex items-center gap-2">
                              <span className="flex items-center gap-1 text-sm text-green-400">
                                <Check className="w-4 h-4" />
                                Connected
                              </span>
                              <button
                                onClick={() => handleDisconnect(integration.id)}
                                className="p-2 rounded-lg hover:bg-red-500/10 transition-colors"
                                title="Disconnect"
                              >
                                <Unlink className="w-5 h-5 text-red-400" />
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => handleConnect(integration.platform)}
                              disabled={connecting === integration.platform}
                              className="btn-primary text-sm flex items-center gap-2"
                            >
                              {connecting === integration.platform ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <ExternalLink className="w-4 h-4" />
                              )}
                              Connect
                            </button>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              <div className="card bg-electric/5 border-electric/20">
                <h3 className="font-semibold mb-2">
                  Why connect your platforms?
                </h3>
                <ul className="text-sm text-white/60 space-y-2">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-electric" />
                    Manage all ads from one dashboard
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-electric" />
                    Automated performance optimization
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-electric" />
                    Cross-platform analytics and attribution
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-electric" />
                    AI-powered campaign creation
                  </li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-6">
                Notification Preferences
              </h2>
              <div className="space-y-4">
                {[
                  { name: "Campaign alerts", desc: "Get notified about campaign performance" },
                  { name: "Weekly reports", desc: "Receive weekly performance summaries" },
                  { name: "Crisis alerts", desc: "Immediate alerts for brand issues" },
                  { name: "Feature updates", desc: "Learn about new NeuroCron features" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between py-3 border-b border-white/5 last:border-0">
                    <div>
                      <h4 className="font-medium">{item.name}</h4>
                      <p className="text-sm text-white/50">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        defaultChecked
                      />
                      <div className="w-11 h-6 bg-white/10 rounded-full peer peer-checked:bg-electric transition-colors after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full" />
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "security" && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-6">Security Settings</h2>
              <div className="space-y-4">
                <button className="btn-secondary w-full justify-start">
                  Change Password
                </button>
                <button className="btn-secondary w-full justify-start">
                  Enable Two-Factor Authentication
                </button>
                <button className="btn-secondary w-full justify-start">
                  View Active Sessions
                </button>
                <button className="btn-secondary w-full justify-start text-red-400 hover:bg-red-400/10">
                  Delete Account
                </button>
              </div>
            </div>
          )}

          {activeTab === "billing" && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-6">Billing & Subscription</h2>
              <div className="p-4 rounded-xl bg-neural-gradient/10 border border-electric/20 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-white/60">Current Plan</span>
                  <span className="px-3 py-1 rounded-full bg-electric/20 text-electric text-sm font-medium">
                    {organization?.plan?.toUpperCase() || "FREE"}
                  </span>
                </div>
                <p className="text-2xl font-bold">$0/month</p>
              </div>
              <button className="btn-primary w-full">
                Upgrade to Pro
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

