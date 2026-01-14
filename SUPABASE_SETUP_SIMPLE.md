# 🚀 MASTERPOST.IO V2.0 - SETUP SUPABASE (SIMPLIFICADO)

## ⚡ EJECUCIÓN PASO A PASO

### **PASO 1: Schema Principal**
En Supabase Dashboard → SQL Editor, ejecutar **supabase_schema_clean.sql**:

```sql
-- Copiar y pegar TODO el contenido del archivo:
-- database/supabase_schema_clean.sql
```

### **PASO 2: Row Level Security**
En Supabase Dashboard → SQL Editor, ejecutar **supabase_rls_clean.sql**:

```sql
-- Copiar y pegar TODO el contenido del archivo:
-- database/supabase_rls_clean.sql
```

### **PASO 3: Funciones de Base de Datos**
En Supabase Dashboard → SQL Editor, ejecutar **supabase_functions.sql**:

```sql
-- Copiar y pegar TODO el contenido del archivo:
-- database/supabase_functions.sql
```

### **PASO 4: Verificar Configuración**
1. **Authentication → Settings**: Habilitar Email Auth
2. **Database → Tables**: Verificar que se crearon 10 tablas
3. **Database → Policies**: Verificar que hay políticas RLS activas

---

## 🎮 PROBAR EL SISTEMA

### **1. Iniciar Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **2. Verificar API:**
```bash
# Health check
curl http://localhost:8000/health

# Ver documentación
curl http://localhost:8000/docs
```

### **3. Crear primer usuario:**
```bash
curl -X POST "http://localhost:8000/api/v2/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@masterpost.io",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### **4. Probar login:**
```bash
curl -X POST "http://localhost:8000/api/v2/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@masterpost.io",
    "password": "password123"
  }'
```

---

## 📚 ARCHIVOS CREADOS

- **supabase_schema_clean.sql** - Esquema principal sin comentarios
- **supabase_rls_clean.sql** - Políticas de seguridad simplificadas
- **supabase_functions.sql** - Funciones de base de datos

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### **Error "Could not find table":**
- Ejecutar **supabase_schema_clean.sql** primero
- Verificar que las tablas se crearon en la pestaña Database

### **Error de autenticación:**
- Verificar que Authentication está habilitado
- Verificar que las políticas RLS se aplicaron

### **Error "snippet doesn't exist":**
- Usar los archivos nuevos (_clean.sql)
- Copiar y pegar manualmente el contenido

---

## ✅ ESTADO FINAL ESPERADO

Después de ejecutar los 3 scripts SQL:

- ✅ 10 tablas creadas en Database
- ✅ Políticas RLS activas en todas las tablas
- ✅ Funciones disponibles (check_usage_limit, etc.)
- ✅ Triggers para updated_at automáticos
- ✅ Backend conecta sin errores
- ✅ Endpoints de autenticación funcionando

**¡MASTERPOST.IO estará listo para usuarios reales!** 🎉