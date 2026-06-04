#!/bin/sh
set -eu

BASE_URL="${1:-http://localhost:5000}"

echo "ShadowMe smoke test: $BASE_URL"

curl -fsS "$BASE_URL/health" | python -c "import json,sys; d=json.load(sys.stdin); assert d['status']=='healthy'; print('[OK] health version=%s restaurants=%s' % (d['version'], d['restaurant_count']))"

curl -fsS -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"weekend friends recommendation"}' |
  python -c "import json,sys; d=json.load(sys.stdin); assert d['success']; x=d['data']; print('[OK] chat identity=%s restaurants=%s activities=%s' % (x['identity_mode'], len(x['recommendations']), len(x['activities'])))"

TASK_ID=$(curl -fsS -X POST "$BASE_URL/api/queue-monitor/start" \
  -H "Content-Type: application/json" \
  -d '{"restaurant_name":"demo-restaurant","target_count":5}' |
  python -c "import json,sys; d=json.load(sys.stdin); assert d['success']; print(d['data']['task_id'])")
echo "[OK] queue monitor task=$TASK_ID"

curl -fsS "$BASE_URL/api/monitors/check-all" |
  python -c "import json,sys; d=json.load(sys.stdin); assert d['success']; x=d['data']; print('[OK] monitors active=%s triggered=%s' % (x['active_monitors'], x['any_triggered']))"

curl -fsS -X POST "$BASE_URL/api/ride-hailing" \
  -H "Content-Type: application/json" \
  -d '{"origin":"current location","destination":"demo destination","car_type":"express"}' |
  python -c "import json,sys; d=json.load(sys.stdin); assert d['success'] and d['data']['status']=='success'; x=d['data']; print('[OK] ride wait=%smin price=%s' % (x['driver_info']['wait_time_minutes'], x['estimated_price']))"

curl -fsS -X POST "$BASE_URL/api/proactive-check" \
  -H "Content-Type: application/json" \
  -d '{"hour":2,"weekday":2}' |
  python -c "import json,sys; d=json.load(sys.stdin); assert d['data']['reason']=='quiet_hours'; print('[OK] proactive quiet_hours')"

curl -fsS -X POST "$BASE_URL/api/proactive-check" \
  -H "Content-Type: application/json" \
  -d '{"hour":12,"weekday":2,"identity_mode":"rescue"}' |
  python -c "import json,sys; d=json.load(sys.stdin); assert d['data']['reason']=='user_busy'; print('[OK] proactive user_busy')"

curl -fsS -X POST "$BASE_URL/api/proactive-feedback" \
  -H "Content-Type: application/json" \
  -d '{"action":"reject"}' |
  python -c "import json,sys; d=json.load(sys.stdin); assert d['data']['recorded']; print('[OK] proactive feedback cooldown=%sh' % d['data']['cooldown_hours'])"

curl -fsS "$BASE_URL/api/sandbox/status" |
  python -c "import json,sys; d=json.load(sys.stdin); assert d['success']; x=d['data']; print('[OK] sandbox restaurants=%s activities=%s events=%s' % (x['restaurant_count'], x['activity_count'], len(x['recent_events'])))"

echo "Smoke test passed."
