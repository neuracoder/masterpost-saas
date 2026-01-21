#!/usr/bin/env python3
"""
MASTERPOST.IO - Admin API v2
Outputs detailed user stats and transaction history in JSON.
"""

import sqlite3
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "masterpost.db"

def get_stats_json():
    try:
        if not DB_PATH.exists():
            return {"error": f"Database not found at {DB_PATH}"}

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        stats = {
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "users_list": []
        }

        # 1. Global Summary (Simplified)
        cursor.execute("SELECT COUNT(*) FROM users")
        stats["summary"]["total_users"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE credits < 51 AND total_spent = 0")
        stats["summary"]["free_users"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE total_spent > 0")
        stats["summary"]["paid_users"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(total_spent) FROM users")
        stats["summary"]["total_revenue"] = cursor.fetchone()[0] or 0.0

        # 2. Detailed User List
        # We join with a subquery to get the LATEST transaction for each user
        query = """
            SELECT 
                u.email, 
                u.credits, 
                u.created_at, 
                u.last_used_at,
                u.basic_images_processed,
                u.qwen_images_processed,
                u.total_spent,
                u.is_paying_customer,
                u.purchase_count,
                (
                    SELECT amount_paid || ' (' || credits_added || ' credits)'
                    FROM transactions t 
                    WHERE t.email = u.email 
                    ORDER BY t.created_at DESC 
                    LIMIT 1
                ) as last_pack_info,
                (
                    SELECT created_at
                    FROM transactions t 
                    WHERE t.email = u.email 
                    ORDER BY t.created_at DESC 
                    LIMIT 1
                ) as last_purchase_date
            FROM users u
            ORDER BY 
                CASE WHEN u.total_spent > 0 THEN 0 ELSE 1 END,
                u.created_at DESC
            LIMIT 50
        """
        
        cursor.execute(query)
        for row in cursor.fetchall():
            stats["users_list"].append({
                "email": row["email"],
                "credits": row["credits"],
                "created_at": row["created_at"],
                "last_active": row["last_used_at"] or row["created_at"],
                "usage_basic": row["basic_images_processed"],
                "usage_premium": row["qwen_images_processed"],
                "total_spent": row["total_spent"],
                "is_paid": bool(row["is_paying_customer"] or row["total_spent"] > 0),
                "purchase_count": row["purchase_count"],
                "last_pack": row["last_pack_info"],
                "last_purchase_date": row["last_purchase_date"]
            })

        conn.close()
        return stats

    except Exception as e:
        return {"error": str(e), "trace": str(sys.exc_info())}

if __name__ == "__main__":
    print(json.dumps(get_stats_json(), indent=2))
