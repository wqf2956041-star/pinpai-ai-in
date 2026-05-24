#!/usr/bin/env python3
"""补全品牌中文内容到500-800字，然后更新9语言翻译"""
import json, sys, urllib.request, urllib.parse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from generator import fetch_wikipedia_zh, fetch_wikipedia_en, LANGUAGES

def fetch_brand_info(name_cn, name_en):
    """抓取品牌信息，中英文结合"""
    # 先试中文
    zh_text, zh_title = fetch_wikipedia_zh(name_cn)
    
    # 再试英文抓长内容
    en_text, en_title = fetch_wikipedia_en(name_en)
    
    return zh_text or "", en_text or ""

# 需要补全的品牌
NEED_FIX = [
    {"name_cn": "范思哲", "name_en": "Versace", "slug": "versace"},
    {"name_cn": "乔治·阿玛尼", "name_en": "Armani", "slug": "armani"},
    {"name_cn": "克里斯汀·迪奥", "name_en": "Christian Dior", "slug": "christian-dior"},
    {"name_cn": "巴宝莉", "name_en": "Burberry", "slug": "burberry"},
    {"name_cn": "圣罗兰", "name_en": "Yves Saint Laurent", "slug": "saint-laurent"},
]

with open(ROOT / "brands_today.json") as f:
    today = json.load(f)

with open(ROOT / "brands_done.json") as f:
    done = json.load(f)

for fix in NEED_FIX:
    slug_guess = fix["slug"]
    # 找到brands_today里对应的
    brand = None
    for b in today["brands"]:
        # match by name_cn or try slug
        if b.get("name_cn", "").strip().lower() == fix["name_cn"].strip().lower() or slug_guess in b.get("name_en", "").lower():
            brand = b
            break
    
    if not brand:
        print(f"  [SKIP] {fix['name_cn']}: not found in brands_today.json")
        continue
    
    current_desc = brand.get("desc", "")
    if len(current_desc) >= 500:
        print(f"  [SKIP] {fix['name_cn']}: already {len(current_desc)}字")
        continue
    
    zh_text, en_text = fetch_brand_info(fix["name_cn"], fix["name_en"])
    print(f"  {fix['name_cn']}: current={len(current_desc)}字, zh_wiki={len(zh_text)}字, en_wiki={len(en_text)}字")

print("\nDone content check. Now need to update translations.")
print(f"Total brands in today: {len(today['brands'])}")
print(f"Brand names: {[b.get('name_cn','?') for b in today['brands']]}")
