import { Metadata } from "next";
import { PricingTable, FeatureComparison } from "@/components/marketing/pricing-table";
import { FAQ } from "@/components/marketing/faq";
import { CTASection } from "@/components/marketing/cta-section";

export const metadata: Metadata = {
  title: "Pricing",
  description: "Simple, transparent pricing for NeuroCron. Start free, upgrade when you need more power. Plans for startups to enterprises.",
  openGraph: {
    title: "Pricing | NeuroCron",
    description: "Simple, transparent pricing. Start free, upgrade when you need more power.",
  },
};

const plans = [
  {
    id: "free",
    name: "Free",
    description: "Perfect for trying NeuroCron",
    priceMonthly: 0,
    priceYearly: 0,
    features: [
      "3 Active Campaigns",
      "Basic Analytics",
      "1 Team Member",
      "10K AI Tokens/month",
      "Email Support",
      "2 Integrations",
    ],
    cta: { text: "Get Started", href: "/register" },
  },
  {
    id: "starter",
    name: "Starter",
    description: "For growing marketing teams",
    priceMonthly: 49,
    priceYearly: 470,
    features: [
      "10 Active Campaigns",
      "Advanced Analytics",
      "3 Team Members",
      "50K AI Tokens/month",
      "NeuroCopilot Access",
      "FlowBuilder",
      "Priority Support",
      "5 Integrations",
    ],
    cta: { text: "Start Trial", href: "/register?plan=starter" },
  },
  {
    id: "growth",
    name: "Growth",
    description: "For scaling businesses",
    priceMonthly: 149,
    priceYearly: 1430,
    features: [
      "50 Active Campaigns",
      "All Analytics Features",
      "10 Team Members",
      "200K AI Tokens/month",
      "All Integrations",
      "Unlimited Flows",
      "BattleStation Access",
      "Dedicated Support",
      "Custom Reports",
    ],
    highlighted: true,
    badge: "Most Popular",
    cta: { text: "Start Trial", href: "/register?plan=growth" },
  },
  {
    id: "enterprise",
    name: "Enterprise",
    description: "For large organizations",
    priceMonthly: null,
    priceYearly: null,
    features: [
      "Unlimited Everything",
      "Custom Integrations",
      "Unlimited Team",
      "Unlimited AI Tokens",
      "SLA Guarantee",
      "Dedicated Account Manager",
      "Custom Training",
      "On-premise Option",
      "Priority Feature Requests",
    ],
    cta: { text: "Contact Sales", href: "/contact" },
  },
];

const featureCategories = [
  {
    name: "Core Features",
    features: [
      { name: "Active Campaigns", free: "3", starter: "10", growth: "50", enterprise: "Unlimited" },
      { name: "AI Tokens per month", free: "10K", starter: "50K", growth: "200K", enterprise: "Unlimited" },
      { name: "Team Members", free: "1", starter: "3", growth: "10", enterprise: "Unlimited" },
      { name: "Platform Integrations", free: "2", starter: "5", growth: "15", enterprise: "Unlimited" },
    ],
  },
  {
    name: "AI Modules",
    features: [
      { name: "NeuroPlan (Strategy)", free: true, starter: true, growth: true, enterprise: true },
      { name: "ContentForge (Content AI)", free: "Basic", starter: true, growth: true, enterprise: true },
      { name: "NeuroCopilot (Chat)", free: false, starter: true, growth: true, enterprise: true },
      { name: "BattleStation (Competitive Intel)", free: false, starter: false, growth: true, enterprise: true },
      { name: "SimulatorX (Predictions)", free: false, starter: false, growth: true, enterprise: true },
    ],
  },
  {
    name: "Automation",
    features: [
      { name: "FlowBuilder Automations", free: "3", starter: "10", growth: "Unlimited", enterprise: "Unlimited" },
      { name: "Scheduled Posts", free: "10/mo", starter: "100/mo", growth: "Unlimited", enterprise: "Unlimited" },
      { name: "AutoCron Execution", free: false, starter: true, growth: true, enterprise: true },
      { name: "Custom Triggers", free: false, starter: false, growth: true, enterprise: true },
    ],
  },
  {
    name: "Analytics & Reporting",
    features: [
      { name: "Basic Analytics", free: true, starter: true, growth: true, enterprise: true },
      { name: "Advanced Dashboards", free: false, starter: true, growth: true, enterprise: true },
      { name: "Custom Reports", free: false, starter: false, growth: true, enterprise: true },
      { name: "White-label Reports", free: false, starter: false, growth: false, enterprise: true },
    ],
  },
  {
    name: "Support",
    features: [
      { name: "Email Support", free: true, starter: true, growth: true, enterprise: true },
      { name: "Priority Support", free: false, starter: true, growth: true, enterprise: true },
      { name: "Dedicated Success Manager", free: false, starter: false, growth: false, enterprise: true },
      { name: "SLA Guarantee", free: false, starter: false, growth: false, enterprise: true },
    ],
  },
];

const pricingFaqs = [
  {
    question: "What happens after my free trial ends?",
    answer: "After your 14-day trial, you'll be automatically moved to the Free plan unless you choose to upgrade. No charges are made without your explicit consent.",
  },
  {
    question: "Can I change plans at any time?",
    answer: "Yes! You can upgrade or downgrade your plan at any time. When upgrading, you'll get immediate access to new features. When downgrading, the change takes effect at the end of your billing cycle.",
  },
  {
    question: "What are AI Tokens?",
    answer: "AI Tokens are used for AI-powered features like content generation, strategy creation, and NeuroCopilot interactions. Each operation uses a certain number of tokens based on complexity. Average users consume 20-30K tokens per month.",
  },
  {
    question: "Do you offer discounts for annual billing?",
    answer: "Yes! Annual billing saves you 20% compared to monthly billing. For example, the Growth plan is $149/month or $119/month when billed annually.",
  },
  {
    question: "What payment methods do you accept?",
    answer: "We accept all major credit cards (Visa, Mastercard, American Express) and can arrange invoice billing for Enterprise customers.",
  },
  {
    question: "Is there a money-back guarantee?",
    answer: "Yes, we offer a 30-day money-back guarantee on all paid plans. If you're not satisfied, contact us within 30 days for a full refund.",
  },
];

export default function PricingPage() {
  return (
    <div className="pt-32">
      <PricingTable
        title="Simple, Transparent Pricing"
        subtitle="Start free, upgrade when you need more power"
        plans={plans}
      />

      <FeatureComparison categories={featureCategories} />

      <FAQ
        title="Pricing FAQ"
        subtitle="Common questions about our plans"
        faqs={pricingFaqs}
      />

      <CTASection
        variant="gradient"
        title="Start Your Free Trial Today"
        subtitle="14 days of full access. No credit card required."
        primaryCta={{ text: "Start Free Trial", href: "/register" }}
        secondaryCta={{ text: "Talk to Sales", href: "/contact" }}
      />
    </div>
  );
}

