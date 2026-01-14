from fastapi import Form, APIRouter, File, UploadFile, HTTPException, Header, Depends
from typing import List, Optional
import os
import uuid
from pathlib import Path
import shutil
import zipfile
import logging

from ..models.schemas import UploadResponse, JobCreate, JobResponse
from ..database_sqlite.sqlite_client import sqlite_client
from .simple_auth import get_current_user_email

router = APIRouter()

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
ALLOWED_ZIP_EXTENSIONS = {".zip"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

logger = logging.getLogger(__name__)

def validate_image_file(file: UploadFile) -> bool:
    if not file.filename:
        return False

    file_ext = Path(file.filename).suffix.lower()
    return file_ext in ALLOWED_EXTENSIONS

def validate_file(file: UploadFile) -> bool:
    """Validate if file is either an image or ZIP"""
    if not file.filename:
        return False

    file_ext = Path(file.filename).suffix.lower()
    return file_ext in ALLOWED_EXTENSIONS or file_ext in ALLOWED_ZIP_EXTENSIONS

async def extract_zip_to_images(zip_file: UploadFile, job_dir: Path) -> List[dict]:
    """Extract images from ZIP file and save them to job directory"""
    extracted_files = []

    # Save ZIP temporarily
    temp_zip = job_dir / f"temp_{zip_file.filename}"

    try:
        # Write ZIP to temporary file
        with open(temp_zip, "wb") as buffer:
            shutil.copyfileobj(zip_file.file, buffer)

        logger.info(f"Processing ZIP: {zip_file.filename}")

        # Extract images from ZIP
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_files = zip_ref.filelist
            image_count = 0

            for file_info in zip_files:
                # Skip directories and hidden files
                if file_info.is_dir() or file_info.filename.startswith('.'):
                    continue

                file_ext = Path(file_info.filename).suffix.lower()
                if file_ext in IMAGE_EXTENSIONS:
                    # Extract to temporary location
                    zip_ref.extract(file_info, job_dir / "temp_extract")

                    # Generate new UUID filename
                    file_id = str(uuid.uuid4())
                    safe_filename = f"{file_id}{file_ext}"

                    # Move to final location with UUID name
                    original_path = job_dir / "temp_extract" / file_info.filename
                    final_path = job_dir / safe_filename

                    # Ensure parent directories exist
                    final_path.parent.mkdir(parents=True, exist_ok=True)
                    original_path.rename(final_path)

                    extracted_files.append({
                        "file_id": file_id,
                        "original_name": file_info.filename,
                        "saved_name": safe_filename,
                        "size": final_path.stat().st_size,
                        "path": str(final_path)
                    })

                    image_count += 1

                    # Limit to prevent abuse
                    if image_count >= 500:
                        logger.warning(f"ZIP contains more than 500 images, limiting to first 500")
                        break

        logger.info(f"ZIP processed: {zip_file.filename}, images extracted: {len(extracted_files)}")

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail=f"Invalid ZIP file: {zip_file.filename}")
    except Exception as e:
        logger.error(f"Error processing ZIP {zip_file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process ZIP: {str(e)}")
    finally:
        # Clean up temporary files
        if temp_zip.exists():
            temp_zip.unlink()
        temp_extract_dir = job_dir / "temp_extract"
        if temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir)

    return extracted_files

@router.post("/upload", response_model=UploadResponse)
async def upload_images(
    files: List[UploadFile] = File(...),
    use_premium: bool = Form(False),
    email: str = Depends(get_current_user_email)
):
    """Upload images for processing - SQLite version"""

    # Determine processing type based on user selection
    processing_type = "qwen" if use_premium else "rembg"
    logger.info(f"Processing type: {processing_type} (premium={use_premium}) for user: {email}")

    # Validate credits BEFORE uploading
    credits_needed = len(files) * (3 if use_premium else 1)
    user_credits = sqlite_client.get_user_credits(email)

    if user_credits < credits_needed:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Need: {credits_needed}, Have: {user_credits}"
        )

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 files allowed")

    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []
    is_zip_upload = False

    try:
        for file in files:
            if not validate_file(file):
                allowed_types = list(ALLOWED_EXTENSIONS) + list(ALLOWED_ZIP_EXTENSIONS)
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}. Allowed: {', '.join(allowed_types)}"
                )

            if file.size and file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large: {file.filename}. Maximum size: 50MB"
                )

            file_ext = Path(file.filename).suffix.lower()

            # Handle ZIP files
            if file_ext in ALLOWED_ZIP_EXTENSIONS:
                logger.info(f"Processing ZIP file: {file.filename}")
                zip_files = await extract_zip_to_images(file, job_dir)
                uploaded_files.extend(zip_files)
                is_zip_upload = True

                if len(uploaded_files) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No valid images found in ZIP: {file.filename}"
                    )

            # Handle regular image files
            else:
                file_id = str(uuid.uuid4())
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

        # Check total file limit after processing all files
        if len(uploaded_files) > 500:
            raise HTTPException(
                status_code=400,
                detail=f"Too many files: {len(uploaded_files)}. Maximum 500 files allowed"
            )

    except Exception as e:
        if job_dir.exists():
            shutil.rmtree(job_dir)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Create job in SQLite
    job_data = {
        'id': job_id,
        'email': email,
        'status': 'uploaded',
        'pipeline': 'pending',
        'total_files': len(uploaded_files),
        'settings': {
            'use_premium': use_premium,
            'is_zip_upload': is_zip_upload,
            'files': uploaded_files
        }
    }

    job_created = sqlite_client.create_job(job_data)

    if not job_created:
        # Clean up uploaded files if job creation fails
        if job_dir.exists():
            shutil.rmtree(job_dir)
        raise HTTPException(status_code=500, detail="Failed to create job")

    logger.info(f"Job {job_id} created for {email} with {len(uploaded_files)} files")

    return UploadResponse(
        job_id=job_id,
        message=f"Successfully uploaded {len(uploaded_files)} files",
        files_uploaded=len(uploaded_files),
        job_status="uploaded"
    )


@router.get("/upload/status")
async def get_upload_limits():
    return {
        "max_files": 500,
        "max_file_size_mb": 50,
        "allowed_image_formats": list(ALLOWED_EXTENSIONS),
        "allowed_archive_formats": list(ALLOWED_ZIP_EXTENSIONS),
        "all_allowed_formats": list(ALLOWED_EXTENSIONS) + list(ALLOWED_ZIP_EXTENSIONS),
        "upload_directory": str(UPLOAD_DIR),
        "zip_support": True,
        "zip_max_images": 500
    }
