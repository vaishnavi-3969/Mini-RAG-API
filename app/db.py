from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
import os

# Explicitly load .env from project root (Windows safe)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase environment variables not loaded")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
