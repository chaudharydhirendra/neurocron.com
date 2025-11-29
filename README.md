# NeuroCron — The Autonomous Marketing Brain

> **AI that plans, executes, audits, and optimizes your entire marketing — automatically.**

NeuroCron is the world's first truly autonomous, end-to-end AI marketing system. It combines neural intelligence with automated precision to create a self-thinking marketing platform that runs 24/7 without human intervention.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Development Setup

```bash
# Clone the repository
git clone git@github.com:chaudharydhirendra/neurocron.com.git
cd neurocron.com

# Copy environment file
cp .env.example .env

# Start infrastructure services
docker-compose up -d postgres redis meilisearch minio

# Install dependencies
make install

# Run database migrations
make db-upgrade

# Start development servers
make dev
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3100 |
| Backend API | http://localhost:8100 |
| API Documentation | http://localhost:8100/docs |
| Celery Flower | http://localhost:5555 |
| MinIO Console | http://localhost:9001 |
| Meilisearch | http://localhost:7700 |

## 📁 Project Structure

```
/opt/neurocron.com/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Config, security, dependencies
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic by module
│   │   └── workers/        # Celery tasks
│   └── alembic/            # Database migrations
├── frontend/               # Next.js application
│   └── src/
│       ├── app/            # App Router pages
│       ├── components/     # React components
│       └── lib/            # Utilities
├── services/               # Microservices
│   ├── trend-service/      # TrendRadar
│   ├── scraper-service/    # BattleStation
│   └── simulation-service/ # SimulatorX
├── nginx/                  # Reverse proxy config
└── docs/                   # Documentation
```

## 🧠 Platform Modules

### Strategy & Planning Suite
- **NeuroPlan** — AI-generated 12-month marketing roadmaps
- **AudienceGenome** — Customer persona & segmentation engine
- **BrainSpark** — Creative intelligence generator
- **TrendRadar** — Real-time market pulse detection
- **BattleStation** — Competitive warfare intelligence
- **SimulatorX** — Marketing what-if prediction engine

### Execution & Automation Suite
- **AutoCron** — Autonomous execution engine
- **ChannelPulse** — Unified cross-channel control center
- **AdPilot** — Automated ad creation & management
- **ContentForge** — AI content manufacturing system
- **FlowBuilder** — Customer journey automations
- **InfluencerIQ** — Influencer discovery & management
- **LocalPulse** — Hyperlocal marketing engine
- **LaunchPad** — Pre-built campaign templates
- **GlobalReach** — Multi-language & localization

### Analytics & Intelligence Suite
- **AuditX** — Autonomous marketing auditor
- **InsightCortex** — AI analytics hub
- **AttributionSense** — Multi-touch attribution
- **ScoreBoard** — Executive reporting
- **CustomerDNA** — Unified customer data platform
- **RevenueLink** — Marketing-to-revenue attribution

### Optimization & Growth Suite
- **GrowthOS** — Continuous optimization system
- **PredictiveAdvantage** — Forecasting intelligence
- **BehaviorMind** — User behavior analytics
- **RetentionAI** — Churn prediction & retention
- **ViralEngine** — Gamification & referral system

### Platform-Wide Intelligence
- **NeuroCopilot** — Conversational AI command center
- **CrisisShield** — Brand safety & reputation guard

## 🛠 Development Commands

```bash
# Start development environment
make dev

# Run tests
make test

# Run linter
make lint

# Format code
make format

# Database migrations
make db-migrate msg="Add new table"
make db-upgrade

# View logs
make logs service=backend

# Clean up
make clean
```

## 🔒 Security

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- API rate limiting
- Encryption at rest (AES-256)
- TLS 1.3 in transit
- GDPR/CCPA compliant

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Feature Specifications](docs/FEATURES.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 📄 License

Proprietary — All rights reserved.

---

Built with ❤️ by the NeuroCron Team

