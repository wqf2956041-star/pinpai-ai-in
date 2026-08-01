#!/usr/bin/env python3
"""从Wikidata查品牌信息并写入brand.json"""
import json, urllib.request
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

QIDS = {
    "anheuser-busch": "Q128738",
    "aesop": "Q4688560",
    "benetton": "Q817139",
    "chaumet": "Q2961620",
    "a--lange-and-s-hne": "Q278880",
}

entities = {}
for slug, qid in QIDS.items():
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        raw = json.loads(urllib.request.urlopen(req, timeout=15).read())
        entities[qid] = raw["entities"][qid]
        print(f"  {slug}: {qid} OK")
    except Exception as e:
        print(f"  {slug}: {e}")

def extract_info(qid):
    e = entities.get(qid)
    if not e:
        return {}
    claims = e.get("claims", {})
    info = {}
    
    # 成立年份 P571
    if "P571" in claims:
        t = claims["P571"][0].get("mainsnak",{}).get("datavalue",{}).get("value",{})
        if isinstance(t, dict):
            info["year"] = t.get("time","").lstrip("+")
    
    # 创始人 P112
    if "P112" in claims:
        founders = []
        for c in claims["P112"]:
            v = c.get("mainsnak",{}).get("datavalue",{}).get("value",{})
            if isinstance(v, dict) and "id" in v:
                founders.append(v["id"])
        info["founders"] = founders
    
    # 官网 P856
    if "P856" in claims:
        url_v = claims["P856"][0].get("mainsnak",{}).get("datavalue",{}).get("value","")
        if isinstance(url_v, str) and url_v.startswith("http"):
            info["website"] = url_v
    
    # 国家 P17
    if "P17" in claims:
        ctry = claims["P17"][0].get("mainsnak",{}).get("datavalue",{}).get("value",{})
        if isinstance(ctry, dict) and "id" in ctry:
            info["country_qid"] = ctry["id"]
    
    # 总部地点 P159
    if "P159" in claims:
        loc = claims["P159"][0].get("mainsnak",{}).get("datavalue",{}).get("value",{})
        if isinstance(loc, dict) and "id" in loc:
            info["location_qid"] = loc["id"]
    
    # 标签和描述
    info["label"] = e.get("labels",{}).get("en",{}).get("value","")
    info["desc"] = e.get("descriptions",{}).get("en",{}).get("value","")
    
    return info

# 解析国家/地名标签
def get_label(qid):
    if not qid:
        return ""
    e = entities.get(qid, {})
    if e:
        return e.get("labels",{}).get("en",{}).get("value","")
    return ""

for slug, qid_list in QIDS.items():
    qid = qid_list
    brand_dir = ROOT / slug
    json_path = brand_dir / "brand.json"
    data = json.loads(json_path.read_text())
    
    info = extract_info(qid)
    
    print(f"\n=== {slug} ({data['names']['en']}) ===")
    print(f"  Wikidata: {qid}")
    print(f"  标签: {info.get('label','')}")
    print(f"  描述: {info.get('desc','')}")
    print(f"  成立: {info.get('year','')}")
    print(f"  网站: {info.get('website','')}")
    print(f"  创始人QID: {info.get('founders','')}")
    print(f"  国家: {get_label(info.get('country_qid',''))}")
    print(f"  地点: {get_label(info.get('location_qid',''))}")
    
    # 写入brand.json
    data["founding_year"] = info.get("year","")
    data["official_website"] = info.get("website","")
    data["founding_location"] = get_label(info.get("location_qid","")) or get_label(info.get("country_qid",""))
    data["country"] = get_label(info.get("country_qid",""))
    
    # 翻译创始人QID→名字
    if info.get("founders"):
        founder_labels = []
        for fid in info["founders"]:
            f_entity = entities.get(fid, {})
            label = f_entity.get("labels",{}).get("en",{}).get("value",fid)
            founder_labels.append(label)
        data["founder"] = ", ".join(founder_labels)
        print(f"  创始人: {data['founder']}")
    
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"  ✅ brand.json 已更新")
