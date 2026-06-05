#!/bin/sh
MSG="$1"
python -c "
import json, subprocess, sys
body = json.dumps({'message': sys.argv[1]})
subprocess.run(['curl', '-s', '-X', 'POST',
  'http://mock-backend:5000/api/chat',
  '-H', 'Content-Type: application/json',
  '-d', body])
" "$MSG"
