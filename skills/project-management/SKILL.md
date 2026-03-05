---
name: project-management
description: Project planning, task tracking, team coordination, and workflow management. Use when planning projects, tracking progress, managing teams, or implementing agile workflows.
---

# Project Management

Project planning, task tracking, and team coordination for efficient delivery.

## When to Use

- Project planning and scoping
- Task tracking and assignment
- Sprint planning
- Progress reporting
- Resource allocation
- Risk management
- Team coordination

## Methodologies

### Agile/Scrum

**Sprint Cycle:**
```
Week 1-2: Sprint Planning → Daily Standups → Development → Review → Retrospective
```

**Key Roles:**
- Product Owner - Defines requirements
- Scrum Master - Removes blockers
- Team - Executes work

**Ceremonies:**
- Sprint Planning (2 hours)
- Daily Standup (15 min)
- Sprint Review (1 hour)
- Retrospective (1 hour)

### Kanban

**Board Columns:**
```
Backlog → To Do → In Progress → Review → Done
```

**WIP Limits:**
- To Do: No limit
- In Progress: 3 per person
- Review: 5 max

## Tools

### Task Tracking

**Markdown Task List:**
```markdown
## Sprint 1 (Mar 3-14)

### To Do
- [ ] Design database schema
- [ ] Set up CI/CD pipeline
- [ ] Write API documentation

### In Progress
- [x] Create project repository
- [ ] Implement user authentication

### Done
- [x] Project kickoff meeting
- [x] Requirements gathering
```

### Project Timeline

```markdown
## Timeline

### Phase 1: Foundation (Week 1-2)
- [x] Project setup
- [ ] Database design
- [ ] Basic API

### Phase 2: Features (Week 3-6)
- [ ] User management
- [ ] Core functionality
- [ ] Testing

### Phase 3: Launch (Week 7-8)
- [ ] Performance optimization
- [ ] Documentation
- [ ] Deployment
```

## Planning Templates

### Project Charter

```markdown
# Project Charter

## Overview
- **Project Name:** [Name]
- **Start Date:** [Date]
- **End Date:** [Date]
- **Budget:** [Amount]

## Objectives
1. [Primary objective]
2. [Secondary objective]
3. [Tertiary objective]

## Stakeholders
- **Sponsor:** [Name]
- **Product Owner:** [Name]
- **Team Lead:** [Name]
- **Team Members:** [Names]

## Success Criteria
- [Measurable outcome 1]
- [Measurable outcome 2]
- [Measurable outcome 3]

## Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | High | High | [Plan] |
| [Risk 2] | Medium | Medium | [Plan] |
```

### Sprint Planning

```markdown
# Sprint [N] Plan

## Sprint Goal
[One sentence describing what we'll achieve]

## Capacity
- Total team members: [N]
- Vacation days: [N]
- Available days: [N]
- Story points capacity: [N]

## User Stories

### Story 1: [Title]
- **Points:** [N]
- **Description:** [As a user, I want...]
- **Acceptance Criteria:**
  - [ ] Criterion 1
  - [ ] Criterion 2

### Story 2: [Title]
...

## Tasks
| Task | Assignee | Estimate | Status |
|------|----------|----------|--------|
| [Task 1] | [Name] | 4h | To Do |
| [Task 2] | [Name] | 2h | In Progress |
```

## Progress Tracking

### Daily Standup Template

```markdown
## Daily Standup - [Date]

### [Name 1]
**Yesterday:**
- Completed task A
- Started task B

**Today:**
- Finish task B
- Start task C

**Blockers:**
- Waiting on [X]

### [Name 2]
...
```

### Status Report

```markdown
# Weekly Status Report

## Summary
- **Overall Status:** 🟢 On Track / 🟡 At Risk / 🔴 Behind
- **Sprint Progress:** 60% complete
- **Budget Status:** On track

## Completed This Week
- ✅ Feature A launched
- ✅ Bug fixes deployed
- ✅ Documentation updated

## Planned Next Week
- 📋 Feature B development
- 📋 Performance testing
- 📋 User interviews

## Risks & Issues
| Item | Status | Action |
|------|--------|--------|
| Risk A | Mitigated | [Action taken] |
| Issue B | Active | [Action plan] |

## Metrics
- Velocity: [N] points/sprint
- Burndown: On track
- Quality: [N] bugs found
```

## Resource Management

### Team Capacity

```python
def calculate_team_capacity(team, sprint_days=10):
    """Calculate team capacity for sprint"""
    total_hours = 0
    
    for member in team:
        available_days = sprint_days - member.vacation_days
        hours_per_day = member.hours_per_day
        focus_factor = member.focus_factor  # 0.6-0.8
        
        member_capacity = available_days * hours_per_day * focus_factor
        total_hours += member_capacity
    
    return total_hours

# Example
team = [
    {'vacation_days': 2, 'hours_per_day': 6, 'focus_factor': 0.7},
    {'vacation_days': 0, 'hours_per_day': 6, 'focus_factor': 0.7},
    {'vacation_days': 1, 'hours_per_day': 6, 'focus_factor': 0.7},
]

capacity = calculate_team_capacity(team)
print(f"Team capacity: {capacity} hours")
```

### Budget Tracking

```python
def track_budget(budget, actual_spend, forecast):
    """Track project budget"""
    remaining = budget - actual_spend
    variance = budget - forecast
    variance_percent = (variance / budget) * 100
    
    return {
        'budget': budget,
        'actual': actual_spend,
        'remaining': remaining,
        'forecast': forecast,
        'variance': variance,
        'variance_percent': variance_percent,
        'status': 'On Track' if variance_percent > -10 else 'At Risk'
    }

# Example
status = track_budget(100000, 45000, 95000)
print(f"Budget status: {status['status']}")
print(f"Variance: {status['variance_percent']:.1f}%")
```

## Best Practices

1. **Clear goals** - Define success criteria upfront
2. **Regular communication** - Daily standups, weekly reports
3. **Track progress** - Use boards, charts, metrics
4. **Manage risks** - Identify early, mitigate proactively
5. **Document decisions** - Keep records of key choices
6. **Retrospectives** - Learn and improve each sprint
7. **Celebrate wins** - Recognize team achievements

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*
