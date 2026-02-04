from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Dict, Optional
from app.config import settings


def create_jwt_token(data: dict) -> str:
    """
    Create a JWT token with expiration
    
    Args:
        data: Dictionary containing the payload data
        
    Returns:
        Encoded JWT token as string
    """
    payload = data.copy()
    payload.update({
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    })
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Optional[Dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
