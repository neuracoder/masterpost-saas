from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/test", tags=["test"])

class TestLoginRequest(BaseModel):
    email: str
    access_code: str

@router.post("/login")
async def test_login(request: TestLoginRequest):
    """Test login endpoint - sin dependencias"""
    try:
        conn = sqlite3.connect('/root/masterpost-saas/backend/data/masterpost.db')
        cursor = conn.execute(
            "SELECT email, credits FROM users WHERE email = ? AND access_code = ?",
            (request.email, request.access_code)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "success": True,
                "email": result[0],
                "credits": result[1],
                "message": "Login OK"
            }
        else:
            return {
                "success": False,
                "message": "User not found"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
