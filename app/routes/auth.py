from fastapi import APIRouter, HTTPException
from typing import Optional
from app.models import TokenResponse, LoginURLResponse, ErrorResponse
from app.utils import (
    get_google_auth_url,
    exchange_code_for_token,
    get_user_info,
    create_jwt_token
)
from app.utils.database import token_db
from app.utils.encryption import token_encryptor
from app.utils.token_storage import save_user_tokens, delete_user_tokens
from app.utils.jwt_utils import verify_jwt_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login/google", response_model=LoginURLResponse)
async def login_google():
    auth_data = get_google_auth_url()
    return {"url": auth_data["url"]}


@router.get("/google/callback")
async def auth_google_callback(code: str, state: Optional[str] = None):

    token_data = exchange_code_for_token(code)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    print(f"\n=== TOKEN DATA ===")
    print(f"Token response: {token_data}")
    print(f"Scope in token: {token_data.get('scope', 'NO SCOPE IN RESPONSE')}")
    print(f"==================\n")

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")

    user_data = get_user_info(access_token)

    if not user_data or "email" not in user_data:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    email = user_data["email"]
    
    # Store encrypted tokens in database
    if refresh_token:
        success = save_user_tokens(email, access_token, refresh_token)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save tokens")

    app_jwt = create_jwt_token({
        "email": email,
        "provider": "google"
    })

    return TokenResponse(
        access_token=app_jwt,
        token_type="bearer"
    )


security = HTTPBearer()


@router.delete("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = security):
    """Logout user and delete stored tokens"""
    try:
        payload = verify_jwt_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token")
        
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        # Delete user tokens from database
        success = delete_user_tokens(email)
        
        return {
            "message": "Successfully logged out",
            "tokens_deleted": success
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

