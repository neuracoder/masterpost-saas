from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import os
import uuid
from pathlib import Path
import shutil
import tempfile
import zipfile

from ..models.schemas import UploadResponse, ProcessRequest, ProcessResponse, JobStatus
from ..database.supabase_client import supabase_client
from ..processing.batch_handler import start_batch_processing

router = APIRouter()

UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_image_file(file: UploadFile) -> bool:
    if not file.filename:
        return False
    file_ext = Path(file.filename).suffix.lower()
    return file_ext in ALLOWED_EXTENSIONS

@router.post("/upload-test", response_model=UploadResponse)
async def upload_images_test(
    files: List[UploadFile] = File(...)
):
    """Testing endpoint without authentication for development"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 files allowed")

    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []

    try:
        for file in files:
            if not validate_image_file(file):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                )

            if file.size and file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large: {file.filename}. Maximum size: 50MB"
                )

            file_id = str(uuid.uuid4())
            file_ext = Path(file.filename).suffix.lower()
            safe_filename = f"{file_id}{file_ext}"
            file_path = job_dir / safe_filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            uploaded_files.append({
                "file_id": file_id,
                "original_name": file.filename,
                "saved_name": safe_filename,
                "size": file.size,
                "path": str(file_path)
            })

    except Exception as e:
        if job_dir.exists():
            shutil.rmtree(job_dir)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Ensure test user exists
    test_user_id = "test_user"
    try:
        supabase_client.get_user_profile(test_user_id)
    except:
        # Create test user if doesn't exist
        from ...database.supabase_client import supabase
        supabase.table('user_profiles').upsert({
            'id': test_user_id,
            'email': 'test@masterpost.io',
            'full_name': 'Test User',
            'plan': 'free'
        }).execute()

    # Create job in Supabase for test user
    job = supabase_client.create_job(
        user_id=test_user_id,
        pipeline="test",
        total_files=len(uploaded_files),
        is_zip_upload=False,
        original_filename="test_upload"
    )

    # Create job files
    for file_info in uploaded_files:
        supabase_client.create_job_file(
            job_id=job["id"],
            original_name=file_info["original_name"],
            saved_name=file_info["saved_name"],
            file_size=file_info["size"],
            input_path=file_info["path"]
        )

    return UploadResponse(
        job_id=job["id"],
        message=f"Successfully uploaded {len(uploaded_files)} files",
        files_uploaded=len(uploaded_files),
        job_status="uploaded"
    )

@router.post("/process-test", response_model=ProcessResponse)
async def process_images_test(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """Testing endpoint without authentication for development"""
    job = supabase_client.get_job(request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "uploaded":
        raise HTTPException(
            status_code=400,
            detail=f"Job cannot be processed. Current status: {job['status']}"
        )

    valid_pipelines = ["amazon", "instagram", "ebay"]
    if request.pipeline not in valid_pipelines:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pipeline. Available: {', '.join(valid_pipelines)}"
        )

    supabase_client.update_job(request.job_id, {
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
        estimated_time_minutes=job["total_files"] * 2
    )

@router.get("/status-test/{job_id}", response_model=JobStatus)
async def get_job_status_test(
    job_id: str
):
    """Testing endpoint without authentication for development"""
    job = supabase_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    total_files = job["total_files"]
    processed_files = job["processed_files"]

    return JobStatus(
        job_id=job["id"],
        status=job["status"],
        total_files=total_files,
        processed_files=processed_files,
        failed_files=job["failed_files"],
        progress_percentage=round(processed_files / total_files * 100, 2) if total_files > 0 else 0,
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        pipeline=job["pipeline"],
        error_message=job.get("error_message")
    )

@router.get("/download-test/{job_id}", response_class=FileResponse)
async def download_processed_images_test(
    job_id: str
):
    """Testing endpoint without authentication for development"""
    job = supabase_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not ready for download. Current status: {job['status']}"
        )

    processed_job_dir = PROCESSED_DIR / job_id
    if not processed_job_dir.exists():
        raise HTTPException(status_code=404, detail="Processed files not found")

    image_files = list(processed_job_dir.glob("*"))
    if not image_files:
        raise HTTPException(status_code=404, detail="No processed files found")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_file in image_files:
                if image_file.is_file():
                    arcname = f"{job['pipeline']}_{image_file.name}"
                    zipf.write(image_file, arcname)

        zip_filename = f"masterpost_{job_id}_{job['pipeline']}.zip"

        return FileResponse(
            path=temp_zip.name,
            filename=zip_filename,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )