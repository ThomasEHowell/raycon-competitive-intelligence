# src/pipeline/ingest_raw.py

import requests
import json
import time

from sqlalchemy import text
from datetime import datetime, timezone

import uuid
from pathlib import Path

from src.db.engine import get_engine
from src.config import SERPAPI_KEY

KEYWORDS = [
    'headphones',
    'earbuds',
    'best headphones',
    'best earbuds',
    'wireless headphones',
    'wireless earbuds',
    'bluetooth headphones'
]

def run_ingest_raw(engine):
    # Logging Setup --------------------------------------------------------

    PIPELINE_NAME = "ingest_raw"
    RUN_ID = str(uuid.uuid4())

    REPO_ROOT = Path(__file__).resolve().parents[2]
    LOG_PATH = REPO_ROOT / "logs" / "pipeline.log"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    STARTED_AT = datetime.now(timezone.utc)

    # Start log line
    start_line = f"{STARTED_AT.isoformat()} | {PIPELINE_NAME} | START | run_id={RUN_ID}\n"
    with open(LOG_PATH, "a") as f:
        f.write(start_line)
        
    print(start_line.strip())

    # ---- Run counters ----
    keywords_planned = len(KEYWORDS)
    successful_payloads = 0
    api_requests = 0
    raw_rows_inserted = 0

    soft_errors = 0
    retries = 0
    keywords_failed_after_retry = 0
    #hard_failures = 0             # Will later be implemented alongside .py refactoring


    # SerpAPI Ingestion Functions -----------------------------------

    def fetch_google_shopping_results(keyword: str) -> dict:
        """
        Pull one SerpAPI request using a pre-determined keyword.
        Returns a Python dictionary from the API's JSON result.
        """
        # URL for Google Shopping engine
        url = 'https://serpapi.com/search.json'
        
        # Standardized parameters for consistent pulls across days
        params = {
            "engine": "google_shopping",
            "q": keyword,
            "api_key": SERPAPI_KEY,
            'location': "Los Angeles,California,United States",  #SerpAPI's canonical code for LA
            'gl': 'us',    # geographic location
            'hl': 'en',    # language
            'num': 100,     # max number of results to return
            'no_cache': 'true'
        }

        # Send request
        response = requests.get(url, params=params, timeout=30)

        response.raise_for_status()     # Discover API errors immediately
        return response.json()

    def insert_raw_google_shopping(keyword: str, response: dict, page: int = 1):
        """
        Insert one SerpAPI response into raycon.raw_google_shopping.
        Returns the new row's id.
        """
        # Record creation timestamp
        pulled_at = datetime.now(timezone.utc)

        # Convert Python dict to JSON string for Postgres
        json_str = json.dumps(response)

        # Flag payload_status as success or flag
        if "shopping_results" in response and "error" not in response:
            payload_status = 'success'
        else:
            payload_status = 'failure'

        # Parameterized INSERT statement
        sql = text("""
                INSERT INTO raycon.raw_google_shopping (pulled_at, keyword, page, response_json, status)
                VALUES (:pulled_at, :keyword, :page, CAST(:response_json AS jsonb), :status)
                RETURNING id;
            """)
        
        # Run inside a transaction and get the new id
        with engine.begin() as conn:
            new_id = conn.execute(
                sql,
                {
                    "pulled_at": pulled_at,
                    "keyword": keyword,
                    "page": page,                 # always 1 for now
                    "response_json": json_str,    # JSONB cast happens in SQL
                    "status": payload_status
                },
            ).scalar_one()
            
        return new_id, payload_status

    def ingest_keyword(keyword: str, page: int = 1) -> tuple[int, dict, str]:
        """
        Fetch Google Shopping results for one keyword and insert into the raw table.
        
        Returns:
            new_row_id (int): Surrogate key of the inserted raw row.
            response_dict (dict): API response returned by SerpAPI.
        """
        # Step 1: Fetch API response for this keyword
        response = fetch_google_shopping_results(keyword)

        # Step 2: Insert into Postgres raw table
        new_id, payload_status = insert_raw_google_shopping(keyword, response, page=page)

        return new_id, response, payload_status


    # Execute Ingestion for All Keywords ------------------------------

    ingestion_results = []
    sample_response = None
    sample_keyword = None

    for i, kw in enumerate(KEYWORDS, start=1):
        api_requests += 1
        print(f"[{i}/{len(KEYWORDS)}] Ingesting {kw!r} ...")

        # Run full ingestion for a single keyword
        new_id, response, payload_status = ingest_keyword(kw, page=1)
        ingestion_results.append({"keyword": kw, "id": new_id, 'payload_status': payload_status})

        # Update counter for logging
        if new_id is not None:
            raw_rows_inserted += 1

        # Allow one retry per keyword
        if payload_status == 'success':
            successful_payloads += 1

        else:
            api_requests += 1
            soft_errors += 1
            retries += 1
            print("Non-standard payload detected (missing shopping_results or error present). Retrying once...")
            time.sleep(5)
            new_id, response, payload_status = ingest_keyword(kw, page=1)
            ingestion_results.append({"keyword": kw, "id": new_id, 'payload_status': payload_status})
            if new_id is not None:
                raw_rows_inserted += 1
                
            # Inform if second ingestion was also non-standard
            if payload_status == 'success':
                successful_payloads += 1
            else:
                soft_errors +=1
                keywords_failed_after_retry += 1
                print(f"Couldn't obtain a standard payload format for '{kw}'. Moving on to next keyword.")

        # Keep the first response as a sample to save to disk later
        if sample_response is None:
            sample_response = response
            sample_keyword = kw


    # Save Sample JSON ---------------------------------------------

    # Create folder if missing
    samples_dir = REPO_ROOT / "data" / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    #os.makedirs("../data/samples", exist_ok=True)

    # Where the sample will be saved
    sample_path = samples_dir / "google_shopping_example.json"
    #sample_path = "../data/samples/google_shopping_example.json"

    # Write to disk
    with sample_path.open("w", encoding="utf-8") as f:
        json.dump(sample_response, f, indent=2)
    #with open(sample_path, "w", encoding="utf-8") as f:
    #    json.dump(sample_response, f, indent=2)

    print(f"Saved sample response for {sample_keyword!r} to {sample_path}")


    # Logging (Completion) ------------------------------------------------------

    ENDED_AT = datetime.now(timezone.utc)
    DURATION_S = (ENDED_AT - STARTED_AT).total_seconds()

    end_line = (
        f"{ENDED_AT.isoformat()} | {PIPELINE_NAME} | COMPLETED | "
        f"run_id={RUN_ID} | duration_s={round(DURATION_S, 2)} | "
        f"keywords_planned={keywords_planned} | "
        f"api_requests={api_requests} | "
        f"raw_rows_inserted={raw_rows_inserted} | "
        f"successful_payloads={successful_payloads} | "
        f"soft_errors={soft_errors} | "
        f"retries={retries} | "
        f"keywords_failed_after_retry={keywords_failed_after_retry}\n"
    )

    with open(LOG_PATH, "a") as f:
        f.write(end_line)
        
    print(end_line.strip())

    return ingestion_results


def main():
    engine = get_engine()
    run_ingest_raw(engine)

if __name__ == '__main__':
    main()

