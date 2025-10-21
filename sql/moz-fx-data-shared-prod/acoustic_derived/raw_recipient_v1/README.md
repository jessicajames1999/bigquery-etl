# Raw Recipient (Acoustic Campaign Data)

## Overview

The `raw_recipient_v1` table contains detailed email engagement data exported from Acoustic Campaign platform. This table captures recipient-level events and interactions with email campaigns, including sends, opens, clicks, bounces, and suppressions. The data is imported from CSV exports provided by Acoustic's Raw Recipient Data Export API.

This table serves as the foundation for analyzing email campaign performance, tracking recipient behavior, and measuring engagement metrics across Mozilla's email marketing initiatives managed through Acoustic Campaign.

## Table Details

- **Database**: `moz-fx-data-shared-prod`
- **Dataset**: `acoustic_derived`
- **Table**: `raw_recipient_v1`
- **Table Type**: Client-level, Incremental
- **Partitioning**: Daily partitioning on `submission_date` field (775 days retention)
- **Clustering**: `event_type`, `recipient_type`, `body_type`
- **Data Source**: [Acoustic Campaign Raw Recipient API](https://developer.goacoustic.com/acoustic-campaign/reference/rawrecipientdataexport)

## Owners

- cbeck@mozilla.com

## Key Columns

| Column | Type | Description |
|--------|------|-------------|
| `recipient_id` | INTEGER | Unique contact identifier |
| `mailing_id` | INTEGER | Specific email send identifier |
| `campaign_id` | INTEGER | Marketing campaign identifier |
| `event_type` | STRING | Email event type (sent, opened, clicked, etc.) |
| `event_timestamp` | DATETIME | When the event occurred |
| `url` | STRING | Clicked link URL (for click events) |
| `suppression_reason` | STRING | Why contact was suppressed |
| `submission_date` | DATE | ETL partition date |

## Downstream Analysis Suggestions

### 1. Email Campaign Performance Dashboard
Analyze campaign effectiveness by aggregating metrics:
- Calculate open rates, click rates, and bounce rates by `campaign_id` and `mailing_id`
- Track engagement trends over time using `event_timestamp` and `submission_date`
- Segment performance by `recipient_type` and `body_type` to optimize targeting
- Identify top-performing content using `content_id` metrics

### 2. Recipient Engagement Scoring
Build recipient engagement profiles:
- Create recipient engagement scores based on frequency and recency of opens/clicks
- Segment recipients into engagement tiers using `recipient_id` event patterns
- Identify at-risk recipients who haven't engaged recently
- Track engagement lifecycle from first send to churn using `event_type` sequences

### 3. Link Performance Analysis
Optimize email content and CTAs:
- Rank top-performing links by `url` and `click_name` across campaigns
- Analyze click patterns by position and content type using `body_type`
- A/B test link placements and messaging across different `mailing_id` variants
- Identify underperforming links that need redesign or removal

### 4. Suppression and Deliverability Analysis
Monitor list health and deliverability:
- Track suppression rates over time by `suppression_reason` categories
- Identify campaigns with high bounce rates using `event_type` = bounced
- Analyze recipient quality by `recipient_type` to improve targeting
- Create alerts for sudden spikes in suppressions or bounces by `campaign_id`

## Usage Notes

- Data is incrementally loaded with daily partitions
- Events are clustered by `event_type`, `recipient_type`, and `body_type` for query optimization
- The `event_timestamp` reflects the Acoustic API user's timezone
- Use `submission_date` for efficient date-range queries with partition filtering
- Multiple event types may exist for a single recipient per mailing (e.g., sent → opened → clicked)
