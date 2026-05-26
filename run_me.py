import json
d = json.load(open('/workspace/pinpai-ai-in/a--lange-and-s-hne/brand.json'))
for k, v in d['languages'].items():
    print(f"{k}: {len(v)} chars")
