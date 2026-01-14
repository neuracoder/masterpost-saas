"""
Manual Editor API Routes - Simplified
Provides simple endpoints for manual image editing
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/v1/manual-editor", tags=["manual-editor"])

# Directories
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
EDITED_DIR = TEMP_DIR / "edited"
EDITED_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

class UploadResponse(BaseModel):
    job_id: str
    file_path: str
    filename: str
    message: str

class SaveResponse(BaseModel):
    edited_id: str
    download_url: str
    message: str

def validate_image_file(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    if not file.filename:
        return False

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False

    # Check file size (max 50MB)
    if file.size and file.size > 50 * 1024 * 1024:
        return False

    return True

@router.post("/upload-single", response_model=UploadResponse)
async def upload_single_for_edit(file: UploadFile = File(...)):
    """
    Upload a single image for manual editing

    Args:
        file: Image file to upload

    Returns:
        UploadResponse: Job details and file path
    """
    try:
        # Validate file
        if not validate_image_file(file):
            raise HTTPException(
                status_code=400,
                detail="Invalid file. Please upload an image file (JPG, PNG, WEBP) under 50MB"
            )

        # Create unique job directory
        job_id = str(uuid.uuid4())
        job_dir = TEMP_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = job_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Uploaded file for manual editing: {file.filename} (Job: {job_id})")

        return UploadResponse(
            job_id=job_id,
            file_path=str(file_path),
            filename=file.filename,
            message="Image uploaded successfully for manual editing"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file for manual editing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )

@router.post("/save-edited", response_model=SaveResponse)
async def save_edited_image(
    edited_image: UploadFile = File(...),
    job_id: Optional[str] = Form(None)
):
    """
    Save manually edited image

    Args:
        edited_image: The edited image file
        job_id: Optional job ID for organization

    Returns:
        SaveResponse: Save confirmation and download URL
    """
    try:
        # Generate unique ID for edited image
        edited_id = str(uuid.uuid4())

        # Determine filename
        original_filename = edited_image.filename or "edited_image.png"
        file_extension = Path(original_filename).suffix or ".png"
        edited_filename = f"edited_{edited_id}{file_extension}"

        # Save edited image
        edited_path = EDITED_DIR / edited_filename

        with open(edited_path, "wb") as f:
            content = await edited_image.read()
            f.write(content)

        # Generate download URL
        download_url = f"/api/v1/manual-editor/download/{edited_filename}"

        logger.info(f"Saved edited image: {edited_filename} (Job: {job_id})")

        return SaveResponse(
            edited_id=edited_id,
            download_url=download_url,
            message="Edited image saved successfully"
        )

    except Exception as e:
        logger.error(f"Error saving edited image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save edited image: {str(e)}"
        )

@router.get("/download/{filename}")
async def download_edited_image(filename: str):
    """
    Download edited image

    Args:
        filename: Name of the edited image file

    Returns:
        FileResponse: The edited image file
    """
    try:
        file_path = EDITED_DIR / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Edited image not found"
            )

        # Determine media type based on file extension
        file_ext = file_path.suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        }

        media_type = media_type_map.get(file_ext, 'image/png')

        return FileResponse(
            file_path,
            media_type=media_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading edited image {filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download image: {str(e)}"
        )

@router.get("/temp/{job_id}/{filename}")
async def get_temp_image(job_id: str, filename: str):
    """
    Get temporary image file

    Args:
        job_id: Job ID
        filename: Image filename

    Returns:
        FileResponse: The temporary image file
    """
    try:
        file_path = TEMP_DIR / job_id / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Temporary image not found"
            )

        # Determine media type
        file_ext = file_path.suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        }

        media_type = media_type_map.get(file_ext, 'image/png')

        return FileResponse(
            file_path,
            media_type=media_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting temp image {job_id}/{filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get image: {str(e)}"
        )

@router.delete("/cleanup/{job_id}")
async def cleanup_temp_files(job_id: str):
    """
    Clean up temporary files for a job

    Args:
        job_id: Job ID to clean up

    Returns:
        dict: Cleanup status
    """
    try:
        job_dir = TEMP_DIR / job_id

        if job_dir.exists():
            # Remove all files in the job directory
            for file_path in job_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()

            # Remove the directory
            job_dir.rmdir()

            logger.info(f"Cleaned up temp files for job: {job_id}")

            return {
                "success": True,
                "message": f"Temporary files for job {job_id} cleaned up successfully"
            }
        else:
            return {
                "success": True,
                "message": f"No temporary files found for job {job_id}"
            }

    except Exception as e:
        logger.error(f"Error cleaning up temp files for job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup temp files: {str(e)}"
        )

@router.get("/test")
async def test_editor_backend():
    """Endpoint de prueba para verificar que el backend del editor funciona"""
    return {
        "message": "✅ Backend del editor funcionando correctamente",
        "service": "manual-editor",
        "endpoints_available": [
            "POST /api/v1/manual-editor/upload-single",
            "POST /api/v1/manual-editor/save-edited",
            "GET /api/v1/manual-editor/download/{filename}",
            "GET /api/v1/manual-editor/temp/{job_id}/{filename}",
            "DELETE /api/v1/manual-editor/cleanup/{job_id}",
            "GET /api/v1/manual-editor/test",
            "GET /api/v1/manual-editor/health"
        ],
        "directories": {
            "temp_dir": str(TEMP_DIR),
            "edited_dir": str(EDITED_DIR),
            "temp_dir_exists": TEMP_DIR.exists(),
            "edited_dir_exists": EDITED_DIR.exists()
        }
    }

@router.get("/health")
async def health_check():
    """Health check for manual editor service"""
    return {
        "status": "healthy",
        "service": "manual-editor",
        "temp_dir": str(TEMP_DIR),
        "edited_dir": str(EDITED_DIR),
        "temp_dir_exists": TEMP_DIR.exists(),
        "edited_dir_exists": EDITED_DIR.exists()
    }