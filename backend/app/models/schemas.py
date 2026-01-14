from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PipelineType(str, Enum):
    AMAZON = "amazon"
    INSTAGRAM = "instagram"
    EBAY = "ebay"

# Request Models
class UploadResponse(BaseModel):
    job_id: str
    message: str
    files_uploaded: int
    job_status: str

class ProcessRequest(BaseModel):
    job_id: str
    pipeline: Optional[PipelineType] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('settings')
    def validate_settings(cls, v):
        if v is None:
            return {}

        # Validate common settings
        allowed_keys = {
            'quality', 'size', 'padding_percent', 'remove_background',
            'saturation', 'contrast', 'brightness', 'sharpness',
            'apply_vignette', 'clean_background', 'reduce_noise',
            'use_premium', 'shadow_enabled', 'shadow_type', 'shadow_intensity',
            'shadow_angle', 'shadow_distance', 'shadow_blur', 'optimize_coverage'
        }

        for key in v.keys():
            if key not in allowed_keys:
                raise ValueError(f"Invalid setting: {key}")

        # Validate numeric ranges
        numeric_settings = {
            'quality': (50, 100),
            'padding_percent': (0, 50),
            'saturation': (0.5, 2.0),
            'contrast': (0.5, 2.0),
            'brightness': (0.5, 2.0),
            'sharpness': (0.5, 2.0)
        }

        for key, (min_val, max_val) in numeric_settings.items():
            if key in v:
                if not isinstance(v[key], (int, float)):
                    raise ValueError(f"{key} must be a number")
                if not min_val <= v[key] <= max_val:
                    raise ValueError(f"{key} must be between {min_val} and {max_val}")

        return v

class ProcessResponse(BaseModel):
    job_id: str
    message: str
    pipeline: str
    status: str
    estimated_time_minutes: int

class DownloadResponse(BaseModel):
    job_id: str
    status: str
    download_ready: bool
    files_count: int
    total_size_mb: float
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None

# Database Models
class FileInfo(BaseModel):
    file_id: str
    original_name: str
    saved_name: str
    size: Optional[int] = None
    path: str

class JobCreate(BaseModel):
    job_id: str
    user_id: str
    status: JobStatus = JobStatus.UPLOADED
    total_files: int
    files: List[FileInfo]
    pipeline: Optional[PipelineType] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    processed_files: Optional[int] = None
    failed_files: Optional[int] = None
    error_message: Optional[str] = None
    pipeline: Optional[PipelineType] = None
    settings: Optional[Dict[str, Any]] = None

class JobResponse(BaseModel):
    job_id: str
    user_id: str
    status: JobStatus
    total_files: int
    processed_files: Optional[int] = 0
    failed_files: Optional[int] = 0
    pipeline: Optional[PipelineType] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    files: Optional[List[FileInfo]] = Field(default_factory=list)

class ProcessedFileInfo(BaseModel):
    success: bool = True
    original: str
    processed: str
    path: str
    shadow_applied: bool = False
    shadow_type: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    status: JobStatus
    total_files: int
    processed_files: int
    failed_files: int
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    pipeline: Optional[PipelineType] = None
    error_message: Optional[str] = None
    successful_files: Optional[List[ProcessedFileInfo]] = Field(default_factory=list)

# User Models (for future authentication)
class UserCreate(BaseModel):
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Pipeline Info Models
class PipelineInfo(BaseModel):
    id: str
    name: str
    description: str
    target_size: tuple
    features: List[str]

class PipelineSettings(BaseModel):
    pipeline: PipelineType
    quality: int = Field(default=95, ge=50, le=100)
    custom_size: Optional[tuple] = None
    padding_percent: float = Field(default=5, ge=0, le=50)

    # Amazon specific
    remove_background: bool = True
    optimize_coverage: bool = True

    # Instagram specific
    saturation: float = Field(default=1.3, ge=0.5, le=2.0)
    apply_vignette: bool = False

    # eBay specific
    clean_background: bool = True
    reduce_noise: bool = True

    # Common enhancements
    contrast: float = Field(default=1.1, ge=0.5, le=2.0)
    brightness: float = Field(default=1.0, ge=0.5, le=2.0)
    sharpness: float = Field(default=1.1, ge=0.5, le=2.0)

# Analytics Models (for future features)
class JobAnalytics(BaseModel):
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_images_processed: int
    average_processing_time: float
    most_used_pipeline: str

class UserUsage(BaseModel):
    user_id: str
    total_jobs: int
    total_images: int
    current_month_usage: int
    plan_limit: int
    percentage_used: float

# Error Models
class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationErrorResponse(BaseModel):
    error: str = "validation_error"
    details: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Image Editor Models
class Coordinate(BaseModel):
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)

class EditorInitRequest(BaseModel):
    image_path: str = Field(..., description="Path to the processed image to edit")
    job_id: Optional[str] = Field(None, description="Optional job ID to associate with")

class EditorInitResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    preview_url: str = Field(..., description="URL to preview image")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    can_undo: bool = Field(default=False, description="Whether undo is available")
    can_redo: bool = Field(default=False, description="Whether redo is available")

class BrushActionRequest(BaseModel):
    session_id: str = Field(..., description="Editor session ID")
    action: str = Field(..., description="Action type: 'erase' or 'restore'")
    coordinates: List[Coordinate] = Field(..., description="Brush stroke coordinates")
    brush_size: int = Field(default=10, ge=1, le=100, description="Brush size in pixels")

    @validator('action')
    def validate_action(cls, v):
        if v not in ['erase', 'restore']:
            raise ValueError("Action must be 'erase' or 'restore'")
        return v

class BrushActionResponse(BaseModel):
    success: bool = Field(..., description="Whether action was successful")
    preview_url: str = Field(..., description="Updated preview URL")
    can_undo: bool = Field(..., description="Whether undo is available")
    can_redo: bool = Field(..., description="Whether redo is available")

class EditorUndoRequest(BaseModel):
    session_id: str = Field(..., description="Editor session ID")

class EditorUndoResponse(BaseModel):
    success: bool = Field(..., description="Whether operation was successful")
    preview_url: str = Field(..., description="Updated preview URL")
    can_undo: bool = Field(..., description="Whether undo is available")
    can_redo: bool = Field(..., description="Whether redo is available")

class EditorSaveRequest(BaseModel):
    session_id: str = Field(..., description="Editor session ID")
    output_path: Optional[str] = Field(None, description="Optional custom output path")

class EditorSaveResponse(BaseModel):
    success: bool = Field(..., description="Whether save was successful")
    saved_path: str = Field(..., description="Path where image was saved")
    download_url: str = Field(..., description="URL to download saved image")

class EditorSessionInfo(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    image_path: str = Field(..., description="Original image path")
    job_id: Optional[str] = Field(None, description="Associated job ID")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    created_at: float = Field(..., description="Session creation timestamp")
    last_activity: float = Field(..., description="Last activity timestamp")
    can_undo: bool = Field(..., description="Whether undo is available")
    can_redo: bool = Field(..., description="Whether redo is available")
    preview_url: str = Field(..., description="Preview image URL")