from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import zipfile
from pathlib import Path
import tempfile

from ..models.schemas import DownloadResponse
from ..database_sqlite.sqlite_client import sqlite_client
from .simple_auth import get_current_user_email

router = APIRouter()

PROCESSED_DIR = Path("processed")

@router.get("/processed/{job_id}/{filename}", response_class=FileResponse)
async def get_processed_image(job_id: str, filename: str):
    """Serve individual processed image for preview"""
    processed_file = PROCESSED_DIR / job_id / filename

    if not processed_file.exists():
        raise HTTPException(status_code=404, detail="Processed image not found")

    return FileResponse(
        path=processed_file,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=3600"
        }
    )

@router.get("/download/{job_id}", response_class=FileResponse)
async def download_processed_images(
    job_id: str
):
    job = sqlite_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Skip user validation for testing
    # if job.get("user_id") != user_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    if job.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not ready for download. Current status: {job.get('status')}"
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
                    arcname = f"{job.get('pipeline', 'processed')}_{image_file.name}"
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

@router.get("/download/info/{job_id}", response_model=DownloadResponse)
async def get_download_info(
    job_id: str
):
    job = sqlite_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Skip user validation for testing
    # if job.get("user_id") != user_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    processed_job_dir = PROCESSED_DIR / job_id
    job_status = job.get("status")

    if job_status == "completed" and processed_job_dir.exists():
        image_files = list(processed_job_dir.glob("*"))
        total_size = sum(f.stat().st_size for f in image_files if f.is_file())

        return DownloadResponse(
            job_id=job_id,
            status=job_status,
            download_ready=True,
            files_count=len(image_files),
            total_size_mb=round(total_size / (1024 * 1024), 2),
            download_url=f"/api/v1/download/{job_id}",
            expires_at=None  # TODO: Implement expiration
        )
    else:
        return DownloadResponse(
            job_id=job_id,
            status=job_status,
            download_ready=False,
            files_count=0,
            total_size_mb=0,
            download_url=None,
            expires_at=None
        )

@router.get("/download-test/{job_id}", response_class=FileResponse)
async def download_processed_images_test(
    job_id: str
):
    """Testing endpoint without authentication for development"""
    job = sqlite_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Skip user validation for testing

    if job.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not ready for download. Current status: {job.get('status')}"
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
                    arcname = f"{job.get('pipeline', 'processed')}_{image_file.name}"
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

@router.delete("/download/{job_id}")
async def cleanup_job_files(
    job_id: str
):
    job = sqlite_client.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Skip user validation for testing
    # if job.get("user_id") != user_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    upload_dir = Path("uploads") / job_id
    processed_dir = PROCESSED_DIR / job_id

    files_removed = 0

    if upload_dir.exists():
        import shutil
        shutil.rmtree(upload_dir)
        files_removed += 1

    if processed_dir.exists():
        import shutil
        shutil.rmtree(processed_dir)
        files_removed += 1

    return {
        "message": f"Cleaned up {files_removed} directories for job {job_id}",
        "job_id": job_id
    }

@router.get("/preview/{job_id}/{filename}")
async def get_preview_image(
    job_id: str,
    filename: str
):
    """Serve preview of processed image"""
    import os
    from fastapi.responses import FileResponse
    
    # Buscar el archivo en processed
    processed_path = f"/root/masterpost-saas/backend/processed/{job_id}/{filename}"
    
    if os.path.exists(processed_path):
        return FileResponse(
            processed_path,
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    else:
        raise HTTPException(status_code=404, detail="Image not found")
