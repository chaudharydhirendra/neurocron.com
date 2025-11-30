"""
NeuroCron ProjectHub API
AI project manager with task automation
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.project import (
    Project, ProjectStatus, Task, TaskStatus, TaskPriority,
    TaskComment, Milestone, TimeEntry
)

router = APIRouter()


# === Schemas ===

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str = "campaign"
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    budget: float = 0.0


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None
    estimated_hours: float = 0.0
    parent_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class CommentCreate(BaseModel):
    content: str


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


def calculate_project_progress(tasks: List[Task]) -> int:
    if not tasks:
        return 0
    done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
    return round((done / len(tasks)) * 100)


# === Projects ===

@router.get("/projects")
async def list_projects(
    org_id: UUID = Query(...),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List projects."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = select(Project).where(Project.organization_id == org_id)
    
    if status:
        try:
            status_enum = ProjectStatus(status.lower())
            query = query.where(Project.status == status_enum)
        except ValueError:
            pass
    
    query = query.order_by(Project.created_at.desc())
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return {
        "projects": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "project_type": p.project_type,
                "status": p.status.value,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "target_date": p.target_date.isoformat() if p.target_date else None,
                "progress": p.progress,
                "budget": p.budget,
                "spent": p.spent,
                "color": p.color,
                "tags": p.tags or [],
            }
            for p in projects
        ]
    }


@router.post("/projects")
async def create_project(
    project: ProjectCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a project."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_project = Project(
        organization_id=org_id,
        created_by=current_user.id,
        owner_id=current_user.id,
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        start_date=project.start_date,
        target_date=project.target_date,
        budget=project.budget,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return {"id": str(new_project.id), "message": "Project created"}


@router.get("/projects/{project_id}")
async def get_project(
    project_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.organization_id == org_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get tasks
    tasks_result = await db.execute(
        select(Task).where(Task.project_id == project_id)
    )
    tasks = tasks_result.scalars().all()
    
    # Get milestones
    milestones_result = await db.execute(
        select(Milestone)
        .where(Milestone.project_id == project_id)
        .order_by(Milestone.target_date)
    )
    milestones = milestones_result.scalars().all()
    
    # Task stats
    task_stats = {
        "total": len(tasks),
        "todo": sum(1 for t in tasks if t.status == TaskStatus.TODO),
        "in_progress": sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
        "done": sum(1 for t in tasks if t.status == TaskStatus.DONE),
    }
    
    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "project_type": project.project_type,
        "status": project.status.value,
        "start_date": project.start_date.isoformat() if project.start_date else None,
        "target_date": project.target_date.isoformat() if project.target_date else None,
        "progress": project.progress,
        "budget": project.budget,
        "spent": project.spent,
        "ai_brief": project.ai_brief,
        "task_stats": task_stats,
        "milestones": [
            {
                "id": str(m.id),
                "name": m.name,
                "target_date": m.target_date.isoformat() if m.target_date else None,
                "is_completed": m.is_completed,
            }
            for m in milestones
        ],
    }


@router.post("/projects/{project_id}/generate-tasks")
async def generate_project_tasks(
    project_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI generates tasks for the project."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.organization_id == org_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Generate tasks based on project type
    task_templates = {
        "campaign": [
            {"title": "Define campaign objectives and KPIs", "priority": "high"},
            {"title": "Research target audience", "priority": "high"},
            {"title": "Create campaign brief", "priority": "high"},
            {"title": "Design creative assets", "priority": "medium"},
            {"title": "Write ad copy variants", "priority": "medium"},
            {"title": "Set up tracking and analytics", "priority": "medium"},
            {"title": "Configure ad platforms", "priority": "medium"},
            {"title": "Launch campaign", "priority": "high"},
            {"title": "Monitor initial performance", "priority": "high"},
            {"title": "Optimize based on data", "priority": "medium"},
        ],
        "content": [
            {"title": "Create content calendar", "priority": "high"},
            {"title": "Research trending topics", "priority": "medium"},
            {"title": "Write content briefs", "priority": "medium"},
            {"title": "Create first draft", "priority": "high"},
            {"title": "Review and edit", "priority": "medium"},
            {"title": "Design visuals", "priority": "medium"},
            {"title": "Optimize for SEO", "priority": "medium"},
            {"title": "Schedule for publishing", "priority": "low"},
        ],
        "launch": [
            {"title": "Define launch goals", "priority": "high"},
            {"title": "Create launch timeline", "priority": "high"},
            {"title": "Prepare press materials", "priority": "medium"},
            {"title": "Set up landing page", "priority": "high"},
            {"title": "Configure email sequences", "priority": "medium"},
            {"title": "Prepare social media content", "priority": "medium"},
            {"title": "Coordinate with partners", "priority": "medium"},
            {"title": "Execute launch day activities", "priority": "high"},
            {"title": "Post-launch analysis", "priority": "medium"},
        ],
    }
    
    templates = task_templates.get(project.project_type, task_templates["campaign"])
    
    created_tasks = []
    for i, template in enumerate(templates):
        task = Task(
            project_id=project_id,
            title=template["title"],
            priority=TaskPriority(template["priority"]),
            position=i,
            is_ai_generated=True,
            ai_reasoning=f"Auto-generated for {project.project_type} project",
        )
        db.add(task)
        created_tasks.append(template["title"])
    
    # Update project with AI brief
    project.ai_brief = f"AI-generated plan for {project.project_type}: {len(templates)} tasks created covering all phases from planning to execution."
    
    await db.commit()
    
    return {
        "message": f"Generated {len(created_tasks)} tasks",
        "tasks": created_tasks,
    }


# === Tasks ===

@router.get("/projects/{project_id}/tasks")
async def list_tasks(
    project_id: UUID,
    status: Optional[str] = None,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tasks for a project."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = select(Task).where(Task.project_id == project_id)
    
    if status:
        try:
            status_enum = TaskStatus(status.lower())
            query = query.where(Task.status == status_enum)
        except ValueError:
            pass
    
    query = query.order_by(Task.position)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return {
        "tasks": [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "status": t.status.value,
                "priority": t.priority.value,
                "assignee_id": str(t.assignee_id) if t.assignee_id else None,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "estimated_hours": t.estimated_hours,
                "actual_hours": t.actual_hours,
                "labels": t.labels or [],
                "is_ai_generated": t.is_ai_generated,
            }
            for t in tasks
        ]
    }


@router.post("/projects/{project_id}/tasks")
async def create_task(
    project_id: UUID,
    task: TaskCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a task."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get max position
    result = await db.execute(
        select(func.max(Task.position))
        .where(Task.project_id == project_id)
    )
    max_pos = result.scalar() or 0
    
    new_task = Task(
        project_id=project_id,
        parent_id=task.parent_id,
        title=task.title,
        description=task.description,
        priority=TaskPriority(task.priority.lower()),
        assignee_id=task.assignee_id,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours,
        position=max_pos + 1,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    return {"id": str(new_task.id), "message": "Task created"}


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: UUID,
    updates: TaskUpdate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Apply updates
    if updates.title is not None:
        task.title = updates.title
    if updates.description is not None:
        task.description = updates.description
    if updates.status is not None:
        task.status = TaskStatus(updates.status.lower())
        if task.status == TaskStatus.DONE:
            task.completed_at = datetime.utcnow()
        elif task.status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
    if updates.priority is not None:
        task.priority = TaskPriority(updates.priority.lower())
    if updates.assignee_id is not None:
        task.assignee_id = updates.assignee_id
    if updates.due_date is not None:
        task.due_date = updates.due_date
    
    # Update project progress
    project_tasks = await db.execute(
        select(Task).where(Task.project_id == task.project_id)
    )
    all_tasks = project_tasks.scalars().all()
    
    project_result = await db.execute(
        select(Project).where(Project.id == task.project_id)
    )
    project = project_result.scalar_one_or_none()
    if project:
        project.progress = calculate_project_progress(all_tasks)
    
    await db.commit()
    
    return {"message": "Task updated"}


@router.post("/tasks/{task_id}/comments")
async def add_comment(
    task_id: UUID,
    comment: CommentCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a comment to a task."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_comment = TaskComment(
        task_id=task_id,
        author_id=current_user.id,
        content=comment.content,
    )
    db.add(new_comment)
    await db.commit()
    
    return {"message": "Comment added"}


# === Analytics ===

@router.get("/analytics/overview")
async def get_project_analytics(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project analytics overview."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Project counts by status
    project_stats = {}
    for status in ProjectStatus:
        result = await db.execute(
            select(func.count(Project.id))
            .where(Project.organization_id == org_id)
            .where(Project.status == status)
        )
        project_stats[status.value] = result.scalar() or 0
    
    # Task counts
    task_result = await db.execute(
        select(Task.status, func.count(Task.id))
        .join(Project, Task.project_id == Project.id)
        .where(Project.organization_id == org_id)
        .group_by(Task.status)
    )
    task_stats = {row.status.value: row[1] for row in task_result.all()}
    
    # Overdue tasks
    overdue_result = await db.execute(
        select(func.count(Task.id))
        .join(Project, Task.project_id == Project.id)
        .where(Project.organization_id == org_id)
        .where(Task.due_date < datetime.utcnow().date())
        .where(Task.status != TaskStatus.DONE)
    )
    overdue = overdue_result.scalar() or 0
    
    return {
        "projects": project_stats,
        "tasks": task_stats,
        "overdue_tasks": overdue,
        "total_projects": sum(project_stats.values()),
        "total_tasks": sum(task_stats.values()),
    }

