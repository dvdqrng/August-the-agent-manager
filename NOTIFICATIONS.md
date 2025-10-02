# 🔔 August's Proactive Notification System

## Overview

August now proactively sends you updates about task and agent activity! Stay in the loop without constantly checking.

## What August Notifies You About

### 1. ✅ Task State Changes
When any task changes state (Backlog → In Progress → Review → Done), August sends you an update:

```
🏃 Task Updated

🔴 Fix Email Sync Bug
Agent: 💻 engineer
Status: IN_PROGRESS

ID: TASK-ABC123
```

### 2. 🚨 Blocked Task Alerts
When a task becomes blocked, you get an immediate alert:

```
🚨 2 Task(s) Blocked!

❌ Vertex AI Migration
   Agent: 💻 engineer

❌ Analytics Export
   Agent: 📊 analyst

These need your attention to unblock!
```

### 3. ⏰ Stale P0 Alerts
If a P0 (critical) task has been in progress >24 hours without updates:

```
⏰ P0 Task Alert

2 critical task(s) in progress >24h:

🔴 Email Sync Fix
   💻 engineer

Should we check on progress or escalate?
```

### 4. 🎉 Task Completion Celebrations
When a task moves to DONE, August celebrates with you:

```
🎉 Task Completed!

✅ Implement Dark Mode
Agent: 🎨 Designer

Great work! Keep the momentum going!
```

### 5. 🌅 Daily Summaries
Every morning at 9:00 AM, August sends a summary of active work:

```
🌅 Daily Summary - October 2, 2025

🏃 In Progress (3)
• Email sync fix (💻)
• Paywall UI (🎨)
• Voice improvements (💻)

👀 In Review (1)
• Cache optimization (🏗️)

All clear on blockers!

Have a productive day! 🚀
```

### 6. ☕ Standup Reminders
At 9:30 AM daily, August reminds you to check the standup:

```
☕ Good morning!

Ready for today's standup?

Send /standup to see what the team is working on.
```

## Notification Settings

### Current Settings
- ✅ Task state changes: **ON**
- ✅ Daily summary: **9:00 AM**
- ✅ Standup reminder: **9:30 AM**
- ✅ Blocked task alerts: **ON**
- ✅ P0 stale alerts: **ON**
- ✅ Completion celebrations: **ON**

### How It Works

**Background Scheduler**
- Runs every 5 minutes
- Checks for task changes
- Monitors P0 tasks
- Sends time-based notifications

**Smart Detection**
- Only notifies about NEW changes
- Prevents duplicate notifications
- Batches related updates

## Benefits

### Stay Informed
- Know immediately when tasks change
- Don't miss critical blockers
- Celebrate wins with the team

### Reduce Manual Checks
- No need to constantly run `/standup`
- August tells you when things change
- Focus on building, not checking status

### Catch Problems Early
- Stale P0 alerts prevent forgotten work
- Blocked task alerts enable quick unblocking
- Proactive PM oversight

## Technical Details

### Files
- `notifications.py` - Notification manager and scheduler
- `bot.py` - Integration with August

### Architecture
```
┌──────────────────┐
│ Notification     │
│ Scheduler        │ ◄── Runs every 5 min
└────────┬─────────┘
         │
    ┌────▼─────┐
    │  Check:  │
    │ - Tasks  │
    │ - States │
    │ - Time   │
    └────┬─────┘
         │
    ┌────▼──────┐
    │  Send     │
    │  Update   │──► Telegram
    └───────────┘
```

### Notification Types

**Real-time** (within 5 minutes)
- Task state changes
- Blocked task alerts
- Task completions

**Scheduled** (exact time)
- Daily summaries (9:00 AM)
- Standup reminders (9:30 AM)

**Conditional** (when threshold met)
- P0 stale alerts (>24h)

## Customization (Coming Soon)

Future notification preferences:

```
/notify_settings

Customize your notifications:
• Daily summary time: 9:00 AM
• Standup reminder: ON/OFF
• Task state changes: ON/OFF
• Blocked alerts: ON/OFF
• P0 stale threshold: 24h
• Quiet hours: 8 PM - 8 AM
```

## Examples

### Scenario 1: Morning Routine
```
9:00 AM - Daily summary arrives
9:30 AM - Standup reminder
10:15 AM - "🏃 Task Updated: Email sync fix → IN_PROGRESS"
```

### Scenario 2: Critical Alert
```
2:45 PM - "🚨 Task Blocked! Vertex migration needs API key"
[You unblock immediately]
3:00 PM - "🏃 Task Updated: Vertex migration → IN_PROGRESS"
```

### Scenario 3: Completion Celebration
```
5:30 PM - "🎉 Task Completed! Dark mode implementation"
[Team celebrates]
6:00 PM - Next task automatically suggested
```

## FAQ

### Q: Can I turn off notifications?
A: Currently all notifications are ON. Custom preferences coming soon.

### Q: What if I get too many notifications?
A: August is smart about batching. He won't spam you with every small change.

### Q: Can I change the summary time?
A: Not yet, but notification settings are on the roadmap!

### Q: Do notifications work if the bot restarts?
A: Yes! The scheduler restarts automatically with the bot.

### Q: What about weekends?
A: Currently sends 7 days/week. Weekend quiet hours coming soon.

## Testing

### Test Immediate Notifications
1. Create a task: `"Create a test task"`
2. Wait ~1 minute
3. Update it via conversation
4. Should receive notification within 5 min

### Test Daily Summary
1. Wait until 9:00 AM
2. Should receive daily summary automatically
3. Or manually trigger: (command coming soon)

### Test Blocked Alert
1. Create a task
2. Mark it as BLOCKED
3. Should receive alert within 5 min

---

**August is now your proactive PM!** He'll keep you informed without you asking. 🎯
