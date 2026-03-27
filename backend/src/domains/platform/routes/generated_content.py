"""API routes for generated content management."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.schemas.generated_content import (
    GeneratedContentCreate,
    GeneratedContentFilter,
    GeneratedContentListResponse,
    GeneratedContentResponse,
    GeneratedContentUpdate,
)
from auth.dependencies import get_current_user
from src.domains.identity.models.user import User

router = APIRouter(prefix="/generated-content", tags=["generated-content"])


@router.get("", response_model=GeneratedContentListResponse)
async def list_generated_content(
    notebook_id: UUID,
    type: Optional[str] = Query(None, description="Filter by content type"),
    is_archived: bool = Query(False, description="Include archived content"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentListResponse:
    """List generated content for a notebook."""
    # Build query
    conditions = [
        GeneratedContent.notebook_id == notebook_id,
        GeneratedContent.user_id == current_user.id,
    ]
    
    if type:
        conditions.append(GeneratedContent.type == type)
    if not is_archived:
        conditions.append(GeneratedContent.is_archived == False)
    
    # Get total count
    count_query = select(func.count()).select_from(GeneratedContent).where(and_(*conditions))
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    # Get items
    query = (
        select(GeneratedContent)
        .where(and_(*conditions))
        .order_by(GeneratedContent.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(query)
    items = result.scalars().all()
    
    return GeneratedContentListResponse(
        items=[GeneratedContentResponse.from_orm(item) for item in items],
        total=total,
    )


@router.post("", response_model=GeneratedContentResponse, status_code=status.HTTP_201_CREATED)
async def create_generated_content(
    data: GeneratedContentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentResponse:
    """Create new generated content."""
    content = GeneratedContent(
        notebook_id=data.notebook_id,
        user_id=current_user.id,
        type=data.type,
        title=data.title,
        content=data.content,
        source_query=data.source_query,
        parent_conversation_id=data.parent_conversation_id,
    )
    
    session.add(content)
    await session.commit()
    await session.refresh(content)
    
    return GeneratedContentResponse.from_orm(content)


@router.get("/{content_id}", response_model=GeneratedContentResponse)
async def get_generated_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentResponse:
    """Get a specific generated content by ID."""
    result = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.user_id == current_user.id,
        )
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )
    
    return GeneratedContentResponse.from_orm(content)


@router.put("/{content_id}", response_model=GeneratedContentResponse)
async def update_generated_content(
    content_id: UUID,
    data: GeneratedContentUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentResponse:
    """Update generated content."""
    result = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.user_id == current_user.id,
        )
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )
    
    # Update fields
    if data.title is not None:
        content.title = data.title
    if data.content is not None:
        content.content = data.content
    if data.is_archived is not None:
        content.is_archived = data.is_archived
    
    content.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(content)
    
    return GeneratedContentResponse.from_orm(content)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_generated_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete generated content (or archive it)."""
    result = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.user_id == current_user.id,
        )
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )
    
    # Soft delete by archiving
    content.is_archived = True
    content.updated_at = datetime.utcnow()
    
    await session.commit()
