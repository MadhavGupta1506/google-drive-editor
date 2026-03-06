from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.routes import auth_router, google_drive_router,google_photos_router, google_calendar_router
import os

security = HTTPBearer()

app = FastAPI(
    title="Google OAuth Authentication API",
    description="API for Google OAuth authentication with JWT token generation",
    version="1.0.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(google_drive_router)
app.include_router(google_photos_router)
app.include_router(google_calendar_router)

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")


@app.get("/")
async def root():
    """Serve the frontend index.html"""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
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
