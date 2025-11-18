from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ....database import DB
from ....dependencies import get_current_user, require_permissions
from ....schemas import LitigationBulkInsertRequest, LitigationCase
from ....services.notifications import notify_litigation_uploaded

router = APIRouter(prefix="/litigation-cases", tags=["litigation"])


@router.get("", response_model=List[LitigationCase])
async def list_cases(user=Depends(get_current_user)) -> List[LitigationCase]:
    rows = [record for record in DB.litigation_cases.values() if record["user_id"] == user["id"]]
    return [LitigationCase(**row) for row in rows]


@router.post("/bulk", response_model=List[LitigationCase])
async def bulk_insert(payload: LitigationBulkInsertRequest, user=Depends(require_permissions(["litigation.create"]))):
    created: List[LitigationCase] = []
    for case in payload.cases:
        record = DB.insert(
            DB.litigation_cases,
            {
                "user_id": user["id"],
                "docket_number": case.docket_number,
                "case_name": case.case_name,
                "status": case.status,
                "amount": case.amount,
                "created_at": datetime.utcnow(),
            },
        )
        created.append(LitigationCase(**record))
    notify_litigation_uploaded(user["id"], len(created))
    return created


@router.delete("/{case_id}")
async def delete_case(case_id: str, user=Depends(require_permissions(["litigation.delete"]))):
    record = DB.litigation_cases.get(case_id)
    if not record or record["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Case not found")
    DB.delete(DB.litigation_cases, case_id)
