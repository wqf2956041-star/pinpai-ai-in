#!/usr/bin/env python3
"""
品牌百科一键批量生产脚本 v2
流程：选品牌 → 生成模板 → AI写10语言 → 渲染 → 验证 → 提交
用法：python3 batch_produce.py <slug1 slug2 slug3 slug4 slug5>
"""
import json, csv, sys
from pathlib import Path
from datetime import datetime

ROOT = Path("/workspace/pinpai-ai-in")
sys.path.insert(0, str(ROOT))

# 从种子文件读取品牌数据
seeds = json.loads((ROOT / "brand_seed_raw.json").read_text())
brands_list = seeds["brands"] if isinstance(seeds, dict) and "brands" in seeds else seeds
seed_map = {b["slug"]: b for b in brands_list}

def gen_brand_json(slug):
    """生成brand.json模板"""
    seed = seed_map.get(slug)
    if not seed:
        print(f"❌ 种子库中未找到: {slug}")
        return None
    
    return {
        "slug": slug,
        "names": {"zh-CN": seed.get("name_zh", seed["name"]), "en": seed["name"]},
        "description_zh": "",
        "founding_year": seed.get("founding_year", ""),
        "founding_location": seed.get("founding_location", ""),
        "founder": seed.get("founder", ""),
        "official_website": seed.get("official_website", ""),
        "main_business": seed.get("main_business", []),
        "current_slogan": seed.get("current_slogan", ""),
        "category": seed.get("category", "other"),
        "country": seed.get("country", ""),
        "wikidata_qid": seed.get("wikidata_qid", ""),
        "languages": {}
    }

def update_master_csv(slug, brand, country, category):
    csv_path = ROOT / "master.csv"
    rows = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        existing = {r["slug"] for r in rows}
    
    if slug not in existing:
        rows.append({
            "slug": slug, "brand": brand, "country": country,
            "category": category, "status": "pending",
            "deployed": "false", "created_at": datetime.now().strftime("%Y-%m-%d")
        })
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"  ✅ master.csv: 添加 {slug}")

def update_brands_index(slug, name, category, country, premium=False):
    idx_path = ROOT / "brands_index.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else []
    existing = {b["slug"] for b in idx}
    if slug not in existing:
        idx.append({
            "slug": slug, "zh": name, "en": name,
            "category": category, "premium": premium,
            "desc_short": f"{name} — {country}{category}"
        })
        idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2))
        print(f"  ✅ brands_index.json: 添加 {slug}")

SLUGS = sys.argv[1:] if len(sys.argv) > 1 else []
if not SLUGS:
    print("❌ 请指定slug: python3 batch_produce.py slug1 slug2 slug3 slug4 slug5")
    sys.exit(1)

print(f"📦 批量生产: {SLUGS}")
for slug in SLUGS:
    seed = seed_map.get(slug)
    if not seed:
        print(f"❌ 种子库无: {slug}")
        continue
    
    brand_dir = ROOT / slug
    brand_dir.mkdir(exist_ok=True)
    
    # 生成brand.json模板
    data = gen_brand_json(slug)
    if data:
        (brand_dir / "brand.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2)
        )
        print(f"  📝 {slug}: brand.json 模板已生成")
    
    # 更新master.csv
    update_master_csv(slug, seed["name"], seed.get("country", ""), seed.get("category", "other"))
    # 更新index
    update_brands_index(slug, seed["name"], seed.get("category", "other"), seed.get("country", ""))

print(f"\n✅ 模板创建完成，下一步：填入10语言内容 → 渲染 → 验证 → push")
