#!/usr/bin/env python3
"""
Wikipedia 品牌分类页爬取 → 全球品牌种子库
用 Wikipedia API 获取分类页下的品牌列表，比 Wikidata SPARQL 快且不限流
"""
import csv, json, urllib.request, urllib.parse, time, sys, os, re

WIKI_API = "https://zh.wikipedia.org/w/api.php"
WIKI_EN_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "GlobalBrandIndex/1.0"

def wiki_query(api_url, params, retries=3):
    """Call Wikipedia API"""
    params["format"] = "json"
    params["origin"] = "*"
    url = f"{api_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(f"  Error: {e}", file=sys.stderr)
            return None
    return None

def get_category_members(category, lang="zh", limit=500):
    """Get all pages in a Wikipedia category"""
    api = WIKI_API if lang == "zh" else WIKI_EN_API
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": "min",
        "cmtype": "page",
    }
    members = []
    while True:
        data = wiki_query(api, params)
        if not data:
            break
        pages = data.get("query", {}).get("categorymembers", [])
        for p in pages:
            title = p.get("title", "")
            if ":" not in title:  # skip subcategories
                members.append(title)
        if "continue" in data and "cmcontinue" in data["continue"]:
            params["cmcontinue"] = data["continue"]["cmcontinue"]
        else:
            break
        if len(members) >= limit:
            break
        time.sleep(0.1)
    return members

def get_page_meta(titles, lang="zh"):
    """Get page metadata (short description, wikidata ID)"""
    api = WIKI_API if lang == "zh" else WIKI_EN_API
    params = {
        "action": "query",
        "titles": "|".join(titles[:50]),  # max 50 per request
        "prop": "pageprops|extracts|info",
        "ppprop": "wikibase_item|shortdescription",
        "exintro": "1",
        "explaintext": "1",
        "exchars": "300",
    }
    data = wiki_query(api, params)
    if not data:
        return {}
    pages = data.get("query", {}).get("pages", {})
    result = {}
    for pid, info in pages.items():
        title = info.get("title", "")
        result[title] = {
            "pageid": info.get("pageid"),
            "wikidata_id": info.get("pageprops", {}).get("wikibase_item", ""),
            "description": info.get("pageprops", {}).get("shortdescription", ""),
            "extract": info.get("extract", ""),
        }
    return result

def get_brand_info(title):
    """Get brand info from Chinese and English Wikipedia"""
    # Chinese
    zh_meta = get_page_meta([title], "zh")
    # English (translate title)
    en_name = title
    en_meta = get_page_meta([en_name], "en")
    
    meta = zh_meta.get(title, {})
    en_data = en_meta.get(en_name, {})
    
    return {
        "title": title,
        "wikidata_id": meta.get("wikidata_id", en_data.get("wikidata_id", "")),
        "description": meta.get("description", en_data.get("description", "")),
        "extract_zh": meta.get("extract", ""),
        "extract_en": en_data.get("extract", ""),
    }

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower().strip()).strip('-')

def categorize_brand(title, desc, extract):
    """Guess category from title/description"""
    t = (title + " " + desc + " " + extract).lower()
    cat_map = [
        ("auto", ["汽车", "汽⻋", "automotive", "automobile", "car", "motor", "car manufacturer"]),
        ("fashion-luxury", ["奢侈品", "luxury", "高定", "couture", "haute"]),
        ("fashion", ["时尚", "服装", "fashion", "apparel", "衣", "clothing", "retail"]),
        ("beauty", ["美妆", "化妆品", "beauty", "cosmetic", "护肤", "skincare", "perfume", "香⽔"]),
        ("tech", ["科技", "技术", "tech", "technology", "电子", "electronic", "software", "internet", "comput"]),
        ("food", ["食品", "饮料", "food", "beverage", "餐饮", "restaurant", "coffee", "brewing"]),
        ("sport", ["运动", "sport", "athletic", "sneaker", "outdoor"]),
        ("watch", ["手表", "watch", "钟表", "horology"]),
        ("jewelry", ["珠宝", "jewelry", "首饰", "jewellery", "gem"]),
        ("toy", ["玩具", "toy", "game", "entertainment"]),
        ("finance", ["银行", "金融", "bank", "finance", "insurance", "investment"]),
    ]
    for cat, keywords in cat_map:
        if any(k in t for k in keywords):
            return cat
    return "other"

def main():
    # Wikipedia category pages for brands
    categories_zh = {
        "时尚品牌": "fashion",
        "奢侈品牌": "fashion-luxury",
        "汽车品牌": "auto",
        "化妆品品牌": "beauty",
        "科技公司": "tech",
        "运动品牌": "sport",
        "食品饮料公司": "food",
        "手表品牌": "watch",
        "珠宝品牌": "jewelry",
        "玩具公司": "toy",
    }
    
    categories_en = {
        "Luxury brands": "fashion-luxury",
        "Fashion brands": "fashion",
        "Automobile manufacturers": "auto",
        "Cosmetics companies": "beauty",
        "Technology companies": "tech",
        "Sporting goods manufacturers": "sport",
        "Food and drink companies": "food",
        "Watch manufacturing companies": "watch",
        "Jewellery companies": "jewelry",
        "Toy companies": "toy",
    }
    
    all_brands = {}
    
    # Phase 1: Chinese Wikipedia
    print("=" * 60)
    print("Phase 1: Chinese Wikipedia category pages")
    print("=" * 60)
    
    for category, default_cat in categories_zh.items():
        print(f"\n📂 Fetching Category:{category} → {default_cat}")
        members = get_category_members(category, "zh", 200)
        print(f"  Found {len(members)} pages")
        
        # Get metadata in batches
        for i in range(0, len(members), 50):
            batch = members[i:i+50]
            metas = get_page_meta(batch, "zh")
            for title, meta in metas.items():
                if not meta.get("wikidata_id"):
                    continue
                qid = meta["wikidata_id"]
                if qid not in all_brands:
                    all_brands[qid] = {
                        "wikidata_id": qid,
                        "brand_name": title,
                        "description": meta.get("description", ""),
                        "category": default_cat,
                        "country": "",
                        "website": "",
                        "founded_year": "",
                        "founder": "",
                    }
            time.sleep(0.2)
    
    print(f"\n✅ After Chinese Wikipedia: {len(all_brands)} unique brands")
    
    # Phase 2: English Wikipedia (more comprehensive)
    print("\n" + "=" * 60)
    print("Phase 2: English Wikipedia category pages")
    print("=" * 60)
    
    for category, default_cat in categories_en.items():
        print(f"\n📂 Fetching Category:{category} → {default_cat}")
        members = get_category_members(category, "en", 200)
        print(f"  Found {len(members)} pages")
        
        for i in range(0, len(members), 50):
            batch = members[i:i+50]
            metas = get_page_meta(batch, "en")
            for title, meta in metas.items():
                qid = meta.get("wikidata_id", "")
                if not qid:
                    continue
                if qid not in all_brands:
                    all_brands[qid] = {
                        "wikidata_id": qid,
                        "brand_name": title,
                        "description": meta.get("description", ""),
                        "category": default_cat,
                        "country": "",
                        "website": "",
                        "founded_year": "",
                        "founder": "",
                    }
            time.sleep(0.2)
    
    print(f"\n✅ Total unique brands: {len(all_brands)}")
    
    # Convert to list and save
    brands_list = list(all_brands.values())
    
    output = {
        "total": len(brands_list),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "brands": brands_list,
    }
    
    with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved to brand_seed_raw.json")
    
    # Show top brands sample
    print("\n--- Sample brands (first 30) ---")
    for b in brands_list[:30]:
        print(f"  {b['brand_name']} [{b['category']}] Q{b['wikidata_id']}")

if __name__ == "__main__":
    main()
