import io
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, mock_open, patch
from uuid import uuid4

import pytest
from fastapi import UploadFile


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


class _ResultQuery:
    def __init__(self, result=None, rows=None):
        self.result = result
        self.rows = rows or []

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.result

    def all(self):
        return self.rows

    def scalar(self):
        return self.result


class _DocumentDBStub:
    def __init__(self):
        self.added = []

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()
        self.added.append(obj)

    def commit(self):
        return None

    def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()


class _PreviewDBStub:
    def query(self, model):
        return _ResultQuery(None)

    def add(self, obj):
        return None

    def flush(self):
        return None

    def commit(self):
        return None


@pytest.mark.asyncio
async def test_student_upload_non_image_always_returns_ocr_metadata_keys():
    from src.domains.academic.routes import students as student_routes

    current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
    db = _DocumentDBStub()
    file = UploadFile(filename="notes.pdf", file=io.BytesIO(b"%PDF-1.4"))
    fake_chunk = SimpleNamespace(
        text="Photosynthesis uses sunlight.",
        document_id="doc-1",
        page_number=1,
        section_title="Biology",
        subject_id="science",
        notebook_id="",
        source_file="notes.pdf",
    )
    vector_store = SimpleNamespace(add_chunks=MagicMock())

    with patch("builtins.open", mock_open()), \
         patch("src.infrastructure.vector_store.ingestion.ingest_document", return_value=[fake_chunk]), \
         patch("src.infrastructure.llm.providers.get_embedding_provider", return_value=SimpleNamespace(embed_batch=AsyncMock(return_value=[[0.1, 0.2]]))), \
         patch("src.infrastructure.llm.providers.get_vector_store_provider", return_value=vector_store), \
         patch("src.domains.academic.routes.students.invalidate_tenant_cache"):
        payload = await student_routes.student_upload(file, current_user, db)

    assert payload["success"] is True
    assert payload["ocr_processed"] is False
    assert payload["ocr_review_required"] is False
    assert payload["ocr_warning"] is None
    assert payload["ocr_languages"] == []
    assert payload["ocr_preprocessing"] == []
    assert "ocr_confidence" in payload
    assert payload["ocr_confidence"] is None


@pytest.mark.asyncio
async def test_teacher_onboard_student_preview_tolerates_missing_ocr_confidence():
    from src.domains.academic.routes import teacher as teacher_routes

    current_user = SimpleNamespace(tenant_id=uuid4(), role="teacher")

    with patch.object(
        teacher_routes,
        "extract_upload_content_result",
        return_value=SimpleNamespace(
            text="Aarav Patil\nDiya Shah",
            used_ocr=True,
            review_required=True,
            warning="Low confidence OCR result.",
            languages=["en", "hi"],
            preprocessing_applied=["grayscale"],
        ),
    ):
        payload = await teacher_routes.onboard_students(
            UploadFile(filename="students.png", file=io.BytesIO(b"img")),
            preview=True,
            current_user=current_user,
            db=MagicMock(),
        )

    assert payload["success"] is True
    assert payload["preview"] is True
    assert payload["ocr_processed"] is True
    assert payload["ocr_review_required"] is True
    assert payload["ocr_warning"] == "Low confidence OCR result."
    assert "ocr_confidence" in payload
    assert payload["ocr_confidence"] is None


@pytest.mark.asyncio
async def test_admin_onboard_students_preview_tolerates_missing_ocr_confidence():
    from src.domains.administrative.routes import admin as admin_routes

    current_user = SimpleNamespace(tenant_id=uuid4())
    db = _PreviewDBStub()

    with patch.object(
        admin_routes,
        "extract_upload_content_result",
        return_value=SimpleNamespace(
            text="Aarav Shah\nDiya Patil",
            used_ocr=True,
            review_required=False,
            warning=None,
            languages=["en", "mr"],
            preprocessing_applied=["grayscale"],
        ),
    ):
        payload = await admin_routes.onboard_students(
            UploadFile(filename="students.png", file=io.BytesIO(b"img")),
            current_user,
            db,
            preview=True,
        )

    assert payload["success"] is True
    assert payload["preview"] is True
    assert payload["ocr_processed"] is True
    assert payload["ocr_confidence"] is None
    assert payload["ocr_unmatched_lines"] == 0


@pytest.mark.asyncio
async def test_onboarding_import_students_tolerates_missing_ocr_confidence():
    from src.domains.identity.routes import onboarding as onboarding_routes

    current_user = SimpleNamespace(tenant_id=uuid4())

    with patch.object(
        onboarding_routes,
        "extract_upload_content_result",
        return_value=SimpleNamespace(
            text="Rohan Sharma\nPreeti Patil",
            used_ocr=True,
            review_required=False,
            warning=None,
            languages=["en", "hi", "mr"],
            preprocessing_applied=["grayscale"],
        ),
    ), patch.object(
        onboarding_routes,
        "import_students_from_csv",
        return_value={"imported": 2, "skipped": 0, "errors": []},
    ):
        payload = await onboarding_routes.import_students(
            UploadFile(filename="students.png", file=io.BytesIO(b"img")),
            current_user,
            MagicMock(),
        )

    assert payload["status"] == "import_complete"
    assert payload["ocr_processed"] is True
    assert "ocr_confidence" in payload
    assert payload["ocr_confidence"] is None
    assert payload["ocr_unmatched_lines"] == 0
