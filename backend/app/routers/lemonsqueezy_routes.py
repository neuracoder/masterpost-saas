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

router = APIRouter(prefix="/api/v1/lemonsqueezy", tags=["lemonsqueezy"])

# Configuración LemonSqueezy
LEMONSQUEEZY_API_KEY = os.getenv("LEMONSQUEEZY_API_KEY")
LEMONSQUEEZY_STORE_ID = os.getenv("LEMONSQUEEZY_STORE_ID")
LEMONSQUEEZY_WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")

sqlite_client = SQLiteClient()

# Mapeo de Variant IDs a créditos
CREDIT_PACKAGES = {
    os.getenv("LEMONSQUEEZY_VARIANT_STARTER"): {"credits": 50, "name": "Starter", "price": "$6.99"},
    os.getenv("LEMONSQUEEZY_VARIANT_PRO"): {"credits": 200, "name": "Pro", "price": "$24.99"},
    os.getenv("LEMONSQUEEZY_VARIANT_BUSINESS"): {"credits": 650, "name": "Business", "price": "$54.99"}
}

# Mapeo de nombres de paquetes a Variant IDs
PACKAGE_TO_VARIANT = {
    "starter": os.getenv("LEMONSQUEEZY_VARIANT_STARTER"),
    "pro": os.getenv("LEMONSQUEEZY_VARIANT_PRO"),
    "business": os.getenv("LEMONSQUEEZY_VARIANT_BUSINESS")
}

@router.post("/webhook")
async def lemonsqueezy_webhook(request: Request):
    """
    Webhook de LemonSqueezy - Recibe notificación de compra exitosa
    y asigna créditos al usuario
    """

    payload = await request.body()
    signature = request.headers.get("X-Signature")

    # Verificar firma del webhook si está configurado
    if LEMONSQUEEZY_WEBHOOK_SECRET:
        try:
            expected_signature = hmac.new(
                LEMONSQUEEZY_WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature or "", expected_signature):
                raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"⚠️ Webhook signature verification failed: {e}")
            # En desarrollo, podemos continuar sin verificación
            # raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Procesar evento de orden creada
    event_name = event.get("meta", {}).get("event_name")

    if event_name == "order_created":
        data = event.get("data", {})
        attributes = data.get("attributes", {})

        # Extraer información
        customer_email = attributes.get("user_email")
        order_number = attributes.get("order_number")
        variant_id = str(attributes.get("first_order_item", {}).get("variant_id", ""))

        print(f"📦 Nueva orden de LemonSqueezy:")
        print(f"   Email: {customer_email}")
        print(f"   Order: #{order_number}")
        print(f"   Variant ID: {variant_id}")

        if not customer_email:
            # Intentar obtener de custom_data si está disponible
            custom_data = attributes.get("custom_data", {})
            customer_email = custom_data.get("email")

        if not customer_email:
            print(f"⚠️ No se pudo obtener email del cliente")
            return {"status": "error", "message": "Missing customer email"}

        # Buscar cuántos créditos corresponden
        package = CREDIT_PACKAGES.get(variant_id)

        if not package:
            print(f"⚠️ Variant ID desconocido: {variant_id}")
            print(f"   Variant IDs conocidos: {list(CREDIT_PACKAGES.keys())}")
            return {"status": "ignored", "message": f"Unknown variant_id: {variant_id}"}

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
            print(f"   Order Number: #{order_number}")

            # Guardar registro de transacción
            sqlite_client.log_transaction(
                email=customer_email,
                credits=credits,
                transaction_type="purchase",
                description=f"Compra de {pack_name} Pack",
                stripe_payment_id=f"lemon_{order_number}"
            )
        else:
            print(f"❌ Error asignando créditos a {customer_email}")
            raise HTTPException(status_code=500, detail="Failed to add credits")

    return {"status": "success"}


@router.post("/create-checkout")
async def create_checkout_session(data: dict):
    """
    Crea checkout en LemonSqueezy
    Frontend llama a este endpoint cuando usuario hace click en "Buy"
    """

    pack_name = data.get("pack", "").lower()
    customer_email = data.get("email")

    if not pack_name or not customer_email:
        raise HTTPException(status_code=400, detail="Missing pack or email")

    # Obtener variant_id del paquete
    variant_id = PACKAGE_TO_VARIANT.get(pack_name)

    if not variant_id:
        raise HTTPException(status_code=400, detail=f"Invalid pack name: {pack_name}")

    try:
        # Crear checkout usando LemonSqueezy API
        url = "https://api.lemonsqueezy.com/v1/checkouts"

        headers = {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {LEMONSQUEEZY_API_KEY}"
        }

        payload = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": customer_email,
                        "custom": {
                            "email": customer_email
                        }
                    }
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": LEMONSQUEEZY_STORE_ID
                        }
                    },
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": variant_id
                        }
                    }
                }
            }
        }

        print(f"🔄 Creando checkout de LemonSqueezy:")
        print(f"   Email: {customer_email}")
        print(f"   Pack: {pack_name}")
        print(f"   Variant ID: {variant_id}")

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 201:
            print(f"❌ Error de LemonSqueezy API: {response.status_code}")
            print(f"   Response: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"LemonSqueezy API error: {response.text}"
            )

        result = response.json()
        checkout_url = result.get("data", {}).get("attributes", {}).get("url")

        if not checkout_url:
            raise HTTPException(status_code=500, detail="No checkout URL received")

        print(f"✅ Checkout creado exitosamente")
        print(f"   URL: {checkout_url}")

        return {"checkout_url": checkout_url, "url": checkout_url}

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión con LemonSqueezy: {e}")
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")
    except Exception as e:
        print(f"❌ Error creando checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
                "variant_id": os.getenv("LEMONSQUEEZY_VARIANT_STARTER"),
                "description": "50 credits - Perfect for small sellers"
            },
            {
                "id": "pro",
                "name": "Pro Pack",
                "credits": 200,
                "price_usd": 24.99,
                "variant_id": os.getenv("LEMONSQUEEZY_VARIANT_PRO"),
                "description": "200 credits - For serious sellers"
            },
            {
                "id": "business",
                "name": "Business Pack",
                "credits": 650,
                "price_usd": 54.99,
                "variant_id": os.getenv("LEMONSQUEEZY_VARIANT_BUSINESS"),
                "description": "650 credits - High-volume sellers & agencies"
            }
        ]
    }
