"""
Authentication Dependencies - FastAPI dependencies for protected routes
"""

import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from typing import Optional

logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    logger.warning("Supabase credentials not configured for auth")
    supabase: Optional[Client] = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    logger.info("✅ Supabase client initialized for auth dependencies")

# Bearer token security scheme
security = HTTPBearer()


class User:
    """Simple user object"""
    def __init__(self, id: str, email: str, user_metadata: dict = None):
        self.id = id
        self.email = email
        self.user_metadata = user_metadata or {}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Usage:
        @router.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"user_id": user.id}

    Raises:
        HTTPException 401: If token is invalid or expired
    """
    if not supabase:
        logger.error("Supabase not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )

    token = credentials.credentials

    try:
        # Verify token with Supabase Auth
        response = supabase.auth.get_user(token)

        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_data = response.user

        logger.debug(f"✅ Authenticated user: {user_data.email} ({user_data.id[:8]}...)")

        return User(
            id=user_data.id,
            email=user_data.email,
            user_metadata=user_data.user_metadata or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Optional authentication dependency - returns None if no token provided

    Usage:
        @router.get("/public-or-protected")
        async def route(user = Depends(get_optional_user)):
            if user:
                return {"authenticated": True, "user_id": user.id}
            else:
                return {"authenticated": False}
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
