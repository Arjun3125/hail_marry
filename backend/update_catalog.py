import json

catalog_path = "features_catalog.json"

with open(catalog_path, "r", encoding="utf-8") as f:
    features = json.load(f)

ai_map = {
    "Heavy AI": [
        "ai_grading_copilot",
        "ai_study_tools",
        "document_intelligence",
        "ai_chat",
        "youtube_ingestion",
        "ocr_onboarding",
        "whatsapp_ai",
        "audio_video_overviews",
        "openai_api",
        "knowledge_graph",
        "hyde_transform",
        "extended_connectors",
        "agent_orchestrator",
        "clickable_citations",
        "docs_chatbot",
    ],
    "Medium AI": ["smart_weakness_alerts", "trace_viewer"],
    "Low AI": [],
    "No AI": [
        "bulk_attendance_marks",
        "realtime_notifications",
        "offline_mode_pwa",
        "dark_mode",
        "study_streaks",
        "parent_weekly_digest",
        "spaced_repetition",
        "attendance_tracking",
        "exam_management",
        "assignment_management",
        "complaint_system",
        "parent_dashboard",
        "admin_dashboard",
        "multi_tenant",
        "compliance_export",
        "incident_management",
        "leaderboard",
        "report_card_pdf",
        "webhook_subscriptions",
        "queue_operations",
        "observability_alerts",
        "enterprise_sso",
        "performance_heatmap",
        "upload_security",
        "razorpay_billing",
        "i18n_support",
        "self_service_onboarding",
        "admission_workflow",
        "fee_management",
        "token_blacklisting",
        "doc_ingestion_watch",
        "recaptcha",
        "plugin_architecture",
        "library_management",
        "team_invitation",
        "enterprise_onboarding",
        "magic_qr",
        "emergency_broadcasts",
    ],
}

erp_modules = {
    "Student Management": [
        "bulk_attendance_marks",
        "attendance_tracking",
        "parent_weekly_digest",
        "parent_dashboard",
        "study_streaks",
        "leaderboard",
        "student_onboarding_ocr",
    ],
    "Examinations": ["exam_management", "ai_grading_copilot", "report_card_pdf", "smart_weakness_alerts"],
    "Learning Management": [
        "assignment_management",
        "ai_study_tools",
        "ai_chat",
        "document_intelligence",
        "youtube_ingestion",
        "spaced_repetition",
        "audio_video_overviews",
        "docs_chatbot",
    ],
    "Finance": ["razorpay_billing", "fee_management"],
    "Communication": ["realtime_notifications", "whatsapp_ai", "complaint_system", "webhook_subscriptions", "emergency_broadcasts"],
    "Platform Operations": [
        "offline_mode_pwa",
        "dark_mode",
        "admin_dashboard",
        "multi_tenant",
        "compliance_export",
        "incident_management",
        "queue_operations",
        "observability_alerts",
        "enterprise_sso",
        "upload_security",
        "i18n_support",
        "self_service_onboarding",
        "token_blacklisting",
        "doc_ingestion_watch",
        "recaptcha",
        "plugin_architecture",
    ],
    "Analytics": ["performance_heatmap", "trace_viewer"],
    "AI Core Infrastructure": [
        "openai_api",
        "knowledge_graph",
        "hyde_transform",
        "extended_connectors",
        "agent_orchestrator",
        "clickable_citations",
        "ocr_onboarding",
    ],
    "Library Management": ["library_management"],
    "Admissions": ["admission_workflow", "enterprise_onboarding", "magic_qr", "team_invitation"],
}

for i, feature in enumerate(features):
    fid = feature["feature_id"]

    ai_intensity = "No AI"
    for level, ids in ai_map.items():
        if fid in ids:
            ai_intensity = level

    module = "Platform Operations"
    for mod, ids in erp_modules.items():
        if fid in ids:
            module = mod

    features[i]["ai_intensity"] = ai_intensity
    features[i]["module"] = module

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(features, f, indent=2)

print("Successfully updated features_catalog.json with modules and AI Intensity levels!")
