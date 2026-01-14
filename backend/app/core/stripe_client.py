"""
Stripe client for payment processing
"""

import stripe
from .config import settings

# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_stripe():
    """Get Stripe module configured with API key"""
    return stripe
