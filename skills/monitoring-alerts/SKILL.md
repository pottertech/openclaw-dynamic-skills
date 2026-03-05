---
name: monitoring-alerts
description: System monitoring, uptime tracking, performance metrics, and alerting setup. Use when monitoring server health, tracking service uptime, setting up alerts, or implementing observability.
---

# Monitoring & Alerting

System monitoring, uptime tracking, and alerting for services and infrastructure.

## When to Use

- Server health monitoring
- Service uptime tracking
- Performance metrics collection
- Alert configuration
- Incident response
- Log aggregation
- Dashboard creation

## Monitoring Tools

### Prometheus + Grafana

**Setup:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
  
  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"

volumes:
  prometheus_data:
  grafana_data:
```

**Prometheus Config:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
  
  - job_name: 'services'
    static_configs:
      - targets: ['localhost:8845', 'localhost:8880', 'localhost:8188']
```

### Uptime Monitoring

**Uptime Kuma:**
```yaml
version: '3.8'

services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    ports:
      - "3001:3001"
    volumes:
      - ./kuma-data:/app/data
    restart: always
```

**Monitor Your Services:**
- Lookup Service: http://localhost:8845/health
- Kokoro TTS: http://localhost:8880
- ComfyUI: http://localhost:8188
- ACE-Step: http://localhost:7860

### Health Check Script

```python
#!/usr/bin/env python3
# health_check.py

import requests
import smtplib
from datetime import datetime

SERVICES = {
    'Lookup Service': 'http://localhost:8845/health',
    'Kokoro TTS': 'http://localhost:8880',
    'ComfyUI': 'http://localhost:8188',
    'ACE-Step': 'http://localhost:7860',
}

def check_service(name, url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, f"{name} is UP"
        else:
            return False, f"{name} returned {response.status_code}"
    except Exception as e:
        return False, f"{name} is DOWN: {str(e)}"

def send_alert(message):
    # Send email alert
    # Configure SMTP settings
    pass

def main():
    alerts = []
    
    for name, url in SERVICES.items():
        status, message = check_service(name, url)
        print(f"[{datetime.now()}] {message}")
        
        if not status:
            alerts.append(message)
    
    if alerts:
        send_alert("\n".join(alerts))

if __name__ == '__main__':
    main()
```

## Log Aggregation

### Loki + Promtail

```yaml
version: '3.8'

services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
  
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
```

### Log Rotation

```bash
# /etc/logrotate.d/openclaw
/tmp/lookup_service.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 skipppotter staff
}
```

## Alerting

### Email Alerts

```python
def send_email_alert(subject, body):
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText(body)
    msg['Subject'] = f"[ALERT] {subject}"
    msg['From'] = 'alerts@example.com'
    msg['To'] = 'admin@example.com'
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)
```

### Slack Alerts

```python
def send_slack_alert(message):
    import requests
    
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    payload = {
        "text": f"🚨 Alert: {message}",
        "username": "Monitor Bot",
        "icon_emoji": ":warning:"
    }
    
    requests.post(webhook_url, json=payload)
```

### Discord Alerts

```python
def send_discord_alert(message):
    import requests
    
    webhook_url = "https://discord.com/api/webhooks/YOUR/WEBHOOK"
    
    payload = {
        "content": f"🚨 **Alert**: {message}",
        "username": "Monitor Bot"
    }
    
    requests.post(webhook_url, json=payload)
```

## Metrics to Monitor

### System Metrics

- CPU usage
- Memory usage
- Disk space
- Network I/O
- Load average

### Application Metrics

- Request rate
- Response time
- Error rate
- Active connections
- Queue depth

### Business Metrics

- Daily active users
- Conversion rate
- Revenue
- Signups

## Dashboard Examples

### Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "Services Overview",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"services\"}"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

## Best Practices

1. **Monitor everything** - If it can break, monitor it
2. **Set meaningful thresholds** - Avoid alert fatigue
3. **Test alerts** - Verify they work
4. **Document runbooks** - How to respond
5. **Regular reviews** - Update thresholds
6. **Redundancy** - Multiple alert channels
7. **Escalation** - Define on-call rotation

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*
