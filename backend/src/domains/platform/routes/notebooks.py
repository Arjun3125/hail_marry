"""API routes for notebook management."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from src.domains.platform.models.notebook import Notebook
from src.domains.platform.schemas.notebook import (
    NotebookCreate,
    NotebookListResponse,
    NotebookResponse,
    NotebookStats,
    NotebookUpdate,
    NotebookExport,
    BulkNotebookOperation,
    BulkOperationResult,
)
from auth.dependencies import get_current_user
from src.domains.identity.models.user import User

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("", response_model=NotebookListResponse)
async def list_notebooks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    include_inactive: bool = False,
) -> NotebookListResponse:
    """List all notebooks for the current user."""
    query = select(Notebook).where(Notebook.user_id == current_user.id)
    
    if not include_inactive:
        query = query.where(Notebook.is_active == True)
    
    query = query.order_by(Notebook.updated_at.desc())
    
    result = await session.execute(query)
    notebooks = result.scalars().all()
    
    return NotebookListResponse(
        items=[NotebookResponse.from_orm(n) for n in notebooks],
        total=len(notebooks),
    )


@router.post("", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    data: NotebookCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookResponse:
    """Create a new notebook."""
    notebook = Notebook(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        subject=data.subject,
        color=data.color,
        icon=data.icon,
    )
    
    session.add(notebook)
    await session.commit()
    await session.refresh(notebook)
    
    return NotebookResponse.from_orm(notebook)


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookResponse:
    """Get a specific notebook by ID."""
    result = await session.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.user_id == current_user.id,
        )
    )
    notebook = result.scalar_one_or_none()
    
    if not notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    
    return NotebookResponse.from_orm(notebook)


@router.put("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: UUID,
    data: NotebookUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookResponse:
    """Update a notebook."""
    result = await session.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.user_id == current_user.id,
        )
    )
    notebook = result.scalar_one_or_none()
    
    if not notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    
    # Update fields
    if data.name is not None:
        notebook.name = data.name
    if data.description is not None:
        notebook.description = data.description
    if data.subject is not None:
        notebook.subject = data.subject
    if data.color is not None:
        notebook.color = data.color
    if data.icon is not None:
        notebook.icon = data.icon
    if data.is_active is not None:
        notebook.is_active = data.is_active
    
    notebook.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(notebook)
    
    return NotebookResponse.from_orm(notebook)


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Soft delete a notebook (mark as inactive)."""
    result = await session.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.user_id == current_user.id,
        )
    )
    notebook = result.scalar_one_or_none()
    
    if not notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    
    notebook.is_active = False
    notebook.updated_at = datetime.utcnow()
    
    await session.commit()


@router.get("/{notebook_id}/stats", response_model=NotebookStats)
async def get_notebook_stats(
    notebook_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookStats:
    """Get comprehensive statistics for a notebook."""
    # Verify notebook exists and belongs to user
    result = await session.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.user_id == current_user.id,
        )
    )
    notebook = result.scalar_one_or_none()
    
    if not notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    
    # Count documents in notebook
    from src.domains.platform.models.document import Document
    doc_result = await session.execute(
        select(func.count(Document.id)).where(
            Document.notebook_id == notebook_id,
            Document.user_id == current_user.id,
        )
    )
    document_count = doc_result.scalar() or 0
    
    # Count AI queries in notebook
    from src.domains.platform.models.ai import AIQuery
    query_result = await session.execute(
        select(func.count(AIQuery.id)).where(
            AIQuery.notebook_id == notebook_id,
            AIQuery.user_id == current_user.id,
            AIQuery.deleted_at.is_(None),
        )
    )
    question_count = query_result.scalar() or 0
    
    # Count generated content by type
    from src.domains.platform.models.generated_content import GeneratedContent
    
    # Quiz count
    quiz_result = await session.execute(
        select(func.count(GeneratedContent.id)).where(
            GeneratedContent.notebook_id == notebook_id,
            GeneratedContent.user_id == current_user.id,
            GeneratedContent.type == "quiz",
            GeneratedContent.is_archived == False,
        )
    )
    quiz_count = quiz_result.scalar() or 0
    
    # Flashcard count
    flashcard_result = await session.execute(
        select(func.count(GeneratedContent.id)).where(
            GeneratedContent.notebook_id == notebook_id,
            GeneratedContent.user_id == current_user.id,
            GeneratedContent.type == "flashcards",
            GeneratedContent.is_archived == False,
        )
    )
    flashcard_count = flashcard_result.scalar() or 0
    
    # Mind map count
    mindmap_result = await session.execute(
        select(func.count(GeneratedContent.id)).where(
            GeneratedContent.notebook_id == notebook_id,
            GeneratedContent.user_id == current_user.id,
            GeneratedContent.type.in_(["mindmap", "concept_map"]),
            GeneratedContent.is_archived == False,
        )
    )
    mindmap_count = mindmap_result.scalar() or 0
    
    # Get last accessed time (most recent AI query or document upload)
    last_query_result = await session.execute(
        select(AIQuery.created_at).where(
            AIQuery.notebook_id == notebook_id,
            AIQuery.user_id == current_user.id,
        ).order_by(AIQuery.created_at.desc()).limit(1)
    )
    last_accessed = last_query_result.scalar()
    
    # Calculate total study time (sum of response times as proxy)
    study_time_result = await session.execute(
        select(func.sum(AIQuery.response_time_ms)).where(
            AIQuery.notebook_id == notebook_id,
            AIQuery.user_id == current_user.id,
        )
    )
    total_response_time = study_time_result.scalar() or 0
    # Convert to minutes (rough estimate: response time is just AI processing)
    # Add 30 seconds per query as estimated user reading time
    total_study_time = (total_response_time / 1000 + question_count * 30) / 60
    
    return NotebookStats(
        document_count=document_count,
        question_count=question_count,
        quiz_count=quiz_count,
        flashcard_count=flashcard_count,
        mindmap_count=mindmap_count,
        total_study_time=round(total_study_time, 2),
        last_accessed=last_accessed,
    )


@router.get("/{notebook_id}/export", response_model=NotebookExport)
async def export_notebook(
    notebook_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookExport:
    """Export all notebook data for backup or sharing."""
    # Verify notebook exists and belongs to user
    result = await session.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.user_id == current_user.id,
        )
    )
    notebook = result.scalar_one_or_none()
    
    if not notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    
    # Get documents
    from src.domains.platform.models.document import Document
    doc_result = await session.execute(
        select(Document).where(
            Document.notebook_id == notebook_id,
            Document.user_id == current_user.id,
        )
    )
    documents = [
        {
            "id": str(d.id),
            "filename": d.filename,
            "file_type": d.file_type,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
        }
        for d in doc_result.scalars().all()
    ]
    
    # Get AI history
    from src.domains.platform.models.ai import AIQuery
    history_result = await session.execute(
        select(AIQuery).where(
            AIQuery.notebook_id == notebook_id,
            AIQuery.user_id == current_user.id,
            AIQuery.deleted_at.is_(None),
        ).order_by(AIQuery.created_at.desc()).limit(100)
    )
    ai_history = [
        {
            "id": str(h.id),
            "query": h.query_text,
            "mode": h.mode,
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }
        for h in history_result.scalars().all()
    ]
    
    # Get generated content
    from src.domains.platform.models.generated_content import GeneratedContent
    content_result = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.notebook_id == notebook_id,
            GeneratedContent.user_id == current_user.id,
            GeneratedContent.is_archived == False,
        )
    )
    generated_content = [
        {
            "id": str(c.id),
            "type": c.type,
            "title": c.title,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in content_result.scalars().all()
    ]
    
    # Get stats (reuse existing logic)
    stats = await get_notebook_stats(notebook_id, current_user, session)
    
    return NotebookExport(
        notebook=NotebookResponse.from_orm(notebook),
        documents=documents,
        ai_history=ai_history,
        generated_content=generated_content,
        stats=stats,
        exported_at=datetime.utcnow(),
    )


@router.post("/bulk", response_model=BulkOperationResult)
async def bulk_notebook_operation(
    data: BulkNotebookOperation,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> BulkOperationResult:
    """Perform bulk operations on multiple notebooks."""
    success = []
    failed = []
    
    for notebook_id in data.notebook_ids:
        try:
            result = await session.execute(
                select(Notebook).where(
                    Notebook.id == notebook_id,
                    Notebook.user_id == current_user.id,
                )
            )
            notebook = result.scalar_one_or_none()
            
            if not notebook:
                failed.append({"id": str(notebook_id), "error": "Notebook not found"})
                continue
            
            if data.operation == "archive":
                notebook.is_active = False
                notebook.updated_at = datetime.utcnow()
            elif data.operation == "delete":
                notebook.is_active = False
                notebook.updated_at = datetime.utcnow()
            elif data.operation == "restore":
                notebook.is_active = True
                notebook.updated_at = datetime.utcnow()
            else:
                failed.append({"id": str(notebook_id), "error": f"Unknown operation: {data.operation}"})
                continue
            
            success.append(notebook_id)
        except Exception as e:
            failed.append({"id": str(notebook_id), "error": str(e)})
    
    await session.commit()
    
    return BulkOperationResult(
        success=[str(s) for s in success],
        failed=failed,
        total_processed=len(data.notebook_ids),
    )
