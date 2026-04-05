"""
Shared pagination utility for list endpoints.
"""
from sqlalchemy.orm import Query
from typing import TypeVar

T = TypeVar("T")


def paginate(
    query: Query,
    page: int = 1,
    page_size: int = 25,
    max_page_size: int = 100,
) -> dict:
    """
    Apply pagination to a SQLAlchemy query.
    Returns dict with items, total, page, page_size, total_pages.
    """
    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
