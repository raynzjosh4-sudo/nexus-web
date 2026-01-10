import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Build paths inside the project like this: BASE_DIR / '.env'
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'

# Force load the .env file
load_dotenv(dotenv_path=env_path)

def get_supabase_client() -> Client:
    # Now we read from the environment variables securely
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        import logging
        logger = logging.getLogger(__name__)
        logger.debug("Looking for .env at: %s", env_path)
        logger.debug("URL found? %s", url is not None)
        logger.debug("Key found? %s", key is not None)
        raise ValueError("Supabase URL or Key is missing in .env file")

    return create_client(url, key)