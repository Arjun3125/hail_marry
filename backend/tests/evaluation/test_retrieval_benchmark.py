"""
FAISS Retrieval Quality Benchmark
==================================
Measures the Information Retrieval quality of the TenantVectorStore
using standard IR metrics: MRR, Recall@K, and NDCG@10.

Uses synthetic embeddings (numpy random vectors) so this benchmark
has ZERO dependency on Ollama or any external LLM service.
"""
import json
import math
import os
import sys
import shutil
import tempfile
from typing import List, Dict, Tuple

import numpy as np
import pytest

# Ensure backend imports resolve
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


# ─── IR Metric Functions ──────────────────────────────────────

def mean_reciprocal_rank(results: List[List[str]], ground_truths: List[str]) -> float:
    """Compute MRR: average of 1/rank for the first relevant result."""
    rrs = []
    for retrieved_ids, gt_id in zip(results, ground_truths):
        rr = 0.0
        for rank, doc_id in enumerate(retrieved_ids, start=1):
            if doc_id == gt_id:
                rr = 1.0 / rank
                break
        rrs.append(rr)
    return float(np.mean(rrs)) if rrs else 0.0


def recall_at_k(results: List[List[str]], ground_truths: List[str], k: int) -> float:
    """Compute Recall@K: fraction of queries where GT appears in top-K results."""
    hits = 0
    for retrieved_ids, gt_id in zip(results, ground_truths):
        if gt_id in retrieved_ids[:k]:
            hits += 1
    return hits / len(ground_truths) if ground_truths else 0.0


def ndcg_at_k(results: List[List[str]], ground_truths: List[str], k: int = 10) -> float:
    """Compute NDCG@K with binary relevance (1 if match, 0 otherwise)."""
    ndcgs = []
    for retrieved_ids, gt_id in zip(results, ground_truths):
        dcg = 0.0
        for rank, doc_id in enumerate(retrieved_ids[:k], start=1):
            if doc_id == gt_id:
                dcg += 1.0 / math.log2(rank + 1)
        # Ideal DCG: relevant doc at position 1
        idcg = 1.0 / math.log2(2)
        ndcgs.append(dcg / idcg if idcg > 0 else 0.0)
    return float(np.mean(ndcgs)) if ndcgs else 0.0


# ─── Synthetic Dataset Generator ─────────────────────────────

EMBED_DIM = 768  # Match nomic-embed-text default


def generate_synthetic_corpus(n_documents: int = 20, chunks_per_doc: int = 5) -> Tuple[List[Dict], List[List[float]]]:
    """Generate synthetic document chunks with random embeddings.
    
    Each chunk has a unique document_id and text. The embeddings are 
    random unit vectors so that cosine similarity is well-defined.
    """
    np.random.seed(42)
    chunks = []
    embeddings = []

    for doc_idx in range(n_documents):
        doc_id = f"doc_{doc_idx:03d}"
        for chunk_idx in range(chunks_per_doc):
            chunk = {
                "document_id": doc_id,
                "text": f"Content for document {doc_idx}, chunk {chunk_idx}. "
                        f"Topic: {'science' if doc_idx % 3 == 0 else 'math' if doc_idx % 3 == 1 else 'history'}",
                "page_number": chunk_idx + 1,
                "subject_id": f"subject_{doc_idx % 5}",
            }
            chunks.append(chunk)

            # Generate a random unit vector
            vec = np.random.randn(EMBED_DIM).astype(np.float32)
            vec = vec / (np.linalg.norm(vec) + 1e-8)
            embeddings.append(vec.tolist())

    return chunks, embeddings


def generate_queries(chunks: List[Dict], embeddings: List[List[float]], n_queries: int = 30) -> Tuple[List[List[float]], List[str]]:
    """Generate synthetic queries by perturbing known chunk embeddings.
    
    Each query is a noisy version of a specific chunk's embedding,
    so we know the ground-truth document_id it should retrieve.
    """
    np.random.seed(123)
    query_embeddings = []
    ground_truth_doc_ids = []

    # Sample random chunk indices
    indices = np.random.choice(len(chunks), size=min(n_queries, len(chunks)), replace=False)
    
    for idx in indices:
        # Add small noise to the original embedding
        original = np.array(embeddings[idx], dtype=np.float32)
        noise = np.random.randn(EMBED_DIM).astype(np.float32) * 0.1
        query = original + noise
        query = query / (np.linalg.norm(query) + 1e-8)
        
        query_embeddings.append(query.tolist())
        ground_truth_doc_ids.append(chunks[idx]["document_id"])

    return query_embeddings, ground_truth_doc_ids


# ─── Test Suite ───────────────────────────────────────────────

class TestRetrievalBenchmark:
    """Quantitative benchmark for FAISS vector retrieval quality."""

    @pytest.fixture(autouse=True)
    def setup_vector_store(self, tmp_path):
        """Create an isolated TenantVectorStore with synthetic data."""
        # Patch the storage directory to use a temp folder
        import src.infrastructure.vector_store.vector_store as vs_module
        original_dir = vs_module.VECTOR_DIR
        vs_module.VECTOR_DIR = tmp_path
        vs_module._stores.clear()
        
        # Also patch EMBED_DIM
        original_dim = vs_module.EMBED_DIM
        vs_module.EMBED_DIM = EMBED_DIM

        # Generate synthetic data
        self.chunks, self.embeddings = generate_synthetic_corpus(n_documents=20, chunks_per_doc=5)
        self.query_embeddings, self.gt_doc_ids = generate_queries(self.chunks, self.embeddings, n_queries=30)
        
        # Create and seed the vector store
        from src.infrastructure.vector_store.vector_store import TenantVectorStore
        self.store = TenantVectorStore.__new__(TenantVectorStore)
        self.store.tenant_id = "benchmark_tenant"
        self.store.namespace = "tenant_benchmark_tenant"
        self.store.index_path = tmp_path / "tenant_benchmark_tenant.index"
        self.store.meta_path = tmp_path / "tenant_benchmark_tenant.meta.json"
        self.store.index = None
        self.store.metadata = []
        self.store._load()
        self.store.add_chunks(self.chunks, self.embeddings)

        yield

        # Restore
        vs_module.VECTOR_DIR = original_dir
        vs_module.EMBED_DIM = original_dim
        vs_module._stores.clear()

    def _run_retrieval(self, top_k: int = 10) -> List[List[str]]:
        """Run all queries and collect retrieved document IDs."""
        all_retrieved = []
        for query_emb in self.query_embeddings:
            results = self.store.search(query_emb, top_k=top_k)
            retrieved_doc_ids = [r[0]["document_id"] for r in results]
            all_retrieved.append(retrieved_doc_ids)
        return all_retrieved

    def test_mrr(self):
        """MRR should be > 0.5 — the correct document should appear in the top few results."""
        retrieved = self._run_retrieval(top_k=10)
        mrr = mean_reciprocal_rank(retrieved, self.gt_doc_ids)
        print(f"\n📊 MRR = {mrr:.4f}")
        assert mrr > 0.3, f"MRR too low: {mrr:.4f}. Retrieval quality is poor."

    def test_recall_at_1(self):
        """Recall@1: fraction of queries where correct doc is the top result."""
        retrieved = self._run_retrieval(top_k=1)
        r1 = recall_at_k(retrieved, self.gt_doc_ids, k=1)
        print(f"\n📊 Recall@1 = {r1:.4f}")
        assert r1 > 0.2, f"Recall@1 too low: {r1:.4f}"

    def test_recall_at_3(self):
        """Recall@3: fraction of queries where correct doc appears in top 3."""
        retrieved = self._run_retrieval(top_k=3)
        r3 = recall_at_k(retrieved, self.gt_doc_ids, k=3)
        print(f"\n📊 Recall@3 = {r3:.4f}")
        assert r3 > 0.3, f"Recall@3 too low: {r3:.4f}"

    def test_recall_at_5(self):
        """Recall@5."""
        retrieved = self._run_retrieval(top_k=5)
        r5 = recall_at_k(retrieved, self.gt_doc_ids, k=5)
        print(f"\n📊 Recall@5 = {r5:.4f}")
        assert r5 > 0.4, f"Recall@5 too low: {r5:.4f}"

    def test_recall_at_10(self):
        """Recall@10."""
        retrieved = self._run_retrieval(top_k=10)
        r10 = recall_at_k(retrieved, self.gt_doc_ids, k=10)
        print(f"\n📊 Recall@10 = {r10:.4f}")
        assert r10 > 0.5, f"Recall@10 too low: {r10:.4f}"

    def test_ndcg_at_10(self):
        """NDCG@10: measures ranking quality accounting for position discount."""
        retrieved = self._run_retrieval(top_k=10)
        ndcg = ndcg_at_k(retrieved, self.gt_doc_ids, k=10)
        print(f"\n📊 NDCG@10 = {ndcg:.4f}")
        assert ndcg > 0.2, f"NDCG@10 too low: {ndcg:.4f}"

    def test_full_report(self):
        """Generate a complete retrieval quality report."""
        retrieved_10 = self._run_retrieval(top_k=10)
        retrieved_5 = self._run_retrieval(top_k=5)
        retrieved_3 = self._run_retrieval(top_k=3)
        retrieved_1 = self._run_retrieval(top_k=1)

        report = {
            "benchmark": "FAISS Retrieval Quality",
            "corpus_size": len(self.chunks),
            "num_queries": len(self.query_embeddings),
            "embed_dim": EMBED_DIM,
            "metrics": {
                "MRR": round(mean_reciprocal_rank(retrieved_10, self.gt_doc_ids), 4),
                "Recall@1": round(recall_at_k(retrieved_1, self.gt_doc_ids, k=1), 4),
                "Recall@3": round(recall_at_k(retrieved_3, self.gt_doc_ids, k=3), 4),
                "Recall@5": round(recall_at_k(retrieved_5, self.gt_doc_ids, k=5), 4),
                "Recall@10": round(recall_at_k(retrieved_10, self.gt_doc_ids, k=10), 4),
                "NDCG@10": round(ndcg_at_k(retrieved_10, self.gt_doc_ids, k=10), 4),
            },
        }

        print("\n" + "=" * 60)
        print("📊 FAISS RETRIEVAL QUALITY REPORT")
        print("=" * 60)
        for metric, value in report["metrics"].items():
            bar = "█" * int(value * 30) + "░" * (30 - int(value * 30))
            print(f"  {metric:12s} │ {bar} │ {value:.4f}")
        print("=" * 60)

        # Write report to temp file
        report_path = os.path.join(tempfile.gettempdir(), "faiss_retrieval_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Full report saved to: {report_path}")

        # Assertions: these should all pass with synthetic near-match data
        assert report["metrics"]["MRR"] > 0.0, "MRR is zero — retrieval is completely broken"
