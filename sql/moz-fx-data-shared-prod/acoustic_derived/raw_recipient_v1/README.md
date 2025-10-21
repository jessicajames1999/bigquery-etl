# Raw Recipient Data (Acoustic Campaign)

## Overview

This table contains raw recipient-level event data exported from Acoustic Campaign via CSV import. It captures granular email engagement metrics including sends, opens, clicks, bounces, and unsubscribes for each contact who received campaign emails.

The table provides a comprehensive view of individual recipient interactions with email campaigns, enabling detailed performance analysis, engagement tracking, and list hygiene management.

## Data Source

- **Platform**: Acoustic Campaign (formerly IBM Watson Campaign Automation)
- **Import Method**: CSV data export via Acoustic Campaign API
- **API Reference**: [Raw Recipient Data Export Documentation](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport)

## Table Details

- **Database**: `moz-fx-data-shared-prod`
- **Dataset**: `acoustic_derived`
- **Table**: `raw_recipient_v1`
- **Update Frequency**: Incremental daily loads
- **Partitioning**: Daily partitioning on `submission_date`
- **Clustering**: Optimized by `event_type`, `recipient_type`, and `body_type`
- **Retention**: 775 days

## Key Metrics

The table tracks several recipient-level events:

- **Email Sends**: Records of emails successfully delivered
- **Opens**: When recipients open the email
- **Clicks**: When recipients click links within the email
- **Bounces**: Failed delivery events
- **Unsubscribes**: Opt-out events
- **Suppressions**: Blocked recipients with reasons

## Schema Highlights

### Identifiers
- `recipient_id`: Individual contact identifier
- `mailing_id`: Specific email send identifier
- `campaign_id`: Marketing campaign grouping
- `content_id`: Content variant tracking (A/B testing)

### Event Data
- `event_type`: Primary dimension for engagement analysis
- `event_timestamp`: Precise timing of recipient actions
- `click_name` & `url`: Link performance tracking

### Segmentation
- `recipient_type`: Filter test vs. production recipients
- `body_type`: HTML vs. Plain Text performance
- `suppression_reason`: List hygiene and compliance

## Downstream Analysis Suggestions

### 1. **Campaign Performance Dashboard**
Calculate key email metrics by campaign:
- Open rate: `COUNT(event_type = 'Opened') / COUNT(event_type = 'Sent')`
- Click-through rate: `COUNT(event_type = 'Clicked') / COUNT(event_type = 'Sent')`
- Bounce rate: `COUNT(event_type = 'Bounced') / COUNT(event_type = 'Sent')`
- Group by `campaign_id`, `mailing_id`, and `submission_date`

### 2. **Content Variant Analysis**
Compare performance across different email content versions:
- Segment by `content_id` and `body_type`
- Analyze which variants drive higher engagement
- Identify optimal send times using `event_timestamp`

### 3. **Recipient Engagement Scoring**
Build recipient-level engagement profiles:
- Aggregate events per `recipient_id` over time windows
- Calculate recency, frequency, and engagement depth
- Identify highly engaged vs. inactive recipients for list segmentation

### 4. **Link Performance Analysis**
Track which CTAs and destinations drive engagement:
- Aggregate clicks by `click_name` and `url`
- Calculate click-through rates per link
- Identify top-performing content elements and conversion paths
- Optimize email layout based on click patterns

## Owners

- cbeck@mozilla.com

## Data Quality Notes

- Records are partitioned by `submission_date` which should align with the date component of `event_timestamp`
- Filter `recipient_type` to exclude test/seed recipients for production metrics
- Some fields may be null depending on the `event_type` (e.g., `click_name` only populated for click events)
- `suppression_reason` provides critical context for bounce and unsubscribe events

## Related Tables

- Consider joining with campaign metadata tables for campaign names and descriptions
- Link with recipient/contact tables for demographic and behavioral attributes
- Combine with conversion/revenue data to calculate email marketing ROI
