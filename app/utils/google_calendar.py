import requests
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
from app.utils.google_oauth import refresh_google_access_token
from app.utils.token_storage import update_user_access_token


def create_meet_link(
    access_token: str,
    summary: str,
    start_time: Optional[datetime] = None,
    duration_minutes: int = 60,
    description: Optional[str] = None,
    refresh_token: str = None,
    email: str = None
) -> dict:
    """
    Create a Google Meet link via Google Calendar API
    
    Args:
        access_token: Google OAuth access token
        summary: Meeting title/summary
        start_time: Meeting start time (defaults to now)
        duration_minutes: Meeting duration in minutes (default 60)
        description: Meeting description (optional)
        refresh_token: Refresh token for auto-refresh
        email: User email for token update
    
    Returns:
        Dictionary with meeting details including Google Meet link
    """
    try:
        # Default to current time if not provided
        if start_time is None:
            start_time = datetime.utcnow()
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Format times in RFC3339 format
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        
        # Create event with Google Meet conference
        event_body = {
            "summary": summary,
            "description": description or "",
            "start": {
                "dateTime": start_str,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_str,
                "timeZone": "UTC"
            },
            "conferenceData": {
                "createRequest": {
                    "requestId": f"meet-{int(datetime.utcnow().timestamp())}",
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    }
                }
            }
        }
        
        response = requests.post(
            f"{settings.GOOGLE_CALENDAR_API_URL}/calendars/primary/events",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            params={"conferenceDataVersion": 1},
            json=event_body,
            timeout=10
        )
        
        result = response.json()
        
        # Handle token refresh if needed
        if response.status_code == 401 and refresh_token and email:
            new_token = refresh_google_access_token(refresh_token)
            if new_token and "access_token" in new_token:
                access_token = new_token["access_token"]
                update_user_access_token(email, access_token)
                
                # Retry with new token
                response = requests.post(
                    f"{settings.GOOGLE_CALENDAR_API_URL}/calendars/primary/events",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    params={"conferenceDataVersion": 1},
                    json=event_body,
                    timeout=10
                )
                result = response.json()
        
        # Check for errors
        if "error" in result:
            return {"error": result.get("error", {}).get("message", "Unknown error")}
        
        # Extract Meet link
        meet_link = None
        if "conferenceData" in result and "entryPoints" in result["conferenceData"]:
            for entry in result["conferenceData"]["entryPoints"]:
                if entry.get("entryPointType") == "video":
                    meet_link = entry.get("uri")
                    break
        
        return {
            "event_id": result.get("id"),
            "summary": result.get("summary"),
            "start_time": result.get("start", {}).get("dateTime"),
            "end_time": result.get("end", {}).get("dateTime"),
            "meet_link": meet_link,
            "html_link": result.get("htmlLink"),
            "status": result.get("status")
        }
        
    except requests.RequestException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def create_event(
    access_token: str,
    summary: str,
    start_time: Optional[datetime] = None,
    duration_minutes: int = 60,
    description: Optional[str] = None,
    refresh_token: str = None,
    email: str = None
) -> dict:
    """
    Create a regular calendar event (without Google Meet)
    
    Args:
        access_token: Google OAuth access token
        summary: Event title/summary
        start_time: Event start time (defaults to now)
        duration_minutes: Event duration in minutes (default 60)
        description: Event description (optional)
        refresh_token: Refresh token for auto-refresh
        email: User email for token update
    
    Returns:
        Dictionary with event details
    """
    try:
        # Default to current time if not provided
        if start_time is None:
            start_time = datetime.utcnow()
        
        # Ensure start_time is a datetime object
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if start_time.tzinfo:
                # Convert to UTC naive datetime
                start_time = start_time.replace(tzinfo=None)
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Format times in RFC3339 format
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Create event without Google Meet conference
        event_body = {
            "summary": summary,
            "description": description or "",
            "start": {
                "dateTime": start_str,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_str,
                "timeZone": "UTC"
            }
        }
        
        response = requests.post(
            f"{settings.GOOGLE_CALENDAR_API_URL}/calendars/primary/events",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=event_body,
            timeout=10
        )
        
        result = response.json()
        
        # Handle token refresh if needed
        if response.status_code == 401 and refresh_token and email:
            new_token = refresh_google_access_token(refresh_token)
            if new_token and "access_token" in new_token:
                access_token = new_token["access_token"]
                update_user_access_token(email, access_token)
                
                # Retry with new token
                response = requests.post(
                    f"{settings.GOOGLE_CALENDAR_API_URL}/calendars/primary/events",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=event_body,
                    timeout=10
                )
                result = response.json()
        
        # Check for errors
        if "error" in result:
            return {"error": result.get("error", {}).get("message", "Unknown error")}
        
        return {
            "event_id": result.get("id"),
            "summary": result.get("summary"),
            "start_time": result.get("start", {}).get("dateTime"),
            "end_time": result.get("end", {}).get("dateTime"),
            "html_link": result.get("htmlLink"),
            "status": result.get("status"),
            "description": result.get("description")
        }
        
    except requests.RequestException as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def list_upcoming_events(access_token: str, max_results: int = 10) -> dict:
    """List upcoming calendar events"""
    try:
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        response = requests.get(
            f"{settings.GOOGLE_CALENDAR_API_URL}/calendars/primary/events",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "timeMin": now,
                "maxResults": max_results,
                "singleEvents": True,
                "orderBy": "startTime"
            },
            timeout=10
        )
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}