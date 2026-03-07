"""Shared schemas for AI runtime and optional AI service separation."""
from typing import Literal

from pydantic import BaseModel, ConfigDict

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AIQueryRequest(StrictBaseModel):
    query: str
    mode: str = "qa"
    subject_id: str | None = None
    language: str = "english"
    response_length: str = "default"
    expertise_level: str = "standard"


class InternalAIQueryRequest(AIQueryRequest):
    tenant_id: str


class AudioOverviewRequest(StrictBaseModel):
    topic: str
    format: str = "deep_dive"
    language: str = "english"


class InternalAudioOverviewRequest(AudioOverviewRequest):
    tenant_id: str


class VideoOverviewRequest(StrictBaseModel):
    topic: str
    num_slides: int = 6
    language: str = "english"


class InternalVideoOverviewRequest(VideoOverviewRequest):
    tenant_id: str


class StudyToolGenerateRequest(StrictBaseModel):
    tool: Literal["quiz", "flashcards", "mindmap", "flowchart", "concept_map"]
    topic: str
    subject_id: str | None = None


class InternalStudyToolGenerateRequest(StudyToolGenerateRequest):
    tenant_id: str


class TeacherAssessmentRequest(StrictBaseModel):
    subject_id: str
    topic: str
    num_questions: int = 5


class InternalTeacherAssessmentRequest(TeacherAssessmentRequest):
    tenant_id: str
    subject_name: str


class IngestURLRequest(StrictBaseModel):
    url: str
    title: str = ""
    subject_id: str | None = None


class InternalIngestURLRequest(IngestURLRequest):
    tenant_id: str


class TeacherDocumentIngestRequest(StrictBaseModel):
    document_id: str
    file_path: str
    file_name: str
    subject_id: str | None = None
    uploaded_by: str
    macros_removed: bool = False


class InternalTeacherDocumentIngestRequest(TeacherDocumentIngestRequest):
    tenant_id: str


class TeacherYoutubeIngestRequest(StrictBaseModel):
    lecture_id: str
    url: str
    title: str
    subject_id: str


class InternalTeacherYoutubeIngestRequest(TeacherYoutubeIngestRequest):
    tenant_id: str
