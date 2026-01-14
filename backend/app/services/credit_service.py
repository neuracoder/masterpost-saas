"""
Credit Service - Manages credit operations with Supabase
"""

import os
import logging
from typing import Dict, Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase credentials not configured")
    supabase: Optional[Client] = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase client initialized for credit service")


async def get_user_credits(user_id: str) -> Dict:
    """
    Get current credit balance for a user

    Args:
        user_id: User UUID from Supabase Auth

    Returns:
        dict: {"user_id": str, "credits": int, "updated_at": str}
    """
    if not supabase:
        logger.error("Supabase not configured")
        return {"user_id": user_id, "credits": 0, "error": "Database not configured"}

    try:
        # PostgREST requires parameter names WITHOUT 'p_' prefix
        result = supabase.rpc('get_user_credits', {'user_id': user_id}).execute()

        # La función RPC retorna un INTEGER directamente
        if result.data is not None:
            credits = result.data if isinstance(result.data, int) else 0
            logger.info(f"💳 User {user_id[:8]}... has {credits} credits")
            return {"user_id": user_id, "credits": credits}
        else:
            logger.warning(f"No credit data returned for user {user_id[:8]}...")
            return {"user_id": user_id, "credits": 0, "error": "No data returned"}

    except Exception as e:
        logger.error(f"Error getting credits for user {user_id[:8]}...: {e}")
        import traceback
        traceback.print_exc()
        return {"user_id": user_id, "credits": 0, "error": str(e)}


async def verify_sufficient_credits(user_id: str, credits_needed: int) -> Dict:
    """
    Verify if user has enough credits for an operation

    Args:
        user_id: User UUID
        credits_needed: Number of credits required

    Returns:
        dict: {"sufficient": bool, "current_credits": int, "credits_needed": int}
    """
    credit_data = await get_user_credits(user_id)
    current_credits = credit_data.get("credits", 0)

    sufficient = current_credits >= credits_needed

    if sufficient:
        logger.info(f"✅ User {user_id[:8]}... has sufficient credits: {current_credits} >= {credits_needed}")
    else:
        logger.warning(f"❌ User {user_id[:8]}... insufficient credits: {current_credits} < {credits_needed}")

    return {
        "sufficient": sufficient,
        "current_credits": current_credits,
        "credits_needed": credits_needed,
        "shortfall": max(0, credits_needed - current_credits)
    }


async def use_credits(
    user_id: str,
    credits_needed: int,
    transaction_type: str,
    description: str
) -> Dict:
    """
    Deduct credits from user account (atomic operation)

    Args:
        user_id: User UUID
        credits_needed: Number of credits to deduct
        transaction_type: Type of transaction (usage_basic, usage_premium)
        description: Description of the transaction

    Returns:
        dict: {"success": bool, "credits_used": int, "credits_before": int, "credits_after": int}
    """
    if not supabase:
        logger.error("Supabase not configured")
        return {"success": False, "error": "Database not configured"}

    try:
        logger.info(f"💳 Attempting to deduct {credits_needed} credits from user {user_id[:8]}...")
        logger.info(f"   Type: {transaction_type}")
        logger.info(f"   Description: {description}")

        # PostgREST requires parameter names WITHOUT 'p_' prefix
        result = supabase.rpc('use_credits', {
            'user_id': user_id,
            'credits_needed': credits_needed,
            'transaction_type': transaction_type,
            'description': description
        }).execute()

        if result.data and len(result.data) > 0:
            response = result.data[0]

            if response.get('success'):
                logger.info(f"✅ Credits deducted successfully:")
                logger.info(f"   Before: {response.get('credits_before')} credits")
                logger.info(f"   Used: {response.get('credits_used')} credits")
                logger.info(f"   After: {response.get('credits_after')} credits")
                return response
            else:
                logger.error(f"❌ Credit deduction failed: {response.get('error')}")
                return response
        else:
            logger.error("No data returned from use_credits function")
            return {"success": False, "error": "No data returned"}

    except Exception as e:
        logger.error(f"Error using credits: {e}")
        return {"success": False, "error": str(e)}


async def add_credits(
    user_id: str,
    credits_amount: int,
    description: str,
    stripe_payment_intent_id: Optional[str] = None
) -> Dict:
    """
    Add credits to user account (for purchases)

    Args:
        user_id: User UUID
        credits_amount: Number of credits to add
        description: Description (e.g., "Purchased Pro Pack")
        stripe_payment_intent_id: Optional Stripe payment intent ID

    Returns:
        dict: {"success": bool, "credits_added": int, "credits_total": int}
    """
    if not supabase:
        logger.error("Supabase not configured")
        return {"success": False, "error": "Database not configured"}

    try:
        logger.info(f"💰 Adding {credits_amount} credits to user {user_id[:8]}...")

        # PostgREST requires parameter names WITHOUT 'p_' prefix
        result = supabase.rpc('add_credits', {
            'user_id': user_id,
            'credits_amount': credits_amount,
            'description': description,
            'stripe_payment_intent_id': stripe_payment_intent_id
        }).execute()

        if result.data and len(result.data) > 0:
            response = result.data[0]
            logger.info(f"✅ Credits added successfully: +{response.get('credits_added')} → Total: {response.get('credits_total')}")
            return response
        else:
            logger.error("No data returned from add_credits function")
            return {"success": False, "error": "No data returned"}

    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        return {"success": False, "error": str(e)}


async def get_transaction_history(user_id: str, limit: int = 50) -> list:
    """
    Get transaction history for a user

    Args:
        user_id: User UUID
        limit: Maximum number of transactions to return (default 50)

    Returns:
        list: List of transaction dictionaries
    """
    if not supabase:
        logger.error("Supabase not configured")
        return []

    try:
        result = supabase.table('transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()

        if result.data:
            logger.info(f"📜 Retrieved {len(result.data)} transactions for user {user_id[:8]}...")
            return result.data
        else:
            logger.info(f"No transactions found for user {user_id[:8]}...")
            return []

    except Exception as e:
        logger.error(f"Error getting transaction history: {e}")
        return []
