#!/usr/bin/env python3
"""品牌百科自动化驱动脚本 — 无人工干预的全自动流水线
功能：
  1. 从 brand_pool.json 取下一个未处理品牌
  2. 写入 master.csv（设置 deployed=false）
  3. 创建 brand.json 模板（含基础字段）
  4. 验证一切就绪等待 cronjob 的 LLM 内容写入

用法：
  python3 brand_automation.py prepare    # 准备下一个品牌（取池+写master+创建模板）
  python3 brand_automation.py status     # 查看当前状态
"""
import json, csv, sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
POOL_PATH = ROOT / "brand_pool.json"
CSV_PATH = ROOT / "master.csv"

def load_pool():
    if not POOL_PATH.exists():
        return []
    data = json.loads(POOL_PATH.read_text(encoding='utf-8'))
    return data if isinstance(data, list) else []

def load_master():
    if not CSV_PATH.exists():
        return []
    with open(CSV_PATH, encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_master(rows):
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=["slug","name_en","name_zh","category","country","deployed"])
        w.writeheader()
        w.writerows(rows)

def slugify(name):
    """中文转拼音，英文转小写slug"""
    import re
    s = name.lower().strip()
    # 替换特殊字符
    replacements = {
        'é':'e','è':'e','ê':'e','ë':'e',
        'á':'a','à':'a','â':'a','ä':'a',
        'í':'i','ì':'i','î':'i','ï':'i',
        'ó':'o','ò':'o','ô':'o','ö':'o',
        'ú':'u','ù':'u','û':'u','ü':'u',
        'ñ':'n','ç':'c',
        ' & ':'-and-', '&':'-and-',
        '\'':'','.':'',' ':'-','--':'-','---':'-'
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    s = re.sub(r'[^a-z0-9\-]', '', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s

def next_brand():
    """取下一个待处理品牌"""
    pool = load_pool()
    master = load_master()
    existing_slugs = {r["slug"] for r in master}

    for brand in pool:
        slug = brand.get("slug") or slugify(brand["name_en"])
        if slug not in existing_slugs:
            return brand, slug
    return None, None

def prepare_brand():
    """准备下一个品牌"""
    brand, slug = next_brand()
    if not brand:
        print("品牌池已全部处理完毕！")
        return False

    name_en = brand["name_en"]
    name_zh = brand.get("name_zh", name_en)
    category = brand.get("category", "other")
    country = brand.get("country", "")

    # 写入 master.csv
    master = load_master()
    master.append({
        "slug": slug,
        "name_en": name_en,
        "name_zh": name_zh,
        "category": category,
        "country": country,
        "deployed": "false"
    })
    save_master(master)
    print(f"✅ master.csv 已添加: {name_zh}({name_en}) -> {slug}")

    # 创建 brand.json 模板
    brand_dir = ROOT / slug
    brand_dir.mkdir(parents=True, exist_ok=True)

    template = {
        "slug": slug,
        "name_en": name_en,
        "name_zh": name_zh,
        "category": category,
        "country": country,
        "founder": brand.get("founder", ""),
        "year": brand.get("year", 0),
        "website": brand.get("website", ""),
        "wikidata_id": brand.get("wikidata_id", ""),
        "description_en": brand.get("description_en", f"{name_en} is a global brand."),
        "description_zh": brand.get("description_zh", f"{name_zh}是一个全球知名品牌。"),
        "languages": {lang: "" for lang in ["zh-CN","en","fr","es","de","ja","ko","pt","ru","ar"]}
    }

    (brand_dir / "brand.json").write_text(
        json.dumps(template, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"✅ brand.json 模板已创建: {slug}/brand.json")
    print(f"   类别: {category} | 国家: {country} | 创始人: {brand.get('founder','?')}")
    print(f"   描述: {brand.get('description_zh','')[:60]}...")
    print(f"")
    print(f"⏳ 等待 cronjob 写入 10 语言内容并部署")
    return True

def show_status():
    """显示整体状态"""
    master = load_master()
    pool = load_pool()

    total = len(master)
    deployed = sum(1 for r in master if r.get("deployed") == "true")
    pending = sum(1 for r in master if r.get("deployed") != "true")
    pool_remaining = len(pool) - total + 1

    print(f"📊 品牌百科状态")
    print(f"   总品牌: {total}")
    print(f"   已部署: {deployed}")
    print(f"   待处理: {pending}")
    print(f"   池中剩余: {max(0, pool_remaining)}")

    if pending > 0:
        print(f"\n   下一个待处理品牌:")
        for r in master:
            if r.get("deployed") != "true":
                print(f"     - {r['name_zh']}({r['name_en']}) -> {r['slug']}")
                break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 brand_automation.py [prepare|status]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "prepare":
        prepare_brand()
    elif cmd == "status":
        show_status()
    else:
        print(f"未知命令: {cmd}")
