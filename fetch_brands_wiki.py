#!/usr/bin/env python3
"""
一键批量生成5个品牌 × 10语言的 brand.json
流程：用种子库的Wikidata QID查询基本信息 → AI写10语言内容 → 写入brand.json
"""
import json, sys, os, re, urllib.request
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")
GEN_LOG = ROOT / "brand_gen_log.json"

BRANDS = [
    {
        "slug": "hermes",
        "qid": "Q843887",
        "brand_name": "Hermès",
        "category": "fashion-luxury",
        "country": "法国",
        "industry": "奢侈品"
    },
    {
        "slug": "bmw",
        "qid": "Q26678",
        "brand_name": "BMW",
        "category": "auto",
        "country": "德国",
        "industry": "汽车"
    },
    {
        "slug": "sony",
        "qid": "Q41187",
        "brand_name": "Sony",
        "category": "tech",
        "country": "日本",
        "industry": "科技"
    },
    {
        "slug": "nike",
        "qid": "Q218202",
        "brand_name": "Nike",
        "category": "sport",
        "country": "美国",
        "industry": "运动"
    },
    {
        "slug": "chanel",
        "qid": "Q218115",
        "brand_name": "Chanel",
        "category": "fashion-luxury",
        "country": "法国",
        "industry": "奢侈品"
    }
]

# Wikidata SPARQL查询函数
def wikidata_query(qid):
    """查询Wikidata获取品牌基本信息"""
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pinpai-ai-in/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        entity = data.get("entities", {}).get(qid, {})
        claims = entity.get("claims", {})
        
        info = {}
        
        # 中文标签
        labels = entity.get("labels", {})
        zh_label = labels.get("zh", {}).get("value", "")
        en_label = labels.get("en", {}).get("value", "")
        if zh_label: info["name_zh"] = zh_label
        if en_label: info["name_en"] = en_label
        
        # 中文描述
        descs = entity.get("descriptions", {})
        zh_desc = descs.get("zh", {}).get("value", "")
        en_desc = descs.get("en", {}).get("value", "")
        if zh_desc: info["desc_zh"] = zh_desc
        if en_desc: info["desc_en"] = en_desc
        
        # 成立年份 (P571)
        inception = claims.get("P571", [])
        if inception and "mainsnak" in inception[0]:
            val = inception[0]["mainsnak"].get("datavalue", {}).get("value", {})
            if isinstance(val, dict):
                info["founding_year"] = val.get("time", "").replace("+", "").split("-")[0] if val.get("time") else ""
        
        # 创始地 (P1071)
        location = claims.get("P1071", []) or claims.get("P740", [])
        if location and "mainsnak" in location[0]:
            loc_qid = location[0]["mainsnak"].get("datavalue", {}).get("value", {}).get("id", "")
            if loc_qid:
                loc_url = f"https://www.wikidata.org/wiki/Special:EntityData/{loc_qid}.json"
                loc_req = urllib.request.Request(loc_url, headers={"User-Agent": "pinpai-ai-in/1.0"})
                with urllib.request.urlopen(loc_req, timeout=15) as loc_resp:
                    loc_data = json.loads(loc_resp.read())
                loc_entity = loc_data.get("entities", {}).get(loc_qid, {})
                zh_loc = loc_entity.get("labels", {}).get("zh", {}).get("value", "")
                en_loc = loc_entity.get("labels", {}).get("en", {}).get("value", "")
                if zh_loc: info["founding_location_zh"] = zh_loc
                if en_loc: info["founding_location_en"] = en_loc
        
        # 创始人 (P112)
        founders = claims.get("P112", [])
        founder_names = []
        if founders:
            for f in founders[:3]:
                f_qid = f.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
                if f_qid:
                    f_url = f"https://www.wikidata.org/wiki/Special:EntityData/{f_qid}.json"
                    try:
                        f_req = urllib.request.Request(f_url, headers={"User-Agent": "pinpai-ai-in/1.0"})
                        with urllib.request.urlopen(f_req, timeout=15) as f_resp:
                            f_data = json.loads(f_resp.read())
                        f_entity = f_data.get("entities", {}).get(f_qid, {})
                        zh_fn = f_entity.get("labels", {}).get("zh", {}).get("value", "")
                        en_fn = f_entity.get("labels", {}).get("en", {}).get("value", "")
                        if zh_fn: founder_names.append(zh_fn)
                    except: pass
        if founder_names: info["founders"] = founder_names
        
        # 官网 (P856)
        website = claims.get("P856", [])
        if website:
            val = website[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
            if val: info["official_website"] = val
        
        # logo图片 (P154)
        logo = claims.get("P154", [])
        if logo:
            img = logo[0].get("mainsnak", {}).get("datavalue", {}).get("value", "")
            if img: info["image_url"] = img
        
        return info
    
    except Exception as e:
        print(f"  ⚠️ Wikidata查询失败 ({qid}): {e}")
        return {}

def main():
    print("=" * 60)
    print("品牌百科 — 5品牌 × 10语言 内容生成")
    print("=" * 60)
    
    gen_log = {}
    if GEN_LOG.exists():
        gen_log = json.loads(GEN_LOG.read_text())
    total = len(BRANDS)
    
    for i, brand in enumerate(BRANDS, 1):
        slug = brand["slug"]
        print(f"\n[{i}/{total}] {brand['brand_name']} ({slug})")
        print("-" * 40)
        
        # 1. Wikidata查询
        print("  [1/3] Wikidata信息查询...")
        wiki_info = wikidata_query(brand["qid"])
        if wiki_info:
            print(f"    ✅ 中文名: {wiki_info.get('name_zh','')}")
            print(f"    ✅ 英文名: {wiki_info.get('name_en','')}")
            if wiki_info.get("founding_year"):
                print(f"    ✅ 成立年份: {wiki_info['founding_year']}")
            if wiki_info.get("founders"):
                print(f"    ✅ 创始人: {', '.join(wiki_info['founders'])}")
            if wiki_info.get("official_website"):
                print(f"    ✅ 官网: {wiki_info['official_website']}")
        else:
            print("    ⚠️ 未获取到Wiki数据，使用默认值")
        
        # 2. 输出最终要写入的JSON结构
        brand_json = {
            "slug": slug,
            "names": {
                "zh-CN": wiki_info.get("name_zh", brand["brand_name"]),
                "en": wiki_info.get("name_en", brand["brand_name"]),
                "fr": "",
                "es": "",
                "de": "",
                "ja": "",
                "ko": "",
                "pt": "",
                "ru": "",
                "ar": ""
            },
            "category": brand["category"],
            "founding_year": int(wiki_info.get("founding_year", 2000)) if wiki_info.get("founding_year", "").isdigit() else 2000,
            "founding_location": wiki_info.get("founding_location_zh", brand["country"]),
            "founding_location_en": wiki_info.get("founding_location_en", brand["country"]),
            "founder": "、".join(wiki_info.get("founders", [brand["country"] + "企业家"])),
            "official_website": wiki_info.get("official_website", ""),
            "main_business": [brand["industry"]],
            "current_slogan": "",
            "description_zh": "",
            "languages": {
                "en": "",
                "zh-CN": "",
                "fr": "",
                "es": "",
                "de": "",
                "ja": "",
                "ko": "",
                "pt": "",
                "ru": "",
                "ar": ""
            },
            "similar_brands": [],
            "is_premium": brand["category"] in ["fashion-luxury", "tech"],
            "image_url": wiki_info.get("image_url", ""),
            "representative_products": [],
            "key_events": [],
            "philanthropy": [],
            "exhibitions": [],
            "past_slogans": [],
            "_meta": {
                "version": "2.0.0",
                "created_at": "",
                "validator_pass": False
            }
        }
        
        # 写入
        brand_dir = ROOT / slug
        brand_dir.mkdir(parents=True, exist_ok=True)
        (brand_dir / "brand.json").write_text(
            json.dumps(brand_json, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"    ✅ brand.json 模板已写入 (待AI填充10语言内容)")
        gen_log[slug] = {"status": "template_ready", "wiki_info": {k: v for k, v in wiki_info.items()}}
    
    GEN_LOG.write_text(json.dumps(gen_log, ensure_ascii=False, indent=2))
    print(f"\n{'='*60}")
    print("✅ 5个品牌模板就绪，等待AI填充10语言内容")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
