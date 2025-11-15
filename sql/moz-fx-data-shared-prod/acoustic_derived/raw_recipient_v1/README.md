# Raw Recipient (Acoustic Campaign Data)

## Overview

The `raw_recipient_v1` table stores granular email engagement event data imported from Acoustic Campaign's Raw Recipient Data Export API. This table captures individual contact-level interactions with marketing emails, including opens, clicks, bounces, unsubscribes, and other engagement events. It serves as the foundational dataset for analyzing email campaign performance, contact behavior, and overall email marketing effectiveness.

This table is crucial for:
- Tracking email campaign performance metrics
- Analyzing individual contact engagement patterns
- Identifying successful email content and campaigns
- Monitoring deliverability issues and suppression reasons
- Supporting attribution and conversion analysis

## Data Source

**Source System**: Acoustic Campaign (formerly IBM Watson Campaign Automation)  
**API Endpoint**: [Raw Recipient Data Export](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport)  
**Import Method**: CSV file export from Acoustic Campaign API  
**Data Type**: Event-level contact engagement data

## Schema

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| `recipient_id` | INTEGER | Unique identifier for the contact in Acoustic Campaign who received or interacted with the email |
| `report_id` | INTEGER | Internal identifier for the report grouping in Acoustic Campaign's reporting system |
| `mailing_id` | INTEGER | Unique identifier for the specific email send/deployment that generated this event |
| `campaign_id` | INTEGER | Identifier for the broader marketing campaign that contains the mailing |
| `content_id` | STRING | Identifier for the specific content variation or personalized content version sent to the recipient |
| `event_timestamp` | DATETIME | Timestamp when the event occurred, recorded in the API user's configured time zone |
| `event_type` | STRING | Type of engagement event (e.g., 'Sent', 'Open', 'Click', 'Bounce', 'Unsubscribe', 'Opt Out') |
| `recipient_type` | STRING | Classification of the recipient (e.g., 'To', 'CC', 'BCC', 'Test') indicating how the email was addressed |
| `body_type` | STRING | Format of the email body the contact received (e.g., 'HTML', 'Text', 'Multipart') |
| `click_name` | STRING | User-defined name for the clicked link or clickstream identifier, useful for tracking specific CTAs |
| `url` | STRING | The full hyperlink URL that was clicked (populated for click events only) |
| `suppression_reason` | STRING | Reason why a contact was suppressed from receiving the email (e.g., 'Hard Bounce', 'Unsubscribed', 'Spam Complaint') |
| `submission_date` | DATE | Date partition field representing Airflow's execution date, used for incremental processing and data organization |

## Update Schedule

**Frequency**: Daily  
**Mechanism**: Incremental import via Airflow DAG  
**Partition Field**: `submission_date`  
**Data Retention**: 775 days (approximately 25 months)  
**Partition Filter**: Not required (but recommended for query performance)

The `submission_date` field corresponds to the Airflow execution date and should align with dates present in the `event_timestamp` field, though there may be slight delays between event occurrence and data availability.

## Table Properties

- **Time Partitioning**: Daily partitions on `submission_date`
- **Clustering**: Optimized for queries filtering by:
  - `event_type` (primary cluster key)
  - `recipient_type`
  - `body_type`
- **Incremental**: Yes - data is appended daily
- **Table Type**: Client-level (contact-level granularity)

## Usage Examples

### Example 1: Daily Email Performance Summary
```sql
SELECT
  submission_date,
  event_type,
  COUNT(*) AS event_count,
  COUNT(DISTINCT recipient_id) AS unique_recipients
FROM
  `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE
  submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY
  submission_date,
  event_type
ORDER BY
  submission_date DESC,
  event_count DESC;
```

### Example 2: Campaign Click-Through Analysis
```sql
SELECT
  campaign_id,
  mailing_id,
  click_name,
  url,
  COUNT(*) AS total_clicks,
  COUNT(DISTINCT recipient_id) AS unique_clickers
FROM
  `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE
  submission_date = CURRENT_DATE()
  AND event_type = 'Click'
  AND click_name IS NOT NULL
GROUP BY
  campaign_id,
  mailing_id,
  click_name,
  url
ORDER BY
  total_clicks DESC;
```

### Example 3: Suppression Reasons Analysis
```sql
SELECT
  suppression_reason,
  COUNT(*) AS suppression_count,
  COUNT(DISTINCT recipient_id) AS unique_recipients_suppressed
FROM
  `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE
  submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND suppression_reason IS NOT NULL
GROUP BY
  suppression_reason
ORDER BY
  suppression_count DESC;
```

### Example 4: Email Engagement Funnel
```sql
WITH event_summary AS (
  SELECT
    recipient_id,
    MAX(CASE WHEN event_type = 'Sent' THEN 1 ELSE 0 END) AS sent,
    MAX(CASE WHEN event_type = 'Open' THEN 1 ELSE 0 END) AS opened,
    MAX(CASE WHEN event_type = 'Click' THEN 1 ELSE 0 END) AS clicked
  FROM
    `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
  WHERE
    submission_date = CURRENT_DATE()
  GROUP BY
    recipient_id
)
SELECT
  SUM(sent) AS total_sent,
  SUM(opened) AS total_opens,
  SUM(clicked) AS total_clicks,
  SAFE_DIVIDE(SUM(opened), SUM(sent)) AS open_rate,
  SAFE_DIVIDE(SUM(clicked), SUM(opened)) AS click_to_open_rate
FROM
  event_summary;
```

## Related Tables

This table may be used in conjunction with:
- Other Acoustic derived tables for comprehensive email marketing analysis
- Campaign dimension tables (if available) for campaign metadata
- Contact/recipient dimension tables for demographic analysis
- Conversion or attribution tables for measuring email marketing ROI

## Data Quality Notes

1. **Event Deduplication**: Multiple events of the same type may occur for a single recipient (e.g., multiple opens or clicks). Consider using `COUNT(DISTINCT recipient_id)` when calculating unique engagement metrics.

2. **Time Zone Considerations**: The `event_timestamp` reflects the API user's configured time zone in Acoustic Campaign. Ensure consistency when joining with other datasets or performing time-based analysis.

3. **Null Values**: 
   - `click_name` and `url` are only populated for click events
   - `suppression_reason` is only populated for suppression-related events
   - `report_id` and `content_id` may be null depending on campaign configuration

4. **Event Types**: Common event types include:
   - `Sent`: Email successfully delivered
   - `Open`: Email opened (tracked via pixel)
   - `Click`: Link clicked within email
   - `Bounce`: Email bounced (hard or soft)
   - `Unsubscribe`: Recipient unsubscribed
   - `Opt Out`: Recipient opted out
   - Additional event types may be present based on Acoustic Campaign configuration

5. **Performance Optimization**: 
   - Always include `submission_date` filter to leverage partitioning
   - Use clustering fields (`event_type`, `recipient_type`, `body_type`) in WHERE clauses for better performance
   - Consider materializing frequently used aggregations

## Contact

**Table Owner**: cbeck@mozilla.com

For questions about data quality, schema changes, or access, please contact the table owner.

## References

- [Acoustic Campaign API Documentation](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport)
- [Acoustic Campaign Raw Recipient Data Export Guide](https://developer.goacoustic.com/acoustic-campaign/docs/raw-recipient-data-export)
