// Documentation content for NeuroCron
// Each doc has metadata and content

export interface DocPage {
  title: string;
  description: string;
  category: string;
  readTime: string;
  lastUpdated: string;
  content: string;
  nextPage?: { title: string; href: string };
  prevPage?: { title: string; href: string };
}

// Helper to create code blocks in template literals
const codeBlock = (lang: string, code: string) => "```" + lang + "\n" + code + "\n```";

export const docsContent: Record<string, DocPage> = {
  // ==========================================
  // GETTING STARTED
  // ==========================================
  "quick-start": {
    title: "Quick Start Guide",
    description: "Get up and running with NeuroCron in under 5 minutes",
    category: "Getting Started",
    readTime: "5 min",
    lastUpdated: "2024-11-28",
    nextPage: { title: "Account Setup", href: "/docs/account-setup" },
    content: `
# Quick Start Guide

Welcome to NeuroCron! This guide will help you get up and running with the autonomous marketing platform in under 5 minutes.

## Prerequisites

Before you begin, make sure you have:
- A NeuroCron account (sign up at [neurocron.com/register](/register))
- At least one marketing channel to connect (Google Ads, Meta, LinkedIn, etc.)
- Basic understanding of your marketing goals

## Step 1: Create Your Account

1. Visit [neurocron.com/register](/register)
2. Enter your email and create a password
3. Verify your email address
4. Complete the onboarding questionnaire

## Step 2: Set Up Your Organization

After logging in, you'll be prompted to create your organization:

- **Organization Name:** Your Company Name
- **Industry:** Select your industry
- **Team Size:** Number of marketing team members
- **Primary Goal:** What you want to achieve

This information helps NeuroCron's AI understand your business context.

## Step 3: Connect Your First Integration

Navigate to **Settings → Integrations** and connect at least one platform:

### Recommended First Integrations:
- **Google Ads** - For search and display advertising
- **Meta Ads** - For Facebook and Instagram campaigns
- **Google Analytics** - For website traffic data

Click "Connect" next to your chosen platform and follow the OAuth flow.

## Step 4: Generate Your First Strategy

1. Go to **Strategy → NeuroPlan**
2. Click "Generate Strategy"
3. Answer the AI's questions about your goals
4. Wait 30-60 seconds for your personalized strategy

NeuroPlan will create a complete 12-month marketing roadmap.

## Step 5: Launch Your First Campaign

1. Navigate to **Campaigns → New Campaign**
2. Select a strategy from NeuroPlan or start fresh
3. Choose your channels and budget
4. Let AutoCron handle the execution

## What's Next?

- [Connect more integrations](/docs/integrations)
- [Explore NeuroCopilot](/docs/neurocopilot) - your AI marketing assistant
- [Set up automations](/docs/flowbuilder) with FlowBuilder
- [Review analytics](/docs/insightcortex) in InsightCortex
    `,
  },

  "account-setup": {
    title: "Account Setup",
    description: "Configure your NeuroCron account and organization settings",
    category: "Getting Started",
    readTime: "3 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Quick Start Guide", href: "/docs/quick-start" },
    nextPage: { title: "Connecting Integrations", href: "/docs/integrations" },
    content: `
# Account Setup

Learn how to configure your NeuroCron account for optimal performance.

## Account Types

### Individual Account
Perfect for freelancers and solo marketers:
- Single user access
- All core features
- Up to 10 campaigns

### Team Account
For growing marketing teams:
- Multiple team members
- Role-based permissions
- Shared workspaces

### Enterprise Account
For large organizations:
- Unlimited users
- Custom integrations
- SSO/SAML authentication

## Organization Settings

### Basic Information

Navigate to **Settings → Organization** to configure:

| Setting | Description |
|---------|-------------|
| Organization Name | Your company or brand name |
| Industry | Helps AI understand your market |
| Website URL | Used for audits and analytics |
| Logo | Displayed in reports |
| Timezone | For scheduling and reporting |

### Team Management

Invite team members at **Settings → Team**:

- **Email:** teammate@company.com
- **Role:** Admin, Editor, or Viewer
- **Permissions:** Customize access levels

## Security Settings

Protect your account at **Settings → Security**:

- **Password** - Change your password
- **Two-Factor Authentication** - Enable 2FA
- **Sessions** - View and manage active sessions
- **API Keys** - Generate keys for integrations
    `,
  },

  "integrations": {
    title: "Connecting Integrations",
    description: "Connect your marketing tools and platforms to NeuroCron",
    category: "Getting Started",
    readTime: "10 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Account Setup", href: "/docs/account-setup" },
    nextPage: { title: "Your First Campaign", href: "/docs/first-campaign" },
    content: `
# Connecting Integrations

NeuroCron integrates with 50+ marketing platforms to create a unified marketing command center.

## How Integrations Work

NeuroCron uses OAuth 2.0 for secure, one-click integrations. When you connect a platform:

1. You're redirected to the platform's authorization page
2. You grant NeuroCron specific permissions
3. We securely store encrypted access tokens
4. AutoCron can now read/write data on your behalf

**Your credentials are never stored** - only encrypted tokens that can be revoked at any time.

## Available Integrations

### Advertising Platforms

| Platform | Features | Status |
|----------|----------|--------|
| Google Ads | Full campaign management | ✅ Live |
| Meta Ads | Facebook & Instagram ads | ✅ Live |
| LinkedIn Ads | B2B advertising | ✅ Live |
| Twitter/X Ads | Promoted tweets | ✅ Live |
| TikTok Ads | Video ads | ✅ Live |

### Analytics & Data

| Platform | Features | Status |
|----------|----------|--------|
| Google Analytics 4 | Traffic, conversions | ✅ Live |
| Google Search Console | SEO data | ✅ Live |

### CRM & Marketing Automation

| Platform | Features | Status |
|----------|----------|--------|
| HubSpot | CRM, email | ✅ Live |
| Salesforce | CRM, leads | ✅ Live |
| Mailchimp | Email campaigns | ✅ Live |

### E-Commerce

| Platform | Features | Status |
|----------|----------|--------|
| Shopify | Products, orders | ✅ Live |
| Stripe | Payments | ✅ Live |

## Connecting Your First Integration

### Step-by-Step: Google Ads

1. Navigate to **Settings → Integrations**
2. Find "Google Ads" and click **Connect**
3. Select your Google account
4. Choose which ad accounts to connect
5. Grant required permissions
6. Click **Allow**

## Troubleshooting

### "Connection Failed"
- Check your internet connection
- Ensure you have admin access to the platform
- Try incognito mode to clear cached sessions

### "Insufficient Permissions"
- Re-authorize with an admin account
- Contact your platform admin for access
    `,
  },

  "first-campaign": {
    title: "Creating Your First Campaign",
    description: "Step-by-step guide to launching your first marketing campaign",
    category: "Getting Started",
    readTime: "8 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Connecting Integrations", href: "/docs/integrations" },
    nextPage: { title: "NeuroPlan", href: "/docs/neuroplan" },
    content: `
# Creating Your First Campaign

This tutorial walks you through creating and launching your first campaign with NeuroCron.

## Before You Begin

Ensure you have:
- ✅ Connected at least one advertising platform
- ✅ Set up your organization profile
- ✅ Defined basic marketing goals

## Step 1: Start a New Campaign

1. Click **Campaigns** in the sidebar
2. Click the **+ New Campaign** button
3. Choose your starting point:
   - **From Strategy** - Use NeuroPlan recommendations
   - **From Template** - Use a pre-built template
   - **From Scratch** - Build manually

## Step 2: Campaign Basics

Fill in the campaign details:

- **Campaign Name:** Q4 Holiday Sale
- **Description:** Drive holiday season sales
- **Campaign Type:** Sales / Lead Gen / Brand Awareness

### Campaign Types

| Type | Best For | Key Metrics |
|------|----------|-------------|
| Sales | E-commerce | ROAS, conversions |
| Lead Gen | B2B, services | CPL, lead quality |
| Brand Awareness | New products | Reach, impressions |

## Step 3: Target Audience

Define who you want to reach using AudienceGenome or manual targeting:

- Demographics (age, location, income)
- Interests and behaviors
- Custom audiences from integrations

## Step 4: Select Channels

Choose where your ads will run:
- Google Search
- Google Display
- Facebook Feed
- Instagram Feed/Stories
- LinkedIn Feed

## Step 5: Set Budget & Schedule

Configure your spend:
- **Daily Budget** - Fixed daily spend
- **Lifetime Budget** - Total for campaign
- **AI-Managed** - AutoCron optimizes

## Step 6: Create Ad Content

Use ContentForge to auto-create ads or upload your own:
- Headlines (multiple variants)
- Descriptions
- Images/Videos
- CTAs

## Step 7: Review & Launch

Before launching, review:
- ✅ Campaign settings
- ✅ Target audience
- ✅ Budget and schedule
- ✅ Ad creatives

Click **Launch Campaign** to go live!
    `,
  },

  // ==========================================
  // CORE MODULES
  // ==========================================
  "neuroplan": {
    title: "NeuroPlan: Strategy Generation",
    description: "AI-powered marketing strategy generation and planning",
    category: "Core Modules",
    readTime: "12 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Your First Campaign", href: "/docs/first-campaign" },
    nextPage: { title: "AutoCron", href: "/docs/autocron" },
    content: `
# NeuroPlan: Strategy Generation

NeuroPlan is NeuroCron's AI-powered strategy engine that generates complete marketing plans.

## Overview

NeuroPlan creates:
- 📅 **12-month marketing roadmap**
- 💰 **Budget allocation recommendations**
- 📊 **Channel prioritization**
- 🎯 **KPI targets and benchmarks**
- 📝 **Content calendar themes**

## How It Works

### 1. Context Gathering
NeuroPlan collects information through your organization profile, connected integrations, and an AI-guided questionnaire.

### 2. Analysis Phase
The AI analyzes your current performance, competitors (via BattleStation), industry trends, and seasonal patterns.

### 3. Strategy Generation
NeuroPlan creates a comprehensive strategy including market analysis, target audiences, channel strategy, campaign calendar, and KPI framework.

## Using NeuroPlan

### Generating a New Strategy

1. Navigate to **Strategy → NeuroPlan**
2. Click **Generate New Strategy**
3. Answer the strategy questionnaire
4. Click **Generate Strategy**
5. Wait 30-90 seconds for AI processing

### Strategy Output

Your generated strategy includes:

**Executive Summary** - High-level overview of recommended approach

**Market Analysis** - Industry trends, competitor landscape, SWOT analysis

**Target Audiences** - Detailed personas with demographics, pain points, buying triggers

**Channel Strategy** - Which channels to prioritize and budget allocation

**Campaign Calendar** - 12-month calendar with major campaigns and content themes

**KPI Framework** - Metrics, current baselines, and targets

## Customizing Strategies

Click any section to modify recommendations. Don't like a section? Click **Regenerate** for alternatives.

## Best Practices

1. **Complete Your Profile** - More context = better strategies
2. **Connect Integrations** - Historical data improves recommendations
3. **Be Specific in Goals** - "Increase e-commerce revenue by 30% in Q4" is better than "increase revenue"
4. **Review Competitor Data** - Ensure BattleStation has competitors tracked
5. **Iterate Regularly** - Refresh strategies quarterly
    `,
  },

  "autocron": {
    title: "AutoCron: Autonomous Execution",
    description: "24/7 autonomous campaign execution and optimization",
    category: "Core Modules",
    readTime: "10 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "NeuroPlan", href: "/docs/neuroplan" },
    nextPage: { title: "ContentForge", href: "/docs/contentforge" },
    content: `
# AutoCron: Autonomous Execution

AutoCron is NeuroCron's autonomous execution engine that runs your marketing campaigns 24/7.

## What is AutoCron?

AutoCron is an AI-powered system that:
- 🤖 **Executes campaigns** across all connected platforms
- 📊 **Optimizes performance** in real-time
- 💰 **Manages budgets** dynamically
- 🎯 **Adjusts targeting** based on results
- ⚠️ **Alerts you** when human input is required

## The AutoCron Loop

AutoCron runs continuously:

1. **MONITOR** - Collect real-time performance
2. **ANALYZE** - Compare against goals & benchmarks
3. **DECIDE** - AI determines optimal actions
4. **EXECUTE** - Implement changes automatically
5. **Repeat**

### Optimization Frequency

| Action Type | Frequency |
|-------------|-----------|
| Bid adjustments | Every 15 minutes |
| Budget reallocation | Hourly |
| Audience refinement | Daily |
| Creative rotation | Daily |

## AutoCron Features

### Automated Bid Management
Adjusts bids based on conversion probability, time of day, device, and competition.

### Budget Optimization
Daily pacing, performance allocation, emergency stops, opportunity capture.

### Audience Optimization
Expands to similar segments, excludes low-converting audiences, creates lookalikes.

### Creative Optimization
A/B tests variants, pauses underperformers, requests new creatives.

## Configuring AutoCron

### Automation Levels

| Level | Description | Human Input |
|-------|-------------|-------------|
| Full Auto | Complete autonomy | Minimal |
| Assisted | AI suggests, you approve | Moderate |
| Manual | You control, AI monitors | High |

### Setting Goals

Define what AutoCron optimizes for:
- Primary Goal: Conversions
- Secondary Goal: Maintain ROAS above 3x
- Constraints: Don't exceed $100/day

## Monitoring

View all AutoCron actions in the Activity Log. Get alerts when campaigns need attention or hit budget limits.
    `,
  },

  "contentforge": {
    title: "ContentForge: AI Content Creation",
    description: "Generate marketing content with AI",
    category: "Core Modules",
    readTime: "10 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "AutoCron", href: "/docs/autocron" },
    nextPage: { title: "InsightCortex", href: "/docs/insightcortex" },
    content: `
# ContentForge: AI Content Creation

ContentForge is NeuroCron's AI-powered content studio that creates marketing content at scale.

## Overview

ContentForge generates:
- 📝 **Blog articles** - SEO-optimized long-form content
- 📱 **Social posts** - Platform-optimized updates
- ✉️ **Email campaigns** - Newsletters and sequences
- 🎯 **Ad copy** - Headlines, descriptions, CTAs
- 📄 **Landing pages** - Conversion-focused pages

## Content Types

### Blog Articles
Generate SEO-optimized articles with meta titles, descriptions, and internal linking suggestions.

### Social Media Posts
Platform-optimized content for LinkedIn, Twitter, Facebook, and Instagram.

### Email Campaigns
Full email sequences with subject lines, preview text, body copy, and CTAs.

### Ad Copy
Multi-variant ad creative with headlines, descriptions, and CTA options.

## Using ContentForge

### Quick Generation

1. Navigate to **Content → ContentForge**
2. Select content type
3. Provide context (topic, audience, tone)
4. Click **Generate**
5. Review and edit output

### Brand Voice Training

Train ContentForge on your brand:
1. Go to **Settings → Brand Voice**
2. Upload examples of your content
3. Define voice attributes (formal/casual, technical/simple)
4. Add words to use/avoid

## AI Models

ContentForge uses multiple AI models:

| Task | Model | Strength |
|------|-------|----------|
| Strategy content | Claude | Deep analysis |
| Creative writing | GPT-4 | Creative flair |
| Quick generation | Llama 3.1 | Speed |

## Best Practices

1. **Provide Context** - More context = better output
2. **Always Edit** - AI is a starting point
3. **Use Variants** - Generate multiple and test
4. **Check Facts** - AI can hallucinate
    `,
  },

  "insightcortex": {
    title: "InsightCortex: Analytics Hub",
    description: "Unified marketing analytics and reporting",
    category: "Core Modules",
    readTime: "10 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "ContentForge", href: "/docs/contentforge" },
    nextPage: { title: "FlowBuilder", href: "/docs/flowbuilder" },
    content: `
# InsightCortex: Analytics Hub

InsightCortex is NeuroCron's unified analytics platform that aggregates data from all channels.

## Overview

InsightCortex provides:
- 📊 **Unified dashboards** - All metrics in one place
- 📈 **Cross-channel attribution** - Understand the full journey
- 🔮 **Predictive analytics** - Forecast future performance
- 📋 **Automated reports** - Scheduled delivery to stakeholders

## Dashboard Overview

The main dashboard shows:
- KPI Summary (Spend, Conversions, ROAS, CPA)
- Performance Over Time
- Channel Breakdown
- Top Campaigns

## Data Sources

InsightCortex aggregates from all connected platforms:
- Advertising data (Google, Meta, LinkedIn)
- Analytics data (GA4, website events)
- CRM data (HubSpot, Salesforce)
- E-commerce data (Shopify, Stripe)

## Attribution Models

| Model | Description | Best For |
|-------|-------------|----------|
| Last Click | 100% credit to last touch | Direct response |
| First Click | 100% credit to first touch | Brand awareness |
| Linear | Equal credit all touches | Balanced view |
| Data-Driven | AI-determined | Best accuracy |

## Custom Dashboards

Create custom dashboards with drag-and-drop widgets:
- Metric cards
- Line/bar/pie charts
- Tables and funnels
- Geographic maps

## Automated Reports

Configure automated reports:
- Choose recipients and schedule
- Select format (PDF, Excel)
- Include executive summary, channel performance, recommendations
    `,
  },

  "flowbuilder": {
    title: "FlowBuilder: Automation",
    description: "Visual automation builder for marketing workflows",
    category: "Core Modules",
    readTime: "8 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "InsightCortex", href: "/docs/insightcortex" },
    nextPage: { title: "NeuroCopilot", href: "/docs/neurocopilot" },
    content: `
# FlowBuilder: Automation

FlowBuilder is NeuroCron's visual automation builder for marketing workflows.

## Overview

FlowBuilder enables:
- 🔄 **Visual workflow design** - Drag and drop interface
- ⚡ **Trigger-based automation** - React to events in real-time
- 🔀 **Conditional logic** - Branch based on conditions
- 📊 **Performance tracking** - Monitor automation results

## Flow Components

### Triggers
Events that start a flow: Form submission, Purchase, Abandoned cart, Page visit, Time-based, API event.

### Actions
What happens in the flow: Send email, Send SMS, Create task, Update contact, Add to audience, Post social.

### Conditions
Decision points: IF condition THEN path A ELSE path B

### Delays
Timing controls: Wait X minutes/hours/days

## Building Flows

1. Go to **Automation → FlowBuilder**
2. Click **+ New Flow**
3. Choose starting trigger
4. Drag components onto the canvas
5. Configure each step
6. Test and activate

## Pre-Built Templates

- **Welcome Series** - Onboard new signups
- **Abandoned Cart** - Recover lost sales
- **Re-Engagement** - Win back inactive users
- **Lead Nurturing** - Convert leads to customers

## Best Practices

1. **Start Simple** - Begin basic, add complexity later
2. **Test Thoroughly** - Always test before activating
3. **Monitor Regularly** - Check drop-off points
4. **Personalize** - Use dynamic content
    `,
  },

  "neurocopilot": {
    title: "NeuroCopilot: AI Assistant",
    description: "Your AI marketing assistant",
    category: "Core Modules",
    readTime: "6 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "FlowBuilder", href: "/docs/flowbuilder" },
    nextPage: { title: "AudienceGenome", href: "/docs/audiencegenome" },
    content: `
# NeuroCopilot: AI Assistant

NeuroCopilot is your AI-powered marketing assistant for questions, tasks, and insights.

## Overview

NeuroCopilot can:
- 💬 **Answer questions** about your marketing performance
- 📊 **Pull data** from any connected platform
- 🚀 **Execute actions** like creating campaigns
- 💡 **Provide recommendations** based on your data

## Accessing NeuroCopilot

Click the chat icon in the bottom right, or press **⌘K** (Mac) / **Ctrl+K** (Windows).

## What You Can Ask

### Performance Questions
- "How did my campaigns perform last week?"
- "What's my best performing ad?"
- "Why did conversions drop yesterday?"

### Data Queries
- "Show me top 10 keywords by conversions"
- "Give me a breakdown by channel"

### Action Requests
- "Pause campaigns with ROAS below 2"
- "Generate 5 ad headlines for my product"

### Strategic Advice
- "Should I increase my Google Ads budget?"
- "What content should I create this week?"

## Capabilities

NeuroCopilot has access to all your marketing data and can execute actions with your permission.

| Action | Confirmation Required |
|--------|----------------------|
| View data | No |
| Generate reports | No |
| Modify campaigns | Yes |
| Change budgets | Yes |

## Best Practices

1. **Be Specific** - "What's my Google Ads ROAS for November?" beats "How am I doing?"
2. **Provide Context** - Include details in your requests
3. **Ask Follow-Ups** - Build on the conversation
4. **Verify Actions** - Review before confirming changes
    `,
  },

  "audiencegenome": {
    title: "AudienceGenome: Persona Engine",
    description: "AI-powered audience segmentation and persona creation",
    category: "Core Modules",
    readTime: "8 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "NeuroCopilot", href: "/docs/neurocopilot" },
    nextPage: { title: "AdPilot", href: "/docs/adpilot" },
    content: `
# AudienceGenome: Persona Engine

AudienceGenome creates deep customer personas and audience segments using AI.

## Overview

AudienceGenome helps you understand:
- 👥 **Who your customers are** - Demographics and psychographics
- 🧠 **What motivates them** - Pain points and desires
- 🛒 **How they buy** - Purchase behavior and triggers
- 📱 **Where to reach them** - Channel preferences

## Persona Generation

1. Navigate to **Audiences → AudienceGenome**
2. Click **Generate Persona**
3. Provide context about your product and market
4. Wait for AI analysis

### Persona Output

Each persona includes:
- **Demographics** - Age, role, company, income
- **Psychographics** - Values, behaviors, motivations
- **Pain Points** - Problems they face
- **Buying Triggers** - What prompts purchase
- **Channel Preferences** - Where they engage

## Audience Segmentation

### Auto-Segmentation

AudienceGenome creates segments automatically:

| Segment | Criteria |
|---------|----------|
| High-Value | Top 20% by revenue |
| At-Risk | Declining engagement |
| New | Joined < 30 days |
| Dormant | No activity 60+ days |

### Custom Segments

Create custom segments with conditions like company size, job title, engagement level, and location.

## Best Practices

1. **Validate with real data** - Compare AI personas to customer interviews
2. **Update regularly** - Refresh personas quarterly
3. **Don't over-segment** - 3-5 primary personas is optimal
4. **Share across team** - Ensure consistent understanding
    `,
  },

  "adpilot": {
    title: "AdPilot: Ad Management",
    description: "Automated advertising creation and optimization",
    category: "Core Modules",
    readTime: "10 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "AudienceGenome", href: "/docs/audiencegenome" },
    nextPage: { title: "BattleStation", href: "/docs/battlestation" },
    content: `
# AdPilot: Ad Management

AdPilot automates ad creation, publishing, and optimization across all platforms.

## Overview

AdPilot handles:
- 🎨 **Creative generation** - AI-powered ad copy and visuals
- 🚀 **Multi-platform publishing** - Deploy to all channels
- 🔬 **A/B testing** - Automatic variant testing
- 📈 **Bid optimization** - Real-time bid management

## Supported Platforms

| Platform | Ad Types |
|----------|----------|
| Google Ads | Search, Display, YouTube |
| Meta Ads | Feed, Stories, Reels |
| LinkedIn | Sponsored, Message |
| Twitter/X | Promoted tweets |
| TikTok | In-feed, TopView |

## Creating Ads

1. Go to **Ads → AdPilot**
2. Click **Create Ad**
3. Select platforms
4. Provide product/service info
5. AdPilot generates creatives

AdPilot creates multiple headline and description variants, plus images.

## A/B Testing

AdPilot automatically:
1. Creates multiple ad variants
2. Distributes budget across variants
3. Measures performance
4. Pauses underperformers
5. Scales winners

## Bid Management

| Strategy | Best For |
|----------|----------|
| Target CPA | Conversions |
| Target ROAS | Revenue |
| Maximize Clicks | Traffic |
| Manual | Control |

## Best Practices

1. **Start with proven formats**
2. **Test one variable at a time**
3. **Set clear goals**
4. **Refresh creatives regularly**
    `,
  },

  "battlestation": {
    title: "BattleStation: Competitive Intel",
    description: "Monitor and analyze competitor marketing strategies",
    category: "Core Modules",
    readTime: "8 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "AdPilot", href: "/docs/adpilot" },
    nextPage: { title: "TrendRadar", href: "/docs/trendradar" },
    content: `
# BattleStation: Competitive Intelligence

BattleStation monitors your competitors' marketing activities.

## Overview

BattleStation tracks:
- 📢 **Ad campaigns** - Competitor creatives and spend
- 📱 **Social activity** - Posts, engagement, growth
- 🔍 **SEO rankings** - Keyword positions
- 📧 **Email campaigns** - Newsletter content
- 💰 **Pricing changes** - Product pricing updates

## Setting Up Competitors

1. Go to **Intelligence → BattleStation**
2. Click **Add Competitor**
3. Enter company name, website, social handles
4. BattleStation starts monitoring

## Monitoring Dashboard

View competitor activity:
- Recent campaigns
- Share of voice comparison
- Social performance metrics
- Ad creative screenshots

## Competitive Reports

### Weekly Digest
Automated report with new campaigns, changes, and opportunities.

### Comparison Analysis

| Metric | You | Competitor A |
|--------|-----|--------------|
| Social Followers | 15K | 22K |
| Monthly Posts | 45 | 62 |
| Avg Engagement | 3.2% | 2.8% |
| Est. Ad Spend | $10K | $25K |

## Best Practices

1. **Focus on 3-5 key competitors**
2. **Review weekly**
3. **Act on insights**
4. **Track trends over time**
    `,
  },

  "trendradar": {
    title: "TrendRadar: Trend Monitoring",
    description: "Real-time trend detection and opportunity alerts",
    category: "Core Modules",
    readTime: "6 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "BattleStation", href: "/docs/battlestation" },
    content: `
# TrendRadar: Trend Monitoring

TrendRadar monitors real-time trends and alerts you to marketing opportunities.

## Overview

TrendRadar monitors:
- 📈 **Trending topics** - What's hot right now
- 🔍 **Search trends** - Google Trends data
- 📱 **Social trends** - Viral content
- 📰 **News trends** - Breaking stories

## Trend Detection

TrendRadar scans Twitter, Google Trends, Reddit, news sites, and industry publications.

### Relevance Scoring

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100 | Highly relevant | Immediate opportunity |
| 70-89 | Relevant | Consider response |
| 50-69 | Somewhat relevant | Monitor |
| <50 | Low relevance | Ignore |

## Opportunity Alerts

Get notified when:
- Trend matches your industry
- Search volume spikes
- Competitor mentions surge
- Viral content in your space

## Best Practices

1. **Set relevant keywords**
2. **Act quickly** - Trends fade fast
3. **Stay authentic** - Don't force relevance
4. **Plan ahead for predictable trends**
    `,
  },

  // ==========================================
  // API REFERENCE
  // ==========================================
  "api/auth": {
    title: "API Authentication",
    description: "Authenticate with the NeuroCron API",
    category: "API Reference",
    readTime: "5 min",
    lastUpdated: "2024-11-28",
    nextPage: { title: "Campaigns API", href: "/docs/api/campaigns" },
    content: `
# API Authentication

Learn how to authenticate with the NeuroCron API.

## Overview

NeuroCron uses **Bearer Token** authentication for all API requests.

## Getting Your API Key

1. Log in to your NeuroCron account
2. Go to **Settings → API Keys**
3. Click **Generate New Key**
4. Copy and securely store your key

⚠️ API keys are shown only once. Store them securely.

## Using Your API Key

Include the key in the Authorization header:

    curl -X GET "https://api.neurocron.com/v1/campaigns" \\
      -H "Authorization: Bearer YOUR_API_KEY" \\
      -H "Content-Type: application/json"

## Rate Limits

| Plan | Requests/Minute | Requests/Day |
|------|-----------------|--------------|
| Free | 60 | 1,000 |
| Starter | 120 | 10,000 |
| Growth | 300 | 50,000 |
| Enterprise | Custom | Custom |

## Error Responses

### 401 Unauthorized
Invalid or missing API key

### 403 Forbidden
API key lacks required permissions

### 429 Rate Limited
Too many requests - includes retry_after value

## Security Best Practices

1. Never commit keys to version control
2. Use environment variables
3. Rotate keys regularly
4. Use minimum permissions required
    `,
  },

  "api/campaigns": {
    title: "Campaigns API",
    description: "Create and manage campaigns via API",
    category: "API Reference",
    readTime: "8 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Authentication", href: "/docs/api/auth" },
    nextPage: { title: "Content API", href: "/docs/api/content" },
    content: `
# Campaigns API

Create, read, update, and delete marketing campaigns.

## Base URL

    https://api.neurocron.com/v1

## Endpoints

### List Campaigns

    GET /campaigns

Query Parameters:
- status: Filter by status (active, paused, draft)
- limit: Results per page (default: 20, max: 100)
- offset: Pagination offset

### Get Campaign

    GET /campaigns/{id}

### Create Campaign

    POST /campaigns

Request body:
- name: Campaign name
- campaign_type: awareness, sales, lead_gen
- budget: Total budget
- channels: Array of channels
- target_audience: Audience configuration

### Update Campaign

    PATCH /campaigns/{id}

### Delete Campaign

    DELETE /campaigns/{id}

### Campaign Actions

    POST /campaigns/{id}/pause
    POST /campaigns/{id}/resume
    POST /campaigns/{id}/duplicate
    `,
  },

  "api/content": {
    title: "Content API",
    description: "Generate marketing content via API",
    category: "API Reference",
    readTime: "6 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Campaigns API", href: "/docs/api/campaigns" },
    nextPage: { title: "Webhooks", href: "/docs/api/webhooks" },
    content: `
# Content API

Generate marketing content using ContentForge AI.

## Generate Content

    POST /content/generate

Request body:
- type: blog_article, social_post, email, ad_copy, landing_page
- topic: Content topic
- length: Word count (for articles)
- tone: professional, casual, etc.
- keywords: Array of keywords
- target_audience: Description

## Content Types

| Type | Description |
|------|-------------|
| blog_article | Long-form SEO content |
| social_post | Platform-specific posts |
| email | Email campaigns |
| ad_copy | Advertising creative |

### Social Post Options

Include platform (linkedin, twitter, etc.) and optional hashtags.

### Ad Copy Options

Include platform, product, USP, and number of variants desired.

## List Content

    GET /content

Query generated content with filters.

## Get Content

    GET /content/{id}

Retrieve specific content by ID.
    `,
  },

  "api/webhooks": {
    title: "Webhooks",
    description: "Receive real-time event notifications",
    category: "API Reference",
    readTime: "5 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Content API", href: "/docs/api/content" },
    content: `
# Webhooks

Receive real-time notifications when events occur in NeuroCron.

## Setting Up Webhooks

1. Go to **Settings → Webhooks**
2. Click **Add Endpoint**
3. Enter your URL and select events
4. Save and test

## Available Events

| Event | Description |
|-------|-------------|
| campaign.created | New campaign created |
| campaign.updated | Campaign modified |
| campaign.paused | Campaign paused |
| budget.threshold | Budget threshold reached |
| performance.alert | Performance anomaly detected |
| content.generated | Content generation completed |

## Webhook Payload

Each webhook includes:
- id: Event ID
- type: Event type
- created_at: Timestamp
- data: Event-specific data

## Verifying Webhooks

Verify signatures using HMAC-SHA256 with your webhook secret.

## Retry Policy

Failed webhooks are retried:
- 1st retry: 1 minute
- 2nd retry: 5 minutes
- 3rd retry: 30 minutes
- 4th retry: 2 hours
- 5th retry: 24 hours

After 5 failures, the endpoint is disabled.
    `,
  },

  // ==========================================
  // SECURITY
  // ==========================================
  "security": {
    title: "Security Overview",
    description: "NeuroCron security practices and certifications",
    category: "Security",
    readTime: "5 min",
    lastUpdated: "2024-11-28",
    nextPage: { title: "GDPR Compliance", href: "/docs/security/gdpr" },
    content: `
# Security Overview

NeuroCron is built with security at its core.

## Certifications

- **SOC 2 Type II** - Audited annually
- **GDPR Compliant** - EU data protection
- **CCPA Compliant** - California privacy law

## Infrastructure Security

### Data Encryption
- TLS 1.3 for data in transit
- AES-256 for data at rest
- Encrypted database connections

### Network Security
- DDoS protection
- Web Application Firewall
- Private network isolation

### Access Control
- Role-based access (RBAC)
- Multi-factor authentication
- Session management

## Data Handling

### What We Store
- Account information
- Connected platform tokens (encrypted)
- Campaign configurations
- Analytics data

### What We Don't Store
- Raw passwords (only hashed)
- Credit card numbers (via Stripe)
- Unnecessary personal data

## Incident Response

24/7 security monitoring with automated threat detection and incident response.

Contact: security@neurocron.com
    `,
  },

  "security/gdpr": {
    title: "GDPR Compliance",
    description: "How NeuroCron complies with GDPR",
    category: "Security",
    readTime: "5 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Security Overview", href: "/docs/security" },
    content: `
# GDPR Compliance

NeuroCron is fully compliant with the General Data Protection Regulation.

## Your Rights

Under GDPR, you have the right to:
- **Access** your personal data
- **Rectify** inaccurate data
- **Erase** your data ("right to be forgotten")
- **Port** your data to another service
- **Object** to certain processing
- **Restrict** processing

## Data Processing

### Legal Basis
- Contract performance (service delivery)
- Legitimate interests (product improvement)
- Consent (marketing communications)

### Data Minimization
We collect only data necessary for service operation.

## Data Subject Requests

Submit GDPR requests:
1. Go to **Settings → Privacy**
2. Click **Submit Request**
3. Choose request type
4. We respond within 30 days

## EU Data Residency

EU customer data can be stored in EU-based servers upon request.

Contact: privacy@neurocron.com
    `,
  },

  // ==========================================
  // BEST PRACTICES
  // ==========================================
  "best-practices/ai-optimization": {
    title: "Optimizing AI Outputs",
    description: "Get better results from NeuroCron's AI features",
    category: "Best Practices",
    readTime: "8 min",
    lastUpdated: "2024-11-28",
    nextPage: { title: "Campaign Strategy", href: "/docs/best-practices/campaigns" },
    content: `
# Optimizing AI Outputs

Learn how to get the best results from NeuroCron's AI features.

## Context is Everything

The quality of AI output depends on input quality.

**Poor:** "Write an ad"

**Good:** "Write a Google Search ad for our project management software targeting small business owners aged 30-50. Emphasize time savings and ease of use. Professional but friendly tone. Include a free trial CTA."

## The SPECIFIC Framework

- **S**ituation - What's the context?
- **P**roduct - What are you promoting?
- **E**xpected outcome - What should happen?
- **C**onstraints - What limitations exist?
- **I**nspiration - Any examples to follow?
- **F**ormat - How should output be structured?
- **I**terations - How many variants?
- **C**hecks - What to verify?

## Common Mistakes

1. **Being Too Vague** - Be explicit about what you want
2. **Expecting Perfection** - AI is a starting point
3. **Ignoring Training** - Train brand voice for better results
4. **Not Iterating** - Ask for variations
5. **Skipping Review** - Verify facts

## Quality Checklist

Before using AI content:
- ✅ Factual accuracy verified
- ✅ Brand voice consistent
- ✅ No placeholder text
- ✅ Links and CTAs correct
- ✅ Grammar checked
    `,
  },

  "best-practices/campaigns": {
    title: "Campaign Strategy Tips",
    description: "Best practices for successful marketing campaigns",
    category: "Best Practices",
    readTime: "10 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "AI Optimization", href: "/docs/best-practices/ai-optimization" },
    nextPage: { title: "Content Guidelines", href: "/docs/best-practices/content" },
    content: `
# Campaign Strategy Tips

Best practices for successful marketing campaigns with NeuroCron.

## Define Clear Goals

Use SMART goals:
- **S**pecific - Increase e-commerce sales
- **M**easurable - By 25% in revenue
- **A**chievable - Based on market potential
- **R**elevant - Aligns with Q4 targets
- **T**ime-bound - Within 60 days

## Budget Allocation

Recommended splits for new campaigns:

| Phase | Budget | Focus |
|-------|--------|-------|
| Testing (Week 1-2) | 20% | Test audiences and creatives |
| Optimization (Week 3-4) | 30% | Double down on winners |
| Scale (Week 5+) | 50% | Full budget to performers |

## Audience Strategy

Layer your audiences:
1. **Core Audience** - Ideal customer profile
2. **Lookalike Audience** - Similar to converters
3. **Retargeting** - Website visitors
4. **Exclusions** - Current customers

## Creative Best Practices

**Images:**
- Use faces when possible
- Contrast with platform background
- Keep text under 20%

**Copy:**
- Lead with benefit
- Use specific numbers
- Include social proof
- Create urgency authentically

## Common Pitfalls

1. Changing too much too fast
2. Audience overlap
3. Creative fatigue
4. Ignoring attribution
    `,
  },

  "best-practices/content": {
    title: "Content Quality Guidelines",
    description: "Create high-performing marketing content",
    category: "Best Practices",
    readTime: "8 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Campaign Strategy", href: "/docs/best-practices/campaigns" },
    nextPage: { title: "Automation Workflows", href: "/docs/best-practices/automation" },
    content: `
# Content Quality Guidelines

Standards for creating effective marketing content.

## Content Principles

1. **Audience First** - Answer "What's in it for the reader?"
2. **Value Over Volume** - One excellent piece beats ten mediocre ones
3. **Authentic Voice** - Your brand personality must shine through
4. **Platform Native** - Adapt to each platform's culture

## Blog Articles

**Length:** 1,500-2,500 words for SEO impact

**Structure:**
- Compelling headline with keyword
- Hook intro (2 sentences)
- Scannable headers
- Visual breaks
- Clear takeaways
- Strong CTA

## Social Media

| Platform | Optimal Length | Best Content |
|----------|---------------|--------------|
| LinkedIn | 1,300 chars | Thought leadership |
| Twitter | 100-280 chars | Quick insights |
| Facebook | 80 chars | Engaging questions |
| Instagram | 150 chars | Visual stories |

## Email

**Subject Lines:**
- Under 50 characters
- Create curiosity
- Personalize when possible

**Body:**
- One clear CTA per email
- Short paragraphs
- Mobile-first design

## Quality Review

Before publishing:
- ✅ Facts verified
- ✅ Brand voice consistent
- ✅ Links working
- ✅ Mobile responsive
    `,
  },

  "best-practices/automation": {
    title: "Automation Workflows",
    description: "Build effective marketing automation",
    category: "Best Practices",
    readTime: "8 min",
    lastUpdated: "2024-11-28",
    prevPage: { title: "Content Guidelines", href: "/docs/best-practices/content" },
    content: `
# Automation Workflows

Best practices for marketing automations with FlowBuilder.

## Automation Principles

1. **Start Simple** - Begin basic, add complexity later
2. **Map the Journey** - Understand customer path first
3. **Personalize Thoughtfully** - Helpful, not creepy
4. **Test Everything** - Always test before activation
5. **Monitor & Iterate** - Ongoing optimization needed

## Essential Workflows

### Welcome Series

Day 0: Welcome email (thank + set expectations)
Day 2: Value email (quick win or tip)
Day 4: Feature highlight
Day 7: Engagement check (branch based on activity)

### Abandoned Cart

Hour 1: Reminder email (no discount)
Hour 24: Second reminder + social proof
Hour 72: Final email + urgency

### Lead Nurturing

Lead Created → Segment by Interest →
Week 1: Related content
Week 2: Case study
Week 3: Webinar invite
Week 4: Direct offer

## Key Metrics

| Metric | Target | Red Flag |
|--------|--------|----------|
| Open rate | >25% | <15% |
| Click rate | >3% | <1% |
| Conversion | >2% | <0.5% |
| Unsubscribe | <0.5% | >1% |

## Testing Checklist

- ✅ All emails reviewed
- ✅ Links tested
- ✅ Personalization working
- ✅ Timing appropriate
- ✅ Exit conditions set
- ✅ Analytics tracking enabled
    `,
  },
};

// Helper to get doc by slug
export function getDocBySlug(slug: string[]): DocPage | null {
  const path = slug.join("/");
  return docsContent[path] || null;
}

// Get all doc slugs for static generation
export function getAllDocSlugs(): string[][] {
  return Object.keys(docsContent).map((key) => key.split("/"));
}
