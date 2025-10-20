# clients_daily_v6

## Overview
Daily aggregated Firefox desktop telemetry providing comprehensive client behavior, configuration, and engagement metrics. This table consolidates multiple main pings per client per day into a single row, enabling efficient daily cohort analysis and longitudinal studies.

## Source
**Base Table:** `telemetry_stable.main_v5`
**Aggregation Level:** Client-day (one row per client_id per submission_date)
**Update Frequency:** Daily

## Key Features
- **Daily Aggregation:** Multiple pings aggregated per client per day
- **Comprehensive Metrics:** 360+ columns covering usage, performance, system specs, and searches
- **Partitioned by Date:** Optimized for date-range queries via submission_date
- **Client Filtering:** Excludes overactive clients (>150K pings/day)

## Primary Use Cases
1. Daily Active Users (DAU) and engagement analysis
2. Feature adoption and A/B test evaluation
3. Browser performance and stability monitoring
4. Search behavior and revenue analysis
5. Hardware/OS distribution studies

## Important Columns
- **submission_date, client_id:** Primary identifiers
- **active_hours_sum:** Browser usage intensity
- **search_counts:** Detailed search activity by engine/source
- **scalar_parent_browser_engagement_*:** User engagement signals
- **country, locale, os:** Geographic and platform dimensions

## Sample Query
```sql
SELECT 
  submission_date,
  COUNT(DISTINCT client_id) AS dau,
  AVG(active_hours_sum) AS avg_hours
FROM `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v6`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND normalized_channel = 'release'
GROUP BY submission_date
ORDER BY submission_date DESC
```

## Notes
- Mode_last aggregation prefers most recent values for dimensions
- Excludes clients with excessive ping volume
- Contains both deprecated and active metrics
- Search metrics differentiate SAP, organic, and follow-on searches