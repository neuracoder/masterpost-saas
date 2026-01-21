# Comandos SCP para Deploy del Blog - Masterpost.io

## Estructura de archivos creados:

```
app/blog/
├── page.tsx                           → Lista de artículos (página principal del blog)
├── layout.tsx                         → Layout específico del blog
├── [slug]/
│   └── page.tsx                       → Template para artículos individuales
└── posts/
    └── amazon-image-requirements-2025.tsx  → Primer artículo

components/blog/
├── BlogCard.tsx                       → Card para preview de artículo
├── BlogHeader.tsx                     → Header del artículo individual
├── BlogContent.tsx                    → Wrapper para contenido + Callout, ComparisonTable, etc.
├── RelatedPosts.tsx                   → Sidebar con artículos relacionados
├── BlogCTA.tsx                        → Call-to-action box
└── index.ts                           → Exports centralizados

lib/
└── blog-data.ts                       → Datos centralizados de los posts

public/blog/
└── amazon-requirements-cover.jpg      → Imagen de portada (placeholder - REEMPLAZAR)
```

---

## IMPORTANTE: Imagen de Portada

Antes de hacer deploy, necesitas crear una imagen de portada real:
- Ubicación: `public/blog/amazon-requirements-cover.jpg`
- Tamaño recomendado: 1200x630px (formato OG Image)
- Contenido sugerido: Diseño profesional con tema de Amazon/e-commerce

---

## Comandos SCP para Ubuntu Server

### Opción 1: Subir todo el blog de una vez

```bash
# Desde la carpeta raíz del proyecto en tu máquina local

# 1. Subir carpeta app/blog completa
scp -r app/blog/ usuario@IP_SERVIDOR:/var/www/masterpost-saas/app/

# 2. Subir componentes del blog
scp -r components/blog/ usuario@IP_SERVIDOR:/var/www/masterpost-saas/components/

# 3. Subir datos del blog
scp lib/blog-data.ts usuario@IP_SERVIDOR:/var/www/masterpost-saas/lib/

# 4. Subir imagen de portada
scp public/blog/amazon-requirements-cover.jpg usuario@IP_SERVIDOR:/var/www/masterpost-saas/public/blog/

# 5. Subir página principal actualizada (con link a Blog en navbar)
scp app/page.tsx usuario@IP_SERVIDOR:/var/www/masterpost-saas/app/
```

### Opción 2: Comando único con rsync (más eficiente)

```bash
# Sincronizar todos los archivos nuevos/modificados
rsync -avz --progress \
  --include='app/blog/***' \
  --include='components/blog/***' \
  --include='lib/blog-data.ts' \
  --include='public/blog/***' \
  --include='app/page.tsx' \
  --exclude='*' \
  ./ usuario@IP_SERVIDOR:/var/www/masterpost-saas/
```

### Opción 3: Comandos individuales detallados

```bash
# Variables (ajustar según tu servidor)
SERVIDOR="usuario@tu-ip-servidor"
RUTA_DESTINO="/var/www/masterpost-saas"

# 1. Crear directorios en servidor
ssh $SERVIDOR "mkdir -p $RUTA_DESTINO/app/blog/posts $RUTA_DESTINO/app/blog/\[slug\] $RUTA_DESTINO/components/blog $RUTA_DESTINO/public/blog"

# 2. Subir layout y página principal del blog
scp app/blog/layout.tsx $SERVIDOR:$RUTA_DESTINO/app/blog/
scp app/blog/page.tsx $SERVIDOR:$RUTA_DESTINO/app/blog/

# 3. Subir template de artículos
scp "app/blog/[slug]/page.tsx" $SERVIDOR:$RUTA_DESTINO/app/blog/\[slug\]/

# 4. Subir artículo
scp app/blog/posts/amazon-image-requirements-2025.tsx $SERVIDOR:$RUTA_DESTINO/app/blog/posts/

# 5. Subir componentes
scp components/blog/BlogCard.tsx $SERVIDOR:$RUTA_DESTINO/components/blog/
scp components/blog/BlogHeader.tsx $SERVIDOR:$RUTA_DESTINO/components/blog/
scp components/blog/BlogContent.tsx $SERVIDOR:$RUTA_DESTINO/components/blog/
scp components/blog/RelatedPosts.tsx $SERVIDOR:$RUTA_DESTINO/components/blog/
scp components/blog/BlogCTA.tsx $SERVIDOR:$RUTA_DESTINO/components/blog/
scp components/blog/index.ts $SERVIDOR:$RUTA_DESTINO/components/blog/

# 6. Subir datos del blog
scp lib/blog-data.ts $SERVIDOR:$RUTA_DESTINO/lib/

# 7. Subir imagen de portada
scp public/blog/amazon-requirements-cover.jpg $SERVIDOR:$RUTA_DESTINO/public/blog/

# 8. Subir página principal actualizada
scp app/page.tsx $SERVIDOR:$RUTA_DESTINO/app/
```

---

## Post-Deploy: Comandos en el servidor

```bash
# Conectar al servidor
ssh usuario@IP_SERVIDOR

# Ir al directorio del proyecto
cd /var/www/masterpost-saas

# Instalar dependencias (si hay nuevas)
npm install

# Build del proyecto
npm run build

# Reiniciar la aplicación
# Si usas PM2:
pm2 restart masterpost

# Si usas systemd:
sudo systemctl restart masterpost

# Si usas Docker:
docker-compose up -d --build
```

---

## Verificación post-deploy

1. Visitar https://masterpost.io/blog - Ver lista de artículos
2. Visitar https://masterpost.io/blog/amazon-image-requirements-2025 - Ver artículo completo
3. Verificar que el link "Blog" aparece en el navbar
4. Probar en móvil (responsive)
5. Verificar SEO: View Source → buscar meta tags y schema.org

---

## URLs del Blog

- Lista de artículos: `/blog`
- Artículo individual: `/blog/amazon-image-requirements-2025`

---

## Notas adicionales

- El blog usa los mismos componentes UI que el resto del sitio (shadcn/ui)
- Los estilos están en Tailwind CSS (ya configurado)
- El artículo tiene Schema.org markup para SEO
- Las imágenes de portada deben ser optimizadas antes de subir

---

## Agregar nuevos artículos

1. Crear archivo en `app/blog/posts/nuevo-articulo.tsx`
2. Agregar entrada en `lib/blog-data.ts`
3. Agregar mapping en `app/blog/[slug]/page.tsx` (articleComponents)
4. Subir imagen de portada a `public/blog/`
5. Deploy con SCP
