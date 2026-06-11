from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.orm import User, ResourceProgress
from app.models.schemas import ResourcesResponse, ResourceItem, CompleteResourceRequest
from app.services.resources_catalog import get_resources, get_all_resource_ids

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/{category}", response_model=ResourcesResponse)
async def get_resources_for_category(
    category: str,
    username: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    resources = get_resources(category)
    if not resources:
        raise HTTPException(status_code=404, detail=f"No resources found for category '{category}'")

    # Get user's completed resource IDs
    completed_ids: set[str] = set()
    stmt = select(User).where(User.chess_com_username == username.strip().lower())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        progress_stmt = select(ResourceProgress).where(ResourceProgress.user_id == user.id)
        progress = (await db.execute(progress_stmt)).scalars().all()
        completed_ids = {p.resource_id for p in progress}

    items = [
        ResourceItem(
            id=r["id"],
            title=r["title"],
            url=r["url"],
            type=r["type"],
            description=r["description"],
            completed=r["id"] in completed_ids,
        )
        for r in resources
    ]

    return ResourcesResponse(category=category, resources=items)


@router.patch("/{resource_id}/complete", response_model=dict)
async def complete_resource(
    resource_id: str,
    body: CompleteResourceRequest,
    db: AsyncSession = Depends(get_db),
):
    all_ids = get_all_resource_ids()
    if resource_id not in all_ids:
        raise HTTPException(status_code=404, detail="Resource not found")

    username = body.username.strip().lower()
    stmt = select(User).where(User.chess_com_username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already completed
    existing_stmt = select(ResourceProgress).where(
        ResourceProgress.user_id == user.id,
        ResourceProgress.resource_id == resource_id,
    )
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()

    if existing:
        # Toggle: delete if already completed
        await db.delete(existing)
        await db.commit()
        return {"resource_id": resource_id, "completed": False}

    db.add(ResourceProgress(
        user_id=user.id,
        resource_id=resource_id,
        completed_at=datetime.utcnow(),
    ))
    await db.commit()
    return {"resource_id": resource_id, "completed": True}
