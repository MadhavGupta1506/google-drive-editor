from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.google_photos import list_albums, list_google_photos, create_album, upload_photo_to_album
from app.utils.jwt_utils import verify_jwt_token
from app.utils.google_oauth import refresh_google_access_token
from app.utils.token_storage import get_user_tokens, update_user_access_token, user_has_tokens
from pydantic import BaseModel
from typing import Optional
import httpx


router = APIRouter(prefix="/google_photos", tags=["google_photos"])
security = HTTPBearer() 

@router.get("/albums")
async def get_albums(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Verify JWT token
        payload = verify_jwt_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token")
        
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        # Check if Google tokens exist
        if not user_has_tokens(email):
            raise HTTPException(status_code=403, detail="Google Photos not linked. Please authenticate first.")
        
        # Get tokens
        tokens = get_user_tokens(email)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        # Call Google Photos API
        print(f"Using access token: {access_token}")  
        albums_data = list_albums(access_token)
        
        # Handle expired token - refresh and retry
        if "error" in albums_data:
            try:
                new_token = refresh_google_access_token(refresh_token)
                if not new_token or "access_token" not in new_token:
                    raise HTTPException(status_code=401, detail="Failed to refresh access token. Please re-authenticate.")
                
                access_token = new_token["access_token"]
                update_user_access_token(email, access_token)
                albums_data = list_albums(access_token)
                
                # If still error after refresh
                if "error" in albums_data:
                    raise HTTPException(status_code=500, detail=f"Google Photos API error: {albums_data['error']}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")
        
        return albums_data
        
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Missing token data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/photos")
async def get_photos(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """List photos from Google Photos"""
    try:
        payload = verify_jwt_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token")
        
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        if not user_has_tokens(email):
            raise HTTPException(status_code=403, detail="Google Photos not linked. Please authenticate first.")
        
        tokens = get_user_tokens(email)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        photos_data = list_google_photos(access_token)
        
        if "error" in photos_data:
            try:
                new_token = refresh_google_access_token(refresh_token)
                if not new_token or "access_token" not in new_token:
                    raise HTTPException(status_code=401, detail="Failed to refresh access token. Please re-authenticate.")
                
                access_token = new_token["access_token"]
                update_user_access_token(email, access_token)
                photos_data = list_google_photos(access_token)
                
                if "error" in photos_data:
                    raise HTTPException(status_code=500, detail=f"Google Photos API error: {photos_data['error']}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")
        
        return photos_data
        
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Missing token data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class CreateAlbumRequest(BaseModel):
    album_title: str


@router.post("/albums")
async def create_new_album(
    album_request: CreateAlbumRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = verify_jwt_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token")
        
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        if not user_has_tokens(email):
            raise HTTPException(status_code=403, detail="Google Photos not linked. Please authenticate first.")
        
        tokens = get_user_tokens(email)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        album_data = create_album(access_token, album_request.album_title, refresh_token, email)
        
        if "error" in album_data:
            raise HTTPException(status_code=500, detail=f"Google Photos API error: {album_data.get('error', 'Unknown error')}")
        
        return album_data
        
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Missing token data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    album_id: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload a photo to Google Photos, optionally to a specific album"""
    try:
        payload = verify_jwt_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token")
        
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        if not user_has_tokens(email):
            raise HTTPException(status_code=403, detail="Google Photos not linked. Please authenticate first.")
        
        tokens = get_user_tokens(email)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # Read file bytes
        photo_bytes = await file.read()
        
        # Upload photo
        result = upload_photo_to_album(
            access_token=access_token,
            photo_bytes=photo_bytes,
            filename=file.filename,
            album_id=album_id,
            refresh_token=refresh_token,
            email=email
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Google Photos API error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
