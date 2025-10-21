# Raw Recipient (Acoustic Campaign Data)

## Overview

The `raw_recipient_v1` table contains raw email event data exported from Acoustic Campaign. This table captures detailed recipient-level interactions with email campaigns, including sends, opens, clicks, bounces, and unsubscribes. The data is imported from CSV files provided by the Acoustic Campaign API and serves as a foundational dataset for email marketing performance analysis.

## Table Details

- **Database**: `moz-fx-data-shared-prod`
- **Dataset**: `acoustic_derived`
- **Table**: `raw_recipient_v1`
- **Data Source**: Acoustic Campaign Raw Recipient Data Export API
- **Table Type**: Client-level event data
- **Update Frequency**: Incremental daily loads
- **Partition Field**: `submission_date` (775 days retention)
- **Clustering**: `event_type`, `recipient_type`, `body_type`

## Schema Summary

This table contains 13 columns tracking:
- **Identifiers**: `recipient_id`, `report_id`, `mailing_id`, `campaign_id`, `content_id`
- **Event Attributes**: `event_timestamp`, `event_type`, `recipient_type`, `body_type`
- **Click Tracking**: `click_name`, `url`
- **Deliverability**: `suppression_reason`
- **ETL Metadata**: `submission_date`

## Key Metrics Tracked

- Email sends and deliverability
- Email opens (unique and total)
- Click-through events and URLs
- Bounce and suppression tracking
- Campaign and content performance
- Recipient engagement patterns

## Downstream Analysis Suggestions

### 1. Email Engagement Funnel Analysis
Calculate conversion rates across the email engagement funnel (sent → opened → clicked) segmented by campaign, content variant, or recipient type. Identify drop-off points and optimize content accordingly.

```sql
SELECT
  campaign_id,
  mailing_id,
  COUNT(DISTINCT CASE WHEN event_type = 'Sent' THEN recipient_id END) as sent_count,
  COUNT(DISTINCT CASE WHEN event_type = 'Open' THEN recipient_id END) as open_count,
  COUNT(DISTINCT CASE WHEN event_type = 'Click' THEN recipient_id END) as click_count,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN event_type = 'Open' THEN recipient_id END),
    COUNT(DISTINCT CASE WHEN event_type = 'Sent' THEN recipient_id END)
  ) * 100 as open_rate,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN event_type = 'Click' THEN recipient_id END),
    COUNT(DISTINCT CASE WHEN event_type = 'Open' THEN recipient_id END)
  ) * 100 as ctr
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY campaign_id, mailing_id
ORDER BY sent_count DESC
```

### 2. Content and Format Performance Comparison
Analyze email engagement by body type (HTML vs. Plain Text) and content variants to determine which formats and content perform best with different audience segments.

```sql
SELECT
  body_type,
  content_id,
  event_type,
  COUNT(DISTINCT recipient_id) as unique_recipients,
  COUNT(*) as total_events
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  AND event_type IN ('Open', 'Click')
GROUP BY body_type, content_id, event_type
ORDER BY total_events DESC
```

### 3. Link Performance and Click Heatmap
Identify the most popular links and CTAs within email campaigns by analyzing click_name and url patterns. Optimize email design by placing high-performing CTAs prominently.

```sql
SELECT
  campaign_id,
  click_name,
  url,
  COUNT(DISTINCT recipient_id) as unique_clickers,
  COUNT(*) as total_clicks
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE event_type = 'Click'
  AND submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)
  AND click_name IS NOT NULL
GROUP BY campaign_id, click_name, url
ORDER BY unique_clickers DESC
LIMIT 50
```

### 4. Email Deliverability and Suppression Analysis
Monitor email list health by tracking suppression reasons, bounce rates, and unsubscribe patterns. Implement targeted list cleaning strategies based on suppression trends.

```sql
SELECT
  suppression_reason,
  recipient_type,
  DATE_TRUNC(submission_date, WEEK) as week,
  COUNT(DISTINCT recipient_id) as suppressed_recipients,
  COUNT(*) as suppression_events
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE suppression_reason IS NOT NULL
  AND submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
GROUP BY suppression_reason, recipient_type, week
ORDER BY week DESC, suppressed_recipients DESC
```

## Data Quality Notes

- Events are partitioned by `submission_date` for efficient querying
- Clustering on `event_type`, `recipient_type`, and `body_type` optimizes common query patterns
- Use partition filters on `submission_date` for cost-effective queries
- `url` and `click_name` are only populated for click events
- `suppression_reason` is only populated for suppression events

## Owners

- **Primary Owner**: cbeck@mozilla.com

## Related Tables

This raw table serves as a source for downstream aggregated tables in the `acoustic_derived` dataset that provide campaign-level and recipient-level analytics.

## API Reference

For detailed information about the data fields and export format, refer to the [Acoustic Campaign Raw Recipient Data Export API documentation](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport).
