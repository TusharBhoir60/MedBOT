import logging
from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.session import get_db_session
from models.review import ReviewTask, ReviewComment, ReviewStatus
from schemas.review import ReviewTaskResponse, ReviewCommentCreate, ReviewTaskOverride
from api.dependencies import get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/review", tags=["HITL Review"])


async def _get_task(db: AsyncSession, task_id: str) -> ReviewTask | None:
    """Fetch a ReviewTask by string ID, resolving to UUID where needed."""
    try:
        pk = UUID(task_id)
    except ValueError:
        return None
    result = await db.execute(
        select(ReviewTask)
        .options(selectinload(ReviewTask.comments))
        .where(ReviewTask.id == pk)
    )
    return result.scalars().first()

@router.get("/queue", response_model=List[ReviewTaskResponse])
async def get_review_queue(
    db: AsyncSession = Depends(get_db_session),
    user: dict[str, Any] = Depends(require_role("physician"))
):
    """Get all tasks in the review queue."""
    result = await db.execute(
        select(ReviewTask)
        .options(selectinload(ReviewTask.comments))
        .where(ReviewTask.status != ReviewStatus.CLOSED)
        .order_by(ReviewTask.status)
    )
    return result.scalars().all()

@router.post("/{task_id}/assign", response_model=ReviewTaskResponse)
async def assign_task(
    task_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: dict[str, Any] = Depends(require_role("physician"))
):
    """Assign a task to the current physician."""
    task = await _get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.assignee_id = user.get("sub")
    if task.status == ReviewStatus.NEW:
        task.status = ReviewStatus.ASSIGNED
        
    await db.commit()
    db.expire_all()
    task = await _get_task(db, task_id)
    return task

@router.post("/{task_id}/approve", response_model=ReviewTaskResponse)
async def approve_task(
    task_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: dict[str, Any] = Depends(require_role("physician"))
):
    """Approve a task without overrides."""
    task = await _get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.status = ReviewStatus.APPROVED
    await db.commit()
    db.expire_all()
    task = await _get_task(db, task_id)
    return task

@router.post("/{task_id}/override", response_model=ReviewTaskResponse)
async def override_task(
    task_id: str,
    override: ReviewTaskOverride,
    db: AsyncSession = Depends(get_db_session),
    user: dict[str, Any] = Depends(require_role("physician"))
):
    """Override a task's final response."""
    task = await _get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.status = ReviewStatus.OVERRIDDEN
    task.final_response = override.final_response
    await db.commit()
    db.expire_all()
    task = await _get_task(db, task_id)
    return task

@router.post("/{task_id}/comments", response_model=ReviewTaskResponse)
async def add_comment(
    task_id: str,
    comment: ReviewCommentCreate,
    db: AsyncSession = Depends(get_db_session),
    user: dict[str, Any] = Depends(require_role("physician"))
):
    """Add a comment to a review task."""
    task = await _get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    new_comment = ReviewComment(
        task_id=UUID(task_id),
        author_id=user.get("sub"),
        content=comment.content
    )
    db.add(new_comment)
    
    if task.status in (ReviewStatus.NEW, ReviewStatus.ASSIGNED):
        task.status = ReviewStatus.UNDER_REVIEW
        
    await db.commit()
    db.expire_all()
    task = await _get_task(db, task_id)
    return task
