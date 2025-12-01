import { Metadata } from "next";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Brain,
  Target,
  Users,
  Heart,
  Zap,
  Globe,
  ArrowRight,
  Award,
  Lightbulb,
  Shield,
} from "lucide-react";
import { CTASection } from "@/components/marketing/cta-section";

export const metadata: Metadata = {
  title: "About",
  description: "Learn about NeuroCron's mission to democratize AI-powered marketing. We're building the autonomous marketing brain that replaces your entire marketing stack.",
  openGraph: {
    title: "About Us | NeuroCron",
    description: "Our mission: Make enterprise-grade AI marketing accessible to every business.",
  },
};

const values = [
  {
    icon: Brain,
    title: "AI-First Innovation",
    description: "We believe AI should amplify human creativity, not replace it. Every feature we build starts with the question: how can AI make this 10x better?",
  },
  {
    icon: Target,
    title: "Outcome Obsession",
    description: "We don't measure success by features shipped. We measure it by the results our customers achieve. Your ROI is our north star.",
  },
  {
    icon: Users,
    title: "Customer Partnership",
    description: "Our best features come from customer conversations. We build with you, not just for you. Every user has a direct line to our product team.",
  },
  {
    icon: Heart,
    title: "Radical Transparency",
    description: "No hidden fees, no surprise limitations, no marketing doublespeak. We tell you exactly what our AI can and can't do.",
  },
];

const milestones = [
  {
    year: "2023",
    quarter: "Q3",
    title: "The Idea",
    description: "Frustrated by managing 12+ marketing tools, our founders envision a single autonomous platform.",
  },
  {
    year: "2023",
    quarter: "Q4",
    title: "First Prototype",
    description: "NeuroPlan launches in closed beta with 50 early adopters. Average strategy creation drops from 40 hours to 2.",
  },
  {
    year: "2024",
    quarter: "Q1",
    title: "AutoCron Ships",
    description: "We launch autonomous execution. Campaigns now run 24/7 without human intervention.",
  },
  {
    year: "2024",
    quarter: "Q2",
    title: "500+ Customers",
    description: "Crossed 500 active customers. Platform now has 20+ modules and 30+ integrations.",
  },
  {
    year: "2024",
    quarter: "Q3",
    title: "Enterprise Ready",
    description: "SOC 2 Type II certification achieved. First Fortune 500 customer onboarded.",
  },
  {
    year: "2024",
    quarter: "Q4",
    title: "The Future",
    description: "Launching NeuroCopilot v2 and expanding to 50+ integrations. Targeting 2,000 customers.",
  },
];

const team = [
  {
    name: "Alex Chen",
    role: "CEO & Co-founder",
    bio: "Former VP of Marketing at TechCorp. 15 years in digital marketing. Frustrated tool-hopper turned platform builder.",
    initial: "AC",
    color: "from-purple-500 to-pink-500",
  },
  {
    name: "Sarah Martinez",
    role: "CTO & Co-founder",
    bio: "Ex-Google AI researcher. Built ML systems serving billions. Believes AI should be accessible to everyone.",
    initial: "SM",
    color: "from-electric to-cyan-400",
  },
  {
    name: "David Kim",
    role: "VP of Product",
    bio: "Former Product Lead at HubSpot. Obsessed with simplifying complex workflows into one-click solutions.",
    initial: "DK",
    color: "from-green-400 to-emerald-500",
  },
  {
    name: "Emma Thompson",
    role: "VP of Engineering",
    bio: "Ex-Stripe. Scaled systems from 0 to millions of transactions. Reliability is not negotiable.",
    initial: "ET",
    color: "from-orange-400 to-red-500",
  },
];

export default function AboutPage() {
  return (
    <div className="pt-32">
      {/* Hero */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Building the <span className="gradient-text">Marketing Brain</span>
            <br />
            of Tomorrow
          </h1>
          <p className="text-xl text-white/60 max-w-3xl mx-auto">
            We&apos;re on a mission to democratize enterprise-grade AI marketing. 
            Because every business deserves autonomous marketing power, 
            not just those with million-dollar budgets.
          </p>
        </div>
      </section>

      {/* Origin Story */}
      <section className="py-20 px-6 bg-midnight-50/30">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <Lightbulb className="w-12 h-12 text-electric mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Why We Built NeuroCron</h2>
          </div>
          
          <div className="space-y-6 text-lg text-white/70 leading-relaxed">
            <p>
              Our founders spent a combined 30 years in marketing leadership. They know 
              the pain of managing 15+ tools, switching between dashboards all day, and 
              still missing opportunities because you can&apos;t be everywhere at once.
            </p>
            <p>
              The breaking point came when we calculated that our teams spent more time 
              <em> managing tools</em> than actually <em>doing marketing</em>. That&apos;s 
              backwards. That&apos;s what we&apos;re fixing.
            </p>
            <p>
              NeuroCron isn&apos;t another tool to add to your stack. It&apos;s the platform 
              that replaces them all. One login. One dashboard. One AI that understands 
              your entire marketing operation and optimizes it 24/7.
            </p>
            <p className="text-white font-medium">
              We believe the future of marketing is autonomous. Not because humans aren&apos;t 
              needed—but because humans should focus on strategy and creativity, not 
              repetitive execution.
            </p>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold mb-4 text-center">Our Values</h2>
          <p className="text-xl text-white/60 text-center mb-16">
            The principles that guide everything we build
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            {values.map((value, index) => (
              <div key={index} className="card">
                <div className="w-14 h-14 rounded-2xl bg-electric/10 flex items-center justify-center mb-4">
                  <value.icon className="w-7 h-7 text-electric" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                <p className="text-white/60">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-24 px-6 bg-midnight-50/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-4 text-center">Our Journey</h2>
          <p className="text-xl text-white/60 text-center mb-16">
            From frustration to innovation
          </p>

          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-0 md:left-1/2 top-0 bottom-0 w-0.5 bg-electric/20 -translate-x-1/2" />

            {milestones.map((milestone, index) => (
              <div
                key={index}
                className={`relative flex flex-col md:flex-row gap-8 mb-12 ${
                  index % 2 === 0 ? "md:flex-row-reverse" : ""
                }`}
              >
                {/* Dot */}
                <div className="absolute left-0 md:left-1/2 w-4 h-4 rounded-full bg-electric -translate-x-1/2 mt-1" />

                {/* Content */}
                <div className={`md:w-1/2 pl-8 md:pl-0 ${index % 2 === 0 ? "md:pr-12 md:text-right" : "md:pl-12"}`}>
                  <div className="text-electric font-mono text-sm mb-1">
                    {milestone.year} {milestone.quarter}
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{milestone.title}</h3>
                  <p className="text-white/60">{milestone.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold mb-4 text-center">Leadership Team</h2>
          <p className="text-xl text-white/60 text-center mb-16">
            Marketing veterans and AI researchers building the future
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {team.map((member, index) => (
              <div key={index} className="card text-center">
                <div
                  className={`w-20 h-20 rounded-full bg-gradient-to-br ${member.color} flex items-center justify-center text-2xl font-bold mx-auto mb-4`}
                >
                  {member.initial}
                </div>
                <h3 className="text-lg font-semibold">{member.name}</h3>
                <p className="text-electric text-sm mb-3">{member.role}</p>
                <p className="text-white/60 text-sm">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="py-20 px-6 bg-midnight-50/30">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-12">Enterprise Trust</h2>
          <div className="grid grid-cols-3 gap-8">
            {[
              { icon: Shield, label: "SOC 2 Type II Certified" },
              { icon: Globe, label: "GDPR Compliant" },
              { icon: Award, label: "99.9% Uptime SLA" },
            ].map((item, index) => (
              <div key={index} className="flex flex-col items-center">
                <div className="w-16 h-16 rounded-2xl bg-green-500/10 flex items-center justify-center mb-4">
                  <item.icon className="w-8 h-8 text-green-400" />
                </div>
                <p className="text-white/80 font-medium">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Join Us CTA */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Join Our Team</h2>
          <p className="text-xl text-white/60 mb-8">
            We&apos;re building the future of marketing. Want to help?
          </p>
          <Link
            href="/careers"
            className="btn-secondary inline-flex items-center gap-2"
          >
            View Open Positions
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Final CTA */}
      <CTASection
        variant="gradient"
        title="Experience the Difference"
        subtitle="See why 500+ marketing teams chose NeuroCron"
        primaryCta={{ text: "Start Free Trial", href: "/register" }}
        secondaryCta={{ text: "Book a Demo", href: "/demo" }}
      />
    </div>
  );
}

