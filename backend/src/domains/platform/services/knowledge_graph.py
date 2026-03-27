"""Knowledge graph service — concept extraction, relationship building, graph traversal."""
from collections import deque
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
import numpy as np

from src.domains.platform.models.knowledge_graph import KGConcept, KGRelationship
from src.infrastructure.llm.providers import get_embedding_provider


RELATION_TYPES = {"prerequisite", "related", "part_of", "example_of", "leads_to"}

# In-memory cache to avoid repeated embedding calls for concepts
_concept_embeddings: dict[str, list[float]] = {}


def add_concept(
    db: Session,
    tenant_id: UUID,
    name: str,
    description: Optional[str] = None,
    subject_id: Optional[UUID] = None,
    source_document_id: Optional[UUID] = None,
    notebook_id: Optional[UUID] = None,
) -> KGConcept:
    """Add a concept to the knowledge graph."""
    query = db.query(KGConcept).filter(
        KGConcept.tenant_id == tenant_id,
        KGConcept.name == name,
    )
    if notebook_id:
        query = query.filter(KGConcept.notebook_id == notebook_id)
    else:
        query = query.filter(KGConcept.notebook_id.is_(None))
    
    existing = query.first()
    if existing:
        return existing

    concept = KGConcept(
        tenant_id=tenant_id,
        name=name,
        description=description,
        subject_id=subject_id,
        source_document_id=source_document_id,
        notebook_id=notebook_id,
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
    """BFS traversal using PostgreSQL Recursive CTE to find related concepts."""
    # Base concept
    start = db.query(KGConcept).filter(
        KGConcept.tenant_id == tenant_id, KGConcept.name == concept_name
    ).first()
    if not start:
        return []

    from sqlalchemy import text
    
    # Recursive CTE to traverse graph purely in SQL
    query = text(f"""
        WITH RECURSIVE concept_tree AS (
            -- Base case: The starting concept
            SELECT 
                target_concept_id as id, 
                1 as depth
            FROM kg_relationships
            WHERE source_concept_id = :start_id AND tenant_id = :tenant_id
            
            UNION
            
            -- Recursive step: Join to find next level
            SELECT 
                r.target_concept_id as id, 
                ct.depth + 1 as depth
            FROM kg_relationships r
            INNER JOIN concept_tree ct ON ct.id = r.source_concept_id
            WHERE r.tenant_id = :tenant_id AND ct.depth < :max_depth
        )
        SELECT 
            c.name as concept, 
            c.description, 
            ct.depth
        FROM concept_tree ct
        JOIN kg_concepts c ON c.id = ct.id
        WHERE c.tenant_id = :tenant_id
        GROUP BY c.name, c.description, ct.depth
        ORDER BY ct.depth ASC;
    """)
    
    result = db.execute(query, {
        "start_id": start.id, 
        "tenant_id": tenant_id, 
        "max_depth": depth
    }).fetchall()
    
    return [
        {
            "concept": row.concept,
            "description": row.description,
            "depth": row.depth
        }
        for row in result
    ]


async def get_concept_context(
    db: Session, 
    tenant_id: UUID, 
    query: str, 
    max_concepts: int = 5,
    notebook_id: Optional[UUID] = None,
) -> list[dict]:
    """Find concepts relevant to a query using semantic similarity matching (embeddings).
    
    Args:
        db: Database session
        tenant_id: Tenant ID for filtering
        query: Search query
        max_concepts: Maximum number of concepts to return
        notebook_id: Optional notebook ID to scope concepts to a specific notebook
    """
    # Build base query
    concept_query = db.query(KGConcept).filter(KGConcept.tenant_id == tenant_id)
    
    # Filter by notebook if provided - include both notebook-specific and global concepts
    if notebook_id:
        concept_query = concept_query.filter(
            sa.or_(
                KGConcept.notebook_id == notebook_id,
                KGConcept.notebook_id.is_(None)
            )
        )
    else:
        # Only global concepts (not associated with any notebook)
        concept_query = concept_query.filter(KGConcept.notebook_id.is_(None))
    
    concepts = concept_query.all()
    if not concepts:
        return []

    provider = get_embedding_provider()
    query_emb = await provider.embed(query)

    texts_to_embed = []
    concepts_to_embed = []

    for c in concepts:
        cid = str(c.id)
        if cid not in _concept_embeddings:
            texts_to_embed.append(f"{c.name}: {c.description or ''}")
            concepts_to_embed.append(c)

    if texts_to_embed:
        # Prevent huge batches if there are thousands of concepts, but normally fine for pilot
        batch_size = 100
        for i in range(0, len(texts_to_embed), batch_size):
            batch_texts = texts_to_embed[i:i + batch_size]
            batch_concepts = concepts_to_embed[i:i + batch_size]
            embs = await provider.embed_batch(batch_texts)
            for c, emb in zip(batch_concepts, embs):
                _concept_embeddings[str(c.id)] = emb

    # Cosine similarity calculation
    q_vec = np.array(query_emb, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []
    q_vec = q_vec / q_norm

    scores = []
    for c in concepts:
        c_vec = np.array(_concept_embeddings[str(c.id)], dtype=np.float32)
        c_norm = np.linalg.norm(c_vec)
        if c_norm > 0:
            c_vec = c_vec / c_norm
            score = float(np.dot(q_vec, c_vec))
            scores.append((score, c))

    # Sort descending
    scores.sort(key=lambda x: x[0], reverse=True)

    results = []
    # Arbitrary threshold to ensure semantic relevance
    threshold = 0.6
    for score, c in scores[:max_concepts]:
        if score >= threshold:
            related = traverse_graph(db, tenant_id, c.name, depth=1)
            results.append({
                "concept": c.name,
                "description": c.description,
                "related": related,
            })

    return results
