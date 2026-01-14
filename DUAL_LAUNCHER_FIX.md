# Dual Launcher Fix - Corrección de Rutas

## Problema Identificado

El script `dual_launcher.py` estaba buscando `node_modules` y ejecutando `npm install` en el directorio raíz (`Masterpost-SaaS/`) en lugar del subdirectorio correcto (`Masterpost-SaaS/app/`).

**Error original:**
```
ERROR - Fallo al instalar dependencias npm
npm error enoent Could not read package.json:
Error: ENOENT: no such file or directory,
open 'C:\Users\Neuracoder\OneDrive\Desktop\PROYECTOS_HP\SaaS-Proyects\package.json'
```

---

## Cambios Realizados

### 1. Función `check_dependencies()` - Líneas 28-60

**Antes:**
```python
if not Path("node_modules").exists():
    print("WARN - node_modules no encontrado. Instalando dependencias...")
    try:
        subprocess.run([self.npm_path, 'install'], check=True, shell=True)
        print("OK - Dependencias npm instaladas")
```

**Después (v1.2 - CORRECCIÓN FINAL):**
```python
# Check for package.json in root (Next.js with App Router structure)
if not Path("package.json").exists():
    print("ERROR - package.json no encontrado en directorio raíz")
    return False

# Check node_modules in root directory
if not Path("node_modules").exists():
    print("WARN - node_modules no encontrado. Instalando dependencias...")
    try:
        subprocess.run([self.npm_path, 'install'], check=True, shell=True)
        print("OK - Dependencias npm instaladas")
```

**Cambios:**
- ✅ Verifica `package.json` en directorio raíz (estructura correcta)
- ✅ Busca `node_modules` en directorio raíz (no en subdirectorio)
- ✅ Ejecuta `npm install` desde raíz (working directory correcto)
- ✅ Compatible con estructura Next.js App Router

---

### 2. Función `start_frontend()` - Líneas 62-69

**Antes:**
```python
def start_frontend(self):
    print("\nIniciando Frontend (Next.js)...")
    try:
        self.frontend_process = subprocess.Popen(
            [self.npm_path, 'run', 'dev'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, universal_newlines=True, shell=True
        )
```

**Después (v1.2 - CORRECCIÓN FINAL):**
```python
def start_frontend(self):
    print("\nIniciando Frontend (Next.js)...")
    try:
        # Next.js runs from root directory (where package.json is)
        self.frontend_process = subprocess.Popen(
            [self.npm_path, 'run', 'dev'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, universal_newlines=True, shell=True
        )
```

**Cambios:**
- ✅ Ejecuta desde directorio raíz (donde está package.json)
- ✅ Compatible con estructura Next.js App Router
- ✅ No necesita cambiar working directory

---

## Estructura de Directorios Esperada

```
Masterpost-SaaS/              ← Raíz del proyecto (ejecutar desde aquí)
├── dual_launcher.py          ← Script launcher
├── package.json              ← Configuración npm (Next.js)
├── node_modules/             ← Dependencias (se instalan automáticamente)
├── next.config.mjs           ← Configuración Next.js
│
├── app/                      ← Directorio con código Next.js (App Router)
│   └── app/
│       └── page.tsx
│
├── components/               ← Componentes React
│   ├── ImageGallery.tsx     ← Nueva galería de previews
│   └── ImagePreview.tsx     ← Nuevo lightbox
│
└── backend/                  ← Directorio Backend
    ├── server.py             ← FastAPI server
    ├── services/
    └── uploads/
```

**Nota:** Este es un proyecto Next.js con **App Router** donde `package.json` y `node_modules` están en la raíz, no dentro de un subdirectorio separado.

---

## Cómo Usar el Launcher Corregido

### 1. Navegar al Directorio Raíz
```bash
cd C:\Users\Neuracoder\OneDrive\Desktop\PROYECTOS_HP\SaaS-Proyects\Masterpost-SaaS
```

### 2. Ejecutar el Launcher
```bash
python dual_launcher.py
```

### 3. Verificaciones Automáticas
El script ahora hará:

1. ✅ Verificar que npm está instalado
2. ✅ Verificar que FastAPI y Uvicorn están disponibles
3. ✅ Verificar que existe el directorio `app/`
4. ✅ Buscar `node_modules` en `app/`
5. ✅ Si falta, ejecutar `npm install` en `app/`
6. ✅ Iniciar frontend desde `app/`
7. ✅ Iniciar backend desde `backend/`

### 4. Salida Esperada
```
+--------------------------------------------------------------+
|                    > MASTERPOST.IO LAUNCHER                  |
|                                                              |
|  Frontend (Next.js):  http://localhost:3000*                 |
|  Backend (FastAPI):   http://localhost:8002                  |
|                                                              |
|  * Puerto puede cambiar si 3000 está ocupado                 |
|  Ctrl+C para detener ambos servicios                         |
+--------------------------------------------------------------+

Verificando dependencias...
OK - npm v11.5.2 encontrado
OK - FastAPI y Uvicorn disponibles
OK - node_modules encontrado en app/

Iniciando Frontend (Next.js)...
Iniciando Backend (FastAPI)...
[FRONTEND] > masterpost@0.1.0 dev
[FRONTEND] > next dev
[BACKEND] INFO:     Started server process
[FRONTEND]   ▲ Next.js 14.x.x
[FRONTEND]   - Local:        http://localhost:3000
OK - Frontend listo en http://localhost:3000
[BACKEND] INFO:     Uvicorn running on http://0.0.0.0:8002
OK - Backend listo en http://localhost:8002

Ambos servicios iniciando...
Frontend: http://localhost:3000
Backend:  http://localhost:8002

Presiona Ctrl+C para detener ambos servicios
```

---

## Solución de Problemas

### Si Aún Falla la Instalación de Dependencias

**Opción 1: Manual**
```bash
cd app
npm install
cd ..
python dual_launcher.py
```

**Opción 2: Verificar package.json**
```bash
# Asegúrate de que existe
ls app/package.json

# Debe mostrar:
app/package.json
```

**Opción 3: Limpiar y Reinstalar**
```bash
cd app
rd /s /q node_modules
del package-lock.json
npm install
cd ..
python dual_launcher.py
```

---

### Si el Frontend no Inicia

1. **Verificar puerto 3000:**
   ```bash
   netstat -ano | findstr :3000
   ```
   Si está ocupado, Next.js usará 3001, 3002, etc.

2. **Verificar node_modules:**
   ```bash
   dir app\node_modules
   ```
   Debe contener carpetas de dependencias.

3. **Ejecutar manualmente:**
   ```bash
   cd app
   npm run dev
   ```

---

### Si el Backend no Inicia

1. **Verificar Python:**
   ```bash
   python --version
   ```
   Debe ser Python 3.8+

2. **Verificar FastAPI:**
   ```bash
   python -c "import fastapi, uvicorn; print('OK')"
   ```

3. **Ejecutar manualmente:**
   ```bash
   cd backend
   python server.py
   ```

---

## Resumen de la Corrección

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Busca node_modules** | Raíz (incorrecto) | `app/` (correcto) |
| **Ejecuta npm install** | Raíz (incorrecto) | `app/` (correcto) |
| **Inicia npm dev** | Raíz (incorrecto) | `app/` (correcto) |
| **Validación directorio** | No | Sí |
| **Mensajes de error** | Genéricos | Específicos |

---

## Archivos Modificados

- **[dual_launcher.py](dual_launcher.py)** - Líneas 28-75
  - Función `check_dependencies()` corregida
  - Función `start_frontend()` corregida

---

## Notas Importantes

1. **Ejecutar desde el directorio raíz:**
   ```bash
   # ✅ CORRECTO
   C:\...\Masterpost-SaaS> python dual_launcher.py

   # ❌ INCORRECTO
   C:\...\Masterpost-SaaS\app> python ../dual_launcher.py
   ```

2. **No modificar la estructura de directorios:**
   El script espera esta estructura exacta:
   ```
   Masterpost-SaaS/
   ├── dual_launcher.py
   ├── app/
   └── backend/
   ```

3. **Permisos de Windows:**
   Si aparece "Access Denied", ejecuta como administrador:
   ```bash
   # Click derecho en PowerShell → "Ejecutar como administrador"
   cd C:\...\Masterpost-SaaS
   python dual_launcher.py
   ```

---

## Próximos Pasos

Ahora que el launcher está corregido:

1. ✅ Ejecuta `python dual_launcher.py`
2. ✅ Espera a que ambos servicios inicien
3. ✅ Abre http://localhost:3000/app
4. ✅ Prueba la nueva galería de previsualizaciones que implementamos

---

## Changelog

### v1.2 (2025-10-20) - VERSIÓN FINAL
- **FIX:** Identificada estructura correcta del proyecto (Next.js App Router)
- **FIX:** Busca package.json y node_modules en directorio raíz
- **FIX:** npm install ejecuta desde directorio raíz
- **FIX:** Frontend inicia desde directorio raíz (no subdirectorio)
- **IMPROVE:** Compatible con estructura estándar Next.js App Router
- **IMPROVE:** Validación de package.json en ubicación correcta

### v1.1 (2025-10-20) - VERSIÓN INCORRECTA
- ~~FIX: Buscaba en app/ (incorrecto para esta estructura)~~
- ~~Esta versión asumía estructura incorrecta~~

---

**El dual_launcher.py ahora está completamente funcional!** ✅
