"""API routes for generated content management."""
from datetime import datetime
from typing import Tuple
from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Result, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from auth.dependencies import get_current_user
from database import get_async_session
from src.domains.identity.models.user import User
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.models.notebook import Notebook
from src.domains.platform.schemas.generated_content import (
    GeneratedContentCreate,
    GeneratedContentListResponse,
    GeneratedContentResponse,
    GeneratedContentUpdate,
)

router = APIRouter(prefix="/api/generated-content", tags=["generated-content"])


def _to_response(content: GeneratedContent) -> GeneratedContentResponse:
    return GeneratedContentResponse.model_validate(content)


async def _ensure_notebook_access(
    notebook_id: UUID,
    current_user: User,
    session: AsyncSession,
) -> Notebook:
    result: Result[Tuple[Notebook]] = await session.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.tenant_id == current_user.tenant_id,
            Notebook.user_id == current_user.id,
        )
    )
    notebook: Notebook | None = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    return notebook


@router.get("", response_model=GeneratedContentListResponse)
async def list_generated_content(
    notebook_id: UUID,
    type: str | None = Query(None, description="Filter by content type"),
    is_archived: bool = Query(False, description="Include archived content"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentListResponse:
    """List generated content for a notebook."""
    await _ensure_notebook_access(notebook_id, current_user, session)

    conditions: list[ColumnElement[bool]] = [
        GeneratedContent.tenant_id == current_user.tenant_id,
        GeneratedContent.notebook_id == notebook_id,
        GeneratedContent.user_id == current_user.id,
    ]
    if type:
        conditions.append(GeneratedContent.type == type)
    if not is_archived:
        conditions.append(GeneratedContent.is_archived.is_(False))

    total_result: Result[Tuple[int]] = await session.execute(
        select(func.count()).select_from(GeneratedContent).where(and_(*conditions))
    )
    total: int = total_result.scalar() or 0

    result: Result[Tuple[GeneratedContent]] = await session.execute(
        select(GeneratedContent)
        .where(and_(*conditions))
        .order_by(GeneratedContent.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items: Sequence[GeneratedContent] = result.scalars().all()

    return GeneratedContentListResponse(
        items=[_to_response(item) for item in items],
        total=total,
    )


@router.post("", response_model=GeneratedContentResponse, status_code=status.HTTP_201_CREATED)
async def create_generated_content(
    data: GeneratedContentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentResponse:
    """Create new generated content."""
    notebook: Notebook = await _ensure_notebook_access(data.notebook_id, current_user, session)

    content = GeneratedContent(
        tenant_id=notebook.tenant_id,
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
    return _to_response(content)


@router.get("/{content_id}", response_model=GeneratedContentResponse)
async def get_generated_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentResponse:
    """Get a specific generated content item."""
    result: Result[Tuple[GeneratedContent]] = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.tenant_id == current_user.tenant_id,
            GeneratedContent.user_id == current_user.id,
        )
    )
    content: GeneratedContent | None = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    return _to_response(content)


@router.put("/{content_id}", response_model=GeneratedContentResponse)
async def update_generated_content(
    content_id: UUID,
    data: GeneratedContentUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentResponse:
    """Update generated content."""
    result: Result[Tuple[GeneratedContent]] = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.tenant_id == current_user.tenant_id,
            GeneratedContent.user_id == current_user.id,
        )
    )
    content: GeneratedContent | None = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    if data.title is not None:
        content.title = data.title
    if data.content is not None:
        content.content = data.content
    if data.is_archived is not None:
        content.is_archived = data.is_archived

    content.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(content)
    return _to_response(content)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_generated_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Archive generated content."""
    result: Result[Tuple[GeneratedContent]] = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.tenant_id == current_user.tenant_id,
            GeneratedContent.user_id == current_user.id,
        )
    )
    content: GeneratedContent | None = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    content.is_archived = True
    content.updated_at = datetime.utcnow()
    await session.commit()


@router.post("/{content_id}/restore", response_model=GeneratedContentResponse)
async def restore_generated_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> GeneratedContentResponse:
    """Restore archived generated content."""
    result: Result[Tuple[GeneratedContent]] = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.tenant_id == current_user.tenant_id,
            GeneratedContent.user_id == current_user.id,
        )
    )
    content: GeneratedContent | None = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    content.is_archived = False
    content.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(content)
    return _to_response(content)
