---
name: proactive-scheduler
description: Trigger proactive reminders at appropriate times based on user routine, weather changes, and behavior patterns. Respects quiet hours and daily limits. Uses exec+curl to call mock-backend API.
metadata: {"openclaw": {"emoji": "⏰", "always": true}}
user-invocable: false
---

# proactive-scheduler

## Purpose
Proactively check if LiHua should send a reminder, without the user asking first. Respects strict restraint principles.

## When to Check
- At routine times (7:00 breakfast, 11:00 lunch, 18:00 dinner, Friday 17:00)
- When weather changes significantly
- When user has been idle
- Weekends (brunch 11:00, dinner 18:00)

## How to Execute

Use `exec` with `curl` (NOT web_fetch):

```bash
curl -s -X POST http://host.docker.internal:5000/api/proactive-check \
  -H "Content-Type: application/json" \
  -d '{"hour":<current hour>,"weekday":<0=Mon>,"identity_mode":"<current_or_last_mode>"}'
```

Response:
```json
{
  "success": true,
  "data": {
    "should_notify": true,
    "notifications": [
      {
        "type": "routine|weather|proactive",
        "message": "快到午饭时间了，今天想吃什么？",
        "priority": "low|medium|high"
      }
    ],
    "weather": "Sunny 22C"
  }
}
```

When `should_notify` is `false`, check `reason`:
- `quiet_hours` (23:00-7:00) — do nothing
- `daily_limit` (3 reminders) — do nothing
- `user_busy` (rescue mode) — do nothing
- `recently_rejected` (24h cooldown) — do nothing
- Otherwise — no notification needed

When the user rejects a proactive reminder ("不用提醒"/"别提醒"/"先不用"):
```bash
curl -s -X POST http://host.docker.internal:5000/api/proactive-feedback \
  -H "Content-Type: application/json" \
  -d '{"action":"reject"}'
```

## Restraint Principles (CRITICAL)

1. **Max 3 proactive reminders per day**
2. **No reminders during quiet hours** (23:00-7:00)
3. **Never interrupt rescue mode** — user is busy
4. **24-hour cooldown after rejection**

## Reminder Types

| Type | Trigger | Example |
|------|---------|---------|
| **routine** | 7:00, 11:00, 18:00, Fri 17:00 | "早上好！早餐想吃啥？" |
| **weather** | Rain forecast | "下午有雨，记得带伞" |
| **proactive** | Friday, weekend no plans | "周五了！周末去哪玩？" |

## Scheduling

This skill is triggered by the heartbeat system (configured in openclaw.json, every 1m). The heartbeat prompt handles timing logic — the skill only needs to provide the API call pattern and restraint rules.

## Important
- Track how many reminders sent today
- Never notify during rescue mode
- If user rejects, avoid same topic for 24 hours
