"""
SQLite Database Client - Simple local database for Masterpost.io
Replaces Supabase with ultra-simplified architecture
"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import secrets
import string

logger = logging.getLogger(__name__)

class SQLiteClient:
    def __init__(self, db_path: str = "/root/masterpost-saas/backend/data/masterpost.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"✅ SQLite database initialized: {self.db_path}")

    def _init_database(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path) as f:
            schema = f.read()

        conn = self._get_connection()
        try:
            conn.executescript(schema)
            conn.commit()
            logger.info("Database schema created successfully")
        finally:
            conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # ==================== USER MANAGEMENT ====================

    def generate_access_code(self) -> str:
        """Generate unique access code (format: MP-XXXX-XXXX)"""
        chars = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(chars) for _ in range(8))
        return f"MP-{code[:4]}-{code[4:]}"

    def create_user(self, email: str, credits: int = 50) -> Optional[str]:
        """Create new user with access code"""
        conn = self._get_connection()
        try:
            access_code = self.generate_access_code()
            conn.execute(
                "INSERT INTO users (email, access_code, credits) VALUES (?, ?, ?)",
                (email, access_code, credits)
            )
            conn.commit()
            logger.info(f"Created user: {email} with code: {access_code}")
            return access_code
        except sqlite3.IntegrityError:
            logger.error(f"User already exists: {email}")
            return None
        finally:
            conn.close()

    def validate_access(self, email: str, access_code: str) -> bool:
        """Validate email and access code"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 Validating: email={email}, code={access_code}")
        
        conn = self._get_connection()
        try:
            query = "SELECT email FROM users WHERE email = ? AND access_code = ?"
            logger.info(f"🔍 Query: {query}")
            logger.info(f"🔍 Params: email='{email}', code='{access_code}'")
            
            cursor = conn.execute(query, (email, access_code))
            result = cursor.fetchone()
            logger.info(f"🔍 Query result: {result}")
            
            if result:
                conn.execute(
                    "UPDATE users SET last_used_at = CURRENT_TIMESTAMP WHERE email = ?",
                    (email,)
                )
                conn.commit()
                logger.info("✅ Returning True")
                return True
            
            logger.info("❌ Returning False - no result")
            return False
        except Exception as e:
            logger.error(f"💥 Exception in validate_access: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        finally:
            conn.close()
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'email': result['email'],
                    'access_code': result['access_code'],
                    'credits': result['credits'],
                    'created_at': result['created_at'],
                    'last_used_at': result['last_used_at']
                }
            return None
        finally:
            conn.close()

    def get_user_credits(self, email: str) -> int:
        """Get user's current credit balance"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT credits FROM users WHERE email = ?",
                (email,)
            )
            result = cursor.fetchone()
            return result['credits'] if result else 0
        finally:
            conn.close()

    def get_user_stats(self, email: str) -> Optional[Dict[str, int]]:
        """
        Get user statistics

        Args:
            email: User email

        Returns:
            Dict with credits, basic_processed, qwen_processed
            None if user doesn't exist
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """SELECT
                    credits,
                    basic_images_processed,
                    qwen_images_processed
                FROM users
                WHERE email = ?""",
                (email,)
            )
            result = cursor.fetchone()

            if result:
                return {
                    "credits": result['credits'],
                    "basic_processed": result['basic_images_processed'] or 0,
                    "qwen_processed": result['qwen_images_processed'] or 0
                }

            return None

        except Exception as e:
            logger.error(f"❌ Error getting user stats for {email}: {e}")
            return None
        finally:
            conn.close()

    def increment_processing_stats(self, email: str, basic_count: int = 0, qwen_count: int = 0) -> bool:
        """
        Increment user's processing counters

        Args:
            email: User email
            basic_count: Number of images processed with basic/rembg
            qwen_count: Number of images processed with Qwen/AI

        Returns:
            bool: True if successful
        """
        conn = self._get_connection()
        try:
            if basic_count > 0:
                conn.execute(
                    """UPDATE users
                    SET basic_images_processed = basic_images_processed + ?
                    WHERE email = ?""",
                    (basic_count, email)
                )

            if qwen_count > 0:
                conn.execute(
                    """UPDATE users
                    SET qwen_images_processed = qwen_images_processed + ?
                    WHERE email = ?""",
                    (qwen_count, email)
                )

            conn.commit()
            logger.info(f"📊 Stats updated for {email}: +{basic_count} basic, +{qwen_count} qwen")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating stats for {email}: {e}")
            return False
        finally:
            conn.close()

    def deduct_credits(self, email: str, amount: int) -> bool:
        """Deduct credits from user account"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT credits FROM users WHERE email = ?",
                (email,)
            )
            result = cursor.fetchone()

            if not result or result['credits'] < amount:
                return False

            conn.execute(
                "UPDATE users SET credits = credits - ? WHERE email = ?",
                (amount, email)
            )
            conn.commit()
            logger.info(f"Deducted {amount} credits from {email}")
            return True
        finally:
            conn.close()

    def add_credits(self, email: str, amount: int) -> bool:
        """
        Suma créditos a un usuario existente
        Retorna True si éxito, False si el usuario no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users
                SET credits = credits + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (amount, email))

            conn.commit()
            success = cursor.rowcount > 0
            conn.close()

            if not success:
                logger.warning(f"⚠️ Usuario {email} no existe en DB")
            else:
                logger.info(f"Added {amount} credits to {email}")

            return success
        except Exception as e:
            logger.error(f"❌ Error adding credits: {e}")
            return False

    def log_transaction(self, email: str, credits: int, transaction_type: str,
                       description: str, stripe_payment_id: str = None) -> bool:
        """
        Registra una transacción de créditos en tabla de historial
        Crea la tabla si no existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    description TEXT,
                    stripe_payment_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                INSERT INTO transactions
                (email, credits, transaction_type, description, stripe_payment_id)
                VALUES (?, ?, ?, ?, ?)
            """, (email, credits, transaction_type, description, stripe_payment_id))

            conn.commit()
            conn.close()
            logger.info(f"Logged transaction: {transaction_type} for {email}")
            return True
        except Exception as e:
            logger.error(f"❌ Error logging transaction: {e}")
            return False

    # ==================== JOB MANAGEMENT ====================

    def create_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Create new processing job"""
        conn = self._get_connection()
        try:
            job_id = job_data.get('id')
            email = job_data.get('email')

            conn.execute(
                """INSERT INTO jobs (id, email, status, pipeline, total_files, settings)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    job_id,
                    email,
                    job_data.get('status', 'uploaded'),
                    job_data.get('pipeline'),
                    job_data.get('total_files', 0),
                    json.dumps(job_data.get('settings', {}))
                )
            )
            conn.commit()
            logger.info(f"Created job: {job_id} for {email}")
            return job_id
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return None
        finally:
            conn.close()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM jobs WHERE id = ?",
                (job_id,)
            )
            result = cursor.fetchone()

            if result:
                return {
                    'id': result['id'],
                    'email': result['email'],
                    'status': result['status'],
                    'pipeline': result['pipeline'],
                    'total_files': result['total_files'],
                    'processed_files': result['processed_files'],
                    'failed_files': result['failed_files'],
                    'settings': json.loads(result['settings']) if result['settings'] else {},
                    'created_at': result['created_at'],
                    'updated_at': result['updated_at']
                }
            return None
        finally:
            conn.close()

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job status and progress"""
        conn = self._get_connection()
        try:
            set_clauses = []
            values = []

            for key, value in updates.items():
                if key == 'settings':
                    value = json.dumps(value)
                set_clauses.append(f"{key} = ?")
                values.append(value)

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(job_id)

            query = f"UPDATE jobs SET {', '.join(set_clauses)} WHERE id = ?"
            conn.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            return False
        finally:
            conn.close()

    def get_user_jobs(self, email: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's jobs"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """SELECT * FROM jobs WHERE email = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (email, limit)
            )
            results = cursor.fetchall()

            jobs = []
            for row in results:
                jobs.append({
                    'id': row['id'],
                    'status': row['status'],
                    'pipeline': row['pipeline'],
                    'total_files': row['total_files'],
                    'processed_files': row['processed_files'],
                    'failed_files': row['failed_files'],
                    'created_at': row['created_at']
                })

            return jobs
        finally:
            conn.close()

    # ==================== TRANSACTIONS ====================

    def record_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """Record credit purchase transaction"""
        conn = self._get_connection()
        try:
            conn.execute(
                """INSERT INTO transactions (email, transaction_type, credits_added,
                   amount_paid, stripe_session_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    transaction_data.get('email'),
                    transaction_data.get('type', 'credit_purchase'),
                    transaction_data.get('credits'),
                    transaction_data.get('amount'),
                    transaction_data.get('stripe_session_id')
                )
            )
            conn.commit()
            logger.info(f"Recorded transaction for {transaction_data.get('email')}")
            return True
        except Exception as e:
            logger.error(f"Error recording transaction: {e}")
            return False
        finally:
            conn.close()

# Global instance
sqlite_client = SQLiteClient()
