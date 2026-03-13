"""Tests for HyDE query transform."""
import pytest
from ai.hyde import should_use_hyde, generate_hypothetical_answer, hyde_transform


def test_short_query_no_hyde():
    assert should_use_hyde("what is DNA") is False


def test_single_word_no_hyde():
    assert should_use_hyde("photosynthesis") is False


def test_complex_question_uses_hyde():
    assert should_use_hyde("Why is photosynthesis important for the carbon cycle and how does it relate to climate change") is True


def test_compare_question_uses_hyde():
    assert should_use_hyde("Compare mitosis and meiosis processes") is True


def test_explain_question_uses_hyde():
    assert should_use_hyde("Explain the relationship between pressure and volume in gases") is True


def test_multi_clause_uses_hyde():
    assert should_use_hyde("What are the causes and effects of deforestation on biodiversity") is True


def test_hypothetical_answer_qa():
    result = generate_hypothetical_answer("How does gravity work", "qa")
    assert "gravity" in result.lower()
    assert len(result) > 50


def test_hypothetical_answer_quiz():
    result = generate_hypothetical_answer("Newton's laws", "quiz")
    assert "quiz" in result.lower() or "Newton" in result


def test_hypothetical_answer_study_guide():
    result = generate_hypothetical_answer("Cell biology", "study_guide")
    assert "study guide" in result.lower()


def test_hyde_transform_short_passthrough():
    result = hyde_transform("what is DNA", "qa")
    assert result == "what is DNA"  # Should pass through for short queries


def test_hyde_transform_complex():
    result = hyde_transform("Explain the relationship between pressure and volume in gases", "qa")
    assert len(result) > len("Explain the relationship between pressure and volume in gases")
