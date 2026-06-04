#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")
BACKEND_DIR="$REPO_ROOT/mock-backend"
PORT="${1:-5000}"

echo "Starting ShadowMe mock backend on http://localhost:$PORT"
echo "Backend directory: $BACKEND_DIR"

cd "$BACKEND_DIR"
python -m pip install -r requirements.txt
PORT="$PORT" export PORT
python server.py
