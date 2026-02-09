from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import DriveFilesListResponse, DriveFolderResponse, UploadFileResponse
from app.utils.jwt_utils import verify_jwt_token as decode_jwt_token
from app.utils.google_oauth import create_drive_folder, list_drive_files, refresh_google_access_token,upload_file_to_drive
from app.utils.token_storage import get_user_tokens, update_user_access_token, user_has_tokens
from typing import Dict

router = APIRouter(prefix="/google_drive", tags=["google_drive"])
security = HTTPBearer()

@router.get("/drive/files", response_model=DriveFilesListResponse)
async def get_drive_files(credentials: HTTPAuthorizationCredentials = Depends(security)):

    payload = decode_jwt_token(credentials.credentials)
    email = payload["email"]

    if not user_has_tokens(email):
        raise HTTPException(403, "Google Drive not linked")

    tokens = get_user_tokens(email)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    drive_data = list_drive_files(access_token)

    if "error" in drive_data:
        new_token = refresh_google_access_token(refresh_token)
        access_token = new_token["access_token"]
        update_user_access_token(email, access_token)
        drive_data = list_drive_files(access_token)

    return drive_data

@router.post("/upload", response_model=UploadFileResponse)
async def upload_to_drive(file:UploadFile=File(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_jwt_token(credentials.credentials)
    email = payload["email"]
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT")

    if not user_has_tokens(email):
        raise HTTPException(403, "Google Drive not linked")
    
    tokens = get_user_tokens(email)
    access_token = tokens["access_token"]
    file_byte=await file.read()
    result=upload_file_to_drive(access_token, file.filename, file_byte,file.content_type)
    return result

@router.post("/create_folder", response_model=DriveFolderResponse)
async def create_folder_route(folder_name: str, parent_id: str | None = None, credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_jwt_token(credentials.credentials)
    email = payload["email"]
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT")

    if not user_has_tokens(email):
        raise HTTPException(403, "Google Drive not linked")
    
    tokens = get_user_tokens(email)
    access_token = tokens["access_token"]
    result=create_drive_folder(access_token, folder_name, parent_id)
    return result
