from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt_utils import verify_jwt_token as decode_jwt_token
from app.utils.google_oauth import list_drive_files, refresh_google_access_token
from app.routes.auth import google_tokens_store
from typing import Dict

router = APIRouter(prefix="/google_drive", tags=["google_drive"])
security = HTTPBearer()

@router.get("/drive/files")
async def get_drive_files(credentials: HTTPAuthorizationCredentials = Depends(security)):

    payload = decode_jwt_token(credentials.credentials)
    email = payload["email"]

    if email not in google_tokens_store:
        print(google_tokens_store)
        raise HTTPException(403, "Google Drive not linked")

    access_token = google_tokens_store[email]["access_token"]
    refresh_token = google_tokens_store[email]["refresh_token"]

    drive_data = list_drive_files(access_token)

    if "error" in drive_data:
        new_token = refresh_google_access_token(refresh_token)
        access_token = new_token["access_token"]
        google_tokens_store[email]["access_token"] = access_token
        drive_data = list_drive_files(access_token)

    return drive_data