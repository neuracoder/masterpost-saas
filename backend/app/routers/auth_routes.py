"""
Authentication routes for MASTERPOST.IO V2.0
User registration, login, logout, password reset
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from ..auth.supabase_auth import supabase_auth, get_current_user, get_current_user_optional
from ..models.user_models import User, PlanType
from ..database.supabase_client import supabase_client

router = APIRouter()

# Request/Response Models
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict
    message: str

class MessageResponse(BaseModel):
    message: str

# =====================================================
# AUTHENTICATION ENDPOINTS
# =====================================================

@router.post("/signup", response_model=AuthResponse)
async def sign_up(request: SignUpRequest):
    """
    Register new user account
    """
    try:
        # Create user with Supabase Auth
        auth_result = await supabase_auth.create_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )

        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )

        # Sign in to get tokens
        sign_in_result = await supabase_auth.sign_in(request.email, request.password)

        if not sign_in_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User created but failed to sign in"
            )

        return AuthResponse(
            access_token=sign_in_result["access_token"],
            refresh_token=sign_in_result["refresh_token"],
            user=sign_in_result["user"],
            message="Account created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """
    Sign in existing user
    """
    try:
        result = await supabase_auth.sign_in(request.email, request.password)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        return AuthResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            user=result["user"],
            message="Signed in successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign in failed: {str(e)}"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token
    """
    try:
        result = await supabase_auth.refresh_token(request.refresh_token)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        return {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "message": "Token refreshed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/signout", response_model=MessageResponse)
async def sign_out(current_user: User = Depends(get_current_user)):
    """
    Sign out current user
    """
    try:
        # Note: Token is handled by the get_current_user dependency
        success = await supabase_auth.sign_out("")  # Token already validated

        return MessageResponse(message="Signed out successfully")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign out failed: {str(e)}"
        )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: PasswordResetRequest):
    """
    Send password reset email
    """
    try:
        success = await supabase_auth.reset_password(request.email)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send reset email"
            )

        return MessageResponse(message="Password reset email sent")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )

# =====================================================
# USER PROFILE ENDPOINTS
# =====================================================

@router.get("/me", response_model=dict)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile with usage statistics
    """
    try:
        # Get comprehensive dashboard stats
        dashboard_stats = await supabase_client.get_user_dashboard_stats(current_user.id)

        return {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "plan": current_user.plan,
                "status": current_user.status,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None
            },
            "dashboard_stats": dashboard_stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None

@router.patch("/me", response_model=MessageResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile
    """
    try:
        updates = {}
        if request.full_name is not None:
            updates["full_name"] = request.full_name

        if not updates:
            return MessageResponse(message="No changes to update")

        success = await supabase_client.update_user_profile(current_user.id, updates)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )

        return MessageResponse(message="Profile updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

# =====================================================
# PLAN AND BILLING ENDPOINTS
# =====================================================

@router.get("/plans", response_model=list)
async def get_available_plans():
    """
    Get all available subscription plans
    """
    try:
        plans = await supabase_client.get_all_plan_features()
        return plans

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plans: {str(e)}"
        )

class UpgradePlanRequest(BaseModel):
    plan: PlanType
    stripe_payment_method_id: Optional[str] = None

@router.post("/upgrade", response_model=MessageResponse)
async def upgrade_plan(
    request: UpgradePlanRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Upgrade user plan (mock implementation - integrate with Stripe)
    """
    try:
        # Validate plan upgrade
        if request.plan == current_user.plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already on this plan"
            )

        # Mock upgrade - in production, integrate with Stripe
        if request.plan in [PlanType.PRO, PlanType.BUSINESS]:
            if not request.stripe_payment_method_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment method required for paid plans"
                )

        # Update user plan
        success = await supabase_client.update_user_profile(
            current_user.id,
            {"plan": request.plan.value}
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upgrade plan"
            )

        return MessageResponse(message=f"Successfully upgraded to {request.plan.value} plan")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plan upgrade failed: {str(e)}"
        )

# =====================================================
# API KEY MANAGEMENT (Business Plan Only)
# =====================================================

@router.get("/api-keys", response_model=list)
async def get_api_keys(current_user: User = Depends(get_current_user)):
    """
    Get user's API keys (Business plan only)
    """
    if current_user.plan != PlanType.BUSINESS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API keys are only available for Business plan users"
        )

    try:
        # Get API keys from database (without showing full keys)
        result = supabase_client.supabase.table('api_keys')\
            .select('id, key_name, key_prefix, last_used_at, requests_count, is_active, created_at')\
            .eq('user_id', current_user.id)\
            .eq('is_active', True)\
            .execute()

        return result.data or []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API keys: {str(e)}"
        )

class CreateApiKeyRequest(BaseModel):
    key_name: str

@router.post("/api-keys", response_model=dict)
async def create_api_key(
    request: CreateApiKeyRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create new API key (Business plan only)
    """
    if current_user.plan != PlanType.BUSINESS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API keys are only available for Business plan users"
        )

    try:
        api_key = await supabase_client.create_api_key(current_user.id, request.key_name)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create API key"
            )

        return {
            "api_key": api_key,
            "message": "API key created successfully. Store this key securely - it won't be shown again.",
            "key_name": request.key_name
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"API key creation failed: {str(e)}"
        )

@router.delete("/api-keys/{key_id}", response_model=MessageResponse)
async def deactivate_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate API key
    """
    if current_user.plan != PlanType.BUSINESS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API keys are only available for Business plan users"
        )

    try:
        # Deactivate API key (soft delete)
        result = supabase_client.supabase.table('api_keys')\
            .update({"is_active": False})\
            .eq('id', key_id)\
            .eq('user_id', current_user.id)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return MessageResponse(message="API key deactivated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"API key deactivation failed: {str(e)}"
        )