from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional

from ..models.schemas import ProcessRequest, ProcessResponse, JobStatus, PipelineType
from ..database_sqlite.sqlite_client import sqlite_client
from ..processing.batch_handler import start_batch_processing
from .simple_auth import get_current_user_email

router = APIRouter()

@router.post("/process", response_model=ProcessResponse)
async def process_images(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    email: str = Depends(get_current_user_email)
):
    """Process images - SQLite version"""

    # Get job from SQLite
    job = sqlite_client.get_job(request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify user owns this job
    if job['email'] != email:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check job status
    if job.get("status") != "uploaded":
        raise HTTPException(
            status_code=400,
            detail=f"Job cannot be processed. Current status: {job.get('status')}"
        )

    # Validate pipeline
    if not request.pipeline:
        request.pipeline = PipelineType.AMAZON

    valid_pipelines = [p.value for p in PipelineType]
    if request.pipeline not in valid_pipelines:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pipeline. Available: {', '.join(valid_pipelines)}"
        )

    # Check credits (deduction happens AFTER successful processing in batch_handler)
    total_files = job['total_files']
    use_premium = request.settings.get("use_premium", False) if request.settings else False
    credits_needed = total_files * (3 if use_premium else 1)
    user_credits = sqlite_client.get_user_credits(email)
    if user_credits < credits_needed:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Need: {credits_needed}, Have: {user_credits}"
        )

    # Update job status
    sqlite_client.update_job(request.job_id, {
        "status": "processing",
        "pipeline": request.pipeline,
        "settings": request.settings or {}
    })

    # Start processing in background
    background_tasks.add_task(
        start_batch_processing,
        job_id=request.job_id,
        pipeline=request.pipeline,
        settings=request.settings
    )

    return ProcessResponse(
        job_id=request.job_id,
        message="Processing started",
        pipeline=request.pipeline,
        status="processing",
        estimated_time_minutes=total_files * 2
    )

@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status - SQLite version"""
    from pathlib import Path

    job = sqlite_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    total_files = job.get("total_files", 0)
    processed_files = job.get("processed_files", 0)

    # Get list of processed files if job is completed
    successful_files = []
    if job.get("status") == "completed":
        processed_dir = Path("processed") / job_id
        if processed_dir.exists():
            # Get all processed image files
            for img_file in processed_dir.glob("*"):
                if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    successful_files.append({
                        "success": True,
                        "original": img_file.name,
                        "processed": img_file.name,
                        "path": str(img_file.relative_to(Path("processed"))),
                        "shadow_applied": False,
                        "shadow_type": None
                    })

    return JobStatus(
        job_id=job.get("id"),
        status=job.get("status"),
        total_files=total_files,
        processed_files=processed_files,
        failed_files=job.get("failed_files", 0),
        progress_percentage=round(processed_files / total_files * 100, 2) if total_files > 0 else 0,
        created_at=job.get("created_at"),
        updated_at=job.get("updated_at"),
        pipeline=job.get("pipeline"),
        error_message=job.get("error_message") if "error_message" in job else None,
        successful_files=successful_files
    )

@router.get("/progress/{job_id}")
async def get_job_progress(job_id: str):
    """Get real-time job progress - returns current/total/percentage"""
    job = sqlite_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    total_files = job.get("total_files", 0)
    processed_files = job.get("processed_files", 0)

    return {
        "current": processed_files,
        "total": total_files,
        "percentage": round(processed_files / total_files * 100, 2) if total_files > 0 else 0,
        "status": job.get("status", "unknown")
    }

@router.get("/pipelines")
async def get_available_pipelines():
    return {
        "pipelines": [
            {
                "id": "amazon",
                "name": "Amazon Compliant",
                "description": "White background, 1000x1000px, 85% product coverage",
                "features": ["White background removal", "Square format", "Product centering", "Quality optimization"]
            },
            {
                "id": "instagram",
                "name": "Instagram Ready",
                "description": "1080x1080px square format with color enhancement",
                "features": ["Square crop", "Color boost", "Contrast enhancement", "Social media optimization"]
            },
            {
                "id": "ebay",
                "name": "eBay Optimized",
                "description": "1600x1600px high resolution for detailed product view",
                "features": ["High resolution", "Detail enhancement", "Multiple angle support", "Zoom optimization"]
            }
        ]
    }

@router.post("/process-test", response_model=ProcessResponse)
async def process_images_test(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """Testing endpoint without authentication for development"""
    job = memory_db.get_job(request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Skip user validation for testing

    if job.get("status") != "uploaded":
        raise HTTPException(
            status_code=400,
            detail=f"Job cannot be processed. Current status: {job.get('status')}"
        )

    valid_pipelines = ["amazon", "instagram", "ebay"]
    if request.pipeline not in valid_pipelines:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pipeline. Available: {', '.join(valid_pipelines)}"
        )

    memory_db.update_job(request.job_id, {
        "status": "processing",
        "pipeline": request.pipeline,
        "settings": request.settings
    })

    background_tasks.add_task(
        start_batch_processing,
        job_id=request.job_id,
        pipeline=request.pipeline,
        settings=request.settings
    )

    return ProcessResponse(
        job_id=request.job_id,
        message="Processing started",
        pipeline=request.pipeline,
        status="processing",
        estimated_time_minutes=job.get("total_files", 0) * 2  # 2 seconds per image estimate
    )

@router.get("/status-test/{job_id}", response_model=JobStatus)
async def get_job_status_test(
    job_id: str
):
    """Testing endpoint without authentication for development"""
    job = memory_db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Skip user validation for testing

    total_files = job.get("total_files", 0)
    processed_files = job.get("processed_files", 0)

    return JobStatus(
        job_id=job.get("job_id"),
        status=job.get("status"),
        total_files=total_files,
        processed_files=processed_files,
        failed_files=job.get("failed_files", 0),
        progress_percentage=round(processed_files / total_files * 100, 2) if total_files > 0 else 0,
        created_at=job.get("created_at"),
        updated_at=job.get("updated_at"),
        pipeline=job.get("pipeline"),
        error_message=job.get("error_message")
    )

@router.post("/cancel/{job_id}")
async def cancel_job(job_id: str, email: str = Depends(get_current_user_email)):
    """Cancel job - SQLite version"""
    job = sqlite_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify user owns this job
    if job.get("email") != email:
        raise HTTPException(status_code=403, detail="Access denied")

    if job.get("status") not in ["uploaded", "processing"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.get('status')}"
        )

    sqlite_client.update_job(job_id, {"status": "cancelled"})

    return {"message": "Job cancelled successfully", "job_id": job_id}