import asyncio
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock


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


def test_execute_study_tool_passes_notebook_id_to_query(monkeypatch):
    from src.shared.ai_tools import study_tools

    notebook_id = uuid4()
    ai_mock = AsyncMock(
        return_value={
            "answer": '[{"question":"Q1","options":["A. One","B. Two"],"correct":"A","citation":"[biology_p1]"}]',
            "mode": "quiz",
            "citations": [],
            "token_usage": 1,
            "citation_valid": True,
        }
    )
    monkeypatch.setattr(study_tools, "execute_text_query", ai_mock)

    payload = asyncio.run(
        study_tools.execute_study_tool(
            study_tools.InternalStudyToolGenerateRequest(
                tool="quiz",
                topic="Chapter 10.1",
                subject_id="biology",
                notebook_id=notebook_id,
                tenant_id=str(uuid4()),
            )
        )
    )

    forwarded_request = ai_mock.await_args.args[0]
    assert str(forwarded_request.notebook_id) == str(notebook_id)
    assert payload["tool"] == "quiz"


def test_execute_audio_overview_passes_notebook_id_to_retrieval(monkeypatch):
    from src.interfaces.rest_api.ai import workflows
    from src.domains.platform.schemas.ai_runtime import InternalAudioOverviewRequest

    notebook_id = uuid4()
    retrieve_mock = AsyncMock(
        return_value=[
            {
                "text": "Photosynthesis uses sunlight to make food.",
                "citation": "[bio_1]",
                "source_file": "biology.pdf",
                "page_number": 1,
                "document_id": "doc-1",
            }
        ]
    )
    llm_mock = SimpleNamespace(
        generate_structured=AsyncMock(return_value={"response": {"title": "Photosynthesis", "dialogue": []}})
    )

    monkeypatch.setattr(workflows, "retrieve_context", retrieve_mock)
    monkeypatch.setattr(workflows, "build_context_string", lambda chunks: "context")
    monkeypatch.setattr(workflows, "get_llm_provider", lambda: llm_mock)

    payload = asyncio.run(
        workflows.execute_audio_overview(
            InternalAudioOverviewRequest(
                topic="Photosynthesis",
                format="deep_dive",
                language="english",
                notebook_id=notebook_id,
                tenant_id=str(uuid4()),
            )
        )
    )

    assert payload["title"] == "Photosynthesis"
    assert retrieve_mock.await_args.kwargs["notebook_id"] == str(notebook_id)


def test_retrieve_context_filters_low_vector_scores(monkeypatch):
    from src.infrastructure.vector_store import retrieval

    class FakeEmbeddingProvider:
        async def embed(self, query: str):
            return [0.1, 0.2]

    class FakeStore:
        chunk_count = 2

        def search(self, **_kwargs):
            return [
                ({"text": "Weak chunk", "source_file": "weak.pdf", "page_number": 1, "document_id": "doc-weak"}, 0.18),
                ({"text": "Strong chunk", "source_file": "strong.pdf", "page_number": 2, "document_id": "doc-strong"}, 0.91),
            ]

    monkeypatch.setattr(retrieval, "get_embedding_provider", lambda: FakeEmbeddingProvider())
    monkeypatch.setattr(retrieval, "get_vector_store_provider", lambda tenant_id: FakeStore())
    monkeypatch.setattr(retrieval, "rerank_chunks", lambda query, results, top_n=5: results[:top_n])
    monkeypatch.setattr(retrieval, "deduplicate_chunks", lambda chunks, similarity_threshold=0.85: chunks)
    monkeypatch.setattr(retrieval.settings.retrieval, "min_vector_score", 0.2)
    monkeypatch.setattr(retrieval.settings.retrieval, "min_rerank_score", 0.0)

    chunks = asyncio.run(retrieval.retrieve_context(query="cell", tenant_id="tenant-1", top_k=4))

    assert [chunk["document_id"] for chunk in chunks] == ["doc-strong"]
    assert chunks[0]["vector_score"] == 0.91


def test_retrieve_context_filters_low_rerank_scores(monkeypatch):
    from src.infrastructure.vector_store import retrieval

    class FakeEmbeddingProvider:
        async def embed(self, query: str):
            return [0.1, 0.2]

    class FakeStore:
        chunk_count = 2

        def search(self, **_kwargs):
            return [
                ({"text": "Chunk A", "source_file": "bio.pdf", "page_number": 1, "document_id": "doc-a"}, 0.91),
                ({"text": "Chunk B", "source_file": "bio.pdf", "page_number": 2, "document_id": "doc-b"}, 0.88),
            ]

    def fake_rerank(_query, results, top_n=5):
        return [
            (results[0][0], 0.49),
            (results[1][0], 0.87),
        ][:top_n]

    monkeypatch.setattr(retrieval, "get_embedding_provider", lambda: FakeEmbeddingProvider())
    monkeypatch.setattr(retrieval, "get_vector_store_provider", lambda tenant_id: FakeStore())
    monkeypatch.setattr(retrieval, "rerank_chunks", fake_rerank)
    monkeypatch.setattr(retrieval, "deduplicate_chunks", lambda chunks, similarity_threshold=0.85: chunks)
    monkeypatch.setattr(retrieval.settings.retrieval, "min_vector_score", 0.2)
    monkeypatch.setattr(retrieval.settings.retrieval, "min_rerank_score", 0.5)

    chunks = asyncio.run(retrieval.retrieve_context(query="cell", tenant_id="tenant-1", top_k=4))

    assert [chunk["document_id"] for chunk in chunks] == ["doc-b"]
    assert chunks[0]["vector_score"] == 0.88
    assert chunks[0]["rerank_score"] == 0.87


def test_execute_text_query_returns_retrieval_audit(monkeypatch):
    from src.interfaces.rest_api.ai import workflows
    from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest

    class FakeLLM:
        async def generate(self, prompt, model, temperature, num_predict, **kwargs):
            return {"response": "Grounded answer [biology.pdf_p4]", "token_usage": 12}

    monkeypatch.setattr(
        workflows,
        "retrieve_context",
        AsyncMock(
            return_value=[
                {
                    "text": "Photosynthesis converts light into chemical energy.",
                    "citation": "[biology.pdf_p4]",
                    "source": "biology.pdf",
                    "page": "4",
                    "section": "10.1",
                    "score": 0.91,
                    "vector_score": 0.88,
                    "rerank_score": 0.91,
                    "document_id": "doc-1",
                    "compressed": False,
                }
            ]
        ),
    )
    monkeypatch.setattr(workflows, "get_llm_provider", lambda: FakeLLM())
    monkeypatch.setattr(workflows.settings.retrieval, "audit_max_chunks", 3)

    payload = asyncio.run(
        workflows.execute_text_query(
            InternalAIQueryRequest(
                query="Explain topic 10.1",
                mode="qa",
                tenant_id=str(uuid4()),
                audit_retrieval=True,
            )
        )
    )

    assert payload["retrieval_audit"]["chunk_count"] == 1
    assert payload["retrieval_audit"]["chunks"][0]["document_id"] == "doc-1"
    assert payload["retrieval_audit"]["chunks"][0]["rerank_score"] == 0.91


def test_cache_key_varies_by_notebook_id():
    from src.infrastructure.llm.cache import _cache_key

    key_a = _cache_key(
        tenant_id="tenant-1",
        query="Explain photosynthesis",
        mode="qa",
        subject_id="biology",
        notebook_id="notebook-a",
    )
    key_b = _cache_key(
        tenant_id="tenant-1",
        query="Explain photosynthesis",
        mode="qa",
        subject_id="biology",
        notebook_id="notebook-b",
    )

    assert key_a != key_b


def test_invalidate_tenant_cache_is_scoped(monkeypatch):
    from src.infrastructure.llm import cache

    class FakeRedis:
        def __init__(self, keys):
            self.keys = list(keys)
            self.deleted = []

        def scan_iter(self, pattern):
            prefix = pattern.rstrip("*")
            return [key for key in self.keys if key.startswith(prefix)]

        def delete(self, key):
            self.deleted.append(key)

    tenant_a_global = cache._cache_key("tenant-a", "Explain cells", "qa")
    tenant_a_notebook = cache._cache_key("tenant-a", "Explain cells", "qa", notebook_id="notebook-1")
    tenant_b_global = cache._cache_key("tenant-b", "Explain cells", "qa")
    fake = FakeRedis([tenant_a_global, tenant_a_notebook, tenant_b_global])

    monkeypatch.setattr(cache, "_get_redis", lambda: fake)

    deleted = cache.invalidate_tenant_cache("tenant-a")

    assert deleted == 2
    assert tenant_a_global in fake.deleted
    assert tenant_a_notebook in fake.deleted
    assert tenant_b_global not in fake.deleted
