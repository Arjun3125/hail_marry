"""
Centralized constants for the VidyaOS backend.

All magic numbers, thresholds, and reusable config values live here.
Import these instead of hardcoding numbers in route handlers or services.
"""

# ── Grading Thresholds ──
# Used by report_card.py, whatsapp.py, admin.py
GRADE_THRESHOLDS = [
    (90, "A+"),
    (80, "A"),
    (70, "B+"),
    (60, "B"),
    (50, "C"),
    (40, "D"),
]
GRADE_FAIL = "F"


def compute_grade(pct: float) -> str:
    """Return letter grade for a percentage score."""
    for threshold, grade in GRADE_THRESHOLDS:
        if pct >= threshold:
            return grade
    return GRADE_FAIL


# ── Attendance Thresholds ──
ATTENDANCE_HEALTHY_PCT = 80
ATTENDANCE_WARNING_PCT = 60

# ── Performance Thresholds ──
PERFORMANCE_GOOD_PCT = 80
PERFORMANCE_AVERAGE_PCT = 60
WEAK_TOPIC_THRESHOLD_PCT = 60

# ── File Upload Limits ──
TEACHER_MAX_FILE_SIZE = 50 * 1024 * 1024   # 50 MB
STUDENT_MAX_FILE_SIZE = 25 * 1024 * 1024   # 25 MB
OCR_MAX_IMAGE_SIZE = 10 * 1024 * 1024      # 10 MB

TEACHER_ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png", "pptx", "xlsx"}
STUDENT_ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png", "pptx", "xlsx"}

# ── AI / Queue ──
DEFAULT_AI_QUERIES_LIMIT = 50
DEFAULT_LEADERBOARD_LIMIT = 50
EMBEDDING_BATCH_SIZE = 10

# ── Rate Limiting ──
RATE_LIMIT_WINDOW_SECONDS = 60

# ── Test Series Defaults ──
DEFAULT_TEST_TOTAL_MARKS = 100
DEFAULT_TEST_DURATION_MINUTES = 60

# ── Report Card Colors (for PDF generation) ──
PDF_PRIMARY_COLOR = "#1e3a5f"
PDF_MUTED_COLOR = "#64748b"
PDF_LABEL_COLOR = "#374151"
PDF_GRID_COLOR = "#cbd5e1"
PDF_HIGHLIGHT_BG = "#f0f9ff"

# ── WhatsApp notification emojis ──
def attendance_emoji(pct: float) -> str:
    """Return emoji for attendance percentage."""
    if pct >= ATTENDANCE_HEALTHY_PCT:
        return "🎉"
    if pct >= ATTENDANCE_WARNING_PCT:
        return "👍"
    return "📖"


def performance_color(avg_pct: float) -> str:
    """Return color label for admin dashboard."""
    if avg_pct >= PERFORMANCE_GOOD_PCT:
        return "green"
    if avg_pct >= PERFORMANCE_AVERAGE_PCT:
        return "yellow"
    return "red"


# ── Billing ──
BILLING_CURRENCY = "INR"
BILLING_PLANS = {
    "basic": {
        "price_per_student_yearly": 600,
        "label": "Basic (ERP Only)",
        "features": {"erp": True, "ai_chat": False, "ai_grading": False},
    },
    "standard": {
        "price_per_student_yearly": 900,
        "label": "Standard (Core AI)",
        "features": {"erp": True, "ai_chat": True, "ai_grading": False},
    },
    "premium": {
        "price_per_student_yearly": 1200,
        "label": "Premium (Full AI)",
        "features": {"erp": True, "ai_chat": True, "ai_grading": True},
    },
}

# ── Admission Workflow ──
ADMISSION_STATUSES = {"pending", "under_review", "accepted", "rejected", "enrolled"}
ADMISSION_STATUS_TRANSITIONS = {
    "pending": {"under_review", "rejected"},
    "under_review": {"accepted", "rejected"},
    "accepted": {"enrolled", "rejected"},
    "rejected": set(),
    "enrolled": set(),
}

# ── i18n ──
SUPPORTED_LOCALES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "mr": "मराठी (Marathi)",
}

# ── Fee Management ──
FEE_TYPES = {"tuition", "lab", "transport", "library", "exam", "other"}
FEE_FREQUENCIES = {"monthly", "quarterly", "yearly", "one_time"}
FEE_INVOICE_STATUSES = {"pending", "partial", "paid", "overdue", "cancelled"}

# ── LLM Providers ──
DEFAULT_LLM_PROVIDER = "ollama"
OLLAMA_BASE_URL = "http://localhost:11434"
SUPPORTED_LLM_PROVIDERS = {"ollama", "openai", "anthropic"}

# ── Extended Connectors ──
EXTENDED_FILE_TYPES = {"pptx", "xlsx", "google_doc", "notion"}
