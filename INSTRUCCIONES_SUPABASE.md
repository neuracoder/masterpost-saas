# 🚀 INSTRUCCIONES PARA CONFIGURAR SUPABASE

## ✅ **LO QUE YA ESTÁ LISTO:**

- ✅ Backend implementado completamente
- ✅ Stripe instalado
- ✅ Archivos de configuración actualizados
- ✅ Script SQL preparado

---

## 📋 **LO QUE NECESITAS HACER AHORA (5 minutos):**

### **Paso 1: Ejecutar SQL en Supabase**

1. **Abre tu navegador** y ve a: https://supabase.com/dashboard

2. **Inicia sesión** con tu cuenta de Supabase

3. **Selecciona tu proyecto**: `cvytoscpsmfagiuglopy`

4. **Haz clic en el ícono "SQL Editor"** (🗄️) en la barra lateral izquierda

5. **Haz clic en el botón "New Query"** (arriba a la derecha)

6. **Abre el archivo**: `backend/supabase_setup.sql` (en VS Code o cualquier editor)

7. **Copia TODO el contenido** del archivo (Ctrl+A → Ctrl+C)

8. **Pega** el contenido en el SQL Editor de Supabase

9. **Haz clic en "Run"** (botón verde) o presiona **Ctrl+Enter**

10. **Espera a que termine** - Deberías ver: "Success. No rows returned"

---

### **Paso 2: Verificar que las tablas se crearon**

1. **Haz clic en "Table Editor"** (📊) en la barra lateral

2. **Verifica que existan estas 3 tablas:**
   - ✅ `user_credits`
   - ✅ `transactions`
   - ✅ `stripe_customers`

3. **Si las ves**, ¡LISTO! ✅

---

### **Paso 3: Verificar las funciones**

Vuelve al **SQL Editor** y ejecuta esta consulta:

```sql
SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('use_credits', 'add_credits', 'get_user_credits');
```

**Deberías ver 3 funciones:**
- ✅ `use_credits`
- ✅ `add_credits`
- ✅ `get_user_credits`

---

## 🎉 **¡CONFIGURACIÓN COMPLETA!**

Una vez que hayas completado estos pasos, dime:

**"Listo, las tablas están creadas"**

Y yo continuaré con:
- ✅ Iniciar el backend
- ✅ Probar los endpoints
- ✅ Implementar el frontend

---

## ❓ **¿Problemas?**

**Error: "relation already exists"**
- Esto significa que las tablas ya existen. ¡Perfecto! Continúa.

**Error: "permission denied"**
- Verifica que estés usando tu cuenta correcta de Supabase

**No veo el proyecto `cvytoscpsmfagiuglopy`**
- Verifica que estés en la organización correcta

---

**¿Necesitas ayuda con algún paso?** Dime en qué parte estás y te guío.
