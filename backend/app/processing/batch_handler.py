import asyncio
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import gc

from .image_processor import ImageProcessor
from .pipelines import PipelineFactory
from ..database_sqlite.sqlite_client import sqlite_client
from ..services.simple_processing import remove_background_simple, process_image_simple

logger = logging.getLogger(__name__)

# Batch processing configuration
BATCH_SIZE = 5  # Process images in batches to manage memory

def _generate_short_filename(index: int, original_ext: str) -> str:
    """
    Generate short filename for processed image.

    Args:
        index: Sequential number of the file in the batch (1-based)
        original_ext: Original file extension (.jpg, .png, etc)

    Returns:
        Short name: img_001.jpg, img_002.jpg, etc.
    """
    # Normalize extension to lowercase
    ext = original_ext.lower()
    # Ensure extension starts with dot
    if not ext.startswith('.'):
        ext = f'.{ext}'
    # Fallback to .jpg if extension is not supported
    if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']:
        ext = '.jpg'

    return f"img_{index:03d}{ext}"

class BatchProcessor:
    def __init__(self):
        self.processor = ImageProcessor()
        self.active_jobs: Dict[str, bool] = {}

    async def process_job(
        self,
        job_id: str,
        pipeline_type: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Process a batch job with the specified pipeline"""

        if job_id in self.active_jobs:
            logger.warning(f"Job {job_id} is already being processed")
            return False

        self.active_jobs[job_id] = True

        try:
            # Get job details from database
            job = sqlite_client.get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False

            # Create pipeline
            pipeline = PipelineFactory.create_pipeline(pipeline_type, self.processor)

            # Setup directories
            upload_dir = Path("uploads") / job_id
            processed_dir = Path("processed") / job_id
            processed_dir.mkdir(parents=True, exist_ok=True)

            if not upload_dir.exists():
                logger.error(f"Upload directory not found: {upload_dir}")
                sqlite_client.update_job(job_id, {"status": "failed", "error_message": "Upload directory not found"})
                return False

            # Get all image files
            image_files = [
                f for f in upload_dir.iterdir()
                if f.is_file() and f.suffix.lower() in self.processor.supported_formats
            ]

            if not image_files:
                logger.error(f"No valid image files found in {upload_dir}")
                sqlite_client.update_job(job_id, {"status": "failed", "error_message": "No valid image files found"})
                return False

            total_files = len(image_files)
            processed_count = 0
            failed_count = 0

            logger.info(f"Starting batch processing for job {job_id}: {total_files} files in batches of {BATCH_SIZE}")

            # Process images in batches to manage memory efficiently
            for batch_start in range(0, total_files, BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, total_files)
                batch_files = image_files[batch_start:batch_end]
                batch_number = (batch_start // BATCH_SIZE) + 1

                logger.info(f"Processing batch {batch_number}: images {batch_start+1} to {batch_end} of {total_files}")

                # Process current batch
                for i, image_file in enumerate(batch_files):
                    index = batch_start + i + 1  # Global index for filename

                    try:
                        # Generate short output filename: img_001.jpg, img_002.jpg, etc.
                        output_filename = _generate_short_filename(index, image_file.suffix)
                        output_path = processed_dir / output_filename

                        # Use premium or basic processing based on settings
                        use_premium = settings.get("use_premium", False) if settings else False

                        # Build shadow_params from frontend settings
                        # Frontend sends: shadow_enabled, shadow_type, shadow_intensity
                        # Backend expects: shadow_params = {enabled, type, intensity, ...}
                        shadow_params = None
                        if settings and settings.get("shadow_enabled", False):
                            shadow_params = {
                                "enabled": True,
                                "type": settings.get("shadow_type", "drop"),
                                "intensity": settings.get("shadow_intensity", 0.5),
                                "angle": settings.get("shadow_angle", 315),
                                "distance": settings.get("shadow_distance", 20),
                                "blur_radius": settings.get("shadow_blur", 15)
                            }
                            logger.info(f"[SHADOW] Shadow enabled: {shadow_params}")

                        result = process_image_simple(
                            input_path=str(image_file),
                            output_path=str(output_path),
                            pipeline=pipeline_type,
                            shadow_params=shadow_params,
                            use_premium=use_premium
                        )
                        success = result.get("success", False)

                        if success:
                            processed_count += 1
                            logger.debug(f"Processed {image_file.name} -> {output_filename}")
                        else:
                            failed_count += 1
                            logger.error(f"Failed to process image: {output_filename}")

                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error processing {image_file.name}: {str(e)}")

                    # Update progress after each image
                    sqlite_client.update_job(job_id, {
                        "processed_files": processed_count + failed_count,
                        "failed_files": failed_count
                    })

                # CRITICAL: Force garbage collection after each batch to free memory
                gc.collect()
                logger.info(f"Batch {batch_number} completed. Memory released. Progress: {batch_end}/{total_files}")

                # Brief pause between batches for system stability
                await asyncio.sleep(0.5)

            # Final status update
            if failed_count == 0:
                sqlite_client.update_job(job_id, {"status": "completed"})
                logger.info(f"Job {job_id} completed successfully: {processed_count} files processed")

                # Deduct credits ONLY after successful completion
                job = sqlite_client.get_job(job_id)
                email = job.get("email")
                use_premium = settings.get("use_premium", False) if settings else False
                credits_to_deduct = processed_count * (3 if use_premium else 1)

                if sqlite_client.deduct_credits(email, credits_to_deduct):
                    logger.info(f"✅ {credits_to_deduct} credits deducted from {email} after successful processing")

                    # Increment processing stats
                    if use_premium:
                        sqlite_client.increment_processing_stats(email, basic_count=0, qwen_count=processed_count)
                    else:
                        sqlite_client.increment_processing_stats(email, basic_count=processed_count, qwen_count=0)
                else:
                    logger.error(f"❌ Failed to deduct credits from {email} after processing")
            elif processed_count > 0:
                sqlite_client.update_job(job_id, {
                    "status": "completed_with_errors",
                    "error_message": f"Processed {processed_count} files, {failed_count} failed"
                })
                logger.warning(f"Job {job_id} completed with errors: {processed_count} success, {failed_count} failed")
            else:
                sqlite_client.update_job(job_id, {"status": "failed", "error_message": "All files failed to process"})
                logger.error(f"Job {job_id} failed: all files failed to process")

            return processed_count > 0

        except Exception as e:
            logger.error(f"Critical error in job {job_id}: {str(e)}")
            sqlite_client.update_job(job_id, {"status": "failed", "error_message": str(e)})
            return False

        finally:
            # Remove from active jobs
            self.active_jobs.pop(job_id, None)

class QueueManager:
    def __init__(self):
        self.processor = BatchProcessor()
        self.queue: List[Dict[str, Any]] = []
        self.processing = False

    async def add_job(
        self,
        job_id: str,
        pipeline_type: str,
        settings: Optional[Dict[str, Any]] = None,
        priority: int = 0
    ):
        """Add a job to the processing queue"""
        job_item = {
            'job_id': job_id,
            'pipeline_type': pipeline_type,
            'settings': settings or {},
            'priority': priority,
            'added_at': datetime.utcnow()
        }

        # Insert based on priority (higher priority first)
        inserted = False
        for i, item in enumerate(self.queue):
            if priority > item['priority']:
                self.queue.insert(i, job_item)
                inserted = True
                break

        if not inserted:
            self.queue.append(job_item)

        logger.info(f"Job {job_id} added to queue (priority: {priority}). Queue length: {len(self.queue)}")

        # Start processing if not already running
        if not self.processing:
            asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Process jobs in the queue"""
        if self.processing:
            return

        self.processing = True

        try:
            while self.queue:
                job_item = self.queue.pop(0)
                logger.info(f"Processing job {job_item['job_id']} from queue")

                try:
                    success = await self.processor.process_job(
                        job_item['job_id'],
                        job_item['pipeline_type'],
                        job_item['settings']
                    )

                    if success:
                        logger.info(f"Job {job_item['job_id']} processed successfully")
                    else:
                        logger.error(f"Job {job_item['job_id']} processing failed")

                except Exception as e:
                    logger.error(f"Error processing job {job_item['job_id']}: {str(e)}")

        finally:
            self.processing = False

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            'queue_length': len(self.queue),
            'processing': self.processing,
            'active_jobs': list(self.processor.active_jobs.keys()),
            'next_jobs': [item['job_id'] for item in self.queue[:5]]  # Next 5 jobs
        }

# Global queue manager instance
queue_manager = QueueManager()

async def start_batch_processing(
    job_id: str,
    pipeline: str,
    settings: Optional[Dict[str, Any]] = None
):
    """Start batch processing for a job (called from router)"""
    await queue_manager.add_job(job_id, pipeline, settings)

async def get_queue_status():
    """Get current queue status"""
    return queue_manager.get_queue_status()
