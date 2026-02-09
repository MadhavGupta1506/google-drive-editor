import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI")
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 10080
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "tokens.db")  
    
    # Google OAuth URLs
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://accounts.google.com/o/oauth2/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v1/userinfo"
    GOOGLE_PHOTOS_BASE = "https://photoslibrary.googleapis.com/v1"
    GOOGLE_DRIVE_API_URL: str = "https://www.googleapis.com/drive/v3/files"
    GOOGLE_CALENDAR_API_URL: str = "https://www.googleapis.com/calendar/v3"
    
    
    # OAuth Scopes
    GOOGLE_SCOPES: list = [
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/photoslibrary",
        "https://www.googleapis.com/auth/photoslibrary.appendonly",
        "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    
    ]


settings = Settings()
