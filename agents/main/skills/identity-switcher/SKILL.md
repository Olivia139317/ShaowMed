---
name: identity-switcher
description: Analyze user messages to detect current life state (commuter/dater/solo/explorer/rescue) via the identity API. Determines LiHua's response style.
metadata: {"openclaw": {"emoji": "🔄", "always": true}}
user-invocable: true
---

# identity-switcher

## Purpose
Detect the user's current life state so LiHua can adapt tone and recommendations.

## When to Use
Call this FIRST for every user message before making recommendations.

## Primary Method: One-Step /api/chat

The recommended approach is the one-step `/api/chat` which returns identity + recommendations + activities + weather all at once:

```bash
bash /home/node/.openclaw/workspace/chat.sh "<user raw message>"
```

## Alternative: Standalone Identity Detection

If you only need identity detection without recommendations:

```bash
curl -s -X POST http://host.docker.internal:5000/api/identity \
  -H "Content-Type: application/json" \
  -d '{"message":"<user raw message>"}'
```

The API returns JSON:
```json
{
  "success": true,
  "data": {
    "identity_mode": "commuter|dater|solo|explorer|rescue",
    "style_hint": "description of tone to use",
    "confidence": "high|low",
    "matched_keywords": ["matched", "words"],
    "priority": 1-5
  }
}
```

## Five Modes (Priority Order)

| Priority | Mode | Keywords | Tone |
|----------|------|----------|------|
| 5 (highest) | **rescue** | 急、快、来不及、怎么办、帮我、忘了、紧急 | Cold, fast, direct results only |
| 4 | **dater** | 约会、聚餐、朋友、闺蜜、同学、生日、见面 | Warm, thoughtful, comprehensive |
| 3 | **explorer** | 想去、没去过、打卡、推荐、探索、新地方 | Excited, weather-aware |
| 2 | **commuter** | 上班、地铁、赶时间、堵车、早饭、下班 | Concise, under 30 chars |
| 1 (default) | **solo** | 一个人、宅、累了、夜宵、躺着、失眠 | Gentle, comforting |

## After Detection

1. When using `/api/chat`: read `identity_mode`, `style_hint`, `recommendations`, `activities`, `weather` all from one response
2. When using `/api/identity`: read `data.identity_mode`, then call `/api/chat` or `/api/recommendations` for actual data
3. Adapt your reply tone to match `style_hint`
4. If `confidence` is "low", default to `solo` mode

## Important
- The API does keyword matching; you can apply additional semantic understanding
- When multiple keywords match, priority wins (rescue beats everything)
- Never skip this step before giving recommendations
