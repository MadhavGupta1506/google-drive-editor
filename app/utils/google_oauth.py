import json
import secrets
import requests
from urllib.parse import quote_plus
from typing import Dict, Optional
from app.config import settings


def get_google_auth_url() -> Dict[str, str]:
    state = secrets.token_urlsafe(16)
    encoded_redirect_uri = quote_plus(settings.GOOGLE_REDIRECT_URI)
    # Properly encode scopes - each scope is URL encoded, then joined with space (%20)
    encoded_scopes = "%20".join([quote_plus(scope) for scope in settings.GOOGLE_SCOPES])
    
    google_auth_url = (
        f"{settings.GOOGLE_AUTH_URL}"
        f"?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={encoded_redirect_uri}"
        f"&scope={encoded_scopes}"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&include_granted_scopes=true"
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
            settings.GOOGLE_DRIVE_API_URL,
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

def upload_file_to_drive(access_token: str, file_name: str, file_bytes: bytes, mime_type: str,parent_folder_id: str | None = None) -> Optional[Dict]:
    try:
        metadata = {
            'name': file_name
        }
        if parent_folder_id:
            metadata["parents"] = [parent_folder_id]
        files = {
            'data': ('metadata', json.dumps(metadata), 'application/json'),
            'file': (file_name, file_bytes, mime_type)
        }
        response = requests.post(
            settings.GOOGLE_DRIVE_API_URL + "?uploadType=multipart",
            headers={"Authorization": f"Bearer {access_token}"},
            files=files,
            timeout=10
        )
        return response.json()
    except requests.RequestException:
        return None
    
def create_drive_folder(access_token: str, folder_name: str, parent_id: str | None = None):
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        metadata["parents"] = [parent_id]
    try:
        response = requests.post(
            settings.GOOGLE_DRIVE_API_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=metadata,
            timeout=10
        )
        return response.json()
    except requests.RequestException:
        return None