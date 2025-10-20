# Baseline Active Users Aggregates v2

## Overview

The `baseline_active_users_aggregates_v2` table provides aggregated metrics of Firefox Desktop user activity based on baseline telemetry pings. This table serves as a foundational dataset for understanding user engagement patterns across multiple dimensions including geography, platform characteristics, and user cohorts.

## Table Details

**Database:** `moz-fx-data-shared-prod`  
**Dataset:** `firefox_desktop_derived`  
**Table:** `baseline_active_users_aggregates_v2`

## Purpose

This aggregate table transforms individual user telemetry from the baseline ping into summarized metrics that enable:
- Daily, weekly, and monthly active user (DAU/WAU/MAU) tracking
- User segmentation analysis by platform, geography, and behavior
- Cohort analysis based on first seen date
- Attribution and distribution effectiveness measurement
- Cross-dimensional trend analysis

## Data Source

**Source Table:** `moz-fx-data-shared-prod.firefox_desktop.baseline_active_users`

The ETL process aggregates individual user records by grouping dimensional attributes and counting users across different activity windows.

## Key Metrics

The table distinguishes between two types of user counts:

### Ping-Based Metrics
- **daily_users**: Users who sent pings on the submission date
- **weekly_users**: Users who sent pings in the 7-day trailing window
- **monthly_users**: Users who sent pings in the 28-day trailing window

### Activity-Based Metrics
- **dau**: Daily Active Users with meaningful browser activity
- **wau**: Weekly Active Users with meaningful browser activity  
- **mau**: Monthly Active Users with meaningful browser activity

Activity-based metrics provide a more accurate representation of engaged users compared to ping-based counts.

## Dimensions

The table aggregates user counts across these dimensional attributes:

### Temporal
- `submission_date`: Daily partition key
- `first_seen_year`: User cohort identifier

### Application
- `app_name`: Application identifier with distribution suffixes
- `app_version`, `app_version_major`, `app_version_minor`, `app_version_patch_revision`: Version details
- `app_version_is_major_release`: Major release flag
- `channel`: Release channel (release, beta, nightly, esr)
- `distribution_id`: Custom distribution identifier

### Platform
- `os`, `os_grouped`: Operating system identifiers
- `os_version`, `os_version_major`, `os_version_minor`, `os_version_build`: OS version details
- `windows_build_number`: Windows-specific build number

### Geography
- `country`: ISO alpha-2 country code
- `city`: City name
- `locale`: UI language preference

### User Characteristics
- `is_default_browser`: Default browser status
- `activity_segment`: User engagement classification
- `attribution_medium`, `attribution_source`: Marketing attribution data

## Partitioning and Clustering

**Partitioning:** Daily partition by `submission_date` (required in queries)  
**Clustering:** Optimized for queries filtering by `app_name`, `channel`, and `country`

## Common Use Cases

1. **KPI Dashboards**: Track DAU, WAU, MAU trends over time
2. **Market Analysis**: Understand user distribution by country and platform
3. **Version Adoption**: Monitor uptake of new Firefox versions
4. **Cohort Analysis**: Analyze retention by first_seen_year
5. **Attribution Reporting**: Measure effectiveness of acquisition channels
6. **Segment Performance**: Compare activity patterns across user segments

## Query Examples

### Daily Active Users by Country
```sql
SELECT 
  submission_date,
  country,
  SUM(dau) as total_dau
FROM `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY submission_date, country
ORDER BY submission_date DESC, total_dau DESC
```

### Version Adoption by Channel
```sql
SELECT
  channel,
  app_version_major,
  SUM(daily_users) as users
FROM `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE submission_date = CURRENT_DATE() - 1
GROUP BY channel, app_version_major
ORDER BY channel, app_version_major DESC
```

## Data Refresh

**Schedule:** Daily via `bqetl_analytics_aggregations` DAG  
**Incremental:** Yes - processes one day at a time based on submission_date parameter

## Owners

- kwindau@mozilla.com
- ago@mozilla.com

## Notes

- Requires partition filter on `submission_date` for query optimization
- Activity-based metrics (dau/wau/mau) differ from ping-based metrics (daily_users/weekly_users/monthly_users)
- Country code '??' indicates unknown or unresolved geolocation
- MozillaOnline and BrowserStack clients have modified app_name values
- Window calculations (weekly/monthly) use trailing 7-day and 28-day periods respectively