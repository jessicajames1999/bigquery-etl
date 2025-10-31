# Baseline Active Users Aggregates V2

## Overview

The `baseline_active_users_aggregates_v2` table provides daily aggregated counts of Firefox Desktop active users across multiple dimensions. This table enables efficient analysis of user populations without requiring complex joins or aggregations on raw telemetry data.

**Key Features:**
- Pre-aggregated daily, weekly, and monthly user counts
- Both submission-based and activity-based metrics
- 24 dimensional breakdowns including geography, OS, app version, and user segments
- Optimized for fast querying with partitioning and clustering

## Table Details

- **Dataset**: `moz-fx-data-shared-prod.firefox_desktop_derived`
- **Table**: `baseline_active_users_aggregates_v2`
- **Type**: Incremental aggregate table
- **Update Schedule**: Daily via `bqetl_analytics_aggregations` DAG
- **Owners**: kwindau@mozilla.com, ago@mozilla.com

## Schema

### Temporal Dimensions
| Column | Type | Description |
|--------|------|-------------|
| submission_date | DATE | Server-side ping receipt date (partition key) |
| first_seen_year | INTEGER | Year of first ping (for cohort analysis) |

### Application & Distribution
| Column | Type | Description |
|--------|------|-------------|
| channel | STRING | Release channel (release, beta, nightly, esr) |
| app_name | STRING | Application identifier with distribution variants |
| app_version | STRING | Full semantic version (e.g., "123.0.1") |
| app_version_major | NUMERIC | Major version number |
| app_version_minor | NUMERIC | Minor version number |
| app_version_patch_revision | NUMERIC | Patch version number |
| app_version_is_major_release | BOOLEAN | Flag for major releases |
| distribution_id | STRING | Partner/distribution identifier |

### Geographic Dimensions
| Column | Type | Description |
|--------|------|-------------|
| country | STRING | ISO country code from IP geolocation |
| city | STRING | City name from geolocation |
| locale | STRING | User interface language/region setting |

### Operating System
| Column | Type | Description |
|--------|------|-------------|
| os | STRING | Normalized OS name |
| os_grouped | STRING | OS grouping for analysis |
| os_version | STRING | Full OS version string |
| os_version_major | INTEGER | Major OS version |
| os_version_minor | INTEGER | Minor OS version |
| os_version_build | STRING | OS build number |
| windows_build_number | INTEGER | Windows-specific build (Windows only) |

### Browser Configuration
| Column | Type | Description |
|--------|------|-------------|
| is_default_browser | BOOLEAN | Whether Firefox is default browser |

### User Segmentation
| Column | Type | Description |
|--------|------|-------------|
| activity_segment | STRING | User activity classification |
| attribution_medium | STRING | Marketing acquisition medium |
| attribution_source | STRING | Specific acquisition source |

### Aggregated Metrics

**Submission-Based Counts** (users who sent pings):
| Column | Type | Description |
|--------|------|-------------|
| daily_users | INTEGER | Users submitting pings on submission_date |
| weekly_users | INTEGER | Users submitting pings in past 7 days |
| monthly_users | INTEGER | Users submitting pings in past 28 days |

**Activity-Based Counts** (users with actual browsing activity):
| Column | Type | Description |
|--------|------|-------------|
| dau | INTEGER | Daily Active Users with browsing activity |
| wau | INTEGER | Weekly Active Users with browsing activity |
| mau | INTEGER | Monthly Active Users with browsing activity |

## Data Sources

**Primary Source**: `moz-fx-data-shared-prod.firefox_desktop.baseline_active_users`

The table aggregates data using COUNTIF operations on boolean flags:
- `is_daily_user`, `is_weekly_user`, `is_monthly_user` → submission-based counts
- `is_dau`, `is_wau`, `is_mau` → activity-based counts

## Update Schedule

- **Frequency**: Daily
- **DAG**: `bqetl_analytics_aggregations`
- **Incremental**: Yes, updates one day at a time
- **Data Availability**: Typically available by 6 AM UTC for the previous day

## Query Optimization

### Required Partition Filter
This table requires a partition filter on `submission_date`. Always include a WHERE clause:

```sql
WHERE submission_date >= '2024-01-01'
```

### Clustering
The table is clustered by `app_name`, `channel`, and `country`. Queries filtering on these fields will be most efficient.

## Usage Examples

### Example 1: Daily Active Users by Country (Last 7 Days)
```sql
SELECT
  submission_date,
  country,
  SUM(dau) AS total_dau
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date >= CURRENT_DATE() - 7
  AND channel = 'release'
GROUP BY
  submission_date,
  country
ORDER BY
  submission_date DESC,
  total_dau DESC
```

### Example 2: Monthly Active Users Trend by Channel
```sql
SELECT
  submission_date,
  channel,
  SUM(mau) AS total_mau
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date >= '2024-01-01'
GROUP BY
  submission_date,
  channel
ORDER BY
  submission_date,
  channel
```

### Example 3: Default Browser Penetration
```sql
SELECT
  submission_date,
  country,
  SUM(CASE WHEN is_default_browser THEN dau ELSE 0 END) AS default_browser_users,
  SUM(dau) AS total_users,
  SAFE_DIVIDE(
    SUM(CASE WHEN is_default_browser THEN dau ELSE 0 END),
    SUM(dau)
  ) * 100 AS default_browser_percentage
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date = CURRENT_DATE() - 1
  AND channel = 'release'
GROUP BY
  submission_date,
  country
ORDER BY
  total_users DESC
LIMIT 10
```

### Example 4: User Activity Segmentation Analysis
```sql
SELECT
  activity_segment,
  SUM(dau) AS active_users,
  ROUND(SUM(dau) * 100.0 / SUM(SUM(dau)) OVER (), 2) AS percentage
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date = CURRENT_DATE() - 1
  AND channel = 'release'
GROUP BY
  activity_segment
ORDER BY
  active_users DESC
```

### Example 5: Cohort Retention - First Seen Year Analysis
```sql
SELECT
  first_seen_year,
  submission_date,
  SUM(mau) AS monthly_active_users
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date >= '2024-01-01'
  AND channel = 'release'
  AND first_seen_year >= 2020
GROUP BY
  first_seen_year,
  submission_date
ORDER BY
  first_seen_year,
  submission_date
```

### Example 6: Operating System Distribution
```sql
SELECT
  os,
  os_version_major,
  SUM(dau) AS daily_active_users
FROM
  `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE
  submission_date = CURRENT_DATE() - 1
  AND channel = 'release'
GROUP BY
  os,
  os_version_major
ORDER BY
  daily_active_users DESC
```

## Metrics Comparison

### Submission-Based vs Activity-Based Metrics

| Metric Type | Measures | Use Case |
|-------------|----------|----------|
| **daily_users/weekly_users/monthly_users** | Users who sent pings | Total reach, installation base |
| **dau/wau/mau** | Users with actual browsing activity | Engagement, genuine usage |

**Key Insight**: Activity-based metrics (dau/wau/mau) are typically lower than submission-based metrics because they require evidence of actual browser usage beyond just opening Firefox.

## Related Tables

- **Source**: `moz-fx-data-shared-prod.firefox_desktop.baseline_active_users` - Source table with client-level data
- **Alternative**: `moz-fx-data-shared-prod.telemetry.clients_daily` - Legacy telemetry-based active users table
- **Related**: `moz-fx-data-shared-prod.firefox_desktop.baseline_clients_daily` - Daily client-level baseline metrics

## Notes

1. **Partition Filter Required**: All queries must include a filter on `submission_date` to avoid full table scans.

2. **Metric Interpretation**: Use activity-based metrics (dau/wau/mau) for measuring genuine engagement. Use submission-based metrics (daily_users/weekly_users/monthly_users) for measuring installation reach.

3. **Clustering Optimization**: Filter on `app_name`, `channel`, and `country` early in WHERE clauses for best query performance.

4. **NULL Handling**: Some dimension fields may be NULL, particularly for older data or clients that don't report certain metrics. Use `COALESCE` or `IFNULL` when necessary.

5. **Geographic Data**: Country code '??' indicates unknown or unresolvable geolocation.

6. **Time Windows**: 
   - Weekly metrics use 7-day rolling windows
   - Monthly metrics use 28-day rolling windows (not calendar months)

7. **Data Freshness**: Data for date D is typically available by 6 AM UTC on D+1.

## Questions or Issues?

Contact the table owners:
- kwindau@mozilla.com
- ago@mozilla.com
