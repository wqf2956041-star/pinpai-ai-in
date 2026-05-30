#!/bin/bash
# brand_cycle.sh — Robust wrapper for brand_cycle.py
# Uses absolute paths. No ambiguity.
cd /workspace/pinpai-ai-in || exit 1

# Always run on gh-pages branch
git checkout gh-pages 2>/dev/null
python3 /workspace/pinpai-ai-in/brand_cycle.py 2>&1

# Sync to main so GH Pages deploys latest content
git checkout main 2>/dev/null
git merge gh-pages --no-edit 2>/dev/null
git push origin main 2>/dev/null
git checkout gh-pages 2>/dev/null
