"""
Credit Routes - API endpoints for credit management
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import logging

from ..services.credit_service import (
    get_user_credits,
    get_transaction_history
)
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/api/credits", tags=["credits"])
logger = logging.getLogger(__name__)


@router.get("/balance")
async def get_balance(user = Depends(get_current_user)):
    """
    Get current credit balance for authenticated user

    Returns:
        {
            "user_id": "uuid",
            "credits": 123,
            "updated_at": "2024-11-28T..."
        }
    """
    try:
        balance = await get_user_credits(user.id)

        if "error" in balance and balance["credits"] == 0:
            raise HTTPException(status_code=500, detail=balance["error"])

        return balance

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_balance: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve balance")


@router.get("/history")
async def get_history(
    limit: Optional[int] = 50,
    user = Depends(get_current_user)
):
    """
    Get transaction history for authenticated user

    Query params:
        limit: Maximum number of transactions (default 50, max 100)

    Returns:
        [
            {
                "id": "uuid",
                "type": "usage_basic",
                "credits_change": -5,
                "credits_after": 45,
                "description": "Processed 5 images",
                "created_at": "2024-11-28T..."
            },
            ...
        ]
    """
    try:
        # Validate limit
        if limit > 100:
            limit = 100

        history = await get_transaction_history(user.id, limit)

        return {
            "user_id": user.id,
            "total_transactions": len(history),
            "transactions": history
        }

    except Exception as e:
        logger.error(f"Error in get_history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")
