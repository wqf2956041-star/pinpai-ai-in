#!/usr/bin/env python3
"""
读取一个品牌的 brand.json，输出品牌信息的摘要，方便 AI 批量生成描述
"""
import csv, json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

with open(ROOT / "master.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

output = []
for row in rows:
    slug = row["slug"]
    if row["status"].strip() == "done":
        continue
    
    json_path = ROOT / slug / "brand.json"
    if not json_path.exists():
        continue
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    output.append({
        "slug": slug,
        "name_zh": data.get("names", {}).get("zh-CN", row["brand"]),
        "name_en": data.get("names", {}).get("en", row["brand"]),
        "category": data.get("category", ""),
        "country": row["country"],
        "founding_year": data.get("founding_year", ""),
        "founding_location": data.get("founding_location", ""),
        "founder": data.get("founder", ""),
        "website": data.get("official_website", ""),
    })

print(json.dumps({"brands": output}, ensure_ascii=False, indent=2))
