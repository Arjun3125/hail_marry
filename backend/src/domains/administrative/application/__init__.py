"""Administrative application orchestration services."""

from .ai_jobs import (
    build_ai_job_detail_response,
    build_ai_job_list_response,
)
from .ai_review import (
    build_ai_review_detail_response,
    build_ai_review_list_response,
)
from .admin_onboarding import (
    process_student_onboarding_upload,
    process_teacher_onboarding_upload,
)
from .academics import (
    build_admin_classes_response,
    build_admin_timetable_response,
    create_admin_class,
    create_admin_subject,
    create_admin_timetable_slot,
    delete_admin_timetable_slot,
    generate_admin_timetable_schedule,
)
from .complaints import (
    build_admin_complaints_response,
    update_admin_complaint,
)
from .communications import (
    build_admin_report_card_payload,
    send_admin_whatsapp_digest_bulk,
)
from .dashboard import build_admin_dashboard_response
from .parent_links import (
    build_admin_parent_links_response,
    create_admin_parent_link,
    delete_admin_parent_link,
)
from .reporting import (
    build_admin_ai_usage_report,
    build_admin_ai_usage_csv_export,
    build_admin_attendance_report,
    build_admin_attendance_csv_export,
    build_admin_billing_info,
    build_admin_performance_csv_export,
    build_admin_performance_heatmap,
    build_admin_performance_report,
    build_admin_security_logs,
)
from .settings import (
    build_admin_settings_response,
    update_admin_settings,
)
from .user_management import (
    build_admin_csv_template_payload,
    build_admin_students_response,
    build_admin_users_response,
    change_admin_user_role,
    generate_admin_qr_tokens,
    toggle_admin_user_active,
)
from .webhooks import (
    build_admin_webhook_deliveries_response,
    build_admin_webhooks_response,
    create_admin_webhook,
    delete_admin_webhook,
    toggle_admin_webhook,
)

__all__ = [
    "build_ai_job_detail_response",
    "build_ai_job_list_response",
    "build_ai_review_detail_response",
    "build_ai_review_list_response",
    "build_admin_ai_usage_csv_export",
    "build_admin_ai_usage_report",
    "build_admin_attendance_csv_export",
    "build_admin_attendance_report",
    "build_admin_billing_info",
    "build_admin_classes_response",
    "build_admin_complaints_response",
    "build_admin_dashboard_response",
    "build_admin_parent_links_response",
    "build_admin_performance_csv_export",
    "build_admin_performance_heatmap",
    "build_admin_performance_report",
    "build_admin_report_card_payload",
    "build_admin_security_logs",
    "build_admin_settings_response",
    "build_admin_students_response",
    "build_admin_users_response",
    "build_admin_webhook_deliveries_response",
    "build_admin_webhooks_response",
    "build_admin_csv_template_payload",
    "build_admin_timetable_response",
    "create_admin_class",
    "change_admin_user_role",
    "create_admin_subject",
    "create_admin_timetable_slot",
    "create_admin_webhook",
    "delete_admin_timetable_slot",
    "delete_admin_webhook",
    "delete_admin_parent_link",
    "generate_admin_timetable_schedule",
    "create_admin_parent_link",
    "process_student_onboarding_upload",
    "process_teacher_onboarding_upload",
    "send_admin_whatsapp_digest_bulk",
    "toggle_admin_webhook",
    "toggle_admin_user_active",
    "generate_admin_qr_tokens",
    "update_admin_settings",
    "update_admin_complaint",
]
