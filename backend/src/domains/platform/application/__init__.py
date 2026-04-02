"""Platform application orchestration services."""

from .ai_queries import (
    build_demo_ai_result,
    build_personalized_ai_request,
    prepare_ai_query,
    validate_notebook_access,
)
from .mascot_release_gate import (
    build_combined_staging_packet_markdown,
    build_mascot_metric_snapshot,
    build_release_gate_evidence_markdown,
    build_release_gate_snapshot,
)
from .mascot_suggestions import build_student_mascot_suggestions
from .personalization_queries import (
    build_completed_study_path_response,
    build_personalization_profile_response,
    build_personalization_metrics_summary,
    build_personalized_recommendations_response,
    build_personalization_remediation_response,
    build_personalization_study_path_response,
    build_recomputed_personalization_profile_response,
)
from .whatsapp_analytics import build_whatsapp_usage_snapshot

__all__ = [
    "build_combined_staging_packet_markdown",
    "build_completed_study_path_response",
    "build_demo_ai_result",
    "build_mascot_metric_snapshot",
    "build_personalization_profile_response",
    "build_personalization_metrics_summary",
    "build_personalized_recommendations_response",
    "build_personalization_remediation_response",
    "build_personalization_study_path_response",
    "build_personalized_ai_request",
    "build_recomputed_personalization_profile_response",
    "build_release_gate_evidence_markdown",
    "build_release_gate_snapshot",
    "build_student_mascot_suggestions",
    "build_whatsapp_usage_snapshot",
    "prepare_ai_query",
    "validate_notebook_access",
]
