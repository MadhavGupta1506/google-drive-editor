import requests
from app.config import settings

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


def create_album(access_token: str, album_title: str) -> dict:
    """Create a new album in Google Photos"""
    try:
        import pdb; pdb.set_trace()
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
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
