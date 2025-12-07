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
- Transform and normalize the data into staging tables
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
**Source:**
SerpAPI → Google Shopping engine

**Frequency:**
Daily pulls (~7 keywords per day)

**Raw Data:**
Each API response includes:
**To be explored in the staging process**

## 3. Dataset Overview
Raw JSON structure explored and documented in `02_parse_raw.ipynb`.```

## 4. Major Project Steps
1. Ingest raw Google Shopping API payloads (`01_ingest_raw.ipynb`)
2. Explore & parse raw JSON; design and prototype staging transformations (`02_parse_raw.ipynb`)
3. Create staging tables (SQL DDL)


## 5. Project Structure
```
raycon-competitive-intel/
│
├── data/
│   └── samples/
│       └── google_shopping_example.json      # Sample raw API payload
│
├── notebooks/
│   ├── 01_ingest_raw.ipynb           # API pull + raw ingestion
│   └── 02_parse_raw.ipynb            # JSON exploration + staging design + prototype transforms
│
├── src/
│   ├── db/
│   │   └── schema_raw.sql                    # Raw table DDL
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

### Steps
1. Create the raw schema via `src/db/schema_raw.sql`
2. Add your database credentials and your SerpAPI key to your .env file
3. Run the ingestion notebook:
- Loads config
- Pulls Google Shopping results
- Inserts raw JSON into Postgres
- Saves/updates the reference sample JSON

## 7. Conclusion