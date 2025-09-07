"""
Session management utilities
"""
from fastapi import Request, Response
import uuid
import hashlib
from typing import Optional

COOKIE_NAME = "session_id"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days

def get_or_create_session_id(request: Request, response: Response) -> str:
    """Get existing session ID from cookie or create a new one"""
    session_id = request.cookies.get(COOKIE_NAME)
    
    if not session_id:
        # Generate new session ID
        session_id = generate_session_id()
        # Set cookie
        response.set_cookie(
            key=COOKIE_NAME,
            value=session_id,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax"
        )
    
    return session_id

def get_session_id(request: Request) -> Optional[str]:
    """Get session ID from cookie"""
    return request.cookies.get(COOKIE_NAME)

def generate_session_id() -> str:
    """Generate a unique session ID"""
    unique_id = str(uuid.uuid4())
    return hashlib.sha256(unique_id.encode()).hexdigest()[:32]

def check_ownership(session_id: str, owner_session_id: Optional[str]) -> bool:
    """Check if the current session owns the resource"""
    if not owner_session_id:
        return False
    return session_id == owner_session_id