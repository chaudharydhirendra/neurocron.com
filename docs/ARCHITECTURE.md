# NeuroCron Architecture

> Complete technical architecture for NeuroCron - The Autonomous Marketing Brain

## System Overview

NeuroCron is a multi-service platform built with:
- **Frontend**: Next.js 14 (App Router)
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 + TimescaleDB
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery + Celery Beat
- **Search**: Meilisearch
- **Storage**: MinIO (S3-compatible)
- **AI**: Ollama (local) + OpenAI/Anthropic (cloud)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         CLIENTS                                              │
│                    Web Browser / Mobile App / API Consumers                                  │
└───────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    NGINX REVERSE PROXY                                       │
│                         SSL Termination | Rate Limiting | Load Balancing                     │
│                    neurocron.com (frontend) | api.neurocron.com (backend)                    │
└────────────────────────────────────┬────────────────────────┬───────────────────────────────┘
                                     │                        │
                    ┌────────────────┴────────────┐           │
                    ▼                             ▼           ▼
┌───────────────────────────────┐  ┌─────────────────────────────────────┐
│       NEXT.JS FRONTEND        │  │          FASTAPI BACKEND            │
│         Port: 3100            │  │           Port: 8100                │
│  ─────────────────────────    │  │  ─────────────────────────────────  │
│  • Landing Page               │  │  • REST API                         │
│  • Dashboard                  │  │  • WebSocket (NeuroCopilot)         │
│  • NeuroCopilot Chat          │  │  • Authentication (JWT)             │
│  • Campaign Management        │  │  • Business Logic                   │
│  • Analytics Views            │  │  • Integration Connectors           │
└───────────────────────────────┘  └─────────────────┬───────────────────┘
                                                     │
                    ┌────────────────────────────────┼────────────────────────────────┐
                    │                                │                                │
                    ▼                                ▼                                ▼
┌───────────────────────────┐  ┌────────────────────────────┐  ┌──────────────────────────┐
│      CELERY WORKERS       │  │       AI SERVICES          │  │    MICROSERVICES         │
│   ─────────────────────   │  │   ──────────────────────   │  │  ────────────────────    │
│   • AutoCron Tasks        │  │   • Ollama (Local LLM)     │  │  • Trend Service (8103)  │
│   • Content Generation    │  │   • OpenAI API             │  │  • Scraper Service(8104) │
│   • Metric Sync           │  │   • Anthropic API          │  │  • Simulation Svc (8105) │
│   • Report Generation     │  │   Port: 8101               │  │                          │
└──────────────┬────────────┘  └────────────────────────────┘  └──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA LAYER                                                │
├──────────────────────┬─────────────────────┬────────────────────┬───────────────────────────┤
│      PostgreSQL      │        Redis        │     Meilisearch    │          MinIO            │
│   ────────────────   │   ───────────────   │   ──────────────   │   ─────────────────────   │
│   Primary Database   │   Cache & Queue     │   Full-text Search │   Object Storage          │
│   TimescaleDB        │   Session Store     │   Content Index    │   Brand Assets            │
│   Port: 5432         │   Port: 6380        │   Port: 7700       │   Port: 9000/9001         │
└──────────────────────┴─────────────────────┴────────────────────┴───────────────────────────┘
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3100 | Next.js application |
| Backend API | 8100 | FastAPI REST API |
| AI Service | 8101 | NeuroCopilot inference |
| WebSocket Hub | 8102 | Real-time communication |
| Trend Service | 8103 | TrendRadar processing |
| Scraper Service | 8104 | BattleStation crawlers |
| Simulation Service | 8105 | SimulatorX engine |
| Celery Flower | 5555 | Task monitoring |
| Meilisearch | 7700 | Search engine |
| MinIO | 9000/9001 | Object storage |
| Redis | 6380 | Cache & queue |
| PostgreSQL | 5432 | Database |
| Ollama | 11434 | Local LLM (shared) |

## Database Schema

### Core Tables

```sql
-- Users & Authentication
users (id, email, hashed_password, full_name, is_active, is_verified, ...)

-- Multi-tenancy
organizations (id, name, slug, plan, settings, ...)
organization_members (id, org_id, user_id, role, ...)

-- Marketing
campaigns (id, org_id, name, status, budget, strategy, metrics, ...)
campaign_contents (id, campaign_id, content_type, body, status, ...)

-- Intelligence
personas (id, org_id, name, attributes, journey_map, ...)
competitors (id, org_id, name, tracking_data, ...)
trends (id, keyword, velocity, sentiment, ...)

-- Analytics (TimescaleDB)
analytics_events (time, org_id, event_type, channel, metrics JSONB)

-- CDP
customer_profiles (id, org_id, external_id, attributes, scores, ...)
touchpoint_events (id, profile_id, event_type, data, ...)
```

## Directory Structure

```
/opt/neurocron.com/
├── docker-compose.yml      # Service orchestration
├── .env.example            # Environment template
├── Makefile                # Dev commands
├── nginx/
│   └── neurocron.conf      # Reverse proxy config
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── core/           # Config, security, deps
│   │   ├── api/v1/         # API routes
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic per module
│   │   └── workers/        # Celery tasks
│   └── alembic/            # Database migrations
├── frontend/
│   └── src/
│       ├── app/            # Next.js pages
│       ├── components/     # React components
│       └── lib/            # Utilities
├── services/               # Microservices
└── docs/                   # Documentation
```

## Security

### Authentication
- JWT access tokens (15 min expiry)
- Refresh tokens (7 day expiry)
- Secure password hashing (bcrypt)

### Authorization
- Role-based access control (RBAC)
- Roles: Owner > Admin > Member > Viewer
- Resource-level permissions

### API Security
- Rate limiting (Redis-based)
- CORS configuration
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)

### Data Security
- TLS 1.2/1.3 in transit
- Encryption at rest (database)
- Secrets management via environment variables

## Deployment

### Development
```bash
# Start development environment
make dev

# Or manually:
docker-compose up -d postgres redis meilisearch minio
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

### Production
```bash
# Build and start all services
make prod-build
make prod-up

# Apply database migrations
make db-upgrade

# Setup SSL (first time)
make setup-ssl
```

## Monitoring

- **Celery Flower**: Task monitoring at `:5555`
- **PostgreSQL**: Connection pooling via SQLAlchemy
- **Redis**: Built-in monitoring
- **Sentry**: Error tracking (optional)
- **Health endpoints**: `/health` on each service

