"""Add enterprise SSO, compliance, and incident-management tables.

Revision ID: 20260306_0002
Revises: 20260303_0001
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


revision: str = "20260306_0002"
down_revision: Union[str, None] = "20260303_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "tenants" in inspector.get_table_names():
        tenant_columns = [
            ("saml_enabled", sa.Boolean(), sa.text("false")),
            ("saml_entity_id", sa.String(length=500), None),
            ("saml_metadata_url", sa.String(length=1000), None),
            ("saml_metadata_xml", sa.Text(), None),
            ("saml_idp_entity_id", sa.String(length=500), None),
            ("saml_idp_sso_url", sa.String(length=1000), None),
            ("saml_idp_slo_url", sa.String(length=1000), None),
            ("saml_x509_cert", sa.Text(), None),
            ("saml_attribute_email", sa.String(length=255), sa.text("'email'")),
            ("saml_attribute_name", sa.String(length=255), sa.text("'full_name'")),
            ("data_retention_days", sa.Integer(), sa.text("365")),
            ("export_retention_days", sa.Integer(), sa.text("30")),
        ]
        for name, column_type, default in tenant_columns:
            if _has_column(inspector, "tenants", name):
                continue
            kwargs = {"nullable": True}
            if default is not None:
                kwargs["server_default"] = default
            op.add_column("tenants", sa.Column(name, column_type, **kwargs))

    if "compliance_exports" not in inspector.get_table_names():
        op.create_table(
            "compliance_exports",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("export_type", sa.String(length=50), nullable=False),
            sa.Column("scope_type", sa.String(length=50), nullable=False),
            sa.Column("scope_user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("format", sa.String(length=20), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("file_path", sa.Text(), nullable=True),
            sa.Column("file_size", sa.Integer(), nullable=True),
            sa.Column("checksum", sa.String(length=128), nullable=True),
            sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["requested_by"], ["users.id"]),
            sa.ForeignKeyConstraint(["scope_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_compliance_exports_requested_by"), "compliance_exports", ["requested_by"], unique=False)
        op.create_index(op.f("ix_compliance_exports_scope_user_id"), "compliance_exports", ["scope_user_id"], unique=False)
        op.create_index(op.f("ix_compliance_exports_tenant_id"), "compliance_exports", ["tenant_id"], unique=False)

    if "deletion_requests" not in inspector.get_table_names():
        op.create_table(
            "deletion_requests",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("target_user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("resolution_note", sa.Text(), nullable=True),
            sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["requested_by"], ["users.id"]),
            sa.ForeignKeyConstraint(["target_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_deletion_requests_requested_by"), "deletion_requests", ["requested_by"], unique=False)
        op.create_index(op.f("ix_deletion_requests_target_user_id"), "deletion_requests", ["target_user_id"], unique=False)
        op.create_index(op.f("ix_deletion_requests_tenant_id"), "deletion_requests", ["tenant_id"], unique=False)

    if "incident_routes" not in inspector.get_table_names():
        op.create_table(
            "incident_routes",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("channel_type", sa.String(length=50), nullable=False),
            sa.Column("target", sa.String(length=1000), nullable=False),
            sa.Column("secret", sa.String(length=255), nullable=True),
            sa.Column("severity_filter", sa.String(length=50), nullable=False),
            sa.Column("escalation_channel_type", sa.String(length=50), nullable=True),
            sa.Column("escalation_target", sa.String(length=1000), nullable=True),
            sa.Column("escalation_after_minutes", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_incident_routes_tenant_id"), "incident_routes", ["tenant_id"], unique=False)

    if "incidents" not in inspector.get_table_names():
        op.create_table(
            "incidents",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("alert_code", sa.String(length=100), nullable=False),
            sa.Column("severity", sa.String(length=30), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("trace_id", sa.String(length=255), nullable=True),
            sa.Column("source_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("acknowledged_by", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_notified_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["acknowledged_by"], ["users.id"]),
            sa.ForeignKeyConstraint(["resolved_by"], ["users.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_incidents_alert_code"), "incidents", ["alert_code"], unique=False)
        op.create_index(op.f("ix_incidents_tenant_id"), "incidents", ["tenant_id"], unique=False)
        op.create_index(op.f("ix_incidents_trace_id"), "incidents", ["trace_id"], unique=False)

    if "incident_events" not in inspector.get_table_names():
        op.create_table(
            "incident_events",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("incident_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("event_type", sa.String(length=50), nullable=False),
            sa.Column("detail", sa.Text(), nullable=True),
            sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_incident_events_incident_id"), "incident_events", ["incident_id"], unique=False)
        op.create_index(op.f("ix_incident_events_tenant_id"), "incident_events", ["tenant_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    for table_name in ["incident_events", "incidents", "incident_routes", "deletion_requests", "compliance_exports"]:
        if table_name in inspector.get_table_names():
            op.drop_table(table_name)

    if "tenants" in inspector.get_table_names():
        for column_name in [
            "export_retention_days",
            "data_retention_days",
            "saml_attribute_name",
            "saml_attribute_email",
            "saml_x509_cert",
            "saml_idp_slo_url",
            "saml_idp_sso_url",
            "saml_idp_entity_id",
            "saml_metadata_xml",
            "saml_metadata_url",
            "saml_entity_id",
            "saml_enabled",
        ]:
            if _has_column(inspector, "tenants", column_name):
                op.drop_column("tenants", column_name)
