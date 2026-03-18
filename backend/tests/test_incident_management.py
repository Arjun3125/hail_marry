"""Tests for incident management service."""
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from src.domains.administrative.services.incident_management import (
    list_incidents,
    list_incident_routes,
    get_incident_detail,
    resolve_incident,
)


class TestListIncidents:
    """Test incident listing."""

    def test_empty_returns_empty(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        result = list_incidents(db, uuid4())
        assert result == []


class TestListIncidentRoutes:
    """Test incident route listing."""

    def test_empty_returns_empty(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        result = list_incident_routes(db, uuid4())
        assert result == []


class TestGetIncidentDetail:
    """Test incident detail retrieval."""

    def test_nonexistent_raises(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="Incident not found"):
            get_incident_detail(db, uuid4(), uuid4())


class TestResolveIncident:
    """Test incident resolution."""

    def test_resolve_nonexistent_raises(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="Incident not found"):
            resolve_incident(db, uuid4(), uuid4(), uuid4(), "Fixed")
