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
