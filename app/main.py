from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.routes import auth_router, google_drive_router,google_photos_router, google_calendar_router

security = HTTPBearer()

app = FastAPI(
    title="Google OAuth Authentication API",
    description="API for Google OAuth authentication with JWT token generation",
    version="1.0.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

# Include routers
app.include_router(auth_router)
app.include_router(google_drive_router)
app.include_router(google_photos_router)
app.include_router(google_calendar_router)


@app.get("/")
async def root():
    return {
        "message": "Google OAuth Authentication API",
        "endpoints": {
            "login": "/auth/login/google",
            "callback": "/auth/google/callback",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
