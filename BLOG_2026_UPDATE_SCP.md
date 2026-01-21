# Comandos SCP - Actualización 2025 → 2026

## Cambios realizados:

1. **Títulos y slugs actualizados:**
   - `amazon-image-requirements-2025` → `amazon-image-requirements-2026`
   - `ebay-image-requirements-2025` → `ebay-image-requirements-2026`
   - `How to Remove Image Backgrounds... (2025)` → `(2026)`

2. **Fechas actualizadas:**
   - Todas las fechas `2025-01-xx` → `2026-01-xx`

3. **Archivos renombrados:**
   - `amazon-image-requirements-2025.tsx` → `amazon-image-requirements-2026.tsx`
   - `ebay-image-requirements-2025.tsx` → `ebay-image-requirements-2026.tsx`

4. **Copyright footer:** `© 2025` → `© 2026`

---

## Archivos a subir:

```
app/blog/posts/
├── amazon-image-requirements-2026.tsx  (NUEVO - reemplaza 2025)
├── ebay-image-requirements-2026.tsx    (NUEVO - reemplaza 2025)
├── instagram-product-images-guide.tsx  (sin cambios)
└── background-removal-guide.tsx        (sin cambios)

app/blog/
├── [slug]/page.tsx                     (actualizado)
└── layout.tsx                          (copyright actualizado)

lib/
└── blog-data.ts                        (slugs y fechas actualizados)

components/blog/
└── RelatedPosts.tsx                    (bg-white fix anterior)
```

---

## Comandos SCP (PowerShell)

```powershell
# 1. Eliminar archivos antiguos 2025 en el servidor
ssh root@49.13.145.150 "rm -f /root/masterpost-saas/app/blog/posts/amazon-image-requirements-2025.tsx /root/masterpost-saas/app/blog/posts/ebay-image-requirements-2025.tsx"

# 2. Subir nuevos artículos 2026
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\app\blog\posts\amazon-image-requirements-2026.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/posts/

scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\app\blog\posts\ebay-image-requirements-2026.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/posts/

# 3. Subir [slug]/page.tsx actualizado
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\app\blog\[slug]\page.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/\[slug\]/

# 4. Subir blog-data.ts actualizado
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\lib\blog-data.ts" root@49.13.145.150:/root/masterpost-saas/lib/

# 5. Subir layout.tsx actualizado (copyright 2026)
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\app\blog\layout.tsx" root@49.13.145.150:/root/masterpost-saas/app/blog/

# 6. Subir RelatedPosts.tsx (fix bg-white)
scp "F:\BACKUPS\MASTERPOST.IO\masterpost-saas\components\blog\RelatedPosts.tsx" root@49.13.145.150:/root/masterpost-saas/components/blog/
```

---

## Post-Deploy

```bash
ssh root@49.13.145.150

cd /root/masterpost-saas
npm run build
pm2 restart masterpost
```

---

## URLs Actualizadas

| Artículo | Nueva URL |
|----------|-----------|
| Amazon Image Requirements | `/blog/amazon-image-requirements-2026` |
| eBay Image Requirements | `/blog/ebay-image-requirements-2026` |
| Instagram Shopping Guide | `/blog/instagram-product-images-guide` |
| Background Removal Guide | `/blog/background-removal-guide` |

---

## Verificación

1. ✅ `/blog` - Ver lista con títulos 2026
2. ✅ `/blog/amazon-image-requirements-2026` - Artículo Amazon
3. ✅ `/blog/ebay-image-requirements-2026` - Artículo eBay
4. ✅ Footer muestra © 2026
