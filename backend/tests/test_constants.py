"""Tests for the centralized constants module."""
from constants import (
    GRADE_THRESHOLDS,
    compute_grade,
    ATTENDANCE_HEALTHY_PCT,
    ATTENDANCE_WARNING_PCT,
    PERFORMANCE_GOOD_PCT,
    PERFORMANCE_AVERAGE_PCT,
    WEAK_TOPIC_THRESHOLD_PCT,
    TEACHER_MAX_FILE_SIZE,
    STUDENT_MAX_FILE_SIZE,
    OCR_MAX_IMAGE_SIZE,
    TEACHER_ALLOWED_EXTENSIONS,
    STUDENT_ALLOWED_EXTENSIONS,
    DEFAULT_AI_QUERIES_LIMIT,
    DEFAULT_LEADERBOARD_LIMIT,
    EMBEDDING_BATCH_SIZE,
    RATE_LIMIT_WINDOW_SECONDS,
    DEFAULT_TEST_TOTAL_MARKS,
    DEFAULT_TEST_DURATION_MINUTES,
    PDF_PRIMARY_COLOR,
    PDF_MUTED_COLOR,
    PDF_LABEL_COLOR,
    PDF_GRID_COLOR,
    PDF_HIGHLIGHT_BG,
    attendance_emoji,
    performance_color,
)


class TestComputeGrade:
    """Test grading threshold logic."""

    def test_grade_a_plus(self):
        assert compute_grade(95) == "A+"
        assert compute_grade(90) == "A+"

    def test_grade_a(self):
        assert compute_grade(85) == "A"
        assert compute_grade(80) == "A"

    def test_grade_b_plus(self):
        assert compute_grade(75) == "B+"
        assert compute_grade(70) == "B+"

    def test_grade_b(self):
        assert compute_grade(65) == "B"
        assert compute_grade(60) == "B"

    def test_grade_c(self):
        assert compute_grade(55) == "C"
        assert compute_grade(50) == "C"

    def test_grade_d(self):
        assert compute_grade(45) == "D"
        assert compute_grade(40) == "D"

    def test_grade_fail(self):
        assert compute_grade(39) == "F"
        assert compute_grade(0) == "F"
        assert compute_grade(10) == "F"

    def test_grade_boundary_exact(self):
        """Exact boundary values should return the higher grade."""
        for threshold, expected_grade in GRADE_THRESHOLDS:
            assert compute_grade(threshold) == expected_grade

    def test_grade_below_boundary(self):
        """One below each boundary should drop to next grade."""
        assert compute_grade(89) == "A"
        assert compute_grade(79) == "B+"
        assert compute_grade(69) == "B"
        assert compute_grade(59) == "C"
        assert compute_grade(49) == "D"
        assert compute_grade(39) == "F"

    def test_grade_100(self):
        assert compute_grade(100) == "A+"

    def test_grade_negative(self):
        assert compute_grade(-5) == "F"


class TestAttendanceEmoji:
    """Test attendance emoji helper."""

    def test_high_attendance(self):
        assert attendance_emoji(90) == "🎉"
        assert attendance_emoji(80) == "🎉"

    def test_medium_attendance(self):
        assert attendance_emoji(70) == "👍"
        assert attendance_emoji(60) == "👍"

    def test_low_attendance(self):
        assert attendance_emoji(50) == "📖"
        assert attendance_emoji(30) == "📖"
        assert attendance_emoji(0) == "📖"

    def test_boundary_values(self):
        assert attendance_emoji(ATTENDANCE_HEALTHY_PCT) == "🎉"
        assert attendance_emoji(ATTENDANCE_WARNING_PCT) == "👍"
        assert attendance_emoji(ATTENDANCE_WARNING_PCT - 1) == "📖"


class TestPerformanceColor:
    """Test performance color helper."""

    def test_green(self):
        assert performance_color(90) == "green"
        assert performance_color(80) == "green"

    def test_yellow(self):
        assert performance_color(70) == "yellow"
        assert performance_color(60) == "yellow"

    def test_red(self):
        assert performance_color(50) == "red"
        assert performance_color(30) == "red"

    def test_boundary_values(self):
        assert performance_color(PERFORMANCE_GOOD_PCT) == "green"
        assert performance_color(PERFORMANCE_AVERAGE_PCT) == "yellow"
        assert performance_color(PERFORMANCE_AVERAGE_PCT - 1) == "red"


class TestConstantValues:
    """Verify that constants have expected types and reasonable values."""

    def test_thresholds_are_integers(self):
        assert isinstance(ATTENDANCE_HEALTHY_PCT, int)
        assert isinstance(ATTENDANCE_WARNING_PCT, int)
        assert isinstance(PERFORMANCE_GOOD_PCT, int)
        assert isinstance(PERFORMANCE_AVERAGE_PCT, int)
        assert isinstance(WEAK_TOPIC_THRESHOLD_PCT, int)

    def test_file_sizes_are_positive(self):
        assert TEACHER_MAX_FILE_SIZE > 0
        assert STUDENT_MAX_FILE_SIZE > 0
        assert OCR_MAX_IMAGE_SIZE > 0

    def test_teacher_max_gt_student_max(self):
        """Teachers should have higher upload limit than students."""
        assert TEACHER_MAX_FILE_SIZE > STUDENT_MAX_FILE_SIZE

    def test_allowed_extensions(self):
        assert "pdf" in TEACHER_ALLOWED_EXTENSIONS
        assert "docx" in TEACHER_ALLOWED_EXTENSIONS
        assert "pdf" in STUDENT_ALLOWED_EXTENSIONS
        assert "jpg" in STUDENT_ALLOWED_EXTENSIONS
        assert "png" in STUDENT_ALLOWED_EXTENSIONS

    def test_student_extensions_superset(self):
        """Student extensions should include teacher extensions plus images."""
        assert TEACHER_ALLOWED_EXTENSIONS.issubset(STUDENT_ALLOWED_EXTENSIONS)

    def test_defaults_positive(self):
        assert DEFAULT_AI_QUERIES_LIMIT > 0
        assert DEFAULT_LEADERBOARD_LIMIT > 0
        assert EMBEDDING_BATCH_SIZE > 0
        assert RATE_LIMIT_WINDOW_SECONDS > 0
        assert DEFAULT_TEST_TOTAL_MARKS > 0
        assert DEFAULT_TEST_DURATION_MINUTES > 0

    def test_pdf_colors_are_hex(self):
        for color in [PDF_PRIMARY_COLOR, PDF_MUTED_COLOR, PDF_LABEL_COLOR, PDF_GRID_COLOR, PDF_HIGHLIGHT_BG]:
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB format

    def test_grade_thresholds_descending(self):
        """Thresholds must be in descending order for compute_grade to work."""
        thresholds = [t[0] for t in GRADE_THRESHOLDS]
        assert thresholds == sorted(thresholds, reverse=True)
