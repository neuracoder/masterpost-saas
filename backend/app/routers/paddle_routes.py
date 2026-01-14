from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent.parent / ".env")
from fastapi import APIRouter, Request, HTTPException, Header
from app.database_sqlite.sqlite_client import SQLiteClient
import os
import hmac
import hashlib
from datetime import datetime
from app.services.email_service import send_access_code_email
import requests
import json
import logging

router = APIRouter(prefix="/api/v1/paddle", tags=["paddle"])

# Setup logger
logger = logging.getLogger(__name__)

# Configuración Paddle
PADDLE_API_KEY = os.getenv("PADDLE_API_KEY")
PADDLE_WEBHOOK_SECRET = os.getenv("PADDLE_WEBHOOK_SECRET", "")
PADDLE_ENVIRONMENT = os.getenv("PADDLE_ENVIRONMENT", "sandbox")  # "sandbox" o "production"

# Base URL según el ambiente
PADDLE_API_BASE = "https://api.paddle.com" if PADDLE_ENVIRONMENT == "production" else "https://sandbox-api.paddle.com"

sqlite_client = SQLiteClient()

# Mapeo de Product IDs a créditos
CREDIT_PACKAGES = {
    "starter": {"credits": 50, "name": "Starter", "price": "6.99", "price_id": os.getenv("PADDLE_PRICE_STARTER")},
    "pro": {"credits": 200, "name": "Pro", "price": "24.99", "price_id": os.getenv("PADDLE_PRICE_PRO")},
    "business": {"credits": 650, "name": "Business", "price": "54.99", "price_id": os.getenv("PADDLE_PRICE_BUSINESS")}
}

@router.post("/webhook")
async def paddle_webhook(request: Request):
    """
    Webhook de Paddle - Recibe notificación de compra exitosa
    y asigna créditos al usuario

    Paddle envía eventos como:
    - transaction.completed
    - transaction.updated
    - subscription.created
    """

    payload = await request.body()
    signature = request.headers.get("Paddle-Signature")

    body_str = payload.decode('utf-8')

    # DEBUG - Log completo del webhook
    print("🔍 DEBUG Paddle Webhook:")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Body: {body_str}")
    print(f"   Signature: {signature}")

    # Parsear JSON para debug
    try:
        event_data = json.loads(body_str)
        print(f"   Event Data: {json.dumps(event_data, indent=2)}")
    except Exception as e:
        print(f"   Error parsing JSON: {e}")

    # Debug: Log completo del payload
    logger.info("🔍 DEBUG Webhook Paddle Received")
    logger.info(f"   Full payload: {body_str}")
    logger.info(f"   Signature: {signature}")

    # Verificar firma del webhook (CRÍTICO en producción)
    if PADDLE_WEBHOOK_SECRET:
        try:
            # Paddle usa ts;h1=signature format
            if not signature:
                raise HTTPException(status_code=400, detail="Missing Paddle-Signature header")

            # Extraer timestamp y signature
            sig_parts = dict(part.split('=') for part in signature.split(';'))
            timestamp = sig_parts.get('ts')
            h1_signature = sig_parts.get('h1')

            if not timestamp or not h1_signature:
                raise HTTPException(status_code=400, detail="Invalid signature format")

            # Construir mensaje a verificar: timestamp:body
            signed_payload = f"{timestamp}:{body_str}"

            # Calcular firma esperada
            expected_signature = hmac.new(
                PADDLE_WEBHOOK_SECRET.encode(),
                signed_payload.encode(),
                hashlib.sha256
            ).hexdigest()

            # Comparar firmas de forma segura
            if not hmac.compare_digest(h1_signature, expected_signature):
                logger.error("❌ Invalid webhook signature")
                raise HTTPException(status_code=400, detail="Invalid signature")

            logger.info("✅ Webhook signature verified")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Webhook signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Signature verification failed")

    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Procesar evento de transacción completada
    event_type = event.get("event_type")

    logger.info(f"📨 Webhook de Paddle recibido:")
    logger.info(f"   Event Type: {event_type}")

    # Paddle envía transaction.completed cuando el pago es exitoso
    if event_type == "transaction.completed":
        data = event.get("data", {})

        # Extraer información del cliente
        customer_email = data.get("customer_email")
        transaction_id = data.get("id")

        # Extraer información de custom_data si está disponible
        custom_data = data.get("custom_data", {})
        if not customer_email and custom_data:
            customer_email = custom_data.get("email")

        logger.info(f"📦 Nueva transacción de Paddle:")
        logger.info(f"   Transaction ID: {transaction_id}")
        logger.info(f"   Email: {customer_email}")

        if not customer_email:
            logger.error("⚠️ No se pudo obtener email del cliente")
            return {"status": "error", "message": "Missing customer email"}

        # Extraer información de los items
        items = data.get("items", [])
        if not items:
            logger.error("⚠️ No se encontraron items en la transacción")
            return {"status": "error", "message": "No items in transaction"}

        # Obtener el primer item (asumimos un item por transacción)
        item = items[0]
        price_id = item.get("price", {}).get("id")

        logger.info(f"   Price ID: {price_id}")

        # Buscar el paquete correspondiente
        package = None
        pack_name_key = None

        for key, pkg in CREDIT_PACKAGES.items():
            if pkg["price_id"] == price_id:
                package = pkg
                pack_name_key = key
                break

        if not package:
            logger.error(f"⚠️ Price ID desconocido: {price_id}")
            logger.error(f"   Price IDs conocidos: {[pkg['price_id'] for pkg in CREDIT_PACKAGES.values()]}")
            return {"status": "ignored", "message": f"Unknown price_id: {price_id}"}

        credits = package["credits"]
        pack_display_name = package["name"]

        # Intentar crear usuario (create_user ya maneja si existe)
        access_code = sqlite_client.create_user(customer_email, credits)

        if access_code:
            # Usuario creado exitosamente
            success = True
            logger.info(f"✅ Usuario creado: {customer_email} con código {access_code}")

            # Send access code email
            email_sent = send_access_code_email(
                email=customer_email,
                access_code=access_code,
                credits=credits,
                pack_name=pack_display_name
            )

            if email_sent:
                logger.info(f"📧 Access code email sent to {customer_email}")
            else:
                logger.warning(f"⚠️ Failed to send email to {customer_email} - but user was created")
        else:
            # Usuario ya existía, agregar créditos
            success = sqlite_client.add_credits(customer_email, credits)
            logger.info(f"✅ Usuario existente. Agregando créditos a {customer_email}")

            # Send email notification for credit top-up
            if success:
                user = sqlite_client.get_user_by_email(customer_email)
                if user and user.get('access_code'):
                    email_sent = send_access_code_email(
                        email=customer_email,
                        access_code=user['access_code'],
                        credits=credits,
                        pack_name=pack_display_name
                    )
                    if email_sent:
                        logger.info(f"📧 Credit top-up email sent to {customer_email}")

        if success:
            logger.info(f"✅ {credits} créditos asignados oficialmente a {customer_email}")
            logger.info(f"   Paquete: {pack_display_name}")
            logger.info(f"   Transaction ID: {transaction_id}")

            # Guardar registro de transacción
            sqlite_client.log_transaction(
                email=customer_email,
                credits=credits,
                transaction_type="purchase",
                description=f"Compra de {pack_display_name} Pack",
                stripe_payment_id=f"paddle_{transaction_id}"
            )
        else:
            logger.error(f"❌ Error asignando créditos a {customer_email} en base de datos")
            raise HTTPException(status_code=500, detail="Failed to add credits")

    return {"status": "success"}


@router.post("/create-checkout")
async def create_checkout_session(data: dict):
    """
    Retorna datos de checkout para Paddle.js (overlay)
    Frontend usa estos datos para abrir checkout con Paddle.Checkout.open()
    """

    pack_name = data.get("pack", "").lower()
    customer_email = data.get("email")

    if not pack_name or not customer_email:
        raise HTTPException(status_code=400, detail="Missing pack or email")

    # Obtener información del paquete
    package = CREDIT_PACKAGES.get(pack_name)

    if not package:
        raise HTTPException(status_code=400, detail=f"Invalid pack name: {pack_name}")

    price_id = package["price_id"]

    if not price_id:
        raise HTTPException(status_code=500, detail=f"Price ID not configured for pack: {pack_name}")

    logger.info(f"🔄 Preparando datos de checkout de Paddle:")
    logger.info(f"   Email: {customer_email}")
    logger.info(f"   Pack: {pack_name}")
    logger.info(f"   Price ID: {price_id}")

    # Retornar datos para Paddle.js (no crear checkout server-side)
    return {
        "price_id": price_id,
        "email": customer_email,
        "pack": pack_name,
        "credits": package["credits"],
        "pack_name": package["name"]
    }


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
                "price_usd": 6.99,
                "price_id": os.getenv("PADDLE_PRICE_STARTER"),
                "description": "50 credits - Perfect for small sellers"
            },
            {
                "id": "pro",
                "name": "Pro Pack",
                "credits": 200,
                "price_usd": 24.99,
                "price_id": os.getenv("PADDLE_PRICE_PRO"),
                "description": "200 credits - For serious sellers"
            },
            {
                "id": "business",
                "name": "Business Pack",
                "credits": 650,
                "price_usd": 54.99,
                "price_id": os.getenv("PADDLE_PRICE_BUSINESS"),
                "description": "650 credits - High-volume sellers & agencies"
            }
        ]
    }
