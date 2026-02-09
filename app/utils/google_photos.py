import requests
from app.config import settings
from app.utils.google_oauth import refresh_google_access_token
from app.routes.auth import google_tokens_store

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
                google_tokens_store[email]["access_token"] = access_token
                
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
