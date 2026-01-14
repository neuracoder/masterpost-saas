"""
Supabase Authentication Integration for MASTERPOST.IO V2.0
Real user authentication with JWT token validation
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from supabase import create_client, Client

from ..core.config import settings
from ..database.supabase_client import supabase_client
from ..models.user_models import User, PlanType

logger = logging.getLogger(__name__)

# Security scheme for bearer token
security = HTTPBearer()

class SupabaseAuth:
    """
    Handles Supabase authentication and user management
    """

    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY  # Use anon key for auth operations
        )
        self.jwt_secret = self._get_jwt_secret()

    def _get_jwt_secret(self) -> str:
        """Get JWT secret from Supabase project settings"""
        # In production, this should be retrieved from environment or Supabase settings
        # For now, we'll extract from service key
        try:
            decoded = jwt.decode(
                settings.SUPABASE_SERVICE_KEY,
                options={"verify_signature": False}
            )
            # The secret is typically the same across the project
            # In production, get this from Supabase dashboard -> Settings -> API
            return "your-jwt-secret"  # Replace with actual JWT secret
        except Exception as e:
            logger.warning(f"Could not extract JWT secret: {e}")
            return "fallback-secret"

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Supabase JWT token and return user claims

        Args:
            token: JWT token from Authorization header

        Returns:
            User claims if valid, None if invalid
        """
        try:
            # Verify token with Supabase
            user = self.supabase.auth.get_user(token)

            if user and user.user:
                return {
                    "user_id": user.user.id,
                    "email": user.user.email,
                    "role": user.user.role,
                    "aud": user.user.aud,
                    "exp": user.user.user_metadata.get("exp"),
                }

            return None

        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None

    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current authenticated user from token

        Args:
            token: JWT token

        Returns:
            User object if authenticated, None otherwise
        """
        try:
            claims = await self.verify_token(token)
            if not claims:
                return None

            user_id = claims["user_id"]

            # Get user profile from database
            user = await supabase_client.get_user_profile(user_id)

            # If user profile doesn't exist, create it
            if not user:
                user_data = {
                    "id": user_id,
                    "email": claims["email"],
                    "plan": "free",
                    "status": "active"
                }
                user = await supabase_client.create_user_profile(user_data)

            return user

        except Exception as e:
            logger.error(f"Get current user failed: {str(e)}")
            return None

    async def create_user(self, email: str, password: str, full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create new user with Supabase Auth

        Args:
            email: User email
            password: User password
            full_name: Optional full name

        Returns:
            User data if successful
        """
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name or ""
                    }
                }
            })

            if response.user:
                return {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "confirmed": response.user.email_confirmed_at is not None
                }

            return None

        except Exception as e:
            logger.error(f"User creation failed: {str(e)}")
            return None

    async def sign_in(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Sign in user and return tokens

        Args:
            email: User email
            password: User password

        Returns:
            Auth response with tokens
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user and response.session:
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "confirmed": response.user.email_confirmed_at is not None
                    }
                }

            return None

        except Exception as e:
            logger.error(f"Sign in failed: {str(e)}")
            return None

    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token

        Args:
            refresh_token: Refresh token

        Returns:
            New tokens if successful
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_token)

            if response.session:
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }

            return None

        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return None

    async def sign_out(self, token: str) -> bool:
        """
        Sign out user

        Args:
            token: Access token

        Returns:
            True if successful
        """
        try:
            # Set token for this operation
            self.supabase.postgrest.auth(token)
            self.supabase.auth.sign_out()
            return True

        except Exception as e:
            logger.error(f"Sign out failed: {str(e)}")
            return False

    async def reset_password(self, email: str) -> bool:
        """
        Send password reset email

        Args:
            email: User email

        Returns:
            True if successful
        """
        try:
            self.supabase.auth.reset_password_email(email)
            return True

        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            return False

# Create singleton instance
supabase_auth = SupabaseAuth()

# Dependency functions for FastAPI

async def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract token from Authorization header"""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

async def get_current_user(token: str = Depends(get_token_from_header)) -> User:
    """
    Get current authenticated user - REQUIRED dependency

    Raises HTTP 401 if not authenticated
    """
    user = await supabase_auth.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:
    """
    Get current authenticated user - OPTIONAL dependency

    Returns None if not authenticated (for public endpoints)
    """
    if not credentials or not credentials.credentials:
        return None

    user = await supabase_auth.get_current_user(credentials.credentials)
    return user

async def get_current_user_id(user: User = Depends(get_current_user)) -> str:
    """Get current user ID from authenticated user"""
    return user.id

async def require_plan(required_plan: PlanType):
    """
    Create a dependency that requires a specific plan or higher

    Args:
        required_plan: Minimum required plan

    Returns:
        Dependency function
    """
    async def check_plan(user: User = Depends(get_current_user)) -> User:
        plan_hierarchy = {
            PlanType.FREE: 0,
            PlanType.PRO: 1,
            PlanType.BUSINESS: 2
        }

        user_level = plan_hierarchy.get(user.plan, 0)
        required_level = plan_hierarchy.get(required_plan, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {required_plan.value} plan or higher"
            )

        return user

    return check_plan

# Pre-configured plan requirements
require_pro_plan = require_plan(PlanType.PRO)
require_business_plan = require_plan(PlanType.BUSINESS)

async def validate_api_key(api_key: str) -> Dict[str, Any]:
    """
    Validate API key for programmatic access

    Args:
        api_key: API key string

    Returns:
        User info if valid

    Raises:
        HTTPException if invalid
    """
    user_info = await supabase_client.validate_api_key(api_key)

    if not user_info or not user_info.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return user_info

async def get_user_from_api_key(api_key: str = None) -> Optional[User]:
    """
    Get user from API key (for API endpoints)

    Args:
        api_key: API key from header or query param

    Returns:
        User if valid API key
    """
    if not api_key:
        return None

    try:
        user_info = await validate_api_key(api_key)
        return await supabase_client.get_user_profile(user_info["user_id"])
    except Exception:
        return None