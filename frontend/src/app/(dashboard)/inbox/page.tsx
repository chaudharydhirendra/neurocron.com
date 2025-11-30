"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Inbox,
  MessageSquare,
  Send,
  Loader2,
  Filter,
  Facebook,
  Instagram,
  Twitter,
  Linkedin,
  Mail,
  ThumbsUp,
  ThumbsDown,
  Minus,
  Reply,
  BarChart3,
  Calendar,
  Clock,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  channel: string;
  type: string;
  author: string;
  author_avatar: string;
  content: string;
  timestamp: string;
  sentiment: string;
  replied: boolean;
  priority: string;
}

interface ChannelStats {
  channel: string;
  connected: boolean;
  followers: number;
  engagement_rate: number;
  growth_rate: number;
}

export default function InboxPage() {
  const { organization } = useAuth();
  const [activeTab, setActiveTab] = useState<"inbox" | "scheduled" | "stats">("inbox");
  const [messages, setMessages] = useState<Message[]>([]);
  const [channelStats, setChannelStats] = useState<ChannelStats[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [replyContent, setReplyContent] = useState("");
  const [channelFilter, setChannelFilter] = useState<string | null>(null);
  const [sentimentFilter, setSentimentFilter] = useState<string | null>(null);

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization, channelFilter, sentimentFilter]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);
    
    try {
      let inboxUrl = `/api/v1/channels/inbox?org_id=${organization.id}`;
      if (channelFilter) inboxUrl += `&channel=${channelFilter}`;
      if (sentimentFilter) inboxUrl += `&sentiment=${sentimentFilter}`;
      
      const [inboxRes, statsRes] = await Promise.all([
        authFetch(inboxUrl),
        authFetch(`/api/v1/channels/stats?org_id=${organization.id}`),
      ]);
      
      if (inboxRes.ok) {
        const data = await inboxRes.json();
        setMessages(data.messages || []);
      }
      
      if (statsRes.ok) {
        const data = await statsRes.json();
        setChannelStats(data.channels || []);
      }
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReply = async () => {
    if (!selectedMessage || !replyContent.trim()) return;
    
    try {
      const response = await authFetch(
        `/api/v1/channels/inbox/${selectedMessage.id}/reply?org_id=${organization?.id}`,
        {
          method: "POST",
          body: JSON.stringify({ reply_content: replyContent }),
        }
      );
      
      if (response.ok) {
        setReplyContent("");
        setSelectedMessage(null);
        fetchData();
      }
    } catch (error) {
      console.error("Failed to send reply:", error);
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case "facebook": return Facebook;
      case "instagram": return Instagram;
      case "twitter": return Twitter;
      case "linkedin": return Linkedin;
      case "email": return Mail;
      default: return MessageSquare;
    }
  };

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case "facebook": return "text-blue-400 bg-blue-400/10";
      case "instagram": return "text-pink-400 bg-pink-400/10";
      case "twitter": return "text-sky-400 bg-sky-400/10";
      case "linkedin": return "text-blue-500 bg-blue-500/10";
      case "email": return "text-purple-400 bg-purple-400/10";
      default: return "text-white/60 bg-white/5";
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case "positive": return ThumbsUp;
      case "negative": return ThumbsDown;
      default: return Minus;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive": return "text-green-400";
      case "negative": return "text-red-400";
      default: return "text-yellow-400";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) return "Just now";
    if (hours < 24) return `${hours}h ago`;
    if (hours < 48) return "Yesterday";
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center">
            <Inbox className="w-5 h-5 text-cyan-400" />
          </div>
          ChannelPulse
        </h1>
        <p className="text-white/60 mt-1">
          Unified inbox and cross-channel control center
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("inbox")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "inbox"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <MessageSquare className="w-4 h-4" />
          Inbox
        </button>
        <button
          onClick={() => setActiveTab("scheduled")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "scheduled"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <Calendar className="w-4 h-4" />
          Scheduled
        </button>
        <button
          onClick={() => setActiveTab("stats")}
          className={cn(
            "px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2",
            activeTab === "stats"
              ? "bg-electric text-midnight"
              : "bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          )}
        >
          <BarChart3 className="w-4 h-4" />
          Channel Stats
        </button>
      </div>

      {activeTab === "inbox" ? (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Filters & List */}
          <div className="lg:col-span-2 space-y-4">
            {/* Filters */}
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setChannelFilter(null)}
                className={cn(
                  "px-3 py-1.5 rounded-lg text-sm transition-colors",
                  !channelFilter ? "bg-electric text-midnight" : "bg-white/5 hover:bg-white/10"
                )}
              >
                All Channels
              </button>
              {["facebook", "instagram", "twitter", "linkedin", "email"].map((ch) => {
                const Icon = getChannelIcon(ch);
                return (
                  <button
                    key={ch}
                    onClick={() => setChannelFilter(ch)}
                    className={cn(
                      "px-3 py-1.5 rounded-lg text-sm transition-colors flex items-center gap-1.5 capitalize",
                      channelFilter === ch ? "bg-electric text-midnight" : "bg-white/5 hover:bg-white/10"
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {ch}
                  </button>
                );
              })}
            </div>

            {/* Messages */}
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-electric" />
              </div>
            ) : messages.length === 0 ? (
              <div className="card text-center py-12">
                <Inbox className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <h3 className="font-medium mb-2">No messages</h3>
                <p className="text-sm text-white/50">
                  All caught up! New messages will appear here.
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {messages.map((message, index) => {
                  const ChannelIcon = getChannelIcon(message.channel);
                  const SentimentIcon = getSentimentIcon(message.sentiment);
                  
                  return (
                    <motion.button
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.02 }}
                      onClick={() => setSelectedMessage(message)}
                      className={cn(
                        "w-full card p-4 text-left transition-all",
                        selectedMessage?.id === message.id
                          ? "ring-2 ring-electric"
                          : "hover:border-white/20",
                        !message.replied && "border-l-4 border-l-electric"
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <img
                          src={message.author_avatar}
                          alt={message.author}
                          className="w-10 h-10 rounded-full"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium">{message.author}</span>
                            <span className={cn(
                              "px-1.5 py-0.5 rounded text-xs capitalize",
                              getChannelColor(message.channel)
                            )}>
                              <ChannelIcon className="w-3 h-3 inline mr-1" />
                              {message.channel}
                            </span>
                            <SentimentIcon className={cn("w-4 h-4", getSentimentColor(message.sentiment))} />
                          </div>
                          <p className="text-sm text-white/70 line-clamp-2">
                            {message.content}
                          </p>
                          <div className="flex items-center gap-2 mt-2 text-xs text-white/40">
                            <Clock className="w-3 h-3" />
                            {formatTimestamp(message.timestamp)}
                            <span className="capitalize">• {message.type}</span>
                            {message.replied && <span className="text-green-400">• Replied</span>}
                          </div>
                        </div>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Selected Message */}
          <div className="lg:col-span-1">
            {selectedMessage ? (
              <div className="card sticky top-24">
                <div className="flex items-start gap-3 mb-4">
                  <img
                    src={selectedMessage.author_avatar}
                    alt={selectedMessage.author}
                    className="w-12 h-12 rounded-full"
                  />
                  <div>
                    <div className="font-medium">{selectedMessage.author}</div>
                    <div className="text-sm text-white/50 capitalize">
                      via {selectedMessage.channel}
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-white/5 mb-4">
                  <p className="text-white/80">{selectedMessage.content}</p>
                </div>

                <div className="text-sm text-white/40 mb-4">
                  {new Date(selectedMessage.timestamp).toLocaleString()}
                </div>

                <div className="space-y-3">
                  <textarea
                    value={replyContent}
                    onChange={(e) => setReplyContent(e.target.value)}
                    placeholder="Write your reply..."
                    className="input min-h-[100px] resize-none"
                  />
                  <button
                    onClick={handleReply}
                    disabled={!replyContent.trim()}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Send Reply
                  </button>
                </div>
              </div>
            ) : (
              <div className="card text-center py-12 sticky top-24">
                <Reply className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <h3 className="font-medium mb-2">Select a message</h3>
                <p className="text-sm text-white/50">
                  Click on a message to view details and reply
                </p>
              </div>
            )}
          </div>
        </div>
      ) : activeTab === "stats" ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {isLoading ? (
            <div className="col-span-4 flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : (
            channelStats.map((stat, index) => {
              const Icon = getChannelIcon(stat.channel);
              return (
                <motion.div
                  key={stat.channel}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center", getChannelColor(stat.channel))}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-medium capitalize">{stat.channel}</h3>
                      <span className={cn(
                        "text-xs",
                        stat.connected ? "text-green-400" : "text-white/40"
                      )}>
                        {stat.connected ? "Connected" : "Not connected"}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-white/60">Followers</span>
                      <span className="font-medium">{stat.followers.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-white/60">Engagement</span>
                      <span className="font-medium">{stat.engagement_rate}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-white/60">Growth</span>
                      <span className={cn(
                        "font-medium",
                        stat.growth_rate > 0 ? "text-green-400" : "text-red-400"
                      )}>
                        {stat.growth_rate > 0 ? "+" : ""}{stat.growth_rate}%
                      </span>
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      ) : (
        <div className="card text-center py-12">
          <Calendar className="w-12 h-12 text-white/20 mx-auto mb-4" />
          <h3 className="font-medium mb-2">Scheduled Posts</h3>
          <p className="text-sm text-white/50">
            Schedule and manage your upcoming social posts
          </p>
        </div>
      )}
    </div>
  );
}

