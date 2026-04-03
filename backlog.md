# Raycon Competitive Intelligence – Backlog
> For deferred work, known issues, and future improvements

# Current Focus (Greater Pipeline Reliability)
- [x] Add try-except in case of errors (hard fails) for logging
- [ ] Add logging for run_daily.py
- [ ] Consider moving logging into a database table
- [ ] Create a loud failure mechanism in the case of pipeline failure


## Known Issues
- Data quality checks could be more comprehensive

## Future Improvements
- Add more complex pricing semantic logic to dim_brand_price_profile.sql (quantiles and derived logic)
- Add data quality checks (row counts, null checks)
- Port over to AWS