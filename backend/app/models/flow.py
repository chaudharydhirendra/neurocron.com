"""
NeuroCron FlowBuilder Models
Customer journey automation flows
"""

import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base


class FlowStatus(str, enum.Enum):
    """Flow status types"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class NodeType(str, enum.Enum):
    """Flow node types"""
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    DELAY = "delay"
    SPLIT = "split"
    END = "end"


class Flow(Base):
    """Marketing automation flow"""
    
    __tablename__ = "flows"
    
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Status
    status: Mapped[FlowStatus] = mapped_column(
        String(20),
        default=FlowStatus.DRAFT,
        nullable=False,
    )
    
    # Flow configuration (nodes and connections as JSON)
    nodes: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    edges: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # Settings
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Stats
    total_executions: Mapped[int] = mapped_column(Integer, default=0)
    successful_executions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    executions: Mapped[List["FlowExecution"]] = relationship(
        "FlowExecution",
        back_populates="flow",
        lazy="dynamic",
    )


class FlowExecution(Base):
    """Single execution of a flow"""
    
    __tablename__ = "flow_executions"
    
    # Flow reference
    flow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flows.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Contact/lead being processed
    contact_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Current state
    current_node_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="running")  # running, completed, failed, paused
    
    # Execution data
    context: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    history: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    flow: Mapped["Flow"] = relationship("Flow", back_populates="executions")

