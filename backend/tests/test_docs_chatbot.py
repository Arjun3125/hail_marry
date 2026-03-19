"""Tests for docs-as-AI chatbot."""
import pytest
from src.domains.platform.services.docs_chatbot import (
    FAQ_DATABASE, generate_support_response, get_docs_categories,
    get_faqs_by_category, search_docs_faq,
)


def test_faq_database_not_empty():
    assert len(FAQ_DATABASE) >= 7


def test_search_tenant_creation():
    result = search_docs_faq("how to create a tenant")
    assert result is not None
    assert result["category"] == "onboarding"


def test_search_add_students():
    result = search_docs_faq("how to add students")
    assert result is not None
    assert "CSV" in result["answer"] or "admission" in result["answer"].lower()


def test_search_no_match():
    result = search_docs_faq("xyzzy irrelevant query")
    assert result is None


def test_categories():
    cats = get_docs_categories()
    assert "onboarding" in cats
    assert "ai" in cats
    assert "fees" in cats


def test_faqs_by_category():
    faqs = get_faqs_by_category("ai")
    assert len(faqs) >= 1


def test_support_response_match():
    response = generate_support_response("how to set up ai")
    assert response["source"] == "faq"
    assert response["confidence"] > 0


def test_support_response_fallback():
    response = generate_support_response("xyzzy nonsense query")
    assert response["source"] == "fallback"
    assert response["confidence"] == 0.0
