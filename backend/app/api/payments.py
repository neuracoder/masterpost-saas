"""
Payment API for Masterpost.io
Handles Stripe checkout sessions, webhooks, and credit pack purchases
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Header
from pydantic import BaseModel
from typing import List, Optional
import logging
import os

from ..core.supabase import supabase_admin
from ..core.stripe_client import get_stripe
from ..core.config import settings
from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["Payments"])

stripe = get_stripe()

# =====================================================
# CREDIT PACKS CONFIGURATION
# =====================================================

CREDIT_PACKS = {
    "free": {
        "name": "Free Pack",
        "credits": 10,
        "price_usd": 0.00,
        "price_cents": 0,
        "description": "10 credits free on signup"
    },
    "pro": {
        "name": "Pro Pack",
        "credits": 200,
        "price_usd": 17.99,
        "price_cents": 1799,
        "description": "200 credits - $0.09 per credit"
    },
    "business": {
        "name": "Business Pack",
        "credits": 500,
        "price_usd": 39.99,
        "price_cents": 3999,
        "description": "500 credits - $0.08 per credit"
    }
}

# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class CreditPack(BaseModel):
    id: str
    name: str
    credits: int
    price_usd: float
    description: str

class CreditPacksResponse(BaseModel):
    packs: List[CreditPack]

class CreateCheckoutRequest(BaseModel):
    pack_id: str  # 'pro' or 'business'

class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str

class WebhookResponse(BaseModel):
    received: bool

# =====================================================
# PAYMENT ENDPOINTS
# =====================================================

@router.get("/packs", response_model=CreditPacksResponse)
async def get_credit_packs():
    """
    Get available credit packs for purchase
    """
    try:
        packs = []
        for pack_id, pack_data in CREDIT_PACKS.items():
            if pack_id != "free":  # Don't show free pack in purchase options
                packs.append(CreditPack(
                    id=pack_id,
                    name=pack_data["name"],
                    credits=pack_data["credits"],
                    price_usd=pack_data["price_usd"],
                    description=pack_data["description"]
                ))

        return CreditPacksResponse(packs=packs)

    except Exception as e:
        logger.error(f"Error getting credit packs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch credit packs")


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create Stripe Checkout session for credit pack purchase
    """
    try:
        user_id = current_user["id"]
        email = current_user["email"]

        # Validate pack ID
        if request.pack_id not in CREDIT_PACKS or request.pack_id == "free":
            raise HTTPException(status_code=400, detail="Invalid pack ID")

        pack = CREDIT_PACKS[request.pack_id]

        # Get or create Stripe customer
        customer_result = supabase_admin.table('stripe_customers')\
            .select('stripe_customer_id')\
            .eq('user_id', user_id)\
            .execute()

        if customer_result.data:
            customer_id = customer_result.data[0]['stripe_customer_id']
        else:
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=email,
                metadata={"user_id": user_id}
            )
            customer_id = customer.id

            # Save to database
            supabase_admin.table('stripe_customers').insert({
                'user_id': user_id,
                'stripe_customer_id': customer_id
            }).execute()

        # Create Checkout Session
        frontend_url = settings.FRONTEND_URL or "http://localhost:3002"

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': pack["name"],
                        'description': pack["description"],
                    },
                    'unit_amount': pack["price_cents"],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{frontend_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/pricing",
            metadata={
                'user_id': user_id,
                'pack_id': request.pack_id,
                'credits': pack["credits"]
            }
        )

        logger.info(f"Created checkout session for user {user_id}, pack: {request.pack_id}")

        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")


@router.post("/webhook", response_model=WebhookResponse)
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    Processes successful payments and adds credits to user account
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')

        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Extract metadata
            user_id = session['metadata']['user_id']
            pack_id = session['metadata']['pack_id']
            credits = int(session['metadata']['credits'])
            payment_intent_id = session.get('payment_intent')

            # Add credits to user account using database function
            result = supabase_admin.rpc('add_credits', {
                'p_user_id': user_id,
                'p_credits_amount': credits,
                'p_description': f"Purchase: {CREDIT_PACKS[pack_id]['name']}",
                'p_stripe_payment_intent_id': payment_intent_id
            }).execute()

            if result.data and result.data.get('success'):
                logger.info(f"✅ Credits added for user {user_id}: +{credits} credits (pack: {pack_id})")
            else:
                logger.error(f"❌ Failed to add credits for user {user_id}")

        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.warning(f"Payment failed for PaymentIntent: {payment_intent['id']}")

        return WebhookResponse(received=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/verify-session/{session_id}")
async def verify_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Verify a Stripe Checkout session
    Used by frontend to confirm payment success
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        # Verify session belongs to current user
        if session.metadata.get('user_id') != current_user["id"]:
            raise HTTPException(status_code=403, detail="Session does not belong to current user")

        return {
            "status": session.status,
            "payment_status": session.payment_status,
            "amount_total": session.amount_total,
            "credits": session.metadata.get('credits'),
            "pack_id": session.metadata.get('pack_id')
        }

    except stripe.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify session")
