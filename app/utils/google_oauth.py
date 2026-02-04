import secrets
import requests
from urllib.parse import quote_plus
from typing import Dict, Optional
from app.config import settings


def get_google_auth_url() -> Dict[str, str]:
    state = secrets.token_urlsafe(16)
    encoded_redirect_uri = quote_plus(settings.GOOGLE_REDIRECT_URI) 
    scopes = "%20".join(settings.GOOGLE_SCOPES)
    
    google_auth_url = (
        f"{settings.GOOGLE_AUTH_URL}"
        f"?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={encoded_redirect_uri}"
        f"&scope={scopes}"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&state={state}"
    )
    
    return {
        "url": google_auth_url,
        "state": state
    }


def exchange_code_for_token(code: str) -> Optional[Dict]:
    token_payload = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    try:
        response = requests.post(
            settings.GOOGLE_TOKEN_URL, 
            data=token_payload, 
            timeout=10
        )
        token_data = response.json()
        
        if "access_token" in token_data:
            return token_data
        return None
    except requests.RequestException:
        return None


def get_user_info(access_token: str) -> Optional[Dict]:
    try:
        response = requests.get(
            settings.GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        user_data = response.json()
        
        if "email" in user_data:
            return user_data
        return None
    except requests.RequestException:
        return None

def refresh_google_access_token(refresh_token: str) -> Optional[Dict]:
    try:
        response = requests.post(
            settings.GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=10
        )
        token_data = response.json()
        if "access_token" in token_data:
            return token_data
        return None
    except requests.RequestException:
        return None


def list_drive_files(access_token: str) -> Optional[Dict]:
    try:
        response = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "pageSize": 10,
                "fields": "files(id,name,mimeType)"
            },
            timeout=10
        )
        return response.json()
    except requests.RequestException:
        return None