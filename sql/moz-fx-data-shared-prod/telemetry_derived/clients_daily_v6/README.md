# Clients Daily (clients_daily_v6)

## Overview

The `clients_daily_v6` table provides a comprehensive daily aggregation of Firefox Desktop telemetry data at the client level. Each row represents one client (identified by `client_id`) for one day (identified by `submission_date`), aggregating all `main` pings received from that client on that day.

## Purpose

This table serves as the primary source for:
- Daily active users (DAU) analysis
- Client-level behavior and engagement metrics
- Hardware and system configuration analysis
- Search metrics and revenue analysis
- Feature usage tracking
- Experiment enrollment and analysis
- Performance and stability metrics

## Data Source

The table is derived from `telemetry_stable.main_v5`, which contains raw telemetry pings from Firefox Desktop. The ETL process:
1. Filters for Firefox `main` pings from the specified submission date
2. Excludes overactive clients (>150K pings/day or >3M active addons)
3. Aggregates multiple pings per client into a single daily row
4. Uses "mode last" for most dimensional attributes (taking the most recent value)
5. Sums numeric counters across all pings
6. Averages gauge-type metrics

## Key Features

### Partitioning & Clustering
- **Partitioned by**: `submission_date` (day-level)
- **Clustered by**: `normalized_channel`, `sample_id`
- **Retention**: 775 days (~2 years)
- **Requires partition filter**: Yes (must filter by `submission_date`)

### Aggregation Strategy

The table uses sophisticated aggregation functions:
- **mozfun.stats.mode_last()**: Most recent non-null value (for dimensions like OS, channel)
- **SUM()**: Total across all pings (for counters like crashes, searches)
- **AVG()**: Average across pings (for metrics like active addons count)
- **mozfun.map.mode_last()**: Mode-last for keyed structures (experiments, add-ons)

### Major Column Groups

1. **Client Identification**: `client_id`, `sample_id`, `profile_group_id`
2. **Time Dimensions**: `submission_date`, `profile_creation_date`, `profile_age_in_days`
3. **Application Info**: `app_version`, `app_build_id`, `channel`, `normalized_channel`
4. **System Configuration**: CPU, memory, OS, graphics features
5. **Geolocation**: `country`, `city`, ISP information
6. **Search Metrics**: Detailed search counts by engine, source, and ad interactions
7. **Engagement Metrics**: Active hours, URIs visited, tabs/windows opened
8. **Stability**: Crashes, hangs, aborts by process type
9. **Features**: Add-ons, experiments, Firefox Sync, devtools usage
10. **Privacy Features**: Tracker blocking, search suggestions preferences

## Common Use Cases

### Daily Active Users (DAU)
```sql
SELECT
  submission_date,
  COUNT(DISTINCT client_id) AS dau
FROM
  `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v6`
WHERE
  submission_date = '2024-01-01'
  AND normalized_channel = 'release'
GROUP BY
  submission_date
```

### Active Hours Distribution
```sql
SELECT
  active_hours_sum,
  COUNT(*) AS client_count
FROM
  `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v6`
WHERE
  submission_date = '2024-01-01'
GROUP BY
  active_hours_sum
ORDER BY
  active_hours_sum
```

### Search Revenue Analysis
```sql
SELECT
  SUM(search_count_all) AS total_searches,
  SUM(search_with_ads_count_all) AS searches_with_ads,
  SUM(ad_clicks_count_all) AS ad_clicks
FROM
  `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v6`
WHERE
  submission_date BETWEEN '2024-01-01' AND '2024-01-31'
  AND normalized_channel = 'release'
```

## User-Facing View

Users should typically query `telemetry.clients_daily` instead of this derived table directly. The user-facing view:
- Provides additional downstream fields from the `event` ping
- Includes fields from `clients_last_seen_joined_v1`
- Offers better documentation and stability guarantees

## Important Notes

1. **Sampling**: Use `sample_id` (0-99) for consistent random sampling across analyses
2. **Activity Definition**: `active_hours_sum` is calculated from active ticks (5-second intervals of user interaction)
3. **Search Metrics**: Multiple search count fields exist for different granularities - use `search_count_all` for total searches
4. **Nested Fields**: Many scalar metrics use RECORD types with `key` and `value` sub-fields for detailed breakdowns
5. **Null Values**: Most columns are nullable; many will be NULL for clients without relevant activity
6. **Mode Last**: Dimensional attributes reflect the last-seen value, not necessarily the most common

## Scheduling

- **DAG**: `bqetl_main_summary`
- **Schedule**: Daily
- **Downstream**: Feeds into Jetstream, Operational Monitoring, and Parquet exports

## Ownership

- **Owner**: ascholtz@mozilla.com
- **Team**: Data Engineering
- **Application**: Firefox Desktop

## Schema Version

This is version 6 of the clients_daily schema. For historical partitions before 2019-11-22, a different version reading from `main_summary_v4` was used.

## Related Tables

- `telemetry.clients_daily` - User-facing view (recommended)
- `telemetry_derived.clients_last_seen_v1` - Client retention analysis
- `telemetry_stable.main_v5` - Source data
- `telemetry_derived.main_summary_v4` - Deprecated predecessor