from PIL import Image, ImageEnhance, ImageFilter
try:
    import cv2
except ImportError:
    print("WARNING: OpenCV (cv2) could not be imported. Edge detection features will be unavailable.")
    cv2 = None
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import io

class ImageProcessor:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}

    def load_image(self, image_path: Path) -> Image.Image:
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Handle transparency by adding white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                    return background
                elif img.mode != 'RGB':
                    return img.convert('RGB')
                return img.copy()
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {str(e)}")

    def save_image(self, image: Image.Image, output_path: Path, quality: int = 95) -> bool:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            save_kwargs = {}
            if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                save_kwargs = {'quality': quality, 'optimize': True}
            elif output_path.suffix.lower() == '.png':
                save_kwargs = {'optimize': True, 'compress_level': 6}

            image.save(output_path, **save_kwargs)
            return True
        except Exception as e:
            print(f"Failed to save image {output_path}: {str(e)}")
            return False

    def resize_image(self, image: Image.Image, target_size: Tuple[int, int], maintain_aspect: bool = True) -> Image.Image:
        if not maintain_aspect:
            return image.resize(target_size, Image.Resampling.LANCZOS)

        # Calculate aspect ratio preserving resize
        original_width, original_height = image.size
        target_width, target_height = target_size

        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        # Resize the image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Create a new image with target size and center the resized image
        result = Image.new('RGB', target_size, (255, 255, 255))
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        result.paste(resized, (paste_x, paste_y))

        return result

    def remove_background(self, image: Image.Image, method: str = 'white_threshold') -> Image.Image:
        if method == 'white_threshold':
            return self._remove_white_background(image)
        elif method == 'edge_detection':
            return self._remove_background_edge_detection(image)
        else:
            # Fallback to white threshold
            return self._remove_white_background(image)

    def _remove_white_background(self, image: Image.Image, threshold: int = 240) -> Image.Image:
        # Convert to numpy array
        img_array = np.array(image)

        # Create mask for white/light pixels
        mask = np.all(img_array >= threshold, axis=2)

        # Create RGBA image
        rgba_array = np.dstack([img_array, np.where(mask, 0, 255).astype(np.uint8)])
        result = Image.fromarray(rgba_array, 'RGBA')

        # Convert back to RGB with white background
        white_bg = Image.new('RGB', image.size, (255, 255, 255))
        white_bg.paste(result, mask=result)

        return white_bg

    def _remove_background_edge_detection(self, image: Image.Image) -> Image.Image:
        if cv2 is None:
            print("Skipping edge detection because OpenCV is not available.")
            return image
        # Convert PIL to OpenCV
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Apply GrabCut algorithm for background removal
        mask = np.zeros(img_cv.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        # Define rectangle around the object (rough estimation)
        height, width = img_cv.shape[:2]
        rect = (int(width * 0.1), int(height * 0.1), int(width * 0.8), int(height * 0.8))

        cv2.grabCut(img_cv, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

        # Modify mask
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

        # Apply mask
        result = img_cv * mask2[:, :, np.newaxis]

        # Convert back to PIL
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        return Image.fromarray(result_rgb)

    def enhance_colors(self, image: Image.Image, enhancement_settings: Dict[str, float]) -> Image.Image:
        result = image.copy()

        # Color enhancement
        if 'saturation' in enhancement_settings:
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(enhancement_settings['saturation'])

        # Contrast enhancement
        if 'contrast' in enhancement_settings:
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(enhancement_settings['contrast'])

        # Brightness enhancement
        if 'brightness' in enhancement_settings:
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(enhancement_settings['brightness'])

        # Sharpness enhancement
        if 'sharpness' in enhancement_settings:
            enhancer = ImageEnhance.Sharpness(result)
            result = enhancer.enhance(enhancement_settings['sharpness'])

        return result

    def add_padding(self, image: Image.Image, padding_percent: float = 10) -> Image.Image:
        width, height = image.size
        padding_x = int(width * padding_percent / 100)
        padding_y = int(height * padding_percent / 100)

        new_width = width + 2 * padding_x
        new_height = height + 2 * padding_y

        result = Image.new('RGB', (new_width, new_height), (255, 255, 255))
        result.paste(image, (padding_x, padding_y))

        return result

    def apply_watermark(self, image: Image.Image, watermark_text: str = "Masterpost.io") -> Image.Image:
        # This is a basic watermark implementation
        # For production, you might want to use a proper watermark image
        from PIL import ImageDraw, ImageFont

        result = image.copy()
        draw = ImageDraw.Draw(result)

        # Try to use a system font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # Add watermark in bottom right corner
        width, height = image.size
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = width - text_width - 10
        y = height - text_height - 10

        # Add semi-transparent background
        draw.rectangle([x-5, y-5, x + text_width + 5, y + text_height + 5], fill=(255, 255, 255, 128))
        draw.text((x, y), watermark_text, fill=(128, 128, 128), font=font)

        return result

    def get_image_info(self, image_path: Path) -> Dict[str, Any]:
        try:
            with Image.open(image_path) as img:
                return {
                    'filename': image_path.name,
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'file_size': image_path.stat().st_size,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            return {'error': str(e)}