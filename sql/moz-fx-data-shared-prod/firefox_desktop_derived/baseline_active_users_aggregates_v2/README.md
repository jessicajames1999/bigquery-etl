# Baseline Active Users Aggregates v2

## Overview

The `baseline_active_users_aggregates_v2` table provides aggregated daily metrics for Firefox Desktop user activity across multiple dimensions including geography, platform, distribution channel, and user engagement segments. This table serves as a foundation for understanding user growth, retention, and engagement patterns.

## Data Source

**Source Table:** `moz-fx-data-shared-prod.firefox_desktop.baseline_active_users`

The table aggregates baseline ping data by counting users across various demographic and technical dimensions.

## Key Features

- **Daily Partitioning:** Partitioned by `submission_date` for efficient querying and cost optimization
- **Clustering:** Optimized for queries filtering by `app_name`, `channel`, and `country`
- **User Metrics:** Provides both ping-based user counts (daily/weekly/monthly_users) and activity-based counts (DAU/WAU/MAU)
- **Multi-dimensional Analysis:** Supports segmentation by geography, OS, app version, channel, and user behavior

## ETL Logic

The table uses `COUNTIF` aggregations on boolean flags from the source table:
- **Ping-based metrics** (daily_users, weekly_users, monthly_users): Count users who sent pings
- **Activity-based metrics** (DAU, WAU, MAU): Count users with actual browser activity flags

Data is grouped by 21 dimensions including submission_date, geography (country, city), platform (os, os_version), application (app_version, channel), and attribution fields.

## Dimensions

### Temporal
- `submission_date`: Primary time dimension
- `first_seen_year`: User cohort identifier

### Geographic
- `country`, `city`: Location-based segmentation
- `locale`: Language/regional preferences

### Platform
- `os`, `os_grouped`, `os_version_*`: Operating system details
- `windows_build_number`: Windows-specific tracking

### Application
- `app_name`, `app_version_*`: Firefox version tracking
- `channel`: Release channel (release, beta, nightly, esr)
- `is_default_browser`: Browser preference status

### Distribution & Attribution
- `distribution_id`: Partner distribution tracking
- `attribution_medium`, `attribution_source`: Marketing attribution

### Engagement
- `activity_segment`: User engagement classification

## Metrics

### Ping-Based User Counts
- `daily_users`: Users who sent a ping on submission_date
- `weekly_users`: Users who sent a ping in the last 7 days
- `monthly_users`: Users who sent a ping in the last 28 days

### Activity-Based User Counts
- `dau`: Daily Active Users with browser activity
- `wau`: Weekly Active Users with browser activity
- `mau`: Monthly Active Users with browser activity

## Downstream Analysis Suggestions

### 1. User Retention & Cohort Analysis
Analyze user retention rates by tracking `first_seen_year` cohorts over time. Compare DAU/WAU/MAU ratios across cohorts to identify engagement trends and lifecycle patterns.

```sql
SELECT 
  first_seen_year,
  submission_date,
  SUM(dau) as total_dau,
  SUM(mau) as total_mau,
  SUM(dau) / NULLIF(SUM(mau), 0) as stickiness_ratio
FROM `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY first_seen_year, submission_date
ORDER BY first_seen_year, submission_date
```

### 2. Version Adoption & Migration Tracking
Monitor Firefox version adoption rates across channels to understand rollout effectiveness and identify potential update blockers by analyzing `app_version_major` distribution over time.

```sql
SELECT 
  submission_date,
  channel,
  app_version_major,
  SUM(dau) as active_users,
  SUM(dau) / SUM(SUM(dau)) OVER (PARTITION BY submission_date, channel) as market_share
FROM `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND channel IN ('release', 'beta')
GROUP BY submission_date, channel, app_version_major
ORDER BY submission_date DESC, channel, active_users DESC
```

### 3. Geographic Market Performance
Identify growth opportunities and market trends by analyzing DAU, WAU, MAU by `country` and `locale`, enabling regional product strategies and localization priorities.

```sql
SELECT 
  country,
  locale,
  SUM(dau) as daily_active_users,
  SUM(mau) as monthly_active_users,
  SUM(CASE WHEN is_default_browser THEN dau END) / NULLIF(SUM(dau), 0) as default_browser_rate,
  COUNT(DISTINCT submission_date) as days_tracked
FROM `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND country != '??'
GROUP BY country, locale
HAVING SUM(mau) > 10000
ORDER BY monthly_active_users DESC
```

### 4. Attribution & Acquisition Channel Effectiveness
Evaluate marketing campaign performance by analyzing user acquisition and engagement across `attribution_source` and `attribution_medium`, correlating with `activity_segment` to assess user quality.

```sql
SELECT 
  attribution_source,
  attribution_medium,
  activity_segment,
  SUM(dau) as active_users,
  SUM(mau) as monthly_users,
  SUM(dau) / NULLIF(SUM(mau), 0) as engagement_ratio
FROM `moz-fx-data-shared-prod.firefox_desktop_derived.baseline_active_users_aggregates_v2`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  AND attribution_source IS NOT NULL
GROUP BY attribution_source, attribution_medium, activity_segment
HAVING SUM(mau) > 1000
ORDER BY monthly_users DESC
```

## Owners

- **kwindau@mozilla.com** (Primary Owner)
- **ago@mozilla.com** (Secondary Owner)

## Data Retention

- **Partition Filter Required:** Yes (queries must include submission_date filter)
- **Expiration:** No automatic expiration configured

## Related Tables

- Source: `firefox_desktop.baseline_active_users`
- Related: `telemetry_derived.clients_daily_v6` (more detailed user-level metrics)

## Notes

- Unknown geographic values are stored as '??' in the `country` field
- MozillaOnline and BrowserStack distributions are identified through modified `app_name` values
- The distinction between ping-based (daily_users, weekly_users, monthly_users) and activity-based (DAU, WAU, MAU) metrics allows for analyzing both presence and engagement
