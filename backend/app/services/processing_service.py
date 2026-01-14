"""
Hybrid Processing Service for MASTERPOST.IO V2.0
Routes processing based on user plan and availability
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import time

from ..models.user_models import PlanType, ProcessingMethod, PLAN_CONFIGS
from .simple_processing import process_image_simple
from ...core.config import settings

logger = logging.getLogger(__name__)

class HybridProcessingService:
    """
    Service that routes image processing based on user plan and API availability
    """

    def __init__(self):
        self.local_available = True

    def check_local_availability(self) -> bool:
        """Check if local processing is available"""
        try:
            from rembg import remove
            return True
        except ImportError:
            logger.error("rembg library not available")
            return False

    def get_processing_method(self, user_plan: PlanType, force_method: Optional[ProcessingMethod] = None) -> ProcessingMethod:
        """
        Always return local processing method

        Args:
            user_plan: User's subscription plan (ignored)
            force_method: Override method (ignored)

        Returns:
            Always ProcessingMethod.LOCAL
        """
        return ProcessingMethod.LOCAL

    def process_single_image(
        self,
        image_path: str,
        output_path: str,
        user_plan: PlanType,
        pipeline: str = "amazon",
        force_method: Optional[ProcessingMethod] = None
    ) -> Dict[str, Any]:
        """
        Process a single image using simple local background removal

        Args:
            image_path: Path to input image
            output_path: Path for processed image
            user_plan: User's subscription plan
            pipeline: Target pipeline (amazon, instagram, ebay)
            force_method: Override processing method (ignored - always local)

        Returns:
            Processing result with metadata
        """
        start_time = time.time()

        logger.info(f"Processing {image_path} with local processing, pipeline: {pipeline}")

        try:
            # Use simple local processing for all pipelines
            result = process_image_simple(
                input_path=image_path,
                output_path=output_path,
                pipeline=pipeline
            )

            # Add processing metadata
            result["processing_time"] = time.time() - start_time
            result["user_plan"] = user_plan

            return result

        except Exception as e:
            logger.error(f"Processing failed for {image_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": "local_rembg",
                "user_plan": user_plan,
                "processing_time": time.time() - start_time
            }

    async def process_batch(
        self,
        image_paths: List[str],
        output_dir: str,
        user_plan: PlanType,
        callback=None,
        max_concurrent: int = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple images with plan-appropriate concurrency

        Args:
            image_paths: List of input image paths
            output_dir: Directory for processed images
            user_plan: User's subscription plan
            callback: Progress callback function
            max_concurrent: Override default concurrency limit

        Returns:
            List of processing results
        """
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Set concurrency based on plan
        if max_concurrent is None:
            plan_config = PLAN_CONFIGS.get(user_plan, PLAN_CONFIGS[PlanType.FREE])
            if plan_config.priority_processing:
                max_concurrent = 5  # Higher concurrency for paid plans
            else:
                max_concurrent = 2  # Limited concurrency for free plan

        # Check local availability
        self.check_local_availability()
        method = self.get_processing_method(user_plan)

        logger.info(f"Processing batch of {len(image_paths)} images with local processing, concurrency: {max_concurrent}")

        # Use local batch processing
        try:
            # Process each image individually with local processing
            results = []
            for i, image_path in enumerate(image_paths):
                output_path = Path(output_dir) / f"{Path(image_path).stem}_processed.jpg"

                result = self.process_single_image(
                    image_path=image_path,
                    output_path=str(output_path),
                    user_plan=user_plan,
                    pipeline="amazon"  # Default pipeline for batch
                )

                result["original_path"] = image_path
                result["index"] = i
                results.append(result)

                if callback:
                    await callback(i + 1, total_images, result)

            return results
        except Exception as e:
            logger.error(f"Local batch processing failed: {str(e)}")
            return [{
                "success": False,
                "error": f"Batch processing failed: {str(e)}",
                "method": "local_rembg",
                "user_plan": user_plan
            }]

    def get_processing_info(self, user_plan: PlanType) -> Dict[str, Any]:
        """
        Get information about processing capabilities for a user plan

        Args:
            user_plan: User's subscription plan

        Returns:
            Processing capabilities and status
        """
        self.check_local_availability()

        plan_config = PLAN_CONFIGS.get(user_plan, PLAN_CONFIGS[PlanType.FREE])
        processing_method = self.get_processing_method(user_plan)

        return {
            "plan": user_plan,
            "processing_method": "local_rembg",
            "local_processing_available": self.local_available,
            "priority_processing": plan_config.priority_processing,
            "watermark_required": plan_config.watermark_required,
            "max_images_per_month": plan_config.max_images_per_month,
            "estimated_quality": "standard"
        }

# Singleton instance
processing_service = HybridProcessingService()

# Compatibility functions for existing code
def process_image_hybrid(
    image_path: str,
    output_path: str,
    user_plan: PlanType = PlanType.FREE,
    **kwargs
) -> Dict[str, Any]:
    """Compatibility wrapper for single image processing"""
    return processing_service.process_single_image(
        image_path=image_path,
        output_path=output_path,
        user_plan=user_plan,
        **kwargs
    )

async def process_batch_hybrid(
    image_paths: List[str],
    output_dir: str,
    user_plan: PlanType = PlanType.FREE,
    **kwargs
) -> List[Dict[str, Any]]:
    """Compatibility wrapper for batch processing"""
    return await processing_service.process_batch(
        image_paths=image_paths,
        output_dir=output_dir,
        user_plan=user_plan,
        **kwargs
    )