import json
with open('/workspace/pinpai-ai-in/aesop/brand.json') as f:
    data = json.load(f)
langs = data['languages']
print("Languages:", len(langs))
for code, text in langs.items():
    m = 800 if code in ('zh-CN','ja','ko') else 1500
    s = "OK" if len(text)>=m else "SHORT"
    print(f"  {code}: {len(text)} chars {s}")
print("desc_zh match:", data['description_zh'] == langs['zh-CN'])
