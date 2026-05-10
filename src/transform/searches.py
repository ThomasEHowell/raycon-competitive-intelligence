# src/transform/searches.py
import pandas as pd

def build_searches_for_keyword(keyword_raw):
    """
    Build the stg_searches record for a single raw search event.

    This function:
    - Takes the first row of df_raw (prototype mode)
    - Extracts identifiers (raw_id, pulled_at, keyword, page)
    - Extracts search parameters from response_json["search_parameters"]
    - Places everything into a clean, single-row DataFrame

    Returns:
        pd.DataFrame: one clean stg_search row
    """
    
     # Grab the first raw record (example row in this case)
    search_row = keyword_raw

     # Pull identifiers & search metadata from the raw table
    raw_id, pulled_at, keyword, page = search_row[['id', 'pulled_at', 'keyword', 'page']]
    
    # Extract the "search_parameters" object from the JSON
    params = search_row["response_json"]["search_parameters"]

    # Build the clean staging DataFrame
    search_df_clean = pd.DataFrame([{
    "raw_id": raw_id,
    "pulled_at": pulled_at,
    "keyword": keyword,
    "page": page,
    "location_used": params.get("location_used"),
    "location_requested": params.get("location_requested"),
    "gl": params.get("gl"),
    "hl": params.get("hl"),
    "device": params.get("device"),
    "num_results_requested": int(params["num"]) if params.get("num") is not None else None,
    "engine": params.get("engine"),
    "google_domain": params.get("google_domain"),
    }])
    return search_df_clean