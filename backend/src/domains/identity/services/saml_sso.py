"""Tenant-scoped SAML SSO helpers."""
from __future__ import annotations

import base64
import json
from typing import Any
from urllib.parse import urlparse
from uuid import UUID
from defusedxml import ElementTree as ET

import httpx
from fastapi import HTTPException, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session

from config import settings
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User


NS = {
    "md": "urn:oasis:names:tc:SAML:2.0:metadata",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}


def get_tenant_for_saml(db: Session, tenant_key: str) -> Tenant:
    filters = [Tenant.domain == tenant_key]
    try:
        filters.append(Tenant.id == UUID(str(tenant_key)))
    except Exception:
        pass
    tenant = db.query(Tenant).filter(
        Tenant.is_active == 1,
        or_(*filters),
    ).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


def parse_idp_metadata(metadata_xml: str) -> dict[str, str | None]:
    root = ET.fromstring(metadata_xml)
    entity = root if root.tag.endswith("EntityDescriptor") else root.find("md:EntityDescriptor", NS)
    if entity is None:
        raise HTTPException(status_code=400, detail="Invalid SAML metadata.")

    idp = entity.find("md:IDPSSODescriptor", NS)
    if idp is None:
        raise HTTPException(status_code=400, detail="IDP SSO descriptor missing from SAML metadata.")

    def _binding_location(binding_suffix: str) -> str | None:
        for service in idp.findall("md:SingleSignOnService", NS) + idp.findall("md:SingleLogoutService", NS):
            binding = service.attrib.get("Binding", "")
            location = service.attrib.get("Location")
            if binding.endswith(binding_suffix):
                return location
        return None

    cert = idp.findtext(".//ds:X509Certificate", default=None, namespaces=NS)
    return {
        "entity_id": entity.attrib.get("entityID"),
        "sso_url": _binding_location("HTTP-Redirect") or _binding_location("HTTP-POST"),
        "slo_url": next((service.attrib.get("Location") for service in idp.findall("md:SingleLogoutService", NS)), None),
        "x509_cert": cert.strip() if cert else None,
    }


async def import_tenant_saml_metadata(tenant: Tenant, *, metadata_url: str | None = None, metadata_xml: str | None = None) -> dict[str, str | None]:
    xml = (metadata_xml or "").strip()
    if not xml and metadata_url:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(metadata_url)
            response.raise_for_status()
            xml = response.text

    if not xml:
        raise HTTPException(status_code=400, detail="SAML metadata XML or URL is required.")

    parsed = parse_idp_metadata(xml)
    tenant.saml_metadata_url = metadata_url or tenant.saml_metadata_url
    tenant.saml_metadata_xml = xml
    tenant.saml_idp_entity_id = parsed.get("entity_id")
    tenant.saml_idp_sso_url = parsed.get("sso_url")
    tenant.saml_idp_slo_url = parsed.get("slo_url")
    tenant.saml_x509_cert = parsed.get("x509_cert")
    if not tenant.saml_entity_id:
        tenant.saml_entity_id = f"{settings.auth.saml_sp_base_url.rstrip('/')}/api/auth/saml/{tenant.domain or tenant.id}/metadata"
    return parsed


def build_service_provider_metadata(tenant: Tenant) -> str:
    tenant_key = tenant.domain or str(tenant.id)
    base_url = settings.auth.saml_sp_base_url.rstrip("/")
    entity_id = tenant.saml_entity_id or f"{base_url}/api/auth/saml/{tenant_key}/metadata"
    acs_url = f"{base_url}/api/auth/saml/{tenant_key}/acs"
    return f"""<?xml version="1.0"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="{entity_id}">
  <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
    <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="{acs_url}" index="1"/>
  </md:SPSSODescriptor>
</md:EntityDescriptor>"""


def _prepare_onelogin_request(request: Request) -> dict[str, Any]:
    url = urlparse(str(request.url))
    return {
        "https": "on" if url.scheme == "https" else "off",
        "http_host": url.netloc,
        "server_port": url.port or (443 if url.scheme == "https" else 80),
        "script_name": request.url.path,
        "get_data": dict(request.query_params),
        "post_data": {},
    }


def _saml_settings_for_tenant(tenant: Tenant) -> dict[str, Any]:
    if not tenant.saml_idp_sso_url or not tenant.saml_x509_cert:
        raise HTTPException(status_code=400, detail="Tenant SAML metadata is incomplete.")

    tenant_key = tenant.domain or str(tenant.id)
    base_url = settings.auth.saml_sp_base_url.rstrip("/")
    entity_id = tenant.saml_entity_id or f"{base_url}/api/auth/saml/{tenant_key}/metadata"
    return {
        "strict": settings.auth.saml_strict,
        "debug": settings.auth.saml_debug,
        "sp": {
            "entityId": entity_id,
            "assertionConsumerService": {
                "url": f"{base_url}/api/auth/saml/{tenant_key}/acs",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        },
        "idp": {
            "entityId": tenant.saml_idp_entity_id,
            "singleSignOnService": {
                "url": tenant.saml_idp_sso_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "singleLogoutService": {
                "url": tenant.saml_idp_slo_url or tenant.saml_idp_sso_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": tenant.saml_x509_cert,
        },
    }


def _get_onelogin_auth(request: Request, tenant: Tenant):
    try:
        from onelogin.saml2.auth import OneLogin_Saml2_Auth
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=503, detail="python3-saml is not installed in this environment.") from exc

    return OneLogin_Saml2_Auth(_prepare_onelogin_request(request), old_settings=_saml_settings_for_tenant(tenant))


def saml_login_redirect(request: Request, tenant: Tenant, relay_state: str | None = None) -> str:
    if not tenant.saml_enabled:
        raise HTTPException(status_code=404, detail="SAML SSO is not enabled for this tenant.")
    auth = _get_onelogin_auth(request, tenant)
    return auth.login(return_to=relay_state)


def process_saml_acs(request: Request, tenant: Tenant, saml_response: str) -> dict[str, Any]:
    if not tenant.saml_enabled:
        raise HTTPException(status_code=404, detail="SAML SSO is not enabled for this tenant.")
    auth = _get_onelogin_auth(request, tenant)
    auth._request_data["post_data"] = {"SAMLResponse": saml_response}  # noqa: SLF001 - library request shim
    auth.process_response()
    errors = auth.get_errors()
    if errors:
        raise HTTPException(status_code=401, detail=f"SAML assertion validation failed: {', '.join(errors)}")
    if not auth.is_authenticated():
        raise HTTPException(status_code=401, detail="SAML authentication failed.")

    attributes = auth.get_attributes()
    email_attr = tenant.saml_attribute_email or "email"
    name_attr = tenant.saml_attribute_name or "full_name"
    email = (attributes.get(email_attr) or [auth.get_nameid()])[0]
    full_name = (attributes.get(name_attr) or [email])[0]
    return {
        "email": email,
        "full_name": full_name,
        "attributes": json.loads(json.dumps(attributes)),
        "name_id": auth.get_nameid(),
    }


def create_or_update_saml_user(db: Session, tenant: Tenant, saml_identity: dict[str, Any]) -> User:
    email = saml_identity["email"].strip().lower()
    user = db.query(User).filter(User.email == email, User.tenant_id == tenant.id).first()
    if not user:
        user = User(
            tenant_id=tenant.id,
            email=email,
            full_name=saml_identity.get("full_name") or email,
            role="student",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.full_name = saml_identity.get("full_name") or user.full_name
        db.commit()
    return user


def decode_saml_response_payload(value: str) -> str:
    try:
        return base64.b64decode(value).decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid SAMLResponse encoding.") from exc
