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
google_tokens_store = {}


@router.get("/login/google", response_model=LoginURLResponse)
async def login_google():
    auth_data = get_google_auth_url()
    return {"url": auth_data["url"]}


@router.get("/google/callback")
async def auth_google_callback(code: str, state: Optional[str] = None):

    token_data = exchange_code_for_token(code)

    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")

    user_data = get_user_info(access_token)

    if not user_data or "email" not in user_data:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    email = user_data["email"]
    print(refresh_token)
    if refresh_token:
        google_tokens_store[email] = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    app_jwt = create_jwt_token({
        "email": email,
        "provider": "google"
    })

    return TokenResponse(
        access_token=app_jwt,
        token_type="bearer"
    )