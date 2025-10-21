# Raw Recipient (Acoustic Campaign Data)

## Overview

This table contains raw recipient-level event data exported from Acoustic Campaign (formerly Silverpop). It captures detailed email marketing interaction events including sends, opens, clicks, bounces, and unsubscribes. The data is imported from CSV files exported via the Acoustic Campaign API.

**Source:** [Acoustic Campaign Raw Recipient Data Export API](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport)

## Table Details

- **Dataset:** `moz-fx-data-shared-prod.acoustic_derived`
- **Table:** `raw_recipient_v1`
- **Table Type:** Client-level (recipient-level granularity)
- **Update Frequency:** Incremental daily imports
- **Partitioning:** Daily partitions on `submission_date` (775-day retention)
- **Clustering:** Optimized for queries filtering by `event_type`, `recipient_type`, and `body_type`

## Schema Summary

The table contains 13 columns tracking:
- **Identifiers:** recipient_id, report_id, mailing_id, campaign_id, content_id
- **Event Metadata:** event_timestamp, event_type, recipient_type
- **Email Content:** body_type, content_id
- **Engagement Details:** click_name, url, suppression_reason
- **ETL Metadata:** submission_date

## Key Event Types

Common values in the `event_type` column include:
- **Sent**: Email successfully delivered to recipient
- **Opened**: Recipient opened the email (tracked via pixel)
- **Clicked**: Recipient clicked a link in the email
- **Bounced**: Email delivery failed (hard or soft bounce)
- **Unsubscribed**: Recipient opted out from future emails
- **Suppressed**: Recipient excluded from mailing due to previous issues

## Downstream Analysis Suggestions

### 1. Email Campaign Performance Dashboard
Analyze email engagement metrics by campaign to measure effectiveness:
```sql
SELECT
  campaign_id,
  COUNT(DISTINCT CASE WHEN event_type = 'Sent' THEN recipient_id END) as sends,
  COUNT(DISTINCT CASE WHEN event_type = 'Opened' THEN recipient_id END) as opens,
  COUNT(DISTINCT CASE WHEN event_type = 'Clicked' THEN recipient_id END) as clicks,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN event_type = 'Opened' THEN recipient_id END),
    COUNT(DISTINCT CASE WHEN event_type = 'Sent' THEN recipient_id END)
  ) as open_rate,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN event_type = 'Clicked' THEN recipient_id END),
    COUNT(DISTINCT CASE WHEN event_type = 'Sent' THEN recipient_id END)
  ) as click_rate
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY campaign_id
ORDER BY sends DESC;
```

### 2. Email Deliverability and Suppression Analysis
Monitor email delivery health by tracking bounce rates and suppression reasons:
```sql
SELECT
  DATE(event_timestamp) as event_date,
  suppression_reason,
  body_type,
  COUNT(DISTINCT recipient_id) as affected_recipients,
  COUNT(*) as total_events
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE event_type IN ('Bounced', 'Suppressed')
  AND submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY event_date, suppression_reason, body_type
ORDER BY event_date DESC, affected_recipients DESC;
```

### 3. Link Click-Through Analysis
Identify top-performing email links and content by analyzing click behavior:
```sql
SELECT
  campaign_id,
  content_id,
  click_name,
  url,
  COUNT(DISTINCT recipient_id) as unique_clickers,
  COUNT(*) as total_clicks
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE event_type = 'Clicked'
  AND submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND url IS NOT NULL
GROUP BY campaign_id, content_id, click_name, url
HAVING unique_clickers >= 10
ORDER BY unique_clickers DESC
LIMIT 50;
```

### 4. Recipient Engagement Cohort Analysis
Segment recipients by engagement patterns to optimize targeting:
```sql
WITH recipient_engagement AS (
  SELECT
    recipient_id,
    COUNT(DISTINCT CASE WHEN event_type = 'Sent' THEN mailing_id END) as emails_received,
    COUNT(DISTINCT CASE WHEN event_type = 'Opened' THEN mailing_id END) as emails_opened,
    COUNT(DISTINCT CASE WHEN event_type = 'Clicked' THEN mailing_id END) as emails_clicked,
    MAX(CASE WHEN event_type = 'Unsubscribed' THEN 1 ELSE 0 END) as has_unsubscribed
  FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
  WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY recipient_id
)
SELECT
  CASE
    WHEN has_unsubscribed = 1 THEN 'Unsubscribed'
    WHEN emails_clicked > 0 THEN 'Highly Engaged (Clickers)'
    WHEN emails_opened > 0 THEN 'Moderately Engaged (Openers)'
    WHEN emails_received > 0 THEN 'Low Engagement (Non-Openers)'
    ELSE 'Unknown'
  END as engagement_segment,
  COUNT(DISTINCT recipient_id) as recipient_count,
  AVG(emails_received) as avg_emails_received,
  AVG(emails_opened) as avg_emails_opened,
  AVG(emails_clicked) as avg_emails_clicked
FROM recipient_engagement
GROUP BY engagement_segment
ORDER BY recipient_count DESC;
```

## Notes

- This is a raw import table; consider joining with dimension tables for campaign and recipient details
- Click and URL fields are only populated for click-type events
- Suppression reason is only populated for bounced or suppressed events
- Time partitioning enables efficient date-range queries; always include `submission_date` filter for performance
- Data retention is 775 days (~2 years)

## Owner

- **Primary Contact:** cbeck@mozilla.com
