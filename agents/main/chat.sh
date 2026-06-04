#!/bin/sh
# LiHua one-shot data pipeline
# Usage: bash chat.sh "<user message>"
# Returns: JSON with identity_mode, style_hint, recommendations, activities, weather

MSG="$1"
python -c "
import json, subprocess, sys
body = json.dumps({'message': sys.argv[1]})
subprocess.run(['curl', '-s', '-X', 'POST',
  'http://host.docker.internal:5000/api/chat',
  '-H', 'Content-Type: application/json',
  '-d', body])
" "$MSG"
