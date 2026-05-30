#!/usr/bin/env python3
"""为第3批品牌查询Wikidata并创建模板"""
import json, urllib.request, csv
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

CAT_ZH = {
    "sport": "体育",
    "toy": "玩具",
    "food": "食品饮料",
    "auto": "汽车",
    "beauty": "美妆护肤"
}

brands_to_add = [
    {"name": "Adidas", "qid": "Q3699", "category": "sport", "country": "Germany"},
    {"name": "Lego", "qid": "Q1067778", "category": "toy", "country": "Denmark"},
    {"name": "Coca-Cola", "qid": "Q3519", "category": "food", "country": "United States"},
    {"name": "Ferrari", "qid": "Q27586", "category": "auto", "country": "Italy"},
    {"name": "L'Oréal", "qid": "Q337521", "category": "beauty", "country": "France"}
]

def fetch_wikidata(qid):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_label(entity, lang='en'):
    labels = entity.get('labels', {})
    return labels.get(lang, {}).get('value', '') or labels.get('en', {}).get('value', '')

def get_description(entity, lang='en'):
    descs = entity.get('descriptions', {})
    return descs.get(lang, {}).get('value', '') or descs.get('en', {}).get('value', '')

def get_founder(entity):
    claims = entity.get('claims', {})
    found = claims.get('P112', [])
    if found:
        mainsnak = found[0].get('mainsnak', {})
        if mainsnak.get('datatype') == 'wikibase-item':
            fqid = mainsnak.get('datavalue', {}).get('value', {}).get('id', '')
            if fqid:
                try:
                    fd = fetch_wikidata(fqid)
                    return get_label(fd['entities'][fqid], 'en')
                except:
                    pass
    return ''

def get_website(entity):
    claims = entity.get('claims', {})
    sites = claims.get('P856', [])
    for s in sites:
        mainsnak = s.get('mainsnak', {})
        if mainsnak.get('datatype') == 'url':
            return mainsnak.get('datavalue', {}).get('value', '')
    return ''

def get_year(entity):
    claims = entity.get('claims', {})
    inception = claims.get('P571', [])
    if inception:
        mainsnak = inception[0].get('mainsnak', {})
        try:
            ts = mainsnak.get('datavalue', {}).get('value', {}).get('time', '')
            if ts and ts.startswith('+'):
                return int(ts[1:5])
        except:
            pass
    return 0

for b in brands_to_add:
    slug = b['name'].lower().replace("'",'').replace(' ','-')
    brand_dir = ROOT / slug
    brand_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=== {b['name']} ({b['qid']}) ===")
    try:
        wd = fetch_wikidata(b['qid'])
        entity = wd['entities'][b['qid']]
        
        name_en = get_label(entity, 'en')
        name_zh = get_label(entity, 'zh-cn') or get_label(entity, 'zh') or ''
        desc_en = get_description(entity, 'en')
        desc_zh = get_description(entity, 'zh-cn') or get_description(entity, 'zh') or ''
        founder = get_founder(entity)
        website = get_website(entity)
        year = get_year(entity)
        
        print(f"  name_en: {name_en}")
        print(f"  name_zh: {name_zh}")
        print(f"  desc_en: {desc_en[:80]}")
        print(f"  desc_zh: {desc_zh[:80]}")
        print(f"  founder: {founder}")
        print(f"  website: {website}")
        print(f"  year: {year}")
        
        # 创建 brand.json
        brand_data = {
            "slug": slug,
            "name_en": name_en or b['name'],
            "name_zh": name_zh or b['name'],
            "category": b['category'],
            "country": b['country'],
            "founder": founder,
            "year": year,
            "website": website,
            "wikidata_id": b['qid'],
            "description_en": desc_en,
            "description_zh": desc_zh or desc_en,
            "languages": {
                "zh-CN": "",
                "en": "",
                "ja": "",
                "ko": "",
                "fr": "",
                "es": "",
                "de": "",
                "pt": "",
                "ru": "",
                "ar": ""
            }
        }
        
        (brand_dir / 'brand.json').write_text(json.dumps(brand_data, ensure_ascii=False, indent=2))
        print(f"  ✅ {slug}/brand.json created")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        # 创建基本模板
        brand_data = {
            "slug": slug,
            "name_en": b['name'],
            "name_zh": b['name'],
            "category": b['category'],
            "country": b['country'],
            "founder": "",
            "year": 0,
            "website": "",
            "wikidata_id": b['qid'],
            "description_en": "",
            "description_zh": "",
            "languages": {
                "zh-CN": "",
                "en": "",
                "ja": "",
                "ko": "",
                "fr": "",
                "es": "",
                "de": "",
                "pt": "",
                "ru": "",
                "ar": ""
            }
        }
        (brand_dir / 'brand.json').write_text(json.dumps(brand_data, ensure_ascii=False, indent=2))
        print(f"  ⚠️ Fallback template created")

print("\n✅ 第3批品牌模板创建完成")
