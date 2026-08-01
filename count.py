#!/usr/bin/env python3
"""Count characters in the existing brand.json"""
import json

with open('/workspace/pinpai-ai-in/a--lange-and-s-hne/brand.json') as f:
    raw = f.read()

d = json.loads(raw)
for k, v in d['languages'].items():
    print(f"{repr(k)}: {len(v)} chars")

# Also check description_zh
print(f"\ndescription_zh: {len(d.get('description_zh',''))} chars")
