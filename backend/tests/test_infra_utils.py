"""Tests for infra utilities — logging, startup checks, pagination."""
import pytest
from unittest.mock import MagicMock


class TestStructuredLogging:
    def test_configure_does_not_raise(self):
        from services.structured_logging import configure_structured_logging
        configure_structured_logging(service_name="test-service")


class TestStartupChecks:
    def test_collect_status_returns_dict(self):
        from services.startup_checks import collect_dependency_status
        result = collect_dependency_status("api")
        assert isinstance(result, dict)
        assert "ready" in result

    def test_enforce_in_testing_mode(self):
        import os
        os.environ["TESTING"] = "true"
        from services.startup_checks import enforce_startup_dependencies
        try:
            enforce_startup_dependencies("api")
        except SystemExit:
            pass


class TestPagination:
    def test_default_page_size(self):
        import inspect
        from utils.pagination import paginate
        sig = inspect.signature(paginate)
        assert sig.parameters["page_size"].default == 25

    def test_paginate_empty_query(self):
        from utils.pagination import paginate
        query = MagicMock()
        query.count.return_value = 0
        query.offset.return_value.limit.return_value.all.return_value = []
        result = paginate(query, page=1, page_size=10)
        assert result["total"] == 0
        assert result["items"] == []
        assert result["page"] == 1
        assert result["total_pages"] == 1

    def test_paginate_clamps_page(self):
        from utils.pagination import paginate
        query = MagicMock()
        query.count.return_value = 5
        query.offset.return_value.limit.return_value.all.return_value = []
        result = paginate(query, page=-1, page_size=10)
        assert result["page"] == 1

    def test_paginate_clamps_page_size(self):
        from utils.pagination import paginate
        query = MagicMock()
        query.count.return_value = 5
        query.offset.return_value.limit.return_value.all.return_value = []
        result = paginate(query, page=1, page_size=200, max_page_size=100)
        assert result["page_size"] == 100
