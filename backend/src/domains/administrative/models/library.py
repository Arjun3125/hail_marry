"""Library management models — book catalog, lending, returns."""
import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class Book(Base):
    __tablename__ = "library_books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(255), nullable=True)
    isbn = Column(String(20), nullable=True, index=True)
    category = Column(String(100), nullable=True)  # textbook, reference, fiction, etc.
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    shelf_location = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BookLending(Base):
    __tablename__ = "library_lendings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    book_id = Column(UUID(as_uuid=True), ForeignKey("library_books.id"), nullable=False, index=True)
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="issued")  # issued, returned, overdue, lost
    fine_amount = Column(Float, default=0.0)
