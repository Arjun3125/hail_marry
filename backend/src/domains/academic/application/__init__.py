"""Academic application orchestration services."""

from .assessment_generation import generate_subject_assessment
from .parent_portal import (
    build_parent_attendance_response,
    build_parent_audio_report_response,
    build_parent_dashboard_response,
    build_parent_digest_preview_response,
    build_parent_report_card_payload,
    build_parent_reports_response,
    get_child_for_parent,
    get_child_results,
)
from .student_assignments import list_student_assignments
from .student_complaints import create_student_complaint, list_student_complaints
from .student_dashboard import build_student_dashboard_response
from .student_learning_insights import (
    build_student_weak_topics,
    list_student_timetable,
    list_student_uploads,
)
from .student_lectures import list_student_lectures
from .student_reviews import (
    complete_student_review,
    create_student_review,
    list_student_reviews,
)
from .student_submissions import (
    StudentAssignmentSubmissionError,
    submit_student_assignment,
)
from .student_engagement import (
    StudentMockTestSubmissionError,
    get_student_streak_overview,
    get_student_test_series_leaderboard,
    get_student_test_series_rank,
    get_student_weakness_alerts,
    list_student_test_series,
    submit_student_mock_test,
)
from .student_quiz_results import (
    StudentQuizResultError,
    process_student_quiz_result,
)
from .student_uploads import StudentUploadError, ingest_student_upload
from .student_results import (
    build_student_result_trends,
    build_student_results,
    list_student_attendance,
)
from .student_study_tools import (
    build_study_tool_personalization,
    generate_student_study_tool,
    generate_student_study_tool_job,
    mark_demo_payload,
)
from .teacher_bulk_updates import (
    apply_bulk_attendance_entries,
    apply_bulk_marks_entries,
    apply_structured_attendance_import_rows,
    apply_structured_marks_import_rows,
)
from .teacher_coursework import (
    build_class_attendance_response,
    build_created_assignment_response,
    build_created_exam_response,
    build_teacher_assignments_response,
)
from .teacher_analytics import (
    build_teacher_classes_response,
    build_teacher_dashboard_response,
    build_teacher_doubt_heatmap_response,
    build_teacher_insights_response,
)
from .teacher_ingestion import (
    TeacherIngestionError,
    ingest_teacher_youtube_video,
    upload_teacher_document,
)
from .teacher_onboarding import (
    TeacherOnboardingError,
    onboard_students_from_upload,
)
from .teacher_reporting import (
    build_attendance_csv_payload,
    build_created_test_series_response,
    build_marks_csv_payload,
    build_teacher_test_series_leaderboard_response,
    list_teacher_test_series_response,
    queue_teacher_ai_grade_job,
)

__all__ = [
    "build_study_tool_personalization",
    "get_child_for_parent",
    "get_child_results",
    "build_parent_dashboard_response",
    "build_parent_attendance_response",
    "build_parent_reports_response",
    "build_parent_audio_report_response",
    "build_parent_digest_preview_response",
    "build_parent_report_card_payload",
    "create_student_complaint",
    "build_student_dashboard_response",
    "build_student_weak_topics",
    "list_student_timetable",
    "list_student_uploads",
    "list_student_assignments",
    "list_student_lectures",
    "list_student_complaints",
    "list_student_reviews",
    "create_student_review",
    "complete_student_review",
    "StudentAssignmentSubmissionError",
    "submit_student_assignment",
    "StudentMockTestSubmissionError",
    "get_student_streak_overview",
    "get_student_weakness_alerts",
    "list_student_test_series",
    "get_student_test_series_leaderboard",
    "get_student_test_series_rank",
    "submit_student_mock_test",
    "StudentQuizResultError",
    "process_student_quiz_result",
    "StudentUploadError",
    "ingest_student_upload",
    "build_student_result_trends",
    "build_student_results",
    "list_student_attendance",
    "apply_bulk_attendance_entries",
    "apply_bulk_marks_entries",
    "apply_structured_attendance_import_rows",
    "apply_structured_marks_import_rows",
    "build_class_attendance_response",
    "build_created_exam_response",
    "build_teacher_assignments_response",
    "build_created_assignment_response",
    "build_teacher_dashboard_response",
    "build_teacher_classes_response",
    "build_teacher_insights_response",
    "build_teacher_doubt_heatmap_response",
    "TeacherIngestionError",
    "upload_teacher_document",
    "ingest_teacher_youtube_video",
    "TeacherOnboardingError",
    "onboard_students_from_upload",
    "build_attendance_csv_payload",
    "build_marks_csv_payload",
    "queue_teacher_ai_grade_job",
    "build_created_test_series_response",
    "list_teacher_test_series_response",
    "build_teacher_test_series_leaderboard_response",
    "generate_student_study_tool",
    "generate_student_study_tool_job",
    "generate_subject_assessment",
    "mark_demo_payload",
]
