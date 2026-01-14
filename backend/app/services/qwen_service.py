"""
Qwen Image Edit Service - Official Implementation
Based on Alibaba Cloud Model Studio Official Documentation
https://help.aliyun.com/zh/model-studio/developer-reference/qwen-image-edit-api
"""

import os
import json
import base64
import mimetypes
import logging
import dashscope
from dashscope import MultiModalConversation
from pathlib import Path
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configure Singapore region
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'


class QwenImageEditService:
    """
    Official Qwen Image Edit API Service
    Based on Alibaba Cloud Model Studio documentation
    """

    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.model = "qwen-image-edit"
        self.available = bool(self.api_key)

        if self.api_key:
            logger.info("="*80)
            logger.info("Qwen Image Edit Service Initialized (Official SDK)")
            logger.info(f"  API Key: {self.api_key[:15]}...{self.api_key[-4:]}")
            logger.info(f"  Model: {self.model}")
            logger.info(f"  Base URL: {dashscope.base_http_api_url}")
            logger.info("="*80)
        else:
            logger.warning("WARNING: DASHSCOPE_API_KEY not configured")

    def encode_image_to_base64(self, file_path: str) -> str:
        """
        Convert image to base64 according to official specification
        Format: data:{MIME_type};base64,{base64_data}

        Args:
            file_path: Path to image file

        Returns:
            Base64 encoded image with MIME type prefix
        """
        path = Path(file_path)

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            # Default to JPEG if cannot detect
            mime_type = "image/jpeg"

        # Read and encode
        with open(path, 'rb') as f:
            image_bytes = f.read()
            encoded_string = base64.b64encode(image_bytes).decode('utf-8')

        return f"data:{mime_type};base64,{encoded_string}"

    def remove_background(
        self,
        input_path: str,
        output_path: str,
        prompt: str = None
    ) -> Dict[str, Any]:
        """
        Remove background using Qwen Image Edit API

        Args:
            input_path: Path to input image
            output_path: Path to save processed image
            prompt: Instructions for the model (optional)

        Returns:
            Dict with success status and details
        """

        try:
            # Optimized prompt for background removal
            if not prompt:
                prompt = """Remove the background completely from this product image.
Replace the background with pure white (RGB 255, 255, 255).
Keep the main product with all details preserved.
Remove ALL shadows, reflections, and background elements.
Maintain original product colors."""

            logger.info("="*80)
            logger.info("QWEN IMAGE EDIT - Background Removal")
            logger.info("="*80)
            logger.info(f"Input: {Path(input_path).name}")
            logger.info(f"Prompt: {prompt[:100]}...")

            # Convert image to base64
            image_base64 = self.encode_image_to_base64(input_path)
            logger.info(f"Image encoded: {len(image_base64)} characters")

            # Build messages according to official documentation
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": image_base64},
                        {"text": prompt}
                    ]
                }
            ]

            logger.info("Calling Qwen Image Edit API...")

            # Call API using official SDK
            response = MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                stream=False,
                watermark=False,  # No watermark
                negative_prompt="shadows, reflections, background, blur, artifacts, low quality"
            )

            logger.info(f"Response status: {response.status_code}")

            # Check response
            if response.status_code == 200:
                # Extract processed image URL
                try:
                    image_url = response.output.choices[0].message.content[0]['image']
                    logger.info(f"Image URL received: {image_url[:50]}...")

                    # Download image (valid for 24 hours)
                    logger.info("Downloading processed image...")
                    img_response = requests.get(image_url, timeout=30)

                    if img_response.status_code == 200:
                        # Save
                        with open(output_path, 'wb') as f:
                            f.write(img_response.content)

                        file_size = len(img_response.content)

                        logger.info(f"Image saved: {output_path}")
                        logger.info(f"File size: {file_size / 1024:.1f} KB")
                        logger.info("="*80)
                        logger.info("QWEN PROCESSING SUCCESSFUL!")
                        logger.info("="*80)

                        return {
                            "success": True,
                            "output_path": output_path,
                            "file_size": file_size,
                            "image_url": image_url,
                            "request_id": response.request_id,
                            "method": "qwen_premium"
                        }
                    else:
                        error_msg = f"Failed to download image: HTTP {img_response.status_code}"
                        logger.error(f"ERROR: {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "fallback_to_basic": True
                        }

                except (KeyError, IndexError, AttributeError) as e:
                    error_msg = f"Failed to extract image URL: {str(e)}"
                    logger.error(f"ERROR: {error_msg}")
                    try:
                        logger.error(f"Response: {json.dumps(response.output, ensure_ascii=False)}")
                    except:
                        logger.error(f"Response: {response.output}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "fallback_to_basic": True
                    }
            else:
                # API error
                error_msg = f"API Error {response.status_code}: {response.message}"
                logger.error("="*80)
                logger.error("QWEN API ERROR")
                logger.error(f"  Status: {response.status_code}")
                logger.error(f"  Code: {response.code}")
                logger.error(f"  Message: {response.message}")
                logger.error("="*80)

                return {
                    "success": False,
                    "error": error_msg,
                    "fallback_to_basic": True
                }

        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            logger.error("="*80)
            logger.error("EXCEPTION in Qwen processing")
            logger.error(f"  {error_msg}")
            logger.exception(e)
            logger.error("="*80)

            return {
                "success": False,
                "error": error_msg,
                "fallback_to_basic": True
            }

    async def process_with_qwen_api(self, image_path: str, pipeline: str, output_path: str) -> Dict[str, Any]:
        """
        Async wrapper for compatibility with existing code
        """
        # Optimized prompts by pipeline
        prompts = {
            "amazon": """Remove the background completely from this product image and replace it with pure white (RGB 255, 255, 255).
Keep ONLY the main product, remove everything else.
Preserve all product details with maximum precision.
Ensure the product covers exactly 85% of the image area.
Remove ALL shadows, reflections, and background elements.""",

            "ebay": """Remove the background completely and replace with pure white (RGB 255, 255, 255).
Preserve MAXIMUM detail quality for zoom inspection.
Keep all fine details: textures, engravings, small text.
Remove all background shadows and elements.""",

            "instagram": """Remove the background completely and replace with pure white (RGB 255, 255, 255).
Create a visually appealing, social-media ready image.
Enhance colors while maintaining natural look.
Remove all background elements."""
        }

        prompt = prompts.get(pipeline.lower(), prompts["amazon"])

        return self.remove_background(
            input_path=image_path,
            output_path=output_path,
            prompt=prompt
        )


# Global instance
qwen_service = QwenImageEditService()


# Wrapper for compatibility with existing code
def remove_background_premium_sync(
    input_path: str,
    output_path: str,
    pipeline: str = "amazon"
) -> Dict[str, Any]:
    """
    Synchronous wrapper for Qwen service

    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        pipeline: Pipeline to use (amazon, ebay, instagram)

    Returns:
        Dict with success status and details
    """

    if not qwen_service.available:
        return {
            "success": False,
            "error": "Qwen API not available - API key not configured",
            "fallback_to_basic": True
        }

    # Optimized prompts by pipeline
    prompts = {
        "amazon": """Remove the background completely from this product image and replace it with pure white (RGB 255, 255, 255).
Keep ONLY the main product, remove everything else.
Preserve all product details with maximum precision.
Ensure the product covers exactly 85% of the image area.
Remove ALL shadows, reflections, and background elements.""",

        "ebay": """Remove the background completely and replace with pure white (RGB 255, 255, 255).
Preserve MAXIMUM detail quality for zoom inspection.
Keep all fine details: textures, engravings, small text.
Remove all background shadows and elements.""",

        "instagram": """Remove the background completely and replace with pure white (RGB 255, 255, 255).
Create a visually appealing, social-media ready image.
Enhance colors while maintaining natural look.
Remove all background elements."""
    }

    prompt = prompts.get(pipeline.lower(), prompts["amazon"])

    return qwen_service.remove_background(
        input_path=input_path,
        output_path=output_path,
        prompt=prompt
    )


def health_check() -> Dict[str, Any]:
    """Check Qwen API health"""
    return {
        "status": "ok" if qwen_service.available else "error",
        "available": qwen_service.available,
        "api_key_configured": bool(qwen_service.api_key),
        "model": qwen_service.model,
        "base_url": dashscope.base_http_api_url
    }
