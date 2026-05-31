#!/bin/bash
# run_pinpai.sh — Run brand heartbeat directly on host, sync to /var/www/pinpai/
cd /workspace/pinpai-ai-in || exit 1
python3 brand_heartbeat.py 2>&1
exit_code=$?
# Ensure www directory is owned by caddy
sudo chown -R caddy:caddy /var/www/pinpai/ 2>/dev/null
exit $exit_code
