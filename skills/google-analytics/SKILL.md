---
name: google-analytics
description: Integrate Google Analytics 4 (GA4) for website analytics, traffic analysis, user behavior tracking, and conversion monitoring. Use when analyzing website performance, tracking user engagement, or measuring marketing effectiveness.
---

# Google Analytics 4 Integration

Website analytics, traffic analysis, and user behavior tracking with GA4.

## When to Use

- Tracking website traffic
- Analyzing user behavior
- Measuring conversion rates
- Monitoring marketing campaigns
- Understanding audience demographics
- Tracking e-commerce performance
- Real-time visitor monitoring

## Setup

### GA4 Property Creation

1. Go to https://analytics.google.com
2. Create account
3. Create property (GA4)
4. Get Measurement ID (G-XXXXXXXXXX)
5. Add tracking code to website

### Hugo Integration

```html
<!-- layouts/partials/head.html -->
<head>
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
  </script>
</head>
```

### hugo.toml Configuration

```toml
[params]
  googleAnalytics = "G-XXXXXXXXXX"

[services]
  [services.googleAnalytics]
    ID = "G-XXXXXXXXXX"
```

## Key Metrics

### Traffic Metrics

| Metric | Description | Goal |
|--------|-------------|------|
| **Users** | Unique visitors | Increase |
| **Sessions** | Total visits | Increase |
| **Pageviews** | Total pages viewed | Increase |
| **Avg. Session Duration** | Time on site | Increase |
| **Bounce Rate** | Single-page visits | Decrease |

### Acquisition Channels

- **Organic Search** - Google, Bing
- **Direct** - Typed URL
- **Referral** - Other websites
- **Social** - Facebook, Twitter, LinkedIn
- **Paid** - Google Ads, Facebook Ads

### Engagement Metrics

- **Engagement Rate** - Engaged sessions / Total sessions
- **Engaged Sessions** - 10+ seconds, conversion, or 2+ pageviews
- **Average Engagement Time** - Time actively engaged
- **Pages per Session** - Depth of visit

## GA4 API Integration

### Setup API Access

```bash
# 1. Create Google Cloud Project
# 2. Enable Google Analytics Data API
# 3. Create Service Account
# 4. Download JSON key
# 5. Grant GA4 access to service account
```

### Python Client

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)

# Initialize client
client = BetaAnalyticsDataClient.from_service_account_json(
    "service_account_key.json"
)

# Run report
request = RunReportRequest(
    property="properties/123456789",
    dimensions=[Dimension(name="date")],
    metrics=[Metric(name="activeUsers")],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
)

response = client.run_report(request)

# Process results
for row in response.rows:
    print(f"Date: {row.dimension_values[0].value}")
    print(f"Users: {row.metric_values[0].value}")
```

### Common Reports

#### 1. Daily Traffic (Last 30 Days)

```python
def get_daily_traffic():
    request = RunReportRequest(
        property="properties/123456789",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="pageViews"),
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        order_bys=[
            {
                "dimension": {"dimension_name": "date"},
                "desc": False,
            }
        ],
    )
    
    return client.run_report(request)
```

#### 2. Top Pages

```python
def get_top_pages():
    request = RunReportRequest(
        property="properties/123456789",
        dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration"),
        ],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        limit=10,
        order_bys=[
            {
                "metric": {"metric_name": "screenPageViews"},
                "desc": True,
            }
        ],
    )
    
    return client.run_report(request)
```

#### 3. Traffic Sources

```python
def get_traffic_sources():
    request = RunReportRequest(
        property="properties/123456789",
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="engagementRate"),
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        order_bys=[
            {
                "metric": {"metric_name": "sessions"},
                "desc": True,
            }
        ],
    )
    
    return client.run_report(request)
```

## Real-Time Monitoring

### Current Visitors

```python
def get_realtime_users():
    request = RunReportRequest(
        property="properties/123456789",
        metrics=[Metric(name="activeUsers")],
    )
    
    response = client.run_report(request)
    return int(response.rows[0].metric_values[0].value)

# Usage
current_users = get_realtime_users()
print(f"Users on site right now: {current_users}")
```

## Conversion Tracking

### Setup Events

```javascript
// Track button click
gtag('event', 'click', {
  'event_category': 'engagement',
  'event_label': 'newsletter_signup',
  'value': 1
});

// Track form submission
gtag('event', 'form_submit', {
  'event_category': 'conversion',
  'event_label': 'contact_form',
  'value': 1
});

// Track purchase
gtag('event', 'purchase', {
  'event_category': 'ecommerce',
  'value': 99.99,
  'currency': 'USD'
});
```

### Custom Events in Hugo

```html
<!-- layouts/partials/analytics-events.html -->
<script>
  function trackEvent(category, action, label, value) {
    gtag('event', action, {
      'event_category': category,
      'event_label': label,
      'value': value
    });
  }
  
  // Track outbound links
  document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.addEventListener('click', function() {
      trackEvent('outbound', 'click', this.href, 1);
    });
  });
  
  // Track file downloads
  document.querySelectorAll('a[href$=".pdf"]').forEach(link => {
    link.addEventListener('click', function() {
      trackEvent('download', 'pdf', this.href, 1);
    });
  });
</script>
```

## Dashboard Examples

### Weekly Traffic Summary

```python
def generate_weekly_report():
    """Generate weekly traffic summary"""
    
    # Get metrics
    traffic = get_daily_traffic()
    top_pages = get_top_pages()
    sources = get_traffic_sources()
    
    # Format report
    report = f"""
# Weekly Traffic Report
    
## Summary
- Total Users: {total_users:,}
- Total Sessions: {total_sessions:,}
- Total Pageviews: {total_pageviews:,}
- Avg. Engagement Rate: {avg_engagement:.1f}%

## Top Pages
"""
    
    for row in top_pages.rows[:5]:
        report += f"- {row.dimension_values[0].value}: {row.metric_values[0].value} views\n"
    
    report += "\n## Traffic Sources\n"
    
    for row in sources.rows:
        report += f"- {row.dimension_values[0].value}: {row.metric_values[0].value} sessions\n"
    
    return report
```

## Best Practices

1. **Set up goals** - Define conversions
2. **Enable enhanced measurement** - Auto-track scrolls, outbound clicks
3. **Create custom audiences** - Segment users
4. **Link Google Search Console** - SEO insights
5. **Set up filters** - Exclude internal traffic
6. **Regular reviews** - Weekly/monthly analysis
7. **A/B testing** - Test changes with experiments

## Resources

- **GA4 Docs:** https://support.google.com/analytics/answer/10089681
- **API Docs:** https://developers.google.com/analytics/devguides/reporting/data/v1
- **Demo Account:** https://support.google.com/analytics/answer/6367342

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*
