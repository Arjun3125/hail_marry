"""Knowledge graph service — concept extraction, relationship building, graph traversal."""
from collections import deque
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.knowledge_graph import KGConcept, KGRelationship


RELATION_TYPES = {"prerequisite", "related", "part_of", "example_of", "leads_to"}


def add_concept(
    db: Session,
    tenant_id: UUID,
    name: str,
    description: Optional[str] = None,
    subject_id: Optional[UUID] = None,
    source_document_id: Optional[UUID] = None,
) -> KGConcept:
    """Add a concept to the knowledge graph."""
    existing = db.query(KGConcept).filter(
        KGConcept.tenant_id == tenant_id,
        KGConcept.name == name,
    ).first()
    if existing:
        return existing

    concept = KGConcept(
        tenant_id=tenant_id,
        name=name,
        description=description,
        subject_id=subject_id,
        source_document_id=source_document_id,
    )
    db.add(concept)
    db.commit()
    db.refresh(concept)
    return concept


def add_relationship(
    db: Session,
    tenant_id: UUID,
    source_name: str,
    target_name: str,
    relation_type: str,
    weight: float = 1.0,
) -> Optional[KGRelationship]:
    """Add a relationship between two concepts."""
    if relation_type not in RELATION_TYPES:
        raise ValueError(f"Invalid relation type: {relation_type}. Supported: {RELATION_TYPES}")

    source = db.query(KGConcept).filter(
        KGConcept.tenant_id == tenant_id, KGConcept.name == source_name
    ).first()
    target = db.query(KGConcept).filter(
        KGConcept.tenant_id == tenant_id, KGConcept.name == target_name
    ).first()

    if not source or not target:
        return None

    # Avoid duplicates
    existing = db.query(KGRelationship).filter(
        KGRelationship.source_concept_id == source.id,
        KGRelationship.target_concept_id == target.id,
        KGRelationship.relation_type == relation_type,
    ).first()
    if existing:
        return existing

    rel = KGRelationship(
        tenant_id=tenant_id,
        source_concept_id=source.id,
        target_concept_id=target.id,
        relation_type=relation_type,
        weight=weight,
    )
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def traverse_graph(
    db: Session,
    tenant_id: UUID,
    concept_name: str,
    depth: int = 2,
) -> list[dict]:
    """BFS traversal from a concept to find related concepts within depth."""
    start = db.query(KGConcept).filter(
        KGConcept.tenant_id == tenant_id, KGConcept.name == concept_name
    ).first()
    if not start:
        return []

    visited = {start.id}
    queue = deque([(start, 0)])
    results = []

    while queue:
        current, d = queue.popleft()
        if d > 0:
            results.append({
                "concept": current.name,
                "description": current.description,
                "depth": d,
            })
        if d >= depth:
            continue

        # Get outgoing relationships
        rels = db.query(KGRelationship).filter(
            KGRelationship.source_concept_id == current.id,
            KGRelationship.tenant_id == tenant_id,
        ).all()

        for rel in rels:
            if rel.target_concept_id not in visited:
                visited.add(rel.target_concept_id)
                target = db.query(KGConcept).filter(KGConcept.id == rel.target_concept_id).first()
                if target:
                    queue.append((target, d + 1))

    return results


def get_concept_context(db: Session, tenant_id: UUID, query: str, max_concepts: int = 5) -> list[dict]:
    """Find concepts relevant to a query using simple keyword matching.

    In production, this would use embedding similarity.
    For now, uses SQL LIKE matching against concept names and descriptions.
    """
    keywords = query.lower().split()
    concepts = set()

    for kw in keywords:
        if len(kw) < 3:
            continue
        matches = db.query(KGConcept).filter(
            KGConcept.tenant_id == tenant_id,
            KGConcept.name.ilike(f"%{kw}%"),
        ).limit(max_concepts).all()
        for c in matches:
            concepts.add(c)

    results = []
    for c in list(concepts)[:max_concepts]:
        related = traverse_graph(db, tenant_id, c.name, depth=1)
        results.append({
            "concept": c.name,
            "description": c.description,
            "related": related,
        })

    return results
