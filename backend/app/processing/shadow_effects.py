"""
Sistema de Sombras Profesionales para E-commerce
Crea efectos de sombra de nivel Amazon/premium para productos con fondo removido
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class ShadowEffects:
    def __init__(self):
        self.shadow_types = {
            'drop': self.create_drop_shadow,
            'reflection': self.create_reflection_shadow,
            'natural': self.create_natural_shadow,
            'none': lambda img, **kwargs: img
        }

    def apply_shadow(self, image_path: str, output_path: str,
                    shadow_type: str = 'drop', **shadow_params) -> bool:
        """Aplicar efecto de sombra a imagen con fondo removido"""

        logger.info(f"[SHADOW] Aplicando sombra tipo '{shadow_type}' a {Path(image_path).name}")

        try:
            # Cargar imagen con transparencia
            img = Image.open(image_path).convert('RGBA')
            logger.info(f"[SHADOW] Imagen cargada: {img.size[0]}x{img.size[1]} pixels")

            # Aplicar sombra según tipo
            if shadow_type in self.shadow_types:
                result_img = self.shadow_types[shadow_type](img, **shadow_params)
                logger.info(f"[SUCCESS] Sombra '{shadow_type}' aplicada exitosamente")
            else:
                logger.warning(f"[WARNING] Tipo de sombra '{shadow_type}' no reconocido, usando original")
                result_img = img.convert('RGB')

            # Las sombras ya incluyen fondo blanco, no necesitamos aplicar otro
            if result_img.mode == 'RGBA':
                logger.warning("[WARNING] Sombra devolvió RGBA, convirtiendo a RGB")
                # Crear fondo blanco y compositar solo si es necesario
                white_bg = Image.new('RGB', result_img.size, (255, 255, 255))
                white_bg.paste(result_img, mask=result_img.split()[-1] if result_img.mode == 'RGBA' else None)
                result_img = white_bg
            logger.info("[SHADOW] Imagen con sombra lista para guardar")

            # Guardar resultado
            result_img.save(output_path, 'PNG', quality=95)
            logger.info(f"[SUCCESS] Imagen con sombra guardada en {Path(output_path).name}")

            return True

        except Exception as e:
            logger.error(f"[ERROR] Error aplicando sombra: {str(e)}")
            return False

    def create_drop_shadow(self, img: Image.Image, intensity: float = 0.3,
                          offset_x: int = 10, offset_y: int = 10,
                          blur_radius: int = 15, **kwargs) -> Image.Image:
        """Crear sombra proyectada (drop shadow) - Estilo Amazon"""

        logger.info(f"[DROP SHADOW] Creando drop shadow - intensidad: {intensity}, offset: ({offset_x}, {offset_y}), blur: {blur_radius}")

        # Crear canvas más grande para la sombra
        shadow_margin = max(abs(offset_x), abs(offset_y)) + blur_radius + 30
        new_width = img.width + shadow_margin * 2
        new_height = img.height + shadow_margin * 2

        # Canvas con fondo BLANCO para que la sombra sea visible
        canvas = Image.new('RGB', (new_width, new_height), (255, 255, 255))

        # Crear máscara de sombra desde el canal alpha
        if img.mode == 'RGBA':
            shadow_mask = img.split()[-1]  # Canal alpha
        else:
            # Si no tiene alpha, crear máscara desde la imagen
            shadow_mask = img.convert('L')

        # Crear sombra (imagen negra con la forma del producto)
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_alpha = shadow_mask.point(lambda x: int(x * intensity) if x > 5 else 0)  # USAR INTENSIDAD VARIABLE
        shadow.paste((150, 150, 150, 255), mask=shadow_alpha)  # GRIS CLARO SUTIL

        # Aplicar blur a la sombra
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # PRIMERO: Pegar la sombra ROJA sobre el fondo blanco
        shadow_x = shadow_margin + offset_x
        shadow_y = shadow_margin + offset_y

        # Convertir sombra RGBA a RGB para el canvas RGB
        shadow_rgb = Image.new('RGB', shadow.size, (255, 255, 255))
        if shadow.mode == 'RGBA':
            shadow_rgb.paste(shadow, mask=shadow.split()[-1])
        else:
            shadow_rgb = shadow

        canvas.paste(shadow_rgb, (shadow_x, shadow_y))
        logger.info("[APPLY] Sombra pegada en canvas blanco")

        # SEGUNDO: Pegar producto original ENCIMA de la sombra
        product_x = shadow_margin
        product_y = shadow_margin
        canvas.paste(img, (product_x, product_y), img if img.mode == 'RGBA' else None)
        logger.info("[APPLY] Producto pegado encima de la sombra")

        logger.info(f"[DROP SHADOW] Canvas final: {canvas.size[0]}x{canvas.size[1]} pixels")
        return canvas

    def create_reflection_shadow(self, img: Image.Image, reflection_height: float = 0.4,
                               opacity: float = 0.2, fade_start: float = 0.0,
                               intensity: float = 0.2, **kwargs) -> Image.Image:
        """Crear sombra reflejo (reflection shadow) - Estilo premium"""

        # Usar intensidad del usuario si está disponible
        if intensity is not None:
            opacity = intensity
        logger.info(f"[REFLECT] Creando reflection shadow - altura: {reflection_height}, opacidad: {opacity}, intensidad: {intensity}")

        # Calcular dimensiones
        reflection_h = int(img.height * reflection_height)
        gap = 10  # Separación entre imagen y reflejo
        total_height = img.height + reflection_h + gap

        # Canvas con fondo transparente, luego se hará blanco
        canvas = Image.new('RGBA', (img.width, total_height), (0, 0, 0, 0))

        # Pegar imagen original
        canvas.paste(img, (0, 0), img if img.mode == 'RGBA' else None)

        # Crear reflejo
        reflection = img.copy()
        reflection = reflection.transpose(Image.FLIP_TOP_BOTTOM)  # Voltear verticalmente

        # Recortar reflejo a la altura deseada
        reflection = reflection.crop((0, 0, reflection.width, reflection_h))

        # Crear máscara de degradado para el fade
        fade_mask = Image.new('L', (reflection.width, reflection_h), 0)
        for y in range(reflection_h):
            # Opacidad que disminuye hacia abajo
            progress = y / reflection_h
            if progress < fade_start:
                fade_factor = 1.0
            else:
                fade_factor = 1.0 - ((progress - fade_start) / (1.0 - fade_start))

            opacity_value = int(255 * opacity * fade_factor)
            for x in range(reflection.width):
                fade_mask.putpixel((x, y), opacity_value)

        # Aplicar máscara al reflejo
        if reflection.mode != 'RGBA':
            reflection = reflection.convert('RGBA')

        # Modificar el canal alpha del reflejo
        r, g, b, a = reflection.split()
        # Combinar el alpha existente con la máscara de fade
        combined_alpha = ImageEnhance.Brightness(a).enhance(opacity)
        combined_alpha = Image.eval(combined_alpha, lambda x: int(x * (fade_mask.getpixel((0, 0)) / 255)))

        # Aplicar fade a todo el reflejo
        reflection_faded = Image.new('RGBA', reflection.size, (0, 0, 0, 0))
        for y in range(reflection_h):
            progress = y / reflection_h
            if progress < fade_start:
                fade_factor = 1.0
            else:
                fade_factor = 1.0 - ((progress - fade_start) / (1.0 - fade_start))

            alpha_value = int(255 * opacity * fade_factor)

            for x in range(reflection.width):
                if a.getpixel((x, y)) > 10:  # Solo si el pixel original no es transparente
                    r_val, g_val, b_val = reflection.getpixel((x, y))[:3]
                    reflection_faded.putpixel((x, y), (r_val, g_val, b_val, alpha_value))

        # Pegar reflejo en canvas
        reflection_y = img.height + gap
        canvas.paste(reflection_faded, (0, reflection_y), reflection_faded)

        logger.info(f"[REFLECT] Reflejo creado con altura {reflection_h}px")
        return canvas

    def create_natural_shadow(self, img: Image.Image, intensity: float = 0.15,
                            blur_radius: int = 8, direction: str = 'bottom-right',
                            **kwargs) -> Image.Image:
        """Crear sombra natural (sigue el contorno) - Estilo Instagram"""

        logger.info(f"[NATURAL] Creando natural shadow - intensidad: {intensity}, dirección: {direction}")

        # Direcciones de sombra
        directions = {
            'bottom-right': (4, 6),
            'bottom-left': (-4, 6),
            'bottom': (0, 6),
            'right': (6, 2),
            'left': (-6, 2)
        }

        offset_x, offset_y = directions.get(direction, (4, 6))

        # Canvas más grande
        margin = blur_radius + 15
        new_width = img.width + margin * 2
        new_height = img.height + margin * 2

        canvas = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))

        # Crear sombra sutil
        if img.mode == 'RGBA':
            shadow_mask = img.split()[-1]
        else:
            shadow_mask = img.convert('L')

        # Crear sombra con color gris oscuro sutil
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_alpha = shadow_mask.point(lambda x: int(x * intensity) if x > 10 else 0)
        shadow.paste((60, 60, 60, 255), mask=shadow_alpha)  # Gris oscuro en lugar de negro puro

        # Blur sutil para efecto natural
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Posicionar sombra en canvas
        shadow_x = margin + offset_x
        shadow_y = margin + offset_y
        canvas.paste(shadow, (shadow_x, shadow_y), shadow)

        # Producto original encima
        canvas.paste(img, (margin, margin), img if img.mode == 'RGBA' else None)

        logger.info(f"[NATURAL] Sombra natural aplicada con offset ({offset_x}, {offset_y})")
        return canvas

def detect_best_shadow_type(image_path: str) -> str:
    """Detectar automáticamente el mejor tipo de sombra según el producto"""

    try:
        # Cargar imagen para análisis
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            logger.warning("[WARNING] No se pudo cargar imagen para análisis, usando drop shadow")
            return 'drop'

        height, width = img.shape[:2]
        aspect_ratio = width / height

        logger.info(f"[AUTO] Analizando imagen: {width}x{height}, ratio: {aspect_ratio:.2f}")

        # Análisis basado en proportions y contenido
        if aspect_ratio > 1.8:
            # Muy ancho - productos como teclados, monitores
            shadow_type = 'natural'
            reason = "producto ancho horizontal"
        elif aspect_ratio < 0.6:
            # Muy alto - productos como botellas, torres de audio
            shadow_type = 'reflection'
            reason = "producto alto vertical"
        elif 0.8 <= aspect_ratio <= 1.2:
            # Cuadrado - la mayoría de productos
            shadow_type = 'drop'
            reason = "producto cuadrado/balanceado"
        else:
            # Casos intermedios
            shadow_type = 'drop'
            reason = "caso general"

        logger.info(f"[AUTO] Sombra recomendada: '{shadow_type}' ({reason})")
        return shadow_type

    except Exception as e:
        logger.error(f"[ERROR] Error detectando tipo de sombra: {str(e)}")
        return 'drop'  # Default seguro

def get_shadow_params_for_pipeline(pipeline: str) -> Dict:
    """Obtener parámetros de sombra optimizados por pipeline"""

    params = {
        'amazon': {
            'shadow_type': 'drop',
            'intensity': 0.15,
            'offset_x': 25,
            'offset_y': 30,
            'blur_radius': 10
        },
        'instagram': {
            'shadow_type': 'natural',
            'intensity': 0.2,
            'blur_radius': 8,
            'direction': 'bottom-right'
        },
        'ebay': {
            'shadow_type': 'reflection',
            'reflection_height': 0.35,
            'opacity': 0.1,
            'fade_start': 0.1
        },
        'shopify': {
            'shadow_type': 'drop',
            'intensity': 0.2,
            'offset_x': 6,
            'offset_y': 12,
            'blur_radius': 15
        },
        'premium': {
            'shadow_type': 'reflection',
            'reflection_height': 0.5,
            'opacity': 0.15,
            'fade_start': 0.0
        }
    }

    selected_params = params.get(pipeline, params['amazon'])
    logger.info(f"[PROCESS] Parámetros para pipeline '{pipeline}': {selected_params}")

    return selected_params

def enhance_shadow_quality(img: Image.Image) -> Image.Image:
    """Mejorar la calidad general de la imagen con sombra"""

    try:
        # Ligero aumento de contraste para que el producto destaque
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)

        # Ligero aumento de nitidez
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))

        logger.info("[PROCESS] Calidad de imagen mejorada")
        return img

    except Exception as e:
        logger.error(f"[ERROR] Error mejorando calidad: {str(e)}")
        return img

# Función principal de conveniencia
def apply_professional_shadow(input_path: str, output_path: str,
                            pipeline: str = 'amazon',
                            shadow_type: str = 'auto',
                            custom_params: Optional[Dict] = None) -> bool:
    """
    Función principal para aplicar sombras profesionales

    Args:
        input_path: Ruta de imagen con fondo removido
        output_path: Ruta de salida
        pipeline: Pipeline de procesamiento (amazon, instagram, ebay, etc.)
        shadow_type: Tipo de sombra ('auto', 'drop', 'reflection', 'natural', 'none')
        custom_params: Parámetros personalizados opcionales

    Returns:
        bool: True si fue exitoso
    """

    logger.info(f"[SHADOW] Iniciando aplicación de sombra profesional")
    logger.info(f"[SHADOW] Input: {Path(input_path).name}")
    logger.info(f"[SHADOW] Pipeline: {pipeline}, Tipo: {shadow_type}")

    try:
        # Detectar tipo automáticamente si es necesario
        if shadow_type == 'auto':
            shadow_type = detect_best_shadow_type(input_path)
            logger.info(f"[AUTO] Tipo detectado automáticamente: {shadow_type}")

        # Si el usuario eligió 'none', saltar todo el procesamiento de sombras
        if shadow_type == 'none':
            logger.info("[SHADOW] Usuario deshabilitó sombras (shadow_type='none'), copiando imagen original")
            # Simplemente copiar la imagen original sin modificaciones
            import shutil
            shutil.copy2(input_path, output_path)
            return True

        # Obtener parámetros base del pipeline
        shadow_params = get_shadow_params_for_pipeline(pipeline)

        # Sobrescribir tipo si se especificó uno diferente (excepto 'auto')
        if shadow_type != 'auto':
            shadow_params['shadow_type'] = shadow_type

        # Aplicar parámetros personalizados si se proporcionaron
        if custom_params:
            shadow_params.update(custom_params)
            logger.info(f"[SHADOW] Parámetros personalizados aplicados: {custom_params}")

        # Crear el procesador de sombras
        shadow_processor = ShadowEffects()

        # Aplicar la sombra
        success = shadow_processor.apply_shadow(
            image_path=input_path,
            output_path=output_path,
            **shadow_params
        )

        if success:
            logger.info(f"[SUCCESS] Sombra profesional aplicada exitosamente")
            logger.info(f"[SUCCESS] Resultado guardado en: {Path(output_path).name}")
        else:
            logger.error(f"[ERROR] Error aplicando sombra profesional")

        return success

    except Exception as e:
        logger.error(f"[ERROR] Error en apply_professional_shadow: {str(e)}")
        return False

def apply_simple_drop_shadow(image, intensity=0.5):
    """
    Simplified drop shadow - just works, no complex parameters

    Args:
        image: PIL Image with RGBA (transparent background)
        intensity: Shadow darkness 0.0-1.0

    Returns:
        PIL Image with drop shadow on white background
    """
    print(f"[SIMPLE SHADOW] Applying basic drop shadow, intensity={intensity}")

    try:
        # Ensure RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        width, height = image.size

        # Create shadow offset (fixed values for simplicity)
        offset_x = 15
        offset_y = 15
        blur_radius = 20

        # Create expanded canvas for shadow
        padding = blur_radius + offset_x + offset_y
        shadow_size = (width + padding * 2, height + padding * 2)

        # Extract alpha channel for shadow mask
        alpha = image.split()[3]

        # Create shadow layer
        shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
        shadow_alpha = alpha.point(lambda x: int(x * intensity) if x > 10 else 0)
        shadow.paste((100, 100, 100, 255), (0, 0), shadow_alpha)

        # Apply blur
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

        # Create final canvas with WHITE background
        result = Image.new('RGB', shadow_size, (255, 255, 255))

        # Position shadow with offset
        shadow_x = padding + offset_x
        shadow_y = padding + offset_y

        # Paste shadow (convert to RGB for white background)
        shadow_rgb = Image.new('RGB', shadow.size, (255, 255, 255))
        shadow_rgb.paste(shadow, mask=shadow.split()[3] if shadow.mode == 'RGBA' else None)
        result.paste(shadow_rgb, (shadow_x, shadow_y))

        # Paste original product on top
        result.paste(image, (padding, padding), image)

        print(f"[SIMPLE SHADOW] Success! Result size: {result.size}")
        return result

    except Exception as e:
        print(f"[SIMPLE SHADOW] ERROR: {e}")
        # Return image on white background as fallback
        fallback = Image.new('RGB', image.size, (255, 255, 255))
        fallback.paste(image, (0, 0), image if image.mode == 'RGBA' else None)
        return fallback