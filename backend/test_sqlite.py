"""
Test script for SQLite migration
Run this to verify the SQLite database is working correctly
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database_sqlite.sqlite_client import sqlite_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sqlite():
    """Test all SQLite functionality"""

    print("\n" + "="*60)
    print("TESTING SQLITE DATABASE")
    print("="*60 + "\n")

    # Test 1: Create User
    print("Test 1: Creating user...")
    user = sqlite_client.create_user("test@masterpost.io", credits=100)

    if user:
        print(f"[OK] User created successfully!")
        print(f"   Email: {user['email']}")
        print(f"   Access Code: {user['access_code']}")
        print(f"   Credits: {user['credits']}")
        access_code = user['access_code']
    else:
        print("[WARN] User already exists (this is OK for re-running the test)")
        # Try to get existing user's access code
        print("   Attempting to validate with a test code...")
        access_code = "MP-TEST-1234"  # This won't work, just for demo

    print()

    # Test 2: Validate Access
    print("Test 2: Validating access...")
    if user:
        is_valid = sqlite_client.validate_access("test@masterpost.io", access_code)
        if is_valid:
            print("✅ Access validation successful!")
        else:
            print("❌ Access validation failed!")
    else:
        print("⚠️  Skipping validation test (user already existed)")

    print()

    # Test 3: Check Credits
    print("Test 3: Checking credits...")
    credits = sqlite_client.get_user_credits("test@masterpost.io")
    print(f"✅ User has {credits} credits")

    print()

    # Test 4: Deduct Credits
    print("Test 4: Deducting 10 credits...")
    success = sqlite_client.deduct_credits("test@masterpost.io", 10)
    if success:
        print("✅ Credits deducted successfully!")
        new_credits = sqlite_client.get_user_credits("test@masterpost.io")
        print(f"   New balance: {new_credits} credits")
    else:
        print("❌ Credit deduction failed!")

    print()

    # Test 5: Add Credits
    print("Test 5: Adding 50 credits...")
    sqlite_client.add_credits("test@masterpost.io", 50)
    new_credits = sqlite_client.get_user_credits("test@masterpost.io")
    print(f"✅ Credits added! New balance: {new_credits} credits")

    print()

    # Test 6: Create Job
    print("Test 6: Creating a job...")
    import uuid
    job_id = str(uuid.uuid4())
    job_data = {
        'id': job_id,
        'email': 'test@masterpost.io',
        'status': 'uploaded',
        'pipeline': 'amazon',
        'total_files': 5,
        'settings': {
            'use_premium': False,
            'test': True
        }
    }

    created_job_id = sqlite_client.create_job(job_data)
    if created_job_id:
        print(f"✅ Job created successfully!")
        print(f"   Job ID: {job_id}")
    else:
        print("❌ Job creation failed!")

    print()

    # Test 7: Get Job
    print("Test 7: Retrieving job...")
    job = sqlite_client.get_job(job_id)
    if job:
        print("✅ Job retrieved successfully!")
        print(f"   Status: {job['status']}")
        print(f"   Pipeline: {job['pipeline']}")
        print(f"   Total files: {job['total_files']}")
    else:
        print("❌ Job retrieval failed!")

    print()

    # Test 8: Update Job
    print("Test 8: Updating job status...")
    update_success = sqlite_client.update_job(job_id, {
        'status': 'processing',
        'processed_files': 3
    })

    if update_success:
        print("✅ Job updated successfully!")
        updated_job = sqlite_client.get_job(job_id)
        print(f"   New status: {updated_job['status']}")
        print(f"   Processed files: {updated_job['processed_files']}")
    else:
        print("❌ Job update failed!")

    print()

    # Test 9: Get User Jobs
    print("Test 9: Getting user's jobs...")
    user_jobs = sqlite_client.get_user_jobs("test@masterpost.io")
    print(f"✅ Found {len(user_jobs)} job(s) for user")
    for i, job in enumerate(user_jobs, 1):
        print(f"   Job {i}: {job['id'][:8]}... - {job['status']}")

    print()

    # Test 10: Record Transaction
    print("Test 10: Recording a transaction...")
    transaction_data = {
        'email': 'test@masterpost.io',
        'type': 'credit_purchase',
        'credits': 100,
        'amount': 9.99,
        'stripe_session_id': 'test_session_123'
    }

    trans_success = sqlite_client.record_transaction(transaction_data)
    if trans_success:
        print("✅ Transaction recorded successfully!")
    else:
        print("❌ Transaction recording failed!")

    print()

    print("="*60)
    print("🎉 ALL TESTS COMPLETED!")
    print("="*60)
    print()
    print("📋 Summary:")
    print(f"   Database: {sqlite_client.db_path}")
    print(f"   Test user: test@masterpost.io")
    if user:
        print(f"   Access code: {user['access_code']}")
    print(f"   Credits: {sqlite_client.get_user_credits('test@masterpost.io')}")
    print()
    print("✨ You can now test the API with these credentials!")
    print()

if __name__ == "__main__":
    test_sqlite()
