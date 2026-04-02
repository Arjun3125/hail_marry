"""AI History API routes for viewing and managing past AI queries."""
from typing import Optional
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, or_, and_

from database import get_db
from auth.dependencies import get_current_user
from src.domains.identity.models.user import User
from src.domains.platform.models.ai import AIQuery, AIFolder
from src.domains.platform.schemas.ai_history import (
    AIHistoryItem,
    AIHistoryListResponse,
    AIFolderCreate,
    AIFolderUpdate,
    AIFolderResponse,
    AIFolderListResponse,
    AIHistoryUpdateTitle,
    AIHistoryMoveToFolder,
    AIHistoryStats,
    AIHistorySearchResponse,
    AIHistorySearchResult,
)

router = APIRouter(prefix="/api/student/ai-history", tags=["AI History"])


def _parse_uuid(value: str, *, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}") from exc


def _query_to_item(query, folder_name=None):
    """Convert AIQuery model to response item."""
    return AIHistoryItem(
        id=str(query.id),
        mode=query.mode,
        query_text=query.query_text,
        response_text=query.response_text or "",
        title=query.title,
        created_at=query.created_at,
        token_usage=query.token_usage,
        citation_count=query.citation_count or 0,
        is_pinned=query.is_pinned or False,
        folder_id=str(query.folder_id) if query.folder_id else None,
        folder_name=folder_name,
        trace_id=query.trace_id,
    )


@router.get("", response_model=AIHistoryListResponse)
async def get_ai_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mode: Optional[str] = Query(None, description="Filter by AI mode"),
    folder_id: Optional[str] = Query(None, description="Filter by folder"),
    is_pinned: Optional[bool] = Query(None, description="Filter pinned items"),
    search: Optional[str] = Query(None, description="Search in query and response"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|title|mode)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    """Get paginated AI history for current user."""
    # Base query - filter by user and not deleted
    base_query = db.query(AIQuery).filter(
        AIQuery.user_id == current_user.id,
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.deleted_at.is_(None)
    )
    
    # Apply filters
    if mode:
        base_query = base_query.filter(AIQuery.mode == mode)
    if folder_id:
        base_query = base_query.filter(AIQuery.folder_id == _parse_uuid(folder_id, field_name="folder_id"))
    if is_pinned is not None:
        base_query = base_query.filter(AIQuery.is_pinned == is_pinned)
    if search:
        search_filter = or_(
            AIQuery.query_text.ilike(f"%{search}%"),
            AIQuery.response_text.ilike(f"%{search}%"),
            AIQuery.title.ilike(f"%{search}%"),
        )
        base_query = base_query.filter(search_filter)
    if date_from:
        base_query = base_query.filter(AIQuery.created_at >= date_from)
    if date_to:
        base_query = base_query.filter(AIQuery.created_at <= date_to)
    
    # Get total count
    total = base_query.count()
    
    # Apply sorting
    sort_column = getattr(AIQuery, sort_by, AIQuery.created_at)
    if sort_order == "desc":
        base_query = base_query.order_by(desc(sort_column))
    else:
        base_query = base_query.order_by(asc(sort_column))
    
    # Apply pagination
    offset = (page - 1) * page_size
    queries = base_query.offset(offset).limit(page_size).all()
    
    # Get folder names for joining
    folder_ids = [q.folder_id for q in queries if q.folder_id]
    folders = {f.id: f.name for f in db.query(AIFolder).filter(AIFolder.id.in_(folder_ids)).all()} if folder_ids else {}
    
    items = [_query_to_item(q, folders.get(q.folder_id)) for q in queries]
    
    return AIHistoryListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=offset + len(items) < total,
    )



@router.get("/folders", response_model=AIFolderListResponse)
async def get_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all AI folders for current user with item counts."""
    folders = db.query(AIFolder).filter(
        AIFolder.user_id == current_user.id,
        AIFolder.tenant_id == current_user.tenant_id,
    ).order_by(AIFolder.name).all()
    
    # Get item counts
    folder_ids = [f.id for f in folders]
    counts = {}
    if folder_ids:
        count_query = db.query(
            AIQuery.folder_id,
            func.count(AIQuery.id).label("count")
        ).filter(
            AIQuery.folder_id.in_(folder_ids),
            AIQuery.deleted_at.is_(None),
        ).group_by(AIQuery.folder_id).all()
        counts = {str(f_id): cnt for f_id, cnt in count_query}
    
    folder_responses = [
        AIFolderResponse(
            id=str(f.id),
            name=f.name,
            color=f.color,
            created_at=f.created_at,
            item_count=counts.get(str(f.id), 0),
        )
        for f in folders
    ]
    
    return AIFolderListResponse(folders=folder_responses)


@router.post("/folders", response_model=AIFolderResponse)
async def create_folder(
    data: AIFolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new AI folder."""
    folder = AIFolder(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        name=data.name,
        color=data.color,
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    return AIFolderResponse(
        id=str(folder.id),
        name=folder.name,
        color=folder.color,
        created_at=folder.created_at,
        item_count=0,
    )


@router.patch("/folders/{folder_id}", response_model=AIFolderResponse)
async def update_folder(
    folder_id: str,
    data: AIFolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an AI folder."""
    folder_uuid = _parse_uuid(folder_id, field_name="folder_id")
    folder = db.query(AIFolder).filter(
        AIFolder.id == folder_uuid,
        AIFolder.user_id == current_user.id,
        AIFolder.tenant_id == current_user.tenant_id,
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if data.name is not None:
        folder.name = data.name
    if data.color is not None:
        folder.color = data.color
    
    db.commit()
    db.refresh(folder)
    
    # Get item count
    count = db.query(AIQuery).filter(
        AIQuery.folder_id == folder.id,
        AIQuery.deleted_at.is_(None),
    ).count()
    
    return AIFolderResponse(
        id=str(folder.id),
        name=folder.name,
        color=folder.color,
        created_at=folder.created_at,
        item_count=count,
    )


@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a folder and move items to uncategorized."""
    folder_uuid = _parse_uuid(folder_id, field_name="folder_id")
    folder = db.query(AIFolder).filter(
        AIFolder.id == folder_uuid,
        AIFolder.user_id == current_user.id,
        AIFolder.tenant_id == current_user.tenant_id,
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Move items to uncategorized
    db.query(AIQuery).filter(AIQuery.folder_id == folder_uuid).update({"folder_id": None})
    
    db.delete(folder)
    db.commit()
    
    return {"success": True, "deleted": True}


# Statistics endpoint

@router.get("/stats", response_model=AIHistoryStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI usage statistics for current user."""
    base_query = db.query(AIQuery).filter(
        AIQuery.user_id == current_user.id,
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.deleted_at.is_(None),
    )
    
    total = base_query.count()
    
    # Count by mode
    mode_counts = db.query(
        AIQuery.mode,
        func.count(AIQuery.id).label("count")
    ).filter(
        AIQuery.user_id == current_user.id,
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.deleted_at.is_(None),
    ).group_by(AIQuery.mode).all()
    
    queries_by_mode = {mode: count for mode, count in mode_counts}
    
    # Time-based stats
    now = datetime.now(UTC)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    queries_this_week = base_query.filter(AIQuery.created_at >= week_ago).count()
    queries_this_month = base_query.filter(AIQuery.created_at >= month_ago).count()
    
    # Favorite mode
    favorite_mode = max(queries_by_mode, key=queries_by_mode.get) if queries_by_mode else None
    
    # Simple streak calculation (consecutive days with queries)
    streak_days = 0  # Simplified - could be enhanced with actual date sequence analysis
    
    return AIHistoryStats(
        total_queries=total,
        queries_by_mode=queries_by_mode,
        queries_this_week=queries_this_week,
        queries_this_month=queries_this_month,
        favorite_mode=favorite_mode,
        streak_days=streak_days,
    )


# Item Management endpoints
@router.get("/{item_id}", response_model=AIHistoryItem)
async def get_ai_history_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single AI history item."""
    item_uuid = _parse_uuid(item_id, field_name="item_id")
    query = db.query(AIQuery).filter(
        AIQuery.id == item_uuid,
        AIQuery.user_id == current_user.id,
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.deleted_at.is_(None),
    ).first()
    
    if not query:
        raise HTTPException(status_code=404, detail="Item not found")
    
    folder_name = None
    if query.folder_id:
        folder = db.query(AIFolder).filter(AIFolder.id == query.folder_id).first()
        folder_name = folder.name if folder else None
    
    return _query_to_item(query, folder_name)


@router.patch("/{item_id}/title")
async def update_item_title(
    item_id: str,
    data: AIHistoryUpdateTitle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the title of an AI history item."""
    item_uuid = _parse_uuid(item_id, field_name="item_id")
    query = db.query(AIQuery).filter(
        AIQuery.id == item_uuid,
        AIQuery.user_id == current_user.id,
        AIQuery.tenant_id == current_user.tenant_id,
    ).first()
    
    if not query:
        raise HTTPException(status_code=404, detail="Item not found")
    
    query.title = data.title
    db.commit()
    return {"success": True, "title": data.title}


@router.post("/{item_id}/pin")
async def toggle_pin(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle pin status of an AI history item."""
    item_uuid = _parse_uuid(item_id, field_name="item_id")
    query = db.query(AIQuery).filter(
        AIQuery.id == item_uuid,
        AIQuery.user_id == current_user.id,
        AIQuery.tenant_id == current_user.tenant_id,
    ).first()
    
    if not query:
        raise HTTPException(status_code=404, detail="Item not found")
    
    query.is_pinned = not (query.is_pinned or False)
    db.commit()
    return {"success": True, "is_pinned": query.is_pinned}


@router.delete("/{item_id}")
async def delete_history_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete an AI history item."""
    item_uuid = _parse_uuid(item_id, field_name="item_id")
    query = db.query(AIQuery).filter(
        AIQuery.id == item_uuid,
        AIQuery.user_id == current_user.id,
        AIQuery.tenant_id == current_user.tenant_id,
    ).first()
    
    if not query:
        raise HTTPException(status_code=404, detail="Item not found")
    
    query.deleted_at = datetime.now(UTC)
    db.commit()
    return {"success": True, "deleted": True}


@router.post("/{item_id}/move")
async def move_to_folder(
    item_id: str,
    data: AIHistoryMoveToFolder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Move AI history item to a folder."""
    item_uuid = _parse_uuid(item_id, field_name="item_id")
    query = db.query(AIQuery).filter(
        AIQuery.id == item_uuid,
        AIQuery.user_id == current_user.id,
        AIQuery.tenant_id == current_user.tenant_id,
    ).first()
    
    if not query:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify folder exists and belongs to user
    if data.folder_id:
        folder_uuid = _parse_uuid(data.folder_id, field_name="folder_id")
        folder = db.query(AIFolder).filter(
            AIFolder.id == folder_uuid,
            AIFolder.user_id == current_user.id,
            AIFolder.tenant_id == current_user.tenant_id,
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    else:
        folder_uuid = None
    
    query.folder_id = folder_uuid
    db.commit()
    return {"success": True, "folder_id": str(folder_uuid) if folder_uuid else None}


# Folder management endpoints
