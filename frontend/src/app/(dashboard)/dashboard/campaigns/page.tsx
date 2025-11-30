"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Plus,
  Search,
  Filter,
  Megaphone,
  MoreVertical,
  Play,
  Pause,
  Trash2,
  Edit,
  ArrowUpRight,
  Calendar,
  DollarSign,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Campaign {
  id: string;
  name: string;
  description: string | null;
  status: string;
  campaign_type: string;
  budget: number | null;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
}

export default function CampaignsPage() {
  const { organization } = useAuth();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  useEffect(() => {
    const fetchCampaigns = async () => {
      if (!organization) return;

      try {
        let url = `/api/v1/campaigns/?org_id=${organization.id}`;
        if (statusFilter) {
          url += `&status=${statusFilter}`;
        }
        
        const response = await authFetch(url);
        if (response.ok) {
          const data = await response.json();
          setCampaigns(data);
        }
      } catch {
        console.error("Failed to fetch campaigns");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCampaigns();
  }, [organization, statusFilter]);

  const filteredCampaigns = campaigns.filter((campaign) =>
    campaign.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-400 bg-green-400/10 border-green-400/20";
      case "paused":
        return "text-yellow-400 bg-yellow-400/10 border-yellow-400/20";
      case "draft":
        return "text-white/50 bg-white/5 border-white/10";
      case "completed":
        return "text-electric bg-electric/10 border-electric/20";
      default:
        return "text-white/50 bg-white/5 border-white/10";
    }
  };

  const handlePause = async (campaignId: string) => {
    const response = await authFetch(`/api/v1/campaigns/${campaignId}/pause`, {
      method: "POST",
    });
    if (response.ok) {
      setCampaigns((prev) =>
        prev.map((c) => (c.id === campaignId ? { ...c, status: "paused" } : c))
      );
    }
  };

  const handleActivate = async (campaignId: string) => {
    const response = await authFetch(`/api/v1/campaigns/${campaignId}/activate`, {
      method: "POST",
    });
    if (response.ok) {
      setCampaigns((prev) =>
        prev.map((c) => (c.id === campaignId ? { ...c, status: "active" } : c))
      );
    }
  };

  const handleDelete = async (campaignId: string) => {
    if (!confirm("Are you sure you want to delete this campaign?")) return;
    
    const response = await authFetch(`/api/v1/campaigns/${campaignId}`, {
      method: "DELETE",
    });
    if (response.ok) {
      setCampaigns((prev) => prev.filter((c) => c.id !== campaignId));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Campaigns</h1>
          <p className="text-white/60 mt-1">
            Manage your marketing campaigns
          </p>
        </div>
        <Link href="/dashboard/campaigns/new" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Campaign
        </Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search campaigns..."
            className="input pl-11"
          />
        </div>

        <div className="flex items-center gap-2">
          {["all", "active", "paused", "draft"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status === "all" ? null : status)}
              className={cn(
                "px-4 py-2 rounded-xl text-sm font-medium transition-colors capitalize",
                (statusFilter === status || (status === "all" && !statusFilter))
                  ? "bg-electric text-midnight"
                  : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
              )}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Campaigns List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-pulse text-white/60">Loading campaigns...</div>
        </div>
      ) : filteredCampaigns.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-12 card"
        >
          <Megaphone className="w-12 h-12 text-white/20 mx-auto mb-4" />
          <h3 className="font-medium mb-2">No campaigns found</h3>
          <p className="text-white/60 text-sm mb-4">
            {searchQuery
              ? "Try a different search term"
              : "Create your first campaign to get started"}
          </p>
          <Link href="/dashboard/campaigns/new" className="btn-primary">
            Create Campaign
          </Link>
        </motion.div>
      ) : (
        <div className="space-y-3">
          {filteredCampaigns.map((campaign, index) => (
            <motion.div
              key={campaign.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="card p-4 flex items-center justify-between group"
            >
              <div className="flex items-center gap-4 flex-1">
                <div className="w-12 h-12 rounded-xl bg-neural-gradient/20 flex items-center justify-center">
                  <Megaphone className="w-6 h-6 text-electric" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <h3 className="font-medium truncate">{campaign.name}</h3>
                    <span
                      className={cn(
                        "text-xs px-2.5 py-0.5 rounded-full border capitalize",
                        getStatusColor(campaign.status)
                      )}
                    >
                      {campaign.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-sm text-white/50">
                    {campaign.budget && (
                      <span className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        {formatCurrency(campaign.budget)}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {formatDate(campaign.start_date)}
                    </span>
                    <span className="capitalize text-white/40">
                      {campaign.campaign_type?.replace("_", " ")}
                    </span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                {campaign.status === "active" ? (
                  <button
                    onClick={() => handlePause(campaign.id)}
                    className="p-2 rounded-lg hover:bg-yellow-400/10 transition-colors"
                    title="Pause"
                  >
                    <Pause className="w-5 h-5 text-yellow-400" />
                  </button>
                ) : campaign.status !== "completed" ? (
                  <button
                    onClick={() => handleActivate(campaign.id)}
                    className="p-2 rounded-lg hover:bg-green-400/10 transition-colors"
                    title="Activate"
                  >
                    <Play className="w-5 h-5 text-green-400" />
                  </button>
                ) : null}
                <Link
                  href={`/dashboard/campaigns/${campaign.id}/edit`}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                  title="Edit"
                >
                  <Edit className="w-5 h-5 text-white/60" />
                </Link>
                <button
                  onClick={() => handleDelete(campaign.id)}
                  className="p-2 rounded-lg hover:bg-red-400/10 transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-5 h-5 text-red-400" />
                </button>
                <Link
                  href={`/dashboard/campaigns/${campaign.id}`}
                  className="p-2 rounded-lg hover:bg-electric/10 transition-colors"
                  title="View Details"
                >
                  <ArrowUpRight className="w-5 h-5 text-electric" />
                </Link>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

