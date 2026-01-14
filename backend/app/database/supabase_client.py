"""
Supabase database client for MASTERPOST.IO V2.0
Replaces memory_client with production-ready PostgreSQL database
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
import uuid
from supabase import create_client, Client
from postgrest.exceptions import APIError

from ..core.config import settings
from ..models.user_models import (
    User, UserUsage, UsageCheck, PlanType,
    JobV2, JobFile, ApiKey, BillingTransaction,
    ProcessingMethod, UserStatus, PLAN_CONFIGS
)

logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Production database client using Supabase PostgreSQL
    """

    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY  # Use service role key for server-side operations
        )
        self._test_connection()

    def _test_connection(self):
        """Test database connection on initialization"""
        try:
            # Test connection with a simple query
            result = self.supabase.table('plan_features').select('plan').limit(1).execute()
            logger.info("Supabase connection established successfully")
        except Exception as e:
            logger.warning(f"Supabase connection test failed (cache issue): {str(e)}")
            # Don't raise - let the app start anyway, Supabase cache will refresh

    # =====================================================
    # USER MANAGEMENT
    # =====================================================

    async def get_user_profile(self, user_id: str) -> Optional[User]:
        """Get user profile by ID"""
        try:
            result = self.supabase.table('user_profiles').select('*').eq('id', user_id).single().execute()

            if result.data:
                return User(
                    id=result.data['id'],
                    email=result.data['email'],
                    full_name=result.data['full_name'],
                    plan=PlanType(result.data['plan']),
                    status=UserStatus(result.data['status']),
                    stripe_customer_id=result.data['stripe_customer_id'],
                    stripe_subscription_id=result.data['stripe_subscription_id'],
                    created_at=datetime.fromisoformat(result.data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(result.data['updated_at'].replace('Z', '+00:00'))
                )
            return None
        except APIError as e:
            logger.error(f"Error getting user profile {user_id}: {str(e)}")
            return None

    async def create_user_profile(self, user_data: Dict[str, Any]) -> Optional[User]:
        """Create new user profile"""
        try:
            result = self.supabase.table('user_profiles').insert(user_data).execute()

            if result.data:
                data = result.data[0]
                return User(
                    id=data['id'],
                    email=data['email'],
                    full_name=data['full_name'],
                    plan=PlanType(data['plan']),
                    status=UserStatus(data['status']),
                    created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
                )
            return None
        except APIError as e:
            logger.error(f"Error creating user profile: {str(e)}")
            return None

    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.supabase.table('user_profiles').update(updates).eq('id', user_id).execute()
            return len(result.data) > 0
        except APIError as e:
            logger.error(f"Error updating user profile {user_id}: {str(e)}")
            return False

    # =====================================================
    # USAGE TRACKING
    # =====================================================

    async def get_current_usage(self, user_id: str) -> UserUsage:
        """Get current month usage for user"""
        try:
            now = datetime.utcnow()
            year = now.year
            month = now.month

            result = self.supabase.table('user_usage')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('year', year)\
                .eq('month', month)\
                .single().execute()

            if result.data:
                data = result.data
                return UserUsage(
                    id=data['id'],
                    user_id=data['user_id'],
                    year=data['year'],
                    month=data['month'],
                    images_processed=data['images_processed'],
                    qwen_api_calls=data['qwen_api_calls'],
                    created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
                )
            else:
                # Create new usage record if none exists
                new_usage = UserUsage(
                    user_id=user_id,
                    year=year,
                    month=month,
                    images_processed=0,
                    qwen_api_calls=0
                )
                await self.create_usage_record(new_usage)
                return new_usage

        except APIError as e:
            logger.error(f"Error getting usage for user {user_id}: {str(e)}")
            # Return default usage
            return UserUsage(
                user_id=user_id,
                year=datetime.utcnow().year,
                month=datetime.utcnow().month,
                images_processed=0,
                qwen_api_calls=0
            )

    async def create_usage_record(self, usage: UserUsage) -> bool:
        """Create new usage record"""
        try:
            usage_data = {
                'user_id': usage.user_id,
                'year': usage.year,
                'month': usage.month,
                'images_processed': usage.images_processed,
                'qwen_api_calls': usage.qwen_api_calls
            }

            result = self.supabase.table('user_usage').insert(usage_data).execute()
            return len(result.data) > 0
        except APIError as e:
            logger.error(f"Error creating usage record: {str(e)}")
            return False

    async def update_usage(self, user_id: str, images_count: int = 0, qwen_calls: int = 0, job_success: bool = True) -> bool:
        """Update user usage using database function"""
        try:
            result = self.supabase.rpc(
                'update_user_usage',
                {
                    'p_user_id': user_id,
                    'p_images_count': images_count,
                    'p_qwen_calls': qwen_calls,
                    'p_job_success': job_success
                }
            ).execute()

            return True
        except APIError as e:
            logger.error(f"Error updating usage for user {user_id}: {str(e)}")
            return False

    async def check_usage_limits(self, user_id: str, images_count: int = 1) -> UsageCheck:
        """Check usage limits using database function"""
        try:
            result = self.supabase.rpc(
                'check_usage_limit',
                {
                    'p_user_id': user_id,
                    'p_images_count': images_count
                }
            ).execute()

            if result.data:
                data = result.data[0]
                return UsageCheck(
                    can_process=data['can_process'],
                    remaining_images=data['remaining_images'],
                    plan_limit=data['plan_limit'],
                    current_usage=data['current_usage'],
                    plan=PlanType(data['user_plan'])
                )
            else:
                # Fallback to default
                return UsageCheck(
                    can_process=False,
                    remaining_images=0,
                    plan_limit=10,
                    current_usage=0,
                    plan=PlanType.FREE
                )

        except APIError as e:
            logger.error(f"Error checking usage limits for user {user_id}: {str(e)}")
            return UsageCheck(
                can_process=images_count <= 10,  # Safe default
                remaining_images=10,
                plan_limit=10,
                current_usage=0,
                plan=PlanType.FREE
            )

    # =====================================================
    # JOB MANAGEMENT
    # =====================================================

    async def create_job(self, job_data: Dict[str, Any]) -> Optional[JobV2]:
        """Create new processing job"""
        try:
            # Convert job_data to match database schema
            db_job_data = {
                'user_id': job_data['user_id'],
                'status': job_data.get('status', 'uploaded'),
                'pipeline': job_data.get('pipeline', 'amazon'),
                'processing_method': job_data.get('processing_method', 'local'),
                'total_files': job_data.get('total_files', 0),
                'is_zip_upload': job_data.get('is_zip_upload', False),
                'original_filename': job_data.get('original_filename'),
                'settings': job_data.get('settings', {}),
                'metadata': job_data.get('metadata', {})
            }

            result = self.supabase.table('jobs').insert(db_job_data).execute()

            if result.data:
                data = result.data[0]
                job = JobV2(
                    id=data['id'],
                    user_id=data['user_id'],
                    status=data['status'],
                    pipeline=data['pipeline'],
                    processing_method=ProcessingMethod(data['processing_method']),
                    total_files=data['total_files'],
                    processed_files=data['processed_files'],
                    failed_files=data['failed_files'],
                    is_zip_upload=data['is_zip_upload'],
                    original_filename=data['original_filename'],
                    settings=data['settings'],
                    created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
                )

                # Create job files if provided
                files = job_data.get('files', [])
                if files:
                    await self.create_job_files(data['id'], files)

                return job

            return None

        except APIError as e:
            logger.error(f"Error creating job: {str(e)}")
            return None

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID with files"""
        try:
            # Get job data
            job_result = self.supabase.table('jobs').select('*').eq('id', job_id).single().execute()

            if not job_result.data:
                return None

            job_data = job_result.data

            # Get job files
            files_result = self.supabase.table('job_files').select('*').eq('job_id', job_id).execute()

            # Convert to format expected by existing code
            job = {
                'job_id': job_data['id'],
                'user_id': job_data['user_id'],
                'status': job_data['status'],
                'pipeline': job_data.get('pipeline'),
                'processing_method': job_data['processing_method'],
                'total_files': job_data['total_files'],
                'processed_files': job_data['processed_files'],
                'failed_files': job_data['failed_files'],
                'is_zip_upload': job_data['is_zip_upload'],
                'original_filename': job_data['original_filename'],
                'settings': job_data['settings'],
                'error_message': job_data['error_message'],
                'created_at': job_data['created_at'],
                'updated_at': job_data['updated_at'],
                'files': []
            }

            # Add files data
            if files_result.data:
                for file_data in files_result.data:
                    job['files'].append({
                        'file_id': file_data['id'],
                        'original_name': file_data['original_name'],
                        'saved_name': file_data['saved_name'],
                        'size': file_data['file_size'],
                        'path': file_data['input_path'],
                        'processing_status': file_data['processing_status'],
                        'error_message': file_data['error_message']
                    })

            return job

        except APIError as e:
            logger.error(f"Error getting job {job_id}: {str(e)}")
            return None

    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job with new data"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.supabase.table('jobs').update(updates).eq('id', job_id).execute()
            return len(result.data) > 0
        except APIError as e:
            logger.error(f"Error updating job {job_id}: {str(e)}")
            return False

    async def create_job_files(self, job_id: str, files_data: List[Dict[str, Any]]) -> bool:
        """Create job files records"""
        try:
            db_files = []
            for file_data in files_data:
                db_file = {
                    'job_id': job_id,
                    'original_name': file_data['original_name'],
                    'saved_name': file_data['saved_name'],
                    'file_size': file_data.get('size'),
                    'input_path': file_data.get('path'),
                    'metadata': file_data
                }
                db_files.append(db_file)

            result = self.supabase.table('job_files').insert(db_files).execute()
            return len(result.data) > 0

        except APIError as e:
            logger.error(f"Error creating job files for job {job_id}: {str(e)}")
            return False

    async def get_user_jobs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's jobs ordered by creation date"""
        try:
            result = self.supabase.table('jobs')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()

            jobs = []
            for job_data in result.data:
                jobs.append({
                    'job_id': job_data['id'],
                    'status': job_data['status'],
                    'pipeline': job_data['pipeline'],
                    'total_files': job_data['total_files'],
                    'processed_files': job_data['processed_files'],
                    'failed_files': job_data['failed_files'],
                    'created_at': job_data['created_at'],
                    'updated_at': job_data['updated_at']
                })

            return jobs

        except APIError as e:
            logger.error(f"Error getting jobs for user {user_id}: {str(e)}")
            return []

    # =====================================================
    # API KEY MANAGEMENT
    # =====================================================

    async def create_api_key(self, user_id: str, key_name: str) -> Optional[str]:
        """Create new API key for user"""
        try:
            result = self.supabase.rpc(
                'generate_api_key',
                {
                    'p_user_id': user_id,
                    'p_key_name': key_name
                }
            ).execute()

            if result.data:
                return result.data  # Returns the generated API key
            return None

        except APIError as e:
            logger.error(f"Error creating API key for user {user_id}: {str(e)}")
            return None

    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user info"""
        try:
            result = self.supabase.rpc(
                'validate_api_key',
                {'api_key_param': api_key}
            ).execute()

            if result.data:
                data = result.data[0]
                # Log usage
                await self.log_api_key_usage(api_key)
                return data
            return None

        except APIError as e:
            logger.error(f"Error validating API key: {str(e)}")
            return None

    async def log_api_key_usage(self, api_key: str) -> bool:
        """Log API key usage"""
        try:
            self.supabase.rpc(
                'log_api_key_usage',
                {'api_key_param': api_key}
            ).execute()
            return True
        except APIError as e:
            logger.error(f"Error logging API key usage: {str(e)}")
            return False

    # =====================================================
    # DASHBOARD AND ANALYTICS
    # =====================================================

    async def get_user_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        try:
            result = self.supabase.rpc(
                'get_user_dashboard_stats',
                {'user_id_param': user_id}
            ).execute()

            if result.data:
                data = result.data[0]
                return {
                    'user_id': user_id,
                    'plan': data['current_plan'],
                    'plan_features': PLAN_CONFIGS.get(PlanType(data['current_plan'])),
                    'current_usage': {
                        'images_processed': data['images_processed_this_month'],
                        'qwen_api_calls': data['qwen_api_calls_this_month'],
                        'remaining_images': data['images_remaining_this_month'],
                        'usage_percentage': round(
                            (data['images_processed_this_month'] /
                             PLAN_CONFIGS[PlanType(data['current_plan'])].max_images_per_month * 100), 1
                        ) if data['images_processed_this_month'] > 0 else 0
                    },
                    'jobs_stats': {
                        'total_jobs': data['total_jobs'],
                        'jobs_this_month': data['jobs_this_month'],
                        'successful_jobs': data['successful_jobs_this_month'],
                        'success_rate': float(data['success_rate'])
                    },
                    'month_year': f"{datetime.utcnow().month}/{datetime.utcnow().year}"
                }
            return {}

        except APIError as e:
            logger.error(f"Error getting dashboard stats for user {user_id}: {str(e)}")
            return {}

    # =====================================================
    # PLAN MANAGEMENT
    # =====================================================

    async def get_plan_features(self, plan: PlanType) -> Optional[Dict[str, Any]]:
        """Get plan features from database"""
        try:
            result = self.supabase.table('plan_features').select('*').eq('plan', plan.value).single().execute()

            if result.data:
                return result.data
            return None

        except APIError as e:
            logger.error(f"Error getting plan features for {plan}: {str(e)}")
            return None

    async def get_all_plan_features(self) -> List[Dict[str, Any]]:
        """Get all available plans"""
        try:
            result = self.supabase.table('plan_features').select('*').order('price_usd').execute()
            return result.data
        except APIError as e:
            logger.error(f"Error getting all plan features: {str(e)}")
            return []

    # =====================================================
    # CLEANUP AND MAINTENANCE
    # =====================================================

    async def cleanup_old_jobs(self, days_old: int = 30) -> int:
        """Clean up old completed jobs"""
        try:
            cutoff_date = datetime.utcnow().date() - datetime.timedelta(days=days_old)

            result = self.supabase.table('jobs')\
                .delete()\
                .eq('status', 'completed')\
                .lt('created_at', cutoff_date.isoformat())\
                .execute()

            return len(result.data) if result.data else 0

        except APIError as e:
            logger.error(f"Error cleaning up old jobs: {str(e)}")
            return 0

# Create singleton instance
supabase_client = SupabaseClient()

# Helper functions for backward compatibility with existing code
async def get_user(user_id: str) -> Optional[User]:
    """Get user profile - compatibility function"""
    return await supabase_client.get_user_profile(user_id)

async def create_job(job_data: Dict[str, Any]) -> Optional[JobV2]:
    """Create job - compatibility function"""
    return await supabase_client.create_job(job_data)

async def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job - compatibility function"""
    return await supabase_client.get_job(job_id)

async def update_job(job_id: str, updates: Dict[str, Any]) -> bool:
    """Update job - compatibility function"""
    return await supabase_client.update_job(job_id, updates)