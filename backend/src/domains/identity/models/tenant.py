"""Tenant model for school-scoped configuration and enterprise controls."""
import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=True)
    plan_tier = Column(String(50), default="basic")
    max_students = Column(Integer, default=100)
    ai_daily_limit = Column(Integer, default=50)
    is_active = Column(Integer, default=1)

    saml_enabled = Column(Boolean, nullable=False, default=False, server_default="false")
    saml_entity_id = Column(String(500), nullable=True)
    saml_metadata_url = Column(String(1000), nullable=True)
    saml_metadata_xml = Column(Text, nullable=True)
    saml_idp_entity_id = Column(String(500), nullable=True)
    saml_idp_sso_url = Column(String(1000), nullable=True)
    saml_idp_slo_url = Column(String(1000), nullable=True)
    saml_x509_cert = Column(Text, nullable=True)
    saml_attribute_email = Column(String(255), nullable=False, default="email", server_default="email")
    saml_attribute_name = Column(String(255), nullable=False, default="full_name", server_default="full_name")

    data_retention_days = Column(Integer, nullable=False, default=365, server_default="365")
    export_retention_days = Column(Integer, nullable=False, default=30, server_default="30")

    logo_url = Column(String(1000), nullable=True)
    primary_color = Column(String(7), nullable=True, default="#4f46e5")
    secondary_color = Column(String(7), nullable=True, default="#10b981")
    accent_color = Column(String(7), nullable=True, default="#f59e0b")
    font_family = Column(String(100), nullable=True, default="Inter")
    theme_style = Column(String(50), nullable=True, default="modern")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="tenant", lazy="dynamic")
