"""
User models and plan management for MASTERPOST.IO V2.0
Hybrid architecture with usage tracking and cost control
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class ProcessingMethod(str, Enum):
    LOCAL = "local"  # rembg + local processing
    QWEN = "qwen"    # Qwen-Image-Edit API

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
    plan: PlanType = PlanType.FREE
    status: UserStatus = UserStatus.ACTIVE
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PlanFeatures(BaseModel):
    plan: PlanType
    max_images_per_month: int
    max_images_per_zip: int
    qwen_api_access: bool = False
    watermark_required: bool = True
    api_access: bool = False
    priority_processing: bool = False
    price_usd: float = 0.00
    description: str

class UserUsage(BaseModel):
    id: Optional[str] = None
    user_id: str
    year: int
    month: int
    images_processed: int = 0
    qwen_api_calls: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UsageCheck(BaseModel):
    can_process: bool
    remaining_images: int
    plan_limit: int
    current_usage: int
    plan: PlanType

class JobV2(BaseModel):
    id: Optional[str] = None
    user_id: str
    status: str = "uploaded"
    pipeline: str
    processing_method: ProcessingMethod = ProcessingMethod.LOCAL
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    is_zip_upload: bool = False
    original_filename: Optional[str] = None
    settings: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class JobFile(BaseModel):
    id: Optional[str] = None
    job_id: str
    original_name: str
    saved_name: str
    file_size: Optional[int] = None
    processing_status: str = "pending"
    processing_method: ProcessingMethod = ProcessingMethod.LOCAL
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ApiKey(BaseModel):
    id: Optional[str] = None
    user_id: str
    key_name: str
    api_key: str
    last_used_at: Optional[datetime] = None
    requests_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None

class BillingTransaction(BaseModel):
    id: Optional[str] = None
    user_id: str
    stripe_payment_intent_id: Optional[str] = None
    amount_usd: float
    plan: PlanType
    billing_period_start: date
    billing_period_end: date
    status: str = "pending"
    created_at: Optional[datetime] = None

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    plan: PlanType = PlanType.FREE

class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    plan: Optional[PlanType] = None
    status: Optional[UserStatus] = None

class UpgradeRequest(BaseModel):
    plan: PlanType
    stripe_payment_method_id: str

class ProcessingRequest(BaseModel):
    job_id: str
    pipeline: str
    settings: Optional[Dict[str, Any]] = {}
    force_method: Optional[ProcessingMethod] = None  # For testing/admin override

class ZipUploadRequest(BaseModel):
    files: List[str]  # List of file paths in extracted ZIP
    pipeline: str
    settings: Optional[Dict[str, Any]] = {}

# Plan configurations
PLAN_CONFIGS = {
    PlanType.FREE: PlanFeatures(
        plan=PlanType.FREE,
        max_images_per_month=10,
        max_images_per_zip=10,
        qwen_api_access=False,
        watermark_required=True,
        api_access=False,
        priority_processing=False,
        price_usd=0.00,
        description="Basic image processing with watermark"
    ),
    PlanType.PRO: PlanFeatures(
        plan=PlanType.PRO,
        max_images_per_month=500,
        max_images_per_zip=500,
        qwen_api_access=True,
        watermark_required=False,
        api_access=False,
        priority_processing=True,
        price_usd=49.00,
        description="Professional AI processing without watermark"
    ),
    PlanType.BUSINESS: PlanFeatures(
        plan=PlanType.BUSINESS,
        max_images_per_month=1500,
        max_images_per_zip=1500,
        qwen_api_access=True,
        watermark_required=False,
        api_access=True,
        priority_processing=True,
        price_usd=119.00,
        description="Enterprise features with API access"
    )
}

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    plan: PlanType
    status: UserStatus
    usage: Optional[UserUsage] = None
    plan_features: PlanFeatures
    created_at: datetime

class DashboardStats(BaseModel):
    user: UserResponse
    current_usage: UserUsage
    remaining_images: int
    jobs_this_month: int
    total_jobs: int
    success_rate: float
    next_billing_date: Optional[date] = None