import requests
from app.config import settings
from app.utils.google_oauth import refresh_google_access_token
from app.utils.token_storage import update_user_access_token

def list_google_photos(access_token: str,page_size: int = 10) -> dict:
    try:
        response = requests.get(
            f"{settings.GOOGLE_PHOTOS_BASE}/mediaItems",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
            params={"pageSize": page_size}
        )
        print(access_token)
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
    
def list_albums(access_token: str,page_size: int = 10) -> dict:
    # import pdb; pdb.set_trace()
    try:
        response = requests.get(
            f"{settings.GOOGLE_PHOTOS_BASE}/albums",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"pageSize": page_size},
            timeout=10  
        )
        print(f"Albums API Response Status: {response.status_code}")
        print(f"Albums API Response: {response.text[:500]}")
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


def create_album(access_token: str, album_title: str, refresh_token: str = None, email: str = None) -> dict:
    """Create a new album in Google Photos with automatic token refresh"""
    try:
        response = requests.post(
            f"{settings.GOOGLE_PHOTOS_BASE}/albums",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={"album": {"title": album_title}},
            timeout=10
        )
        print(f"Create Album Response Status: {response.status_code}")
        print(f"Create Album Response: {response.text}")
        result = response.json()
        
        # If error and we have refresh token, try refreshing
        if "error" in result and refresh_token and email:
            new_token = refresh_google_access_token(refresh_token)
            if new_token and "access_token" in new_token:
                access_token = new_token["access_token"]
                update_user_access_token(email, access_token)
                
                # Retry with new token
                response = requests.post(
                    f"{settings.GOOGLE_PHOTOS_BASE}/albums",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={"album": {"title": album_title}},
                    timeout=10
                )
                result = response.json()
        
        return result
    except requests.RequestException as e:
        return {"error": str(e)}


def upload_photo_to_album(access_token: str, photo_bytes: bytes, filename: str, album_id: str = None, refresh_token: str = None, email: str = None) -> dict:
    """Upload a photo to Google Photos, optionally to a specific album"""
    try:
        # Step 1: Upload the raw bytes to get an upload token
        upload_response = requests.post(
            f"{settings.GOOGLE_PHOTOS_BASE}/uploads",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/octet-stream",
                "X-Goog-Upload-File-Name": filename,
                "X-Goog-Upload-Protocol": "raw"
            },
            data=photo_bytes,
            timeout=30
        )
        
        if upload_response.status_code != 200:
            return {"error": f"Upload failed with status {upload_response.status_code}: {upload_response.text}"}
        
        upload_token = upload_response.text
        
        # Step 2: Create media item with the upload token
        new_media_item = {
            "description": filename,
            "simpleMediaItem": {
                "uploadToken": upload_token
            }
        }
        
        # Add album ID if provided
        create_payload = {"newMediaItems": [new_media_item]}
        if album_id:
            create_payload["albumId"] = album_id
        
        create_response = requests.post(
            f"{settings.GOOGLE_PHOTOS_BASE}/mediaItems:batchCreate",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=create_payload,
            timeout=10
        )
        
        result = create_response.json()
        
        # Handle token refresh if needed
        if "error" in result and refresh_token and email:
            new_token = refresh_google_access_token(refresh_token)
            if new_token and "access_token" in new_token:
                access_token = new_token["access_token"]
                update_user_access_token(email, access_token)
                
                # Retry the entire upload process with new token
                return upload_photo_to_album(access_token, photo_bytes, filename, album_id, refresh_token, email)
        
        return result
        
    except requests.RequestException as e:
        return {"error": str(e)}
