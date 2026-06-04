#!/bin/sh
# LiHua Session Start Hook
# Runs on every new session to initialize context

echo "=== LiHua Session Init ==="
echo ""

# 1. Health check
echo "--- Backend Health ---"
HEALTH=$(curl -s http://host.docker.internal:5000/health 2>/dev/null)
if echo "$HEALTH" | grep -q "healthy"; then
  echo " Mock Backend: OK ($(echo "$HEALTH" | python -c "import sys,json; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null))"
else
  echo " Mock Backend: UNREACHABLE"
fi

# 2. Active monitors
echo "--- Active Monitors ---"
MONITORS=$(curl -s http://host.docker.internal:5000/api/monitors/check-all 2>/dev/null)
if echo "$MONITORS" | grep -q "any_triggered"; then
  TRIGGERED=$(echo "$MONITORS" | python -c "import sys,json; d=json.load(sys.stdin)['data']; print('YES' if d.get('any_triggered') else 'NO')" 2>/dev/null)
  COUNT=$(echo "$MONITORS" | python -c "import sys,json; print(json.load(sys.stdin)['data']['active_monitors'])" 2>/dev/null)
  echo " Active: $COUNT | Triggered: $TRIGGERED"
else
  echo " No active monitors"
fi

# 3. Pending notifications
echo "--- Pending Notifications ---"
NOTIFS=$(curl -s http://host.docker.internal:5000/api/notifications/pending 2>/dev/null)
if [ -n "$NOTIFS" ]; then
  COUNT=$(echo "$NOTIFS" | python -c "import sys,json; print(json.load(sys.stdin)['data'].get('count',0))" 2>/dev/null)
  echo " Pending: $COUNT"
else
  echo " None"
fi

# 4. Flash deals
echo "--- Active Flash Deals ---"
DEALS=$(curl -s http://host.docker.internal:5000/api/flash-deals 2>/dev/null)
if [ -n "$DEALS" ]; then
  COUNT=$(echo "$DEALS" | python -c "import sys,json; print(json.load(sys.stdin)['data'].get('count',0))" 2>/dev/null)
  echo " Active deals: $COUNT"
else
  echo " None"
fi

# 5. Weather
echo "--- Today's Weather ---"
WEATHER=$(curl -s http://host.docker.internal:5000/api/weather 2>/dev/null)
if [ -n "$WEATHER" ]; then
  TEMP=$(echo "$WEATHER" | python -c "import sys,json; d=json.load(sys.stdin)['data']; print(d['current']['temperature'])" 2>/dev/null)
  COND=$(echo "$WEATHER" | python -c "import sys,json; d=json.load(sys.stdin)['data']; print(d['current']['condition'])" 2>/dev/null)
  echo " $TEMP°C, $COND"
else
  echo " N/A"
fi

echo ""
echo "=== Init Complete ==="
