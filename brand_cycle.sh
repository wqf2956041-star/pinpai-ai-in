#!/bin/bash
# brand_cycle.sh — Robust wrapper for brand_cycle.py
# Uses absolute paths. No ambiguity.
cd /workspace/pinpai-ai-in || exit 1
python3 /workspace/pinpai-ai-in/brand_cycle.py 2>&1
