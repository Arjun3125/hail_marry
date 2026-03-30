import io
import os
import sys
import tempfile
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


class _TeacherUploadDBStub:
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


class _AdminImportDBStub:
    def __init__(self):
        self.added = []

    def query(self, model):
        name = getattr(model, "__name__", str(model))
        if name in {"User", "Class"} or "Tenant" in name:
            return _ResultQuery(None)
        raise AssertionError(f"Unexpected model query: {name}")

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None


class _AttendanceImportDBStub:
    def __init__(self, student):
        self.student = student
        self.added = []

    def query(self, model):
        name = getattr(model, "__name__", str(model))
        if name == "Enrollment":
            return _ResultQuery(rows=[SimpleNamespace(student_id=self.student.id)])
        if name == "User":
            return _ResultQuery(self.student)
        if name == "Attendance":
            return _ResultQuery(None)
        raise AssertionError(f"Unexpected model query: {name}")

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        return None


def test_parse_attendance_rows_supports_freeform_ocr_lines():
    from src.shared.ocr_imports import parse_attendance_rows

    rows = parse_attendance_rows("Aarav Shah present\nDiya Patil absent\nMeera late")

    assert rows == [
        ("Aarav Shah", "present"),
        ("Diya Patil", "absent"),
        ("Meera", "late"),
    ]


def test_parse_marks_rows_supports_freeform_ocr_lines():
    from src.shared.ocr_imports import parse_marks_rows

    rows = parse_marks_rows("Aarav Shah 91\nDiya Patil,78")

    assert rows == [("Aarav Shah", 91), ("Diya Patil", 78)]


def test_parse_attendance_rows_reports_unmatched_lines_for_review():
    from src.shared.ocr_imports import parse_attendance_rows_with_diagnostics

    parsed = parse_attendance_rows_with_diagnostics("Aarav Shah present\nblurry row ???")

    assert parsed.rows == [("Aarav Shah", "present")]
    assert parsed.review_required is True
    assert parsed.unmatched_lines == ["blurry row ???"]
    assert "need review" in (parsed.warning or "")


def test_parse_account_rows_reports_unmatched_lines_for_review():
    from src.shared.ocr_imports import parse_account_rows_with_diagnostics

    parsed = parse_account_rows_with_diagnostics("Rohan Sharma\n??\nPreeti Patil", default_password="Student123!")

    assert len(parsed.rows) == 2
    assert parsed.review_required is True
    assert parsed.unmatched_lines == ["??"]
    assert "need review" in (parsed.warning or "")


@pytest.mark.asyncio
async def test_teacher_upload_document_converts_image_to_ocr_pdf_and_ingests():
    from src.domains.academic.routes import teacher as teacher_routes

    current_user = SimpleNamespace(tenant_id=uuid4(), id=uuid4())
    db = _TeacherUploadDBStub()
    file = UploadFile(filename="notes.png", file=io.BytesIO(b"image-bytes"))
    fake_chunk = SimpleNamespace(
        text="Plants make food by photosynthesis.",
        document_id="doc-1",
        page_number=1,
        section_title="Biology",
        subject_id="science",
        notebook_id="",
        source_file="notes.png",
    )
    embedding_provider = SimpleNamespace(embed_batch=AsyncMock(return_value=[[0.1, 0.2]]))
    vector_store = SimpleNamespace(add_chunks=MagicMock())

    with patch("builtins.open", mock_open()), \
         patch("src.infrastructure.vector_store.ingestion.ingest_document", return_value=[fake_chunk]), \
         patch("src.infrastructure.llm.embeddings.generate_embeddings_batch", AsyncMock(return_value=[[0.1, 0.2]])), \
         patch("src.infrastructure.vector_store.vector_store.get_vector_store", return_value=vector_store), \
         patch("src.domains.academic.routes.teacher.invalidate_tenant_cache") as invalidate_mock, \
         patch("src.infrastructure.vector_store.ocr_service.validate_image_size"), \
         patch(
             "src.infrastructure.vector_store.ocr_service.image_bytes_to_pdf",
             return_value=SimpleNamespace(
                 review_required=True,
                 warning="OCR extracted very little text. Review the image quality before proceeding.",
                 languages=["en", "hi", "mr"],
                 preprocessing_applied=["grayscale", "autocontrast"],
             ),
         ) as image_to_pdf_mock:
        payload = await teacher_routes.upload_document(file, current_user, db)

    assert payload["success"] is True
    assert payload["ocr_processed"] is True
    assert payload["ocr_review_required"] is True
    assert payload["ocr_languages"] == ["en", "hi", "mr"]
    image_to_pdf_mock.assert_called_once()
    invalidate_mock.assert_called_once_with(str(current_user.tenant_id))


@pytest.mark.asyncio
async def test_onboarding_import_students_accepts_image_and_builds_csv():
    from src.domains.identity.routes import onboarding as onboarding_routes

    user = SimpleNamespace(tenant_id=uuid4())

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
    ) as import_mock:
        payload = await onboarding_routes.import_students(
            UploadFile(filename="students.png", file=io.BytesIO(b"img")),
            user,
            MagicMock(),
        )

    assert payload["ocr_processed"] is True
    assert payload["ocr_review_required"] is False
    csv_text = import_mock.call_args.args[2]
    assert "full_name,email,class_name" in csv_text
    assert "rohan.sharma@example.com" in csv_text
    assert payload["imported"] == 2


@pytest.mark.asyncio
async def test_onboarding_import_students_flags_review_required_for_noisy_ocr():
    from src.domains.identity.routes import onboarding as onboarding_routes

    user = SimpleNamespace(tenant_id=uuid4())

    with patch.object(
        onboarding_routes,
        "extract_upload_content_result",
        return_value=SimpleNamespace(
            text="Rohan Sharma\n???\nPreeti Patil",
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
            user,
            MagicMock(),
        )

    assert payload["ocr_processed"] is True
    assert payload["ocr_review_required"] is True
    assert payload["ocr_unmatched_lines"] == 1
    assert "need review" in (payload["ocr_warning"] or "")


@pytest.mark.asyncio
async def test_admin_onboard_students_accepts_image_rows():
    from src.domains.administrative.routes import admin as admin_routes

    current_user = SimpleNamespace(tenant_id=uuid4())
    db = _AdminImportDBStub()

    with patch.object(
        admin_routes,
        "extract_upload_content_result",
        return_value=SimpleNamespace(
            text="Aarav Shah\nDiya Patil",
            used_ocr=True,
            review_required=False,
            warning=None,
            languages=["en", "hi", "mr"],
            preprocessing_applied=["grayscale"],
        ),
    ):
        payload = await admin_routes.onboard_students(
            UploadFile(filename="students.png", file=io.BytesIO(b"img")),
            current_user,
            db,
        )

    assert payload["success"] is True
    assert payload["ocr_processed"] is True
    assert payload["ocr_review_required"] is False
    assert payload["created"] == 2


@pytest.mark.asyncio
async def test_admin_onboard_teachers_flags_review_required_for_noisy_ocr():
    from src.domains.administrative.routes import admin as admin_routes

    current_user = SimpleNamespace(tenant_id=uuid4())
    db = _AdminImportDBStub()

    with patch.object(
        admin_routes,
        "extract_upload_content_result",
        return_value=SimpleNamespace(
            text="Aarav Shah\n???\nDiya Patil",
            used_ocr=True,
            review_required=False,
            warning=None,
            languages=["en", "hi", "mr"],
            preprocessing_applied=["grayscale"],
        ),
    ):
        payload = await admin_routes.onboard_teachers(
            UploadFile(filename="teachers.png", file=io.BytesIO(b"img")),
            current_user,
            db,
        )

    assert payload["success"] is True
    assert payload["created_count"] == 2
    assert payload["ocr_processed"] is True
    assert payload["ocr_review_required"] is True
    assert payload["ocr_unmatched_lines"] == 1
    assert "need review" in (payload["ocr_warning"] or "")


@pytest.mark.asyncio
async def test_teacher_attendance_import_accepts_image_names():
    from src.domains.academic.routes import teacher as teacher_routes

    tenant_id = uuid4()
    class_id = uuid4()
    student = SimpleNamespace(id=uuid4(), full_name="Aarav Shah", email="aarav@example.com")
    db = _AttendanceImportDBStub(student)
    current_user = SimpleNamespace(tenant_id=tenant_id, role="teacher")

    with patch.object(
        teacher_routes,
        "extract_upload_content_result",
        return_value=SimpleNamespace(
            text="Aarav Shah present",
            used_ocr=True,
            review_required=False,
            warning=None,
            languages=["en", "hi", "mr"],
            preprocessing_applied=["grayscale"],
        ),
    ):
        payload = await teacher_routes.import_attendance_csv(
            UploadFile(filename="attendance.png", file=io.BytesIO(b"img")),
            str(class_id),
            "2026-03-29",
            current_user,
            [class_id],
            db,
        )

    assert payload["success"] is True
    assert payload["imported"] == 1
    assert payload["errors"] == []
    assert payload["ocr_processed"] is True


@pytest.mark.asyncio
async def test_teacher_attendance_import_marks_review_required_when_some_ocr_lines_fail():
    from src.domains.academic.routes import teacher as teacher_routes

    tenant_id = uuid4()
    class_id = uuid4()
    student = SimpleNamespace(id=uuid4(), full_name="Aarav Shah", email="aarav@example.com")
    db = _AttendanceImportDBStub(student)
    current_user = SimpleNamespace(tenant_id=tenant_id, role="teacher")

    with patch.object(
        teacher_routes,
        "extract_upload_content_result",
        return_value=SimpleNamespace(
            text="Aarav Shah present\nnoise row",
            used_ocr=True,
            review_required=False,
            warning=None,
            languages=["en", "hi", "mr"],
            preprocessing_applied=["grayscale"],
        ),
    ):
        payload = await teacher_routes.import_attendance_csv(
            UploadFile(filename="attendance.png", file=io.BytesIO(b"img")),
            str(class_id),
            "2026-03-29",
            current_user,
            [class_id],
            db,
        )

    assert payload["success"] is True
    assert payload["imported"] == 1
    assert payload["ocr_review_required"] is True
    assert payload["ocr_unmatched_lines"] == 1
    assert "need review" in (payload["ocr_warning"] or "")


@pytest.mark.asyncio
async def test_whatsapp_media_ingest_returns_ocr_review_metadata():
    from src.domains.platform.services import whatsapp_gateway as whatsapp_mod

    tenant_id = str(uuid4())
    user_id = str(uuid4())
    db = _TeacherUploadDBStub()
    fake_chunk = SimpleNamespace(
        text="Plants make food using light energy.",
        document_id="doc-1",
        page_number=1,
        section_title="Biology",
        subject_id="science",
        notebook_id="",
        source_file="notes.png",
    )
    embedding_provider = SimpleNamespace(embed_batch=AsyncMock(return_value=[[0.1, 0.2]]))
    vector_store = SimpleNamespace(add_chunks=MagicMock())

    with patch.object(whatsapp_mod, "_download_whatsapp_media", new=AsyncMock(return_value=(b"image", "image/png"))), \
         patch.object(whatsapp_mod, "_create_whatsapp_notebook", return_value=SimpleNamespace(id=uuid4())), \
         patch("src.infrastructure.vector_store.ingestion.ingest_document", return_value=[fake_chunk]), \
         patch("src.infrastructure.llm.providers.get_embedding_provider", return_value=embedding_provider), \
         patch("src.infrastructure.llm.providers.get_vector_store_provider", return_value=vector_store), \
         patch("src.infrastructure.vector_store.ocr_service.validate_image_size"), \
         patch(
             "src.infrastructure.vector_store.ocr_service.image_bytes_to_pdf",
             return_value=SimpleNamespace(
                 review_required=True,
                 warning="OCR extracted very little text. Review the image quality before proceeding.",
                 languages=["en", "hi", "mr"],
                 preprocessing_applied=["grayscale", "autocontrast"],
             ),
         ), \
         patch.object(whatsapp_mod, "invalidate_tenant_cache") as invalidate_mock:
        payload = await whatsapp_mod._ingest_whatsapp_media_upload(
            db,
            user_id=user_id,
            tenant_id=tenant_id,
            media_id="media-123",
            message_type="image",
            media_filename="notes.png",
            media_mime_type="image/png",
        )

    assert payload["ocr_processed"] is True
    assert payload["ocr_review_required"] is True
    assert payload["ocr_languages"] == ["en", "hi", "mr"]
    assert "review recommended" in payload["response_text"]
    invalidate_mock.assert_called_once_with(tenant_id)


@pytest.mark.asyncio
async def test_ai_grading_returns_ocr_review_metadata():
    from src.domains.platform.services import ai_grading as ai_grading_mod

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(b"image")
        temp_path = tmp.name

    try:
        with patch.object(
            ai_grading_mod,
            "extract_ocr_result_from_image_path",
            return_value=SimpleNamespace(
                text="short answer",
                used_ocr=True,
                review_required=True,
                warning="OCR extracted very little text. Review the image quality before proceeding.",
                languages=["en", "hi", "mr"],
                preprocessing_applied=["grayscale"],
            ),
        ), patch.object(ai_grading_mod, "record_trace_event"):
            payload = await ai_grading_mod.run_ai_grade(
                {"file_path": temp_path, "file_name": "answer.png"},
                trace_id="trace-1",
                tenant_id=str(uuid4()),
            )
    finally:
        Path(temp_path).unlink(missing_ok=True)

    assert payload["ocr_processed"] is True
    assert payload["ocr_review_required"] is True
    assert payload["ocr_languages"] == ["en", "hi", "mr"]
    assert "Review the image quality" in (payload["ocr_warning"] or "")
