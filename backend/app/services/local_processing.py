"""
Local background removal processing for MASTERPOST.IO V2.0
Uses rembg for local processing when Qwen API is unavailable or for free tier
"""

import asyncio
import logging
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont
import io
import time
from pathlib import Path

logger = logging.getLogger(__name__)

async def local_background_removal(
    image_path: str,
    output_path: str,
    add_watermark: bool = False
) -> Dict[str, Any]:
    """
    Remove background using local rembg processing

    Args:
        image_path: Path to input image
        output_path: Path for processed image
        add_watermark: Whether to add watermark (for free tier)

    Returns:
        Dict with success status and metadata
    """
    start_time = time.time()

    try:
        # Import rembg dynamically to handle missing dependency gracefully
        try:
            from rembg import remove, new_session
        except ImportError:
            logger.error("rembg not installed. Install with: pip install rembg")
            return {
                "success": False,
                "error": "Local processing not available - rembg not installed",
                "method": "local"
            }

        # Load image
        with open(image_path, 'rb') as f:
            input_data = f.read()

        # Process with rembg
        output_data = await asyncio.to_thread(remove, input_data)

        # Convert to PIL Image for watermarking if needed
        if add_watermark:
            image = Image.open(io.BytesIO(output_data))
            image = await add_watermark_to_image(image)

            # Convert back to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            output_data = img_buffer.getvalue()

        # Save result
        with open(output_path, 'wb') as f:
            f.write(output_data)

        processing_time = time.time() - start_time

        return {
            "success": True,
            "method": "local",
            "processing_time": processing_time,
            "output_path": output_path,
            "watermark_applied": add_watermark
        }

    except Exception as e:
        logger.error(f"Local processing failed for {image_path}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "method": "local",
            "processing_time": time.time() - start_time
        }

async def add_watermark_to_image(image: Image.Image, watermark_text: str = "MASTERPOST.IO") -> Image.Image:
    """
    Add watermark to processed image for free tier

    Args:
        image: PIL Image object
        watermark_text: Text to use as watermark

    Returns:
        Image with watermark applied
    """
    try:
        # Create a copy to avoid modifying original
        watermarked = image.copy()

        # Ensure image is in RGBA mode for transparency
        if watermarked.mode != 'RGBA':
            watermarked = watermarked.convert('RGBA')

        # Create transparent overlay
        overlay = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Calculate font size based on image size
        img_width, img_height = watermarked.size
        font_size = max(20, min(img_width, img_height) // 20)

        try:
            # Try to use a built-in font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                # Fallback if no fonts available
                font = None

        # Calculate text position (bottom right with padding)
        if font:
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            # Estimate text size without font
            text_width = len(watermark_text) * font_size // 2
            text_height = font_size

        padding = 20
        x = img_width - text_width - padding
        y = img_height - text_height - padding

        # Draw watermark with semi-transparent white background
        bg_padding = 10
        draw.rectangle([
            x - bg_padding,
            y - bg_padding,
            x + text_width + bg_padding,
            y + text_height + bg_padding
        ], fill=(255, 255, 255, 180))

        # Draw text
        draw.text((x, y), watermark_text, fill=(0, 0, 0, 255), font=font)

        # Composite watermark onto image
        watermarked = Image.alpha_composite(watermarked, overlay)

        return watermarked

    except Exception as e:
        logger.warning(f"Failed to add watermark: {str(e)}")
        return image  # Return original image if watermarking fails

async def batch_local_processing(
    image_paths: list,
    output_dir: str,
    add_watermark: bool = False,
    max_concurrent: int = 2
) -> list:
    """
    Process multiple images locally with concurrency control

    Args:
        image_paths: List of input image paths
        output_dir: Directory for processed images
        add_watermark: Whether to add watermark
        max_concurrent: Maximum concurrent processing

    Returns:
        List of processing results
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_single(image_path: str, index: int) -> Dict[str, Any]:
        async with semaphore:
            output_path = Path(output_dir) / f"{Path(image_path).stem}_processed.png"

            result = await local_background_removal(
                image_path=image_path,
                output_path=str(output_path),
                add_watermark=add_watermark
            )

            result["original_path"] = image_path
            result["index"] = index

            return result

    tasks = [process_single(path, i) for i, path in enumerate(image_paths)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "success": False,
                "error": str(result),
                "original_path": image_paths[i],
                "index": i,
                "method": "local"
            })
        else:
            processed_results.append(result)

    return processed_results