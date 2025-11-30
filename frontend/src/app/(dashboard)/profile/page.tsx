"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  User,
  Mail,
  Lock,
  Bell,
  Globe,
  Moon,
  Sun,
  Loader2,
  Save,
  Camera,
  Check,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  timezone?: string;
  preferences?: {
    theme?: string;
    email_notifications?: boolean;
    marketing_emails?: boolean;
    weekly_digest?: boolean;
  };
}

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  
  // Form state
  const [fullName, setFullName] = useState("");
  const [timezone, setTimezone] = useState("UTC");
  const [theme, setTheme] = useState("dark");
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [marketingEmails, setMarketingEmails] = useState(false);
  const [weeklyDigest, setWeeklyDigest] = useState(true);
  
  // Password change
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || "");
      setProfile({
        id: user.id,
        email: user.email,
        full_name: user.full_name,
      });
      setIsLoading(false);
    }
  }, [user]);

  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      // In production, call API to save profile
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error("Failed to save profile:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      alert("Passwords don't match");
      return;
    }
    
    setIsSaving(true);
    try {
      // In production, call API to change password
      await new Promise(resolve => setTimeout(resolve, 1000));
      setShowPasswordChange(false);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      alert("Password changed successfully");
    } catch (error) {
      console.error("Failed to change password:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const TIMEZONES = [
    "UTC",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Kolkata",
    "Australia/Sydney",
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-electric" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center">
            <User className="w-5 h-5 text-electric" />
          </div>
          Profile & Settings
        </h1>
        <p className="text-white/60 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Profile Section */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <User className="w-5 h-5" />
          Profile Information
        </h2>

        <div className="space-y-4">
          {/* Avatar */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-electric to-purple-500 flex items-center justify-center text-2xl font-bold">
                {fullName.charAt(0).toUpperCase()}
              </div>
              <button className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-midnight-100 border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors">
                <Camera className="w-4 h-4" />
              </button>
            </div>
            <div>
              <div className="font-medium">{fullName}</div>
              <div className="text-sm text-white/50">{profile?.email}</div>
            </div>
          </div>

          {/* Full Name */}
          <div>
            <label className="block text-sm text-white/60 mb-2">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="input"
            />
          </div>

          {/* Email (read-only) */}
          <div>
            <label className="block text-sm text-white/60 mb-2">Email</label>
            <input
              type="email"
              value={profile?.email || ""}
              disabled
              className="input opacity-60 cursor-not-allowed"
            />
            <p className="text-xs text-white/40 mt-1">
              Contact support to change your email address
            </p>
          </div>

          {/* Timezone */}
          <div>
            <label className="block text-sm text-white/60 mb-2 flex items-center gap-2">
              <Globe className="w-4 h-4" />
              Timezone
            </label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="input"
            >
              {TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>
                  {tz.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Notification Preferences */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Notification Preferences
        </h2>

        <div className="space-y-4">
          <label className="flex items-center justify-between p-3 rounded-xl bg-white/5 cursor-pointer">
            <div>
              <div className="font-medium">Email Notifications</div>
              <div className="text-sm text-white/50">
                Receive important updates via email
              </div>
            </div>
            <input
              type="checkbox"
              checked={emailNotifications}
              onChange={(e) => setEmailNotifications(e.target.checked)}
              className="w-5 h-5 rounded accent-electric"
            />
          </label>

          <label className="flex items-center justify-between p-3 rounded-xl bg-white/5 cursor-pointer">
            <div>
              <div className="font-medium">Weekly Digest</div>
              <div className="text-sm text-white/50">
                Summary of your marketing performance
              </div>
            </div>
            <input
              type="checkbox"
              checked={weeklyDigest}
              onChange={(e) => setWeeklyDigest(e.target.checked)}
              className="w-5 h-5 rounded accent-electric"
            />
          </label>

          <label className="flex items-center justify-between p-3 rounded-xl bg-white/5 cursor-pointer">
            <div>
              <div className="font-medium">Marketing Emails</div>
              <div className="text-sm text-white/50">
                Tips, product updates, and offers
              </div>
            </div>
            <input
              type="checkbox"
              checked={marketingEmails}
              onChange={(e) => setMarketingEmails(e.target.checked)}
              className="w-5 h-5 rounded accent-electric"
            />
          </label>
        </div>
      </div>

      {/* Appearance */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Moon className="w-5 h-5" />
          Appearance
        </h2>

        <div className="flex gap-4">
          <button
            onClick={() => setTheme("dark")}
            className={cn(
              "flex-1 p-4 rounded-xl border-2 transition-colors",
              theme === "dark"
                ? "border-electric bg-electric/10"
                : "border-white/10 hover:border-white/20"
            )}
          >
            <Moon className="w-6 h-6 mx-auto mb-2" />
            <div className="text-sm font-medium">Dark</div>
          </button>
          <button
            onClick={() => setTheme("light")}
            className={cn(
              "flex-1 p-4 rounded-xl border-2 transition-colors",
              theme === "light"
                ? "border-electric bg-electric/10"
                : "border-white/10 hover:border-white/20"
            )}
          >
            <Sun className="w-6 h-6 mx-auto mb-2" />
            <div className="text-sm font-medium">Light</div>
          </button>
          <button
            onClick={() => setTheme("system")}
            className={cn(
              "flex-1 p-4 rounded-xl border-2 transition-colors",
              theme === "system"
                ? "border-electric bg-electric/10"
                : "border-white/10 hover:border-white/20"
            )}
          >
            <div className="flex justify-center gap-1 mb-2">
              <Moon className="w-5 h-5" />
              <Sun className="w-5 h-5" />
            </div>
            <div className="text-sm font-medium">System</div>
          </button>
        </div>
      </div>

      {/* Password */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Lock className="w-5 h-5" />
          Security
        </h2>

        {!showPasswordChange ? (
          <button
            onClick={() => setShowPasswordChange(true)}
            className="btn-secondary"
          >
            Change Password
          </button>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-white/60 mb-2">
                Current Password
              </label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-2">
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-2">
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowPasswordChange(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleChangePassword}
                disabled={!currentPassword || !newPassword || !confirmPassword}
                className="btn-primary"
              >
                Update Password
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSaveProfile}
          disabled={isSaving}
          className="btn-primary flex items-center gap-2"
        >
          {isSaving ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : saved ? (
            <>
              <Check className="w-5 h-5" />
              Saved!
            </>
          ) : (
            <>
              <Save className="w-5 h-5" />
              Save Changes
            </>
          )}
        </button>
      </div>
    </div>
  );
}

