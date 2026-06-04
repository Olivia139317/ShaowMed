---
name: queue-monitor
description: 7x24 background task for monitoring restaurant queue times. Start monitoring, check status, and trigger proactive alerts when queue drops to target level. Uses exec+curl to call mock-backend API.
metadata: {"openclaw": {"emoji": "👀", "always": true}}
user-invocable: true
---

# queue-monitor

## Purpose
Monitor restaurant queues as a background task. When queue count drops to target, proactively alert the user and suggest calling a ride.

## When to Use
When user says: "帮我盯着海底捞排队" / "排到5桌时叫我" / "有位了告诉我"

## How to Execute

Use `exec` with `curl` (NOT web_fetch — it blocks internal addresses).

### Start Monitoring
```bash
curl -s -X POST http://host.docker.internal:5000/api/queue-monitor/start \
  -H "Content-Type: application/json" \
  -d '{"restaurant_name":"海底捞","target_count":5}'
```

Response includes `task_id` — SAVE THIS. Example response:
```json
{
  "success": true,
  "data": {
    "task_id": "queue_1717000000",
    "status": "monitoring_started",
    "message": "已开始监控海底捞(中关村店)，当前排队15桌，到剩5桌时提醒你。",
    "current_queue": 15
  }
}
```

### Check Status
```bash
curl -s http://host.docker.internal:5000/api/queue-monitor/check/<task_id>
```

When `data.triggered` is `true`, alert the user immediately with `data.message`.

### Stop Monitoring
```bash
curl -s -X POST http://host.docker.internal:5000/api/queue-monitor/stop/<task_id>
```

## Workflow: Queue -> Alert -> Ride

1. User asks to monitor a restaurant queue
2. Call start API, tell user current status
3. Remind user to check back, or check when they message you next
4. When triggered, proactively alert user
5. Ask if they want to call a ride via `ride-hailing`
6. If yes, call ride-hailing API

## Proactive Check Pattern
On each new user message, quickly check active monitors:
```bash
curl -s http://host.docker.internal:5000/api/queue-monitor/check/<saved_task_id>
```
If triggered, immediately alert user before processing their new message.

## Important
- Always save the `task_id` from the start response
- The mock-backend sandbox changes queue counts every 10 seconds
- Between checks, queue counts can go up OR down
- Monitoring state persists in the mock-backend until stopped
