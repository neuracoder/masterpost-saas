# 🎉 STRIPE INTEGRACIÓN - LISTA PARA PROBAR

## ✅ Estado: 100% CONFIGURADA

Todas las credenciales de Stripe han sido configuradas exitosamente en `backend/.env`:

- ✅ **Secret Key**: Configurada
- ✅ **Publishable Key**: Configurada
- ✅ **Webhook Secret**: Configurada
- ✅ **Price IDs**: Configurados (Starter, Pro, Business)

---

## 🧪 Cómo Probar la Integración

### Opción 1: Prueba con Stripe CLI (Recomendado para desarrollo)

1. **Instalar Stripe CLI** (si no lo tienes):
```bash
# Windows (con Scoop)
scoop install stripe

# Mac
brew install stripe/stripe-cli/stripe

# O descargar desde: https://stripe.com/docs/stripe-cli
```

2. **Autenticar Stripe CLI**:
```bash
stripe login
```

3. **Iniciar el servidor backend**:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

4. **En otra terminal, reenviar webhooks a localhost**:
```bash
stripe listen --forward-to localhost:8000/api/v1/stripe/webhook
```

5. **Probar un pago simulado**:
```bash
stripe trigger checkout.session.completed
```

6. **Verificar en logs del servidor**:
Deberías ver algo como:
```
✅ 200 créditos asignados a test@example.com
   Paquete: Pro
   Payment Intent: pi_ABC123...
```

---

### Opción 2: Prueba desde Frontend (Próximo paso)

Para probar desde el frontend, necesitarás crear una página de compra que:

1. Llame a `GET /api/v1/stripe/packs` para obtener los paquetes
2. Cuando el usuario haga clic en "Comprar", llame a `POST /api/v1/stripe/create-checkout`
3. Redirija al usuario a la URL de Stripe Checkout
4. Después del pago, Stripe enviará el webhook automáticamente

---

## 🔍 Verificar que todo funciona

### 1. Verificar endpoints disponibles:
```bash
curl http://localhost:8000/api/v1/stripe/packs
```

**Respuesta esperada**:
```json
{
  "packs": [
    {
      "id": "starter",
      "name": "Starter Pack",
      "credits": 50,
      "price_usd": 4.99,
      "price_id": "price_1SLljD3M485N62s33mV2Jx2e",
      "description": "50 credits - Perfect for testing"
    },
    ...
  ]
}
```

### 2. Crear sesión de checkout (reemplazar email real):
```bash
curl -X POST http://localhost:8000/api/v1/stripe/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "price_id": "price_1SLljE3M485N62s3ieI3a0xv",
    "customer_email": "demo@masterpost.io"
  }'
```

**Respuesta esperada**:
```json
{
  "session_id": "cs_test_...",
  "url": "https://checkout.stripe.com/c/pay/..."
}
```

### 3. Verificar usuario en base de datos:
```bash
# Desde la raíz del proyecto
cd backend
python -c "from app.database_sqlite.sqlite_client import sqlite_client; print(sqlite_client.get_user_credits('demo@masterpost.io'))"
```

---

## 🎯 Tarjetas de Prueba de Stripe

Para probar pagos exitosos, usa estas tarjetas de prueba:

**Pago exitoso**:
- Número: `4242 4242 4242 4242`
- Fecha: Cualquier fecha futura (ej: 12/34)
- CVC: Cualquier 3 dígitos (ej: 123)
- ZIP: Cualquier 5 dígitos (ej: 12345)

**Pago declinado**:
- Número: `4000 0000 0000 0002`

**Requiere autenticación 3D Secure**:
- Número: `4000 0025 0000 3155`

Más tarjetas de prueba: https://stripe.com/docs/testing

---

## 📊 Flujo Completo de Prueba

1. **Usuario visita la página de compra** (frontend)
2. **Hace clic en "Buy Pro Pack"**
3. **Frontend llama**: `POST /api/v1/stripe/create-checkout`
4. **Backend crea sesión** y devuelve URL de Stripe
5. **Usuario es redirigido** a Stripe Checkout
6. **Completa el pago** con tarjeta de prueba `4242 4242 4242 4242`
7. **Stripe envía webhook** a `/api/v1/stripe/webhook`
8. **Backend procesa webhook**:
   - Valida firma
   - Identifica paquete (Pro = 200 créditos)
   - Suma créditos al usuario
   - Registra transacción
9. **Usuario redirigido** a success URL
10. **Verificar**: Usuario tiene 200 créditos más

---

## 🔧 Configuración del Webhook en Stripe Dashboard

Para que funcione en **PRODUCCIÓN**, configurar webhook:

1. Ir a: https://dashboard.stripe.com/webhooks
2. Click en **"Add endpoint"**
3. **Endpoint URL**: `https://masterpost.io/api/v1/stripe/webhook`
4. **Events to send**: Seleccionar `checkout.session.completed`
5. Copiar el **Signing secret** (empieza con `whsec_...`)
6. Actualizar en `.env`: `STRIPE_WEBHOOK_SECRET=whsec_...`

**Nota**: El webhook secret actual es para testing local. En producción necesitarás uno nuevo.

---

## 🎨 Ejemplo de Frontend (Next.js)

```typescript
// app/buy-credits/page.tsx
'use client'

import { useState } from 'react'

export default function BuyCreditsPage() {
  const [loading, setLoading] = useState(false)

  const handleBuyPack = async (priceId: string) => {
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/stripe/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price_id: priceId,
          customer_email: 'demo@masterpost.io' // Obtener del contexto de auth
        })
      })

      const { url } = await response.json()

      // Redirigir a Stripe Checkout
      window.location.href = url

    } catch (error) {
      console.error('Error:', error)
      alert('Error al procesar el pago')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Buy Credits</h1>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Starter Pack */}
        <div className="border rounded-lg p-6">
          <h3 className="text-xl font-bold">Starter Pack</h3>
          <p className="text-3xl font-bold my-4">$4.99</p>
          <p className="text-gray-600 mb-4">50 credits</p>
          <button
            onClick={() => handleBuyPack('price_1SLljD3M485N62s33mV2Jx2e')}
            disabled={loading}
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Buy Now
          </button>
        </div>

        {/* Pro Pack */}
        <div className="border rounded-lg p-6 border-blue-500">
          <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded mb-2 inline-block">
            BEST VALUE
          </div>
          <h3 className="text-xl font-bold">Pro Pack</h3>
          <p className="text-3xl font-bold my-4">$17.99</p>
          <p className="text-gray-600 mb-4">200 credits</p>
          <button
            onClick={() => handleBuyPack('price_1SLljE3M485N62s3ieI3a0xv')}
            disabled={loading}
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Buy Now
          </button>
        </div>

        {/* Business Pack */}
        <div className="border rounded-lg p-6">
          <h3 className="text-xl font-bold">Business Pack</h3>
          <p className="text-3xl font-bold my-4">$39.99</p>
          <p className="text-gray-600 mb-4">500 credits</p>
          <button
            onClick={() => handleBuyPack('price_1SLljE3M485N62s3R66Ym6iA')}
            disabled={loading}
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Buy Now
          </button>
        </div>
      </div>
    </div>
  )
}
```

---

## 🚀 Siguiente Paso

Crear la página frontend de compra de créditos usando el ejemplo arriba como referencia.

---

## ✅ Checklist Final

- [x] Stripe router creado (`stripe_routes.py`)
- [x] Métodos de DB implementados (`add_credits`, `log_transaction`)
- [x] Router registrado en `main.py`
- [x] Variables de entorno configuradas
- [x] Credenciales de Stripe agregadas
- [x] Dependencia `stripe` instalada
- [ ] Crear página frontend de compra
- [ ] Probar flujo completo
- [ ] Configurar webhook en Stripe Dashboard para producción

---

## 📞 Soporte

Si hay algún error al probar:
1. Verificar logs del servidor
2. Verificar que el backend esté corriendo en puerto 8000
3. Verificar que las credenciales en `.env` estén correctas
4. Verificar que Stripe CLI esté reenviando webhooks correctamente
