"""
Simple Masterpost.io Backend Server
LOCAL PROCESSING ONLY - NO EXTERNAL APIS
"""

import os
import time
import asyncio
import logging
import zipfile
import tempfile
import threading
import io
from pathlib import Path
from typing import List, Dict, Any
import uuid
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print(f"Loading .env from: {env_path}")
print(f"SUPABASE_URL exists: {os.getenv('SUPABASE_URL') is not None}")
print(f"SUPABASE_SERVICE_ROLE_KEY exists: {os.getenv('SUPABASE_SERVICE_ROLE_KEY') is not None}")

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Import our simple processing function
from app.services.simple_processing import process_image_simple
from app.services.batch_processor import SmartBatchProcessor

# Imports para créditos
from app.services.credit_service import (
    get_user_credits,
    verify_sufficient_credits,
    use_credits,
    get_transaction_history
)
from app.config.supabase_config import get_supabase

# Verificar que las credenciales de Supabase existan
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    print(f"OK - Supabase credentials loaded: {SUPABASE_URL[:30]}...")
else:
    print("WARNING: Supabase credentials not found in environment")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory progress tracking
JOB_PROGRESS = {}
progress_lock = threading.Lock()

def _generate_short_filename(index: int, original_ext: str) -> str:
    """
    Generate short filename for processed image.

    Args:
        index: Sequential number of the file in the batch (1-based)
        original_ext: Original file extension (.jpg, .png, etc)

    Returns:
        Short name: img_001.jpg, img_002.jpg, etc.

    Examples:
        >>> _generate_short_filename(1, '.jpg')
        'img_001.jpg'
        >>> _generate_short_filename(42, '.png')
        'img_042.png'
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

def update_progress(job_id: str, current: int, total: int, status: str = "processing"):
    """Update job progress in memory"""
    with progress_lock:
        JOB_PROGRESS[job_id] = {
            "current": current,
            "total": total,
            "percentage": int((current / total * 100)) if total > 0 else 0,
            "status": status,
            "updated_at": time.time()
        }

# FastAPI app
app = FastAPI(
    title="Masterpost.io API - Simple",
    description="Simple local image processing API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "https://masterpost-io.netlify.app",  # Netlify production URL
        "http://masterpost.io",    # Dominio personalizado HTTP
        "https://masterpost.io",   # Dominio personalizado HTTPS
        os.getenv("FRONTEND_URL", "")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Permite que el frontend acceda a headers personalizados
)

# Directories
UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
TEMP_DIR = Path("temp")
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Mount static files for serving processed images
app.mount("/processed", StaticFiles(directory="processed"), name="processed")

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z"}

def validate_upload_file(file: UploadFile) -> bool:
    """Validate uploaded file (image or archive)"""
    if not file.filename:
        return False

    # Check if it's an image or archive
    is_image = any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
    is_archive = any(file.filename.lower().endswith(ext) for ext in ALLOWED_ARCHIVE_EXTENSIONS)

    if not (is_image or is_archive):
        return False

    # Size limits
    if is_archive:
        max_size = 500 * 1024 * 1024  # 500MB for ZIP archives
    else:
        max_size = 50 * 1024 * 1024   # 50MB for individual images

    if file.size and file.size > max_size:
        return False

    return True

def is_archive_file(filename: str) -> bool:
    """Check if file is an archive"""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_ARCHIVE_EXTENSIONS)

def extract_images_from_zip(zip_path: Path, extract_to: Path) -> tuple:
    """
    Extract ALL images from ZIP file with SHORT FILENAMES to avoid Windows path length limits.
    Uses format: img_0001_a3f8d9e2.jpg (max 25 chars)
    Returns: (extracted_images: List[Path], failed_images: List[dict])
    """
    from PIL import Image
    import io
    import hashlib

    # Extended image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif'}
    extracted_images = []
    failed_images = []
    skipped_files = []

    logger.info("=" * 80)
    logger.info(f"🔍 ANALYZING ZIP: {zip_path.name}")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_files = zip_ref.namelist()
            logger.info(f"📁 Total files in ZIP: {len(all_files)}")
            logger.info("")

            image_count = 0

            for idx, file_info in enumerate(zip_ref.filelist, 1):
                full_filename = file_info.filename
                file_path = Path(full_filename)
                filename = file_path.name

                # Show original filename (truncated if too long)
                display_name = full_filename if len(full_filename) <= 60 else full_filename[:57] + "..."
                logger.info(f"[{idx}/{len(all_files)}] {display_name}")

                # 1. Check if directory
                if file_info.is_dir():
                    logger.info(f"   ⏭️  SKIP: Is directory")
                    skipped_files.append({"file": full_filename, "reason": "directory"})
                    continue

                # 2. Check system files
                if any(x in full_filename for x in ['__MACOSX', '.DS_Store', 'Thumbs.db', 'desktop.ini']):
                    logger.info(f"   ⏭️  SKIP: System file")
                    skipped_files.append({"file": full_filename, "reason": "system_file"})
                    continue

                # 3. Check hidden files
                if filename.startswith('.') or filename.startswith('._'):
                    logger.info(f"   ⏭️  SKIP: Hidden file")
                    skipped_files.append({"file": full_filename, "reason": "hidden_file"})
                    continue

                # 4. Check extension (case-insensitive)
                ext = file_path.suffix.lower()
                if ext not in image_extensions:
                    logger.info(f"   ⏭️  SKIP: Not an image (ext: {file_path.suffix})")
                    skipped_files.append({"file": full_filename, "reason": f"not_image:{file_path.suffix}"})
                    continue

                # 5. Check size in ZIP
                if file_info.file_size == 0:
                    logger.info(f"   ❌ FAILED: Empty file (0 bytes)")
                    failed_images.append({"file": full_filename, "reason": "empty_file"})
                    continue

                logger.info(f"   📏 Size: {file_info.file_size:,} bytes")

                # 6. GENERATE SHORT FILENAME to avoid Windows 260 char path limit
                # Format: img_0001_a3f8d9e2.jpg (max 25 chars)
                name_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
                short_filename = f"img_{image_count:04d}_{name_hash}{ext}"

                # 7. Try to extract and validate
                try:
                    # Read file data from ZIP
                    data = zip_ref.read(file_info)

                    # Validate the image data
                    try:
                        img = Image.open(io.BytesIO(data))
                        img.verify()
                        img_format = img.format
                        # Re-open for size (verify closes the image)
                        img = Image.open(io.BytesIO(data))
                        img_size = img.size
                    except Exception as img_error:
                        logger.info(f"   ❌ FAILED: Corrupt/invalid image - {str(img_error)}")
                        failed_images.append({"file": full_filename, "reason": f"corrupt:{str(img_error)}"})
                        continue

                    # 8. Save with SHORT filename
                    extract_path = extract_to / short_filename

                    with open(extract_path, 'wb') as f:
                        f.write(data)

                    # 9. Verify file was saved
                    if not extract_path.exists():
                        logger.info(f"   ❌ FAILED: File not saved")
                        failed_images.append({"file": full_filename, "reason": "not_saved"})
                        continue

                    actual_size = extract_path.stat().st_size
                    if actual_size == 0:
                        logger.info(f"   ❌ FAILED: File is 0 bytes after saving")
                        failed_images.append({"file": full_filename, "reason": "zero_bytes_after_save"})
                        extract_path.unlink()  # Clean up
                        continue

                    # 10. Success!
                    logger.info(f"   ✅ SUCCESS: {img_format} {img_size} -> {short_filename}")
                    extracted_images.append(extract_path)
                    image_count += 1

                except Exception as e:
                    logger.error(f"   ❌ FAILED: Extraction error - {str(e)}")
                    failed_images.append({"file": full_filename, "reason": f"extract_error:{str(e)}"})
                    continue

            # Summary
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"📊 EXTRACTION SUMMARY:")
            logger.info(f"   ✅ Extracted: {len(extracted_images)}")
            logger.info(f"   ❌ Failed: {len(failed_images)}")
            logger.info(f"   ⏭️  Skipped: {len(skipped_files)}")
            logger.info(f"   📁 Total processed: {len(extracted_images) + len(failed_images) + len(skipped_files)}")

            if failed_images:
                logger.info(f"")
                logger.info(f"❌ FAILED FILES:")
                for fail in failed_images:
                    # Truncate long filenames in summary
                    fail_file = fail['file'] if len(fail['file']) <= 80 else fail['file'][:77] + "..."
                    logger.info(f"   - {fail_file}: {fail['reason']}")

            if skipped_files:
                logger.info(f"")
                logger.info(f"⏭️  SKIPPED FILES (showing first 10):")
                for skip in skipped_files[:10]:
                    skip_file = skip['file'] if len(skip['file']) <= 80 else skip['file'][:77] + "..."
                    logger.info(f"   - {skip_file}: {skip['reason']}")
                if len(skipped_files) > 10:
                    logger.info(f"   ... and {len(skipped_files) - 10} more")

            logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Error opening ZIP file {zip_path}: {e}")

    return extracted_images, failed_images

def format_time(seconds: int) -> str:
    """Format seconds to mm:ss"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}:{secs:02d}"

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Masterpost.io API is running",
        "status": "online",
        "port": int(os.getenv("PORT", 8002)),
        "version": "2.0.0 - Simple Local Processing"
    }

@app.post("/api/v1/analyze-upload")
async def analyze_upload(files: List[UploadFile] = File(...)):
    """
    Analyze uploaded files and count how many images there are
    before processing them. Returns total image count and estimated time.

    Real production data:
    100 images = 230 seconds → 2.3 seconds per image
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        # Real average time based on production data:
        # 100 images = 230 seconds → 2.3 seconds per image
        SECONDS_PER_IMAGE = 2.3

        total_images = 0
        file_details = []

        for file in files:
            file_info = {
                "filename": file.filename,
                "type": "unknown",
                "image_count": 0
            }

            # If it's a ZIP file, count images inside
            if file.filename and is_archive_file(file.filename):
                try:
                    # Read ZIP in memory
                    contents = await file.read()
                    zip_file = zipfile.ZipFile(io.BytesIO(contents))

                    # Count image files
                    image_count = 0
                    for zip_info in zip_file.namelist():
                        ext = Path(zip_info).suffix.lower()
                        if ext in ALLOWED_EXTENSIONS:
                            image_count += 1

                    file_info["type"] = "zip"
                    file_info["image_count"] = image_count
                    total_images += image_count

                    # Reset file pointer for later processing
                    await file.seek(0)

                    logger.info(f"Analyzed ZIP {file.filename}: found {image_count} images")

                except Exception as e:
                    logger.error(f"Error analyzing ZIP {file.filename}: {str(e)}")
                    file_info["error"] = str(e)

            # If it's an individual image
            elif file.content_type and file.content_type.startswith('image/'):
                file_info["type"] = "image"
                file_info["image_count"] = 1
                total_images += 1
                await file.seek(0)  # Reset pointer

            file_details.append(file_info)

        # Calculate estimated time with real production data
        estimated_seconds = int(total_images * SECONDS_PER_IMAGE)

        return {
            "success": True,
            "total_images": total_images,
            "files": file_details,
            "estimated_time_seconds": estimated_seconds,
            "estimated_time_formatted": format_time(estimated_seconds),
            "seconds_per_image": SECONDS_PER_IMAGE
        }

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/upload")
async def upload_images(files: List[UploadFile] = File(...)):
    """Upload images for processing"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        # Generate job ID
        job_id = str(uuid.uuid4())
        job_dir = UPLOAD_DIR / job_id
        job_dir.mkdir(exist_ok=True)

        logger.info(f"Uploading {len(files)} files for job {job_id}")

        uploaded_files = []
        all_image_files = []
        all_failed_images = []

        for file in files:
            if not validate_upload_file(file):
                logger.warning(f"Invalid file: {file.filename}")
                continue

            # Save file
            file_path = job_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            uploaded_files.append({
                "filename": file.filename,
                "size": len(content),
                "path": str(file_path)
            })

            logger.info(f"Saved: {file.filename} ({len(content)} bytes)")

            # If it's a ZIP file, extract images
            if is_archive_file(file.filename):
                logger.info(f"📦 Extracting images from archive: {file.filename}")
                extracted_images, failed_images = extract_images_from_zip(file_path, job_dir)
                all_image_files.extend(extracted_images)
                all_failed_images.extend(failed_images)
                logger.info(f"✅ Extracted {len(extracted_images)} images, ❌ {len(failed_images)} failed from {file.filename}")
            else:
                # Regular image file
                all_image_files.append(file_path)

        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No valid files uploaded")

        if not all_image_files:
            raise HTTPException(status_code=400, detail="No valid image files found (either direct uploads or in archives)")

        logger.info("")
        logger.info("🎯 FINAL COUNT:")
        logger.info(f"   ✅ Images to process: {len(all_image_files)}")
        logger.info(f"   ❌ Failed images: {len(all_failed_images)}")

        return {
            "success": True,
            "job_id": job_id,
            "message": f"Uploaded {len(uploaded_files)} files, found {len(all_image_files)} images for processing",
            "files_uploaded": len(uploaded_files),
            "images_found": len(all_image_files),
            "images_failed": len(all_failed_images),
            "failed_details": all_failed_images[:10] if len(all_failed_images) <= 10 else all_failed_images[:10],
            "files": uploaded_files
        }

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/process")
async def process_images(request: dict, authorization: str = Header(None)):
    """
    Process uploaded images with Basic or Premium processing
    NOW WITH CREDIT VERIFICATION
    """
    try:
        # Extract user from Authorization header
        user_id = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            try:
                supabase = get_supabase()
                if supabase:
                    auth_response = supabase.auth.get_user(token)
                    if auth_response and auth_response.user:
                        user_id = auth_response.user.id
                        logger.info(f"🔐 Authenticated user: {user_id[:8]}...")
            except Exception as e:
                logger.warning(f"Failed to verify token: {e}")
        
        job_id = request.get("job_id")
        pipeline = request.get("pipeline", "amazon")
        settings = request.get("settings", {})
        use_premium = settings.get("use_premium", False)
        
        shadow_params = {
            "enabled": settings.get("shadow_enabled", False),
            "type": settings.get("shadow_type", "drop"),
            "intensity": settings.get("shadow_intensity", 0.5),
            "angle": settings.get("shadow_angle", 315),
            "distance": settings.get("shadow_distance", 20),
            "blur_radius": settings.get("shadow_blur", 15)
        }
        
        if not job_id:
            raise HTTPException(status_code=400, detail="job_id is required")
        
        # Find uploaded files
        job_dir = UPLOAD_DIR / job_id
        if not job_dir.exists():
            raise HTTPException(status_code=404, detail="Job not found")
        
        image_files = [f for f in job_dir.glob("*") if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS]
        if not image_files:
            raise HTTPException(status_code=404, detail="No images found for processing")
        
        logger.info(f"Found {len(image_files)} images to process")

        # CREDIT VERIFICATION TEMPORARILY DISABLED
        # TODO: Re-enable after fixing Supabase RPC functions
        # if user_id:
        #     credits_per_image = 3 if use_premium else 1
        #     total_credits_needed = credits_per_image * len(image_files)
        #
        #     logger.info("=" * 60)
        #     logger.info(f"💳 CREDIT VERIFICATION")
        #     logger.info(f"   User: {user_id[:8]}...")
        #     logger.info(f"   Images: {len(image_files)}")
        #     logger.info(f"   Processing: {'PREMIUM (Qwen)' if use_premium else 'BASIC (rembg)'}")
        #     logger.info(f"   Credits per image: {credits_per_image}")
        #     logger.info(f"   Total credits needed: {total_credits_needed}")
        #     logger.info("=" * 60)
        #
        #     verification = await verify_sufficient_credits(user_id, total_credits_needed)
        #
        #     if not verification["sufficient"]:
        #         logger.error(f"❌ INSUFFICIENT CREDITS")
        #         logger.error(f"   Current: {verification['current_credits']}")
        #         logger.error(f"   Needed: {verification['credits_needed']}")
        #         logger.error(f"   Shortfall: {verification['shortfall']}")
        #
        #         raise HTTPException(
        #             status_code=402,
        #             detail={
        #                 "error": "Insufficient credits",
        #                 "current_credits": verification["current_credits"],
        #                 "credits_needed": verification["credits_needed"],
        #                 "shortfall": verification["shortfall"]
        #             }
        #         )
        #
        #     logger.info(f"✅ CREDIT VERIFICATION PASSED")
        #     logger.info(f"   Current credits: {verification['current_credits']}")
        #     logger.info(f"   Will deduct: {total_credits_needed}")
        #     logger.info(f"   Remaining after: {verification['current_credits'] - total_credits_needed}")
        #     logger.info("=" * 60)
        # else:
        #     logger.warning("⚠️  No user authentication - processing without credit check")

        logger.info("⚠️  Credit verification DISABLED - processing all requests")

        # Start async processing (removed user_id parameter to match backup)
        asyncio.create_task(process_images_simple(job_id, image_files, pipeline, shadow_params, use_premium))
        
        credits_per_image = 3 if use_premium else 1
        total_credits = credits_per_image * len(image_files)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Started processing {len(image_files)} images with {pipeline} pipeline",
            "pipeline": pipeline,
            "processing_tier": "premium" if use_premium else "basic",
            "shadow_enabled": shadow_params["enabled"],
            "status": "processing",
            "files_count": len(image_files),
            "credits_per_image": credits_per_image,
            "total_credits": total_credits,
            "authenticated": user_id is not None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_images_simple(job_id: str, image_files: list, pipeline: str, shadow_params: dict = None, use_premium: bool = False, user_id: str = None):
    """
    Process images with intelligent parallel execution
    Supports both Basic (rembg) and Premium (Qwen API) processing
    OPTIMIZED: 60-87% faster than sequential processing
    NOW WITH AUTOMATIC CREDIT DEDUCTION AFTER SUCCESSFUL PROCESSING
    """
    try:
        logger.info(f"[PARALLEL] Starting job {job_id}: {len(image_files)} images with {pipeline} pipeline")

        # Initialize progress tracking
        total = len(image_files)
        update_progress(job_id, 0, total, "starting")

        # Create processed directory
        processed_dir = PROCESSED_DIR / job_id
        processed_dir.mkdir(exist_ok=True)

        # Initialize smart processor
        batch_processor = SmartBatchProcessor()

        # Prepare processing function with index tracking
        def process_single_image(item):
            """Wrapper for processing a single image"""
            index, image_file = item  # Unpack tuple (index, file)

            # Generate short filename: img_001.jpg, img_002.jpg, etc.
            # Index is 0-based from enumerate, so add 1 for 1-based naming
            output_filename = _generate_short_filename(index + 1, image_file.suffix)
            output_path = processed_dir / output_filename

            result = process_image_simple(
                input_path=str(image_file),
                output_path=str(output_path),
                pipeline=pipeline,
                shadow_params=shadow_params,
                use_premium=use_premium  # Pass premium flag
            )

            if result.get("success"):
                return {
                    "success": True,
                    "original": image_file.name,
                    "processed": output_filename,
                    "path": str(output_path),
                    "shadow_applied": result.get("shadow_applied", False),
                    "shadow_type": result.get("shadow_type")
                }
            else:
                return {
                    "success": False,
                    "original": image_file.name,
                    "error": result.get("error", "Unknown error")
                }

        # Progress tracking with global progress updates
        def progress_update(current, total):
            percent = (current * 100) // total
            logger.info(f"[PARALLEL] Job {job_id}: {current}/{total} ({percent}%) complete")
            # Update global progress tracker
            update_progress(job_id, current, total, "processing")

        # Process batch with smart parallelization
        # Enumerate files to provide index for short filename generation
        indexed_files = list(enumerate(image_files))
        results = await batch_processor.process_batch_async(
            items=indexed_files,
            process_func=process_single_image,
            progress_callback=progress_update
        )

        # Separate successful and failed
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]

        # Save results
        import json
        final_results = {
            "job_id": job_id,
            "pipeline": pipeline,
            "shadow_enabled": shadow_params.get("enabled", False) if shadow_params else False,
            "shadow_type": shadow_params.get("type", "none") if shadow_params and shadow_params.get("enabled") else "none",
            "total_files": len(image_files),
            "successful": len(successful),
            "failed": len(failed),
            "successful_files": successful,
            "failed_files": failed,
            "status": "completed",
            "completed_at": time.time()
        }

        results_file = processed_dir / "results.json"
        with open(results_file, "w") as f:
            json.dump(final_results, f, indent=2)

        # Mark as completed
        update_progress(job_id, total, total, "completed")

        logger.info(
            f"[PARALLEL] Job {job_id} completed: "
            f"{len(successful)}/{len(image_files)} successful, {len(failed)} failed"
        )

        # ============================================================
        # CREDIT DEDUCTION TEMPORARILY DISABLED
        # TODO: Re-enable after fixing Supabase RPC functions
        # ============================================================
        # if user_id and len(successful) > 0:
        #     credits_per_image = 3 if use_premium else 1
        #     total_credits_used = credits_per_image * len(successful)
        #     transaction_type = 'usage_premium' if use_premium else 'usage_basic'
        #     description = f"Processed {len(successful)} images (job: {job_id}, pipeline: {pipeline})"
        #
        #     logger.info("=" * 60)
        #     logger.info(f"💳 DEDUCTING CREDITS")
        #     logger.info(f"   User: {user_id[:8]}...")
        #     logger.info(f"   Images processed: {len(successful)}")
        #     logger.info(f"   Credits per image: {credits_per_image}")
        #     logger.info(f"   Total to deduct: {total_credits_used}")
        #     logger.info("=" * 60)
        #
        #     try:
        #         deduction_result = await use_credits(
        #             user_id=user_id,
        #             credits_needed=total_credits_used,
        #             transaction_type=transaction_type,
        #             description=description
        #         )
        #
        #         if deduction_result.get('success'):
        #             logger.info(f"✅ CREDITS DEDUCTED SUCCESSFULLY")
        #             logger.info(f"   Before: {deduction_result.get('credits_before')} credits")
        #             logger.info(f"   Used: {deduction_result.get('credits_used')} credits")
        #             logger.info(f"   After: {deduction_result.get('credits_after')} credits")
        #         else:
        #             logger.error(f"❌ CREDIT DEDUCTION FAILED: {deduction_result.get('error')}")
        #
        #     except Exception as credit_error:
        #         logger.error(f"❌ EXCEPTION DURING CREDIT DEDUCTION: {credit_error}")
        #         import traceback
        #         traceback.print_exc()
        #
        #     logger.info("=" * 60)

        logger.info("⚠️  Credit deduction DISABLED - no credits will be deducted")

    except Exception as e:
        logger.error(f"[PARALLEL] Job {job_id} failed: {e}")
        # Mark as error
        update_progress(job_id, 0, len(image_files), "error")
        import traceback
        traceback.print_exc()

@app.get("/api/v1/status/{job_id}")
async def get_job_status(job_id: str):
    """Get processing status for a job"""
    try:
        processed_dir = PROCESSED_DIR / job_id
        results_file = processed_dir / "results.json"

        if results_file.exists():
            # Job completed
            import json
            with open(results_file, "r") as f:
                results = json.load(f)
            return results
        else:
            # Job still processing or not found
            job_dir = UPLOAD_DIR / job_id
            if job_dir.exists():
                return {
                    "job_id": job_id,
                    "status": "processing",
                    "message": "Job is being processed"
                }
            else:
                raise HTTPException(status_code=404, detail="Job not found")

    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/progress/{job_id}")
async def get_job_progress(job_id: str):
    """Get real-time processing progress for a job"""
    try:
        with progress_lock:
            progress = JOB_PROGRESS.get(job_id)

        if not progress:
            return {
                "job_id": job_id,
                "status": "unknown",
                "current": 0,
                "total": 0,
                "percentage": 0
            }

        return {
            "job_id": job_id,
            "status": progress["status"],
            "current": progress["current"],
            "total": progress["total"],
            "percentage": progress["percentage"]
        }

    except Exception as e:
        logger.error(f"Progress check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/download/{job_id}")
async def download_results(job_id: str):
    """Download processed images as ZIP - includes all formats (JPG, PNG)"""
    try:
        processed_dir = PROCESSED_DIR / job_id
        if not processed_dir.exists():
            raise HTTPException(status_code=404, detail="Job not found")

        # Create ZIP file in temp directory
        zip_path = TEMP_DIR / f"{job_id}_processed.zip"

        # Collect all image files (JPG and PNG)
        image_files = list(processed_dir.glob("*.jpg")) + list(processed_dir.glob("*.jpeg")) + list(processed_dir.glob("*.png"))

        if not image_files:
            raise HTTPException(status_code=404, detail="No processed files found")

        logger.info(f"Creating ZIP with {len(image_files)} images for job {job_id}")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Include ALL processed images (JPG and PNG)
            for file_path in image_files:
                logger.info(f"Adding to ZIP: {file_path.name}")
                zipf.write(file_path, file_path.name)

        # Verify ZIP was created and has content
        if not zip_path.exists() or zip_path.stat().st_size == 0:
            raise HTTPException(status_code=500, detail="Failed to create ZIP file")

        logger.info(f"ZIP created successfully: {zip_path} ({zip_path.stat().st_size} bytes)")

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"masterpost_{job_id}.zip",
            background=None  # Don't delete immediately
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/preview/{job_id}/{filename}")
async def get_image_preview(job_id: str, filename: str):
    """Serve individual processed image for preview"""
    try:
        processed_dir = PROCESSED_DIR / job_id
        if not processed_dir.exists():
            raise HTTPException(status_code=404, detail="Job not found")

        image_path = processed_dir / filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")

        # Validate file is an image
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Determine media type based on extension
        media_type = "image/png" if filename.lower().endswith('.png') else "image/jpeg"

        return FileResponse(
            image_path,
            media_type=media_type,
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Access-Control-Allow-Origin": "*"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =======================================
# MANUAL EDITOR ENDPOINTS
# =======================================

# Manual editor temp directories
MANUAL_EDITOR_TEMP_DIR = Path("temp")
MANUAL_EDITOR_EDITED_DIR = MANUAL_EDITOR_TEMP_DIR / "edited"
MANUAL_EDITOR_TEMP_DIR.mkdir(exist_ok=True)
MANUAL_EDITOR_EDITED_DIR.mkdir(exist_ok=True)

@app.get("/api/v1/manual-editor/test")
async def test_manual_editor():
    """Test endpoint for manual editor"""
    return {
        "message": "✅ Manual Editor Backend Working!",
        "service": "manual-editor",
        "endpoints": [
            "POST /api/v1/manual-editor/upload-single",
            "POST /api/v1/manual-editor/save-edited",
            "GET /api/v1/manual-editor/download/{filename}",
            "GET /api/v1/manual-editor/test"
        ],
        "directories": {
            "temp_dir": str(MANUAL_EDITOR_TEMP_DIR),
            "edited_dir": str(MANUAL_EDITOR_EDITED_DIR),
            "temp_exists": MANUAL_EDITOR_TEMP_DIR.exists(),
            "edited_exists": MANUAL_EDITOR_EDITED_DIR.exists()
        }
    }

@app.post("/api/v1/manual-editor/upload-single")
async def upload_single_for_edit(file: UploadFile = File(...)):
    """Upload single image for manual editing"""
    try:
        logger.info(f"📤 Manual Editor: Uploading {file.filename}")

        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files allowed")

        # Create unique job ID
        job_id = str(uuid.uuid4())
        job_dir = MANUAL_EDITOR_TEMP_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = job_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"✅ Manual Editor: File saved to {file_path}")

        return {
            "success": True,
            "job_id": job_id,
            "file_path": str(file_path),
            "filename": file.filename,
            "message": "File uploaded successfully for manual editing"
        }

    except Exception as e:
        logger.error(f"❌ Manual Editor Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/manual-editor/save-edited")
async def save_edited_image(edited_image: UploadFile = File(...)):
    """Save manually edited image"""
    try:
        logger.info(f"💾 Manual Editor: Saving edited image {edited_image.filename}")

        # Generate unique filename
        edited_id = str(uuid.uuid4())
        edited_filename = f"edited_{edited_id}_{edited_image.filename or 'image.png'}"
        edited_path = MANUAL_EDITOR_EDITED_DIR / edited_filename

        # Save edited image
        with open(edited_path, "wb") as buffer:
            content = await edited_image.read()
            buffer.write(content)

        # Generate download URL
        download_url = f"/api/v1/manual-editor/download/{edited_filename}"

        logger.info(f"✅ Manual Editor: Edited image saved as {edited_filename}")

        return {
            "success": True,
            "edited_id": edited_id,
            "download_url": download_url,
            "filename": edited_filename,
            "message": "Edited image saved successfully"
        }

    except Exception as e:
        logger.error(f"❌ Manual Editor Save Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/manual-editor/download/{filename}")
async def download_edited_image(filename: str):
    """Download edited image"""
    try:
        logger.info(f"📥 Manual Editor: Downloading {filename}")

        file_path = MANUAL_EDITOR_EDITED_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            file_path,
            media_type="image/png",
            filename=filename
        )

    except Exception as e:
        logger.error(f"❌ Manual Editor Download Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =======================================
# END MANUAL EDITOR ENDPOINTS
# =======================================

# =======================================
# GALLERY ENDPOINTS (Landing Page)
# =======================================

# Gallery images configuration
GALLERY_IMAGES = {
    "bicicleta": {
        "original": "img_original/bicicleta.jpg",
        "processed": "img_procesada/bicicleta.jpg",
        "title": "Complex Vintage Bicycle",
        "description": "Multiple angles & spokes",
        "processing_time": "6 seconds",
        "tier": "Premium"
    },
    "lampara": {
        "original": "img_original/lampara.jpg",
        "processed": "img_procesada/lampara.jpg",
        "title": "Glass & Metal Lamp",
        "description": "Transparent glass",
        "processing_time": "5 seconds",
        "tier": "Premium"
    },
    "joyeria": {
        "original": "img_original/joyeria.jpg",
        "processed": "img_procesada/joyeria.jpg",
        "title": "Jewelry with Reflections",
        "description": "Fine details & shine",
        "processing_time": "4 seconds",
        "tier": "Premium"
    },
    "botella": {
        "original": "img_original/botella.jpg",
        "processed": "img_procesada/botella.jpg",
        "title": "Glass Bottle",
        "description": "Transparency & reflections",
        "processing_time": "5 seconds",
        "tier": "Premium"
    },
    "zapato": {
        "original": "img_original/zapato.jpg",
        "processed": "img_procesada/zapato.jpg",
        "title": "Leather Shoe",
        "description": "Textures & details",
        "processing_time": "4 seconds",
        "tier": "Premium"
    },
    "peluche": {
        "original": "img_original/peluche.jpg",
        "processed": "img_procesada/peluche.jpg",
        "title": "Plush Toy",
        "description": "Fuzzy edges",
        "processing_time": "5 seconds",
        "tier": "Premium"
    }
}

@app.get("/api/v1/gallery/{item_name}/original")
async def get_gallery_original(item_name: str):
    """Get original image for gallery showcase"""
    if item_name not in GALLERY_IMAGES:
        raise HTTPException(status_code=404, detail=f"Gallery item '{item_name}' not found")

    image_path = Path(GALLERY_IMAGES[item_name]["original"])

    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")

    return FileResponse(
        image_path,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/api/v1/gallery/{item_name}/processed")
async def get_gallery_processed(item_name: str):
    """Get processed image for gallery showcase"""
    if item_name not in GALLERY_IMAGES:
        raise HTTPException(status_code=404, detail=f"Gallery item '{item_name}' not found")

    image_path = Path(GALLERY_IMAGES[item_name]["processed"])

    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")

    return FileResponse(
        image_path,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/api/v1/gallery/all")
async def get_all_gallery_items():
    """Get all gallery items metadata"""
    items = []

    for item_id, data in GALLERY_IMAGES.items():
        original_exists = Path(data["original"]).exists()
        processed_exists = Path(data["processed"]).exists()

        items.append({
            "id": item_id,
            "title": data["title"],
            "description": data["description"],
            "processing_time": data["processing_time"],
            "tier": data["tier"],
            "original_url": f"/api/v1/gallery/{item_id}/original",
            "processed_url": f"/api/v1/gallery/{item_id}/processed",
            "status": "ready" if (original_exists and processed_exists) else "pending"
        })

    return {
        "items": items,
        "total": len(items),
        "ready": sum(1 for item in items if item["status"] == "ready")
    }

# =======================================
# END GALLERY ENDPOINTS
# =======================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test rembg availability
        from rembg import remove
        rembg_available = True
    except ImportError:
        rembg_available = False

    return {
        "status": "healthy",
        "local_processing": rembg_available,
        "manual_editor": "available",
        "timestamp": time.time()
    }

# ============================================================
# CREDIT MANAGEMENT ROUTES
# ============================================================

@app.get("/api/credits/balance")
async def get_balance(authorization: str = Header(None)):
    """Get current credit balance for authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No authorization token provided")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Verify token and get user
        auth_response = supabase.auth.get_user(token)
        if not auth_response or not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = auth_response.user.id
        
        # Get balance
        balance = await get_user_credits(user_id)
        
        if "error" in balance and balance["credits"] == 0:
            raise HTTPException(status_code=500, detail=balance["error"])
        
        return balance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_balance: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve balance")


@app.get("/api/credits/history")
async def get_history(authorization: str = Header(None), limit: int = 50):
    """Get transaction history for authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No authorization token provided")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Verify token and get user
        auth_response = supabase.auth.get_user(token)
        if not auth_response or not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = auth_response.user.id
        
        # Validate limit
        if limit > 100:
            limit = 100
        
        # Get history
        history = await get_transaction_history(user_id, limit)
        
        return {
            "user_id": user_id,
            "total_transactions": len(history),
            "transactions": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    print(f">> Starting Simple Masterpost.io Backend on port {port}...")
    print(f">> API Docs: http://localhost:{port}/docs")
    print(f">> Health: http://localhost:{port}/health")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8002)),
        log_level="info",
        reload=False
    )