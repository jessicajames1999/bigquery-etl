# Raw Recipient (Acoustic Campaign Data)

## Table Overview

`moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1` contains raw recipient event data exported from Acoustic Campaign, a marketing automation platform. This table captures granular email performance metrics and recipient interactions including email sends, opens, clicks, bounces, and suppressions. The data is imported as CSV exports from Acoustic's Raw Recipient Data Export API and provides a comprehensive view of email campaign engagement at the individual recipient level.

**Data Source:** [Acoustic Campaign Raw Recipient Data Export API](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport)

## Table Schema

### Recipient & Campaign Identifiers

| Column | Type | Description |
|--------|------|-------------|
| `recipient_id` | INTEGER | Unique identifier for the email recipient contact record in Acoustic Campaign system |
| `report_id` | INTEGER | Internal report identifier used for Acoustic Campaign analytics and tracking purposes |
| `mailing_id` | INTEGER | Unique identifier of the specific email mailing or send associated with this recipient event |
| `campaign_id` | INTEGER | Identifier of the marketing campaign associated with this email event in Acoustic Campaign |
| `content_id` | STRING | Identifier for the specific email content or creative variant sent to the recipient |

### Event Details

| Column | Type | Description |
|--------|------|-------------|
| `event_timestamp` | DATETIME | Date and time when the recipient event occurred, in the API user's configured time zone |
| `event_type` | STRING | Classification of the recipient interaction (e.g., sent, opened, clicked, bounced, unsubscribed) |
| `recipient_type` | STRING | Classification of the recipient contact type (e.g., normal, test, seed) to whom the email was sent |
| `body_type` | STRING | Format of the email body received by the contact (e.g., HTML, plain text, multipart) |

### Click & Engagement Tracking

| Column | Type | Description |
|--------|------|-------------|
| `click_name` | STRING | User-defined label or name assigned to the clicked link or clickstream element in the email |
| `url` | STRING | Full URL of the hyperlink that was clicked through or tracked as a clickstream event |

### Suppression Information

| Column | Type | Description |
|--------|------|-------------|
| `suppression_reason` | STRING | Reason code or description explaining why a contact was suppressed from receiving the email |

### ETL Metadata

| Column | Type | Description |
|--------|------|-------------|
| `submission_date` | DATE | Airflow's execution date should overlap with date inside event_timestamp field |

## Table Configuration

- **Partitioning:** Daily partitioning on `submission_date` field
- **Partition Expiration:** 775 days (~2.1 years)
- **Clustering:** `event_type`, `recipient_type`, `body_type`
- **Incremental:** Yes
- **Table Type:** Client-level data

## Downstream Analysis Suggestions

### 1. Email Campaign Performance Analysis
Analyze email engagement metrics by campaign to identify high-performing campaigns and content strategies:
```sql
SELECT
  campaign_id,
  mailing_id,
  event_type,
  COUNT(DISTINCT recipient_id) as unique_recipients,
  COUNT(*) as total_events,
  DATE(event_timestamp) as event_date
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE event_type IN ('sent', 'opened', 'clicked')
GROUP BY campaign_id, mailing_id, event_type, event_date
ORDER BY event_date DESC, unique_recipients DESC
```

### 2. Click-Through Rate (CTR) Analysis
Calculate engagement rates and identify which links and content variants drive the most clicks:
```sql
SELECT
  content_id,
  click_name,
  url,
  body_type,
  COUNT(DISTINCT recipient_id) as unique_clickers,
  COUNT(*) as total_clicks
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE event_type = 'clicked'
  AND submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY content_id, click_name, url, body_type
ORDER BY total_clicks DESC
LIMIT 100
```

### 3. Recipient Behavior Segmentation
Segment recipients by engagement patterns and recipient types to optimize targeting strategies:
```sql
SELECT
  recipient_id,
  recipient_type,
  COUNT(DISTINCT CASE WHEN event_type = 'sent' THEN mailing_id END) as emails_sent,
  COUNT(DISTINCT CASE WHEN event_type = 'opened' THEN mailing_id END) as emails_opened,
  COUNT(DISTINCT CASE WHEN event_type = 'clicked' THEN mailing_id END) as emails_clicked,
  MAX(event_timestamp) as last_interaction
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY recipient_id, recipient_type
HAVING emails_sent > 0
```

### 4. Suppression & Deliverability Monitoring
Track email suppressions and deliverability issues to maintain list health and sender reputation:
```sql
SELECT
  suppression_reason,
  recipient_type,
  body_type,
  DATE(event_timestamp) as suppression_date,
  COUNT(DISTINCT recipient_id) as suppressed_recipients,
  COUNT(*) as suppression_events
FROM `moz-fx-data-shared-prod.acoustic_derived.raw_recipient_v1`
WHERE suppression_reason IS NOT NULL
  AND submission_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY suppression_reason, recipient_type, body_type, suppression_date
ORDER BY suppression_date DESC, suppression_events DESC
```

## Data Quality Considerations

- Events are time-zone dependent based on API user's configuration
- The `submission_date` field should align with the date portion of `event_timestamp` for data validation
- Null values in `suppression_reason` indicate non-suppressed events
- Click events will have populated `click_name` and `url` fields, while other event types may have these as null
- Test and seed recipient types should be filtered out for production analytics

## Owners

- cbeck@mozilla.com

## Related Tables

- `moz-fx-data-shared-prod.acoustic_derived.*` - Other Acoustic Campaign derived tables
- Consider joining with user dimension tables for enriched recipient profiles

---

*Last Updated: Documentation generated for schema improvements (Issue #54)*
