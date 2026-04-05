"""Tests for compliance service."""
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from src.domains.administrative.services.compliance import (
    list_compliance_exports,
    create_deletion_request,
    resolve_deletion_request,
)


class TestListComplianceExports:
    """Test listing existing exports."""

    def test_empty_list(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        result = list_compliance_exports(db, uuid4())
        assert result == []


class TestCreateDeletionRequest:
    """Test data deletion request creation."""

    def test_creates_request(self):
        db = MagicMock()
        req = MagicMock()
        req.id = uuid4()
        req.status = "requested"
        db.refresh = MagicMock(return_value=None)
        # Mock the constructor to just return req
        create_deletion_request(
            db,
            tenant_id=uuid4(),
            requested_by=uuid4(),
            target_user_id=uuid4(),
            reason="GDPR right to erasure",
        )
        assert db.add.called
        assert db.commit.called


class TestResolveDeletionRequest:
    """Test deletion request resolution."""

    def test_resolve_nonexistent_raises(self):
        from fastapi import HTTPException

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            resolve_deletion_request(
                db,
                tenant_id=uuid4(),
                request_id=uuid4(),
                note="Completed",
            )
        assert exc_info.value.status_code == 404
