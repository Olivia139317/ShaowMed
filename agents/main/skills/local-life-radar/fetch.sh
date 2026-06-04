#!/bin/sh
MODE=${1:-solo}
curl -s -X POST "http://host.docker.internal:5000/api/recommendations" -H "Content-Type: application/json" -d "{\"identity_mode\": \"$MODE\"}"