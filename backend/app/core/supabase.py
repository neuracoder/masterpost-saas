"""
Supabase clients for authentication and credits system
"""

from supabase import create_client, Client
from .config import settings

# Admin client (service role) - for backend operations
def get_supabase_admin() -> Client:
    """Get Supabase admin client with service role key"""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )

# Anon client - for client-side operations
def get_supabase_anon() -> Client:
    """Get Supabase anon client with anon key"""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )

# Create singleton instances
supabase_admin = get_supabase_admin()
supabase_anon = get_supabase_anon()
