-- src/db/create_staging_tables.sql


-- ============================================
-- Staging Table: stg_searches
-- Purpose: Store search-level information and parameters
-- Grain: One row per Google Shopping keyword search
-- ============================================
CREATE TABLE IF NOT EXISTS raycon.stg_searches (
    -- Links to raw record that generated this search
    raw_id                 INTEGER PRIMARY KEY
        REFERENCES raycon.raw_google_shopping (id),

    -- Context of the search
    pulled_at              TIMESTAMPTZ NOT NULL,
    keyword                TEXT        NOT NULL,
    page                   INTEGER     NOT NULL,

    -- Parameters extracted from search_parameters (one of the JSON dictionaries)
    location_used 		   TEXT,
    location_requested 	   TEXT,
    gl                     TEXT,
    hl                     TEXT,
    device                 TEXT,
    num_results_requested  INTEGER,
    engine                 TEXT,
    google_domain          TEXT
);


-- ============================================================================
-- Staging Table: stg_results
-- Purpose: Store flattened product results and fields from the SerpAPI requests.
-- Grain: One row per product result (roughly 50-75 rows from each keyword search)
-- ============================================================================
CREATE TABLE IF NOT EXISTS raycon.stg_results (
    -- Search context / linkage
    raw_id             INTEGER     NOT NULL
        REFERENCES raycon.raw_google_shopping (id),
    keyword            TEXT        NOT NULL,
    page               INTEGER     NOT NULL,
    pulled_at          TIMESTAMPTZ NOT NULL,

    -- Product identifiers
    title              TEXT        NOT NULL,
    product_id         TEXT,                -- SerpAPI / Google product ID if available

    -- Pricing & review metrics
    price              DOUBLE PRECISION,    -- current price
    old_price          DOUBLE PRECISION,    -- the "standard price" (exists during a sale)
    reviews            INTEGER,             -- review count
    rating             DOUBLE PRECISION,    -- average rating (e.g. 4.7)

    -- Merchant / source
    source             TEXT,                -- seller / merchant / marketplace
    multiple_sources   BOOLEAN     NOT NULL DEFAULT FALSE,

    -- Categorization / module metadata
    tag                TEXT,                -- Quite often present as a discount percentage
    module_type        TEXT,                -- Either "all_products" or "categorized"
    module_label       TEXT,                -- e.g. "Waterproof fitness earbuds"
    module_index       INTEGER     NOT NULL,
	block_position     TEXT,       

    -- Position within each module
    position_in_module INTEGER     NOT NULL,

    -- Composite key: unique per product-position within a given search
    PRIMARY KEY (raw_id, module_index, position_in_module)
);


------------------------------------------------
-- Indexes
------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_stg_results_keyword
    ON raycon.stg_results (keyword);

CREATE INDEX IF NOT EXISTS idx_stg_results_title
    ON raycon.stg_results (title);

	