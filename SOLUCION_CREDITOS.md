# 🔧 SOLUCIÓN: HTTP 402 Payment Required

## 📊 DIAGNÓSTICO

**Problema**: El endpoint `/api/v1/process` retorna HTTP 402 porque:
1. Usuario autenticado: `48beba84-bbe5-493b-906d-b98790951d9d`
2. La función `get_user_credits()` está fallando o retornando 0 créditos
3. El código requiere créditos antes de procesar:
   - **BASIC (rembg)**: 1 crédito por imagen
   - **PREMIUM (Qwen)**: 3 créditos por imagen

**Ubicación del código**: `backend/server.py` líneas 540-576

---

## ✅ SOLUCIÓN 1: Dar créditos en Supabase (RECOMENDADO)

### Paso 1: Ir a Supabase Dashboard

1. Ir a: https://supabase.com/dashboard
2. Seleccionar proyecto: `vzjcmpvtavfqffjkzpdo`
3. Ir a **SQL Editor**

### Paso 2: Ejecutar SQL

Copiar y pegar este SQL (también está en `fix_user_credits.sql`):

```sql
-- Verificar créditos actuales
SELECT user_id, credits, created_at, updated_at
FROM public.user_credits
WHERE user_id = '48beba84-bbe5-493b-906d-b98790951d9d';

-- Dar 1000 créditos al usuario
INSERT INTO public.user_credits (user_id, credits, created_at, updated_at)
VALUES (
  '48beba84-bbe5-493b-906d-b98790951d9d',
  1000,
  NOW(),
  NOW()
)
ON CONFLICT (user_id)
DO UPDATE SET
  credits = 1000,
  updated_at = NOW();

-- Verificar que se aplicó
SELECT user_id, credits FROM public.user_credits
WHERE user_id = '48beba84-bbe5-493b-906d-b98790951d9d';
```

### Paso 3: Reintentar

1. Volver al frontend
2. Hacer clic en **Process Images**
3. Debería funcionar ✅

---

## 🚀 SOLUCIÓN 2: Modo desarrollo (bypass créditos)

Si no querés tocar Supabase, podés agregar un modo DEBUG en el código.

### Modificar `backend/server.py`

**Buscar línea ~540** (donde dice `# VERIFY CREDITS BEFORE PROCESSING`):

```python
# VERIFY CREDITS BEFORE PROCESSING
if user_id:
    # 👇 AGREGAR ESTA LÍNEA
    DEBUG_MODE = os.getenv("DEBUG_SKIP_CREDITS", "false").lower() == "true"

    if DEBUG_MODE:
        logger.warning("⚠️  DEBUG MODE: Skipping credit verification")
    else:
        credits_per_image = 3 if use_premium else 1
        total_credits_needed = credits_per_image * len(image_files)

        # ... resto del código de verificación ...
```

### Agregar a `.env`

```bash
DEBUG_SKIP_CREDITS=true
```

### Reiniciar servidor

```bash
# Ctrl+C en la terminal del dual_launcher
python dual_launcher.py
```

---

## 🎯 SOLUCIÓN 3: Modo anónimo (sin autenticación)

El código ya tiene una condición para usuarios NO autenticados:

```python
else:
    logger.warning("⚠️  No user authentication - processing without credit check")
```

**Para activarlo:**
1. Ir al frontend
2. Desloguear (si hay botón de logout)
3. O borrar el token de localStorage en DevTools:
   ```js
   localStorage.removeItem('supabase.auth.token')
   ```
4. Recargar página
5. Subir imágenes sin estar logueado

---

## 📋 VERIFICACIÓN

Para ver los logs en tiempo real mientras procesas:

```bash
# En una terminal aparte
tail -f launcher.log
```

Deberías ver:
```
💳 CREDIT VERIFICATION
   User: 48beba84...
   Images: 1
   Processing: BASIC (rembg)
   Credits per image: 1
   Total credits needed: 1
✅ CREDIT VERIFICATION PASSED
   Current credits: 1000
   Will deduct: 1
   Remaining after: 999
```

---

## 🔍 DEBUG: Verificar si get_user_credits funciona

Podés probar la función directamente en Python:

```python
import asyncio
from backend.app.services.credit_service import get_user_credits

async def test():
    result = await get_user_credits('48beba84-bbe5-493b-906d-b98790951d9d')
    print(result)

asyncio.run(test())
```

**Resultado esperado**:
```python
{'user_id': '48beba84-bbe5-493b-906d-b98790951d9d', 'credits': 1000}
```

**Si retorna error**, el problema está en la función RPC de Supabase.

---

## 🎯 RECOMENDACIÓN

**Para desarrollo local**: Usar **SOLUCIÓN 2** (DEBUG_MODE)

**Para producción**: Usar **SOLUCIÓN 1** (dar créditos reales)

**Para testing rápido**: Usar **SOLUCIÓN 3** (modo anónimo)

---

## 📞 SI SIGUE FALLANDO

1. Verificar que `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` están en `.env`
2. Verificar que la función `get_user_credits(p_user_id UUID)` existe en Supabase
3. Revisar logs del backend para ver el error exacto:
   ```bash
   grep "Error getting credits" launcher.log
   ```

¿Con cuál solución querés arrancar?
