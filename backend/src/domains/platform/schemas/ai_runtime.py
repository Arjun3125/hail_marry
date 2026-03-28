"""Shared schemas for the in-process AI runtime and worker execution paths."""
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

try:
    from pydantic import field_validator
except ImportError:  # Pydantic v1 compatibility
    from pydantic import validator as field_validator


AI_QUERY_MODE = Literal[
    "qa",
    "study_guide",
    "quiz",
    "concept_map",
    "weak_topic",
    "flowchart",
    "mindmap",
    "flashcards",
    "socratic",
    "perturbation",
    "debate",
    "essay_review",
]
AI_RESPONSE_LENGTH = Literal["brief", "default", "detailed"]
AI_EXPERTISE_LEVEL = Literal["simple", "standard", "advanced"]


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AIQueryRequest(StrictBaseModel):
    query: str
    mode: AI_QUERY_MODE = "qa"
    subject_id: str | None = None
    notebook_id: UUID | None = None
    language: str = "english"
    response_length: AI_RESPONSE_LENGTH = "default"
    expertise_level: AI_EXPERTISE_LEVEL = "standard"

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Query must not be empty.")
        return normalized


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


class IngestURLRequest(StrictBaseModel):
    url: str
    subject_id: str | None = None
    title: str | None = None


class InternalIngestURLRequest(IngestURLRequest):
    tenant_id: str


class TeacherDocumentIngestRequest(StrictBaseModel):
    subject_id: str
    filename: str
    content_type: str | None = None


class InternalTeacherDocumentIngestRequest(TeacherDocumentIngestRequest):
    tenant_id: str
    file_path: str


class TeacherYoutubeIngestRequest(StrictBaseModel):
    subject_id: str
    youtube_url: str


class InternalTeacherYoutubeIngestRequest(TeacherYoutubeIngestRequest):
    tenant_id: str
