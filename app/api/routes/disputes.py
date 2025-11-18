from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ....database import DB
from ....dependencies import get_current_user, require_permissions
from ....schemas import Dispute, DisputeCreate, DisputeUpdate, DocumentUploadResponse
from ....services.notifications import notify_dispute_created
from ....services.storage import save_files

router = APIRouter(prefix="/disputes", tags=["disputes"])


@router.get("", response_model=List[Dispute])
async def list_disputes(user=Depends(get_current_user)) -> List[Dispute]:
    rows = [record for record in DB.disputes.values() if record["user_id"] == user["id"]]
    return [Dispute(**row) for row in rows]


@router.post("", response_model=Dispute)
async def create_dispute(payload: DisputeCreate, user=Depends(require_permissions(["disputes.create"]))):
    record = DB.insert(
        DB.disputes,
        {
            "user_id": user["id"],
            "title": payload.title,
            "status": "open",
            "amount": payload.amount,
            "created_at": datetime.utcnow(),
            "documents": [],
        },
    )
    notify_dispute_created(record)
    return Dispute(**record)


@router.put("/{dispute_id}", response_model=Dispute)
async def update_dispute(dispute_id: str, payload: DisputeUpdate, user=Depends(require_permissions(["disputes.update"]))):
    record = DB.disputes.get(dispute_id)
    if not record or record["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Dispute not found")
    record.update({k: v for k, v in payload.dict(exclude_unset=True).items()})
    return Dispute(**record)


@router.delete("/{dispute_id}")
async def delete_dispute(dispute_id: str, user=Depends(require_permissions(["disputes.delete"]))):
    record = DB.disputes.get(dispute_id)
    if not record or record["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Dispute not found")
    DB.delete(DB.disputes, dispute_id)


@router.post("/{dispute_id}/documents", response_model=DocumentUploadResponse)
async def upload_documents(
    dispute_id: str,
    files: List[UploadFile] = File(..., description="Up to 50 files (500MB each)"),
    user=Depends(get_current_user),
) -> DocumentUploadResponse:
    record = DB.disputes.get(dispute_id)
    if not record or record["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Dispute not found")

    saved = save_files(user["id"], files)
    record.setdefault("documents", []).extend([doc.dict() for doc in saved])
    return DocumentUploadResponse(documents=saved)
