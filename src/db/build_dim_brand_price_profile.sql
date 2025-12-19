/*
  View: raycon.build_dim_brand_price_profile

  Type:
    Derived / dynamic dimension VIEW (recomputes as data accrues).

  Grain:
    One row per brand.

  Purpose:
    Brand-level price context to support competitive-intelligence analysis in Tableau,
    so price-band questions (e.g., "does Brand X overlap Raycon's band?") do not
    require querying staging tables.

  Data source:
    raycon.vw_results_with_brand

  Modeling notes (MVP decisions — intentional):
    - Excludes brand = 'Other/Unknown' (heterogeneous long-tail bucket; not a coherent entity).
    - Includes Raycon as its own row.
    - Uses observed prices only (price IS NOT NULL).
        * This filter is defensive; as of now, all observed appearances are priced.
    - Counts and price profiles are based on observed product appearances
      within the current dataset window.
    - Price-band overlap is based on observed min/max ranges (existence-based competition).
    - This view is data-dependent and will evolve as historical depth increases.
*/

CREATE OR REPLACE VIEW raycon.dim_brand_price_profile AS
WITH priced_results AS (
  SELECT
    r.brand,
    r.pulled_at::date AS day,
    r.price
  FROM raycon.vw_results_with_brand r
  WHERE r.brand <> 'Other/Unknown'
    AND r.price IS NOT NULL
),

brand_price_profile AS (
  SELECT
    pr.brand,

    -- coverage / context
    COUNT(*) AS total_appearances,
    COUNT(DISTINCT pr.day) AS active_days_priced,

    -- observed price profile
    MIN(pr.price) AS min_price_observed,
    MAX(pr.price) AS max_price_observed,
    AVG(pr.price) AS avg_price_observed,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY pr.price) AS median_price_observed

  FROM priced_results pr
  GROUP BY pr.brand
),

raycon_band AS (
  SELECT
    MIN(pr.price) AS raycon_min_price_observed,
    MAX(pr.price) AS raycon_max_price_observed
  FROM priced_results pr
  WHERE pr.brand = 'Raycon'
)

SELECT
  bpp.brand,

  -- coverage / context
  bpp.total_appearances,
  bpp.active_days_priced,

  -- price profile
  bpp.min_price_observed,
  bpp.max_price_observed,
  bpp.avg_price_observed,
  bpp.median_price_observed,

  -- Raycon observed band (constant across rows; useful for Tableau/debugging)
  rb.raycon_min_price_observed,
  rb.raycon_max_price_observed,

  /*
    Overlap definition:
      - 1 if the brand’s observed price range intersects Raycon’s observed range
      - 0 if entirely below or entirely above
      - NULL if Raycon band is unavailable (should be rare if Raycon exists in data)
  */
  CASE
    WHEN rb.raycon_min_price_observed IS NULL
      OR rb.raycon_max_price_observed IS NULL
      THEN NULL
    WHEN bpp.max_price_observed < rb.raycon_min_price_observed THEN 0
    WHEN bpp.min_price_observed > rb.raycon_max_price_observed THEN 0
    ELSE 1
  END AS overlaps_raycon_band,

  /*
    Coarse relationship label for filtering / storytelling in Tableau.
  */
  CASE
    WHEN rb.raycon_min_price_observed IS NULL
      OR rb.raycon_max_price_observed IS NULL
      THEN 'unknown'
    WHEN bpp.max_price_observed < rb.raycon_min_price_observed THEN 'below_raycon_band'
    WHEN bpp.min_price_observed > rb.raycon_max_price_observed THEN 'above_raycon_band'
    ELSE 'overlaps_raycon_band'
  END AS raycon_band_relationship

FROM brand_price_profile bpp
CROSS JOIN raycon_band rb
ORDER BY
  overlaps_raycon_band DESC NULLS LAST,
  bpp.total_appearances DESC,
  bpp.brand;