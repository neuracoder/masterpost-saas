"""
In-memory database client for testing without Supabase
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class MemoryDatabaseClient:
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.files: Dict[str, Dict] = {}

    def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job"""
        job_id = job_data.get('job_id', str(uuid.uuid4()))

        job = {
            "job_id": job_id,
            "user_id": job_data.get("user_id", "test_user"),
            "status": job_data.get("status", "uploaded"),
            "total_files": job_data.get("total_files", 0),
            "processed_files": job_data.get("processed_files", 0),
            "failed_files": job_data.get("failed_files", 0),
            "pipeline": job_data.get("pipeline"),
            "settings": job_data.get("settings", {}),
            "error_message": job_data.get("error_message"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "files": job_data.get("files", [])
        }

        self.jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        return self.jobs.get(job_id)

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update job"""
        if job_id not in self.jobs:
            return None

        job = self.jobs[job_id]
        job.update(updates)
        job["updated_at"] = datetime.utcnow().isoformat()

        return job

    def delete_job(self, job_id: str) -> bool:
        """Delete job"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False

    def list_jobs(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all jobs, optionally filtered by user"""
        jobs = list(self.jobs.values())
        if user_id:
            jobs = [job for job in jobs if job.get("user_id") == user_id]
        return jobs

    def save_to_file(self, filepath: str):
        """Save database to JSON file"""
        data = {
            "jobs": self.jobs,
            "files": self.files
        }
        Path(filepath).write_text(json.dumps(data, indent=2, default=str))

    def load_from_file(self, filepath: str):
        """Load database from JSON file"""
        if Path(filepath).exists():
            data = json.loads(Path(filepath).read_text())
            self.jobs = data.get("jobs", {})
            self.files = data.get("files", {})

# Global instance
memory_db = MemoryDatabaseClient()