#!/usr/bin/env python3
"""
为批次3（科技/运动/食品/潮玩）的17个品牌填充描述内容
使用AI直接生成品牌描述、英文摘要和类似品牌
"""
import csv, json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

# Read master.csv
with open(ROOT / "master.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# The batch 3 brands: tech(8), sport(3), food(3), toy(2), fashion(1)
batch3_slugs = ["apple","microsoft","google","amazon","samsung","huawei","sony","nvidia",
                "nike","adidas","puma",
                "coca-cola","mcdonald-s","starbucks",
                "lego","mattel","coach"]

# Build slug -> brand info
slug_map = {}
for r in rows:
    slug_map[r["slug"]] = r

# Build brand list with available data
for slug in batch3_slugs:
    brand_json_path = ROOT / slug / "brand.json"
    if not brand_json_path.exists():
        print(f"⚠️ {slug}: brand.json not found")
        continue
    
    data = json.loads(brand_json_path.read_text(encoding="utf-8"))
    print(f"\n[{slug}] {data['names'].get('zh-CN', slug)}")
    print(f"  wikidata_id: {data.get('wikidata_id', 'N/A')}")
    print(f"  country: {slug_map[slug]['country']}")
    print(f"  category: {data.get('category', '')}")
    print(f"  founding_year: {data.get('founding_year', 'N/A')}")
    print(f"  founder: {data.get('founder', 'N/A')}")
    print(f"  website: {data.get('official_website', 'N/A')}")

print(f"\n\nTotal batch3 brands: {len(batch3_slugs)}")
print("Write the content areas for each brand.")
