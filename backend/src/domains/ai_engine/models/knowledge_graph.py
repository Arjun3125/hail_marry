"""Knowledge graph models — concepts and relationships for concept-based retrieval."""
import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class KGConcept(Base):
    __tablename__ = "kg_concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    source_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KGRelationship(Base):
    __tablename__ = "kg_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    source_concept_id = Column(UUID(as_uuid=True), ForeignKey("kg_concepts.id"), nullable=False, index=True)
    target_concept_id = Column(UUID(as_uuid=True), ForeignKey("kg_concepts.id"), nullable=False, index=True)
    relation_type = Column(String(50), nullable=False)  # prerequisite, related, part_of, example_of
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
