import json
# Read the brand.json and count characters
with open('/workspace/pinpai-ai-in/a--lange-and-s-hne/brand.json') as f:
    d = json.load(f)

langs = d['languages']
all_ok = True
for k, v in langs.items():
    L = len(v)
    if k in ('zh-CN', 'ja', 'ko'):
        target = 800
    else:
        target = 1500
    status = "OK" if L >= target else f"SHORT by {target-L}"
    if L < target:
        all_ok = False
    print(f"{k}: {L} chars (target {target}) -> {status}")

print(f"\nAll languages meet requirements: {all_ok}")
