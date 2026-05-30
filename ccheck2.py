import json,subprocess,sys
r=subprocess.run(['python3','-c',"""
import json
d=json.load(open('/workspace/pinpai-ai-in/a--lange-and-s-hne/brand.json'))
for k,v in d['languages'].items():
    print(f'{k}: {len(v)}c')
"""],capture_output=True,text=True)
print(r.stdout)
print(r.stderr)
