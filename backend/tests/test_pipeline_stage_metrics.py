import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import httpx
import pytest
from src.domains.platform.services.traceability import TraceabilityError


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


@pytest.fixture(autouse=True)
def reset_metrics_registry():
    from src.domains.platform.services.metrics_registry import reset_metrics_registry

    reset_metrics_registry()
    yield
    reset_metrics_registry()


@pytest.mark.asyncio
async def test_execute_text_query_records_retrieval_and_generation_success_metrics():
    from src.interfaces.rest_api.ai import workflows
    from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest
    from src.domains.platform.services.metrics_registry import snapshot_stage_latency_metrics

    chunks = [
        {
            "text": "Photosynthesis uses sunlight to make glucose.",
            "citation": "[biology.pdf_p10]",
            "source": "biology.pdf",
            "page": "10",
            "source_file": "biology.pdf",
            "page_number": 10,
            "document_id": "doc-1",
        }
    ]

    class FakeLLM:
        async def generate(self, prompt, model, temperature, num_predict, **kwargs):
            return {"response": "Plants make glucose using sunlight [biology.pdf_p10]", "token_usage": 11}

    with patch.object(workflows, "retrieve_context", AsyncMock(return_value=chunks)), \
         patch.object(workflows, "get_llm_provider", return_value=FakeLLM()):
        payload = await workflows.execute_text_query(
            InternalAIQueryRequest(
                query="Explain photosynthesis",
                mode="qa",
                tenant_id=str(uuid4()),
            )
        )

    rows = snapshot_stage_latency_metrics()
    metrics = {(row["stage"], row["operation"], row["outcome"]): row for row in rows}

    assert payload["citation_valid"] is True
    assert ("ai_query", "retrieval", "success") in metrics
    assert ("ai_query", "generation", "success") in metrics
    assert metrics[("ai_query", "retrieval", "success")]["count"] == 1.0
    assert metrics[("ai_query", "generation", "success")]["count"] == 1.0


@pytest.mark.asyncio
async def test_execute_text_query_records_generation_timeout_metric():
    from src.interfaces.rest_api.ai import workflows
    from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest
    from src.domains.platform.services.metrics_registry import snapshot_stage_latency_metrics

    chunks = [
        {
            "text": "The light reaction releases oxygen.",
            "citation": "[biology.pdf_p12]",
            "source": "biology.pdf",
            "page": "12",
            "source_file": "biology.pdf",
            "page_number": 12,
            "document_id": "doc-2",
        }
    ]

    class TimeoutLLM:
        async def generate(self, prompt, model, temperature, num_predict, **kwargs):
            raise httpx.TimeoutException("timed out")

    with patch.object(workflows, "retrieve_context", AsyncMock(return_value=chunks)), \
         patch.object(workflows, "get_llm_provider", return_value=TimeoutLLM()):
        with pytest.raises(TraceabilityError) as exc_info:
            await workflows.execute_text_query(
                InternalAIQueryRequest(
                    query="Explain the light reaction",
                    mode="qa",
                    tenant_id=str(uuid4()),
                )
            )

    rows = snapshot_stage_latency_metrics()
    metrics = {(row["stage"], row["operation"], row["outcome"]): row for row in rows}

    assert exc_info.value.status_code == 504
    assert ("ai_query", "retrieval", "success") in metrics
    assert ("ai_query", "generation", "timeout") in metrics
    assert metrics[("ai_query", "generation", "timeout")]["count"] == 1.0


@pytest.mark.asyncio
async def test_execute_whatsapp_media_ingestion_records_all_success_stage_metrics():
    from src.interfaces.rest_api.ai import ingestion_workflows
    from src.domains.platform.schemas.ai_runtime import InternalWhatsAppMediaIngestRequest
    from src.domains.platform.services.metrics_registry import snapshot_stage_latency_metrics

    document = SimpleNamespace(
        id=uuid4(),
        tenant_id=uuid4(),
        notebook_id=uuid4(),
        ingestion_status="processing",
        chunk_count=0,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = document
    embedding_provider = SimpleNamespace(embed_batch=AsyncMock(return_value=[[0.1, 0.2]]))
    vector_store = SimpleNamespace(add_chunks=MagicMock())
    fake_chunk = SimpleNamespace(
        text="Transcript chunk",
        document_id="doc-1",
        page_number=1,
        section_title="Transcript",
        subject_id="",
        notebook_id=str(document.notebook_id),
        source_file="lesson.mp4",
    )

    request = InternalWhatsAppMediaIngestRequest(
        document_id=str(document.id),
        file_path="C:/tmp/lesson.mp4",
        display_name="lesson.mp4",
        media_kind="video",
        follow_up_message="Explain the key ideas",
        follow_up_user_id="11111111-1111-1111-1111-111111111111",
        role="student",
        conversation_history=[{"role": "user", "content": "earlier context"}],
        tenant_id=str(document.tenant_id),
    )

    with patch.object(ingestion_workflows, "SessionLocal", return_value=db), \
         patch("src.infrastructure.vector_store.ingestion.ingest_media_transcript", return_value=[fake_chunk]), \
         patch("src.infrastructure.llm.providers.get_embedding_provider", return_value=embedding_provider), \
         patch("src.infrastructure.llm.providers.get_vector_store_provider", return_value=vector_store), \
         patch.object(ingestion_workflows, "invalidate_tenant_cache"), \
         patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=AsyncMock(return_value={
             "response": "Here is a grounded answer from the transcript.",
             "intent": "ask_ai_question",
             "tool_name": "ask_ai_question",
         })):
        payload = await ingestion_workflows.execute_whatsapp_media_ingestion(request)

    rows = snapshot_stage_latency_metrics()
    metrics = {(row["stage"], row["operation"], row["outcome"]): row for row in rows}

    assert payload["status"] == "completed"
    assert ("whatsapp_media_ingest", "transcription", "success") in metrics
    assert ("whatsapp_media_ingest", "embedding", "success") in metrics
    assert ("whatsapp_media_ingest", "follow_up_generation", "success") in metrics


@pytest.mark.asyncio
async def test_execute_whatsapp_media_ingestion_records_transcription_error_metric():
    from src.interfaces.rest_api.ai import ingestion_workflows
    from src.domains.platform.schemas.ai_runtime import InternalWhatsAppMediaIngestRequest
    from src.domains.platform.services.metrics_registry import snapshot_stage_latency_metrics

    document = SimpleNamespace(
        id=uuid4(),
        tenant_id=uuid4(),
        notebook_id=uuid4(),
        ingestion_status="processing",
        chunk_count=0,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = document

    request = InternalWhatsAppMediaIngestRequest(
        document_id=str(document.id),
        file_path="C:/tmp/broken.mp4",
        display_name="broken.mp4",
        media_kind="video",
        tenant_id=str(document.tenant_id),
    )

    with patch.object(ingestion_workflows, "SessionLocal", return_value=db), \
         patch("src.infrastructure.vector_store.ingestion.ingest_media_transcript", side_effect=RuntimeError("ffmpeg failed")):
        with pytest.raises(RuntimeError, match="ffmpeg failed"):
            await ingestion_workflows.execute_whatsapp_media_ingestion(request)

    rows = snapshot_stage_latency_metrics()
    metrics = {(row["stage"], row["operation"], row["outcome"]): row for row in rows}

    assert ("whatsapp_media_ingest", "transcription", "error") in metrics
    assert document.ingestion_status == "failed"
