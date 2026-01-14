# 🚀 Comandos Git para Deploy - Masterpost-SaaS

## ⚡ COMANDOS PARA COPIAR Y PEGAR

### 1️⃣ Verificar que estás en la carpeta correcta

```bash
cd c:\Users\Neuracoder\OneDrive\Desktop\PROYECTOS_HP\SaaS-Proyects\Masterpost-SaaS
pwd
```

**Debe mostrar:** `.../Masterpost-SaaS`

---

### 2️⃣ Verificar que .env NO se va a subir

```bash
git status
```

**IMPORTANTE:** `.env` NO debe aparecer en la lista!
- ✅ SI aparece `.env.example` → OK
- ❌ SI aparece `.env` → PROBLEMA! (verifica .gitignore)

---

### 3️⃣ Inicializar repositorio Git

```bash
git init
```

---

### 4️⃣ Agregar todos los archivos

```bash
git add .
```

---

### 5️⃣ Verificar nuevamente que .env NO está incluido

```bash
git status
```

**Busca en la lista:** `.env` NO debe estar
**Debe estar:** `.env.example`, `.gitignore`, `README.md`, etc.

---

### 6️⃣ Primer commit

```bash
git commit -m "Initial commit: MVP ready for production deployment"
```

---

### 7️⃣ Agregar remote de GitHub

```bash
git remote add origin https://github.com/neuracoder/Masterpost-SaaS.git
```

---

### 8️⃣ Renombrar rama a main

```bash
git branch -M main
```

---

### 9️⃣ Push a GitHub

```bash
git push -u origin main
```

**Si pide autenticación:**
- Usuario: neuracoder
- Contraseña: Tu Personal Access Token de GitHub

**¿No tienes token?**
1. Ve a: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Selecciona: `repo` (full control)
4. Guarda el token (no lo podrás ver después!)

---

### 🔟 Verificar en GitHub

```bash
# Abrir en el navegador
start https://github.com/neuracoder/Masterpost-SaaS
```

**Verifica que existan:**
- ✅ README.md (con contenido profesional)
- ✅ .gitignore (con .env excluido)
- ✅ .env.example (template SIN valores reales)
- ✅ vercel.json (configuración de deployment)
- ✅ backend/requirements.txt (todas las dependencias)
- ✅ backend/img_original/ (6 imágenes)
- ✅ backend/img_procesada/ (6 imágenes)
- ✅ DEPLOYMENT_GUIDE.md
- ❌ .env (NO debe existir!)
- ❌ node_modules/ (NO debe existir!)
- ❌ __pycache__/ (NO debe existir!)

---

## 🎯 Siguiente Paso: Deployment en Vercel

Una vez que hayas verificado que todo está en GitHub correctamente:

1. **Lee:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) (guía completa)
2. **Ve a:** https://vercel.com
3. **Importa:** tu repositorio Masterpost-SaaS
4. **Configura:** environment variables
5. **Deploy!**

---

## ❌ Troubleshooting

### Error: "fatal: remote origin already exists"

```bash
# Eliminar remote existente
git remote remove origin

# Agregar nuevamente
git remote add origin https://github.com/neuracoder/Masterpost-SaaS.git
```

### Error: "Updates were rejected"

```bash
# Force push (SOLO si es un repo nuevo!)
git push -u origin main --force
```

### Error: ".env aparece en git status"

```bash
# Eliminar .env del tracking
git rm --cached .env

# Verificar que .gitignore tiene .env
cat .gitignore | findstr .env

# Debería mostrar: .env

# Commit el cambio
git commit -m "Remove .env from tracking"
```

### Ver qué archivos se van a subir

```bash
# Ver todos los archivos en el staging area
git status --short

# Ver el árbol completo
git ls-files
```

---

## 📂 Estructura que se subirá a GitHub

```
Masterpost-SaaS/
├── .gitignore                      ✅
├── .env.example                    ✅
├── README.md                       ✅
├── vercel.json                     ✅
├── DEPLOYMENT_GUIDE.md             ✅
├── COMANDOS_GIT.md                 ✅ (este archivo)
├── backend/
│   ├── requirements.txt            ✅
│   ├── supabase_setup.sql          ✅
│   ├── app/
│   │   ├── main.py                 ✅
│   │   ├── api/                    ✅
│   │   │   ├── auth.py
│   │   │   ├── credits.py
│   │   │   └── payments.py
│   │   ├── core/                   ✅
│   │   └── routers/                ✅
│   ├── img_original/               ✅ (6 imágenes)
│   └── img_procesada/              ✅ (6 imágenes)
└── frontend/                       ✅
    ├── index.html
    ├── login.html
    ├── signup.html
    ├── css/
    └── js/

# EXCLUIDOS (no se suben):
├── .env                            ❌ (protegido por .gitignore)
├── node_modules/                   ❌
├── __pycache__/                    ❌
├── venv/                           ❌
├── uploads/                        ❌
└── processed/                      ❌
```

---

## ✅ Checklist Final

Antes de hacer push, verifica:

- [ ] Estás en la carpeta `Masterpost-SaaS`
- [ ] `.env` NO aparece en `git status`
- [ ] `.env.example` SÍ aparece en `git status`
- [ ] Las 6 imágenes de ejemplo están en `img_original/` y `img_procesada/`
- [ ] `README.md` tiene contenido profesional
- [ ] `vercel.json` existe
- [ ] `backend/requirements.txt` tiene todas las dependencias
- [ ] Has hecho commit con mensaje descriptivo
- [ ] Remote apunta a `https://github.com/neuracoder/Masterpost-SaaS.git`

---

## 🎉 ¡Listo para hacer push!

```bash
git push -u origin main
```

Después de esto, sigue con **DEPLOYMENT_GUIDE.md** para deployar en Vercel.

---

<div align="center">

**¿Preguntas?** Lee [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

Built with ❤️ by [Neuracoder](https://neuracoder.com)

</div>
