# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root
repo_root = Path(__file__).resolve().parents[1]
load_dotenv(repo_root / ".env")

PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")

SERPAPI_KEY = os.getenv("SERPAPI_KEY")