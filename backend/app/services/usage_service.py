"""
Usage tracking and limits service for MASTERPOST.IO V2.0
Manages user quotas, usage tracking, and hard limits enforcement
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, date
from ..models.user_models import (
    PlanType, UserUsage, UsageCheck, PLAN_CONFIGS,
    User, ProcessingMethod
)
from ...database.supabase_client import supabase_client

logger = logging.getLogger(__name__)

class UsageTrackingService:
    """
    Service for tracking user usage and enforcing plan limits
    """

    def __init__(self):
        self.usage_cache = {}  # In-memory cache for current month usage
        self.cache_ttl = 300  # 5 minutes cache

    async def check_usage_limits(self, user_id: str, images_count: int = 1) -> UsageCheck:
        """
        Check if user can process the requested number of images

        Args:
            user_id: User identifier
            images_count: Number of images to process

        Returns:
            UsageCheck with limits and availability
        """
        try:
            # Use Supabase database function for usage checking
            return await supabase_client.check_usage_limits(user_id, images_count)

        except Exception as e:
            logger.error(f"Error checking usage limits for user {user_id}: {str(e)}")
            # Fail safe - allow processing with basic limits
            return UsageCheck(
                can_process=images_count <= 10,
                remaining_images=10,
                plan_limit=10,
                current_usage=0,
                plan=PlanType.FREE
            )

    async def update_usage(
        self,
        user_id: str,
        images_processed: int = 0,
        qwen_api_calls: int = 0,
        processing_method: ProcessingMethod = ProcessingMethod.LOCAL
    ) -> bool:
        """
        Update user usage statistics

        Args:
            user_id: User identifier
            images_processed: Number of images processed
            qwen_api_calls: Number of Qwen API calls made
            processing_method: Method used for processing

        Returns:
            True if update successful
        """
        try:
            # Use Supabase database function for usage updates
            job_success = images_processed > 0  # Assume success if images were processed

            return await supabase_client.update_usage(
                user_id=user_id,
                images_count=images_processed,
                qwen_calls=qwen_api_calls if processing_method == ProcessingMethod.QWEN else 0,
                job_success=job_success
            )

        except Exception as e:
            logger.error(f"Failed to update usage for user {user_id}: {str(e)}")
            return False

    async def get_current_usage(self, user_id: str) -> UserUsage:
        """
        Get current month usage for user with caching

        Args:
            user_id: User identifier

        Returns:
            UserUsage for current month
        """
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        cache_key = f"{user_id}_{year}_{month}"

        # Check cache first
        if cache_key in self.usage_cache:
            cached = self.usage_cache[cache_key]
            if current_date.timestamp() - cached["timestamp"] < self.cache_ttl:
                return cached["usage"]

        # Get from database (mock implementation)
        usage = UserUsage(
            user_id=user_id,
            year=year,
            month=month,
            images_processed=0,
            qwen_api_calls=0,
            created_at=current_date,
            updated_at=current_date
        )

        # In production, this would query the database
        # For now, return default usage
        return usage

    async def get_user_info(self, user_id: str) -> Optional[User]:
        """
        Get user information including plan

        Args:
            user_id: User identifier

        Returns:
            User object or None if not found
        """
        try:
            return await supabase_client.get_user_profile(user_id)
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {str(e)}")
            return None

    async def save_usage(self, usage: UserUsage) -> bool:
        """
        Save usage to database

        Args:
            usage: UserUsage object to save

        Returns:
            True if successful
        """
        try:
            # Mock implementation - in production this would save to database
            logger.info(f"Saving usage for user {usage.user_id}: {usage.images_processed} images")
            return True
        except Exception as e:
            logger.error(f"Failed to save usage: {str(e)}")
            return False

    async def get_usage_history(self, user_id: str, months: int = 12) -> list:
        """
        Get usage history for user

        Args:
            user_id: User identifier
            months: Number of months to retrieve

        Returns:
            List of UserUsage objects
        """
        # Mock implementation - in production this would query the database
        return []

    async def reset_usage(self, user_id: str) -> bool:
        """
        Reset usage for current month (admin function)

        Args:
            user_id: User identifier

        Returns:
            True if successful
        """
        try:
            current_date = datetime.now()
            year = current_date.year
            month = current_date.month
            cache_key = f"{user_id}_{year}_{month}"

            # Clear cache
            if cache_key in self.usage_cache:
                del self.usage_cache[cache_key]

            logger.info(f"Reset usage for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset usage for user {user_id}: {str(e)}")
            return False

    async def get_plan_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive usage summary for user dashboard

        Args:
            user_id: User identifier

        Returns:
            Summary with usage, limits, and plan info
        """
        try:
            # Use Supabase dashboard stats function
            return await supabase_client.get_user_dashboard_stats(user_id)

        except Exception as e:
            logger.error(f"Failed to get usage summary for user {user_id}: {str(e)}")
            return {}

    async def check_zip_limits(self, user_id: str, files_count: int) -> Dict[str, Any]:
        """
        Check if user can process a ZIP file with given number of files

        Args:
            user_id: User identifier
            files_count: Number of files in ZIP

        Returns:
            Check result with limits and permissions
        """
        try:
            user = await self.get_user_info(user_id)
            if not user:
                return {"allowed": False, "reason": "User not found"}

            plan_config = PLAN_CONFIGS.get(user.plan, PLAN_CONFIGS[PlanType.FREE])

            # Check ZIP file limits
            if files_count > plan_config.max_images_per_zip:
                return {
                    "allowed": False,
                    "reason": f"ZIP contains {files_count} files, but your {user.plan} plan allows maximum {plan_config.max_images_per_zip} files per ZIP",
                    "limit": plan_config.max_images_per_zip,
                    "requested": files_count
                }

            # Check monthly usage limits
            usage_check = await self.check_usage_limits(user_id, files_count)
            if not usage_check.can_process:
                return {
                    "allowed": False,
                    "reason": f"Processing {files_count} files would exceed your monthly limit. You have {usage_check.remaining_images} images remaining this month.",
                    "monthly_limit": usage_check.plan_limit,
                    "remaining": usage_check.remaining_images
                }

            return {
                "allowed": True,
                "plan": user.plan,
                "zip_limit": plan_config.max_images_per_zip,
                "monthly_remaining": usage_check.remaining_images
            }

        except Exception as e:
            logger.error(f"Error checking ZIP limits for user {user_id}: {str(e)}")
            return {"allowed": False, "reason": "System error"}

# Singleton instance
usage_service = UsageTrackingService()

# Helper functions for easy integration
async def can_process_images(user_id: str, images_count: int = 1) -> bool:
    """Quick check if user can process images"""
    result = await usage_service.check_usage_limits(user_id, images_count)
    return result.can_process

async def track_processing(
    user_id: str,
    images_count: int,
    method: ProcessingMethod = ProcessingMethod.LOCAL
) -> bool:
    """Track image processing for user"""
    qwen_calls = images_count if method == ProcessingMethod.QWEN else 0
    return await usage_service.update_usage(user_id, images_count, qwen_calls, method)