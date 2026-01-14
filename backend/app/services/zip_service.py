"""
ZIP/RAR/7ZIP file processing service for MASTERPOST.IO V2.0
Key differentiator feature - bulk processing of compressed files
"""

import asyncio
import logging
import zipfile
import tempfile
import shutil
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import mimetypes
from PIL import Image

from .usage_service import usage_service
from .processing_service import processing_service
from ..models.user_models import PlanType

logger = logging.getLogger(__name__)

class ZipProcessingService:
    """
    Service for handling compressed file uploads and batch processing
    Supports ZIP, RAR, and 7ZIP formats
    """

    def __init__(self):
        # Check for optional dependencies
        self.has_rarfile = False
        self.has_py7zr = False

        try:
            import rarfile
            self.has_rarfile = True
        except ImportError:
            logger.warning("rarfile not installed - RAR support disabled")

        try:
            import py7zr
            self.has_py7zr = True
        except ImportError:
            logger.warning("py7zr not installed - 7ZIP support disabled")

        # Set supported formats based on available libraries
        self.supported_formats = {'.zip'}
        if self.has_rarfile:
            self.supported_formats.add('.rar')
        if self.has_py7zr:
            self.supported_formats.add('.7z')

        self.image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif'}
        self.max_file_size = 500 * 1024 * 1024  # 500MB max archive size
        self.temp_dir = Path(tempfile.gettempdir()) / "masterpost_extracts"
        self.temp_dir.mkdir(exist_ok=True)

    async def validate_archive(self, file_path: str, user_id: str) -> Dict[str, Any]:
        """
        Validate compressed file before processing

        Args:
            file_path: Path to compressed file
            user_id: User identifier for plan checking

        Returns:
            Validation result with file info
        """
        try:
            file_path = Path(file_path)

            # Check file extension
            if file_path.suffix.lower() not in self.supported_formats:
                return {
                    "valid": False,
                    "error": f"Unsupported format: {file_path.suffix}. Supported: {', '.join(self.supported_formats)}"
                }

            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                size_mb = file_size / (1024 * 1024)
                return {
                    "valid": False,
                    "error": f"File too large: {size_mb:.1f}MB. Maximum: 500MB"
                }

            # Preview archive contents
            image_files = await self._preview_archive_contents(str(file_path))

            if not image_files:
                return {
                    "valid": False,
                    "error": "No valid image files found in archive"
                }

            # Check plan limits
            zip_check = await usage_service.check_zip_limits(user_id, len(image_files))
            if not zip_check["allowed"]:
                return {
                    "valid": False,
                    "error": zip_check["reason"],
                    "limit_exceeded": True
                }

            return {
                "valid": True,
                "format": file_path.suffix.lower(),
                "size_mb": round(file_size / (1024 * 1024), 2),
                "image_count": len(image_files),
                "preview_files": image_files[:10],  # Show first 10 files
                "plan_limits": zip_check
            }

        except Exception as e:
            logger.error(f"Archive validation failed for {file_path}: {str(e)}")
            return {
                "valid": False,
                "error": f"Archive validation failed: {str(e)}"
            }

    async def extract_and_process(
        self,
        archive_path: str,
        user_id: str,
        user_plan: PlanType,
        pipeline: str,
        job_id: str,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Extract archive and process all images

        Args:
            archive_path: Path to compressed file
            user_id: User identifier
            user_plan: User's subscription plan
            pipeline: Processing pipeline to use
            job_id: Job identifier for tracking
            progress_callback: Function to call with progress updates

        Returns:
            Processing results
        """
        extract_dir = None
        try:
            # Create temporary extraction directory
            extract_dir = self.temp_dir / f"extract_{job_id}"
            extract_dir.mkdir(exist_ok=True)

            # Extract archive
            if progress_callback:
                await progress_callback("extracting", 0, 0, "Extracting archive...")

            image_files = await self._extract_archive(archive_path, str(extract_dir))

            if not image_files:
                return {
                    "success": False,
                    "error": "No valid image files found in archive",
                    "files_processed": 0
                }

            # Final usage check before processing
            usage_check = await usage_service.check_usage_limits(user_id, len(image_files))
            if not usage_check.can_process:
                return {
                    "success": False,
                    "error": f"Cannot process {len(image_files)} images. Monthly limit exceeded.",
                    "usage_info": usage_check
                }

            # Create output directory
            output_dir = Path("processed") / job_id
            output_dir.mkdir(parents=True, exist_ok=True)

            # Process images using hybrid service
            if progress_callback:
                await progress_callback("processing", 0, len(image_files), "Starting image processing...")

            async def process_progress_callback(current: int, total: int, result: Dict[str, Any]):
                if progress_callback:
                    status = "processing"
                    message = f"Processing image {current}/{total}: {Path(result.get('original_path', '')).name}"
                    await progress_callback(status, current, total, message)

            results = await processing_service.process_batch(
                image_paths=image_files,
                output_dir=str(output_dir),
                user_plan=user_plan,
                callback=process_progress_callback
            )

            # Track usage
            successful_count = sum(1 for r in results if r.get("success", False))
            if successful_count > 0:
                method = results[0].get("method", "local")
                await usage_service.track_processing(
                    user_id,
                    successful_count,
                    method
                )

            # Create results summary
            failed_files = [r for r in results if not r.get("success", False)]
            successful_files = [r for r in results if r.get("success", False)]

            summary = {
                "success": len(successful_files) > 0,
                "total_files": len(image_files),
                "processed_files": len(successful_files),
                "failed_files": len(failed_files),
                "output_directory": str(output_dir),
                "processing_method": results[0].get("method", "local") if results else "unknown",
                "user_plan": user_plan,
                "archive_format": Path(archive_path).suffix.lower()
            }

            if failed_files:
                summary["errors"] = [
                    {
                        "file": Path(f.get("original_path", "")).name,
                        "error": f.get("error", "Unknown error")
                    }
                    for f in failed_files[:10]  # Limit error list
                ]

            if progress_callback:
                status = "completed" if summary["success"] else "failed"
                message = f"Processed {summary['processed_files']}/{summary['total_files']} images"
                await progress_callback(status, summary["processed_files"], summary["total_files"], message)

            return summary

        except Exception as e:
            logger.error(f"Archive processing failed for {archive_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "files_processed": 0
            }

        finally:
            # Cleanup extraction directory
            if extract_dir and extract_dir.exists():
                try:
                    shutil.rmtree(extract_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup extraction directory: {str(e)}")

    async def _preview_archive_contents(self, archive_path: str) -> List[str]:
        """
        Preview archive contents without extracting

        Args:
            archive_path: Path to archive file

        Returns:
            List of image file paths in archive
        """
        try:
            archive_path = Path(archive_path)
            image_files = []

            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    for file_info in zip_ref.filelist:
                        if not file_info.is_dir() and self._is_image_file(file_info.filename):
                            image_files.append(file_info.filename)

            elif archive_path.suffix.lower() == '.rar' and self.has_rarfile:
                import rarfile
                with rarfile.RarFile(archive_path, 'r') as rar_ref:
                    for file_info in rar_ref.infolist():
                        if not file_info.is_dir() and self._is_image_file(file_info.filename):
                            image_files.append(file_info.filename)

            elif archive_path.suffix.lower() == '.7z' and self.has_py7zr:
                import py7zr
                with py7zr.SevenZipFile(archive_path, 'r') as sz_ref:
                    for file_info in sz_ref.list():
                        if not file_info.is_dir and self._is_image_file(file_info.filename):
                            image_files.append(file_info.filename)

            return image_files

        except Exception as e:
            logger.error(f"Failed to preview archive {archive_path}: {str(e)}")
            return []

    async def _extract_archive(self, archive_path: str, extract_dir: str) -> List[str]:
        """
        Extract archive and return paths to image files

        Args:
            archive_path: Path to archive file
            extract_dir: Directory to extract to

        Returns:
            List of extracted image file paths
        """
        try:
            archive_path = Path(archive_path)
            extract_path = Path(extract_dir)
            image_files = []

            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)

            elif archive_path.suffix.lower() == '.rar' and self.has_rarfile:
                import rarfile
                with rarfile.RarFile(archive_path, 'r') as rar_ref:
                    rar_ref.extractall(extract_path)

            elif archive_path.suffix.lower() == '.7z' and self.has_py7zr:
                import py7zr
                with py7zr.SevenZipFile(archive_path, 'r') as sz_ref:
                    sz_ref.extractall(extract_path)

            # Find all extracted image files
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    if self._is_image_file(file):
                        file_path = Path(root) / file
                        # Validate image can be opened
                        if await self._validate_image_file(str(file_path)):
                            image_files.append(str(file_path))

            return image_files

        except Exception as e:
            logger.error(f"Failed to extract archive {archive_path}: {str(e)}")
            return []

    def _is_image_file(self, filename: str) -> bool:
        """Check if file is a supported image format"""
        return Path(filename).suffix.lower() in self.image_extensions

    async def _validate_image_file(self, file_path: str) -> bool:
        """
        Validate that file is a valid image

        Args:
            file_path: Path to image file

        Returns:
            True if valid image
        """
        try:
            with Image.open(file_path) as img:
                # Try to load the image to verify it's valid
                img.verify()
                return True
        except Exception:
            return False

    async def create_results_archive(self, processed_dir: str, job_id: str) -> str:
        """
        Create ZIP archive of processed images

        Args:
            processed_dir: Directory containing processed images
            job_id: Job identifier

        Returns:
            Path to created archive
        """
        try:
            processed_path = Path(processed_dir)
            archive_path = processed_path.parent / f"masterpost_{job_id}_processed.zip"

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for file_path in processed_path.glob("*"):
                    if file_path.is_file():
                        zip_ref.write(file_path, file_path.name)

            return str(archive_path)

        except Exception as e:
            logger.error(f"Failed to create results archive: {str(e)}")
            raise

    async def get_extraction_info(self, archive_path: str) -> Dict[str, Any]:
        """
        Get detailed information about archive without extracting

        Args:
            archive_path: Path to archive file

        Returns:
            Archive information
        """
        try:
            archive_path = Path(archive_path)

            # Basic file info
            file_size = archive_path.stat().st_size

            # Get file listing
            image_files = await self._preview_archive_contents(str(archive_path))

            # Calculate estimated processing time (rough estimate)
            estimated_minutes = max(1, len(image_files) * 0.5)  # 30 seconds per image average

            return {
                "format": archive_path.suffix.lower(),
                "size_mb": round(file_size / (1024 * 1024), 2),
                "total_files": len(image_files),
                "image_files": image_files,
                "estimated_processing_minutes": round(estimated_minutes, 1),
                "supported_formats": list(self.image_extensions)
            }

        except Exception as e:
            logger.error(f"Failed to get archive info for {archive_path}: {str(e)}")
            return {"error": str(e)}

# Singleton instance
zip_service = ZipProcessingService()

# Helper functions
async def process_zip_upload(
    archive_path: str,
    user_id: str,
    user_plan: PlanType,
    pipeline: str,
    job_id: str,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Process uploaded ZIP file - main entry point

    Args:
        archive_path: Path to uploaded archive
        user_id: User identifier
        user_plan: User's plan
        pipeline: Processing pipeline
        job_id: Job ID for tracking
        progress_callback: Progress callback function

    Returns:
        Processing results
    """
    return await zip_service.extract_and_process(
        archive_path=archive_path,
        user_id=user_id,
        user_plan=user_plan,
        pipeline=pipeline,
        job_id=job_id,
        progress_callback=progress_callback
    )

async def validate_zip_upload(file_path: str, user_id: str) -> Dict[str, Any]:
    """
    Validate ZIP file before processing

    Args:
        file_path: Path to uploaded file
        user_id: User identifier

    Returns:
        Validation result
    """
    return await zip_service.validate_archive(file_path, user_id)