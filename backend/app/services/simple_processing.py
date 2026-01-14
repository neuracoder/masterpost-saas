"""
Simple Local Background Removal Service
Supports both Basic (local rembg) and Premium (Qwen API) processing
OPTIMIZED: Pre-loads rembg model for 2-3x faster processing
"""

from rembg import remove, new_session
from PIL import Image, ImageFilter
import io
import logging
import os
from pathlib import Path

# Import shadow effects module (working version with class-based approach)
from ..processing.shadow_effects import apply_professional_shadow, ShadowEffects

# Import Qwen premium service
try:
    from .qwen_service import remove_background_premium_sync, qwen_service
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    logger.warning("⚠️ Qwen service not available. Premium processing disabled.")

logger = logging.getLogger(__name__)

# OPTIMIZATION: Pre-load rembg model ONCE at module import
# This saves ~2-3 seconds per image by reusing the same model session
try:
    logger.info("[OPTIMIZATION] Pre-loading rembg U2-Net model...")
    REMBG_SESSION = new_session("u2net")
    logger.info("[OPTIMIZATION] ✓ Model loaded successfully - ready for parallel processing")
except Exception as e:
    logger.error(f"[OPTIMIZATION] Failed to pre-load model: {e}")
    REMBG_SESSION = None

def apply_simple_shadow(img_rgba: Image.Image, shadow_type: str = 'drop', intensity: float = 0.5, blur_radius: int = 15) -> Image.Image:
    """
    Simple shadow effect using PIL in-memory (no temp files)

    Args:
        img_rgba: Image with alpha channel (transparent background)
        shadow_type: 'drop', 'natural', or 'reflection'
        intensity: Shadow opacity 0.0-1.0
        blur_radius: Blur amount

    Returns:
        RGB image with shadow and white background
    """
    logger.info(f"[DEBUG] Creating shadow - type: {shadow_type}, intensity: {intensity}, blur: {blur_radius}")

    # Ensure RGBA
    if img_rgba.mode != 'RGBA':
        img_rgba = img_rgba.convert('RGBA')

    width, height = img_rgba.size
    logger.info(f"[DEBUG] Image size: {width}x{height}")

    # Extract alpha channel (product silhouette)
    alpha = img_rgba.split()[3]

    # Create shadow as a black silhouette with the same shape as the product
    shadow_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    # Fill shadow with dark gray/black, using alpha as mask
    shadow_fill = Image.new('RGBA', (width, height), (0, 0, 0, int(255 * intensity)))
    shadow_layer.paste(shadow_fill, (0, 0), alpha)

    logger.info(f"[DEBUG] Shadow layer created with intensity {int(255 * intensity)}")

    # Apply blur to soften shadow
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur_radius))
    logger.info(f"[DEBUG] Blur applied: {blur_radius}px")

    # Create canvas with white background
    canvas = Image.new('RGB', (width, height), (255, 255, 255))

    # Paste shadow with offset (slightly down and right for drop shadow)
    if shadow_type == 'drop':
        offset_x, offset_y = 8, 8
    else:
        offset_x, offset_y = 0, 0

    # Create offset shadow canvas
    shadow_offset = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_offset.paste(shadow_layer, (offset_x, offset_y))

    # Composite: white bg + shadow + product
    canvas.paste(shadow_offset, (0, 0), shadow_offset)
    canvas.paste(img_rgba, (0, 0), img_rgba)

    logger.info(f"[DEBUG] Shadow composited with offset ({offset_x}, {offset_y})")

    return canvas

def remove_background_simple(input_path: str, output_path: str, shadow_params: dict = None, pipeline: str = "amazon") -> tuple[bool, str]:
    """
    Simple local background removal using rembg + white background + optional shadows

    Args:
        input_path: Path to input image
        output_path: Path for processed image
        shadow_params: Optional dict with shadow parameters:
            - enabled (bool): Enable shadow effect
            - type (str): Shadow type (drop, reflection, natural, auto)
            - intensity (float): Shadow opacity (0.0-1.0)
            - angle (int): Light angle in degrees (0-360)
            - distance (int): Shadow distance in pixels
            - blur_radius (int): Blur level
        pipeline: Pipeline type (amazon, instagram, ebay, transparent)

    Returns:
        tuple[bool, str]: (success, actual_output_path)
    """
    try:
        logger.info(f"Starting simple background removal: {input_path}")
        logger.info(f"[DEBUG] Shadow params passed to remove_background_simple: {shadow_params}")

        # Read original image
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()

        # Remove background with rembg (using pre-loaded session for speed)
        logger.info("Removing background with rembg...")
        if REMBG_SESSION:
            output_data = remove(input_data, session=REMBG_SESSION)
        else:
            output_data = remove(input_data)  # Fallback if session failed to load

        # Open image without background (RGBA)
        img_no_bg = Image.open(io.BytesIO(output_data))
        logger.info(f"Background removed, image size: {img_no_bg.size}")

        # Ensure image is in RGBA mode
        if img_no_bg.mode != 'RGBA':
            img_no_bg = img_no_bg.convert('RGBA')

        # Clean edges to reduce halo effect
        if img_no_bg.mode == 'RGBA':
            # Get alpha channel
            alpha = img_no_bg.split()[3]

            # Erode alpha slightly to remove edge artifacts
            alpha = alpha.filter(ImageFilter.MinFilter(3))  # Shrink edges by 1-2px

            # Apply slight blur to alpha for smoother transition
            alpha = alpha.filter(ImageFilter.GaussianBlur(0.5))

            # Reconstruct image with cleaned alpha
            r, g, b, _ = img_no_bg.split()
            img_no_bg = Image.merge('RGBA', (r, g, b, alpha))

            logger.info("[HALO-REMOVAL] Edge refinement applied to reduce halo")

        # ALTERNATIVE: More aggressive halo removal (uncomment if needed)
        # if img_no_bg.mode == 'RGBA':
        #     import numpy as np
        #
        #     # Convert to numpy for processing
        #     img_array = np.array(img_no_bg)
        #     alpha = img_array[:, :, 3]
        #
        #     # Create binary mask (fully opaque or fully transparent)
        #     threshold = 200  # Adjust between 150-250
        #     alpha_binary = np.where(alpha > threshold, 255, 0).astype(np.uint8)
        #
        #     # Erode to remove halo
        #     alpha_pil = Image.fromarray(alpha_binary)
        #     alpha_pil = alpha_pil.filter(ImageFilter.MinFilter(5))  # Stronger erosion
        #
        #     # Slight blur for natural edge
        #     alpha_pil = alpha_pil.filter(ImageFilter.GaussianBlur(1))
        #
        #     # Apply back to image
        #     img_array[:, :, 3] = np.array(alpha_pil)
        #     img_no_bg = Image.fromarray(img_array)
        #
        #     logger.info("[HALO-REMOVAL] Aggressive halo removal applied")

        # Standard pipelines (amazon, instagram, ebay) - resize and add white background
        # Resize image maintaining aspect ratio (keep as RGBA)
        img_no_bg.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
        logger.info(f"Image resized to: {img_no_bg.size}")

        # Apply shadow effect if enabled
        if shadow_params and shadow_params.get('enabled', False):
            logger.info("=" * 60)
            logger.info(f"[SHADOW] Applying simple drop shadow")
            logger.info(f"   Intensity: {shadow_params.get('intensity', 0.5)}")
            logger.info("=" * 60)

            try:
                from .shadow_effects import apply_simple_drop_shadow

                img_with_shadow = apply_simple_drop_shadow(
                    image=img_no_bg,
                    intensity=shadow_params.get('intensity', 0.5)
                )

                logger.info("=" * 60)
                logger.info(f"[SHADOW] Success!")
                logger.info("=" * 60)

                # Use image with shadow
                img_final = img_with_shadow

            except Exception as shadow_error:
                logger.error("=" * 60)
                logger.error(f"[SHADOW] FAILED: {shadow_error}")
                logger.error("=" * 60)
                import traceback
                traceback.print_exc()
                # Create white background as fallback
                white_bg = Image.new('RGB', img_no_bg.size, (255, 255, 255))
                white_bg.paste(img_no_bg, (0, 0), img_no_bg)
                img_final = white_bg
        else:
            # Create white background (no shadow)
            white_bg = Image.new('RGB', img_no_bg.size, (255, 255, 255))
            white_bg.paste(img_no_bg, (0, 0), img_no_bg)
            img_final = white_bg

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save result as JPEG
        img_final.save(output_path, 'JPEG', quality=95)
        logger.info(f"Image saved successfully: {output_path}")

        return True, output_path

    except Exception as e:
        logger.error(f"Error processing {input_path}: {e}")
        return False, output_path

def process_image_simple(input_path: str, output_path: str, pipeline: str = "amazon", shadow_params: dict = None, use_premium: bool = False) -> dict:
    """
    Process image with Basic (local rembg) or Premium (Qwen API) processing

    Args:
        input_path: Path to input image
        output_path: Path for processed image
        pipeline: Pipeline type (amazon, instagram, ebay)
        shadow_params: Optional shadow parameters dict
        use_premium: If True, use Qwen API (Premium, 3 credits)
                     If False, use local rembg (Basic, 1 credit)

    Returns:
        dict: Processing result with cost information
    """
    # PREMIUM PROCESSING with Qwen API
    if use_premium:
        if not QWEN_AVAILABLE or not qwen_service.available:
            logger.warning("⚠️ Premium requested but not available. Falling back to Basic.")
            use_premium = False  # Fallback to basic
        else:
            logger.info(f"🌟 Using PREMIUM processing (Qwen API) for: {Path(input_path).name}")

            result = remove_background_premium_sync(input_path, output_path, pipeline)

            if result.get('success'):
                logger.info(f"✅ Premium processing successful!")
                return {
                    "success": True,
                    "method": "qwen_premium",
                    "pipeline": pipeline,
                    "input_path": input_path,
                    "output_path": output_path,
                    "cost": 0.045,  # API cost
                    "credits_used": 3,
                    "shadow_applied": False,  # Qwen handles shadows in prompt
                    "shadow_type": None,
                    "message": "Background removed successfully with Premium AI"
                }
            else:
                # Fallback to basic if premium fails
                logger.warning(f"⚠️ Premium processing failed: {result.get('error')}")
                logger.warning("   Falling back to Basic processing...")
                use_premium = False

    # BASIC PROCESSING with local rembg
    if not use_premium:
        logger.info(f"🔧 Using BASIC processing (local rembg) for: {Path(input_path).name}")

        # Process image with shadow parameters (or None for no shadow)
        success, actual_output_path = remove_background_simple(input_path, output_path, shadow_params, pipeline)

        if not success:
            return {
                "success": False,
                "method": "local_rembg",
                "pipeline": pipeline,
                "input_path": input_path,
                "error": "Failed to process image with local background removal"
            }

        shadow_enabled = shadow_params and shadow_params.get('enabled', False)

        result = {
            "success": True,
            "method": "local_rembg",
            "pipeline": pipeline,
            "input_path": input_path,
            "output_path": actual_output_path,  # Use the actual output path (may be .png for transparent)
            "cost": 0.0,  # No API cost for local processing
            "credits_used": 1,
            "shadow_applied": shadow_enabled,
            "shadow_type": shadow_params.get('type', 'drop') if shadow_enabled else None,
            "message": f"Background removed successfully" + (f" with {shadow_params.get('type', 'drop')} shadow" if shadow_enabled else "")
        }

        return result