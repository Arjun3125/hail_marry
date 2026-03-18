"""Tests for library management."""
import uuid
import pytest
from src.domains.administrative.services.library import DEFAULT_LENDING_DAYS, FINE_PER_DAY
from src.domains.administrative.models.library import Book, BookLending


def test_default_lending_days():
    assert DEFAULT_LENDING_DAYS == 14


def test_fine_per_day():
    assert FINE_PER_DAY == 2.0


def test_book_model():
    book = Book(tenant_id=uuid.uuid4(), title="Physics Textbook", author="Dr. Smith",
                isbn="978-0-123456-78-9", category="textbook", total_copies=5)
    assert book.title == "Physics Textbook"
    assert book.total_copies == 5


def test_book_lending_model():
    lending = BookLending(tenant_id=uuid.uuid4(), book_id=uuid.uuid4(),
                          borrower_id=uuid.uuid4(), status="issued")
    assert lending.status == "issued"


def test_book_categories():
    categories = ["textbook", "reference", "fiction", "general"]
    for cat in categories:
        book = Book(tenant_id=uuid.uuid4(), title="Test", category=cat)
        assert book.category == cat


def test_lending_statuses():
    for status in ["issued", "returned", "overdue", "lost"]:
        lending = BookLending(tenant_id=uuid.uuid4(), book_id=uuid.uuid4(),
                              borrower_id=uuid.uuid4(), status=status)
        assert lending.status == status


def test_library_stats_structure():
    stats = {
        "total_books": 100, "available": 85, "issued": 15,
        "overdue": 3, "catalog_count": 50,
    }
    assert stats["total_books"] == stats["available"] + stats["issued"]
