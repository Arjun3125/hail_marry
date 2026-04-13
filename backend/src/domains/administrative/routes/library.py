"""Library API routes — catalog, lending, returns, stats."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID

from auth.dependencies import require_role
from src.domains.administrative.models.library import Book
from src.domains.administrative.models.library import BookLending
from database import get_db
from src.domains.administrative.services.library import (
    add_book, get_library_stats, get_overdue_books, issue_book,
    return_book, search_catalog,
)

router = APIRouter(prefix="/api/library", tags=["Library"])


class AddBookRequest(BaseModel):
    title: str
    author: str = ""
    isbn: str = ""
    category: str = "general"
    total_copies: int = 1
    shelf_location: str = ""


class IssueBookRequest(BaseModel):
    book_id: str
    borrower_id: str
    lending_days: int = 14


@router.post("/books")
def create_book(body: AddBookRequest, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    book: Book = add_book(db, user.tenant_id, body.title, body.author, body.isbn,
                    body.category, body.total_copies, body.shelf_location)
    return {"id": str(book.id), "title": book.title}


@router.get("/books")
def list_books(q: str = Query(""), category: str = Query(""), limit: int = Query(50),
               user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    books: list[Book] = search_catalog(db, user.tenant_id, q, category, limit)
    return {"books": [{"id": str(b.id), "title": b.title, "author": b.author,
                        "available": b.available_copies, "total": b.total_copies} for b in books]}


@router.post("/issue")
def issue(body: IssueBookRequest, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    try:
        lending: BookLending = issue_book(db, user.tenant_id, UUID(body.book_id), UUID(body.borrower_id), body.lending_days)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"lending_id": str(lending.id), "due_date": lending.due_date.isoformat()}


@router.post("/return/{lending_id}")
def return_lending(lending_id: str, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    try:
        lending: BookLending = return_book(db, UUID(lending_id))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"status": lending.status, "fine": lending.fine_amount}


@router.get("/overdue")
def overdue(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    items: list[BookLending] = get_overdue_books(db, user.tenant_id)
    return {"overdue": [{"lending_id": str(i.id), "book_id": str(i.book_id),
                          "due_date": i.due_date.isoformat()} for i in items]}


@router.get("/stats")
def stats(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    return {"stats": get_library_stats(db, user.tenant_id)}
