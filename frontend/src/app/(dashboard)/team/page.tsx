"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Users,
  UserPlus,
  MoreVertical,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Eye,
  Trash2,
  Loader2,
  Mail,
  Crown,
  Check,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface TeamMember {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  joined_at: string;
  is_active: boolean;
}

interface Permissions {
  role: string;
  permissions: string[];
  can_manage_team: boolean;
  can_manage_billing: boolean;
  is_owner: boolean;
}

const ROLES = [
  { id: "owner", name: "Owner", description: "Full access to everything", icon: Crown },
  { id: "admin", name: "Admin", description: "Manage team and settings", icon: ShieldCheck },
  { id: "member", name: "Member", description: "Create and manage content", icon: Shield },
  { id: "viewer", name: "Viewer", description: "View-only access", icon: Eye },
];

export default function TeamPage() {
  const { organization } = useAuth();
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [permissions, setPermissions] = useState<Permissions | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");
  const [isInviting, setIsInviting] = useState(false);
  const [editingMember, setEditingMember] = useState<string | null>(null);

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [membersRes, permissionsRes] = await Promise.all([
        authFetch(`/api/v1/teams/members?org_id=${organization.id}`),
        authFetch(`/api/v1/teams/permissions?org_id=${organization.id}`),
      ]);

      if (membersRes.ok) {
        const data = await membersRes.json();
        setMembers(data.members || []);
      }
      if (permissionsRes.ok) {
        const data = await permissionsRes.json();
        setPermissions(data);
      }
    } catch (error) {
      console.error("Failed to fetch team data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInvite = async () => {
    if (!organization || !inviteEmail) return;
    setIsInviting(true);

    try {
      const response = await authFetch(
        `/api/v1/teams/invite?org_id=${organization.id}`,
        {
          method: "POST",
          body: JSON.stringify({ email: inviteEmail, role: inviteRole }),
        }
      );

      if (response.ok) {
        setShowInviteModal(false);
        setInviteEmail("");
        setInviteRole("member");
        fetchData();
      }
    } catch (error) {
      console.error("Failed to invite:", error);
    } finally {
      setIsInviting(false);
    }
  };

  const handleUpdateRole = async (memberId: string, newRole: string) => {
    if (!organization) return;

    try {
      const response = await authFetch(
        `/api/v1/teams/members/${memberId}/role?org_id=${organization.id}`,
        {
          method: "PUT",
          body: JSON.stringify({ role: newRole }),
        }
      );

      if (response.ok) {
        setEditingMember(null);
        fetchData();
      }
    } catch (error) {
      console.error("Failed to update role:", error);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!organization) return;
    if (!confirm("Are you sure you want to remove this member?")) return;

    try {
      const response = await authFetch(
        `/api/v1/teams/members/${memberId}?org_id=${organization.id}`,
        { method: "DELETE" }
      );

      if (response.ok) {
        fetchData();
      }
    } catch (error) {
      console.error("Failed to remove member:", error);
    }
  };

  const getRoleIcon = (role: string) => {
    const roleData = ROLES.find((r) => r.id === role);
    return roleData?.icon || Shield;
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case "owner":
        return "text-yellow-400 bg-yellow-400/10";
      case "admin":
        return "text-purple-400 bg-purple-400/10";
      case "member":
        return "text-blue-400 bg-blue-400/10";
      case "viewer":
        return "text-white/40 bg-white/5";
      default:
        return "text-white/40 bg-white/5";
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
              <Users className="w-5 h-5 text-purple-400" />
            </div>
            Team
          </h1>
          <p className="text-white/60 mt-1">
            Manage your team members and permissions
          </p>
        </div>
        {permissions?.can_manage_team && (
          <button
            onClick={() => setShowInviteModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <UserPlus className="w-5 h-5" />
            Invite Member
          </button>
        )}
      </div>

      {/* Members List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-electric" />
        </div>
      ) : (
        <div className="space-y-3">
          {members.map((member, index) => {
            const RoleIcon = getRoleIcon(member.role);
            return (
              <motion.div
                key={member.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="card p-4 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-electric to-purple-500 flex items-center justify-center text-lg font-bold">
                    {member.full_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{member.full_name}</span>
                      {member.role === "owner" && (
                        <Crown className="w-4 h-4 text-yellow-400" />
                      )}
                    </div>
                    <div className="text-sm text-white/50">{member.email}</div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {editingMember === member.id ? (
                    <div className="flex items-center gap-2">
                      <select
                        defaultValue={member.role}
                        onChange={(e) => handleUpdateRole(member.id, e.target.value)}
                        className="input py-1 text-sm"
                      >
                        {ROLES.filter((r) => r.id !== "owner").map((role) => (
                          <option key={role.id} value={role.id}>
                            {role.name}
                          </option>
                        ))}
                      </select>
                      <button
                        onClick={() => setEditingMember(null)}
                        className="p-1 hover:bg-white/10 rounded"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <div
                      className={cn(
                        "px-3 py-1 rounded-lg text-sm capitalize flex items-center gap-2",
                        getRoleColor(member.role)
                      )}
                    >
                      <RoleIcon className="w-4 h-4" />
                      {member.role}
                    </div>
                  )}

                  {permissions?.can_manage_team && member.role !== "owner" && (
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() =>
                          setEditingMember(
                            editingMember === member.id ? null : member.id
                          )
                        }
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        title="Change role"
                      >
                        <Shield className="w-4 h-4 text-white/50" />
                      </button>
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="p-2 hover:bg-red-400/10 rounded-lg transition-colors"
                        title="Remove member"
                      >
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </button>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Role Descriptions */}
      <div className="card">
        <h3 className="font-semibold mb-4">Role Permissions</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {ROLES.map((role) => {
            const Icon = role.icon;
            return (
              <div
                key={role.id}
                className="p-4 rounded-xl bg-white/5 flex items-start gap-3"
              >
                <Icon className={cn("w-5 h-5 mt-0.5", getRoleColor(role.id).split(" ")[0])} />
                <div>
                  <div className="font-medium">{role.name}</div>
                  <div className="text-sm text-white/50">{role.description}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card w-full max-w-md mx-4"
          >
            <h2 className="text-xl font-bold mb-4">Invite Team Member</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="colleague@company.com"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">Role</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="input"
                >
                  {ROLES.filter((r) => r.id !== "owner").map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.name} - {role.description}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowInviteModal(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={handleInvite}
                disabled={isInviting || !inviteEmail}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                {isInviting ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Mail className="w-5 h-5" />
                    Send Invite
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}

