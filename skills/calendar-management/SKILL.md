---
name: calendar-management
description: Calendar scheduling, meeting coordination, time management, and appointment automation. Use when scheduling meetings, managing calendars, coordinating events, or optimizing time allocation.
---

# Calendar Management

Calendar scheduling, meeting coordination, and time management automation.

## When to Use

- Scheduling meetings
- Managing multiple calendars
- Setting up recurring events
- Time blocking
- Appointment booking
- Meeting coordination
- Calendar automation

## Calendar APIs

### Google Calendar

**Setup:**
```bash
# Enable Google Calendar API
# Create service account
# Download JSON key
# Share calendar with service account
```

**Python Integration:**
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Authenticate
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = service_account.Credentials.from_service_account_file(
    'service_account.json', scopes=SCOPES)

service = build('calendar', 'v3', credentials=creds)
```

**Create Event:**
```python
def create_event(summary, start_time, end_time, attendees=None):
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/New_York',
        },
        'attendees': [{'email': email} for email in (attendees or [])],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    
    event = service.events().insert(
        calendarId='primary', body=event).execute()
    
    return event['id']

# Usage
create_event(
    summary='Team Standup',
    start_time=datetime(2026, 3, 6, 9, 0),
    end_time=datetime(2026, 3, 6, 9, 30),
    attendees=['team@example.com']
)
```

**Find Free Time:**
```python
def find_free_time(duration_minutes=60, days_ahead=7):
    """Find available time slots"""
    now = datetime.now()
    end = now + timedelta(days=days_ahead)
    
    free_busy = service.freebusy().query(body={
        'timeMin': now.isoformat(),
        'timeMax': end.isoformat(),
        'calendars': {'primary': {}},
    }).execute()
    
    # Parse busy periods and find gaps
    calendar = free_busy['calendars']['primary']
    busy_periods = calendar.get('busy', [])
    
    # Return available slots
    return find_gaps(busy_periods, duration_minutes)
```

## Scheduling Workflows

### Meeting Scheduler

```python
def schedule_meeting(topic, duration, participants, preferred_times):
    """Schedule meeting with multiple participants"""
    
    # Find common availability
    common_slots = []
    for time in preferred_times:
        if all(is_available(participant, time, duration) 
               for participant in participants):
            common_slots.append(time)
    
    if not common_slots:
        return "No common time found"
    
    # Book first available slot
    chosen_time = common_slots[0]
    event_id = create_event(
        summary=topic,
        start_time=chosen_time,
        end_time=chosen_time + timedelta(minutes=duration),
        attendees=participants
    )
    
    return f"Meeting scheduled: {chosen_time}"
```

### Recurring Meetings

```python
def create_recurring_meeting(summary, start_time, duration, recurrence_rule):
    """Create recurring meeting"""
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': (start_time + timedelta(minutes=duration)).isoformat(),
            'timeZone': 'America/New_York',
        },
        'recurrence': [recurrence_rule],
    }
    
    return service.events().insert(
        calendarId='primary', body=event).execute()

# Examples
# Daily standup
create_recurring_meeting(
    summary='Daily Standup',
    start_time=datetime(2026, 3, 6, 9, 0),
    duration=15,
    recurrence_rule='RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR'
)

# Weekly team meeting
create_recurring_meeting(
    summary='Team Meeting',
    start_time=datetime(2026, 3, 10, 14, 0),
    duration=60,
    recurrence_rule='RRULE:FREQ=WEEKLY;BYDAY=MO'
)
```

## Time Blocking

### Daily Schedule Template

```python
def create_daily_schedule(date, working_hours=(9, 17)):
    """Create time-blocked daily schedule"""
    schedule = {
        'deep_work': [],
        'meetings': [],
        'admin': [],
        'breaks': []
    }
    
    # Block morning deep work
    schedule['deep_work'].append({
        'start': f"{date}T{working_hours[0]:02d}:00",
        'end': f"{date}T{working_hours[0]+3:02d}:00",
        'task': 'Deep work - priority tasks'
    })
    
    # Add lunch break
    schedule['breaks'].append({
        'start': f"{date}T12:00",
        'end': f"{date}T13:00",
        'task': 'Lunch break'
    })
    
    # Block afternoon for meetings
    schedule['meetings'].append({
        'start': f"{date}T14:00",
        'end': f"{date}T16:00",
        'task': 'Meetings & collaboration'
    })
    
    # End of day admin
    schedule['admin'].append({
        'start': f"{date}T16:00",
        'end': f"{date}T{working_hours[1]:02d}:00",
        'task': 'Email, planning, wrap-up'
    })
    
    return schedule
```

## Meeting Templates

### 1:1 Meeting

```markdown
# 1:1 Meeting - [Name]

## Date: [Date]

## Check-in
- How are you doing?
- What's on your mind?

## Topics
1. [Topic 1]
2. [Topic 2]
3. [Topic 3]

## Updates
- Projects: [Status]
- Blockers: [List]
- Wins: [Celebrations]

## Action Items
- [ ] [Action 1] - [Owner]
- [ ] [Action 2] - [Owner]

## Next Meeting: [Date]
```

### Team Meeting

```markdown
# Team Meeting - [Date]

## Agenda

### 1. Round Robin (5 min each)
- [Name 1]: [Update]
- [Name 2]: [Update]

### 2. Key Metrics (10 min)
- [Metric 1]: [Value]
- [Metric 2]: [Value]

### 3. Discussion Topics (30 min)
- [Topic 1]
- [Topic 2]

### 4. Action Items (10 min)
- [ ] [Action 1] - [Owner] - [Due]
- [ ] [Action 2] - [Owner] - [Due]

## Notes
[Meeting notes]

## Next Meeting: [Date]
```

## Automation

### Auto-Decline Conflicts

```python
def handle_conflicts(event):
    """Automatically handle scheduling conflicts"""
    conflicts = check_conflicts(event)
    
    if conflicts:
        # Decline and suggest alternatives
        decline_event(event['id'])
        suggest_alternatives(event, conflicts)
    else:
        accept_event(event['id'])
```

### Meeting Reminders

```python
def send_meeting_reminders():
    """Send reminders for upcoming meetings"""
    events = get_todays_events()
    
    for event in events:
        if event['start'] - datetime.now() < timedelta(hours=1):
            send_reminder(event)

# Run every 15 minutes via cron
*/15 * * * * python3 calendar_reminders.py
```

## Best Practices

1. **Set clear availability** - Define working hours
2. **Buffer time** - 15 min between meetings
3. **Agendas required** - No agenda, no meeting
4. **Time limits** - Default 30 min, not 60
5. **Batch meetings** - Group on specific days/times
6. **Protect deep work** - Block focus time
7. **Review weekly** - Optimize calendar usage

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*
