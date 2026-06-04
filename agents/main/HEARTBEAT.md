# LiHua Heartbeat Plan

## Schedule

- **Interval**: Every 1 minute
- **Active hours**: 7:00-23:00 (outside = silence, respond "OK" only. Server triggers at hour 7/11/18, heartbeat fires every minute)
- **Isolated session**: Yes (heartbeat runs independently, does not pollute user session)

## Check Pipeline (6 Steps)

Execute in order every heartbeat tick:

### 1. Queue Monitor Check
```
curl -s http://host.docker.internal:5000/api/monitors/check-all
```
- If `any_triggered` is true: alert user immediately with restaurant name, current queue count, and offer ride-hailing

### 2. Pending Notifications
```
curl -s http://host.docker.internal:5000/api/notifications/pending
```
- Deliver any pending notifications to user

### 3. Flash Deals
```
curl -s http://host.docker.internal:5000/api/flash-deals
```
- If active deals exist, mention the best one (highest discount or shortest expiry)

### 4. Proactive Reminder (hour-bounded)
Get Beijing time (hour, weekday), then:
```
curl -s -X POST http://host.docker.internal:5000/api/proactive-check \
  -H "Content-Type: application/json" \
  -d '{"hour":<hour>,"weekday":<0-6>,"identity_mode":"<last_mode_if_available>"}'
```
- Target windows: 7:00 (breakfast), 11:00 (lunch), 18:00 (dinner), Fri 17:00 (weekend plan)
- If `should_notify` is true: deliver the notification to user
- Skip if reason is `quiet_hours`, `daily_limit`, `user_busy`, or `recently_rejected`

### 5. Critical Events
```
curl -s http://host.docker.internal:5000/api/events?limit=3
```
- Alert user on: `sudden_full` (nearby restaurant suddenly packed), `rain_start` (bring umbrella), `temp_change` (dress warning)
- Ignore: `peak_surge`, `traffic`, routine fluctuations

### 6. Fallback
If nothing important to report, respond with just "OK" (one word, no explanation).

## Proactive Limits

| Rule | Value |
|------|-------|
| Max reminders/day | 3 |
| Quiet hours | 23:00-7:00 |
| No interruption | When user in rescue mode (server returns `user_busy`) |
| Rejection cooldown | 24 hours after user rejects (server returns `recently_rejected`) |
