-- vw_raw_non_canonical_daily
--
-- Returns raw_google_shopping IDs that are NOT the most recent successful
-- keyword search for a given keyword on a given day.
--
-- A raw row is considered non-canonical if a later same-day pull exists.
-- Used to clean up staging tables (stg_searches, stg_results) so they only
-- reflect the latest successful search per (keyword, day).

CREATE OR REPLACE VIEW raycon.vw_raw_non_canonical_daily AS
WITH recency AS (
  SELECT
    id,
    keyword,
    pulled_at,
    ROW_NUMBER() OVER (
      PARTITION BY keyword, CAST(pulled_at AS date)
      ORDER BY pulled_at DESC, id DESC
    ) AS rn
  FROM raycon.raw_google_shopping
  WHERE status = 'success'
)
SELECT id, keyword, pulled_at
FROM recency
WHERE rn > 1
ORDER BY id;