"""
Migration script to add stats columns to existing users table
Run this script ONCE to update existing database
"""
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path("backend/data/masterpost.db")


def migrate_database():
    """Add stats columns to users table if they don't exist"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        columns_to_add = []
        if 'basic_images_processed' not in columns:
            columns_to_add.append(('basic_images_processed', 'INTEGER DEFAULT 0'))
        if 'qwen_images_processed' not in columns:
            columns_to_add.append(('qwen_images_processed', 'INTEGER DEFAULT 0'))

        if not columns_to_add:
            logger.info("✅ Database already up to date - stats columns exist")
            conn.close()
            return

        # Add missing columns
        for column_name, column_def in columns_to_add:
            logger.info(f"Adding column: {column_name}")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")

        conn.commit()
        logger.info("✅ Migration completed successfully!")
        logger.info(f"   Added {len(columns_to_add)} column(s) to users table")

        # Verify
        cursor.execute("PRAGMA table_info(users)")
        all_columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"   Current columns: {', '.join(all_columns)}")

        conn.close()

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    logger.info("🚀 Starting database migration...")
    logger.info(f"   Database path: {DB_PATH}")

    if not DB_PATH.exists():
        logger.error(f"❌ Database not found at {DB_PATH}")
        logger.error("   Please ensure the backend has been run at least once")
        exit(1)

    migrate_database()
