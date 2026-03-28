"""API routes for notebook management."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database import get_async_session
from src.domains.identity.models.user import User
from src.domains.platform.models.notebook import Notebook
from src.domains.platform.schemas.notebook import (
    BulkNotebookOperation,
    BulkOperationResult,
    NotebookCreate,
    NotebookExport,
    NotebookListResponse,
    NotebookResponse,
    NotebookStats,
    NotebookUpdate,
)

router = APIRouter(prefix="/api/notebooks", tags=["notebooks"])


def _to_notebook_response(notebook: Notebook) -> NotebookResponse:
    return NotebookResponse.model_validate(notebook)


async def _get_user_notebook(
    notebook_id: UUID,
    current_user: User,
    session: AsyncSession,
) -> Notebook:
    result = await session.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.tenant_id == current_user.tenant_id,
            Notebook.user_id == current_user.id,
        )
    )
    notebook = result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    return notebook


@router.get("", response_model=NotebookListResponse)
async def list_notebooks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    include_inactive: bool = False,
) -> NotebookListResponse:
    """List all notebooks for the current user."""
    query = select(Notebook).where(Notebook.user_id == current_user.id)
    query = query.where(Notebook.tenant_id == current_user.tenant_id)
    if not include_inactive:
        query = query.where(Notebook.is_active.is_(True))
    query = query.order_by(Notebook.updated_at.desc())

    result = await session.execute(query)
    notebooks = result.scalars().all()

    return NotebookListResponse(
        items=[_to_notebook_response(notebook) for notebook in notebooks],
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
        tenant_id=current_user.tenant_id,
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
    return _to_notebook_response(notebook)


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookResponse:
    """Get a specific notebook by ID."""
    notebook = await _get_user_notebook(notebook_id, current_user, session)
    return _to_notebook_response(notebook)


@router.put("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: UUID,
    data: NotebookUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookResponse:
    """Update a notebook."""
    notebook = await _get_user_notebook(notebook_id, current_user, session)

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
    return _to_notebook_response(notebook)


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Soft delete a notebook (mark as inactive)."""
    notebook = await _get_user_notebook(notebook_id, current_user, session)
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
    await _get_user_notebook(notebook_id, current_user, session)

    from src.domains.platform.models.ai import AIQuery
    from src.domains.platform.models.document import Document
    from src.domains.platform.models.generated_content import GeneratedContent

    doc_result = await session.execute(
        select(func.count(Document.id)).where(
            Document.tenant_id == current_user.tenant_id,
            Document.notebook_id == notebook_id,
            Document.uploaded_by == current_user.id,
        )
    )
    document_count = doc_result.scalar() or 0

    query_result = await session.execute(
        select(func.count(AIQuery.id)).where(
            AIQuery.tenant_id == current_user.tenant_id,
            AIQuery.notebook_id == notebook_id,
            AIQuery.user_id == current_user.id,
            AIQuery.deleted_at.is_(None),
        )
    )
    question_count = query_result.scalar() or 0

    quiz_result = await session.execute(
        select(func.count(GeneratedContent.id)).where(
            GeneratedContent.tenant_id == current_user.tenant_id,
            GeneratedContent.notebook_id == notebook_id,
            GeneratedContent.user_id == current_user.id,
            GeneratedContent.type == "quiz",
            GeneratedContent.is_archived.is_(False),
        )
    )
    quiz_count = quiz_result.scalar() or 0

    flashcard_result = await session.execute(
        select(func.count(GeneratedContent.id)).where(
            GeneratedContent.tenant_id == current_user.tenant_id,
            GeneratedContent.notebook_id == notebook_id,
            GeneratedContent.user_id == current_user.id,
            GeneratedContent.type == "flashcards",
            GeneratedContent.is_archived.is_(False),
        )
    )
    flashcard_count = flashcard_result.scalar() or 0

    mindmap_result = await session.execute(
        select(func.count(GeneratedContent.id)).where(
            GeneratedContent.tenant_id == current_user.tenant_id,
            GeneratedContent.notebook_id == notebook_id,
            GeneratedContent.user_id == current_user.id,
            GeneratedContent.type.in_(["mindmap", "concept_map", "flowchart"]),
            GeneratedContent.is_archived.is_(False),
        )
    )
    mindmap_count = mindmap_result.scalar() or 0

    last_query_result = await session.execute(
        select(AIQuery.created_at)
        .where(
            AIQuery.tenant_id == current_user.tenant_id,
            AIQuery.notebook_id == notebook_id,
            AIQuery.user_id == current_user.id,
            AIQuery.deleted_at.is_(None),
        )
        .order_by(AIQuery.created_at.desc())
        .limit(1)
    )
    last_accessed = last_query_result.scalar()

    study_time_result = await session.execute(
        select(func.sum(AIQuery.response_time_ms)).where(
            AIQuery.tenant_id == current_user.tenant_id,
            AIQuery.notebook_id == notebook_id,
            AIQuery.user_id == current_user.id,
            AIQuery.deleted_at.is_(None),
        )
    )
    total_response_time = study_time_result.scalar() or 0
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
    notebook = await _get_user_notebook(notebook_id, current_user, session)

    from src.domains.platform.models.ai import AIQuery
    from src.domains.platform.models.document import Document
    from src.domains.platform.models.generated_content import GeneratedContent

    doc_result = await session.execute(
        select(Document).where(
            Document.tenant_id == current_user.tenant_id,
            Document.notebook_id == notebook_id,
            Document.uploaded_by == current_user.id,
        )
    )
    documents = [
        {
            "id": str(document.id),
            "filename": document.file_name,
            "file_type": document.file_type,
            "uploaded_at": document.created_at.isoformat() if document.created_at else None,
        }
        for document in doc_result.scalars().all()
    ]

    history_result = await session.execute(
        select(AIQuery)
        .where(
            AIQuery.tenant_id == current_user.tenant_id,
            AIQuery.notebook_id == notebook_id,
            AIQuery.user_id == current_user.id,
            AIQuery.deleted_at.is_(None),
        )
        .order_by(AIQuery.created_at.desc())
        .limit(100)
    )
    ai_history = [
        {
            "id": str(item.id),
            "query": item.query_text,
            "mode": item.mode,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in history_result.scalars().all()
    ]

    content_result = await session.execute(
        select(GeneratedContent).where(
            GeneratedContent.tenant_id == current_user.tenant_id,
            GeneratedContent.notebook_id == notebook_id,
            GeneratedContent.user_id == current_user.id,
            GeneratedContent.is_archived.is_(False),
        )
    )
    generated_content = [
        {
            "id": str(item.id),
            "type": item.type,
            "title": item.title,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in content_result.scalars().all()
    ]

    stats = await get_notebook_stats(notebook_id, current_user, session)

    return NotebookExport(
        notebook=_to_notebook_response(notebook),
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
    success: list[UUID] = []
    failed: list[dict] = []

    for notebook_id in data.notebook_ids:
        try:
            notebook = await _get_user_notebook(notebook_id, current_user, session)
            if data.operation in {"archive", "delete"}:
                notebook.is_active = False
            elif data.operation == "restore":
                notebook.is_active = True
            else:
                failed.append({"id": str(notebook_id), "error": f"Unknown operation: {data.operation}"})
                continue

            notebook.updated_at = datetime.utcnow()
            success.append(notebook_id)
        except HTTPException as exc:
            failed.append({"id": str(notebook_id), "error": exc.detail})
        except Exception as exc:
            failed.append({"id": str(notebook_id), "error": str(exc)})

    await session.commit()

    return BulkOperationResult(
        success=[str(item) for item in success],
        failed=failed,
        total_processed=len(data.notebook_ids),
    )
