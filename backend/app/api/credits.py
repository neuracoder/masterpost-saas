"""
Credits API for Masterpost.io
Handles credit balance, usage, and transaction history
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

from ..core.supabase import supabase_admin
from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/credits", tags=["Credits"])

# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class BalanceResponse(BaseModel):
    user_id: str
    credits: int
    updated_at: str

class UseCreditsRequest(BaseModel):
    credits: int
    transaction_type: str  # 'usage_basic' or 'usage_premium'
    description: Optional[str] = None

class UseCreditsResponse(BaseModel):
    success: bool
    credits_used: Optional[int] = None
    credits_remaining: Optional[int] = None
    error: Optional[str] = None

class Transaction(BaseModel):
    id: str
    type: str
    credits_change: int
    credits_after: int
    description: Optional[str]
    created_at: str

class TransactionHistoryResponse(BaseModel):
    transactions: List[Transaction]
    total: int

# =====================================================
# CREDITS ENDPOINTS
# =====================================================

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(current_user: dict = Depends(get_current_user)):
    """
    Get current user's credit balance
    """
    try:
        user_id = current_user["id"]

        # Get user credits
        result = supabase_admin.table('user_credits')\
            .select('credits, updated_at')\
            .eq('user_id', user_id)\
            .single()\
            .execute()

        if not result.data:
            # If no record exists, create one with 10 free credits
            create_result = supabase_admin.table('user_credits').insert({
                'user_id': user_id,
                'credits': 10
            }).execute()

            return BalanceResponse(
                user_id=user_id,
                credits=10,
                updated_at=create_result.data[0]['updated_at']
            )

        return BalanceResponse(
            user_id=user_id,
            credits=result.data['credits'],
            updated_at=result.data['updated_at']
        )

    except Exception as e:
        logger.error(f"Error getting balance for user {current_user['id']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch credit balance")


@router.post("/use", response_model=UseCreditsResponse)
async def use_credits(
    request: UseCreditsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Use credits for image processing
    Validates transaction type and uses database function for atomic operation
    """
    try:
        user_id = current_user["id"]

        # Validate transaction type
        if request.transaction_type not in ['usage_basic', 'usage_premium']:
            raise HTTPException(
                status_code=400,
                detail="Invalid transaction type. Must be 'usage_basic' or 'usage_premium'"
            )

        # Validate credits amount
        if request.credits <= 0:
            raise HTTPException(status_code=400, detail="Credits must be positive")

        # Use the database function for atomic credit deduction
        result = supabase_admin.rpc('use_credits', {
            'p_user_id': user_id,
            'p_credits_needed': request.credits,
            'p_transaction_type': request.transaction_type,
            'p_description': request.description or f"{request.transaction_type} processing"
        }).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to process credit usage")

        response_data = result.data

        if not response_data.get('success', False):
            return UseCreditsResponse(
                success=False,
                error=response_data.get('error', 'Insufficient credits')
            )

        logger.info(f"User {user_id} used {request.credits} credits. Remaining: {response_data['credits_remaining']}")

        return UseCreditsResponse(
            success=True,
            credits_used=response_data['credits_used'],
            credits_remaining=response_data['credits_remaining']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error using credits for user {current_user['id']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to use credits: {str(e)}")


@router.get("/history", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get user's transaction history (purchases and usage)
    """
    try:
        user_id = current_user["id"]

        # Get transactions ordered by most recent
        result = supabase_admin.table('transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        # Get total count
        count_result = supabase_admin.table('transactions')\
            .select('id', count='exact')\
            .eq('user_id', user_id)\
            .execute()

        transactions = []
        if result.data:
            for tx in result.data:
                transactions.append(Transaction(
                    id=tx['id'],
                    type=tx['type'],
                    credits_change=tx['credits_change'],
                    credits_after=tx['credits_after'],
                    description=tx.get('description'),
                    created_at=tx['created_at']
                ))

        return TransactionHistoryResponse(
            transactions=transactions,
            total=count_result.count or 0
        )

    except Exception as e:
        logger.error(f"Error getting transaction history for user {current_user['id']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch transaction history")
