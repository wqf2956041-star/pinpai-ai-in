#!/usr/bin/env python3
"""
批量初始化 50 个品牌：init + AI 查找品牌数据
"""
import csv, json, os, sys, re
from pathlib import Path
from datetime import datetime

ROOT = Path("/workspace/pinpai-ai-in")
CSV_PATH = ROOT / "master.csv"
SEED_PATH = ROOT / "brand_seed_raw.json"

# Load seed data
with open(SEED_PATH, "r", encoding="utf-8") as f:
    seed = json.load(f)

seed_brands = seed["brands"]

# Build lookup tables
seed_by_name = {}
for b in seed_brands:
    key = b["brand_name"].strip().lower()
    seed_by_name[key] = b
    qid = b.get("wikidata_id", "")
    if qid:
        seed_by_name[qid] = b

# Read master.csv
with open(CSV_PATH, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

templates_created = 0

for row in rows:
    slug = row["slug"]
    brand_name = row["brand"]
    industry = row["industry"]
    
    if row["status"].strip() == "done":
        continue
    
    brand_dir = ROOT / slug
    json_path = brand_dir / "brand.json"
    
    if json_path.exists():
        print(f"  ⏭ {slug}: 已存在，跳过")
        continue
    
    seed_entry = seed_by_name.get(brand_name.strip().lower())
    wikidata_id = ""
    if seed_entry:
        wikidata_id = seed_entry.get("wikidata_id", "")
    
    brand_dir.mkdir(parents=True, exist_ok=True)
    
    zh_name = brand_name
    en_name = brand_name
    
    template = {
        "slug": slug,
        "names": {"zh-CN": zh_name, "en": en_name},
        "category": industry,
        "founding_year": "",
        "founding_location": "",
        "founder": "",
        "official_website": "",
        "main_business": [],
        "current_slogan": "",
        "description_zh": "",
        "languages": {"en": ""},
        "similar_brands": [],
        "is_premium": False,
        "image_url": "",
        "representative_products": [],
        "key_events": [],
        "philanthropy": [],
        "exhibitions": [],
        "past_slogans": [],
        "wikidata_id": wikidata_id,
        "_meta": {
            "version": "2.0.0",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "validator_pass": False
        }
    }
    
    json_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    templates_created += 1
    print(f"  ✅ {slug}: brand.json 已创建 ({zh_name})")

print(f"\n✅ 批量初始化完成: {templates_created} 个品牌模板已创建")
