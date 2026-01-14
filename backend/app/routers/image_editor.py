"""
Image Editor API Routes
Provides endpoints for manual background removal touch-ups
"""

import logging
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ..models.schemas import EditorInitRequest, EditorInitResponse, BrushActionRequest, BrushActionResponse, EditorSaveRequest, EditorSaveResponse, EditorUndoRequest, EditorUndoResponse, EditorSessionInfo
from ..processing.manual_editor import ManualImageEditor

# Set up logging
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/v1/editor", tags=["image-editor"])

# Directories
PROCESSED_DIR = Path("processed")
PROCESSED_DIR.mkdir(exist_ok=True)

# Global editor instance
editor = ManualImageEditor(PROCESSED_DIR)

# Dependency to get editor instance
def get_editor() -> ManualImageEditor:
    """Get the editor instance"""
    return editor

@router.post("/init", response_model=EditorInitResponse)
async def init_editor_session(
    request: EditorInitRequest,
    editor: ManualImageEditor = Depends(get_editor)
) -> EditorInitResponse:
    """
    Initialize editing session for manual touch-ups

    Args:
        request: Editor initialization request

    Returns:
        EditorInitResponse: Session ID and initial preview URL
    """
    try:
        # Clean up expired sessions first
        editor.cleanup_expired_sessions()

        # Validate image path
        image_path = request.image_path
        if not Path(image_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Image not found: {image_path}"
            )

        # Initialize session
        session_id = editor.init_session(
            image_path=image_path,
            job_id=request.job_id
        )

        # Get session info
        session_info = editor.get_session_info(session_id)
        if not session_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to create editor session"
            )

        logger.info(f"Initialized editor session {session_id} for image {image_path}")

        return EditorInitResponse(
            session_id=session_id,
            preview_url=f"/api/v1/editor/preview/{session_id}",
            width=session_info['width'],
            height=session_info['height'],
            can_undo=session_info['can_undo'],
            can_redo=session_info['can_redo']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initialize editor session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize editor session: {str(e)}"
        )

@router.post("/brush-action", response_model=BrushActionResponse)
async def apply_brush_action(
    request: BrushActionRequest,
    editor: ManualImageEditor = Depends(get_editor)
) -> BrushActionResponse:
    """
    Apply brush action (erase or restore) to image

    Args:
        request: Brush action request

    Returns:
        BrushActionResponse: Updated preview URL and session state
    """
    try:
        # Validate session
        session_info = editor.get_session_info(request.session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        # Apply brush action
        preview_path = editor.apply_brush_action(
            session_id=request.session_id,
            action=request.action,
            coordinates=[(coord.x, coord.y) for coord in request.coordinates],
            brush_size=request.brush_size
        )

        if not preview_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to apply brush action"
            )

        # Get updated session info
        updated_session_info = editor.get_session_info(request.session_id)
        if not updated_session_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to get updated session info"
            )

        logger.info(f"Applied {request.action} brush action to session {request.session_id}")

        return BrushActionResponse(
            success=True,
            preview_url=f"/api/v1/editor/preview/{request.session_id}",
            can_undo=updated_session_info['can_undo'],
            can_redo=updated_session_info['can_redo']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply brush action: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply brush action: {str(e)}"
        )

@router.post("/undo", response_model=EditorUndoResponse)
async def undo_action(
    request: EditorUndoRequest,
    editor: ManualImageEditor = Depends(get_editor)
) -> EditorUndoResponse:
    """
    Undo last action

    Args:
        request: Undo request

    Returns:
        EditorUndoResponse: Updated preview URL and session state
    """
    try:
        # Validate session
        session_info = editor.get_session_info(request.session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        # Undo action
        preview_path = editor.undo(request.session_id)

        if not preview_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to undo action"
            )

        # Get updated session info
        updated_session_info = editor.get_session_info(request.session_id)
        if not updated_session_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to get updated session info"
            )

        logger.info(f"Undid action in session {request.session_id}")

        return EditorUndoResponse(
            success=True,
            preview_url=f"/api/v1/editor/preview/{request.session_id}",
            can_undo=updated_session_info['can_undo'],
            can_redo=updated_session_info['can_redo']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to undo action: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to undo action: {str(e)}"
        )

@router.post("/redo", response_model=EditorUndoResponse)
async def redo_action(
    request: EditorUndoRequest,
    editor: ManualImageEditor = Depends(get_editor)
) -> EditorUndoResponse:
    """
    Redo last undone action

    Args:
        request: Redo request

    Returns:
        EditorUndoResponse: Updated preview URL and session state
    """
    try:
        # Validate session
        session_info = editor.get_session_info(request.session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        # Redo action
        preview_path = editor.redo(request.session_id)

        if not preview_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to redo action"
            )

        # Get updated session info
        updated_session_info = editor.get_session_info(request.session_id)
        if not updated_session_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to get updated session info"
            )

        logger.info(f"Redid action in session {request.session_id}")

        return EditorUndoResponse(
            success=True,
            preview_url=f"/api/v1/editor/preview/{request.session_id}",
            can_undo=updated_session_info['can_undo'],
            can_redo=updated_session_info['can_redo']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to redo action: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to redo action: {str(e)}"
        )

@router.post("/reset", response_model=EditorUndoResponse)
async def reset_to_original(
    request: EditorUndoRequest,
    editor: ManualImageEditor = Depends(get_editor)
) -> EditorUndoResponse:
    """
    Reset image to original state

    Args:
        request: Reset request

    Returns:
        EditorUndoResponse: Reset preview URL and session state
    """
    try:
        # Validate session
        session_info = editor.get_session_info(request.session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        # Reset to original
        preview_path = editor.reset_to_original(request.session_id)

        if not preview_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to reset image"
            )

        # Get updated session info
        updated_session_info = editor.get_session_info(request.session_id)
        if not updated_session_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to get updated session info"
            )

        logger.info(f"Reset session {request.session_id} to original")

        return EditorUndoResponse(
            success=True,
            preview_url=f"/api/v1/editor/preview/{request.session_id}",
            can_undo=updated_session_info['can_undo'],
            can_redo=updated_session_info['can_redo']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset image: {str(e)}"
        )

@router.post("/save", response_model=EditorSaveResponse)
async def save_edited_image(
    request: EditorSaveRequest,
    editor: ManualImageEditor = Depends(get_editor)
) -> EditorSaveResponse:
    """
    Save edited image

    Args:
        request: Save request

    Returns:
        EditorSaveResponse: Saved image URL
    """
    try:
        # Validate session
        session_info = editor.get_session_info(request.session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        # Save edited image
        saved_path = editor.save_edited_image(
            session_id=request.session_id,
            output_path=request.output_path
        )

        if not saved_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to save edited image"
            )

        # Generate download URL
        saved_filename = Path(saved_path).name
        download_url = f"/api/v1/editor/download/{request.session_id}/{saved_filename}"

        logger.info(f"Saved edited image from session {request.session_id} to {saved_path}")

        return EditorSaveResponse(
            success=True,
            saved_path=saved_path,
            download_url=download_url
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save edited image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save edited image: {str(e)}"
        )

@router.get("/preview/{session_id}")
async def get_preview_image(
    session_id: str,
    editor: ManualImageEditor = Depends(get_editor)
):
    """
    Get preview image for session

    Args:
        session_id: Editor session ID

    Returns:
        FileResponse: Preview image file
    """
    try:
        # Validate session
        session_info = editor.get_session_info(session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        preview_path = session_info.get('preview_path')
        if not preview_path or not Path(preview_path).exists():
            raise HTTPException(
                status_code=404,
                detail="Preview image not found"
            )

        return FileResponse(
            preview_path,
            media_type="image/png",
            filename=f"preview_{session_id}.png"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get preview image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get preview image: {str(e)}"
        )

@router.get("/download/{session_id}/{filename}")
async def download_edited_image(
    session_id: str,
    filename: str,
    editor: ManualImageEditor = Depends(get_editor)
):
    """
    Download edited image

    Args:
        session_id: Editor session ID
        filename: Image filename

    Returns:
        FileResponse: Edited image file
    """
    try:
        # Validate session
        session_info = editor.get_session_info(session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        # Construct file path
        file_path = PROCESSED_DIR / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Edited image not found"
            )

        return FileResponse(
            file_path,
            media_type="image/png",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download edited image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download edited image: {str(e)}"
        )

@router.get("/session/{session_id}", response_model=EditorSessionInfo)
async def get_session_info(
    session_id: str,
    editor: ManualImageEditor = Depends(get_editor)
) -> EditorSessionInfo:
    """
    Get editor session information

    Args:
        session_id: Editor session ID

    Returns:
        EditorSessionInfo: Session details
    """
    try:
        session_info = editor.get_session_info(session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        return EditorSessionInfo(
            session_id=session_info['session_id'],
            image_path=session_info['image_path'],
            job_id=session_info.get('job_id'),
            width=session_info['width'],
            height=session_info['height'],
            created_at=session_info['created_at'],
            last_activity=session_info['last_activity'],
            can_undo=session_info['can_undo'],
            can_redo=session_info['can_redo'],
            preview_url=f"/api/v1/editor/preview/{session_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )

@router.delete("/session/{session_id}")
async def cleanup_session(
    session_id: str,
    editor: ManualImageEditor = Depends(get_editor)
):
    """
    Clean up editor session

    Args:
        session_id: Editor session ID

    Returns:
        dict: Success status
    """
    try:
        success = editor.cleanup_session(session_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Editor session not found"
            )

        logger.info(f"Cleaned up editor session {session_id}")

        return {"success": True, "message": "Session cleaned up successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cleanup session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup session: {str(e)}"
        )