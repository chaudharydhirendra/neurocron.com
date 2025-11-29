"""
NeuroCron - The Autonomous Marketing Brain
Main FastAPI Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🧠 NeuroCron v{settings.APP_VERSION} starting...")
    print(f"📍 Environment: {settings.APP_ENV}")
    print(f"🔗 API URL: {settings.API_URL}")
    
    yield
    
    # Shutdown
    print("🧠 NeuroCron shutting down...")


app = FastAPI(
    title="NeuroCron API",
    description="The Autonomous Marketing Brain - AI-powered marketing automation platform",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "name": "NeuroCron",
        "tagline": "The Autonomous Marketing Brain",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }

