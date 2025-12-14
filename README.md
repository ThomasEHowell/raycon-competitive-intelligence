# Raycon Competitive Intelligence: Google Shopping Visibility & Pricing Analytics

## 1. Project Scope
**Target Audience:**
A DTC-first audio brand (Raycon) seeking to improve its digital visibility and competitiveness in Google Shopping search results.

**Client Scenario:**
This project simulates a consulting engagement with Raycon, a DTC-first audio brand. Raycon has not hired me and this project is not affiliated with Raycon; this is a fictional business case to demonstrate competitive intelligence workflows using real Google Shopping data.

**Business Problem:**
Raycon competes in crowded, high-intent keyword categories such as wireless earbuds, noise-cancelling earbuds, and budget headphones. Because Raycon earns significantly higher margins from customers who buy through its own website rather than through Amazon or retail partners, improving Google Shopping visibility is strategically important.
However, Raycon lacks clear visibility into:
- How often its products appear in Google Shopping search results
- How its rankings compare against competitors
- How pricing and seller dynamics influence placement
- Whether visibility is improving or declining over time

**Objectives:**
This project aims to build a data pipeline and competitive-intelligence analytics system that will:
- Pull daily Google Shopping results for 7 high importance keywords
- Store the raw API payloads in a PostgreSQL raw table
- Transform and flatten the data into staging tables
- Generate visibility and pricing metrics in analytic mart tables
- Produce insights and recommendations based on trends

**Business Value:**
By understanding visibility patterns, pricing pressures, and competitor dominance, Raycon can:
- Improve high-margin DTC acquisition
- Reduce dependence on Amazon marketplace fees
- Identify keywords where sponsored or organic presence is weak
- Benchmark their position against major competitor
- Make data-driven marketing and pricing decisions

**Deliverables:** 
- Automated Google Shopping API data pulls
- PostgreSQL database with raw → staging → mart layers
- Daily visibility and pricing metrics
- Competitor visibility share
- Trend analysis over time
- Clear insights and potential recommendations based on observed patterns

## 2. Results Overview
**Source:** SerpAPI (Google Shopping engine)  
**Cadence:** Daily (7 keywords/day)  
**Storage layers:**
- Raw: full JSON payload per keyword search
- Staging: relational tables at search-level and product-level grain

**Key complexity handled in staging:**
Google Shopping responses include variable result modules (e.g., standard results, categorized modules, and occasional inline/sponsored blocks). The staging logic safely handles missing/optional modules without breaking.

## 3. Dataset Overview
Raw JSON structure explored and documented in `02_parse_raw.ipynb`.

## 4. Major Project Steps
1. Create raw and staging tables via SQL DDL
1. Ingest raw Google Shopping API payloads (`01_ingest_raw.ipynb`)
3. Explore & parse raw JSON; design and prototype staging transformations (`02_parse_raw.ipynb`)
4. Transform raw JSON into structured staging tables (`03_stage_unprocessed_raw.ipynb`)
5. Future analytical and reporting layers


## 5. Project Structure
```
raycon-competitive-intel/
│
├── data/
│   └── samples/
│       └── google_shopping_example.json      # Sample raw API payload
│
├── notebooks/
│   ├── 01_ingest_raw.ipynb               # API pull + raw ingestion
│   ├── 02_parse_raw.ipynb                # JSON exploration + staging design + prototype transforms
│   └── 03_stage_unprocessed_raw.ipynb    # Stage unprocessed raw searches into schema-aligned staging tables
│
├── src/
│   └── db/
│       ├── schema_raw.sql                    # Raw table DDL
│       └── create_staging_tables.sql         # Staging tables DDL
│
├── README.md
├── .env (not committed)
└── requirements.txt
```
## 6. How to Recreate This Project

### Prerequisites
- Python 3.9+
- PostgreSQL
- SerpAPI key
- Libraries installation:
`pip install -r requirements.txt`

## Setup & Execution Steps

1. Create database schemas and tables
   - Run `src/db/schema_raw.sql` to create the raw schema
   - Run `src/db/schema_staging.sql` to create staging tables

2. Configure environment variables
   - Add PostgreSQL credentials to `.env`
   - Add your SerpAPI key (`SERPAPI_API_KEY`)

3. Run raw data ingestion
   - Execute `01_ingest_raw.ipynb`
   - Pulls Google Shopping results via SerpAPI
   - Inserts full JSON responses into the raw PostgreSQL table
   - Updates the reference sample JSON used for development

4. Parse and inspect raw JSON structure
   - Execute `02_parse_raw.ipynb`
   - Explore result modules and validate parsing logic

5. Stage unprocessed raw searches
   - Execute `03_stage_unprocessed_raw.ipynb`
   - Identifies raw searches not yet staged
   - Transforms JSON into structured staging tables
   - Appends results within a single database transaction

## 7. Conclusion

This project demonstrates an end-to-end data pipeline for competitive intelligence using real Google Shopping data, with a focus on robust ingestion, raw data preservation, and repeatable staging transformations. The resulting dataset provides a foundation for downstream visibility, pricing, and trend analysis.