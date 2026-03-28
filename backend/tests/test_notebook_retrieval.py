import asyncio
from uuid import uuid4


def test_retrieve_context_passes_notebook_id_to_vector_store(monkeypatch):
    from src.infrastructure.vector_store import retrieval

    class FakeEmbeddingProvider:
        async def embed(self, query: str):
            assert query == "mitosis"
            return [0.1, 0.2]

    class FakeStore:
        chunk_count = 1

        def __init__(self):
            self.calls = []

        def search(self, *, query_embedding, top_k=8, subject_id=None, notebook_id=None):
            self.calls.append(
                {
                    "query_embedding": query_embedding,
                    "top_k": top_k,
                    "subject_id": subject_id,
                    "notebook_id": notebook_id,
                }
            )
            return [
                (
                    {
                        "text": "Mitosis has four main phases.",
                        "source_file": "biology-notes.pdf",
                        "page_number": 3,
                        "section_title": "Cell Division",
                        "document_id": "doc-1",
                        "notebook_id": notebook_id,
                    },
                    0.92,
                )
            ]

    fake_store = FakeStore()

    monkeypatch.setattr(retrieval, "get_embedding_provider", lambda: FakeEmbeddingProvider())
    monkeypatch.setattr(retrieval, "get_vector_store_provider", lambda tenant_id: fake_store)
    monkeypatch.setattr(retrieval, "rerank_chunks", lambda query, results, top_n=5: results[:top_n])
    monkeypatch.setattr(retrieval, "deduplicate_chunks", lambda chunks, similarity_threshold=0.85: chunks)

    chunks = asyncio.run(
        retrieval.retrieve_context(
            query="mitosis",
            tenant_id="tenant-1",
            top_k=4,
            subject_id="science",
            notebook_id="notebook-123",
        )
    )

    assert fake_store.calls == [
        {
            "query_embedding": [0.1, 0.2],
            "top_k": 8,
            "subject_id": "science",
            "notebook_id": "notebook-123",
        }
    ]
    assert len(chunks) == 1
    assert chunks[0]["document_id"] == "doc-1"
    assert chunks[0]["citation"] == "[biology-notes.pdf_p3]"


def test_faiss_provider_filters_results_by_notebook_id(monkeypatch):
    from src.infrastructure.vector_store import vector_store

    monkeypatch.setattr(vector_store, "faiss", None)

    provider = vector_store.FAISSProvider(str(uuid4()))
    provider.metadata = [
        {
            "document_id": "doc-a",
            "text": "Notebook A content",
            "notebook_id": "notebook-a",
            "_vector": [1.0, 0.0],
        },
        {
            "document_id": "doc-b",
            "text": "Notebook B content",
            "notebook_id": "notebook-b",
            "_vector": [0.9, 0.1],
        },
    ]

    results = provider.search(query_embedding=[1.0, 0.0], top_k=5, notebook_id="notebook-a")

    assert len(results) == 1
    assert results[0][0]["document_id"] == "doc-a"
