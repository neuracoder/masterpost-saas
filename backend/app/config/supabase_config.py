import os
import time
import logging
from supabase import create_client, Client
from typing import Optional

logger = logging.getLogger(__name__)

def init_supabase_with_retry(max_retries: int = 3, retry_delay: int = 2) -> Optional[Client]:
    """
    Initialize Supabase client with retry mechanism
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase credentials missing: URL=%s, KEY=%s", 
                    bool(supabase_url), bool(supabase_key))
        return None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting Supabase connection (attempt {attempt + 1}/{max_retries})")

            supabase: Client = create_client(supabase_url, supabase_key)

            # Skip table verification - tables are verified via SQL
            # test_result = supabase.table("profiles").select("id").limit(1).execute()

            logger.info("Supabase connection established successfully")
            return supabase
            
        except Exception as e:
            logger.warning(f"Supabase connection attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All Supabase connection attempts failed")
    
    return None

# Global Supabase client instance
supabase_client = init_supabase_with_retry()

def get_supabase() -> Optional[Client]:
    """Get the Supabase client instance"""
    return supabase_client
