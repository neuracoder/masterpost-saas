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
import paypalrestsdk
import json

router = APIRouter(prefix="/api/v1/paypal", tags=["paypal"])

# Configuración PayPal
# Configuración PayPal
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")
# Valores por defecto para desarrollo/sandbox (fallback)
DEFAULT_CLIENT_ID = "AX6pyssg-FRjyy9a0_xALKj3u42r21vL4ddqSq01JaxJ_glgrjvTaxZCkG5W_f1mgDTVxUCt7C5PoxTO"
DEFAULT_CLIENT_SECRET = "ELzOJ5cEJgsJYUlGaTCLd3oR2Ev10xPMo8fL8SKKB4JbGDg7f1ABl1NpAnsbNQYksWwfGBWK9meU925v"

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", DEFAULT_CLIENT_ID)
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", DEFAULT_CLIENT_SECRET)

# Configurar PayPal SDK
paypalrestsdk.configure({
    "mode": PAYPAL_MODE,
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET
})

sqlite_client = SQLiteClient()

# Mapeo de paquetes a créditos y precios
CREDIT_PACKAGES = {
    "starter": {"credits": 50, "name": "Starter", "price": "6.99"},
    "pro": {"credits": 200, "name": "Pro", "price": "24.99"},
    "business": {"credits": 650, "name": "Business", "price": "54.99"}
}

@router.post("/create-order")
async def create_order(data: dict):
    """
    Crea una orden de PayPal
    Frontend llama a este endpoint cuando usuario hace click en "Buy"
    """

    pack_name = data.get("pack", "").lower()
    customer_email = data.get("email")

    if not pack_name or not customer_email:
        raise HTTPException(status_code=400, detail="Missing pack or email")

    # Obtener información del paquete
    package = CREDIT_PACKAGES.get(pack_name)

    if not package:
        raise HTTPException(status_code=400, detail=f"Invalid pack name: {pack_name}")

    try:
        # Crear orden de PayPal
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal",
                "payer_info": {
                    "email": customer_email
                }
            },
            "redirect_urls": {
                "return_url": "https://masterpost.io/payment-success",
                "cancel_url": "https://masterpost.io/pricing"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"{package['name']} Pack - {package['credits']} Credits",
                        "sku": pack_name,
                        "price": package['price'],
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": package['price'],
                    "currency": "USD"
                },
                "description": f"Masterpost - {package['name']} Pack ({package['credits']} credits)",
                "custom": json.dumps({
                    "email": customer_email,
                    "pack": pack_name
                })
            }],
            "application_context": {
                "brand_name": "Masterpost.io",
                "landing_page": "BILLING",
                "shipping_preference": "NO_SHIPPING"
            }
        })

        if payment.create():
            print(f"🔄 Orden de PayPal creada:")
            print(f"   Email: {customer_email}")
            print(f"   Pack: {pack_name}")
            print(f"   Payment ID: {payment.id}")

            # Obtener URL de aprobación
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break

            if not approval_url:
                raise HTTPException(status_code=500, detail="No approval URL received")

            print(f"✅ Orden creada exitosamente")
            print(f"   Approval URL: {approval_url}")

            return {
                "order_id": payment.id,
                "approval_url": approval_url,
                "status": "created"
            }
        else:
            print(f"❌ Error creando orden de PayPal: {payment.error}")
            raise HTTPException(
                status_code=500,
                detail=f"PayPal error: {payment.error}"
            )

    except Exception as e:
        print(f"❌ Error creando orden: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capture-order")
async def capture_order(data: dict):
    """
    Captura el pago de PayPal después de que el usuario apruebe
    Frontend llama a este endpoint cuando usuario regresa de PayPal
    """

    payment_id = data.get("payment_id")
    payer_id = data.get("payer_id")

    if not payment_id or not payer_id:
        raise HTTPException(status_code=400, detail="Missing payment_id or payer_id")

    try:
        # Obtener el pago
        payment = paypalrestsdk.Payment.find(payment_id)

        print(f"🔍 Payment state: {payment.state}")

        # Extraer información del pago ANTES de ejecutar (por si ya está ejecutado)
        transaction = payment.transactions[0] if payment.transactions else None
        if not transaction:
            raise HTTPException(status_code=400, detail="No transaction found in payment")

        custom_data = json.loads(transaction.custom) if transaction.custom else {}
        customer_email = custom_data.get("email")
        pack_name = custom_data.get("pack")

        if not customer_email or not pack_name:
            print(f"⚠️ No se pudo obtener email o pack del pago")
            raise HTTPException(status_code=400, detail="Missing customer email or pack in payment")

        # Buscar información del paquete
        package = CREDIT_PACKAGES.get(pack_name)

        if not package:
            print(f"⚠️ Paquete desconocido: {pack_name}")
            raise HTTPException(status_code=400, detail=f"Unknown pack: {pack_name}")

        credits = package["credits"]
        pack_display_name = package["name"]

        # Verificar estado del pago
        if payment.state == "approved":
            # Ejecutar el pago
            if payment.execute({"payer_id": payer_id}):
                print(f"💰 Pago de PayPal capturado:")
                print(f"   Payment ID: {payment_id}")
                print(f"   Payer ID: {payer_id}")
            else:
                print(f"❌ Error ejecutando pago: {payment.error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"PayPal execution error: {payment.error}"
                )
        elif payment.state == "created":
            print(f"⚠️ Pago no aprobado aún: {payment_id}")
            return {
                "status": "error",
                "message": "Payment not yet approved by user"
            }
        elif payment.state in ["completed", "approved"]:
            # Ya fue ejecutado (posiblemente por webhook o intento anterior)
            print(f"ℹ️ Pago ya fue procesado anteriormente: {payment_id}")
            print(f"   Estado actual: {payment.state}")
        else:
            # Cancelado u otro estado
            print(f"⚠️ Estado de pago no válido: {payment.state}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment state: {payment.state}"
            )

        # Procesar créditos (tanto si acabamos de ejecutar como si ya estaba ejecutado)
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
                pack_name=pack_display_name
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
                        pack_name=pack_display_name
                    )
                    if email_sent:
                        print(f"📧 Credit top-up email sent to {customer_email}")

        if success:
            print(f"✅ {credits} créditos asignados a {customer_email}")
            print(f"   Paquete: {pack_display_name}")
            print(f"   Payment ID: {payment_id}")

            # Guardar registro de transacción
            sqlite_client.log_transaction(
                email=customer_email,
                credits=credits,
                transaction_type="purchase",
                description=f"Compra de {pack_display_name} Pack",
                stripe_payment_id=f"paypal_{payment_id}"
            )

            return {
                "status": "success",
                "credits": credits,
                "email": customer_email,
                "pack": pack_display_name
            }
        else:
            print(f"❌ Error asignando créditos a {customer_email}")
            raise HTTPException(status_code=500, detail="Failed to add credits")

    except paypalrestsdk.ResourceNotFound:
        print(f"❌ Pago no encontrado: {payment_id}")
        raise HTTPException(status_code=404, detail="Payment not found")
    except Exception as e:
        print(f"❌ Error capturando orden: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ... imports ...
import logging

# Setup logger
logger = logging.getLogger(__name__)

# ... existing code ...

@router.post("/webhook")
async def paypal_webhook(request: Request):
    """
    Webhook de PayPal - Recibe notificación de compra exitosa
    y asigna créditos al usuario
    """

    payload = await request.body()
    body_str = payload.decode('utf-8')

    # Debug: Log completo del payload
    logger.info("🔍 DEBUG Webhook PayPal Received")
    logger.info(f"   Full payload: {body_str}")

    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Procesar evento de pago completado
    event_type = event.get("event_type")

    logger.info(f"📨 Webhook de PayPal recibido:")
    logger.info(f"   Event Type: {event_type}")

    # PayPal envía varios tipos de eventos
    # Soportamos tanto SALE (venta directa) como CAPTURE (captura de autorización)
    if event_type in ["PAYMENT.SALE.COMPLETED", "PAYMENT.CAPTURE.COMPLETED"]:
        resource = event.get("resource", {})
        payment_id = resource.get("parent_payment")
        
        # En caso de CAPTURE, a veces el parent_payment es el ID de autorización, 
        # pero necesitamos el Payment ID original si usamos V1 SDK.
        # Si no hay parent_payment, intentamos usar el ID del recurso mismo si es SALE
        if not payment_id and event_type == "PAYMENT.SALE.COMPLETED":
             payment_id = resource.get("id")

        logger.info(f"📦 Nueva orden de PayPal procesada:")
        logger.info(f"   Payment ID: {payment_id}")
        logger.info(f"   Estado: {resource.get('state')}")

        if not payment_id:
             logger.error("⚠️ No se encontró Payment ID en el recurso")
             return {"status": "error", "message": "No payment ID found"}

        # Obtener el pago completo para acceder al custom data
        try:
            payment = paypalrestsdk.Payment.find(payment_id)

            # Debug: Log del payment object
            logger.info(f"🔍 DEBUG Payment Object Found: {payment.id}")
            
            # Extraer información del pago
            transaction = payment.transactions[0] if payment.transactions else None

            # Debug: Log de transaction
            if transaction:
                logger.info(f"🔍 DEBUG Transaction found with amount: {transaction.amount}")
                logger.info(f"   Custom data raw: {transaction.custom if hasattr(transaction, 'custom') else 'No custom attr'}")

            if not transaction:
                logger.warning(f"⚠️ No se encontró transacción en el pago {payment_id}")
                return {"status": "error", "message": "No transaction found"}

            # Extraer custom data
            custom_data = {}
            if transaction.custom:
                try:
                    custom_data = json.loads(transaction.custom)
                except json.JSONDecodeError:
                    pass

            customer_email = custom_data.get("email")
            pack_name = custom_data.get("pack")

            logger.info(f"   Email extraction: {customer_email}")
            logger.info(f"   Pack extraction: {pack_name}")

            if not customer_email or not pack_name:
                logger.error(f"⚠️ No se pudo obtener email o pack del pago")
                return {"status": "error", "message": "Missing customer email or pack"}

            # Buscar cuántos créditos corresponden
            package = CREDIT_PACKAGES.get(pack_name)

            if not package:
                logger.error(f"⚠️ Pack desconocido: {pack_name}")
                return {"status": "ignored", "message": f"Unknown pack: {pack_name}"}

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
            else:
                # Usuario ya existía, agregar créditos
                success = sqlite_client.add_credits(customer_email, credits)
                logger.info(f"✅ Usuario existente. Agregando créditos a {customer_email}")
                
                 # Send email notification for credit top-up
                if success:
                    user = sqlite_client.get_user_by_email(customer_email)
                    if user and user.get('access_code'):
                         send_access_code_email(
                            email=customer_email,
                            access_code=user['access_code'],
                            credits=credits,
                            pack_name=pack_display_name
                        )

            if success:
                logger.info(f"✅ {credits} créditos asignados oficialmente a {customer_email}")
                
                # Guardar registro de transacción
                sqlite_client.log_transaction(
                    email=customer_email,
                    credits=credits,
                    transaction_type="purchase",
                    description=f"Compra de {pack_display_name} Pack",
                    stripe_payment_id=f"paypal_{payment_id}"
                )
            else:
                logger.error(f"❌ Error asignando créditos a {customer_email} en base de datos")
                raise HTTPException(status_code=500, detail="Failed to add credits")

        except paypalrestsdk.ResourceNotFound:
            logger.error(f"❌ Pago no encontrado en PayPal: {payment_id}")
            return {"status": "error", "message": "Payment not found"}
        except Exception as e:
            logger.error(f"❌ Error procesando webhook interno: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "success"}


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
                "description": "50 credits - Perfect for small sellers"
            },
            {
                "id": "pro",
                "name": "Pro Pack",
                "credits": 200,
                "price_usd": 24.99,
                "description": "200 credits - For serious sellers"
            },
            {
                "id": "business",
                "name": "Business Pack",
                "credits": 650,
                "price_usd": 54.99,
                "description": "650 credits - High-volume sellers & agencies"
            }
        ]
    }
