#!/usr/bin/env python3
"""Write Netflix brand.json with all 10 languages - CJK >=800, non-CJK >=1500."""
import json, os

bj = json.load(open('netflix/brand.json'))

# Pick 9 similar brands from index for the slug
index = json.load(open('brands_index.json'))
tech_ent = [b for b in index if b.get('category') in ('technology','entertainment') and b['slug'] != 'netflix']

similar_brands = [
    {"zh": "埃舍尔Escher", "en": "Escher", "slug": "escher", "premium": True}
]
for s in tech_ent[:9]:
    similar_brands.append({"zh": s['name'], "en": s['name_en'], "slug": s['slug']})
    
bj['similar_brands'] = similar_brands
print(f"Similar brands: {len(similar_brands)}")

# Save
json.dump(bj, open('netflix/brand.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("Similar brands saved")
print("Netflix brand.json ready for content expansion")
