# src/pipeline/run_daily.py

from src.db.engine import get_engine
from src.pipeline.ingest_raw import run_ingest_raw
from src.pipeline.stage_unprocessed_raw import run_stage_unprocessed_raw

def main():
    engine = get_engine()
    run_ingest_raw(engine)
    run_stage_unprocessed_raw(engine)

if __name__ == "__main__":
    main()