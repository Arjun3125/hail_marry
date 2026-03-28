"""Pydantic schemas for AI history feature."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class AIHistoryItem(BaseModel):
    """Single AI query item in history."""
    id: str
    mode: str
    query_text: str
    response_text: str
    title: Optional[str] = None
    created_at: datetime
    token_usage: Optional[int] = None
    citation_count: int = 0
    is_pinned: bool = False
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    trace_id: Optional[str] = None
    notebook_id: Optional[str] = None
    notebook_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AIHistoryFilter(BaseModel):
    """Filters for AI history queries."""
    mode: Optional[str] = None
    folder_id: Optional[str] = None
    notebook_id: Optional[str] = None
    search_query: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    is_pinned: Optional[bool] = None


class AIHistoryListResponse(BaseModel):
    """Paginated AI history response."""
    items: List[AIHistoryItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class AIFolderCreate(BaseModel):
    """Create a new AI folder."""
    name: str
    color: str = "blue"


class AIFolderUpdate(BaseModel):
    """Update an existing AI folder."""
    name: Optional[str] = None
    color: Optional[str] = None


class AIFolderResponse(BaseModel):
    """AI folder response."""
    id: str
    name: str
    color: str
    created_at: datetime
    item_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AIFolderListResponse(BaseModel):
    """List of AI folders."""
    folders: List[AIFolderResponse]


class AIHistoryUpdateTitle(BaseModel):
    """Update title of AI history item."""
    title: str


class AIHistoryMoveToFolder(BaseModel):
    """Move AI history item to folder."""
    folder_id: Optional[str] = None


class AIHistoryStats(BaseModel):
    """AI usage statistics."""
    total_queries: int
    queries_by_mode: dict
    queries_this_week: int
    queries_this_month: int
    favorite_mode: Optional[str] = None
    streak_days: int = 0


class AIHistorySearchResult(BaseModel):
    """Search result with highlight."""
    item: AIHistoryItem
    highlight: Optional[str] = None  # Snippet with matching text highlighted
    relevance_score: float = 0.0


class AIHistorySearchResponse(BaseModel):
    """Search response."""
    results: List[AIHistorySearchResult]
    total: int
    query: str


class AIHistoryExportRequest(BaseModel):
    """Export AI history items."""
    item_ids: List[str]
    format: str = "markdown"  # markdown, pdf, json, anki


class AIHistoryRegenerateRequest(BaseModel):
    """Regenerate from history item."""
    use_original_settings: bool = True
    new_settings: Optional[dict] = None  # Override settings if not using original
