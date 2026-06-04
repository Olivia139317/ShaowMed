---
name: ride-hailing
description: Fast path planning and one-click ride hailing via mock-backend API. Book rides, get price estimates, and driver info. Can be chained with queue-monitor alerts.
metadata: {"openclaw": {"emoji": "🚗", "always": true}}
user-invocable: true
---

# ride-hailing

## Purpose
Book a ride with estimated price, wait time, and driver info. Works standalone or chained with queue-monitor alerts.

## When to Use
- User says "帮我叫车" / "打车去XXX" / "叫个快车"
- After queue-monitor alert triggers and user accepts the ride suggestion

## How to Execute

Use `exec` with `curl` (NOT web_fetch):

```bash
curl -s -X POST http://host.docker.internal:5000/api/ride-hailing \
  -H "Content-Type: application/json" \
  -d '{"destination":"<destination>","origin":"<optional>","car_type":"<快车|专车>"}'
```

Response:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "message": "已经帮你叫好快车了，司机大概3分钟后到。预估18元。",
    "driver_info": {
      "plate": "京A88888",
      "car": "白色 丰田卡罗拉",
      "wait_time_minutes": 3
    },
    "estimated_price": 18,
    "route": {
      "distance": "3.5km",
      "duration": "15分钟"
    }
  }
}
```

## Present to User
Format naturally:
```
已叫好快车：
- 车牌：京A88888（白色卡罗拉）
- 到达：约3分钟
- 预估：18元，3.5km，15分钟到
```

## Chaining with Queue Monitor
When queue-monitor triggers and user wants a ride:
1. Get restaurant name from the monitor alert
2. Call ride-hailing with that restaurant as destination
3. Present driver info and ETA

## Important
- Car types: 快车 (default) or 专车
- Origin defaults to "当前位置"
- All prices are simulated mock data
