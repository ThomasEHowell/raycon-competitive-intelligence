/*
  View: raycon.build_mart_brand_day_visibility

  Grain:
    One row per (brand × day).

  Purpose:
    Daily brand-level Google Shopping visibility metrics for competitive
    intelligence dashboards.

    This mart summarizes product appearance counts and pricing signals,
    enabling analysis of:
      - Brand visibility over time
      - Organic vs inline-sponsored presence
      - Categorized vs uncategorized module exposure

  Data source:
    raycon.vw_results_with_brand

    All brand classification logic is centralized in the helper view.
    This mart performs aggregation only.

  Modeling notes (MVP decisions — intentional):
    - No date spine or gap filling:
        Brands with zero appearances on a given day do not appear.
    - "Organic" is defined as any non-inline module.
    - Inline products are treated as sponsored for CI purposes.
    - Metrics reflect observed Google Shopping results only and evolve
      as data accrues.
*/

CREATE OR REPLACE VIEW raycon.mart_brand_day_visibility AS
WITH base AS (
  SELECT
    pulled_at::date AS day,
    brand,
    price,
    module_type,
    module_label
  FROM raycon.vw_results_with_brand
)

SELECT
  brand,
  day AS date,

  -- brand's average pricing for each day
  AVG(price) AS avg_price,

  -- brand's total visibility each the day
  COUNT(*) AS total_appearances,

  -- organic vs sponsored split
  COUNT(*) FILTER (
    WHERE module_type != 'inline_products'
  ) AS appearances_organic,

  -- module-level breakdown
  COUNT(*) FILTER (
    WHERE module_type = 'all_products'
  ) AS appearances_uncategorized,

  COUNT(*) FILTER (
    WHERE module_type = 'categorized_products'
  ) AS appearances_categorized,

  COUNT(*) FILTER (
    WHERE module_type = 'inline_products'
  ) AS appearances_inline_sponsored

FROM base
GROUP BY
  brand,day;