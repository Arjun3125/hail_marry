"""
FAISS Retrieval Quality Benchmark
=================================
Measures Information Retrieval quality of the TenantVectorStore using
standard IR metrics: MRR, Recall@K, and NDCG@10.

Uses synthetic embeddings so this benchmark has zero dependency on any
external LLM service.
"""
import json
import math
import os
import sys
import tempfile
from typing import Dict, List, Tuple

import numpy as np
import pytest

# Ensure backend imports resolve
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


def mean_reciprocal_rank(results: List[List[str]], ground_truths: List[str]) -> float:
    """Compute MRR: average of 1/rank for the first relevant result."""
    reciprocal_ranks = []
    for retrieved_ids, gt_id in zip(results, ground_truths):
        reciprocal_rank = 0.0
        for rank, doc_id in enumerate(retrieved_ids, start=1):
            if doc_id == gt_id:
                reciprocal_rank = 1.0 / rank
                break
        reciprocal_ranks.append(reciprocal_rank)
    return float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0


def recall_at_k(results: List[List[str]], ground_truths: List[str], k: int) -> float:
    """Compute Recall@K: fraction of queries where GT appears in top-K results."""
    hits = 0
    for retrieved_ids, gt_id in zip(results, ground_truths):
        if gt_id in retrieved_ids[:k]:
            hits += 1
    return hits / len(ground_truths) if ground_truths else 0.0


def ndcg_at_k(results: List[List[str]], ground_truths: List[str], k: int = 10) -> float:
    """Compute doc-level NDCG@K with binary relevance.

    Retrieval returns chunk-level results, which may include repeated hits for
    the same document. We score only the first relevant document hit so NDCG
    remains bounded in [0, 1].
    """
    ndcgs = []
    for retrieved_ids, gt_id in zip(results, ground_truths):
        dcg = 0.0
        for rank, doc_id in enumerate(retrieved_ids[:k], start=1):
            if doc_id == gt_id:
                dcg = 1.0 / math.log2(rank + 1)
                break
        idcg = 1.0 / math.log2(2)
        ndcgs.append(dcg / idcg if idcg > 0 else 0.0)
    return float(np.mean(ndcgs)) if ndcgs else 0.0


def ascii_bar(value: float, width: int = 30) -> str:
    """Render a stable ASCII progress bar for console-safe benchmark output."""
    clamped = max(0.0, min(value, 1.0))
    filled = int(clamped * width)
    return "#" * filled + "-" * (width - filled)


EMBED_DIM = 768


def generate_synthetic_corpus(
    n_documents: int = 20,
    chunks_per_doc: int = 5,
) -> Tuple[List[Dict], List[List[float]]]:
    """Generate synthetic document chunks with random unit embeddings."""
    np.random.seed(42)
    chunks = []
    embeddings = []

    for doc_idx in range(n_documents):
        doc_id = f"doc_{doc_idx:03d}"
        for chunk_idx in range(chunks_per_doc):
            chunk = {
                "document_id": doc_id,
                "text": (
                    f"Content for document {doc_idx}, chunk {chunk_idx}. "
                    f"Topic: {'science' if doc_idx % 3 == 0 else 'math' if doc_idx % 3 == 1 else 'history'}"
                ),
                "page_number": chunk_idx + 1,
                "subject_id": f"subject_{doc_idx % 5}",
            }
            chunks.append(chunk)

            vector = np.random.randn(EMBED_DIM).astype(np.float32)
            vector = vector / (np.linalg.norm(vector) + 1e-8)
            embeddings.append(vector.tolist())

    return chunks, embeddings


def generate_queries(
    chunks: List[Dict],
    embeddings: List[List[float]],
    n_queries: int = 30,
) -> Tuple[List[List[float]], List[str]]:
    """Generate synthetic queries by perturbing known chunk embeddings."""
    np.random.seed(123)
    query_embeddings = []
    ground_truth_doc_ids = []

    indices = np.random.choice(len(chunks), size=min(n_queries, len(chunks)), replace=False)

    for idx in indices:
        original = np.array(embeddings[idx], dtype=np.float32)
        noise = np.random.randn(EMBED_DIM).astype(np.float32) * 0.1
        query = original + noise
        query = query / (np.linalg.norm(query) + 1e-8)

        query_embeddings.append(query.tolist())
        ground_truth_doc_ids.append(chunks[idx]["document_id"])

    return query_embeddings, ground_truth_doc_ids


class TestRetrievalBenchmark:
    """Quantitative benchmark for FAISS vector retrieval quality."""

    @pytest.fixture(autouse=True)
    def setup_vector_store(self, tmp_path):
        """Create an isolated TenantVectorStore with synthetic data."""
        import src.infrastructure.vector_store.vector_store as vs_module

        original_dir = vs_module.VECTOR_DIR
        original_dim = vs_module.EMBED_DIM
        vs_module.VECTOR_DIR = tmp_path
        vs_module.EMBED_DIM = EMBED_DIM
        vs_module._stores.clear()

        self.chunks, self.embeddings = generate_synthetic_corpus(n_documents=20, chunks_per_doc=5)
        self.query_embeddings, self.gt_doc_ids = generate_queries(
            self.chunks,
            self.embeddings,
            n_queries=30,
        )

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

        vs_module.VECTOR_DIR = original_dir
        vs_module.EMBED_DIM = original_dim
        vs_module._stores.clear()

    def _run_retrieval(self, top_k: int = 10) -> List[List[str]]:
        """Run all queries and collect retrieved document IDs."""
        all_retrieved = []
        for query_emb in self.query_embeddings:
            results = self.store.search(query_emb, top_k=top_k)
            retrieved_doc_ids = [result[0]["document_id"] for result in results]
            all_retrieved.append(retrieved_doc_ids)
        return all_retrieved

    def test_mrr(self):
        """MRR should be > 0.3; the correct document should appear near the top."""
        retrieved = self._run_retrieval(top_k=10)
        mrr = mean_reciprocal_rank(retrieved, self.gt_doc_ids)
        print(f"\nMRR = {mrr:.4f}")
        assert mrr > 0.3, f"MRR too low: {mrr:.4f}. Retrieval quality is poor."

    def test_recall_at_1(self):
        retrieved = self._run_retrieval(top_k=1)
        recall = recall_at_k(retrieved, self.gt_doc_ids, k=1)
        print(f"\nRecall@1 = {recall:.4f}")
        assert recall > 0.2, f"Recall@1 too low: {recall:.4f}"

    def test_recall_at_3(self):
        retrieved = self._run_retrieval(top_k=3)
        recall = recall_at_k(retrieved, self.gt_doc_ids, k=3)
        print(f"\nRecall@3 = {recall:.4f}")
        assert recall > 0.3, f"Recall@3 too low: {recall:.4f}"

    def test_recall_at_5(self):
        retrieved = self._run_retrieval(top_k=5)
        recall = recall_at_k(retrieved, self.gt_doc_ids, k=5)
        print(f"\nRecall@5 = {recall:.4f}")
        assert recall > 0.4, f"Recall@5 too low: {recall:.4f}"

    def test_recall_at_10(self):
        retrieved = self._run_retrieval(top_k=10)
        recall = recall_at_k(retrieved, self.gt_doc_ids, k=10)
        print(f"\nRecall@10 = {recall:.4f}")
        assert recall > 0.5, f"Recall@10 too low: {recall:.4f}"

    def test_ndcg_at_10(self):
        retrieved = self._run_retrieval(top_k=10)
        ndcg = ndcg_at_k(retrieved, self.gt_doc_ids, k=10)
        print(f"\nNDCG@10 = {ndcg:.4f}")
        assert 0.0 <= ndcg <= 1.0
        assert ndcg > 0.2, f"NDCG@10 too low: {ndcg:.4f}"

    def test_ndcg_is_bounded_even_with_duplicate_relevant_doc_ids(self):
        results = [["doc_a", "doc_a", "doc_a"], ["doc_b", "doc_c", "doc_b"]]
        ground_truths = ["doc_a", "doc_b"]

        ndcg = ndcg_at_k(results, ground_truths, k=10)

        assert 0.0 <= ndcg <= 1.0
        assert ndcg == pytest.approx(1.0)

    def test_full_report(self, capsys):
        """Generate a complete retrieval quality report with ASCII-safe output."""
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
        print("FAISS RETRIEVAL QUALITY REPORT")
        print("=" * 60)
        for metric, value in report["metrics"].items():
            print(f"  {metric:12s} | {ascii_bar(value)} | {value:.4f}")
        print("=" * 60)

        report_path = os.path.join(tempfile.gettempdir(), "faiss_retrieval_report.json")
        with open(report_path, "w", encoding="utf-8") as file_obj:
            json.dump(report, file_obj, indent=2)
        print(f"\nFull report saved to: {report_path}")

        output = capsys.readouterr().out
        output.encode("ascii")

        assert 0.0 <= report["metrics"]["NDCG@10"] <= 1.0
        assert report["metrics"]["MRR"] > 0.0, "MRR is zero - retrieval is completely broken"
