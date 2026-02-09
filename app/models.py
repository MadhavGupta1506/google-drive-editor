from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenResponse(BaseModel):
    """JWT token response model"""
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """User information from Google"""
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None


class JWTPayload(BaseModel):
    """JWT token payload"""
    email: EmailStr
    provider: str
    iat: int
    exp: int


class LoginURLResponse(BaseModel):
    """Login URL response"""
    url: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[dict] = None

class DriveFile(BaseModel):
    """Google Drive File model"""
    id: str
    name: str
    mimeType: str
    parents: Optional[list[str]] = None
class DriveFolderResponse(BaseModel):
    """Google Drive Folder creation response model"""
    id: str
    name: str
    mimeType: str
class UploadFileResponse(BaseModel):
    """Google Drive File upload response model"""
    id: str
    name: str
    mimeType: str
class DriveFilesListResponse(BaseModel):
    """Google Drive Files List response model"""
    files: list[DriveFile]
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[dict] = None


class CreateMeetRequest(BaseModel):
    summary: str
    start_time: Optional[str] = None  # ISO format: "2026-02-10T14:00:00"
    duration_minutes: int = 60
    description: Optional[str] = None