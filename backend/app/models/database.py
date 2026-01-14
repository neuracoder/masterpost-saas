import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
import json

from ...core.config import settings
from .schemas import JobCreate, JobUpdate, JobResponse, JobStatus

class SupabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )

    async def create_job(self, job_data: JobCreate) -> JobResponse:
        """Create a new job in the database"""
        try:
            job_dict = {
                'job_id': job_data.job_id,
                'user_id': job_data.user_id,
                'status': job_data.status.value,
                'total_files': job_data.total_files,
                'processed_files': 0,
                'failed_files': 0,
                'pipeline': job_data.pipeline.value if job_data.pipeline else None,
                'settings': json.dumps(job_data.settings),
                'files': json.dumps([file.dict() for file in job_data.files]),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            result = self.supabase.table('jobs').insert(job_dict).execute()

            if result.data:
                return self._dict_to_job_response(result.data[0])
            else:
                raise Exception("Failed to create job")

        except Exception as e:
            print(f"Error creating job: {str(e)}")
            raise

    async def get_job(self, job_id: str) -> Optional[JobResponse]:
        """Get a job by ID"""
        try:
            result = self.supabase.table('jobs').select('*').eq('job_id', job_id).execute()

            if result.data:
                return self._dict_to_job_response(result.data[0])
            return None

        except Exception as e:
            print(f"Error getting job {job_id}: {str(e)}")
            return None

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update job status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }

            if error_message:
                update_data['error_message'] = error_message

            result = self.supabase.table('jobs').update(update_data).eq('job_id', job_id).execute()

            return len(result.data) > 0

        except Exception as e:
            print(f"Error updating job status {job_id}: {str(e)}")
            return False

    async def update_job_progress(
        self,
        job_id: str,
        processed_files: int,
        failed_files: int = 0
    ) -> bool:
        """Update job progress"""
        try:
            update_data = {
                'processed_files': processed_files,
                'failed_files': failed_files,
                'updated_at': datetime.utcnow().isoformat()
            }

            result = self.supabase.table('jobs').update(update_data).eq('job_id', job_id).execute()

            return len(result.data) > 0

        except Exception as e:
            print(f"Error updating job progress {job_id}: {str(e)}")
            return False

    async def get_user_jobs(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[JobResponse]:
        """Get all jobs for a user"""
        try:
            result = (
                self.supabase.table('jobs')
                .select('*')
                .eq('user_id', user_id)
                .order('created_at', desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return [self._dict_to_job_response(job) for job in result.data]

        except Exception as e:
            print(f"Error getting user jobs {user_id}: {str(e)}")
            return []

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job from the database"""
        try:
            result = self.supabase.table('jobs').delete().eq('job_id', job_id).execute()
            return len(result.data) > 0

        except Exception as e:
            print(f"Error deleting job {job_id}: {str(e)}")
            return False

    def _dict_to_job_response(self, job_dict: Dict[str, Any]) -> JobResponse:
        """Convert database dict to JobResponse"""
        try:
            files = json.loads(job_dict.get('files', '[]')) if job_dict.get('files') else []
            settings = json.loads(job_dict.get('settings', '{}')) if job_dict.get('settings') else {}

            return JobResponse(
                job_id=job_dict['job_id'],
                user_id=job_dict['user_id'],
                status=job_dict['status'],
                total_files=job_dict['total_files'],
                processed_files=job_dict.get('processed_files', 0),
                failed_files=job_dict.get('failed_files', 0),
                pipeline=job_dict.get('pipeline'),
                settings=settings,
                error_message=job_dict.get('error_message'),
                created_at=datetime.fromisoformat(job_dict['created_at']),
                updated_at=datetime.fromisoformat(job_dict['updated_at']),
                files=files
            )
        except Exception as e:
            print(f"Error converting job dict: {str(e)}")
            raise

# Global database manager instance
db_manager = SupabaseManager()

# Database functions (used by routers)
async def create_job(job_data: JobCreate) -> JobResponse:
    return await db_manager.create_job(job_data)

async def get_job(job_id: str) -> Optional[JobResponse]:
    return await db_manager.get_job(job_id)

async def update_job_status(job_id: str, status: str, error_message: Optional[str] = None) -> bool:
    return await db_manager.update_job_status(job_id, status, error_message)

async def update_job_progress(job_id: str, processed_files: int, failed_files: int = 0) -> bool:
    return await db_manager.update_job_progress(job_id, processed_files, failed_files)

async def get_user_jobs(user_id: str, limit: int = 50, offset: int = 0) -> List[JobResponse]:
    return await db_manager.get_user_jobs(user_id, limit, offset)

async def delete_job(job_id: str) -> bool:
    return await db_manager.delete_job(job_id)

# Initialize database schema (call this once)
async def init_database():
    """Initialize database tables if they don't exist"""
    try:
        # Check if tables exist by trying to query them
        result = db_manager.supabase.table('jobs').select('job_id').limit(1).execute()
        print("Database tables already exist")
    except Exception as e:
        print(f"Database initialization might be needed: {str(e)}")
        print("Please ensure the following table exists in your Supabase database:")
        print("""
        CREATE TABLE jobs (
            id SERIAL PRIMARY KEY,
            job_id VARCHAR(255) UNIQUE NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            total_files INTEGER NOT NULL,
            processed_files INTEGER DEFAULT 0,
            failed_files INTEGER DEFAULT 0,
            pipeline VARCHAR(50),
            settings JSONB DEFAULT '{}',
            files JSONB DEFAULT '[]',
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX idx_jobs_user_id ON jobs(user_id);
        CREATE INDEX idx_jobs_status ON jobs(status);
        CREATE INDEX idx_jobs_created_at ON jobs(created_at);
        """)

# User management functions (for future authentication)
class UserManager:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def create_user(self, email: str, password: str, full_name: Optional[str] = None):
        """Create a new user"""
        try:
            # Use Supabase Auth
            result = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name
                    }
                }
            })
            return result
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            raise

    async def authenticate_user(self, email: str, password: str):
        """Authenticate a user"""
        try:
            result = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return result
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            raise

user_manager = UserManager(db_manager.supabase)