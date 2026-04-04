# Raycon Competitive Intelligence – Backlog
> For deferred work, known issues, and future improvements

# Current Focus (Greater Pipeline Reliability)
- [x] Add try-except in case of errors (hard fails) for logging
- [x] Add logging for run_daily.py
- [x] Create a loud failure mechanism (email alert) in the case of pipeline failure
- [ ] Create user-optionality to enable or disable email alerts on failure
- [ ] Consider moving logging into a database table


## Known Issues
- Data quality checks could be more comprehensive

## Future Improvements
- Add more complex pricing semantic logic to dim_brand_price_profile.sql (quantiles and derived logic)
- Add data quality checks (row counts, null checks)
- Port over to AWS