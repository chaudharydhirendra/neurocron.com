"""
NeuroCron SimulatorX API
Marketing what-if prediction engine and scenario planning
"""

import random
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.simulation import (
    Simulation, SimulationStatus, SimulationType,
    SimulationTemplate, PredictionModel, ForecastScenario
)

router = APIRouter()


# === Schemas ===

class SimulationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    simulation_type: str = "budget"
    base_scenario: dict
    test_scenario: dict


class ForecastCreate(BaseModel):
    name: str
    description: Optional[str] = None
    forecast_start: datetime
    forecast_end: datetime
    assumptions: dict


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


def run_simulation_prediction(base: dict, test: dict, sim_type: str) -> dict:
    """Run prediction model for simulation (simplified)."""
    # In production, this would use actual ML models
    base_budget = base.get("budget", 10000)
    test_budget = test.get("budget", base_budget)
    
    # Base metrics (estimated from budget)
    base_impressions = int(base_budget * 100)
    base_clicks = int(base_impressions * 0.02)
    base_conversions = int(base_clicks * 0.05)
    base_revenue = base_conversions * 100
    
    # Calculate test metrics with multipliers
    budget_multiplier = test_budget / base_budget if base_budget > 0 else 1
    
    # Add some randomness for realism
    variance = random.uniform(0.9, 1.1)
    
    test_impressions = int(base_impressions * budget_multiplier * variance)
    test_clicks = int(test_impressions * 0.02 * random.uniform(0.95, 1.05))
    test_conversions = int(test_clicks * 0.05 * random.uniform(0.9, 1.1))
    test_revenue = test_conversions * 100
    
    # Improvement
    improvement = ((test_revenue - base_revenue) / base_revenue * 100) if base_revenue > 0 else 0
    
    return {
        "base_predicted": {
            "impressions": base_impressions,
            "clicks": base_clicks,
            "conversions": base_conversions,
            "revenue": base_revenue,
            "ctr": round(base_clicks / base_impressions * 100, 2) if base_impressions > 0 else 0,
            "cvr": round(base_conversions / base_clicks * 100, 2) if base_clicks > 0 else 0,
            "roas": round(base_revenue / base_budget, 2) if base_budget > 0 else 0,
        },
        "test_predicted": {
            "impressions": test_impressions,
            "clicks": test_clicks,
            "conversions": test_conversions,
            "revenue": test_revenue,
            "ctr": round(test_clicks / test_impressions * 100, 2) if test_impressions > 0 else 0,
            "cvr": round(test_conversions / test_clicks * 100, 2) if test_clicks > 0 else 0,
            "roas": round(test_revenue / test_budget, 2) if test_budget > 0 else 0,
        },
        "improvement_percentage": round(improvement, 1),
        "confidence_score": round(random.uniform(70, 95), 1),
        "risk_level": "low" if improvement > 0 else "medium" if improvement > -10 else "high",
    }


# === Simulations ===

@router.get("/simulations")
async def list_simulations(
    org_id: UUID = Query(...),
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List simulations."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = select(Simulation).where(Simulation.organization_id == org_id)
    
    if status:
        try:
            status_enum = SimulationStatus(status.lower())
            query = query.where(Simulation.status == status_enum)
        except ValueError:
            pass
    
    query = query.order_by(Simulation.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    simulations = result.scalars().all()
    
    return {
        "simulations": [
            {
                "id": str(s.id),
                "name": s.name,
                "simulation_type": s.simulation_type.value,
                "status": s.status.value,
                "improvement_percentage": s.improvement_percentage,
                "confidence_score": s.confidence_score,
                "created_at": s.created_at.isoformat(),
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in simulations
        ]
    }


@router.post("/simulations")
async def create_simulation(
    simulation: SimulationCreate,
    org_id: UUID = Query(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create and run a simulation."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        sim_type = SimulationType(simulation.simulation_type.lower())
    except ValueError:
        sim_type = SimulationType.CUSTOM
    
    new_simulation = Simulation(
        organization_id=org_id,
        created_by=current_user.id,
        name=simulation.name,
        description=simulation.description,
        simulation_type=sim_type,
        base_scenario=simulation.base_scenario,
        test_scenario=simulation.test_scenario,
        status=SimulationStatus.RUNNING,
        started_at=datetime.utcnow(),
    )
    db.add(new_simulation)
    await db.commit()
    await db.refresh(new_simulation)
    
    # Run prediction
    prediction = run_simulation_prediction(
        simulation.base_scenario,
        simulation.test_scenario,
        simulation.simulation_type
    )
    
    # Update with results
    new_simulation.base_predicted_metrics = prediction["base_predicted"]
    new_simulation.predicted_metrics = prediction["test_predicted"]
    new_simulation.improvement_percentage = prediction["improvement_percentage"]
    new_simulation.confidence_score = prediction["confidence_score"]
    new_simulation.risk_level = prediction["risk_level"]
    new_simulation.status = SimulationStatus.COMPLETED
    new_simulation.completed_at = datetime.utcnow()
    
    # Generate insights
    new_simulation.insights = {
        "summary": f"The test scenario shows a {prediction['improvement_percentage']}% change in revenue.",
        "key_drivers": [
            "Budget increase leads to more impressions",
            "Conversion rate remains stable",
        ],
        "risks": [
            "Diminishing returns at higher budgets",
        ] if prediction["improvement_percentage"] < 20 else [],
    }
    new_simulation.recommendations = [
        {"action": "Proceed with test scenario", "priority": "high"} if prediction["improvement_percentage"] > 10 else
        {"action": "Consider alternative approaches", "priority": "medium"},
    ]
    
    await db.commit()
    
    return {
        "id": str(new_simulation.id),
        "status": new_simulation.status.value,
        "results": {
            "base_predicted": prediction["base_predicted"],
            "test_predicted": prediction["test_predicted"],
            "improvement_percentage": prediction["improvement_percentage"],
            "confidence_score": prediction["confidence_score"],
            "risk_level": prediction["risk_level"],
        },
        "insights": new_simulation.insights,
        "recommendations": new_simulation.recommendations,
    }


@router.get("/simulations/{simulation_id}")
async def get_simulation(
    simulation_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get simulation details."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(Simulation)
        .where(Simulation.id == simulation_id)
        .where(Simulation.organization_id == org_id)
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return {
        "id": str(simulation.id),
        "name": simulation.name,
        "description": simulation.description,
        "simulation_type": simulation.simulation_type.value,
        "status": simulation.status.value,
        "base_scenario": simulation.base_scenario,
        "test_scenario": simulation.test_scenario,
        "base_predicted_metrics": simulation.base_predicted_metrics,
        "predicted_metrics": simulation.predicted_metrics,
        "improvement_percentage": simulation.improvement_percentage,
        "confidence_score": simulation.confidence_score,
        "risk_level": simulation.risk_level,
        "insights": simulation.insights,
        "recommendations": simulation.recommendations,
        "created_at": simulation.created_at.isoformat(),
        "completed_at": simulation.completed_at.isoformat() if simulation.completed_at else None,
    }


# === Templates ===

@router.get("/templates")
async def list_templates(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List simulation templates."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get org templates and system templates
    result = await db.execute(
        select(SimulationTemplate)
        .where(
            (SimulationTemplate.organization_id == org_id) |
            (SimulationTemplate.is_system == True)
        )
        .where(SimulationTemplate.is_active == True)
    )
    templates = result.scalars().all()
    
    return {
        "templates": [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "simulation_type": t.simulation_type.value,
                "category": t.category,
                "is_system": t.is_system,
                "variable_fields": t.variable_fields,
            }
            for t in templates
        ]
    }


# === Quick Simulations ===

@router.post("/quick/budget")
async def quick_budget_simulation(
    current_budget: float = Query(...),
    test_budget: float = Query(...),
    channel: str = Query("all"),
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quick budget what-if simulation."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    prediction = run_simulation_prediction(
        {"budget": current_budget, "channel": channel},
        {"budget": test_budget, "channel": channel},
        "budget"
    )
    
    return {
        "scenario": {
            "current_budget": current_budget,
            "test_budget": test_budget,
            "budget_change": test_budget - current_budget,
            "budget_change_percent": round((test_budget - current_budget) / current_budget * 100, 1),
        },
        "prediction": prediction,
        "recommendation": "Increase budget" if prediction["improvement_percentage"] > 10 else "Maintain current budget",
    }


@router.post("/quick/timing")
async def quick_timing_simulation(
    campaign_start: str = Query(...),
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quick timing what-if simulation."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Parse day of week
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_multipliers = {
        "monday": 0.95,
        "tuesday": 1.0,
        "wednesday": 1.02,
        "thursday": 1.05,
        "friday": 0.98,
        "saturday": 0.85,
        "sunday": 0.80,
    }
    
    results = []
    for day in days:
        multiplier = day_multipliers.get(day, 1.0)
        base_revenue = 1000
        results.append({
            "day": day.capitalize(),
            "predicted_revenue": round(base_revenue * multiplier, 2),
            "performance_index": round(multiplier * 100, 1),
            "is_recommended": multiplier >= 1.0,
        })
    
    best_day = max(results, key=lambda x: x["performance_index"])
    
    return {
        "analysis": results,
        "recommendation": f"Best day to launch: {best_day['day']}",
        "best_day": best_day,
    }


# === Forecasting ===

@router.get("/forecasts")
async def list_forecasts(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List forecast scenarios."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(ForecastScenario)
        .where(ForecastScenario.organization_id == org_id)
        .order_by(ForecastScenario.created_at.desc())
    )
    forecasts = result.scalars().all()
    
    return {
        "forecasts": [
            {
                "id": str(f.id),
                "name": f.name,
                "forecast_start": f.forecast_start.isoformat(),
                "forecast_end": f.forecast_end.isoformat(),
                "total_projected_spend": f.total_projected_spend,
                "total_projected_revenue": f.total_projected_revenue,
                "projected_roi": f.projected_roi,
                "status": f.status,
            }
            for f in forecasts
        ]
    }


@router.post("/forecasts")
async def create_forecast(
    forecast: ForecastCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a forecast scenario."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Generate monthly forecast data
    monthly_budget = forecast.assumptions.get("monthly_budget", 10000)
    growth_rate = forecast.assumptions.get("growth_rate", 0.05)
    
    forecast_data = {}
    current_date = forecast.forecast_start
    month_idx = 0
    total_spend = 0
    total_revenue = 0
    
    while current_date <= forecast.forecast_end:
        month_key = current_date.strftime("%Y-%m")
        budget = monthly_budget * (1 + growth_rate) ** month_idx
        revenue = budget * random.uniform(2.5, 4.0)  # ROAS 2.5-4x
        
        forecast_data[month_key] = {
            "budget": round(budget, 2),
            "projected_revenue": round(revenue, 2),
            "projected_roas": round(revenue / budget, 2),
        }
        
        total_spend += budget
        total_revenue += revenue
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
        month_idx += 1
    
    new_forecast = ForecastScenario(
        organization_id=org_id,
        name=forecast.name,
        description=forecast.description,
        forecast_start=forecast.forecast_start,
        forecast_end=forecast.forecast_end,
        assumptions=forecast.assumptions,
        forecast_data=forecast_data,
        total_projected_spend=round(total_spend, 2),
        total_projected_revenue=round(total_revenue, 2),
        projected_roi=round((total_revenue - total_spend) / total_spend * 100, 1) if total_spend > 0 else 0,
        status="active",
    )
    db.add(new_forecast)
    await db.commit()
    await db.refresh(new_forecast)
    
    return {
        "id": str(new_forecast.id),
        "forecast_data": forecast_data,
        "summary": {
            "total_projected_spend": new_forecast.total_projected_spend,
            "total_projected_revenue": new_forecast.total_projected_revenue,
            "projected_roi": new_forecast.projected_roi,
        },
    }

