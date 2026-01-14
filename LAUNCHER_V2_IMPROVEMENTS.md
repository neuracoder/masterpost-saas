# Dual Launcher v2.0 - Mejoras Implementadas

## 🎯 Mejoras Principales

### 1. Detección Automática de Directorio Incorrecto ✅

**Antes:**
```
ERROR - package.json no encontrado en directorio raíz
ERROR - Faltan dependencias. Saliendo...
```

**Ahora:**
```
============================================================
ERROR - Directorio incorrecto detectado
============================================================
Directorio actual: C:\Users\...\SaaS-Proyects

Este script debe ejecutarse desde el directorio del proyecto:
  Masterpost-SaaS/

SOLUCIÓN ENCONTRADA:

  cd Masterpost-SaaS
  python dual_launcher.py

Archivos esperados en el directorio actual:
  ✗ package.json - NO ENCONTRADO
  ✗ backend/ - NO ENCONTRADO
  ✗ app/ - NO ENCONTRADO
============================================================
```

---

### 2. Logging Mejorado con Colores y Archivo ✅

**Características:**
- ✅ **Colores en consola:**
  - 🔴 Rojo para errores
  - 🟡 Amarillo para warnings
  - 🟢 Verde para éxitos
  - ⚪ Blanco para info

- ✅ **Archivo de logs:** `launcher.log`
  - Timestamp para cada mensaje
  - Historial completo de ejecuciones
  - Útil para debugging

**Ejemplo:**
```
[2025-10-20 13:15:42] [SUCCESS] OK - npm v11.5.2 encontrado
[2025-10-20 13:15:43] [SUCCESS] OK - FastAPI y Uvicorn disponibles
[2025-10-20 13:15:43] [ERROR] ERROR - package.json no encontrado
```

---

### 3. Manejo de Errores Detallado ✅

#### npm Errors
```python
# Captura stderr de npm install
try:
    result = subprocess.run(['npm', 'install'], capture_output=True, ...)
except subprocess.CalledProcessError as e:
    self.log(f"ERROR - Fallo al instalar dependencias npm", "ERROR")
    self.log(f"Código de error: {e.returncode}", "ERROR")
    if e.stderr:
        self.log("Detalles del error:", "ERROR")
        for line in e.stderr.split('\n')[:20]:  # First 20 lines
            if line.strip():
                self.log(f"  {line}", "ERROR")
```

#### Python Errors
```python
# Muestra traceback completo
except Exception as e:
    self.log(f"ERROR - Al iniciar backend: {e}", "ERROR")
    import traceback
    self.log(traceback.format_exc(), "ERROR")
```

---

### 4. Monitoreo de stdout y stderr Separados ✅

**Antes:**
- Solo capturaba stdout
- stderr se perdía

**Ahora:**
- Captura stdout → `[FRONTEND]` / `[BACKEND]`
- Captura stderr → `[FRONTEND-ERR]` / `[BACKEND-ERR]`
- Detecta automáticamente palabras clave de error

**Ejemplo:**
```
[FRONTEND] ▲ Next.js 14.2.5
[FRONTEND] - Local: http://localhost:3000
[FRONTEND-ERR] Warning: React.createElement: type is invalid
[BACKEND] INFO:     Uvicorn running on http://0.0.0.0:8002
[BACKEND-ERR] Exception in ASGI application
```

---

### 5. Timeouts para Prevenir Colgado ✅

```python
# npm --version (10 segundos)
result = subprocess.run(['npm', '--version'], timeout=10)

# npm install (5 minutos)
result = subprocess.run(['npm', 'install'], timeout=300)

# Cleanup (5 segundos)
process.wait(timeout=5)
```

**Beneficio:** El launcher no se queda colgado indefinidamente si algo falla.

---

### 6. Verificación Extendida de Dependencias ✅

**Verifica:**
- ✅ npm instalado y respondiendo
- ✅ FastAPI, Uvicorn disponibles
- ✅ rembg, PIL disponibles (procesamiento de imágenes)
- ✅ package.json existe
- ✅ node_modules existe (o instala)
- ✅ backend/ existe
- ✅ backend/server.py existe

**Muestra exactamente qué falta:**
```
ERROR - Paquete Python faltante: rembg
INFO - Ejecuta: pip install fastapi uvicorn rembg pillow
```

---

### 7. Códigos de Salida de Procesos ✅

**Ahora muestra por qué falló un proceso:**
```
ERROR - Frontend se cerró inesperadamente (código: 1)
INFO - Revisa los logs arriba para más detalles
```

**Códigos comunes:**
- `0` - Éxito
- `1` - Error general
- `2` - Mal uso de comando
- `126` - Comando no ejecutable
- `127` - Comando no encontrado

---

### 8. Compatibilidad Multi-plataforma ✅

```python
if sys.platform == "win32":
    # Windows: taskkill
    subprocess.run(f"taskkill /F /PID {pid} /T", ...)
else:
    # Linux/Mac: terminate
    process.terminate()
    process.wait(timeout=5)
```

---

## 📊 Comparativa Antes vs Después

| Característica | v1.0 (Antes) | v2.0 (Ahora) |
|----------------|--------------|--------------|
| **Detección de directorio** | ❌ No | ✅ Sí, con sugerencias |
| **Colores en consola** | ❌ No | ✅ Rojo/Verde/Amarillo |
| **Archivo de logs** | ❌ No | ✅ launcher.log con timestamps |
| **Captura stderr** | ❌ No | ✅ Sí, separado de stdout |
| **Timeouts** | ❌ No | ✅ Sí, para prevenir colgado |
| **Códigos de salida** | ❌ No muestra | ✅ Muestra y explica |
| **Errores de npm** | ❌ Solo mensaje | ✅ Detalles completos |
| **Traceback Python** | ❌ No | ✅ Traceback completo |
| **Verificación deps** | ⚠️ Básica | ✅ Extendida (rembg, PIL) |
| **Sugerencias** | ❌ No | ✅ Comandos de solución |

---

## 🚀 Cómo Usar

### Desde el directorio correcto:
```bash
cd Masterpost-SaaS
python dual_launcher.py
```

### Desde el directorio incorrecto:
```bash
# El launcher detectará el error y te dirá cómo solucionarlo
cd SaaS-Proyects
python Masterpost-SaaS/dual_launcher.py

# Verás:
# ERROR - Directorio incorrecto detectado
# SOLUCIÓN: cd Masterpost-SaaS
```

---

## 📝 Ejemplos de Salida

### ✅ Inicio Exitoso

```
+--------------------------------------------------------------+
|                    > MASTERPOST.IO LAUNCHER                  |
|  Frontend (Next.js):  http://localhost:3000*                 |
|  Backend (FastAPI):   http://localhost:8002                  |
+--------------------------------------------------------------+

Logs guardados en: C:\...\Masterpost-SaaS\launcher.log

Verificando dependencias...
OK - npm v11.5.2 encontrado
OK - FastAPI y Uvicorn disponibles
OK - rembg y PIL disponibles
OK - node_modules encontrado
OK - Directorio backend verificado

Iniciando Frontend (Next.js)...
Iniciando Backend (FastAPI)...
[FRONTEND] > masterpost@0.1.0 dev
[FRONTEND] ▲ Next.js 14.2.5
[FRONTEND] - Local: http://localhost:3000
OK - Frontend listo en http://localhost:3000
[BACKEND] INFO:     Started server process [12345]
[BACKEND] INFO:     Uvicorn running on http://0.0.0.0:8002
OK - Backend listo en http://localhost:8002

Ambos servicios iniciando...
Frontend: http://localhost:3000
Backend:  http://localhost:8002

Presiona Ctrl+C para detener ambos servicios
```

---

### ❌ Error: Directorio Incorrecto

```
+--------------------------------------------------------------+
|                    > MASTERPOST.IO LAUNCHER                  |
+--------------------------------------------------------------+

Logs guardados en: C:\...\SaaS-Proyects\launcher.log

============================================================
ERROR - Directorio incorrecto detectado
============================================================
Directorio actual: C:\Users\Neuracoder\...\SaaS-Proyects

Este script debe ejecutarse desde el directorio del proyecto:
  Masterpost-SaaS/

SOLUCIÓN ENCONTRADA:

  cd Masterpost-SaaS
  python dual_launcher.py

Archivos esperados en el directorio actual:
  ✗ package.json - NO ENCONTRADO
  ✗ backend/ - NO ENCONTRADO
  ✗ app/ - NO ENCONTRADO
============================================================

ERROR - Ejecuta el script desde el directorio correcto
```

---

### ⚠️ Error: Dependencia Faltante

```
Verificando dependencias...
OK - npm v11.5.2 encontrado
ERROR - Paquete Python faltante: rembg
INFO - Ejecuta: pip install fastapi uvicorn rembg pillow

ERROR - Faltan dependencias. Revisa los errores arriba.
```

---

### ❌ Error: Frontend Crash

```
[FRONTEND] ▲ Next.js 14.2.5
[FRONTEND-ERR] Error: Cannot find module 'next/dist/...'
[FRONTEND-ERR]     at Module._resolveFilename (node:internal/modules/cjs/loader:1145:15)
ERROR - Frontend se cerró inesperadamente (código: 1)
INFO - Revisa los logs arriba para más detalles

Deteniendo servicios...
OK - Frontend detenido
OK - Backend detenido

Logs completos en: C:\...\Masterpost-SaaS\launcher.log
```

---

### 🛑 Cierre Manual (Ctrl+C)

```
^CCtrl+C detectado, cerrando servicios...

Deteniendo servicios...
OK - Frontend detenido
OK - Backend detenido

Logs completos en: C:\...\Masterpost-SaaS\launcher.log
```

---

## 🔍 Revisar Logs

```bash
# Ver logs en tiempo real
tail -f launcher.log

# Windows PowerShell
Get-Content launcher.log -Wait

# Ver últimas 50 líneas
tail -n 50 launcher.log

# Windows PowerShell
Get-Content launcher.log -Tail 50

# Buscar errores
grep ERROR launcher.log

# Windows PowerShell
Select-String -Path launcher.log -Pattern "ERROR"
```

---

## 🐛 Troubleshooting

### Si no ves colores en Windows:

```powershell
# Habilita ANSI colors en PowerShell
$PSStyle.OutputRendering = 'Ansi'

# O usa Windows Terminal en lugar de cmd.exe
```

### Si launcher.log no se crea:

- Verifica permisos de escritura en el directorio
- Ejecuta como administrador si es necesario

### Si los servicios no se detienen:

```bash
# Matar todos los procesos Python
taskkill /F /IM python.exe

# Matar todos los procesos Node
taskkill /F /IM node.exe
```

---

## 📈 Mejoras Futuras (Roadmap)

- [ ] GUI con tkinter para ver logs en ventana
- [ ] Health checks automáticos (ping endpoints)
- [ ] Auto-restart si un servicio falla
- [ ] Configuración de puertos personalizados
- [ ] Modo verbose/debug con flag `-v`
- [ ] Export logs a JSON/HTML
- [ ] Notificaciones de escritorio cuando esté listo
- [ ] Docker support

---

## 📚 Archivos Relacionados

- **[dual_launcher.py](dual_launcher.py)** - Script mejorado
- **[DUAL_LAUNCHER_FIX.md](DUAL_LAUNCHER_FIX.md)** - Documentación de correcciones
- **launcher.log** - Archivo de logs (generado automáticamente)

---

## ✅ Changelog

### v2.0 (2025-10-20)
- ✅ **NEW:** Detección automática de directorio incorrecto
- ✅ **NEW:** Sistema de logging con colores (rojo/verde/amarillo)
- ✅ **NEW:** Archivo launcher.log con timestamps
- ✅ **NEW:** Captura separada de stdout y stderr
- ✅ **NEW:** Timeouts para prevenir colgado (10s, 5min, 5s)
- ✅ **NEW:** Verificación extendida de deps (rembg, PIL)
- ✅ **NEW:** Muestra códigos de salida de procesos
- ✅ **NEW:** Traceback completo para excepciones Python
- ✅ **NEW:** Detalles completos de errores de npm
- ✅ **NEW:** Sugerencias automáticas de solución
- ✅ **IMPROVE:** Mejor manejo de errores en cleanup
- ✅ **IMPROVE:** Compatibilidad multi-plataforma (Windows/Linux/Mac)

### v1.2 (2025-10-20)
- ✅ **FIX:** Busca package.json en raíz (estructura Next.js App Router)
- ✅ **FIX:** npm install ejecuta desde directorio correcto

### v1.1 (2025-10-20)
- ~~Versión con estructura incorrecta~~

### v1.0 (Original)
- Versión básica sin detección de errores

---

## 🎉 Resumen

**El dual_launcher.py v2.0 es ahora:**

1. 🎯 **Inteligente** - Detecta errores comunes y sugiere soluciones
2. 📝 **Informativo** - Logs detallados con colores y timestamps
3. 🛡️ **Robusto** - Maneja errores gracefully sin colgarse
4. 🔍 **Debuggable** - Captura todos los errores de stdout/stderr
5. 🚀 **Fácil de usar** - Mensajes claros y ayuda contextual

**¡Ahora con 100% más debugging power!** 🎊
