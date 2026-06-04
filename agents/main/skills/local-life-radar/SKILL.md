---
name: local-life-radar
description: One-shot local life recommendations (restaurants + weather + identity detection) via the /api/chat endpoint. Returns real-time queue times and open status from mock backend.
metadata: {"openclaw": {"emoji": "📍", "always": true}}
user-invocable: true
---

# local-life-radar

## Purpose
Get restaurant recommendations, weather info, and identity mode detection in a single API call.

## When to Use
Whenever the user asks about food, restaurants, activities, or needs recommendations.

## The ONLY Command You Need

Use `exec` with curl (NOT web_fetch — it blocks internal addresses):

```bash
curl -s -X POST http://host.docker.internal:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"<user raw message>"}'
```

This one call returns everything:
```json
{
  "success": true,
  "data": {
    "identity_mode": "rescue|dater|explorer|commuter|solo",
    "style_hint": "how to talk to the user",
    "recommendations": [
      {
        "name": "Restaurant",
        "cuisine": "Type",
        "address": "Address",
        "distance": 200,
        "rating": 4.6,
        "price": 15,
        "wait_time": 2,
        "queue_count": 0,
        "open_status": true,
        "open_hours": "06:00-10:00",
        "highlight": "200m - 5min prep",
        "tags": ["tag1"]
      }
    ],
    "activities": [
      {
        "name": "活动名称",
        "category": "类别",
        "address": "地址",
        "distance": 500,
        "rating": 4.7,
        "price": 0,
        "duration": 90,
        "crowd_level": "中等",
        "weather_suitable": ["晴", "多云"],
        "open_hours": "10:00-22:00",
        "highlight": "亮点描述"
      }
    ],
    "weather": {
      "condition": "晴",
      "temperature": 22,
      "humidity": 45
    },
    "memory": {
      "last_mode": "solo",
      "last_topic": "吃饭",
      "turn_count": 1
    }
  }
}
```

## Mode-Specific Filtering (done automatically by API)

| Mode | Filter Strategy |
|------|----------------|
| **commuter** | <500m, fast prep, no queue |
| **dater** | Rating >4.5, private rooms, romantic |
| **solo** | Solo-friendly, delivery, comfortable |
| **explorer** | Unique/new, Instagram-worthy |
| **rescue** | <1000m, must be open now |

## Response Rules

1. Present up to 3 recommendations from the API response
2. Include: name, address, distance, rating, price, highlight, wait_time, open_status
3. Adapt your tone to match `style_hint`
4. Mention weather when relevant
5. NEVER fabricate data — if `recommendations` is empty, say so honestly
6. NEVER use web_search or web_fetch
