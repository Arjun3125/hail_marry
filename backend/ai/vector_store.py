"""
FAISS Vector Store — tenant-namespaced vector storage and retrieval.
Stores document chunks as vectors for semantic search.
"""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from config import settings

try:
    import faiss
except ImportError:
    faiss = None

VECTOR_DIR = Path(settings.storage.vector_store_dir).resolve()
VECTOR_DIR.mkdir(parents=True, exist_ok=True)
EMBED_DIM = settings.embedding.embed_dim


@dataclass
class StoredChunk:
    """Chunk stored in vector DB with its metadata."""
    chunk_id: int
    document_id: str
    text: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    subject_id: Optional[str] = None
    source_file: Optional[str] = None


class TenantVectorStore:
    """Tenant-isolated FAISS vector store."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.namespace = f"tenant_{tenant_id}"
        self.index_path = VECTOR_DIR / f"{self.namespace}.index"
        self.meta_path = VECTOR_DIR / f"{self.namespace}.meta.json"
        self.index: Optional[object] = None
        self.metadata: List[Dict] = []
        self._load()

    def _load(self):
        """Load existing index and metadata from disk."""
        if faiss is None:
            # Fallback: use numpy-based search
            self.index = None
            if self.meta_path.exists():
                with open(self.meta_path, "r") as f:
                    self.metadata = json.load(f)
            return

        if self.index_path.exists() and self.meta_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.meta_path, "r") as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(EMBED_DIM)  # Inner product (cosine on normalized vecs)
            self.metadata = []

    def _save(self):
        """Persist index and metadata to disk."""
        if faiss is not None and self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w") as f:
            json.dump(self.metadata, f)

    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Add chunks with their embeddings to the store.
        chunks: list of dicts with text, document_id, page_number, etc.
        embeddings: corresponding embedding vectors.
        """
        if not chunks or not embeddings:
            return

        vectors = np.array(embeddings, dtype=np.float32)
        # Normalize for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / (norms + 1e-8)

        if faiss is not None and self.index is not None:
            self.index.add(vectors)
        else:
            # Numpy fallback: store vectors in metadata
            for i, chunk in enumerate(chunks):
                chunk["_vector"] = embeddings[i]

        self.metadata.extend(chunks)
        self._save()

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 8,
        subject_id: Optional[str] = None,
    ) -> List[Tuple[Dict, float]]:
        """
        Search for most similar chunks.
        Returns list of (chunk_metadata, similarity_score).
        """
        if not self.metadata:
            return []

        query_vec = np.array([query_embedding], dtype=np.float32)
        query_vec = query_vec / (np.linalg.norm(query_vec) + 1e-8)

        if faiss is not None and self.index is not None and self.index.ntotal > 0:
            # Search more than top_k to allow post-filtering
            search_k = min(top_k * 3, self.index.ntotal)
            scores, indices = self.index.search(query_vec, search_k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                meta = self.metadata[idx]

                # Subject filter
                if subject_id and meta.get("subject_id") and meta["subject_id"] != subject_id:
                    continue

                results.append((meta, float(score)))
                if len(results) >= top_k:
                    break
            return results
        else:
            # Numpy fallback
            results = []
            for meta in self.metadata:
                if "_vector" in meta:
                    vec = np.array(meta["_vector"], dtype=np.float32)
                    vec = vec / (np.linalg.norm(vec) + 1e-8)
                    score = float(np.dot(query_vec[0], vec))

                    if subject_id and meta.get("subject_id") and meta["subject_id"] != subject_id:
                        continue

                    results.append((meta, score))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

    def delete_document(self, document_id: str):
        """Remove all chunks for a document. Requires full re-index."""
        self.metadata = [m for m in self.metadata if m.get("document_id") != document_id]
        # Re-index would be needed for FAISS — for pilot, just save metadata
        self._save()

    @property
    def chunk_count(self) -> int:
        return len(self.metadata)


# Global cache of tenant stores
_stores: Dict[str, TenantVectorStore] = {}


def get_vector_store(tenant_id: str) -> TenantVectorStore:
    """Get or create a tenant vector store."""
    if tenant_id not in _stores:
        _stores[tenant_id] = TenantVectorStore(tenant_id)
    return _stores[tenant_id]
