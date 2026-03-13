"""Library management service — catalog, lending, returns, overdue tracking."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.library import Book, BookLending


# Default lending period
DEFAULT_LENDING_DAYS = 14
FINE_PER_DAY = 2.0  # INR per day overdue


def add_book(
    db: Session, tenant_id: UUID, title: str, author: str = "",
    isbn: str = "", category: str = "general", total_copies: int = 1,
    shelf_location: str = "",
) -> Book:
    """Add a book to the library catalog."""
    book = Book(
        tenant_id=tenant_id, title=title, author=author, isbn=isbn,
        category=category, total_copies=total_copies,
        available_copies=total_copies, shelf_location=shelf_location,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def search_catalog(
    db: Session, tenant_id: UUID, query: str = "", category: str = "",
    limit: int = 50,
) -> list[Book]:
    """Search book catalog by title, author, or ISBN."""
    q = db.query(Book).filter(Book.tenant_id == tenant_id)
    if query:
        q = q.filter(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%")) |
            (Book.isbn.ilike(f"%{query}%"))
        )
    if category:
        q = q.filter(Book.category == category)
    return q.order_by(Book.title).limit(limit).all()


def issue_book(
    db: Session, tenant_id: UUID, book_id: UUID, borrower_id: UUID,
    lending_days: int = DEFAULT_LENDING_DAYS,
) -> BookLending:
    """Issue a book to a borrower."""
    book = db.query(Book).filter(Book.id == book_id, Book.tenant_id == tenant_id).first()
    if not book:
        raise ValueError("Book not found")
    if book.available_copies <= 0:
        raise ValueError("No copies available")

    due = datetime.now(timezone.utc) + timedelta(days=lending_days)
    lending = BookLending(
        tenant_id=tenant_id, book_id=book_id, borrower_id=borrower_id,
        due_date=due, status="issued",
    )
    db.add(lending)
    book.available_copies -= 1
    db.commit()
    db.refresh(lending)
    return lending


def return_book(db: Session, lending_id: UUID) -> BookLending:
    """Process a book return, calculating any fines."""
    lending = db.query(BookLending).filter(BookLending.id == lending_id).first()
    if not lending:
        raise ValueError("Lending record not found")

    lending.returned_at = datetime.now(timezone.utc)
    lending.status = "returned"

    # Calculate overdue fine
    if lending.returned_at > lending.due_date:
        overdue_days = (lending.returned_at - lending.due_date).days
        lending.fine_amount = overdue_days * FINE_PER_DAY

    # Restore available copies
    book = db.query(Book).filter(Book.id == lending.book_id).first()
    if book:
        book.available_copies += 1

    db.commit()
    db.refresh(lending)
    return lending


def get_overdue_books(db: Session, tenant_id: UUID) -> list[BookLending]:
    """Get all overdue book lendings."""
    now = datetime.now(timezone.utc)
    return (
        db.query(BookLending)
        .filter(
            BookLending.tenant_id == tenant_id,
            BookLending.status == "issued",
            BookLending.due_date < now,
        )
        .all()
    )


def get_library_stats(db: Session, tenant_id: UUID) -> dict:
    """Get library statistics."""
    from sqlalchemy import func as sqlfunc

    total_books = db.query(sqlfunc.sum(Book.total_copies)).filter(Book.tenant_id == tenant_id).scalar() or 0
    available = db.query(sqlfunc.sum(Book.available_copies)).filter(Book.tenant_id == tenant_id).scalar() or 0
    active_lendings = db.query(BookLending).filter(
        BookLending.tenant_id == tenant_id, BookLending.status == "issued"
    ).count()
    overdue = len(get_overdue_books(db, tenant_id))

    return {
        "total_books": total_books,
        "available": available,
        "issued": active_lendings,
        "overdue": overdue,
        "catalog_count": db.query(Book).filter(Book.tenant_id == tenant_id).count(),
    }
