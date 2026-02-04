from fastapi import FastAPI
from app.routes import auth_router

app = FastAPI(
    title="Google OAuth Authentication API",
    description="API for Google OAuth authentication with JWT token generation",
    version="1.0.0"
)

# Include routers
app.include_router(auth_router)


@app.get("/")
async def root():
    """Root endpoint"""
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
