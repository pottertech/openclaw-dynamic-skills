---
name: cost-optimization
description: Cloud cost optimization, resource tracking, and budget management. Use when analyzing cloud spending, optimizing resource usage, setting up budgets, or reducing infrastructure costs.
---

# Cost Optimization

Cloud cost optimization, resource tracking, and budget management for AWS, GCP, Azure, and other providers.

## When to Use

- Analyzing cloud spending
- Optimizing resource usage
- Setting up budgets and alerts
- Right-sizing instances
- Identifying waste
- Cost allocation
- Forecasting expenses

## Cost Tracking

### AWS Cost Explorer

```python
import boto3

# Initialize client
ce = boto3.client('ce')

# Get costs for last month
response = ce.get_cost_and_usage(
    TimePeriod={
        'Start': '2026-02-01',
        'End': '2026-02-28'
    },
    Granularity='MONTHLY',
    Metrics=['UnblendedCost']
)

print(f"Total: ${response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']}")
```

### GCP Billing

```python
from google.cloud import billing

client = billing.CloudBillingClient()

# Get project costs
project_name = "projects/your-project-id"
# Use Billing API to retrieve costs
```

## Optimization Strategies

### 1. Right-Sizing Instances

```bash
# AWS: Check underutilized instances
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name]'

# Compare with CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
  --start-time 2026-02-01T00:00:00Z \
  --end-time 2026-03-01T00:00:00Z \
  --period 86400 \
  --statistics Average
```

### 2. Reserved Instances

```python
# Calculate RI savings
def calculate_ri_savings(on_demand_cost, ri_cost, term_years):
    annual_savings = (on_demand_cost - ri_cost) * 12
    total_savings = annual_savings * term_years
    roi = (total_savings / (ri_cost * 12 * term_years)) * 100
    
    return {
        'annual_savings': annual_savings,
        'total_savings': total_savings,
        'roi_percent': roi
    }

# Example
savings = calculate_ri_savings(100, 60, 1)
print(f"Annual savings: ${savings['annual_savings']}")
print(f"ROI: {savings['roi_percent']:.1f}%")
```

### 3. Spot Instances

```yaml
# AWS ECS with Spot
Resources:
  SpotFleet:
    Type: AWS::EC2::SpotFleet
    Properties:
      SpotFleetRequestConfigData:
        IamFleetRole: !Ref FleetRole
        AllocationStrategy: lowestPrice
        TargetCapacity: 10
        SpotPrice: 0.05
        LaunchSpecifications:
          - InstanceType: m5.large
            ImageId: ami-12345678
```

### 4. Storage Optimization

```bash
# AWS S3: Find large/old objects
aws s3api list-objects-v2 \
  --bucket my-bucket \
  --query 'Contents[?Size>`1073741824`].[Key,Size,LastModified]'

# Move to Glacier
aws s3api put-object-retention \
  --bucket my-bucket \
  --key large-file.zip \
  --retention '{"Mode":"GOVERNANCE","RetainUntilDate":"2027-01-01"}'
```

## Budget Alerts

### AWS Budget

```yaml
Resources:
  Budget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetName: MonthlyBudget
        BudgetLimit:
          Amount: 1000
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 80
          Subscribers:
            - SubscriptionType: EMAIL
              Address: admin@example.com
```

### GCP Budget

```bash
# Create budget
gcloud billing budgets create \
  --billing-account=000000-000000-000000 \
  --display-name="Monthly Budget" \
  --budget-amount=1000 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

## Cost Allocation

### Tagging Strategy

```python
# Required tags for all resources
REQUIRED_TAGS = {
    'Environment': ['dev', 'staging', 'prod'],
    'Team': ['engineering', 'marketing', 'sales'],
    'Project': ['project-a', 'project-b'],
    'CostCenter': ['cc-001', 'cc-002']
}

# Enforce tagging
def enforce_tagging(resource, tags):
    for key, allowed_values in REQUIRED_TAGS.items():
        if key not in tags:
            raise ValueError(f"Missing required tag: {key}")
        if tags[key] not in allowed_values:
            raise ValueError(f"Invalid value for {key}: {tags[key]}")
```

## Monitoring Dashboard

### Cost Dashboard (Grafana)

```json
{
  "dashboard": {
    "title": "Cloud Costs",
    "panels": [
      {
        "title": "Daily Spend",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(cloud_cost_total)"
          }
        ]
      },
      {
        "title": "Cost by Service",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (service) (cloud_cost_total)"
          }
        ]
      },
      {
        "title": "Budget vs Actual",
        "type": "gauge",
        "targets": [
          {
            "expr": "(actual_cost / budget) * 100"
          }
        ]
      }
    ]
  }
}
```

## Best Practices

1. **Tag everything** - Enable cost allocation
2. **Set budgets** - Get alerts before overspending
3. **Review monthly** - Identify optimization opportunities
4. **Use reserved capacity** - For predictable workloads
5. **Automate shutdown** - Non-prod outside business hours
6. **Monitor waste** - Unused resources, over-provisioning
7. **Right-size regularly** - Adjust based on actual usage

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*
