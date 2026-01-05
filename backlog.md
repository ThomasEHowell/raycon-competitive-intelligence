# Raycon Competitive Intelligence – Backlog
> For deferred work, known issues, and future improvements

## Current Focus (Pipeline Reliability)
- [x] Idempotency
- [x] Robustness
- [x] Logging (log each pull, log error payloads for debugging, log staging)
- [ ] Refactoring (include logging robustness update ready for hard fails too)
- [ ] Scheduled Local Automation

## Engineering Work
- Add ingestion retries + exponential backoff
- Handle SerpAPI error responses without deleting raw
- Make ingestion idempotent across re-pulls
- Add scheduling for API requests

## Known Issues
- Raw error batch temporarily quarantined during MVP build
- No data quality checks yet
- Staging notebook assumes shopping_results exists for all keyword searches

## Future Improvements
- Add more complex pricing semantic logic to dim_brand_price_profile.sql (quantiles and derived logic)
- Add automated re-pull for failed keywords
- Add data quality checks (row counts, null checks)
- Port over to AWS