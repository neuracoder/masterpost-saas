# Comandos SCP para Deploy de 3 Nuevos Artículos del Blog

## Archivos creados/modificados:

```
app/blog/posts/
├── ebay-image-requirements-2025.tsx      → Artículo eBay (NUEVO)
├── instagram-product-images-guide.tsx    → Artículo Instagram (NUEVO)
└── background-removal-guide.tsx          → Artículo Background Removal (NUEVO)

app/blog/[slug]/
└── page.tsx                              → Actualizado con nuevos componentes

lib/
└── blog-data.ts                          → Actualizado con 3 nuevos posts

public/blog/
├── ebay-requirements-cover.jpg           → Placeholder (REEMPLAZAR)
├── instagram-guide-cover.jpg             → Placeholder (REEMPLAZAR)
└── background-removal-cover.jpg          → Placeholder (REEMPLAZAR)

components/blog/
└── RelatedPosts.tsx                      → Arreglado bg-white sólido
```

---

## IMPORTANTE: Imágenes de Portada

Antes de hacer deploy, crear las imágenes reales con NanaBanana:

| Archivo | Tamaño | Contenido sugerido |
|---------|--------|-------------------|
| `ebay-requirements-cover.jpg` | 1200x630px | eBay theme, product photos, seller dashboard |
| `instagram-guide-cover.jpg` | 1200x630px | Instagram Shopping, product grid, social commerce |
| `background-removal-cover.jpg` | 1200x630px | Before/after comparison, AI processing visual |

---

## Comandos SCP para Subir Todo

### Opción 1: Comandos individuales (PowerShell/CMD)

```powershell
# 1. Subir los 3 nuevos artículos
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\app\blog\posts\ebay-image-requirements-2025.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/posts/

scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\app\blog\posts\instagram-product-images-guide.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/posts/

scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\app\blog\posts\background-removal-guide.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/posts/

# 2. Subir page.tsx actualizado (con imports de nuevos artículos)
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\app\blog\[slug]\page.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/\[slug\]/

# 3. Subir blog-data.ts actualizado
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\lib\blog-data.ts" root@49.13.145.150:/root/masterpost-saas/lib/

# 4. Subir imágenes de portada (después de crearlas con NanaBanana)
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\public\blog\ebay-requirements-cover.jpg" root@49.13.145.150:/root/masterpost-saas/public/blog/

scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\public\blog\instagram-guide-cover.jpg" root@49.13.145.150:/root/masterpost-saas/public/blog/

scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\public\blog\background-removal-cover.jpg" root@49.13.145.150:/root/masterpost-saas/public/blog/

# 5. Subir RelatedPosts.tsx arreglado (bg-white sólido)
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\components\blog\RelatedPosts.tsx" root@49.13.145.150:/root/masterpost-saas/components/blog/
```

### Opción 2: Comando único con todos los archivos

```bash
# Desde Linux/Mac o Git Bash en Windows
scp -r \
  app/blog/posts/ebay-image-requirements-2025.tsx \
  app/blog/posts/instagram-product-images-guide.tsx \
  app/blog/posts/background-removal-guide.tsx \
  root@49.13.145.150:/root/masterpost-saas/app/blog/posts/

scp "app/blog/[slug]/page.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/\[slug\]/
scp lib/blog-data.ts root@49.13.145.150:/root/masterpost-saas/lib/
scp components/blog/RelatedPosts.tsx root@49.13.145.150:/root/masterpost-saas/components/blog/
scp public/blog/*.jpg root@49.13.145.150:/root/masterpost-saas/public/blog/
```

---

## Post-Deploy: Comandos en el Servidor

```bash
# Conectar al servidor
ssh root@49.13.145.150

# Ir al directorio del proyecto
cd /root/masterpost-saas

# Build del proyecto
npm run build

# Reiniciar la aplicación (PM2)
pm2 restart masterpost

# O si usas otro método:
# systemctl restart masterpost
# docker-compose up -d --build
```

---

## URLs de los Nuevos Artículos

| Artículo | URL |
|----------|-----|
| eBay Image Requirements | `/blog/ebay-image-requirements-2025` |
| Instagram Shopping Guide | `/blog/instagram-product-images-guide` |
| Background Removal Guide | `/blog/background-removal-guide` |

---

## Verificación Post-Deploy

1. ✅ Visitar `/blog` - Verificar que aparecen los 4 artículos
2. ✅ Verificar cada artículo individual:
   - `/blog/ebay-image-requirements-2025`
   - `/blog/instagram-product-images-guide`
   - `/blog/background-removal-guide`
3. ✅ Verificar Table of Contents en sidebar (bg-white sólido)
4. ✅ Verificar Related Posts en cada artículo
5. ✅ Probar en móvil (responsive)
6. ✅ Verificar imágenes de portada

---

## Resumen de Artículos

| Artículo | Palabras | Categoría | Featured |
|----------|----------|-----------|----------|
| Amazon Image Requirements | ~2000 | Amazon Selling | ✅ Yes |
| eBay Image Requirements | ~1600 | eBay Selling | No |
| Instagram Shopping Guide | ~1500 | Social Commerce | No |
| Background Removal Guide | ~1700 | Image Editing | ✅ Yes |

**Total: 4 artículos, ~6800 palabras de contenido SEO**
