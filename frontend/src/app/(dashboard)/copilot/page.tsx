"use client";

import { useState, useRef, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  Send,
  Sparkles,
  User,
  Loader2,
  Lightbulb,
  Zap,
  BarChart3,
  Megaphone,
  Copy,
  Check,
  RefreshCw,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  suggestions?: string[];
  isError?: boolean;
}

const initialSuggestions = [
  { icon: Megaphone, text: "Create a new campaign for product launch" },
  { icon: BarChart3, text: "Analyze my last week's performance" },
  { icon: Lightbulb, text: "Generate content ideas for social media" },
  { icon: Zap, text: "Optimize my current campaigns" },
];

export default function CopilotPage() {
  const searchParams = useSearchParams();
  const { organization } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm NeuroCopilot, your AI marketing assistant. I can help you create campaigns, analyze performance, generate content, and optimize your marketing. What would you like to do today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check for initial query from URL
  useEffect(() => {
    const query = searchParams.get("q");
    if (query && messages.length === 1) {
      setInput(query);
    }
  }, [searchParams, messages.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateId = () => Math.random().toString(36).substring(2, 9);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const response = await authFetch("/api/v1/copilot/chat", {
        method: "POST",
        body: JSON.stringify({
          content: currentInput,
          org_id: organization?.id,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: data.message,
        timestamp: new Date(),
        suggestions: data.suggestions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: generateId(),
        role: "assistant",
        content:
          "I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (id: string, content: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleRetry = async (messageIndex: number) => {
    // Find the user message before the error
    const userMessage = messages
      .slice(0, messageIndex)
      .reverse()
      .find((m) => m.role === "user");
    if (userMessage) {
      setInput(userMessage.content);
      // Remove the error message and the user message
      setMessages((prev) => prev.slice(0, messageIndex - 1));
    }
  };

  const handleSuggestionClick = (text: string) => {
    setInput(text);
  };

  const formatContent = (content: string) => {
    // Simple markdown-like formatting
    return content
      .split("\n")
      .map((line, i) => {
        // Headers
        if (line.startsWith("**") && line.endsWith("**")) {
          return (
            <strong key={i} className="block text-white">
              {line.slice(2, -2)}
            </strong>
          );
        }
        // Bold text
        const boldRegex = /\*\*(.*?)\*\*/g;
        if (boldRegex.test(line)) {
          const parts = line.split(boldRegex);
          return (
            <span key={i} className="block">
              {parts.map((part, j) =>
                j % 2 === 1 ? (
                  <strong key={j} className="text-white">
                    {part}
                  </strong>
                ) : (
                  part
                )
              )}
            </span>
          );
        }
        // List items
        if (line.startsWith("• ") || line.startsWith("- ")) {
          return (
            <li key={i} className="ml-4">
              {line.slice(2)}
            </li>
          );
        }
        // Numbered items
        if (/^\d+\.\s/.test(line)) {
          return (
            <li key={i} className="ml-4">
              {line}
            </li>
          );
        }
        // Empty lines
        if (!line.trim()) {
          return <br key={i} />;
        }
        return (
          <span key={i} className="block">
            {line}
          </span>
        );
      });
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-neural-gradient flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold">NeuroCopilot</h1>
            <p className="text-sm text-white/60">Your AI Marketing Assistant</p>
          </div>
        </div>
        {organization && (
          <div className="text-sm text-white/40">
            {organization.name}
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.map((message, i) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
              "flex gap-3",
              message.role === "user" && "flex-row-reverse"
            )}
          >
            <div
              className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
                message.role === "assistant" ? "bg-neural-gradient" : "bg-electric"
              )}
            >
              {message.role === "assistant" ? (
                <Sparkles className="w-4 h-4" />
              ) : (
                <User className="w-4 h-4" />
              )}
            </div>
            <div
              className={cn(
                "max-w-[70%] p-4 rounded-2xl relative group",
                message.role === "assistant"
                  ? message.isError
                    ? "bg-red-500/10 border border-red-500/20"
                    : "bg-white/5"
                  : "bg-electric/20"
              )}
            >
              <div className="text-sm whitespace-pre-wrap">
                {formatContent(message.content)}
              </div>

              {/* Suggestions */}
              {message.suggestions && message.suggestions.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-xs text-white/40 mb-2">Suggestions:</p>
                  <div className="flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion, j) => (
                      <button
                        key={j}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="text-xs px-3 py-1.5 rounded-lg bg-white/5 hover:bg-electric/10 hover:text-electric transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between mt-3">
                <p className="text-xs text-white/30">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>

                {message.role === "assistant" && (
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleCopy(message.id, message.content)}
                      className="p-1.5 rounded-md hover:bg-white/10 transition-colors"
                      title="Copy"
                    >
                      {copiedId === message.id ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4 text-white/40" />
                      )}
                    </button>
                    {message.isError && (
                      <button
                        onClick={() => handleRetry(i)}
                        className="p-1.5 rounded-md hover:bg-white/10 transition-colors"
                        title="Retry"
                      >
                        <RefreshCw className="w-4 h-4 text-white/40" />
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-lg bg-neural-gradient flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl bg-white/5">
              <div className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-electric" />
                <span className="text-sm text-white/60">Thinking...</span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="mb-4">
          <p className="text-sm text-white/50 mb-3">Get started:</p>
          <div className="grid grid-cols-2 gap-2">
            {initialSuggestions.map((suggestion, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                onClick={() => handleSuggestionClick(suggestion.text)}
                className="flex items-center gap-3 p-4 rounded-xl bg-white/5 hover:bg-white/10 hover:border-electric/30 border border-transparent transition-all text-left group"
              >
                <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center group-hover:bg-electric/20 transition-colors">
                  <suggestion.icon className="w-5 h-5 text-electric" />
                </div>
                <span className="text-sm">{suggestion.text}</span>
              </motion.button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask NeuroCopilot anything..."
          className="flex-1 input"
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="btn-primary px-4 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
