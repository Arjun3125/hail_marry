"""Tests for report card PDF generation — grading integration."""
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from constants import compute_grade


class TestReportCardGrading:
    """Verify grading logic used by report card matches constants."""

    def test_grade_distribution(self):
        test_cases = [
            (100, "A+"), (95, "A+"), (90, "A+"),
            (89, "A"), (85, "A"), (80, "A"),
            (79, "B+"), (75, "B+"), (70, "B+"),
            (69, "B"), (65, "B"), (60, "B"),
            (59, "C"), (55, "C"), (50, "C"),
            (49, "D"), (45, "D"), (40, "D"),
            (39, "F"), (25, "F"), (10, "F"), (0, "F"),
        ]
        for score, expected in test_cases:
            result = compute_grade(score)
            assert result == expected, f"compute_grade({score}) = {result}, expected {expected}"

    def test_report_card_imports_from_constants(self):
        """report_card.py should import compute_grade from constants, not define its own."""
        import inspect
        from services import report_card
        source = inspect.getsource(report_card)
        assert "from constants import" in source
        assert "compute_grade" in source

    def test_pdf_uses_constant_colors(self):
        """Verify the module references PDF_PRIMARY_COLOR, not hardcoded hex."""
        import inspect
        from services import report_card
        source = inspect.getsource(report_card)
        assert "PDF_PRIMARY_COLOR" in source
        assert "PDF_MUTED_COLOR" in source
