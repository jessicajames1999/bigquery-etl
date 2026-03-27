# clients_daily_v6

## Overview

The `clients_daily_v6` table provides a comprehensive daily aggregation of Firefox Desktop telemetry data at the client level. Each row represents one client's activity for a single day, combining data from multiple telemetry pings received on that submission date.

**Database:** `moz-fx-data-shared-prod`  
**Dataset:** `telemetry_derived`  
**Table:** `clients_daily_v6`

## Purpose

This table is the primary source for analyzing daily Firefox Desktop client behavior, including:

- **User Engagement:** Active hours, URI counts, tab/window usage, unique domains visited
- **Search Activity:** Detailed search counts by engine, source, and access point; ad impressions and clicks
- **Stability Metrics:** Crash counts, abort events, hang events by process type
- **Feature Usage:** Developer tools, Quick Suggest, sidebar, library, text recognition
- **Configuration:** Browser settings, experiments, addons, search engines, user preferences
- **System Information:** Hardware specs, OS details, graphics features
- **Data Migration:** Import quantities from Chrome, Edge, and Safari

## Key Characteristics

- **Granularity:** One row per client per day
- **Aggregation:** Combines all pings from a client on a given submission_date
- **Source:** Derived from `telemetry_stable.main_v5`
- **Update Schedule:** Daily, processing data from the previous day
- **Data Volume:** Filters out overactive clients (>150,000 pings/day or >3M active addons)

## Important Columns

### Identity
- `client_id`: Unique client identifier (UUID)
- `submission_date`: Date when pings were received (partitioning key)
- `sample_id`: Consistent 0-99 sample bucket for data sampling

### Engagement
- `active_hours_sum`: Total active usage hours (based on active ticks)
- `scalar_parent_browser_engagement_total_uri_count_sum`: Total pages loaded
- `scalar_parent_browser_engagement_unique_domains_count_max`: Unique domains visited
- `sessions_started_on_this_day`: Number of browser sessions initiated

### Search
- `search_counts`: Detailed array of search counts by engine and source
- `search_count_all`: Aggregated total searches
- `ad_clicks_count_all`: Total ad clicks from searches
- `search_with_ads_count_all`: Searches that displayed ads

### Stability
- `crashes_detected_*_sum`: Crash counts by process type (content, plugin, gmplugin)
- `crash_submit_success_*_sum`: Successfully submitted crash reports
- `aborts_*_sum`: Process abort events

### Configuration
- `active_addons`: Array of installed addon details
- `experiments`: Active experiments and their branches
- `default_search_engine`: Default search engine identifier
- `attribution`: Marketing attribution data

### Hardware & OS
- `os`, `os_version`, `normalized_os_version`: Operating system details
- `cpu_*`: CPU specifications (cores, model, speed, cache)
- `memory_mb`: System RAM
- `gfx_features_*`: Graphics feature status

## RECORD Type Columns

Several columns use the RECORD (struct) type to store complex nested data:

- **active_addons**: Array of addon details with properties like addon_id, version, is_system, etc.
- **attribution**: Marketing attribution with source, medium, campaign fields
- **experiments**: Active experiments with key-value pairs
- **search_counts**: Search activity by engine and source
- **Keyed scalars**: Many `scalar_parent_*` fields contain key-value maps for categorized metrics

## Common Use Cases

### Daily Active Users (DAU)
```sql
SELECT submission_date, COUNT(DISTINCT client_id) AS dau
FROM `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v6`
WHERE submission_date = '2024-01-15'
GROUP BY submission_date
```

### Search Behavior Analysis
```sql
SELECT 
  submission_date,
  SUM(search_count_all) AS total_searches,
  SUM(ad_clicks_count_all) AS total_ad_clicks
FROM `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v6`
WHERE submission_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY submission_date
```

### Addon Usage
```sql
SELECT 
  addon.addon_id,
  addon.name,
  COUNT(DISTINCT client_id) AS users
FROM `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v6`,
  UNNEST(active_addons) AS addon
WHERE submission_date = '2024-01-15'
GROUP BY addon.addon_id, addon.name
ORDER BY users DESC
LIMIT 20
```

## Data Quality Considerations

1. **Overactive Clients Excluded:** Clients with >150,000 pings/day are filtered out to prevent aggregation errors
2. **Mode Last Aggregation:** Many fields use `mode_last` to select the most recent value when multiple pings have different values
3. **Null Values:** Many columns can be NULL if the client didn't send that telemetry or if the feature wasn't used
4. **Deprecated Fields:** Some columns are marked as deprecated (e.g., `active_experiment_id`, `total_hours_sum`)

## Schema Evolution

This is version 6 of the clients_daily schema. Key changes from previous versions:
- Migrated from `main_summary_v4` to `main_v5` as source (as of 2019-11-22)
- Added numerous Quick Suggest metrics
- Enhanced search metrics with detailed access points
- Added migration quantity metrics
- Added text recognition metrics
- Added sidebar and library usage metrics

## Related Tables

- **Source:** `telemetry_stable.main_v5` (raw ping data)
- **Alternative:** `telemetry.clients_daily` (public view)
- **Aggregations:** Various derived tables use this as a source for further aggregation

## Performance Tips

1. **Always filter by submission_date** - This is the partitioning key
2. **Use sample_id for testing** - Query `sample_id = 0` for ~1% sample
3. **Limit date ranges** - Each day contains millions of rows
4. **Use UNNEST carefully** - Nested fields (addons, experiments, search_counts) can explode row counts

## Documentation Links

- [BigQuery ETL Repository](https://github.com/mozilla/bigquery-etl)
- [Firefox Data Documentation](https://docs.telemetry.mozilla.org/)
- [Telemetry Collection](https://firefox-source-docs.mozilla.org/toolkit/components/telemetry/)

## Contact

For questions about this table:
- Data Engineering Team
- #data-help on Mozilla Slack
- [File a bug](https://bugzilla.mozilla.org/enter_bug.cgi?product=Data%20Platform%20and%20Tools)
