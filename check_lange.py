import json
d = json.loads(open('a--lange-and-s-hne/brand.json').read())
for k,v in d.get('languages',{}).items():
    print(f"{k}: {len(v)}c")
