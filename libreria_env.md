# 📚 Librería de Variables de Entorno (Masterpost.io)

Este archivo contiene una recopilación de todas las variables de entorno utilizadas en el proyecto, extraídas de los archivos `.env` (Frontend) y `backend/.env`.

> [!IMPORTANT]
> **SEGURIDAD**: Este archivo contiene credenciales sensibles. **NO LO COMPARTAS** ni lo subas a repositorios públicos. Asegúrate de que esté incluido en `.gitignore`.

---

## 🖥️ Backend (`backend/.env`)

Configuración para el servidor FastAPI y servicios de backend.

```env
# Qwen AI (Alibaba Cloud)
DASHSCOPE_API_KEY=sk-41cb19a4a3a04ab8974a9abf0f4b34ee

# Server Configuration
PORT=8002
API_V1_STR=/api/v1
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Supabase (Backend Connection)
SUPABASE_URL=https://vzjcmpvtavfqffjkzpdo.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ6amNtcHZ0YXZmcWZmamt6cGRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNzIzNjAsImV4cCI6MjA3Njg0ODM2MH0.S23uT3XaBuBTP3IJmEwjPQp-Gm0MD8ddCs62IJi4ba0
SUPABASE_JWT_SECRET=u8adt4kuBetghDIkCqnWzqQj/cpzzsVN7pt5mgYSBXDShY1SwF2d8GTPudsVA4bfrh1NAGe2PZlWJGqRlPAJkQ==
```

---

## 🌐 Frontend / Root (`.env`)

Configuración para la aplicación Next.js y conexión cliente a Supabase.

```env
# Environment
ENVIRONMENT=development

# Supabase (Client Connection)
SUPABASE_URL=https://vzjcmpvtavfqffjkzpdo.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ6amNtcHZ0YXZmcWZmamt6cGRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNzIzNjAsImV4cCI6MjA3Njg0ODM2MH0.S23uT3XaBuBTP3IJmEwjPQp-Gm0MD8ddCs62IJi4ba0

# Supabase Admin (Service Role - SENSITIVE)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ6amNtcHZ0YXZmcWZmamt6cGRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTI3MjM2MCwiZXhwIjoyMDc2ODQ4MzYwfQ.RNM7k4pBkeerctRv2is3bDGYOhwU9TNTiql_EXmlYjs

# Next.js Public Key
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ6amNtcHZ0YXZmcWZmamt6cGRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNzIzNjAsImV4cCI6MjA3Njg0ODM2MH0.S23uT3XaBuBTP3IJmEwjPQp-Gm0MD8ddCs62IJi4ba0
```

---

## 🔑 Resumen de Claves

| Servicio | Variable | Valor (Parcial) |
|----------|----------|-----------------|
| **Qwen AI** | `DASHSCOPE_API_KEY` | `sk-41cb...` |
| **Supabase URL** | `SUPABASE_URL` | `https://vzjcmp...` |
| **Supabase Anon** | `SUPABASE_KEY` / `ANON_KEY` | `eyJhbG...` |
| **Supabase Admin** | `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbG...` |
| **JWT Secret** | `SUPABASE_JWT_SECRET` | `u8adt4...` |
