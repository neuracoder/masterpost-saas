# 🔧 Solución Error 500 en `/api/v1/upload`

## 🐛 Problema Identificado

El endpoint `/api/v1/upload` está fallando con error **HTTP 500** al intentar procesar las imágenes.

**Error en consola del navegador**:
```
localhost:8002/api/v1/upload:1 Failed to load resource: the server responded with a status of 500 (Internal Server Error)
Processing error: Error: HTTP 500
```

---

## 🔍 Causa del Error

El código en `backend/app/routers/upload.py` (líneas 192-215) está intentando:

1. **Conectarse a Supabase** para verificar el usuario
2. **Crear un job en Supabase**
3. **Guardar archivos en la base de datos**

```python
# Líneas 192-204: Intento de conexión a Supabase
try:
    supabase_client.get_user_profile(user_id)
except:
    supabase.table('user_profiles').upsert({...}).execute()

# Líneas 205-215: Creación de job en Supabase
job = await supabase_client.create_job(job_data)
```

**Posibles causas**:
- ❌ Supabase no está configurado
- ❌ Credenciales de Supabase incorrectas o faltantes
- ❌ Variable de entorno no configurada
- ❌ Conexión a Supabase fallando

---

## ✅ Solución Temporal (Modo Local)

### Opción 1: Usar Almacenamiento Local (Sin Supabase)

Crear un nuevo endpoint simplificado que NO dependa de Supabase:

**Archivo**: `backend/app/routers/local_upload.py`

```python
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import os
import uuid
from pathlib import Path
import shutil
import json

router = APIRouter()

UPLOAD_DIR = Path("uploads")
JOBS_FILE = Path("jobs.json")  # Simple JSON storage
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Initialize jobs storage
if not JOBS_FILE.exists():
    with open(JOBS_FILE, 'w') as f:
        json.dump({}, f)

def load_jobs():
    with open(JOBS_FILE, 'r') as f:
        return json.load(f)

def save_jobs(jobs):
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)

@router.post("/upload-local")
async def upload_images_local(files: List[UploadFile] = File(...)):
    """Upload endpoint without Supabase dependency"""

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 files allowed")

    # Generate job ID
    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []

    try:
        for file in files:
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}"
                )

            # Validate file size
            if file.size and file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large: {file.filename}"
                )

            # Save file
            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}{file_ext}"
            file_path = job_dir / safe_filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            uploaded_files.append({
                "file_id": file_id,
                "original_name": file.filename,
                "saved_name": safe_filename,
                "size": file.size,
                "path": str(file_path)
            })

        # Save job to JSON file
        jobs = load_jobs()
        jobs[job_id] = {
            "id": job_id,
            "status": "uploaded",
            "pipeline": "pending",
            "total_files": len(uploaded_files),
            "files": uploaded_files,
            "created_at": str(uuid.uuid1().time)
        }
        save_jobs(jobs)

        return {
            "job_id": job_id,
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files_uploaded": len(uploaded_files),
            "job_status": "uploaded"
        }

    except Exception as e:
        # Clean up on error
        if job_dir.exists():
            shutil.rmtree(job_dir)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
```

### Agregar a `main.py`:

```python
from app.routers import local_upload

app.include_router(local_upload.router, prefix="/api/v1", tags=["local-upload"])
```

---

## ✅ Solución Permanente (Configurar Supabase)

### 1. Obtener Credenciales de Supabase

1. Ir a [supabase.com](https://supabase.com)
2. Crear proyecto o usar existente
3. Ir a **Settings** → **API**
4. Copiar:
   - `SUPABASE_URL`
   - `SUPABASE_KEY` (service_role key)

### 2. Configurar Variables de Entorno

**Archivo**: `backend/.env`

```env
# Supabase Configuration
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key-aqui
SUPABASE_SERVICE_KEY=tu-service-role-key-aqui

# App Configuration
ENVIRONMENT=development
DEBUG=true
```

### 3. Verificar Tablas en Supabase

Ejecutar el schema SQL en Supabase:

```sql
-- user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    full_name TEXT,
    plan TEXT DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW()
);

-- jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES user_profiles(id),
    pipeline TEXT,
    total_files INTEGER,
    status TEXT DEFAULT 'uploaded',
    is_zip_upload BOOLEAN DEFAULT false,
    original_filename TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- job_files table
CREATE TABLE IF NOT EXISTS job_files (
    id SERIAL PRIMARY KEY,
    job_id TEXT REFERENCES jobs(id),
    file_id TEXT,
    original_name TEXT,
    saved_name TEXT,
    size BIGINT,
    path TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Reiniciar Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8002
```

---

## 🧪 Testing

### Test con cURL (Local Upload):

```bash
curl -X POST http://localhost:8002/api/v1/upload-local \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg"
```

### Test con Frontend:

```typescript
// En lib/api.ts, cambiar:
const endpoint = '/api/v1/upload';
// Por:
const endpoint = '/api/v1/upload-local';
```

---

## 📊 Diagnóstico Adicional

### Ver logs del backend Python:

En la terminal donde corre el backend, deberías ver algo como:

```
INFO:     127.0.0.1:xxxxx - "POST /api/v1/upload HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  ...
  [Detalles del error]
```

### Verificar conexión a Supabase:

```python
# En backend/test_supabase.py
from app.database.supabase_client import supabase

try:
    result = supabase.table('user_profiles').select("*").limit(1).execute()
    print("✅ Conexión exitosa a Supabase")
    print(result)
except Exception as e:
    print(f"❌ Error de conexión: {e}")
```

Ejecutar:
```bash
cd backend
python test_supabase.py
```

---

## 🎯 Resumen

| Solución | Ventajas | Desventajas |
|----------|----------|-------------|
| **Modo Local** | ✅ Funciona inmediatamente<br>✅ No requiere configuración<br>✅ Simple | ❌ No persistente<br>❌ No multi-usuario<br>❌ Solo para desarrollo |
| **Supabase** | ✅ Persistente<br>✅ Multi-usuario<br>✅ Escalable<br>✅ Producción-ready | ❌ Requiere configuración<br>❌ Requiere cuenta Supabase |

---

## 🔄 Próximos Pasos

1. **Inmediato**: Usar endpoint local para desarrollo
2. **Corto plazo**: Configurar Supabase para producción
3. **Futuro**: Migrar datos de local a Supabase

---

**Desarrollado con ❤️ por Claude Code**
**Fecha**: 2025-10-08
