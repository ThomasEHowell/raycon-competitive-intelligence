# src/pipeline/stage_unprocessed_raw.py

import pandas as pd
pd.set_option("future.no_silent_downcasting", True)

from sqlalchemy import text

import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.db.engine import get_engine
from src.transform.searches import build_searches_for_keyword
from src.transform.results import build_results_for_keyword

def run_stage_unprocessed_raw(engine):
    # Logging Setup ----------------------------------------------

    PIPELINE_NAME = 'stage_unprocessed_raw'
    RUN_ID = str(uuid.uuid4())

    REPO_ROOT = Path(__file__).resolve().parents[2]
    LOG_PATH = REPO_ROOT / "logs" / "pipeline.log"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    STARTED_AT = datetime.now(timezone.utc)

    try:
        # Start log line
        start_line = f'{STARTED_AT.isoformat()} | {PIPELINE_NAME} | START | run_id={RUN_ID}\n'
        with open(LOG_PATH, 'a') as f:
            f.write(start_line)
            
        print(start_line.strip())

        # ---- Run counters ----
        canonical_raws_selected = 0
        canonical_raws_processed = 0
        canonical_raws_skipped = 0
        stg_searches_rows_written = 0
        stg_results_rows_written = 0


        # Pull Raw JSON Records Not Yet Staged -----------------------------------------

        query = '''
        WITH daily_recency AS(
            SELECT id, pulled_at, keyword, page, response_json,
                ROW_NUMBER() OVER(PARTITION BY keyword, CAST(pulled_at AS date) ORDER BY pulled_at DESC) AS recency
            FROM raycon.raw_google_shopping
            WHERE status = 'success'
            ORDER BY pulled_at)
        SELECT id, pulled_at, keyword, page, response_json
        FROM daily_recency
        WHERE 
        recency = 1
        AND
        id NOT IN (SELECT raw_id FROM raycon.stg_searches);
        '''

        with engine.connect() as conn:
            df_raw = pd.read_sql(query, conn)

        canonical_raws_selected = len(df_raw)


        # Build Staging DataFrames from Unprocessed Searches ---------------------------------

        # Reset staged dfs each run (prevents stale dfs when not resetting kernel)
        stg_searches_df = None
        stg_results_df = None

        # Create lists to store the staged results of each raw record
        search_rows = []
        results_dfs = []

        # Append each raw record to its respective list
        for _, raw_row in df_raw.iterrows():
            search_rows.append(build_searches_for_keyword(raw_row))
            results_dfs.append(build_results_for_keyword(raw_row))

        # Keep only valid, non-empty dfs in case of irregularities
        search_rows = [df for df in search_rows if df is not None and not df.empty]
        results_dfs = [df for df in results_dfs if df is not None and not df.empty]

        # Build final staging dfs (remain None if no usable data)
        if search_rows:
            stg_searches_df = pd.concat(search_rows, ignore_index=True)
        if results_dfs:
            stg_results_df = pd.concat(results_dfs, ignore_index=True)

        # Derive processing counts for logging
        if stg_searches_df is not None and not stg_searches_df.empty:
            canonical_raws_processed = stg_searches_df["raw_id"].nunique()
        else:
            canonical_raws_processed = 0

        canonical_raws_skipped = canonical_raws_selected - canonical_raws_processed


        # Persist Staged Data -------------------------------------------

        #Only write to database if proper dataframes were created
        if (stg_searches_df is not None and not stg_searches_df.empty
            and stg_results_df is not None and not stg_results_df.empty):
            
            # Persist staged data atomically (either both tables succeed or both fail)
            with engine.begin() as conn:
                
                # 1) Check for and delete non-canonical first (results then searches)
                conn.execute(text("""
                    DELETE FROM raycon.stg_results sr
                    WHERE EXISTS (
                    SELECT 1
                    FROM raycon.vw_raw_non_canonical_daily rncd
                    WHERE sr.raw_id = rncd.id
                    );
                """))
            
                conn.execute(text("""
                    DELETE FROM raycon.stg_searches ss
                    WHERE EXISTS (
                    SELECT 1
                    FROM raycon.vw_raw_non_canonical_daily rncd
                    WHERE ss.raw_id = rncd.id
                    );
                """))
            
                # 2) Insert new canonical parsed rows
                stg_searches_df.to_sql(
                    "stg_searches", conn, schema="raycon",
                    if_exists="append", index=False)
            
                stg_results_df.to_sql(
                    "stg_results", conn, schema="raycon",
                    if_exists="append", index=False)

                # 3) Record inserted row counts for logging
                stg_searches_rows_written = len(stg_searches_df)
                stg_results_rows_written  = len(stg_results_df)


        # Logging (Completion) ------------------------------
        ENDED_AT = datetime.now(timezone.utc)
        DURATION_S = (ENDED_AT - STARTED_AT).total_seconds()

        end_line = (
            f'{ENDED_AT.isoformat()} | {PIPELINE_NAME} | COMPLETED | '
            f'run_id={RUN_ID} | duration_s={round(DURATION_S, 2)} | '
            f'canonical_raws_selected={canonical_raws_selected} | '
            f'canonical_raws_processed={canonical_raws_processed} | '
            f'canonical_raws_skipped={canonical_raws_skipped} | '
            f'stg_searches_rows_written={stg_searches_rows_written} | '
            f'stg_results_rows_written={stg_results_rows_written}\n'
        )

        with open(LOG_PATH, 'a') as f:
            f.write(end_line)

        print(end_line.strip())

    except Exception:
        error_line = (
            f"{datetime.now(timezone.utc).isoformat()} | {PIPELINE_NAME} | FAILED | "
            f"run_id={RUN_ID}\n{traceback.format_exc()}\n"
        )
        with open(LOG_PATH, "a") as f:
            f.write(error_line)
        raise

def main():
    engine = get_engine()
    run_stage_unprocessed_raw(engine)

if __name__ == '__main__':
    main()
