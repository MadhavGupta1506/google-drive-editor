from typing import Optional, Dict
from app.utils.database import token_db
from app.utils.encryption import token_encryptor


def get_user_tokens(email: str) -> Optional[Dict[str, str]]:
    """Get decrypted tokens for a user"""
    encrypted_tokens = token_db.get_tokens(email)
    if not encrypted_tokens:
        return None
    
    return {
        "access_token": token_encryptor.decrypt(encrypted_tokens["access_token"]),
        "refresh_token": token_encryptor.decrypt(encrypted_tokens["refresh_token"])
    }


def save_user_tokens(email: str, access_token: str, refresh_token: str) -> bool:
    """Save encrypted tokens for a user"""
    encrypted_access = token_encryptor.encrypt(access_token)
    encrypted_refresh = token_encryptor.encrypt(refresh_token)
    return token_db.save_tokens(email, encrypted_access, encrypted_refresh)


def update_user_access_token(email: str, access_token: str) -> bool:
    """Update only the access token for a user"""
    encrypted_access = token_encryptor.encrypt(access_token)
    return token_db.update_access_token(email, encrypted_access)


def user_has_tokens(email: str) -> bool:
    """Check if user has stored tokens"""
    return token_db.user_exists(email)


def delete_user_tokens(email: str) -> bool:
    """Delete user tokens"""
    return token_db.delete_tokens(email)
