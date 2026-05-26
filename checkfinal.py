#!/usr/bin/env python3
import json, os, sys
os.chdir('/workspace/pinpai-ai-in')
with open('a--lange-and-s-hne/brand.json') as f:
    d = json.load(f)
for k, v in d['languages'].items():
    print(f"{k}: {len(v)}c")
