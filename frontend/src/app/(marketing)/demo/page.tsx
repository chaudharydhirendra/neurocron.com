"use client";

import { useState } from "react";
import { Metadata } from "next";
import {
  Calendar,
  Clock,
  Check,
  Play,
  Users,
  Zap,
  BarChart3,
  ArrowRight,
  Video,
  MessageSquare,
} from "lucide-react";
import { CTASection } from "@/components/marketing/cta-section";

const benefits = [
  "Personalized walkthrough of key features",
  "Live Q&A with our product experts",
  "Custom strategy recommendations",
  "See how NeuroCron fits your workflow",
  "Get answers to technical questions",
];

const features = [
  {
    icon: Zap,
    title: "AutoCron Demo",
    description: "See autonomous campaign execution in action",
  },
  {
    icon: BarChart3,
    title: "Analytics Deep Dive",
    description: "Explore unified cross-channel analytics",
  },
  {
    icon: Users,
    title: "AI Persona Generation",
    description: "Watch AI create customer personas live",
  },
];

export default function DemoPage() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    company: "",
    role: "",
    teamSize: "",
    message: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Submit to API
    console.log("Demo request:", formData);
    // Show success message
    alert("Demo request submitted! We'll be in touch within 24 hours.");
  };

  return (
    <div className="pt-32">
      {/* Hero */}
      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Content */}
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-electric/20 mb-6">
                <Video className="w-4 h-4 text-electric" />
                <span className="text-sm">30-minute personalized demo</span>
              </div>
              
              <h1 className="text-4xl md:text-5xl font-bold mb-6">
                See NeuroCron
                <br />
                <span className="gradient-text">In Action</span>
              </h1>
              
              <p className="text-xl text-white/60 mb-8">
                Get a personalized walkthrough of the autonomous marketing platform
                that&apos;s changing how teams work.
              </p>

              {/* Benefits */}
              <ul className="space-y-3 mb-8">
                {benefits.map((benefit, index) => (
                  <li key={index} className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0">
                      <Check className="w-3 h-3 text-green-400" />
                    </div>
                    <span className="text-white/80">{benefit}</span>
                  </li>
                ))}
              </ul>

              {/* Demo Preview Cards */}
              <div className="grid grid-cols-3 gap-3">
                {features.map((feature, index) => (
                  <div
                    key={index}
                    className="p-4 rounded-xl bg-white/5 border border-white/10"
                  >
                    <feature.icon className="w-6 h-6 text-electric mb-2" />
                    <div className="text-sm font-medium">{feature.title}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Form */}
            <div className="card lg:p-8">
              <h2 className="text-2xl font-bold mb-6">Book Your Demo</h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-white/60 mb-2">
                      First Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.firstName}
                      onChange={(e) =>
                        setFormData({ ...formData, firstName: e.target.value })
                      }
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-white/60 mb-2">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.lastName}
                      onChange={(e) =>
                        setFormData({ ...formData, lastName: e.target.value })
                      }
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    Work Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                  />
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    Company *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.company}
                    onChange={(e) =>
                      setFormData({ ...formData, company: e.target.value })
                    }
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-white/60 mb-2">
                      Your Role
                    </label>
                    <select
                      value={formData.role}
                      onChange={(e) =>
                        setFormData({ ...formData, role: e.target.value })
                      }
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                    >
                      <option value="">Select...</option>
                      <option value="cmo">CMO / VP Marketing</option>
                      <option value="director">Marketing Director</option>
                      <option value="manager">Marketing Manager</option>
                      <option value="growth">Growth Lead</option>
                      <option value="founder">Founder / CEO</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-white/60 mb-2">
                      Team Size
                    </label>
                    <select
                      value={formData.teamSize}
                      onChange={(e) =>
                        setFormData({ ...formData, teamSize: e.target.value })
                      }
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                    >
                      <option value="">Select...</option>
                      <option value="1-5">1-5 people</option>
                      <option value="6-20">6-20 people</option>
                      <option value="21-50">21-50 people</option>
                      <option value="51-200">51-200 people</option>
                      <option value="200+">200+ people</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-white/60 mb-2">
                    What would you like to see? (optional)
                  </label>
                  <textarea
                    value={formData.message}
                    onChange={(e) =>
                      setFormData({ ...formData, message: e.target.value })
                    }
                    rows={3}
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition resize-none"
                    placeholder="Tell us about your marketing challenges..."
                  />
                </div>

                <button
                  type="submit"
                  className="w-full btn-primary flex items-center justify-center gap-2 py-4"
                >
                  <Calendar className="w-5 h-5" />
                  Request Demo
                </button>

                <p className="text-center text-sm text-white/40">
                  We&apos;ll contact you within 24 hours to schedule
                </p>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* What to Expect */}
      <section className="py-20 px-6 bg-midnight-50/30">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-12">What to Expect</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Clock,
                title: "30 Minutes",
                description: "Quick but comprehensive overview tailored to your needs",
              },
              {
                icon: Users,
                title: "1-on-1 Session",
                description: "Personal attention from a product expert",
              },
              {
                icon: MessageSquare,
                title: "Q&A Included",
                description: "Get all your questions answered live",
              },
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className="w-14 h-14 rounded-2xl bg-electric/10 flex items-center justify-center mx-auto mb-4">
                  <item.icon className="w-7 h-7 text-electric" />
                </div>
                <h3 className="font-semibold mb-2">{item.title}</h3>
                <p className="text-white/60 text-sm">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Video Preview */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Want a Quick Preview?</h2>
            <p className="text-white/60">
              Watch our 2-minute product overview video
            </p>
          </div>

          <div className="aspect-video rounded-2xl bg-gradient-to-br from-electric/20 to-purple-500/20 flex items-center justify-center cursor-pointer group">
            <div className="w-20 h-20 rounded-full bg-electric flex items-center justify-center group-hover:scale-110 transition-transform">
              <Play className="w-8 h-8 text-midnight ml-1" />
            </div>
          </div>
        </div>
      </section>

      {/* Alternative CTA */}
      <CTASection
        title="Prefer to Explore on Your Own?"
        subtitle="Start your free 14-day trial and discover NeuroCron at your own pace"
        primaryCta={{ text: "Start Free Trial", href: "/register" }}
        features={["No credit card required", "Full platform access", "Cancel anytime"]}
      />
    </div>
  );
}

