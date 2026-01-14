from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent.parent / ".env")
from fastapi import APIRouter, Request, HTTPException, Header
from app.database_sqlite.sqlite_client import SQLiteClient
import stripe
import os
from datetime import datetime
from app.services.email_service import send_access_code_email

router = APIRouter(prefix="/api/v1/stripe", tags=["stripe"])

# Configuración Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

sqlite_client = SQLiteClient()

# Mapeo de Price IDs a créditos
CREDIT_PACKAGES = {
    os.getenv("STRIPE_PRICE_STARTER"): {"credits": 50, "name": "Starter"},
    os.getenv("STRIPE_PRICE_PRO"): {"credits": 200, "name": "Pro"},
    os.getenv("STRIPE_PRICE_BUSINESS"): {"credits": 650, "name": "Business"}
}

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Webhook de Stripe - Recibe notificación de pago exitoso
    y asigna créditos al usuario
    """

    payload = await request.body()

    # Verificar firma del webhook (seguridad)
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Procesar evento de pago completado
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Extraer información
        customer_email = session.get('customer_details', {}).get('email')
        payment_intent = session.get('payment_intent')

        # Obtener price_id del line_item
        line_items = stripe.checkout.Session.list_line_items(session['id'])
        price_id = line_items.data[0]['price']['id']

        # Buscar cuántos créditos corresponden
        package = CREDIT_PACKAGES.get(price_id)

        if not package:
            print(f"⚠️ Price ID desconocido: {price_id}")
            return {"status": "ignored"}

        credits = package["credits"]
        pack_name = package["name"]

        # Intentar crear usuario (create_user ya maneja si existe)
        access_code = sqlite_client.create_user(customer_email, credits)

        if access_code:
            # Usuario creado exitosamente
            success = True
            print(f"✅ Usuario creado: {customer_email} con código {access_code}")

            # Send access code email
            email_sent = send_access_code_email(
                email=customer_email,
                access_code=access_code,
                credits=credits,
                pack_name=pack_name
            )

            if email_sent:
                print(f"📧 Access code email sent to {customer_email}")
            else:
                print(f"⚠️ Failed to send email to {customer_email} - but user was created")
        else:
            # Usuario ya existía, agregar créditos
            success = sqlite_client.add_credits(customer_email, credits)

            # Send email notification for credit top-up
            if success:
                user = sqlite_client.get_user_by_email(customer_email)
                if user and user.get('access_code'):
                    email_sent = send_access_code_email(
                        email=customer_email,
                        access_code=user['access_code'],
                        credits=credits,
                        pack_name=pack_name
                    )
                    if email_sent:
                        print(f"📧 Credit top-up email sent to {customer_email}")

        if success:
            print(f"✅ {credits} créditos asignados a {customer_email}")
            print(f"   Paquete: {pack_name}")
            print(f"   Payment Intent: {payment_intent}")

            # Guardar registro de transacción (opcional)
            sqlite_client.log_transaction(
                email=customer_email,
                credits=credits,
                transaction_type="purchase",
                description=f"Compra de {pack_name} Pack",
                stripe_payment_id=payment_intent
            )
        else:
            print(f"❌ Error asignando créditos a {customer_email}")
            raise HTTPException(status_code=500, detail="Failed to add credits")

    return {"status": "success"}


@router.post("/create-checkout")
async def create_checkout_session(data: dict):
    """
    Crea sesión de checkout en Stripe
    Frontend llama a este endpoint cuando usuario hace click en "Buy"
    """

    price_id = data.get("price_id")
    customer_email = data.get("customer_email")

    if not price_id or not customer_email:
        raise HTTPException(status_code=400, detail="Missing price_id or customer_email")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            customer_email=customer_email,
            success_url=f'https://masterpost.io/payment-success?email={customer_email}',
            cancel_url='https://masterpost.io/buy-credits?payment=cancel',
        )

        return {"session_id": session.id, "url": session.url}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/packs")
async def get_credit_packs():
    """
    Lista los paquetes de créditos disponibles
    Frontend usa esto para mostrar precios
    """
    return {
        "packs": [
            {
                "id": "starter",
                "name": "Starter Pack",
                "credits": 50,
                "price_usd": 4.99,
                "price_id": os.getenv("STRIPE_PRICE_STARTER"),
                "description": "50 credits - Perfect for testing"
            },
            {
                "id": "pro",
                "name": "Pro Pack",
                "credits": 200,
                "price_usd": 17.99,
                "price_id": os.getenv("STRIPE_PRICE_PRO"),
                "description": "200 credits - Best value"
            },
            {
                "id": "business",
                "name": "Business Pack",
                "credits": 650,
                "price_usd": 54.99,
                "price_id": os.getenv("STRIPE_PRICE_BUSINESS"),
                "description": "650 credits - For agencies"
            }
        ]
    }
