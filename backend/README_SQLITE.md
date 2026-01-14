# Masterpost.io - SQLite Backend

## ✨ Arquitectura Simplificada

Este backend usa SQLite en lugar de Supabase para una arquitectura ultra-simplificada:

- **3 tablas** en lugar de 15+
- **1 archivo de base de datos** (`backend/data/masterpost.db`)
- **Autenticación simple**: Email + Código de Acceso (sin JWT, sin OAuth)
- **Sin dependencias externas** de base de datos

## 🚀 Quick Start

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Crear usuario demo

```bash
python quick_start.py
```

Este comando:
- Crea la base de datos SQLite
- Genera un usuario demo con 500 créditos
- Muestra el código de acceso

**⚠️ IMPORTANTE**: Guarda el código de acceso que se muestra. Lo necesitarás para hacer login.

### 3. Iniciar el servidor

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Verificar que funciona

```bash
curl http://localhost:8000/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "database": "sqlite",
  "version": "2.0.0 (SQLite migration)"
}
```

## 📚 API Endpoints

### Autenticación

#### Crear Usuario (Admin)
```bash
POST /api/v1/auth/create-user
Content-Type: application/json

{
  "email": "user@example.com",
  "initial_credits": 100
}
```

**Respuesta:**
```json
{
  "success": true,
  "email": "user@example.com",
  "access_code": "MP-XXXX-XXXX",
  "credits": 100,
  "message": "User created successfully"
}
```

#### Validar Acceso
```bash
POST /api/v1/auth/validate
Content-Type: application/json

{
  "email": "user@example.com",
  "access_code": "MP-XXXX-XXXX"
}
```

**Respuesta:**
```json
{
  "success": true,
  "email": "user@example.com",
  "credits": 100,
  "message": "Access granted"
}
```

#### Obtener Créditos
```bash
GET /api/v1/auth/credits
x-user-email: user@example.com
```

**Respuesta:**
```json
{
  "email": "user@example.com",
  "credits": 95
}
```

### Procesamiento de Imágenes

Todos los endpoints de procesamiento requieren el header `x-user-email`:

#### Upload
```bash
POST /api/v1/upload
x-user-email: user@example.com
Content-Type: multipart/form-data

files: [archivo1.jpg, archivo2.jpg]
use_premium: false
```

#### Process
```bash
POST /api/v1/process
x-user-email: user@example.com
Content-Type: application/json

{
  "job_id": "uuid-del-job",
  "pipeline": "amazon",
  "settings": {"use_premium": false}
}
```

#### Status
```bash
GET /api/v1/status/{job_id}
```

#### Download
```bash
GET /api/v1/download/{job_id}
```

## 💳 Sistema de Créditos

### Costo por Imagen

- **Procesamiento local (rembg)**: 1 crédito por imagen
- **Procesamiento premium (Qwen API)**: 3 créditos por imagen

### Validación

1. Al hacer **upload**, el sistema valida que tengas suficientes créditos
2. Al iniciar **procesamiento**, se deducen los créditos
3. Si no tienes suficientes créditos, recibirás un error `402 Payment Required`

### Agregar Créditos Manualmente

```python
from app.database_sqlite.sqlite_client import sqlite_client

# Agregar 100 créditos
sqlite_client.add_credits("user@example.com", 100)

# Ver créditos actuales
credits = sqlite_client.get_user_credits("user@example.com")
print(f"Credits: {credits}")
```

## 🗄️ Base de Datos SQLite

### Estructura

```sql
-- Tabla de usuarios
users (
  email TEXT PRIMARY KEY,
  access_code TEXT UNIQUE,
  credits INTEGER,
  created_at TIMESTAMP,
  last_used_at TIMESTAMP
)

-- Tabla de trabajos
jobs (
  id TEXT PRIMARY KEY,
  email TEXT,
  status TEXT,
  pipeline TEXT,
  total_files INTEGER,
  processed_files INTEGER,
  failed_files INTEGER,
  settings TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Tabla de transacciones
transactions (
  id INTEGER PRIMARY KEY,
  email TEXT,
  transaction_type TEXT,
  credits_added INTEGER,
  amount_paid REAL,
  stripe_session_id TEXT,
  created_at TIMESTAMP
)
```

### Ubicación

```
backend/data/masterpost.db
```

### Backup

Para hacer backup, simplemente copia el archivo:

```bash
cp backend/data/masterpost.db backend/data/masterpost_backup_$(date +%Y%m%d).db
```

### Explorar la Base de Datos

```bash
sqlite3 backend/data/masterpost.db

# Comandos útiles:
.tables                    # Ver tablas
.schema users             # Ver estructura
SELECT * FROM users;      # Ver usuarios
SELECT * FROM jobs;       # Ver trabajos
```

## 🧪 Testing

### Script de Test Completo

```bash
python backend/test_sqlite.py
```

### Test Manual

```python
import sys
sys.path.insert(0, 'backend')

from app.database_sqlite.sqlite_client import sqlite_client

# Crear usuario
user = sqlite_client.create_user("test@test.com", credits=100)
print(f"Access code: {user['access_code']}")

# Validar
is_valid = sqlite_client.validate_access("test@test.com", user['access_code'])
print(f"Valid: {is_valid}")

# Ver créditos
credits = sqlite_client.get_user_credits("test@test.com")
print(f"Credits: {credits}")
```

## 🔧 Troubleshooting

### Error: "No module named 'app'"

Asegúrate de estar en el directorio correcto:

```bash
cd backend
python -c "import sys; sys.path.insert(0, '.'); from app.database_sqlite.sqlite_client import sqlite_client; print('OK')"
```

### Error: "Database locked"

SQLite puede bloquear si hay múltiples escrituras simultáneas. Esto es normal y el sistema reintentará.

### Error: "User already exists"

Si intentas crear un usuario que ya existe, recibirás `None`. Esto no es un error, solo significa que el usuario ya está en la base de datos.

### Resetear la Base de Datos

```bash
rm backend/data/masterpost.db
python backend/quick_start.py
```

## 🔐 Seguridad

### Códigos de Acceso

- Formato: `MP-XXXX-XXXX`
- Generados con `secrets.choice()` (criptográficamente seguros)
- Únicos por usuario
- Se validan en cada request mediante el header `x-user-email`

### Headers Requeridos

Todos los endpoints protegidos requieren:

```
x-user-email: user@example.com
```

El API client (`lib/api.ts`) agrega este header automáticamente desde `localStorage`.

## 📊 Monitoreo

### Ver Usuarios Activos

```python
from app.database_sqlite.sqlite_client import sqlite_client
conn = sqlite_client._get_connection()
cursor = conn.execute("""
    SELECT email, credits, last_used_at
    FROM users
    ORDER BY last_used_at DESC
    LIMIT 10
""")
for row in cursor:
    print(dict(row))
conn.close()
```

### Ver Jobs Recientes

```python
from app.database_sqlite.sqlite_client import sqlite_client
conn = sqlite_client._get_connection()
cursor = conn.execute("""
    SELECT id, email, status, total_files, created_at
    FROM jobs
    ORDER BY created_at DESC
    LIMIT 10
""")
for row in cursor:
    print(dict(row))
conn.close()
```

## 🚀 Producción

### Variables de Entorno

```bash
# .env
DASHSCOPE_API_KEY=your_qwen_api_key  # Solo para procesamiento premium
```

### Consideraciones

1. **Backup automático**: Configura un cron job para hacer backup del `.db`
2. **Límites de SQLite**: SQLite soporta hasta ~140TB de datos y miles de requests/segundo
3. **Concurrencia**: SQLite maneja bien lecturas concurrentes, escrituras son serializadas
4. **Migración futura**: Si creces mucho, puedes migrar a PostgreSQL usando un script

---

**¿Preguntas?** Consulta [SQLITE_MIGRATION_COMPLETE.md](../SQLITE_MIGRATION_COMPLETE.md) para más detalles.
