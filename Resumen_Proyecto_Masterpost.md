# 🟢 Resumen del Proyecto Masterpost.io

## 📋 Información General
**Masterpost.io** es una plataforma SaaS profesional para la eliminación de fondos de imágenes, diseñada específicamente para el comercio electrónico. Utiliza inteligencia artificial avanzada para procesar imágenes en masa con un sistema de precios basado en créditos.

- **Sitio Web**: [masterpost.io](https://masterpost.io)
- **Repositorio**: [github.com/neuracoder/Masterpost-SaaS](https://github.com/neuracoder/Masterpost-SaaS)
- **Estado**: 🚀 Listo para Producción (MVP Completo)

---

## 🚀 Características Principales

### 1. Sistema de Procesamiento Dual
La plataforma ofrece dos niveles de procesamiento para adaptarse a diferentes necesidades y presupuestos:

*   **Nivel Básico (Local)**
    *   **Tecnología**: `rembg` (U2-Net) ejecutado localmente.
    *   **Costo**: 1 crédito ($0.10) por imagen.
    *   **Uso ideal**: Procesamiento masivo, fondos simples, bajo costo.
    *   **Velocidad**: Rápida (~10s/imagen).

*   **Nivel Premium (AI Avanzada)**
    *   **Tecnología**: Qwen Image Edit API (Alibaba Cloud).
    *   **Costo**: 3 créditos ($0.30) por imagen.
    *   **Uso ideal**: Joyería, vidrio, objetos transparentes, fondos complejos.
    *   **Calidad**: Superior en bordes y preservación de detalles.
    *   **Fallback Automático**: Si la API falla, el sistema cambia automáticamente al nivel básico y ajusta el cobro.

### 2. Experiencia de Usuario (UI/UX)
*   **Animación de Procesamiento**: Nueva interfaz circular moderna con gradientes (Purple/Pink) que muestra el progreso en tiempo real.
*   **Galería Before/After**: Slider interactivo para comparar resultados originales y procesados.
*   **Diseño Responsivo**: Interfaz optimizada para móviles y escritorio con branding verde (#10b981) y amarillo (#fbbf24).
*   **Estimación de Costos**: Calculadora en tiempo real según el nivel de procesamiento seleccionado.

### 3. Gestión de Créditos y Usuarios
*   **Autenticación**: Registro y login seguro vía Supabase Auth (JWT).
*   **Créditos de Bienvenida**: 10 créditos gratuitos al registrarse.
*   **Historial**: Registro detallado de transacciones y uso de créditos.

### 4. Juego para espera de Procesamiento
*   Juego de globo rojo esquivando diferentes objetos que se interponen a su ascenso. Este juego 
se activa automaticamente cuando se comienzan a procesar las imagenes permitiendo al usuario jugar o no mientras espera a que finalice el proceso.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Descripción |
|------------|------------|-------------|
| **Frontend** | Next.js / React | Interfaz moderna con TailwindCSS y Lucide Icons. |
| **Backend** | FastAPI (Python 3.11) | API robusta y asíncrona. |
| **Base de Datos** | Supabase (PostgreSQL) | Almacenamiento de usuarios, créditos y transacciones. |
| **Auth** | Supabase Auth | Gestión de sesiones y seguridad JWT. |
| **AI (Premium)** | Qwen VL (DashScope) | Modelo de visión para edición de imágenes de alta calidad. |
| **AI (Básico)** | rembg | Librería de Python para remoción de fondos local. |
| **Infraestructura** | Vercel | Despliegue de frontend y backend (serverless/edge). |

---

## 🔄 Integraciones Recientes (Detalle)

### ✅ Integración Qwen Premium
Se implementó un servicio completo (`backend/services/qwen_service.py`) que conecta con la API de Qwen para el procesamiento premium.
*   **Lógica de Fallback**: Garantiza que el usuario siempre obtenga un resultado, degradando a básico si la API externa no responde.
*   **Parámetros por Pipeline**: Ajustes específicos (suavizado de bordes, realce de color) para Amazon, eBay e Instagram.

### ✅ Animación de Procesamiento
Componente React (`components/ProcessingAnimation.tsx`) que mejora la percepción de velocidad y calidad.
*   **Feedback Visual**: Spinner, porcentaje, contador de imágenes y mensajes de estado.
*   **Estética**: Glassmorphism y animaciones suaves (pulse, bounce).

---

## 🌍 Infraestructura y Despliegue

### Configuración de Producción
*   **Variables de Entorno**: Gestionadas de forma segura (excluidas del repo).
*   **Base de Datos**: Tablas configuradas (`user_credits`, `transactions`) con Row Level Security (RLS).
*   **Dominios**: Configurado para `masterpost.io` con HTTPS automático.

### Guía de Despliegue
El proyecto cuenta con una guía detallada (`DEPLOYMENT_GUIDE.md`) que cubre:
1.  Preparación del repositorio.
2.  Configuración de Supabase (Tablas y Auth).
3.  Despliegue en Vercel.
4.  Configuración de dominios y CORS.

---

## 📅 Próximos Pasos (Roadmap)

### Fase 2: Pagos (Próximamente)
*   [ ] Integración con **Stripe**.
*   [ ] Compra de packs de créditos (Pro $17.99, Business $39.99).
*   [ ] Webhooks para asignación automática de créditos.

### Fase 3: Optimizaciones
*   [ ] Procesamiento en cola (Celery/Redis) para mayor escalabilidad.
*   [ ] Historial de imágenes procesadas con almacenamiento en la nube.
*   [ ] Descarga de resultados en formato ZIP.

---

<div align="center">
  <p>Documento actualizado automáticamente el 29/11/2025</p>
  <p><strong>Masterpost.io - Transform backgrounds, transform business</strong></p>
</div>
