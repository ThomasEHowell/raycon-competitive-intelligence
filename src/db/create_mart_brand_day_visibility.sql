CREATE OR REPLACE VIEW raycon.mart_brand_day_visibility AS
/*
  Mart: Brand × Day Visibility (Raycon-only)

  Purpose:
    Daily competitive visibility metrics derived from Google Shopping results staged in raycon.stg_results.

  Grain:
    One row per (brand, day)

  Notes:
    - Brand classification is rule-based via title substring matching (ILIKE).
    - Multiple matching patterns are resolved deterministically via priority + row_number.
    - "Organic" is defined as non-inline results (module_type != 'inline_products').
*/

WITH brand_patterns AS (
  /*
    Canonical brand pattern dictionary.
    Lower priority = higher precedence when multiple patterns match the same title.
  */
  SELECT 'Raycon' AS brand, 'raycon' AS pattern, 1 AS priority
  UNION ALL SELECT 'Bose', 'bose', 2
  UNION ALL SELECT 'Sony', 'sony', 3
  UNION ALL SELECT 'Soundcore', 'soundcore', 4
  UNION ALL SELECT 'Soundcore', 'anker', 4
  UNION ALL SELECT 'JBL',     'jbl',      5
  UNION ALL SELECT 'Beats',   'beats',    6
  UNION ALL SELECT 'JLab',   'jlab',    7
  UNION ALL SELECT 'Marshall',   'marshall',    8
  UNION ALL SELECT 'Bowers & Wilkins',   'bowers & wilkins',    9
  UNION ALL SELECT 'Apple',   'apple',    10
  UNION ALL SELECT 'Skullcandy',   'skullcandy',    11
  UNION ALL SELECT 'Shokz',   'shokz',    12
  UNION ALL SELECT 'Samsung',   'samsung',    13
  UNION ALL SELECT 'Technics',   'technics',    14
  UNION ALL SELECT 'Cshidworld',   'cshidworld',    15
  UNION ALL SELECT 'Sennheiser',   'sennheiser',    16
  UNION ALL SELECT 'Beyerdynamic',   'beyerdynamic',    17
  UNION ALL SELECT 'Vilinice',   'vilinice',    18
  UNION ALL SELECT 'SiriusXM',   'sirius',    19
  UNION ALL SELECT 'Status Audio',   'status',    20
  UNION ALL SELECT 'Logitech',   'logitech',    21
  UNION ALL SELECT 'HyperX',   'hyperx',    22
  UNION ALL SELECT 'Corsair',   'corsair',    23
  UNION ALL SELECT 'SteelSeries',   'steelseries',    24
  UNION ALL SELECT 'TOZO',   'tozo',    25
  UNION ALL SELECT 'Audio-Technica',   'audio-technica',    26
  UNION ALL SELECT 'Audio-Technica',   'audio technica',    27
  UNION ALL SELECT 'Razer',   'razer',    28
  UNION ALL SELECT 'Onn (Walmart)',   'onn ',    29
  UNION ALL SELECT 'Onn (Walmart)',   'onn.',    30
  UNION ALL SELECT 'Onn (Walmart)',   ' onn',    31
  UNION ALL SELECT 'Tzumi',   'tzumi',    32
  UNION ALL SELECT 'Cowin',   'cowin',    33
  UNION ALL SELECT 'Google',   'google',    34
  UNION ALL SELECT 'Monolith',   'monolith',    35
  UNION ALL SELECT 'Shure',   'shure',    36
  UNION ALL SELECT 'Edifier',   'edifier',    37
  UNION ALL SELECT 'OnePlus',   'oneplus',    38
),

results AS (
  /*
    Canonical row-level input for brand classification.
    One row per product appearance within a search result.
  */
  SELECT
    raw_id,
    module_index,
    position_in_module,
    module_type,
    pulled_at::date AS day,
    title,
    price
  FROM raycon.stg_results
),

matched AS (
  /*
    Join each title to all matching brand patterns.
    row_number() selects the highest-precedence match per result row.
  */
  SELECT
    r.*,
    bp.brand,
    bp.priority,
    ROW_NUMBER() OVER (
      PARTITION BY r.raw_id, r.module_index, r.position_in_module
      ORDER BY bp.priority, bp.brand
    ) AS rn
  FROM results r
  LEFT JOIN brand_patterns bp
    ON r.title ILIKE ('%' || bp.pattern || '%')
),

classified AS (
  /*
    Final row-level classification: exactly one brand per result row.
  */
  SELECT
    COALESCE(brand, 'Other/Unknown') AS brand,
    day,
    price,
    module_type
  FROM matched
  WHERE rn = 1
)

SELECT
  brand,
  day AS date,

  AVG(price) AS avg_price,
  COUNT(*)   AS total_appearances,

  /* Organic = everything except inline (sponsored) module */
  COUNT(*) FILTER (WHERE module_type != 'inline_products') AS appearances_organic,

  COUNT(*) FILTER (WHERE module_type = 'all_products')         AS appearances_uncategorized,
  COUNT(*) FILTER (WHERE module_type = 'categorized_products') AS appearances_categorized,
  COUNT(*) FILTER (WHERE module_type = 'inline_products')      AS appearances_inline_sponsored

FROM classified
GROUP BY brand, day;