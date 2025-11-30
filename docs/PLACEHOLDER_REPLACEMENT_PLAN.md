# NeuroCron — Placeholder & Mock Data Replacement Plan

## Executive Summary

This document identifies all placeholder data, mock responses, and stub implementations across the NeuroCron platform and provides a prioritized plan to replace them with real functionality.

---

## 🔴 CRITICAL PRIORITY (Core Platform Functionality)

### 1. AI Integration Layer (Currently Fallback to Sample Data)

**Location:** Multiple backend services  
**Impact:** HIGH — Core AI features don't work without this

| File | Issue | Solution |
|------|-------|----------|
| `backend/app/api/v1/strategy.py` | `_generate_sample_strategy()` returns hardcoded strategy | Connect to Ollama/OpenAI with proper prompts |
| `backend/app/api/v1/strategy.py` | `_generate_sample_ideas()` returns static ideas | Implement AI-powered idea generation |
| `backend/app/api/v1/personas.py` | `_generate_sample_personas()` returns 3 static personas | Use AI to generate context-aware personas |
| `backend/app/api/v1/ads.py` | `_generate_ad_variants()` returns template ads | AI-powered ad copy generation |
| `backend/app/api/v1/content.py` | Returns placeholder content ideas | Full AI content generation |
| `backend/app/api/v1/localization.py` | Line 205-206: "For now, simulate with placeholder" | Integrate AI translation service |

**Action Items:**
- [ ] Create unified AI service layer (`backend/app/services/ai/`)
- [ ] Implement prompt templates for each use case
- [ ] Add fallback handling and error recovery
- [ ] Add streaming support for long-form content

---

### 2. OAuth Integration (Platforms Show as Disconnected)

**Location:** `backend/app/api/v1/integrations.py`  
**Impact:** HIGH — No real platform connections work

| Line | Issue | Solution |
|------|-------|----------|
| 95-96 | `oauth_states = {}` in-memory (lost on restart) | Store in Redis with TTL |
| 122-133 | Returns all platforms as "disconnected" | Query DB for real connection status |
| 255-293 | OAuth callback handlers are placeholders | Implement full OAuth token exchange |
| 328+ | Token refresh, disconnect handlers incomplete | Full OAuth lifecycle management |

**Action Items:**
- [ ] Create `IntegrationToken` model for storing OAuth credentials
- [ ] Implement encrypted token storage (using Fernet)
- [ ] Build token refresh scheduler (Celery task)
- [ ] Complete OAuth callback handlers for all platforms
- [ ] Add real API client wrappers for each platform

---

### 3. Celery Workers (All Stubs)

**Location:** `backend/app/workers/`  
**Impact:** HIGH — AutoCron automation doesn't work

#### `autocron_tasks.py`
| Task | Current State | Required Implementation |
|------|---------------|------------------------|
| `execute_scheduled_tasks()` | Returns `{"executed": 0}` | Query DB, execute via platform APIs |
| `optimize_campaigns()` | Returns empty list | Fetch metrics, apply ML optimization |
| `sync_platform_metrics()` | Returns all `False` | Real API calls to sync data |
| `generate_daily_reports()` | Returns 0 reports | Generate and store/email reports |
| `publish_social_post()` | Placeholder | Real platform API calls |
| `send_scheduled_email()` | Placeholder | SendGrid/SES integration |
| `adjust_ad_budget()` | Placeholder | Google/Meta Ads API calls |

#### `trend_tasks.py`
| Task | Current State | Required Implementation |
|------|---------------|------------------------|
| `check_trends()` | Returns sample trends | Twitter/Reddit/News API integration |
| `monitor_brand_mentions()` | Placeholder | Social listening implementation |
| `analyze_sentiment()` | "Placeholder - would use actual ML" | Integrate sentiment model |

#### `content_tasks.py`
| Task | Current State | Required Implementation |
|------|---------------|------------------------|
| `generate_content()` | "In production: Call AI service" | Real AI content generation |
| `generate_social_post()` | Placeholder | AI + platform-specific formatting |
| `generate_email()` | Placeholder | AI email generation |
| `repurpose_content()` | Placeholder | Content transformation logic |

**Action Items:**
- [ ] Implement all platform SDK clients
- [ ] Create scheduling infrastructure for posts/emails
- [ ] Build metrics sync pipeline
- [ ] Implement ML-based optimization logic
- [ ] Add proper error handling and retry logic

---

### 4. Stripe Billing (Mock Session)

**Location:** `backend/app/api/v1/billing.py`  
**Impact:** HIGH — Can't monetize

| Line | Issue | Solution |
|------|-------|----------|
| 17 | `stripe.api_key = "sk_test_placeholder"` | Use real Stripe API key from env |
| 245-248 | "For now, return mock session" | Create real Stripe checkout |
| 274 | Mock portal session | Real Stripe billing portal |
| 353 | "In production, calculate actual usage" | Real usage tracking |
| 389 | "In production, fetch from database" | Real invoice fetching |

**Action Items:**
- [ ] Configure Stripe API keys in environment
- [ ] Implement Subscription model persistence
- [ ] Create real checkout session flow
- [ ] Set up webhook endpoint for subscription events
- [ ] Implement usage-based billing tracking

---

## 🟠 HIGH PRIORITY (Data Collection & Display)

### 5. Analytics Dashboard (All Hardcoded)

**Location:** `frontend/src/app/(dashboard)/analytics/page.tsx`

| Line | Issue | Solution |
|------|-------|----------|
| 39-48 | `const trafficData = [...]` hardcoded | Fetch from `/api/v1/analytics/traffic` |
| 50-56 | `const channelData = [...]` hardcoded | Fetch from `/api/v1/analytics/channels` |
| 58-63 | `const campaignPerformance = [...]` hardcoded | Fetch from `/api/v1/analytics/campaigns` |
| 65-71 | `const conversionFunnel = [...]` hardcoded | Fetch from `/api/v1/analytics/funnel` |
| 172-200 | MetricCard values hardcoded | Dynamic from API |
| 401-406 | Top content table hardcoded | Fetch from API |

**Action Items:**
- [ ] Create analytics API endpoints for each data type
- [ ] Implement date range filtering
- [ ] Connect frontend to real API endpoints
- [ ] Add loading states and error handling

---

### 6. Competitor & Intelligence Data (Sample Data Fallback)

**Location:** `backend/app/api/v1/competitors.py`

| Line | Issue | Solution |
|------|-------|----------|
| 105-140 | Returns sample competitor data when DB empty | Implement competitor scraping |
| 236-263 | Returns sample insights | Generate real insights from scraped data |
| 316-376 | Returns sample trends | Real trend detection |
| 519-563 | Returns sample brand mentions | Real social listening |
| 461 | "In production, would calculate from actual mentions" | Real sentiment analysis |

**Action Items:**
- [ ] Build competitor website scraper (using Playwright)
- [ ] Implement SEO metrics fetching (Ahrefs/Moz API)
- [ ] Create social media monitoring pipeline
- [ ] Add news/PR monitoring
- [ ] Build threat level scoring algorithm

---

### 7. Unified Inbox (Random Generated Messages)

**Location:** `backend/app/api/v1/channels.py`

| Line | Issue | Solution |
|------|-------|----------|
| 84-104 | `_generate_sample_inbox()` returns random messages | Pull from connected platforms |
| 317-375 | Random message generation with `random.choice()` | Real message aggregation |
| 143-191 | Channel stats are all hardcoded | Real metrics from platform APIs |

**Action Items:**
- [ ] Build unified inbox aggregator
- [ ] Implement platform-specific message fetching
- [ ] Add real-time webhook receivers for each platform
- [ ] Create reply functionality via platform APIs
- [ ] Sync follower counts and engagement metrics

---

### 8. Ad Campaigns (Sample Data)

**Location:** `backend/app/api/v1/ads.py`

| Line | Issue | Solution |
|------|-------|----------|
| 128-174 | Returns sample campaigns list | Fetch from Google/Meta Ads API |
| 236-283 | Sample optimization suggestions | AI-powered recommendations |
| 306-341 | `_generate_ad_variants()` template-based | Real AI ad generation |

**Action Items:**
- [ ] Implement Google Ads API client
- [ ] Implement Meta Ads API client
- [ ] Build campaign sync pipeline
- [ ] Create AI optimization engine
- [ ] Add real A/B test tracking

---

## 🟡 MEDIUM PRIORITY (Enhanced Features)

### 9. Customer DNA (Sample Cohort Data)

**Location:** `backend/app/api/v1/customer_dna.py`

| Line | Issue |
|------|-------|
| 623 | "Sample cohort data (in production, calculate from events)" |

**Action Items:**
- [ ] Implement event tracking SDK
- [ ] Build cohort analysis engine
- [ ] Create customer scoring algorithms
- [ ] Implement journey mapping

---

### 10. Behavior Analytics (Limited Real Tracking)

**Location:** Frontend/Backend

| Component | Issue | Solution |
|-----------|-------|----------|
| Heatmaps | "Add tracking script" placeholder | Build JavaScript SDK |
| Session Recordings | Shows empty | Implement recording infrastructure |
| Funnels | No real conversion tracking | Event-based funnel analysis |

**Action Items:**
- [ ] Create JavaScript tracking SDK (`neurocron.js`)
- [ ] Build session recording storage (MinIO)
- [ ] Implement heatmap aggregation
- [ ] Create funnel builder with real data

---

### 11. Attribution (Sample Paths)

**Location:** `backend/app/api/v1/attribution.py`

| Line | Issue |
|------|-------|
| 346 | "Sample conversion paths (in production, compute from actual data)" |
| 402 | "In production, this would trigger a background job" |

**Action Items:**
- [ ] Implement touchpoint tracking
- [ ] Build multi-touch attribution models
- [ ] Create revenue connection pipeline
- [ ] Add attribution visualization

---

### 12. Teams & Invites (Email Not Sent)

**Location:** `backend/app/api/v1/teams.py`

| Line | Issue |
|------|-------|
| 190-195 | "In production, send email with invite link" |

**Action Items:**
- [ ] Integrate email service (SendGrid configured)
- [ ] Create email templates for invites
- [ ] Implement invite token verification

---

### 13. Agency Mode (Placeholder Organization)

**Location:** `backend/app/api/v1/agency.py`

| Line | Issue |
|------|-------|
| 106-107 | "In production, create a new organization... For now, use a placeholder" |

**Action Items:**
- [ ] Implement multi-organization architecture
- [ ] Create white-label configuration
- [ ] Build client dashboard views

---

## 🟢 LOWER PRIORITY (Nice-to-Have Enhancements)

### 14. LaunchPad Templates

**Location:** `backend/app/api/v1/launchpad.py`

| Line | Issue |
|------|-------|
| 403 | "In production: ..." - templates are static |

**Action Items:**
- [ ] Create template library
- [ ] Build template customization engine
- [ ] Add AI-powered template recommendations

---

### 15. Audit System

**Location:** `backend/app/api/v1/audit.py`

| Line | Issue |
|------|-------|
| 484 | "In production, fetch from database" |

**Action Items:**
- [ ] Implement website crawler
- [ ] Build SEO analysis engine
- [ ] Create performance auditing
- [ ] Add social profile analysis

---

### 16. Simulator (No Real ML)

**Location:** `backend/app/api/v1/simulator.py`

| Line | Issue |
|------|-------|
| 58 | "In production, this would use actual ML models" |

**Action Items:**
- [ ] Build prediction models (using Prophet/Scikit-learn)
- [ ] Train on historical campaign data
- [ ] Create scenario simulation engine

---

## Implementation Priority Matrix

| Phase | Duration | Focus Areas |
|-------|----------|-------------|
| **Phase 1** | 2 weeks | AI Integration, OAuth, Celery Workers |
| **Phase 2** | 2 weeks | Analytics, Billing, Platform APIs |
| **Phase 3** | 2 weeks | Inbox, Competitors, Ad Management |
| **Phase 4** | 2 weeks | Customer DNA, Behavior, Attribution |
| **Phase 5** | 1 week | Teams, Agency, Templates |
| **Phase 6** | 1 week | Audit, Simulator, Polish |

---

## Quick Wins (Can Fix Immediately)

1. **Environment Variables** - Add real API keys to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_live_...
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   META_APP_ID=...
   META_APP_SECRET=...
   SENDGRID_API_KEY=...
   ```

2. **AI Fallback Improvement** - Instead of static data, generate dynamic sample data using Ollama that's already configured

3. **Analytics API** - Create real endpoints that query TimescaleDB

4. **Billing Webhook** - Set up Stripe webhook endpoint

---

## Dependencies Map

```
OAuth Integration → Platform API Clients → Celery Workers → Real Data
                                      ↘
AI Service Layer → Content/Strategy/Ads Generation
                                      ↘
Billing Integration → Usage Tracking → Revenue Attribution
```

---

## Estimated Total Effort

| Category | Effort |
|----------|--------|
| AI Integration | 3-4 days |
| OAuth + Platform APIs | 5-7 days |
| Celery Workers | 4-5 days |
| Billing | 2-3 days |
| Analytics/Data | 3-4 days |
| Frontend Wiring | 2-3 days |
| Testing & Polish | 3-4 days |
| **TOTAL** | **~25-30 days** |

---

## Files Changed Summary

### Backend Files with Placeholders:
- `backend/app/api/v1/strategy.py` ✓
- `backend/app/api/v1/personas.py` ✓
- `backend/app/api/v1/competitors.py` ✓
- `backend/app/api/v1/ads.py` ✓
- `backend/app/api/v1/channels.py` ✓
- `backend/app/api/v1/billing.py` ✓
- `backend/app/api/v1/integrations.py` ✓
- `backend/app/api/v1/localization.py` ✓
- `backend/app/api/v1/attribution.py` ✓
- `backend/app/api/v1/customer_dna.py` ✓
- `backend/app/api/v1/agency.py` ✓
- `backend/app/api/v1/simulator.py` ✓
- `backend/app/api/v1/teams.py` ✓
- `backend/app/api/v1/audit.py` ✓
- `backend/app/api/v1/content.py` ✓
- `backend/app/api/v1/copilot.py` ✓
- `backend/app/api/v1/launchpad.py` ✓
- `backend/app/api/v1/webhooks.py` ✓
- `backend/app/workers/autocron_tasks.py` ✓
- `backend/app/workers/trend_tasks.py` ✓
- `backend/app/workers/content_tasks.py` ✓

### Frontend Files with Placeholders:
- `frontend/src/app/(dashboard)/analytics/page.tsx` ✓

---

*Last Updated: November 30, 2025*

