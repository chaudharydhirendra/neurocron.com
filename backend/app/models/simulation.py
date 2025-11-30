"""
NeuroCron SimulatorX Models
Marketing what-if prediction engine and scenario planning
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base


class SimulationStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationType(str, enum.Enum):
    BUDGET = "budget"
    AUDIENCE = "audience"
    TIMING = "timing"
    CHANNEL = "channel"
    CREATIVE = "creative"
    PRICING = "pricing"
    CUSTOM = "custom"


class Simulation(Base):
    """
    Marketing simulation/what-if scenario.
    """
    
    __tablename__ = "simulations"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Created by
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Simulation info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Type
    simulation_type: Mapped[SimulationType] = mapped_column(
        Enum(SimulationType), default=SimulationType.BUDGET
    )
    
    # Base scenario (current state)
    base_scenario: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"budget": 10000, "audience": "millennials", "channel": "meta"}
    
    # Test scenario (what-if)
    test_scenario: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"budget": 15000, "audience": "gen_z", "channel": "tiktok"}
    
    # Prediction results
    predicted_metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Example: {"impressions": 50000, "clicks": 2500, "conversions": 125, "revenue": 12500}
    
    # Comparison
    base_predicted_metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    improvement_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Confidence
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # low, medium, high
    
    # Model info
    model_version: Mapped[str] = mapped_column(String(50), default="v1")
    
    # Status
    status: Mapped[SimulationStatus] = mapped_column(
        Enum(SimulationStatus), default=SimulationStatus.PENDING
    )
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Insights (AI-generated)
    insights: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    __table_args__ = (
        Index("ix_simulations_org_status", "organization_id", "status"),
    )


class SimulationTemplate(Base):
    """
    Pre-built simulation templates for common scenarios.
    """
    
    __tablename__ = "simulation_templates"
    
    # Organization (null for system templates)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    # Template info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Type
    simulation_type: Mapped[SimulationType] = mapped_column(
        Enum(SimulationType), default=SimulationType.BUDGET
    )
    
    # Template configuration
    base_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    variable_fields: Mapped[dict] = mapped_column(JSONB, default=list)
    # Example: ["budget", "audience_size", "cpm"]
    
    # Metadata
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PredictionModel(Base):
    """
    Machine learning model configuration for predictions.
    """
    
    __tablename__ = "prediction_models"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Model info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)  # linear, xgboost, prophet, neural
    
    # Target metric
    target_metric: Mapped[str] = mapped_column(String(50), nullable=False)  # revenue, conversions, clicks
    
    # Features used
    features: Mapped[dict] = mapped_column(JSONB, default=list)
    
    # Performance metrics
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    mae: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Mean Absolute Error
    rmse: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Root Mean Square Error
    
    # Training info
    training_data_points: Mapped[int] = mapped_column(Integer, default=0)
    last_trained_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Model state
    model_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ForecastScenario(Base):
    """
    Long-term marketing forecast scenario.
    """
    
    __tablename__ = "forecast_scenarios"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Scenario info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Time range
    forecast_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    forecast_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Assumptions
    assumptions: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"monthly_budget": 10000, "growth_rate": 0.05, "seasonality": true}
    
    # Forecast data (time series)
    forecast_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"2024-01": {...}, "2024-02": {...}}
    
    # Summary metrics
    total_projected_spend: Mapped[float] = mapped_column(Float, default=0.0)
    total_projected_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    projected_roi: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, active, archived

