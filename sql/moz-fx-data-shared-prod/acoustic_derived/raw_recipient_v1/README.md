# Raw Recipient (Acoustic Campaign Data)

## Overview

This table contains raw recipient-level event data imported from Acoustic Campaign via CSV exports. It captures granular email engagement metrics including sends, opens, clicks, bounces, and unsubscribes for Mozilla's email marketing campaigns managed through the Acoustic platform.

The data provides a comprehensive view of recipient interactions with email campaigns, enabling detailed performance analysis, deliverability monitoring, and recipient behavior tracking.

## Data Source

- **Platform**: Acoustic Campaign (formerly IBM Watson Campaign Automation)
- **Import Method**: CSV file export via Acoustic Campaign API
- **Update Frequency**: Incremental daily loads
- **API Documentation**: [Acoustic Campaign Raw Recipient Data Export](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport)

## Table Properties

- **Partition Field**: `submission_date` (day-level partitioning)
- **Partition Expiration**: 775 days (~2 years)
- **Clustering**: `event_type`, `recipient_type`, `body_type`
- **Table Type**: Client-level (recipient-level granularity)

## Schema Summary

The table contains 13 columns organized into:

- **Campaign Identifiers**: `campaign_id`, `mailing_id`, `content_id`, `report_id`
- **Recipient Information**: `recipient_id`, `recipient_type`
- **Event Details**: `event_type`, `event_timestamp`, `body_type`
- **Click/Link Data**: `click_name`, `url`
- **Deliverability**: `suppression_reason`
- **ETL Metadata**: `submission_date`

## Key Event Types

The `event_type` column captures various recipient interactions:
- **Sent**: Email successfully delivered to recipient
- **Open**: Email opened by recipient (tracked via pixel)
- **Click**: Link clicked within email
- **Bounce**: Email delivery failure (hard or soft bounce)
- **Unsubscribe**: Recipient opted out of future emails
- **Spam Complaint**: Recipient marked email as spam

## Downstream Analysis Suggestions

### 1. Email Campaign Performance Dashboard
Calculate key email marketing KPIs by campaign:
- **Open Rate**: `COUNT(DISTINCT recipient_id WHERE event_type = 'Open') / COUNT(DISTINCT recipient_id WHERE event_type = 'Sent')`
- **Click Rate**: `COUNT(DISTINCT recipient_id WHERE event_type = 'Click') / COUNT(DISTINCT recipient_id WHERE event_type = 'Sent')`
- **Bounce Rate**: `COUNT(DISTINCT recipient_id WHERE event_type = 'Bounce') / COUNT(DISTINCT recipient_id WHERE event_type = 'Sent')`
- **Unsubscribe Rate**: Track opt-out trends over time

Group by `campaign_id`, `mailing_id`, or `submission_date` to identify top-performing campaigns and trends.

### 2. Recipient Engagement Segmentation
Build recipient cohorts based on engagement patterns:
- Identify highly engaged recipients (multiple opens/clicks across campaigns)
- Flag inactive recipients (sent but no opens over N days)
- Segment by `body_type` preference (HTML vs plain text engagement)
- Analyze time-to-open and time-to-click patterns using `event_timestamp`

This enables targeted re-engagement campaigns and list hygiene.

### 3. Link Performance & Content Analysis
Analyze which content drives clicks:
- Rank links by click volume using `click_name` and `url`
- Compare performance across `content_id` variants (A/B testing)
- Track clickstream patterns (sequential clicks by recipient)
- Identify broken or underperforming links

Optimize email creative and CTAs based on click behavior.

### 4. Deliverability & List Health Monitoring
Monitor email deliverability metrics:
- Trend `suppression_reason` categories over time
- Identify problematic recipient segments or domains
- Track bounce types and implement list cleaning rules
- Monitor spam complaint rates by campaign or sending pattern
- Analyze `recipient_type` distribution (test vs production sends)

Maintain sender reputation and improve inbox placement rates.

## Owners

- **Primary Contact**: cbeck@mozilla.com

## Notes

- The `submission_date` partition field should align with dates in `event_timestamp` for proper Airflow scheduling
- Table uses day-level partitioning with 775-day expiration (approximately 2 years of retention)
- Clustering on `event_type`, `recipient_type`, and `body_type` optimizes common query patterns
- This is raw, client-level data - consider aggregating for reporting to reduce scan costs
