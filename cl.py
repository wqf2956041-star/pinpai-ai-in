import json,sys,os
os.chdir('/workspace/pinpai-ai-in')
d=json.load(open('a--lange-and-s-hne/brand.json'))
for k,v in d['languages'].items():
    print(f"{k}: {len(v)}c")
