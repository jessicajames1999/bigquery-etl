# Baseline Active Users Aggregates v2

## Overview

The `baseline_active_users_aggregates_v2` table provides daily aggregated metrics of Firefox Desktop active users derived from baseline telemetry pings. This table serves as a multi-dimensional analytical cube for analyzing user populations across various segments including geographic location, operating system, application version, distribution channels, and user behavior patterns.

This aggregate table is optimized for efficient querying and reporting on Firefox Desktop user metrics without the need to scan the underlying raw baseline ping data.

## Table Details

- **Dataset**: `moz-fx-data-shared-prod.firefox_desktop_derived`
- **Table**: `baseline_active_users_aggregates_v2`
- **Type**: Incremental aggregate table
- **Owners**: kwindau@mozilla.com, ago@mozilla.com
- **DAG**: `bqetl_analytics_aggregations`

## Data Sources

### Primary Source
- **Table**: `moz-fx-data-shared-prod.firefox_desktop.baseline_active_users`
- **Type**: User-level baseline ping data with activity flags

### ETL Logic
The table aggregates user-level data by:
1. Grouping by all dimensional attributes (channel, country, OS, version, etc.)
2. Counting users based on activity flags for different time windows
3. Distinguishing between ping-based metrics (users who sent pings) and activity-based metrics (users with actual browsing activity)

## Schema

The table contains 30 columns organized into the following categories:

### Temporal Dimensions
- `submission_date` - Date pings were received (partition key, required in queries)
- `first_seen_year` - Year when user first sent a ping (for cohort analysis)

### Distribution and Channel
- `channel` - Release channel (release, beta, nightly, esr)
- `app_name` - Application name (Firefox Desktop variants)
- `distribution_id` - Distribution variant identifier

### Geographic
- `country` - ISO country code from IP geolocation (clustering key)
- `city` - City name from geolocation
- `locale` - Language and regional settings

### Operating System
- `os` - Normalized OS name
- `os_grouped` - OS category grouping
- `os_version` - Full OS version string
- `os_version_major` - Major OS version number
- `os_version_minor` - Minor OS version number
- `os_version_build` - OS build identifier
- `windows_build_number` - Windows-specific build number

### Application Version
- `app_version` - Full Firefox version string
- `app_version_major` - Major version number
- `app_version_minor` - Minor version number
- `app_version_patch_revision` - Patch/revision number
- `app_version_is_major_release` - Boolean flag for major releases

### User Behavior and Attribution
- `is_default_browser` - Whether Firefox is the default browser
- `activity_segment` - User engagement classification
- `attribution_medium` - Marketing medium attribution
- `attribution_source` - Install source attribution

### User Count Metrics

**Ping-Based Metrics** (users who sent pings):
- `daily_users` - Users who sent pings on submission_date
- `weekly_users` - Users who sent pings in the last 7 days
- `monthly_users` - Users who sent pings in the last 28 days

**Activity-Based Metrics** (users with actual browsing activity):
- `dau` - Daily Active Users (activity on submission_date)
- `wau` - Weekly Active Users (activity in last 7 days)
- `mau` - Monthly Active Users (activity in last 28 days)

## Update Schedule

- **Frequency**: Daily
- **Update Type**: Incremental
- **DAG**: `bqetl_analytics_aggregations`
- **Partition**: By `submission_date` (day)
- **Partition Filter**: Required for all queries
- **Clustering**: By `app_name`, `channel`, `country`

## Key Differences: Users vs. Active Users

This table provides two parallel sets of metrics:

1. **Ping-Based Metrics** (`daily_users`, `weekly_users`, `monthly_users`):
   - Count users who sent baseline pings within the time window
   - Represents ping submission behavior
   - May include users without active browsing

2. **Activity-Based Metrics** (`dau`, `wau`, `mau`):
   - Count users who had actual browsing activity
   - Represents genuine user engagement
   - The primary metrics for measuring active usage

For most analytical purposes, use the activity-based metrics (dau, wau, mau) as they reflect genuine user engagement.

## Usage Examples

### Example 1: Daily Active Users by Country and Channel
```sql
SELECT
  submission_date,
  country,
  channel,
  SUM(dau) AS total_dau,
  SUM(mau) AS total_mau,
  SAFE_DIVIDE(SUM(dau), SUM(mau)) AS dau_mau_ratio
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date = '2024-01-15'
  AND country IN ('US', 'DE', 'FR', 'GB')
GROUP BY
  submission_date,
  country,
  channel
ORDER BY
  country,
  channel;
```

### Example 2: Version Adoption Analysis
```sql
SELECT
  submission_date,
  app_version_major,
  channel,
  SUM(dau) AS daily_active_users,
  SUM(mau) AS monthly_active_users
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date BETWEEN '2024-01-01' AND '2024-01-31'
  AND channel = 'release'
GROUP BY
  submission_date,
  app_version_major,
  channel
ORDER BY
  submission_date,
  app_version_major;
```

### Example 3: Default Browser Status Analysis
```sql
SELECT
  submission_date,
  is_default_browser,
  SUM(dau) AS daily_active_users,
  SUM(mau) AS monthly_active_users,
  SAFE_DIVIDE(SUM(dau), SUM(mau)) AS engagement_ratio
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date = '2024-01-15'
  AND is_default_browser IS NOT NULL
GROUP BY
  submission_date,
  is_default_browser;
```

### Example 4: Operating System Distribution
```sql
SELECT
  submission_date,
  os,
  os_version_major,
  SUM(dau) AS daily_active_users,
  ROUND(SUM(dau) * 100.0 / SUM(SUM(dau)) OVER (PARTITION BY submission_date), 2) AS percentage
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date = '2024-01-15'
  AND os IS NOT NULL
GROUP BY
  submission_date,
  os,
  os_version_major
ORDER BY
  daily_active_users DESC;
```

### Example 5: Attribution Source Analysis
```sql
SELECT
  first_seen_year,
  attribution_source,
  attribution_medium,
  SUM(mau) AS monthly_active_users
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date = '2024-01-15'
  AND attribution_source IS NOT NULL
  AND first_seen_year >= 2023
GROUP BY
  first_seen_year,
  attribution_source,
  attribution_medium
ORDER BY
  first_seen_year,
  monthly_active_users DESC;
```

### Example 6: Activity Segment Analysis
```sql
SELECT
  submission_date,
  activity_segment,
  SUM(dau) AS daily_active_users,
  SUM(wau) AS weekly_active_users,
  SUM(mau) AS monthly_active_users,
  SAFE_DIVIDE(SUM(dau), SUM(wau)) AS daily_weekly_ratio,
  SAFE_DIVIDE(SUM(wau), SUM(mau)) AS weekly_monthly_ratio
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date = '2024-01-15'
  AND activity_segment IS NOT NULL
GROUP BY
  submission_date,
  activity_segment
ORDER BY
  daily_active_users DESC;
```

## Query Performance Tips

1. **Always include partition filter**: The table requires a filter on `submission_date` in the WHERE clause
2. **Use clustering keys**: Filter on `app_name`, `channel`, or `country` for optimal performance
3. **Aggregate efficiently**: The table is already aggregated, so further aggregation is lightweight
4. **Avoid full table scans**: Use specific date ranges rather than unbounded queries
5. **Leverage pre-computed metrics**: Use the aggregate counts rather than recalculating from raw data

## Related Tables

- **Source Table**: `moz-fx-data-shared-prod.firefox_desktop.baseline_active_users` - User-level baseline ping data
- **Similar Tables**:
  - `firefox_desktop_derived.clients_daily_v6` - Daily client-level aggregations from main pings
  - `telemetry_derived.clients_last_seen_v1` - Last seen information for clients
  - `firefox_desktop_derived.active_users_aggregates` - Similar aggregates from main pings

## Notes

- **Partition Requirement**: Always include `submission_date` filter to avoid full table scans
- **NULL Handling**: Geographic fields use "??" for unknown countries; other fields may be NULL
- **Time Windows**:
  - Weekly = 7 days
  - Monthly = 28 days (not calendar month)
- **Activity vs. Ping Metrics**: Use activity-based metrics (dau, wau, mau) for engagement analysis
- **Data Freshness**: Updated daily by the analytics aggregations DAG
- **Historical Data**: Available from the table's creation date forward
- **China Market**: MozillaOnline clients have distribution_id appended to app_name

## Questions or Issues?

For questions about this table or to report issues:
- Contact the owners: kwindau@mozilla.com, ago@mozilla.com
- File an issue in the [bigquery-etl repository](https://github.com/mozilla/bigquery-etl)
- Check the [Mozilla Data Documentation](https://docs.telemetry.mozilla.org/)
