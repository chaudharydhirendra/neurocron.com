"use client";

import { useState, useRef, useEffect } from "react";
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
} from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const suggestions = [
  { icon: Megaphone, text: "Create a new campaign for product launch" },
  { icon: BarChart3, text: "Analyze my last week's performance" },
  { icon: Lightbulb, text: "Generate content ideas for social media" },
  { icon: Zap, text: "Optimize my current campaigns" },
];

export default function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm NeuroCopilot, your AI marketing assistant. I can help you create campaigns, analyze performance, generate content, and optimize your marketing. What would you like to do today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      const assistantMessage: Message = {
        role: "assistant",
        content: generateResponse(input),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const generateResponse = (input: string): string => {
    const lower = input.toLowerCase();
    
    if (lower.includes("campaign") && (lower.includes("create") || lower.includes("new"))) {
      return "I'd be happy to help you create a new campaign! To get started, I'll need a few details:\n\n1. **Campaign Name**: What would you like to call this campaign?\n2. **Goal**: What's the primary objective? (Brand awareness, Lead generation, Sales, etc.)\n3. **Budget**: What's your budget for this campaign?\n4. **Duration**: When should it start and end?\n\nOnce you provide these details, I'll generate a complete strategy including targeting, content, and channel recommendations.";
    }
    
    if (lower.includes("analyze") || lower.includes("performance")) {
      return "📊 **Performance Summary (Last 7 Days)**\n\n• **Total Spend**: $8,450 (+12% vs previous week)\n• **Impressions**: 1.2M (+8%)\n• **Clicks**: 24.5K (+15%)\n• **Conversions**: 567 (+23%)\n• **ROAS**: 3.2x\n\n**Key Insights:**\n1. Your 'Product Launch' campaign is outperforming expectations by 34%\n2. Instagram is your best-performing channel with 2.1x ROAS\n3. Ad creative #3 has the highest CTR (4.2%)\n\n**Recommendations:**\n- Increase budget for Instagram ads\n- A/B test new creatives on Facebook\n- Consider expanding to TikTok based on audience demographics\n\nWould you like me to implement any of these recommendations?";
    }
    
    if (lower.includes("content") || lower.includes("ideas")) {
      return "🎨 **Content Ideas for Your Brand**\n\nHere are 5 content ideas based on your audience and trending topics:\n\n1. **Behind-the-Scenes**: Show your team's daily workflow\n2. **Customer Spotlight**: Feature a success story from a recent client\n3. **Industry Trend Analysis**: Create a carousel about emerging trends\n4. **Product Tips**: Quick tips for getting the most out of your product\n5. **User-Generated Content**: Repost and celebrate customer content\n\nWant me to generate full content briefs for any of these? I can also create the actual posts for you.";
    }
    
    return "I understand you're asking about marketing. I can help with:\n\n• **Creating campaigns** - I'll build complete strategies with targeting, content, and budget allocation\n• **Analyzing performance** - Get insights on what's working and what needs improvement\n• **Generating content** - I'll create posts, ads, emails, and more\n• **Optimizing campaigns** - Automatic improvements based on performance data\n\nWhat would you like to focus on?";
  };

  const handleSuggestionClick = (text: string) => {
    setInput(text);
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
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((message, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex gap-3 ${
              message.role === "user" ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                message.role === "assistant"
                  ? "bg-neural-gradient"
                  : "bg-electric"
              }`}
            >
              {message.role === "assistant" ? (
                <Sparkles className="w-4 h-4" />
              ) : (
                <User className="w-4 h-4" />
              )}
            </div>
            <div
              className={`max-w-[70%] p-4 rounded-2xl ${
                message.role === "assistant"
                  ? "bg-white/5"
                  : "bg-electric/20"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <p className="text-xs text-white/30 mt-2">
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
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
              <Loader2 className="w-5 h-5 animate-spin text-electric" />
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="mb-4">
          <p className="text-sm text-white/50 mb-3">Suggestions:</p>
          <div className="grid grid-cols-2 gap-2">
            {suggestions.map((suggestion, i) => (
              <button
                key={i}
                onClick={() => handleSuggestionClick(suggestion.text)}
                className="flex items-center gap-3 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors text-left"
              >
                <suggestion.icon className="w-5 h-5 text-electric" />
                <span className="text-sm">{suggestion.text}</span>
              </button>
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
          className="btn-primary px-4 disabled:opacity-50"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

