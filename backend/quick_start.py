"""
Quick Start Script for SQLite Migration
Creates a demo user and shows credentials
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database_sqlite.sqlite_client import sqlite_client

def quick_start():
    print("\n" + "="*60)
    print("MASTERPOST.IO - QUICK START (SQLite)")
    print("="*60 + "\n")

    # Create demo user
    email = "demo@masterpost.io"
    print(f"Creating demo user: {email}")

    user = sqlite_client.create_user(email, credits=500)

    if user:
        print("\n[SUCCESS] Demo user created!\n")
        print("Your credentials:")
        print(f"  Email:       {user['email']}")
        print(f"  Access Code: {user['access_code']}")
        print(f"  Credits:     {user['credits']}")
        print()
        print("Save this access code! You'll need it to login.")
    else:
        print("\n[INFO] Demo user already exists.")
        credits = sqlite_client.get_user_credits(email)
        print(f"Current credits: {credits}")

    print()
    print("="*60)
    print("NEXT STEPS:")
    print("="*60)
    print()
    print("1. Start the backend:")
    print("   cd backend && uvicorn app.main:app --reload --port 8000")
    print()
    print("2. Test the API:")
    print(f"   curl -X POST http://localhost:8000/api/v1/auth/validate \\")
    print(f'     -H "Content-Type: application/json" \\')
    print(f"     -d '{{\"email\":\"{email}\",\"access_code\":\"YOUR_CODE\"}}'")
    print()
    print("3. Start the frontend:")
    print("   npm run dev")
    print()
    print("="*60)
    print()

if __name__ == "__main__":
    quick_start()
