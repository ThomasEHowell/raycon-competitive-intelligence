-- src/db/schema_raw.sql


-- Ensure the project schema exists
CREATE SCHEMA IF NOT EXISTS raycon;

-- ============================================
-- Raw Table: raw_google_shopping
-- One row per Google Shopping keyword search
-- ============================================
-- Raw table storing full SerpAPI JSON responses
CREATE TABLE IF NOT EXISTS raycon.raw_google_shopping (
 id				BIGSERIAL PRIMARY KEY,
 pulled at		TIMESTAMPTZ NOT NULL,
 keyword 		TEXT NOT NULL,
 page 			INT NOT NULL,
 response_json	JSONB NOT NULL
);

