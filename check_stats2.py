import json
with open('/workspace/pinpai-ai-in/a--lange-and-s-hne/brand.json') as f:
    d = json.load(f)
langs = d.get('languages', {})
for k, v in langs.items():
    print(f"{k}: {len(v)} chars")
print()
print("Requirements:")
print("  zh-CN, ja, ko >= 800 chars")
print("  en, fr, es, de, pt, ru, ar >= 1500 chars")
print()
print("Shortfalls:")
for k, v in langs.items():
    if k in ('zh-CN', 'ja', 'ko'):
        need = 800 - len(v)
    else:
        need = 1500 - len(v)
    if need > 0:
        print(f"  {k}: need {need} more chars (need {len(v)+need}, have {len(v)})")
    else:
        print(f"  {k}: OK ({len(v)})")
