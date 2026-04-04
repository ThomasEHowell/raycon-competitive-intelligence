# src/pipeline/run_daily.py

import traceback
from pathlib import Path
from datetime import datetime, timezone

from src.db.engine import get_engine
from src.pipeline.ingest_raw import run_ingest_raw
from src.pipeline.stage_unprocessed_raw import run_stage_unprocessed_raw
from src.utils.paths import get_pipeline_log_path
from src.utils.email import send_failure_email

def main():

    # Set run-level exception logging
    LOG_PATH = get_pipeline_log_path()
    PIPELINE_NAME = "run_daily"
    RUN_ID = "daily_run"

    # Call ingestion and staging pipeline
    try:
        engine = get_engine()
        run_ingest_raw(engine)
        run_stage_unprocessed_raw(engine)

    # Log and email alert in the case of exceptions
    except Exception:
        error_line = (
            f"{datetime.now(timezone.utc).isoformat()} | {PIPELINE_NAME} | FAILED | "
            f"run_id={RUN_ID}\n{traceback.format_exc()}\n"
        )
        with open(LOG_PATH, "a") as f:
            f.write(error_line)
            f.write("\n")

        send_failure_email(error_line)
        raise
        
if __name__ == "__main__":
    main()