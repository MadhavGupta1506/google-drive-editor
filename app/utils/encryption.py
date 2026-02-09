from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


class TokenEncryption:
    """Encrypt and decrypt sensitive tokens"""
    
    def __init__(self):
        # Generate a key from the JWT secret for consistency
        # In production, use a separate encryption key
        key = hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, token: str) -> str:
        """Encrypt a token"""
        if not token:
            return ""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt a token"""
        if not encrypted_token:
            return ""
        return self.cipher.decrypt(encrypted_token.encode()).decode()


# Global encryption instance
token_encryptor = TokenEncryption()
