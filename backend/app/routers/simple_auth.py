"""
Simple Authentication Router - Email + Access Code
Replaces complex Supabase auth with SQLite-based authentication
"""
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from ..database_sqlite.sqlite_client import sqlite_client
from ..services.email_service import send_free_trial_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

class AccessRequest(BaseModel):
    email: EmailStr
    access_code: str

class AccessResponse(BaseModel):
    success: bool
    email: str
    credits: int
    message: str

class CreateUserRequest(BaseModel):
    email: EmailStr
    initial_credits: int = 50

class CreateUserResponse(BaseModel):
    success: bool
    email: str
    access_code: str
    credits: int
    message: str

@router.post("/validate", response_model=AccessResponse)
async def validate_access(request: AccessRequest):
    """Validate email and access code"""

    is_valid = sqlite_client.validate_access(request.email, request.access_code)

    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or access code"
        )

    credits = sqlite_client.get_user_credits(request.email)

    return AccessResponse(
        success=True,
        email=request.email,
        credits=credits,
        message="Access granted"
    )

@router.post("/create-user", response_model=CreateUserResponse)
async def create_user(request: CreateUserRequest):
    """Create a new user (for testing/admin use)"""

    user = sqlite_client.create_user(request.email, request.initial_credits)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="User already exists or could not be created"
        )

    return CreateUserResponse(
        success=True,
        email=user['email'],
        access_code=user['access_code'],
        credits=user['credits'],
        message="User created successfully"
    )

@router.get("/credits")
async def get_credits(x_user_email: str = Header(...)):
    """Get user's current credit balance"""
    credits = sqlite_client.get_user_credits(x_user_email)
    return {"email": x_user_email, "credits": credits}

@router.get("/stats")
async def get_user_stats(email: str):
    """
    Get user statistics including credits and processing counts

    Args:
        email: User email (query parameter)

    Returns:
        User stats or 404 if user not found
    """
    try:
        stats = sqlite_client.get_user_stats(email)

        if not stats:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return {
            "success": True,
            "credits_available": stats["credits"],
            "basic_processed": stats["basic_processed"],
            "qwen_processed": stats["qwen_processed"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting stats for {email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get user stats"
        )


# ==================== FREE TRIAL ENDPOINT ====================

class FreeTrialRequest(BaseModel):
    email: EmailStr


class FreeTrialResponse(BaseModel):
    success: bool
    email: str
    access_code: str
    credits: int
    message: str


@router.post("/free-trial", response_model=FreeTrialResponse)
async def create_free_trial(
    request: FreeTrialRequest,
    client_request: Request
):
    """
    Create user with 10 free credits
    Only allows 1 free trial per unique email
    """
    try:
        email = request.email.lower().strip()

        # Log IP for abuse monitoring
        client_ip = client_request.client.host
        logger.info(f"Free trial request from {email} - IP: {client_ip}")

        # 1. Check if email already exists
        existing_user = sqlite_client.get_user_by_email(email)
        if existing_user:
            logger.warning(f"Free trial already used by {email}")
            raise HTTPException(
                status_code=400,
                detail="This email has already been used for a free trial. Please purchase credits or use a different email."
            )

        # 2. Create user with 10 credits
        access_code = sqlite_client.create_user(email=email, credits=10)

        if not access_code:
            logger.error(f"Failed to create free trial user: {email}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create free trial account. Please try again."
            )

        logger.info(f"✅ Free trial user created: {email} with code {access_code}")

        # 3. Send welcome email
        try:
            email_sent = await send_free_trial_email(
                to_email=email,
                access_code=access_code,
                credits=10
            )
            if email_sent:
                logger.info(f"📧 Free trial email sent to {email}")
            else:
                logger.warning(f"⚠️ Email service returned False for {email}")
        except Exception as email_error:
            logger.error(f"❌ Failed to send free trial email to {email}: {email_error}")
            # Don't fail the request if email fails
            # User can still use the access_code

        # 4. Return success response
        return FreeTrialResponse(
            success=True,
            email=email,
            access_code=access_code,
            credits=10,
            message="Free trial activated! Check your email for the access code."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating free trial: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )


# Dependency for protected routes
async def get_current_user_email(
    x_user_email: Optional[str] = Header(None)
) -> str:
    """Extract user email from header - use this for protected routes"""
    if not x_user_email:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide x-user-email header."
        )
    return x_user_email