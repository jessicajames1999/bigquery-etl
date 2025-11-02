# Raw Recipient (Acoustic Campaign Data)

## Overview

The `raw_recipient_v1` table contains detailed email recipient event data exported from Acoustic Campaign. This table serves as the foundation for analyzing email campaign performance, tracking recipient interactions, and understanding engagement patterns across Mozilla's email marketing efforts.

**Data Source:** Acoustic Campaign API
**Update Frequency:** Daily (incremental)
**Granularity:** Individual recipient events
**API Reference:** [Acoustic Campaign Raw Recipient Data Export](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport)

## Key Features

- **Time-partitioned** by `submission_date` for efficient querying
- **Clustered** by `event_type`, `recipient_type`, and `body_type` for optimized filtering
- **Retention:** 775 days (~2 years)
- **Data Level:** Individual recipient-level events

## Schema Summary

This table captures comprehensive email campaign event data including:
- **Identifiers:** Recipient, mailing, campaign, and content IDs
- **Event tracking:** Event types, timestamps, and recipient classifications
- **Engagement metrics:** Click tracking with link names and URLs
- **Deliverability:** Suppression reasons and recipient types
- **Content details:** Body type and content variations

## Downstream Analysis Suggestions

### 1. Email Engagement Funnel Analysis
Analyze the progression from email sends through opens, clicks, and conversions:
```sql
SELECT
  event_type,
  COUNT(DISTINCT recipient_id) as unique_recipients,
  COUNT(*) as total_events
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY event_type
ORDER BY total_events DESC
```

### 2. Campaign Performance Comparison
Compare click-through rates and engagement across different campaigns:
```sql
SELECT
  campaign_id,
  COUNTIF(event_type = 'Sent') as sends,
  COUNTIF(event_type = 'Opened') as opens,
  COUNTIF(event_type = 'Clicked') as clicks,
  SAFE_DIVIDE(COUNTIF(event_type = 'Clicked'), COUNTIF(event_type = 'Sent')) as ctr
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY campaign_id
HAVING sends > 1000
ORDER BY ctr DESC
```

### 3. Content Optimization Analysis
Identify which email body types and content variations drive the highest engagement:
```sql
SELECT
  body_type,
  content_id,
  COUNT(DISTINCT recipient_id) as recipients,
  COUNTIF(event_type = 'Clicked') / NULLIF(COUNTIF(event_type = 'Opened'), 0) as click_to_open_rate
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)
  AND event_type IN ('Opened', 'Clicked')
GROUP BY body_type, content_id
HAVING recipients > 100
ORDER BY click_to_open_rate DESC
```

### 4. Suppression and Deliverability Trends
Monitor email list health by tracking suppression reasons over time:
```sql
SELECT
  DATE_TRUNC(submission_date, WEEK) as week,
  suppression_reason,
  COUNT(DISTINCT recipient_id) as suppressed_recipients
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE suppression_reason IS NOT NULL
  AND submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
GROUP BY week, suppression_reason
ORDER BY week DESC, suppressed_recipients DESC
```

## Owners

- cbeck@mozilla.com

## Related Tables

Consider joining with other Acoustic Campaign tables for comprehensive analysis:
- Campaign metadata tables for campaign names and details
- Contact/recipient dimension tables for demographic analysis
- Other event tables for complete customer journey tracking

## Notes

- The `submission_date` field represents the ETL processing date and should align with dates in `event_timestamp`
- Events are recorded at the individual recipient level, allowing for detailed behavioral analysis
- The table is partitioned and clustered for optimal query performance on recent data filtered by event characteristics
