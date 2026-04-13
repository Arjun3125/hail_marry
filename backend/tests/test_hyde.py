"""Tests for HyDE query transform."""
import pytest
from unittest.mock import AsyncMock
from src.infrastructure.vector_store.hyde import should_use_hyde, generate_hypothetical_answer, hyde_transform


@pytest.fixture(autouse=True)
def mock_llm_generate(monkeypatch):
    mock_provider = AsyncMock()
    
    async def fake_generate(prompt, **kwargs):
        if "quiz" in prompt.lower():
            return {"response": "A quiz on this topic involves Newton and definitions."}
        if "study_guide" in prompt.lower() or "study guide" in prompt.lower() or "syllabus" in prompt.lower() or "cell biology" in prompt.lower():
            return {"response": "This syllabus covers core principles and cell parts."}
        return {"response": "The answer involves gravity and mass and pulls things down. The relationship between these entities can completely change the structure of the system."}
        
    mock_provider.generate = fake_generate
    monkeypatch.setattr("src.infrastructure.vector_store.hyde.get_llm_provider", lambda: mock_provider)


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


@pytest.mark.asyncio
async def test_hypothetical_answer_qa():
    result = await generate_hypothetical_answer("How does gravity work", "qa")
    assert "gravity" in result.lower()
    assert len(result) > 40


@pytest.mark.asyncio
async def test_hypothetical_answer_quiz():
    result = await generate_hypothetical_answer("Newton's laws", "quiz")
    assert "quiz" in result.lower() or "Newton" in result


@pytest.mark.asyncio
async def test_hypothetical_answer_study_guide():
    result = await generate_hypothetical_answer("Cell biology", "study_guide")
    assert "syllabus" in result.lower() or "principles" in result.lower()


@pytest.mark.asyncio
async def test_hyde_transform_short_passthrough():
    result = await hyde_transform("what is DNA", "qa")
    assert result == "what is DNA"  # Should pass through for short queries


@pytest.mark.asyncio
async def test_hyde_transform_complex():
    result = await hyde_transform("Explain the relationship between pressure and volume in gases", "qa")
    assert len(result) > len("Explain the relationship between pressure and volume in gases")
