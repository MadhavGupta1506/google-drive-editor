from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models import TokenResponse, LoginURLResponse, ErrorResponse
from app.utils import (
    get_google_auth_url,
    exchange_code_for_token,
    get_user_info,
    create_jwt_token
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login/google", response_model=LoginURLResponse)
async def login_google():
    """
    Generate Google OAuth login URL
    
    Returns:
        Dictionary containing the Google OAuth authorization URL
    """
    auth_data = get_google_auth_url()
    return {"url": auth_data["url"]}


@router.get("/google/callback")
async def auth_google_callback(code: str, state: Optional[str] = None):
    """
    Handle Google OAuth callback
    
    Args:
        code: Authorization code from Google
        state: State parameter for CSRF protection
        
    Returns:
        JWT token for the authenticated user
    """
    # Exchange code for access token
    token_data = exchange_code_for_token(code)
    
    if not token_data:
        raise HTTPException(
            status_code=400,
            detail="Failed to get access token from Google"
        )
    
    access_token = token_data["access_token"]
    
    # Get user information
    user_data = get_user_info(access_token)
    
    if not user_data:
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch user info from Google"
        )
    
    # Create JWT token
    app_jwt = create_jwt_token({
        "email": user_data["email"],
        "provider": "google"
    })
    
    return TokenResponse(
        access_token=app_jwt,
        token_type="bearer"
    )
