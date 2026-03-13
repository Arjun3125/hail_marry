"""Document viewing routes for citation linking."""
from __future__ import annotations

import mimetypes
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import FileResponse

from auth.dependencies import get_current_user
from database import get_db
from models.document import Document
from models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/documents", tags=["Documents"])


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


@router.get("/{document_id}/view")
async def view_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Serve a stored document for citation click-through."""
    doc_uuid = _parse_uuid(document_id, "document_id")
    doc = db.query(Document).filter(
        Document.id == doc_uuid,
        Document.tenant_id == current_user.tenant_id,
    ).first()
    if not doc or not doc.storage_path:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = Path(doc.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file is missing.")

    media_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        path=str(file_path),
        media_type=media_type or "application/octet-stream",
        filename=doc.file_name,
    )
