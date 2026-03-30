import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, mock_open, patch
from uuid import uuid4

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


@pytest.mark.asyncio
async def test_ingest_whatsapp_media_upload_trims_queued_history_snapshot_to_last_ten_items():
    from src.domains.platform.services import whatsapp_gateway as whatsapp_mod

    tenant_id = str(uuid4())
    user_id = str(uuid4())
    notebook = SimpleNamespace(id=uuid4())

    class _DBStub:
        def add(self, obj):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()

        def commit(self):
            return None

        def refresh(self, obj):
            if getattr(obj, "id", None) is None:
                obj.id = uuid4()

    history = [{"role": "user", "content": f"message-{idx}"} for idx in range(15)]

    with patch.object(whatsapp_mod, "_download_whatsapp_media", new=AsyncMock(return_value=(b"video-bytes", "video/mp4"))), \
         patch.object(whatsapp_mod, "_create_whatsapp_notebook", return_value=notebook), \
         patch("builtins.open", mock_open()), \
         patch("src.domains.platform.services.ai_queue.enqueue_job", return_value={"job_id": "job-123"}) as enqueue_mock:
        payload = await whatsapp_mod._ingest_whatsapp_media_upload(
            _DBStub(),
            user_id=user_id,
            tenant_id=tenant_id,
            media_id="media-video-123",
            message_type="video",
            text="Explain the key ideas",
            media_filename="lesson.mp4",
            media_mime_type="video/mp4",
            conversation_history=list(history),
        )

    assert payload["status"] == "queued"
    queued_payload = enqueue_mock.call_args.args[1]
    assert len(queued_payload["conversation_history"]) == 10
    assert queued_payload["conversation_history"][0]["content"] == "message-5"
    assert queued_payload["conversation_history"][-1]["content"] == "message-14"


@pytest.mark.asyncio
async def test_execute_whatsapp_media_ingestion_uses_document_notebook_and_trimmed_history_for_follow_up():
    from src.domains.platform.schemas.ai_runtime import InternalWhatsAppMediaIngestRequest
    from src.interfaces.rest_api.ai import ingestion_workflows

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
    history = [{"role": "user", "content": f"earlier-{idx}"} for idx in range(14)]

    request = InternalWhatsAppMediaIngestRequest(
        document_id=str(document.id),
        file_path="C:/tmp/lesson.mp4",
        display_name="lesson.mp4",
        media_kind="video",
        follow_up_message="Explain the key ideas",
        follow_up_user_id="11111111-1111-1111-1111-111111111111",
        role="student",
        conversation_history=history,
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
         })) as agent_mock:
        payload = await ingestion_workflows.execute_whatsapp_media_ingestion(request)

    assert payload["status"] == "completed"
    kwargs = agent_mock.await_args.kwargs
    assert kwargs["notebook_id"] == str(document.notebook_id)
    assert len(kwargs["conversation_history"]) == 10
    assert kwargs["conversation_history"][0]["content"] == "earlier-4"
    assert kwargs["conversation_history"][-1]["content"] == "earlier-13"


@pytest.mark.asyncio
async def test_execute_whatsapp_media_ingestion_passes_none_notebook_when_document_has_no_notebook():
    from src.domains.platform.schemas.ai_runtime import InternalWhatsAppMediaIngestRequest
    from src.interfaces.rest_api.ai import ingestion_workflows

    document = SimpleNamespace(
        id=uuid4(),
        tenant_id=uuid4(),
        notebook_id=None,
        ingestion_status="processing",
        chunk_count=0,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = document
    embedding_provider = SimpleNamespace(embed_batch=AsyncMock(return_value=[[0.1, 0.2]]))
    vector_store = SimpleNamespace(add_chunks=MagicMock())
    fake_chunk = SimpleNamespace(
        text="Transcript chunk",
        document_id="doc-2",
        page_number=1,
        section_title="Transcript",
        subject_id="",
        notebook_id="",
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
        conversation_history=[],
        tenant_id=str(document.tenant_id),
    )

    with patch.object(ingestion_workflows, "SessionLocal", return_value=db), \
         patch("src.infrastructure.vector_store.ingestion.ingest_media_transcript", return_value=[fake_chunk]), \
         patch("src.infrastructure.llm.providers.get_embedding_provider", return_value=embedding_provider), \
         patch("src.infrastructure.llm.providers.get_vector_store_provider", return_value=vector_store), \
         patch.object(ingestion_workflows, "invalidate_tenant_cache"), \
         patch("src.interfaces.whatsapp_bot.agent.run_whatsapp_agent", new=AsyncMock(return_value={
             "response": "Grounded answer without notebook.",
             "intent": "ask_ai_question",
             "tool_name": "ask_ai_question",
         })) as agent_mock:
        payload = await ingestion_workflows.execute_whatsapp_media_ingestion(request)

    assert payload["status"] == "completed"
    assert agent_mock.await_args.kwargs["notebook_id"] is None
