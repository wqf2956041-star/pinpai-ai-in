#!/usr/bin/env python3
"""
品牌百科自动推进器 —— 每20分钟执行一批
流程：挑3个pending品牌 → 写入10语言内容 → render → 更新index → 更新sitemap → git push
"""
import csv, json, subprocess, sys, re, urllib.request
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
CSV_PATH = ROOT / "master.csv"
POOL_PATH = ROOT / "brand_pool.json"
LANGUAGES = ["zh-CN", "en", "fr", "es", "de", "ja", "ko", "pt", "ru", "ar"]

CJK_LANGS = {"zh-CN", "ja", "ko"}
CHAR_MIN = {l: 800 if l in CJK_LANGS else 1500 for l in LANGUAGES}

LOG_FILE = ROOT / "logs" / "auto_drive.log"
(ROOT / "logs").mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def get_pending_brands():
    """从master.csv找到pending=3个，或从brand_pool.json拿新的"""
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        deployed = {r["slug"] for r in csv.DictReader(f) if r.get("deployed","").lower() == "true"}
    
    with open(POOL_PATH, encoding="utf-8") as f:
        pool = json.load(f)
    
    # 排除已部署的
    candidates = []
    for b in pool:
        slug = b["name_en"].lower().replace(" ", "-").replace("&", "and").replace("'", "").replace(".", "-").replace(",", "")
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        if slug not in deployed:
            candidates.append(b)
    
    log(f"Brand pool: {len(pool)} total, {len(candidates)} not yet deployed")
    
    # 取前3个
    batch = candidates[:3]
    if not batch:
        log("No pending brands found!")
        return []
    
    log(f"Next batch: {[b['name_en'] for b in batch]}")
    return batch

def slugify(name):
    slug = name.lower().replace(" ", "-").replace("&", "and").replace("'", "").replace(".", "-").replace(",", "")
    return re.sub(r'[^a-z0-9-]', '', slug)

def init_brand(brand):
    """用brand_factory.py初始化一个品牌"""
    slug = slugify(brand["name_en"])
    name_en = brand["name_en"]
    name_zh = brand.get("name_zh", name_en)
    country = brand.get("country", "")
    category = brand.get("category", "")
    
    # 检查是否已存在
    brand_dir = ROOT / slug
    if brand_dir.exists() and (brand_dir / "brand.json").exists():
        log(f"  {slug}: already exists, skipping init")
        return slug, True
    
    # Add to master.csv
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([slug, name_en, name_zh, category, country, "false"])
    
    # Init brand.json template
    result = subprocess.run(
        [sys.executable, "brand_factory.py", "add", slug, name_en, country, category],
        capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode != 0:
        log(f"  ❌ add failed: {result.stderr[:200]}")
        return slug, False
    
    result2 = subprocess.run(
        [sys.executable, "brand_factory.py", "init", slug],
        capture_output=True, text=True, cwd=ROOT
    )
    if result2.returncode != 0:
        log(f"  ❌ init failed: {result2.stderr[:200]}")
        return slug, False
    
    # Read brand.json and add required fields
    bj_path = brand_dir / "brand.json"
    bj = json.loads(bj_path.read_text(encoding="utf-8"))
    
    # Fill from pool data
    if brand.get("wikidata_id"):
        bj["wikidata_id"] = brand["wikidata_id"]
    if brand.get("founder"):
        bj["founder"] = brand["founder"]
    if brand.get("year"):
        bj["founding_year"] = brand["year"]
    if brand.get("website"):
        bj["official_website"] = brand["website"]
    if brand.get("description_en"):
        bj["description_en"] = brand["description_en"]
    if brand.get("description_zh"):
        bj["description_zh"] = brand["description_zh"]
    if not bj.get("names", {}).get("zh-CN"):
        bj["names"]["zh-CN"] = name_zh
    if not bj.get("names", {}).get("en"):
        bj["names"]["en"] = name_en
    
    bj_path.write_text(json.dumps(bj, ensure_ascii=False, indent=2))
    
    log(f"  ✅ {slug}: initialized")
    return slug, True

def write_brand_content(slug, brand):
    """Write 10-language content for a brand using LLM-based generation.
    The cron job will call this and the agent fills in the content."""
    # This function is a placeholder — the actual content writing happens
    # in the cron job session via the agent's LLM capability.
    # We return the brand data so the cron job session can use it.
    bj_path = ROOT / slug / "brand.json"
    bj = json.loads(bj_path.read_text(encoding="utf-8"))
    return bj

def main():
    log("=" * 60)
    log("Brand Auto Drive — Starting batch")
    
    batch = get_pending_brands()
    if not batch:
        log("Nothing to do. Exiting.")
        return 0
    
    # Check if this is a clean run or we're in the middle of something
    active_slugs = []
    for b in batch:
        slug, ok = init_brand(b)
        if ok:
            active_slugs.append((slug, b))
    
    if not active_slugs:
        log("No brands initialized. Exiting.")
        return 1
    
    log(f"\nActive brands for this batch: {[s for s,_ in active_slugs]}")
    log("\n⚠️  Content writing will happen in the cron job agent session.") 
    log("The cron job prompt should call the brand-encyclopedia-seo skill")
    log("to write 10-language content for these brands.")
    
    # Return info for the cron job agent
    print("BATCH_INFO_START")
    print(json.dumps({
        "active_slugs": [s for s,_ in active_slugs],
        "batch_brands": [{**b, "slug": s} for s,b in active_slugs],
        "char_min": CHAR_MIN,
        "languages": LANGUAGES
    }, ensure_ascii=False))
    print("BATCH_INFO_END")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
