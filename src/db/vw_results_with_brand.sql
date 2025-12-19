/*
===============================================================================
View: vw_results_with_brand

Grain:
  One row per product appearance per search result.
  (Derived directly from raycon.stg_results.)

Purpose:
  Assign a deterministic, rule-based brand label to each product result
  using substring matching on product titles.

  This view centralizes brand classification logic so it can be reused
  consistently across downstream marts and dimension tables.

Key design notes:
  - Brand classification is intentionally heuristic and "good enough" for
    competitive-intelligence use cases.
  - When multiple brand patterns match the same title, precedence is resolved
    deterministically using an explicit priority ranking.
  - Unmatched titles are labeled as 'Other/Unknown'.
===============================================================================
*/

CREATE OR REPLACE VIEW raycon.vw_results_with_brand AS

WITH brand_patterns AS (
  /*
    Canonical brand pattern dictionary.

    Each row defines:
      - brand:   canonical brand name
      - pattern: lowercase substring used to identify the brand in product titles
      - priority: explicit precedence ranking (lower = higher priority)

    Design principles:
      - Priorities encode intentional disambiguation (e.g., Raycon before others).
      - Patterns are kept simple and readable rather than exhaustive.
  */
  SELECT 'Raycon' AS brand, 'raycon' AS pattern, 1 AS priority
  UNION ALL SELECT 'Skullcandy',   'skullcandy',    2
  UNION ALL SELECT 'Sony',         'sony',          3
  UNION ALL SELECT 'Soundcore',    'soundcore',     4
  UNION ALL SELECT 'Soundcore',    'anker',         5
  UNION ALL SELECT 'JBL',          'jbl',           6
  UNION ALL SELECT 'Beats',        'beats',         7
  UNION ALL SELECT 'JLab',         'jlab',           8
  UNION ALL SELECT 'Marshall',     'marshall',      9
  UNION ALL SELECT 'Bowers & Wilkins', 'bowers & wilkins', 10
  UNION ALL SELECT 'Apple',        'apple',        11
  UNION ALL SELECT 'Bose',         'bose',         12
  UNION ALL SELECT 'Shokz',        'shokz',         13
  UNION ALL SELECT 'Samsung',      'samsung',      14
  UNION ALL SELECT 'Technics',     'technics',     15
  UNION ALL SELECT 'Cshidworld',   'cshidworld',   16
  UNION ALL SELECT 'Sennheiser',   'sennheiser',   17
  UNION ALL SELECT 'Beyerdynamic', 'beyerdynamic', 18
  UNION ALL SELECT 'Vilinice',     'vilinice',     19
  UNION ALL SELECT 'SiriusXM',     'sirius',       20
  UNION ALL SELECT 'Status Audio', 'status',       21
  UNION ALL SELECT 'Logitech',     'logitech',     22
  UNION ALL SELECT 'HyperX',       'hyperx',       23
  UNION ALL SELECT 'Corsair',      'corsair',      24
  UNION ALL SELECT 'SteelSeries',  'steelseries',  25
  UNION ALL SELECT 'TOZO',         'tozo',         26
  UNION ALL SELECT 'Audio-Technica','audio-technica',27
  UNION ALL SELECT 'Audio-Technica','audio technica',28
  UNION ALL SELECT 'Razer',        'razer',        29
  UNION ALL SELECT 'Onn (Walmart)','onn ',         30
  UNION ALL SELECT 'Onn (Walmart)','onn.',         31
  UNION ALL SELECT 'Onn (Walmart)',' onn',         32
  UNION ALL SELECT 'Tzumi',        'tzumi',        33
  UNION ALL SELECT 'Cowin',        'cowin',        34
  UNION ALL SELECT 'Google',       'google',       35
  UNION ALL SELECT 'Monolith',     'monolith',     36
  UNION ALL SELECT 'Shure',        'shure',        37
  UNION ALL SELECT 'Edifier',      'edifier',      38
  UNION ALL SELECT 'OnePlus',      'oneplus',      39
  UNION ALL SELECT 'Audeze',      'audeze',        40
  UNION ALL SELECT 'iLive',      'ilive',          41
  UNION ALL SELECT 'Focal',      'focal',          42
  UNION ALL SELECT 'Hifiman',      'hifiman',      43
),

matches AS (
  /*
    Join each staged product result to all matching brand patterns
    based on substring matches against the product title.

    A product title may match multiple patterns; this is resolved
    deterministically using ROW_NUMBER() in the next step.
  */
  SELECT
    r.raw_id,
    r.keyword,
    r.page,
    r.pulled_at,
    r.title,
    r.product_id,
    r.price,
    r.old_price,
    r.module_type,
    r.module_label,
    r.module_index,
    r.block_position,
    r.position_in_module,

    bp.brand,
    bp.priority,

    ROW_NUMBER() OVER (
      PARTITION BY r.raw_id, r.module_index, r.position_in_module
      ORDER BY
        bp.priority,
        LENGTH(bp.pattern) DESC,
        bp.brand
    ) AS rn
  FROM raycon.stg_results r
  LEFT JOIN brand_patterns bp
    ON r.title ILIKE ('%' || bp.pattern || '%')
),

resolved AS (
  /*
    Select the single highest-priority brand match per product appearance.
    The ORDER BY clause in ROW_NUMBER() guarantees deterministic resolution.
  */
  SELECT *
  FROM matches
  WHERE rn = 1
),

classified AS (
  /*
    Final classification layer.

    Products with no matching brand patterns are labeled as 'Other/Unknown'.
    All original row-level detail is preserved.
  */
  SELECT
    raw_id,
    keyword,
    page,
    pulled_at,
    title,
    product_id,
    price,
    old_price,
    module_type,
    module_label,
    module_index,
    block_position,
    position_in_module,
    COALESCE(brand, 'Other/Unknown') AS brand
  FROM resolved
)

SELECT * FROM classified;