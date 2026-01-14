from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from .database_sqlite.sqlite_client import sqlite_client
from .routers import upload, process, download, simple_auth, image_editor, manual_editor, lemonsqueezy_routes, paypal_routes, paddle_routes
# test_routes and credit_routes disabled (use Supabase - need migration)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Masterpost.io API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api_prefix = "/api/v1"
app.include_router(upload.router, prefix=api_prefix)
app.include_router(process.router, prefix=api_prefix)
app.include_router(download.router, prefix=api_prefix)
# app.include_router(test_routes.router, prefix=api_prefix)  # Disabled - uses Supabase
app.include_router(simple_auth.router, prefix=api_prefix)
app.include_router(lemonsqueezy_routes.router)  # LemonSqueezy routes (includes /api/v1 prefix in router)
app.include_router(paypal_routes.router)  # PayPal routes (includes /api/v1 prefix in router)
app.include_router(paddle_routes.router)  # Paddle routes (includes /api/v1 prefix in router)
app.include_router(image_editor.router, prefix=api_prefix)
app.include_router(manual_editor.router, prefix=api_prefix)
# app.include_router(credit_routes.router, prefix=api_prefix)  # Disabled - uses Supabase

@app.get("/")
async def root():
    return {"message": "Masterpost.io API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "sqlite",
        "version": "2.0.0 (SQLite migration)"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Masterpost.io API v2.0 (SQLite)")
    logger.info("✅ SQLite database initialized successfully")
    logger.info(f"📁 Database path: {sqlite_client.db_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Test auth router
from .routers import test_auth
app.include_router(test_auth.router, prefix="/api/v1")

# Test auth router
from .routers import test_auth
app.include_router(test_auth.router, prefix="/api/v1")
