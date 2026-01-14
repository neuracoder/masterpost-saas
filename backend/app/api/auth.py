"""
Authentication API for Masterpost.io Credit System
Handles user signup, login, logout, and profile management
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from ..core.supabase import supabase_admin, supabase_anon

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict
    expires_in: int

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    created_at: str

class MessageResponse(BaseModel):
    message: str

# =====================================================
# HELPER FUNCTIONS
# =====================================================

async def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Dependency to get current user from JWT token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        # Verify JWT token with Supabase
        user_response = supabase_anon.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return {
            "id": user_response.user.id,
            "email": user_response.user.email,
            "created_at": user_response.user.created_at
        }
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# =====================================================
# AUTHENTICATION ENDPOINTS
# =====================================================

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """
    Register a new user and automatically create user_credits record
    """
    try:
        # Create user with Supabase Auth
        auth_response = supabase_anon.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name or ""
                }
            }
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=400,
                detail="Failed to create user. Email may already be registered."
            )

        user_id = auth_response.user.id

        # Create user_credits record with 10 free credits
        credits_result = supabase_admin.table('user_credits').insert({
            'user_id': user_id,
            'credits': 10  # FREE tier: 10 credits
        }).execute()

        # Record the free pack transaction
        supabase_admin.table('transactions').insert({
            'user_id': user_id,
            'type': 'free_pack',
            'credits_change': 10,
            'credits_after': 10,
            'description': 'Free 10 credits pack on signup'
        }).execute()

        logger.info(f"New user registered: {request.email} with 10 free credits")

        return AuthResponse(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            expires_in=auth_response.session.expires_in or 3600,
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "full_name": request.full_name or ""
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login existing user with email and password
    """
    try:
        # Sign in with Supabase Auth
        auth_response = supabase_anon.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not auth_response.user or not auth_response.session:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Get user metadata
        full_name = auth_response.user.user_metadata.get("full_name", "")

        return AuthResponse(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            expires_in=auth_response.session.expires_in or 3600,
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "full_name": full_name
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user (invalidate session)
    """
    try:
        # Supabase handles token invalidation
        supabase_anon.auth.sign_out()

        return MessageResponse(message="Logged out successfully")

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Return success anyway since logout should not fail
        return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile information
    """
    try:
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=current_user.get("full_name", ""),
            created_at=current_user.get("created_at", "")
        )

    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user information")
