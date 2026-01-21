#!/usr/bin/env python3
"""
MASTERPOST.IO - Admin Statistics Dashboard
Quick CLI tool to view user stats and revenue

Usage:
    python3 admin_stats.py
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "masterpost.db"

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("MASTERPOST.IO - ADMIN DASHBOARD")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    print(f"Total Users: {total_users}")

    # Users last 24h
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at > ?", (yesterday,))
    print(f"Signups (24h): {cursor.fetchone()[0]}")

    # Users last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at > ?", (week_ago,))
    print(f"Signups (7 days): {cursor.fetchone()[0]}")

    # Credits stats - schema has 'credits' but no 'credits_used'
    # Calculate used from: basic_images_processed + qwen_images_processed
    cursor.execute("""
        SELECT
            SUM(credits) as available,
            SUM(basic_images_processed) as basic,
            SUM(qwen_images_processed) as qwen
        FROM users
    """)
    row = cursor.fetchone()
    available = row[0] or 0
    basic = row[1] or 0
    qwen = row[2] or 0
    # Credits used = basic (1 credit each) + qwen (3 credits each)
    credits_used = basic + (qwen * 3)

    print(f"\nCredits Available: {available}")
    print(f"Credits Used (calculated): {credits_used}")
    print(f"Revenue (est): ${(available + credits_used) * 0.10:.2f}")

    print(f"\nImages Processed (Basic): {basic}")
    print(f"Images Processed (Premium): {qwen}")
    print(f"Total Images Processed: {basic + qwen}")

    print("\n" + "="*60)
    print("RECENT USERS (Last 10)")
    print("="*60 + "\n")

    cursor.execute("""
        SELECT email, credits, basic_images_processed, qwen_images_processed, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 10
    """)

    print(f"{'Email':35} | {'Cred':>5} | {'Basic':>6} | {'Qwen':>5} | Created")
    print("-" * 85)

    for row in cursor.fetchall():
        email, credits, basic, qwen, created = row
        email_display = email[:33] + ".." if len(email) > 35 else email
        created_short = created[:16] if created else "N/A"
        print(f"{email_display:35} | {credits or 0:>5} | {basic or 0:>6} | {qwen or 0:>5} | {created_short}")

    print("\n" + "="*60)
    print("TOP USERS BY IMAGES PROCESSED")
    print("="*60 + "\n")

    cursor.execute("""
        SELECT email, credits, basic_images_processed, qwen_images_processed,
               basic_images_processed + qwen_images_processed as total
        FROM users
        WHERE basic_images_processed > 0 OR qwen_images_processed > 0
        ORDER BY total DESC
        LIMIT 10
    """)

    print(f"{'Email':35} | {'Credits':>7} | {'Basic':>6} | {'Qwen':>5} | {'Total':>6}")
    print("-" * 75)

    for row in cursor.fetchall():
        email, credits, basic, qwen, total = row
        email_display = email[:33] + ".." if len(email) > 35 else email
        print(f"{email_display:35} | {credits or 0:>7} | {basic or 0:>6} | {qwen or 0:>5} | {total or 0:>6}")

    print("\n" + "="*60)
    print("USERS WITH ACTIVE CREDITS (Top 10)")
    print("="*60 + "\n")

    cursor.execute("""
        SELECT email, credits, created_at
        FROM users
        WHERE credits > 0
        ORDER BY credits DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        email, credits, created = row
        print(f"{email:40} | {credits:>5} credits")

    # Recent jobs
    print("\n" + "="*60)
    print("RECENT JOBS (Last 10)")
    print("="*60 + "\n")

    cursor.execute("""
        SELECT id, email, status, pipeline, total_files, processed_files, created_at
        FROM jobs
        ORDER BY created_at DESC
        LIMIT 10
    """)

    print(f"{'Job ID':12} | {'Email':25} | {'Status':10} | {'Pipeline':10} | {'Files':>5} | Created")
    print("-" * 95)

    for row in cursor.fetchall():
        job_id, email, status, pipeline, total, processed, created = row
        job_short = job_id[:10] + ".." if job_id and len(job_id) > 12 else (job_id or "N/A")
        email_short = email[:23] + ".." if email and len(email) > 25 else (email or "N/A")
        created_short = created[:16] if created else "N/A"
        print(f"{job_short:12} | {email_short:25} | {status or 'N/A':10} | {pipeline or 'N/A':10} | {processed or 0:>5} | {created_short}")

    conn.close()

    print("\n" + "="*60)
    print("END OF REPORT")
    print("="*60 + "\n")

if __name__ == "__main__":
    get_stats()
