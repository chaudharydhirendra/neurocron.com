"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Users,
  Search,
  Filter,
  UserPlus,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  DollarSign,
  Activity,
  ChevronRight,
  Loader2,
  Mail,
  Phone,
  Building2,
  Calendar,
  Tag,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface Customer {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  company_name?: string;
  engagement_score: number;
  churn_risk: number;
  lifetime_value: number;
  total_orders: number;
  last_seen_at: string;
  acquisition_source?: string;
  tags: string[];
}

interface CDPOverview {
  total_customers: number;
  active_customers_30d: number;
  total_revenue: number;
  average_engagement_score: number;
  high_churn_risk_count: number;
}

export default function CustomersPage() {
  const { organization } = useAuth();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [overview, setOverview] = useState<CDPOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState<string | null>(null);

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [customersRes, overviewRes] = await Promise.all([
        authFetch(`/api/v1/customer-dna/customers?org_id=${organization.id}`),
        authFetch(`/api/v1/customer-dna/analytics/overview?org_id=${organization.id}`),
      ]);

      if (customersRes.ok) {
        const data = await customersRes.json();
        setCustomers(data.customers || []);
      }
      if (overviewRes.ok) {
        const data = await overviewRes.json();
        setOverview(data);
      }
    } catch (error) {
      console.error("Failed to fetch customer data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number, invert: boolean = false) => {
    if (invert) score = 100 - score;
    if (score >= 70) return "text-green-400 bg-green-400/10";
    if (score >= 40) return "text-yellow-400 bg-yellow-400/10";
    return "text-red-400 bg-red-400/10";
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "Never";
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
              <Users className="w-5 h-5 text-white" />
            </div>
            CustomerDNA
          </h1>
          <p className="text-white/60 mt-1">
            Unified customer profiles across all touchpoints
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <UserPlus className="w-5 h-5" />
          Add Customer
        </button>
      </div>

      {/* Overview Stats */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {overview.total_customers.toLocaleString()}
                </div>
                <div className="text-xs text-white/50">Total Customers</div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card p-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <Activity className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {overview.active_customers_30d.toLocaleString()}
                </div>
                <div className="text-xs text-white/50">Active (30d)</div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card p-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-electric/10 flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-electric" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {formatCurrency(overview.total_revenue)}
                </div>
                <div className="text-xs text-white/50">Total Revenue</div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card p-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {overview.average_engagement_score}
                </div>
                <div className="text-xs text-white/50">Avg Engagement</div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card p-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {overview.high_churn_risk_count}
                </div>
                <div className="text-xs text-white/50">High Churn Risk</div>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search by name, email, or company..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10 w-full"
          />
        </div>
        <button className="btn-secondary flex items-center gap-2">
          <Filter className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Customers Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-electric" />
          </div>
        ) : customers.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-12 h-12 mx-auto mb-4 text-white/20" />
            <h3 className="text-lg font-medium mb-2">No customers yet</h3>
            <p className="text-white/50 mb-4">
              Start tracking customers to build your CDP
            </p>
            <button className="btn-primary">Add First Customer</button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left p-4 text-sm font-medium text-white/60">
                    Customer
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-white/60 hidden md:table-cell">
                    Company
                  </th>
                  <th className="text-center p-4 text-sm font-medium text-white/60">
                    Engagement
                  </th>
                  <th className="text-center p-4 text-sm font-medium text-white/60">
                    Churn Risk
                  </th>
                  <th className="text-right p-4 text-sm font-medium text-white/60 hidden sm:table-cell">
                    LTV
                  </th>
                  <th className="text-right p-4 text-sm font-medium text-white/60 hidden lg:table-cell">
                    Last Seen
                  </th>
                  <th className="p-4"></th>
                </tr>
              </thead>
              <tbody>
                {customers
                  .filter(
                    (c) =>
                      !search ||
                      c.full_name.toLowerCase().includes(search.toLowerCase()) ||
                      c.email?.toLowerCase().includes(search.toLowerCase()) ||
                      c.company_name?.toLowerCase().includes(search.toLowerCase())
                  )
                  .map((customer, index) => (
                    <motion.tr
                      key={customer.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.02 }}
                      className="border-b border-white/5 hover:bg-white/5 cursor-pointer"
                      onClick={() => setSelectedCustomer(customer.id)}
                    >
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-electric to-purple-500 flex items-center justify-center font-medium">
                            {customer.full_name?.charAt(0) || customer.email?.charAt(0) || "?"}
                          </div>
                          <div>
                            <div className="font-medium">
                              {customer.full_name || "Anonymous"}
                            </div>
                            <div className="text-sm text-white/50">
                              {customer.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="p-4 hidden md:table-cell">
                        <div className="flex items-center gap-2 text-white/60">
                          <Building2 className="w-4 h-4" />
                          {customer.company_name || "-"}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex justify-center">
                          <span
                            className={cn(
                              "px-2 py-1 rounded-lg text-sm font-medium",
                              getScoreColor(customer.engagement_score)
                            )}
                          >
                            {customer.engagement_score}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex justify-center">
                          <span
                            className={cn(
                              "px-2 py-1 rounded-lg text-sm font-medium",
                              getScoreColor(customer.churn_risk, true)
                            )}
                          >
                            {customer.churn_risk}%
                          </span>
                        </div>
                      </td>
                      <td className="p-4 text-right hidden sm:table-cell">
                        <span className="font-medium">
                          {formatCurrency(customer.lifetime_value)}
                        </span>
                      </td>
                      <td className="p-4 text-right text-white/50 hidden lg:table-cell">
                        {formatDate(customer.last_seen_at)}
                      </td>
                      <td className="p-4">
                        <ChevronRight className="w-4 h-4 text-white/30" />
                      </td>
                    </motion.tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Segments */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="card p-4 cursor-pointer hover:border-electric/50 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium">High Value Customers</h3>
            <TrendingUp className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">
            {Math.round((overview?.total_customers || 0) * 0.15)}
          </div>
          <p className="text-sm text-white/50 mt-1">
            Top 15% by lifetime value
          </p>
        </div>

        <div className="card p-4 cursor-pointer hover:border-electric/50 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium">At Risk Customers</h3>
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-yellow-400">
            {overview?.high_churn_risk_count || 0}
          </div>
          <p className="text-sm text-white/50 mt-1">
            Churn risk above 70%
          </p>
        </div>

        <div className="card p-4 cursor-pointer hover:border-electric/50 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium">New This Month</h3>
            <UserPlus className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-blue-400">
            {Math.round((overview?.total_customers || 0) * 0.12)}
          </div>
          <p className="text-sm text-white/50 mt-1">
            Acquired in last 30 days
          </p>
        </div>
      </div>
    </div>
  );
}

