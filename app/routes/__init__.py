from .auth import router as auth_router
from .google_drive import router as google_drive_router
from .google_photos import router as google_photos_router
from .google_calendar import router as google_calendar_router
__all__ = ["auth_router", "google_drive_router","google_photos_router", "google_calendar_router"]