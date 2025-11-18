from __future__ import annotations

from fastapi import APIRouter, Depends

from ....database import DB
from ....dependencies import get_current_user
from ....schemas import AlertSettings, AlertSettingsUpdate, Profile, ProfileUpdate

router = APIRouter(prefix="/me", tags=["profile"])


@router.get("/profile", response_model=Profile)
async def get_profile(user=Depends(get_current_user)) -> Profile:
    return Profile(**DB.profiles[user["id"]])


@router.put("/profile", response_model=Profile)
async def update_profile(payload: ProfileUpdate, user=Depends(get_current_user)) -> Profile:
    record = DB.profiles[user["id"]]
    record.update({k: v for k, v in payload.dict(exclude_unset=True).items()})
    return Profile(**record)


@router.get("/alerts", response_model=AlertSettings)
async def get_alert_settings(user=Depends(get_current_user)) -> AlertSettings:
    return AlertSettings(**DB.alert_settings[user["id"]])


@router.put("/alerts", response_model=AlertSettings)
async def update_alert_settings(payload: AlertSettingsUpdate, user=Depends(get_current_user)) -> AlertSettings:
    record = DB.alert_settings[user["id"]]
    record.update({k: v for k, v in payload.dict(exclude_unset=True).items()})
    return AlertSettings(**record)
