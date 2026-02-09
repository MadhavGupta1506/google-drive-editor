from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.google_meet import create_meet_link
from app.utils.jwt_utils import verify_jwt_token
from app.utils.token_storage import get_user_tokens, user_has_tokens
from app.models import CreateMeetRequest
from datetime import datetime


router = APIRouter(prefix="/google_meet", tags=["google_meet"])
security = HTTPBearer()




@router.post("/create")
async def create_meeting(
    meet_request: CreateMeetRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a Google Meet link"""
    try:
        payload = verify_jwt_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token")
        
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        if not user_has_tokens(email):
            raise HTTPException(status_code=403, detail="Google Calendar not linked. Please authenticate first.")
        
        tokens = get_user_tokens(email)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # Parse start_time if provided
        start_time = None
        if meet_request.start_time:
            try:
                start_time = datetime.fromisoformat(meet_request.start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_time format. Use ISO format: 2026-02-10T14:00:00")
        
        # Create Meet link
        result = create_meet_link(
            access_token=access_token,
            summary=meet_request.summary,
            start_time=start_time,
            duration_minutes=meet_request.duration_minutes,
            description=meet_request.description,
            refresh_token=refresh_token,
            email=email
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Google Calendar API error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
