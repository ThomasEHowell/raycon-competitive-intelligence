# src/db/engine.py
from sqlalchemy import create_engine
from src.config import PGUSER, PGPASSWORD, PGHOST, PGPORT, PGDATABASE


def get_engine():
    url = (
        f"postgresql+psycopg2://"
        f"{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
    )
    return create_engine(url)