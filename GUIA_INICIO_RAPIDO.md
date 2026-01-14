# 🚀 Guía de Inicio Rápido - Masterpost.io

## ✅ Sistema de Autenticación Migrado

El sistema ahora usa **Email + Código de Acceso** en lugar de Supabase.

---

## 📋 Pasos para Iniciar

### 1. Crear Usuario Demo (PRIMERO)

```bash
cd backend
python quick_start.py
```

**Guarda el código que aparece** (formato: `MP-XXXX-XXXX`)

Ejemplo de salida:
```
Your credentials:
  Email:       demo@masterpost.io
  Access Code: MP-A9TS-IZJR
  Credits:     500
```

---

### 2. Iniciar el Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Deberías ver:
```
INFO: Starting Masterpost.io API v2.0 (SQLite)
INFO: ✅ SQLite database initialized successfully
```

---

### 3. Iniciar el Frontend

```bash
# En otra terminal, desde la raíz del proyecto
npm run dev
```

---

### 4. Acceder a la Aplicación

1. Abre el navegador en: `http://localhost:3000`

2. Click en **"Login"** o **"Start Free"**

3. Serás redirigido a: `http://localhost:3000/login`

4. **Ingresa tus credenciales**:
   - Email: `demo@masterpost.io`
   - Código: `MP-A9TS-IZJR` (el que obtuviste en el paso 1)

5. Click en **"Ingresar"**

6. Serás redirigido a: `http://localhost:3000/app`

---

## 🎯 Cómo Funciona

### Sistema de Autenticación

| Aspecto | Descripción |
|---------|-------------|
| **No hay passwords** | Solo email + código de acceso |
| **Formato del código** | `MP-XXXX-XXXX` (8 caracteres) |
| **Storage** | `localStorage` (mp_email, mp_access_code) |
| **Header automático** | El API client agrega `x-user-email` |
| **Logout** | Elimina datos de localStorage |

### Flujo de Autenticación

```
1. Usuario ingresa email + código en /login
   ↓
2. Sistema valida con backend (/api/v1/auth/validate)
   ↓
3. Si válido → Guarda en localStorage
   ↓
4. Redirect a /app
   ↓
5. SimpleAuthContext carga automáticamente
   ↓
6. API client agrega header x-user-email a todas las requests
```

---

## 💳 Sistema de Créditos

### Costos

- **Procesamiento local (rembg)**: 1 crédito/imagen
- **Procesamiento premium (Qwen)**: 3 créditos/imagen

### Cómo se Validan

1. **Al subir**: Verifica que tengas suficientes créditos
2. **Al procesar**: Deduce los créditos
3. **Ver balance**: Click en el badge de créditos en el header

### Agregar Créditos Manualmente

```python
cd backend
python -c "
from app.database_sqlite.sqlite_client import sqlite_client
sqlite_client.add_credits('demo@masterpost.io', 100)
print('✅ 100 créditos agregados')
"
```

---

## 🔑 Crear Más Usuarios

### Opción 1: Python Script

```python
cd backend
python -c "
from app.database_sqlite.sqlite_client import sqlite_client
user = sqlite_client.create_user('tu@email.com', credits=200)
print(f'Email: {user[\"email\"]}')
print(f'Código: {user[\"access_code\"]}')
print(f'Créditos: {user[\"credits\"]}')
"
```

### Opción 2: cURL

```bash
curl -X POST http://localhost:8000/api/v1/auth/create-user \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@usuario.com",
    "initial_credits": 100
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "email": "nuevo@usuario.com",
  "access_code": "MP-ZZZZ-ZZZZ",
  "credits": 100,
  "message": "User created successfully"
}
```

---

## 🧪 Testing

### Ver Usuarios Existentes

```bash
sqlite3 backend/data/masterpost.db "SELECT email, access_code, credits FROM users;"
```

### Probar Autenticación

```bash
curl -X POST http://localhost:8000/api/v1/auth/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@masterpost.io",
    "access_code": "MP-A9TS-IZJR"
  }'
```

### Ver Créditos

```bash
curl http://localhost:8000/api/v1/auth/credits \
  -H "x-user-email: demo@masterpost.io"
```

---

## 🔄 Flujo Completo de Uso

### 1. Login
- Ir a `http://localhost:3000`
- Click "Login"
- Ingresar email + código
- Click "Ingresar"

### 2. Upload
- En `/app`, arrastra imágenes o ZIP
- Selecciona pipeline (Amazon/Instagram/eBay)
- Opcional: Marca "Premium" para Qwen API
- Click "Upload"

### 3. Process
- Espera confirmación de upload
- Click "Start Processing"
- Los créditos se deducen automáticamente
- Ver progreso en tiempo real

### 4. Download
- Cuando termine, click "Download Results"
- Se descarga ZIP con imágenes procesadas

---

## 📁 Estructura del Proyecto

```
Masterpost-SaaS/
├── app/
│   ├── login/
│   │   └── page.tsx          # Nueva página de login
│   ├── app/
│   │   └── page.tsx          # App principal (actualizada)
│   ├── contexts/
│   │   └── SimpleAuthContext.tsx  # Context de autenticación
│   ├── layout.tsx            # Layout con SimpleAuthProvider
│   └── page.tsx              # Homepage (actualizada)
│
├── lib/
│   └── api.ts                # API client (actualizado con x-user-email)
│
└── backend/
    ├── app/
    │   ├── database_sqlite/
    │   │   ├── schema.sql           # Esquema SQLite
    │   │   ├── sqlite_client.py     # Cliente SQLite
    │   │   └── __init__.py
    │   ├── routers/
    │   │   ├── simple_auth.py       # Router de autenticación
    │   │   ├── upload.py            # Upload (actualizado)
    │   │   ├── process.py           # Process (actualizado)
    │   │   └── ...
    │   └── main.py                  # FastAPI app (actualizada)
    │
    ├── data/
    │   └── masterpost.db            # Base de datos SQLite
    │
    ├── quick_start.py               # Script de inicio
    └── test_sqlite.py               # Tests
```

---

## ⚠️ Troubleshooting

### Error: "Invalid email or access code"

**Causa**: Código incorrecto o usuario no existe

**Solución**:
```bash
# Ver todos los usuarios
sqlite3 backend/data/masterpost.db "SELECT * FROM users;"
```

### Error: "Backend debe estar corriendo..."

**Causa**: Backend no está iniciado

**Solución**:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Error: "Insufficient credits"

**Causa**: No tienes suficientes créditos

**Solución**:
```python
from app.database_sqlite.sqlite_client import sqlite_client
sqlite_client.add_credits('tu@email.com', 100)
```

### Los créditos no se actualizan

**Solución**: Click en el badge de créditos en el header

### No redirige al login

**Solución**:
1. Abre Console (F12)
2. Ejecuta: `localStorage.clear()`
3. Recarga la página

---

## 📱 Usar desde el Navegador

Si solo quieres probar sin hacer login completo:

1. Abre Console (F12) en `http://localhost:3000`
2. Ejecuta:

```javascript
localStorage.setItem('mp_email', 'demo@masterpost.io');
localStorage.setItem('mp_access_code', 'MP-A9TS-IZJR');
location.reload();
```

---

## 🎨 Páginas Disponibles

| URL | Descripción | Requiere Auth |
|-----|-------------|---------------|
| `/` | Homepage (landing) | No |
| `/login` | Página de login | No |
| `/app` | App principal | **Sí** |
| `/dashboard` | Dashboard | **Sí** |
| `/manual-editor` | Editor manual | **Sí** |

---

## 💡 Tips

### Desarrollo Rápido

1. **Usuario demo siempre disponible**:
   - Email: `demo@masterpost.io`
   - Código: `MP-A9TS-IZJR`
   - Créditos: 500

2. **Refrescar créditos**: Click en el badge verde del header

3. **Logout rápido**: Botón "Salir" en el header

4. **Ver logs**: Terminal del backend muestra todas las operaciones

### Producción

1. **Cambiar API URL** en `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=https://tu-dominio.com
   ```

2. **Backup de DB**:
   ```bash
   cp backend/data/masterpost.db backend/data/backup_$(date +%Y%m%d).db
   ```

3. **Eliminar usuario demo** (producción):
   ```bash
   sqlite3 backend/data/masterpost.db "DELETE FROM users WHERE email='demo@masterpost.io';"
   ```

---

## ✅ Checklist de Verificación

Antes de empezar, verifica:

- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 3000
- [ ] Usuario demo creado con `quick_start.py`
- [ ] Código de acceso guardado
- [ ] Base de datos existe en `backend/data/masterpost.db`

---

## 📚 Documentación Adicional

- [MIGRATION_SUCCESS.md](MIGRATION_SUCCESS.md) - Detalles técnicos de la migración
- [SQLITE_MIGRATION_COMPLETE.md](SQLITE_MIGRATION_COMPLETE.md) - Guía completa
- [backend/README_SQLITE.md](backend/README_SQLITE.md) - Documentación del backend
- [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) - Integración frontend

---

**¡Listo para empezar! 🚀**

Si tienes problemas, revisa los logs del backend y verifica que el usuario exista en la base de datos.
