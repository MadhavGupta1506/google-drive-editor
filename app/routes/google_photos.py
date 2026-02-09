from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, requests, requests
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.google_photos import list_albums, list_google_photos, create_album
from app.utils.jwt_utils import verify_jwt_token
from app.utils.google_oauth import refresh_google_access_token
from app.routes.auth import google_tokens_store
from pydantic import BaseModel
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
        if email not in google_tokens_store:
            raise HTTPException(status_code=403, detail="Google Photos not linked. Please authenticate first.")
        
        # Get tokens
        access_token = google_tokens_store[email]["access_token"]
        refresh_token = google_tokens_store[email]["refresh_token"]
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
                google_tokens_store[email]["access_token"] = access_token
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
        
        if email not in google_tokens_store:
            raise HTTPException(status_code=403, detail="Google Photos not linked. Please authenticate first.")
        
        access_token = google_tokens_store[email]["access_token"]
        refresh_token = google_tokens_store[email]["refresh_token"]
        
        photos_data = list_google_photos(access_token)
        
        if "error" in photos_data:
            try:
                new_token = refresh_google_access_token(refresh_token)
                if not new_token or "access_token" not in new_token:
                    raise HTTPException(status_code=401, detail="Failed to refresh access token. Please re-authenticate.")
                
                access_token = new_token["access_token"]
                google_tokens_store[email]["access_token"] = access_token
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
