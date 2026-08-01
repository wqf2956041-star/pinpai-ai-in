#!/usr/bin/env python3
"""
批量品牌内容生成器 - 读取模板，输出AI生成指令
为每个 pending 品牌的 brand.json 生成需要的品牌内容
"""

import csv, json, urllib.request, urllib.parse, time, re, os
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

def wikidata_query(qid):
    """查询Wikidata获取品牌信息"""
    if not qid:
        return {}
    
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels|descriptions|claims|sitelinks",
        "languages": "zh,en",
        "format": "json",
        "origin": "*",
    }
    url = f"https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(params)}"
    
    for attempt in range(3):
        req = urllib.request.Request(url, headers={"User-Agent": "GlobalBrandIndex/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                entity = data.get("entities", {}).get(qid, {})
                result = {}
                
                # Labels (localized names)
                labels = entity.get("labels", {})
                result["zh_label"] = labels.get("zh", {}).get("value", "")
                result["en_label"] = labels.get("en", {}).get("value", "")
                
                # Description
                descs = entity.get("descriptions", {})
                result["zh_desc"] = descs.get("zh", {}).get("value", "")
                result["en_desc"] = descs.get("en", {}).get("value", "")
                
                # Claims (properties)
                claims = entity.get("claims", {})
                
                # P571: inception (founding year)
                inception = claims.get("P571", [])
                if inception:
                    result["founding_year"] = inception[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
                
                # P17: country
                country = claims.get("P17", [])
                if country:
                    cid = country[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
                    if cid:
                        # Get country label
                        result["country_qid"] = cid
                
                # P112: founded by
                founder = claims.get("P112", [])
                if not founder:
                    founder = claims.get("P57", [])  # P57 = founder (alternative)
                if founder:
                    fid = founder[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
                    if fid:
                        result["founder_qid"] = fid
                
                # P856: official website
                website = claims.get("P856", [])
                if website:
                    result["website"] = website[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
                
                # P452: industry
                industry = claims.get("P452", [])
                if industry:
                    iid = industry[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
                    if iid:
                        result["industry_qid"] = iid
                
                # P1454: legal form (business type)
                legal = claims.get("P1454", [])
                if legal:
                    lid = legal[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
                    if lid:
                        result["legal_qid"] = lid
                
                # P1128: employees count
                employees = claims.get("P1128", [])
                if employees:
                    result["employees"] = employees[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
                
                # P2139: revenue
                revenue = claims.get("P2139", [])
                if revenue:
                    result["revenue"] = revenue[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("amount", "")
                
                # Wikipedia link
                sitelinks = entity.get("sitelinks", {})
                result["wiki_en"] = sitelinks.get("enwiki", {}).get("title", "")
                result["wiki_zh"] = sitelinks.get("zhwiki", {}).get("title", "")
                
                # Get label for a QID
                def get_label(qid_val):
                    return ""
                result["_get_label"] = get_label
                
                return result
        except Exception as e:
            time.sleep(1)
            continue
    return {}

def resolve_qid_label(qid):
    """Get label for a QID"""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels",
        "languages": "zh,en",
        "format": "json",
        "origin": "*",
    }
    url = f"https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "GlobalBrandIndex/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            entity = data.get("entities", {}).get(qid, {})
            labels = entity.get("labels", {})
            zh = labels.get("zh", {}).get("value", "")
            en = labels.get("en", {}).get("value", "")
            return zh or en or qid
    except:
        return qid

# Read master.csv to get brands
with open(ROOT / "master.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Read brand_seed_raw for Wikidata IDs
with open(ROOT / "brand_seed_raw.json", "r", encoding="utf-8") as f:
    seed = json.load(f)

seed_by_name = {}
for b in seed["brands"]:
    seed_by_name[b["brand_name"].strip().lower()] = b

# Load Wikidata IDs from seed
print("Resolving Wikidata info for brands...")
print()

for row in rows:
    slug = row["slug"]
    brand_name = row["brand"]
    
    if row["status"].strip() == "done":
        continue
    
    json_path = ROOT / slug / "brand.json"
    if not json_path.exists():
        continue
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Find Wikidata ID
    seed_entry = seed_by_name.get(brand_name.strip().lower())
    qid = ""
    if seed_entry:
        qid = seed_entry.get("wikidata_id", "")
    
    if qid:
        print(f"[{slug}] Wikidata: {qid} → 查询中...")
        info = wikidata_query(qid)
        
        # Update Chinese name
        if info.get("zh_label"):
            data["names"]["zh-CN"] = info["zh_label"]
        if info.get("en_label"):
            data["names"]["en"] = info["en_label"]
        
        # Founding year
        if info.get("founding_year"):
            # Format: +YYYY-MM-DDT00:00:00Z
            year_match = re.search(r'(\d{4})', info["founding_year"])
            if year_match:
                data["founding_year"] = year_match.group(1)
                print(f"  成立年份: {data['founding_year']}")
        
        # Country
        if info.get("country_qid"):
            country = resolve_qid_label(info["country_qid"])
            print(f"  国家: {country}")
            # Save country info
        
        # Founder
        if info.get("founder_qid"):
            founder = resolve_qid_label(info["founder_qid"])
            data["founder"] = founder
            print(f"  创始人: {founder}")
        
        # Website
        if info.get("website"):
            data["official_website"] = info["website"]
            print(f"  官网: {data['official_website']}")
        
        # Founding location (country name as simple approximation)
        if info.get("country_qid"):
            country = resolve_qid_label(info["country_qid"])
            data["founding_location"] = country
        
        # Description
        if info.get("zh_desc"):
            print(f"  Wikidata中文描述: {info['zh_desc']}")
        if info.get("en_desc"):
            print(f"  Wikidata英文描述: {info['en_desc']}")
        
        # Wikipedia pages
        if info.get("wiki_zh"):
            print(f"  中文Wikipedia: {info['wiki_zh']}")
        if info.get("wiki_en"):
            print(f"  英文Wikipedia: {info['wiki_en']}")
        
        data["wikidata_id"] = qid
        
        # Save updated brand.json
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(f"[{slug}] 无 Wikidata ID，跳过")
    
    time.sleep(0.5)  # Rate limit

print()
print("✅ Wikidata 信息查询完成")
print()
print("⚠️  品牌描述（description_zh/languages.en）仍为空")
print("   需要后续用 AI 生成品牌内容")
