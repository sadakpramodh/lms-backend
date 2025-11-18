"""Shared Pydantic schemas for request/response bodies."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field, HttpUrl


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(..., description="Access token TTL in seconds")


class UserBase(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_enabled: bool = True


class Profile(BaseModel):
    user_id: str
    full_name: str
    avatar_url: Optional[HttpUrl] = None
    is_enabled: bool = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None


class AlertSettings(BaseModel):
    user_id: str
    email_alerts: bool = True
    sms_alerts: bool = False


class AlertSettingsUpdate(BaseModel):
    email_alerts: Optional[bool] = None
    sms_alerts: Optional[bool] = None


class AuthSignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class AuthSignInRequest(BaseModel):
    email: EmailStr
    password: str


class AuthRefreshRequest(BaseModel):
    refresh_token: str


class DisputeFileMetadata(BaseModel):
    filename: str
    url: HttpUrl
    size_bytes: int


class Dispute(BaseModel):
    id: str
    user_id: str
    title: str
    status: Literal["open", "pending", "closed"] = "open"
    amount: float
    created_at: datetime
    documents: List[DisputeFileMetadata] = []


class DisputeCreate(BaseModel):
    title: str
    amount: float


class DisputeUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[Literal["open", "pending", "closed"]] = None
    amount: Optional[float] = None


class LitigationCase(BaseModel):
    id: str
    user_id: str
    docket_number: str
    case_name: str
    status: Literal["draft", "filed", "closed"]
    amount: float
    created_at: datetime


class LitigationCaseInsert(BaseModel):
    docket_number: str
    case_name: str
    status: Literal["draft", "filed", "closed"] = "draft"
    amount: float


class LitigationBulkInsertRequest(BaseModel):
    cases: List[LitigationCaseInsert]


class PermissionUpdate(BaseModel):
    user_id: str
    permissions: List[str]


class AccessToggleRequest(BaseModel):
    user_id: str
    is_enabled: bool


class AdminUserSummary(BaseModel):
    profile: Profile
    permissions: List[str]
    last_sign_in: Optional[datetime] = None


class DocumentUploadResponse(BaseModel):
    documents: List[DisputeFileMetadata]


class HealthResponse(BaseModel):
    status: str = "ok"
