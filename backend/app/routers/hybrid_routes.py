"""
Hybrid processing routes for MASTERPOST.IO V2.0
Integrates usage tracking, plan-based processing, and ZIP support
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import uuid
from pathlib import Path
import shutil
import tempfile
import asyncio
import json

from ..models.schemas import UploadResponse, ProcessRequest, ProcessResponse, JobStatus
from ..models.user_models import PlanType, ProcessingMethod, User
from ..database.supabase_client import supabase_client
from ..services.processing_service import processing_service
from ..services.usage_service import usage_service
from ..services.zip_service import zip_service
from ..auth.supabase_auth import get_current_user, get_current_user_optional

router = APIRouter()

UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
ALLOWED_ARCHIVES = {".zip", ".rar", ".7z"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB for hybrid system

def validate_file(file: UploadFile) -> dict:
    """Validate uploaded file and determine type"""
    if not file.filename:
        return {"valid": False, "error": "No filename provided"}

    file_ext = Path(file.filename).suffix.lower()
    file_type = None

    if file_ext in ALLOWED_EXTENSIONS:
        file_type = "image"
    elif file_ext in ALLOWED_ARCHIVES:
        file_type = "archive"
    else:
        return {
            "valid": False,
            "error": f"Unsupported file type: {file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS | ALLOWED_ARCHIVES)}"
        }

    if file.size and file.size > MAX_FILE_SIZE:
        size_mb = file.size / (1024 * 1024)
        return {
            "valid": False,
            "error": f"File too large: {size_mb:.1f}MB. Maximum: 100MB"
        }

    return {"valid": True, "type": file_type, "extension": file_ext}

@router.post("/upload-hybrid", response_model=UploadResponse)
async def upload_hybrid(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload endpoint that supports both images and archives
    Includes usage limit checking
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 100:  # Reasonable limit for mixed uploads
        raise HTTPException(status_code=400, detail="Maximum 100 files allowed per upload")

    # User is already authenticated via dependency
    user_id = current_user.id

    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []
    total_images_estimate = 0

    try:
        for file in files:
            validation = validate_file(file)
            if not validation["valid"]:
                raise HTTPException(status_code=400, detail=validation["error"])

            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}{validation['extension']}"
            file_path = job_dir / safe_filename

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            file_info = {
                "file_id": file_id,
                "original_name": file.filename,
                "saved_name": safe_filename,
                "size": file.size,
                "path": str(file_path),
                "type": validation["type"]
            }

            # For archives, validate and get image count
            if validation["type"] == "archive":
                archive_validation = await zip_service.validate_archive(str(file_path), user_id)
                if not archive_validation["valid"]:
                    raise HTTPException(status_code=400, detail=archive_validation["error"])

                file_info["archive_info"] = archive_validation
                total_images_estimate += archive_validation.get("image_count", 0)
            else:
                total_images_estimate += 1

            uploaded_files.append(file_info)

        # Check if user can process estimated total images
        usage_check = await usage_service.check_usage_limits(user_id, total_images_estimate)
        if not usage_check.can_process:
            # Cleanup uploaded files
            if job_dir.exists():
                shutil.rmtree(job_dir)
            raise HTTPException(
                status_code=400,
                detail=f"Cannot process {total_images_estimate} images. You have {usage_check.remaining_images} images remaining this month."
            )

        # Create job with hybrid info
        job_data = {
            "job_id": job_id,
            "user_id": user_id,
            "user_plan": current_user.plan,
            "status": "uploaded",
            "total_files": len(uploaded_files),
            "estimated_images": total_images_estimate,
            "files": uploaded_files,
            "has_archives": any(f["type"] == "archive" for f in uploaded_files),
            "usage_check": usage_check.dict()
        }

        job = await supabase_client.create_job(job_data)

        return UploadResponse(
            job_id=job_id,
            message=f"Successfully uploaded {len(uploaded_files)} files (estimated {total_images_estimate} images)",
            files_uploaded=len(uploaded_files),
            job_status="uploaded"
        )

    except Exception as e:
        if job_dir.exists():
            shutil.rmtree(job_dir)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/process-hybrid", response_model=ProcessResponse)
async def process_hybrid(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Process images using hybrid system with plan-based routing
    """
    job = await supabase_client.get_job(request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify job belongs to current user
    if job.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if job.get("status") != "uploaded":
        raise HTTPException(
            status_code=400,
            detail=f"Job cannot be processed. Current status: {job.get('status')}"
        )

    # Validate pipeline
    valid_pipelines = ["amazon", "instagram", "ebay"]
    if request.pipeline not in valid_pipelines:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pipeline. Available: {', '.join(valid_pipelines)}"
        )

    # Get user plan
    user_plan = current_user.plan

    # Final usage check
    estimated_images = job.get("estimated_images", 0)
    usage_check = await usage_service.check_usage_limits(job.get("user_id"), estimated_images)
    if not usage_check.can_process:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot process {estimated_images} images. Monthly limit exceeded."
        )

    # Get processing info for user's plan
    processing_info = await processing_service.get_processing_info(user_plan)

    # Update job status
    await supabase_client.update_job(request.job_id, {
        "status": "processing",
        "pipeline": request.pipeline,
        "settings": request.settings,
        "processing_method": processing_info["processing_method"],
        "processing_info": processing_info
    })

    # Start background processing
    background_tasks.add_task(
        start_hybrid_processing,
        job_id=request.job_id,
        user_plan=user_plan,
        pipeline=request.pipeline,
        settings=request.settings
    )

    # Estimate processing time based on plan and method
    time_per_image = 1.0 if processing_info["processing_method"] == "qwen" else 2.0
    estimated_minutes = max(1, estimated_images * time_per_image / 60)

    return ProcessResponse(
        job_id=request.job_id,
        message=f"Processing started with {processing_info['processing_method']} method",
        pipeline=request.pipeline,
        status="processing",
        estimated_time_minutes=round(estimated_minutes, 1)
    )

async def start_hybrid_processing(
    job_id: str,
    user_plan: PlanType,
    pipeline: str,
    settings: dict
):
    """
    Background task for hybrid processing
    """
    try:
        job = await supabase_client.get_job(job_id)
        if not job:
            return

        user_id = job.get("user_id")
        files = job.get("files", [])
        has_archives = job.get("has_archives", False)

        # Create processing directory
        processed_dir = PROCESSED_DIR / job_id
        processed_dir.mkdir(parents=True, exist_ok=True)

        all_results = []
        total_processed = 0
        total_failed = 0

        # Progress callback
        async def progress_callback(status: str, current: int, total: int, message: str):
            progress = round((current / total * 100), 2) if total > 0 else 0
            await supabase_client.update_job(job_id, {
                "processed_files": current,
                "progress_percentage": progress,
                "current_message": message
            })

        # Process each uploaded file
        for file_info in files:
            file_path = file_info["path"]

            if file_info["type"] == "archive":
                # Process archive
                archive_results = await zip_service.extract_and_process(
                    archive_path=file_path,
                    user_id=user_id,
                    user_plan=user_plan,
                    pipeline=pipeline,
                    job_id=f"{job_id}_{file_info['file_id']}",
                    progress_callback=progress_callback
                )

                if archive_results.get("success"):
                    total_processed += archive_results.get("processed_files", 0)
                    total_failed += archive_results.get("failed_files", 0)

                all_results.append(archive_results)

            else:
                # Process single image
                output_path = processed_dir / f"{Path(file_path).stem}_processed.png"

                result = await processing_service.process_single_image(
                    image_path=file_path,
                    output_path=str(output_path),
                    user_plan=user_plan
                )

                if result.get("success"):
                    total_processed += 1
                else:
                    total_failed += 1

                all_results.append(result)

        # Update usage tracking
        if total_processed > 0:
            processing_method = all_results[0].get("method", "local")
            await usage_service.update_usage(
                user_id=user_id,
                images_processed=total_processed,
                processing_method=ProcessingMethod(processing_method)
            )

        # Determine final status
        if total_processed == 0:
            final_status = "failed"
        elif total_failed > 0:
            final_status = "completed_with_errors"
        else:
            final_status = "completed"

        # Update job with final results
        await supabase_client.update_job(job_id, {
            "status": final_status,
            "processed_files": total_processed,
            "failed_files": total_failed,
            "progress_percentage": 100,
            "processing_results": [r for r in all_results if isinstance(r, dict)],
            "completed_at": str(asyncio.get_event_loop().time())
        })

    except Exception as e:
        await supabase_client.update_job(job_id, {
            "status": "failed",
            "error_message": str(e)
        })

@router.get("/status-hybrid/{job_id}")
async def get_hybrid_status(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Get job status with hybrid processing information
    """
    job = await supabase_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify job belongs to current user
    if job.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get processing info if available
    processing_info = job.get("processing_info", {})

    # Calculate progress
    total_files = job.get("estimated_images", job.get("total_files", 0))
    processed_files = job.get("processed_files", 0)
    progress = round(processed_files / total_files * 100, 2) if total_files > 0 else 0

    return {
        "job_id": job_id,
        "status": job.get("status"),
        "user_plan": job.get("user_plan"),
        "processing_method": processing_info.get("processing_method", "local"),
        "total_files": job.get("total_files", 0),
        "estimated_images": total_files,
        "processed_files": processed_files,
        "failed_files": job.get("failed_files", 0),
        "progress_percentage": progress,
        "pipeline": job.get("pipeline"),
        "has_archives": job.get("has_archives", False),
        "current_message": job.get("current_message", ""),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
        "processing_info": processing_info,
        "error_message": job.get("error_message")
    }

@router.get("/download-hybrid/{job_id}", response_class=FileResponse)
async def download_hybrid(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Download processed images as ZIP
    """
    job = await supabase_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify job belongs to current user
    if job.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if job.get("status") not in ["completed", "completed_with_errors"]:
        raise HTTPException(
            status_code=400,
            detail=f"Job not ready for download. Current status: {job.get('status')}"
        )

    processed_dir = PROCESSED_DIR / job_id
    if not processed_dir.exists():
        raise HTTPException(status_code=404, detail="Processed files not found")

    # Find all processed images
    image_files = []
    for ext in [".png", ".jpg", ".jpeg"]:
        image_files.extend(processed_dir.glob(f"*{ext}"))

    if not image_files:
        raise HTTPException(status_code=404, detail="No processed files found")

    # Create ZIP file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
        import zipfile
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_file in image_files:
                if image_file.is_file():
                    # Use descriptive names
                    pipeline = job.get("pipeline", "processed")
                    user_plan = job.get("user_plan", "free")
                    arcname = f"masterpost_{pipeline}_{user_plan}_{image_file.name}"
                    zipf.write(image_file, arcname)

        zip_filename = f"masterpost_{job_id}_{job.get('pipeline', 'processed')}.zip"

        return FileResponse(
            path=temp_zip.name,
            filename=zip_filename,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )

@router.get("/usage")
async def get_user_usage(current_user: User = Depends(get_current_user)):
    """
    Get user usage information and plan limits
    """
    try:
        usage_summary = await usage_service.get_plan_usage_summary(current_user.id)
        if not usage_summary:
            raise HTTPException(status_code=404, detail="User usage not found")

        return usage_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage: {str(e)}")

@router.get("/processing-info")
async def get_processing_info(current_user: User = Depends(get_current_user)):
    """
    Get processing capabilities for user's plan
    """
    try:
        processing_info = await processing_service.get_processing_info(current_user.plan)
        return processing_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get processing info: {str(e)}")