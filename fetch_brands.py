#!/usr/bin/env python3
"""
Wikidata → 全球品牌种子库
从 Wikidata SPARQL 爬取全球知名品牌，生成 master.csv 的种子数据
"""

import csv, json, urllib.request, urllib.parse, time, sys, os, re
from urllib.error import HTTPError

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
USER_AGENT = "GlobalBrandIndex/1.0 (brand database builder)"
DELAY = 0.3  # seconds between queries

def query_wikidata(sparql, retries=3):
    """Execute SPARQL query against Wikidata"""
    params = urllib.parse.urlencode({"format": "json", "query": sparql})
    url = f"{WIKIDATA_SPARQL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return None
    return None

def slugify(name):
    """Convert brand name to URL-safe slug"""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug

def clean_wiki_name(raw):
    """Clean Wikipedia page title from URL"""
    if raw and raw.startswith("http"):
        raw = raw.rsplit("/", 1)[-1]
    return raw.replace("_", " ") if raw else ""

def get_country_name(qid):
    """Fetch country name from Wikidata QID"""
    sparql = f"""
    SELECT ?countryLabel WHERE {{
      wd:{qid} rdfs:label ?countryLabel.
      FILTER(LANG(?countryLabel) = "zh")
    }}
    """
    result = query_wikidata(sparql)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"][0].get("countryLabel", {}).get("value", "")
    # fallback: English
    sparql = f"""
    SELECT ?countryLabel WHERE {{
      wd:{qid} rdfs:label ?countryLabel.
      FILTER(LANG(?countryLabel) = "en")
    }}
    """
    result = query_wikidata(sparql)
    if result and result.get("results", {}).get("bindings"):
        return result["results"]["bindings"][0].get("countryLabel", {}).get("value", "")
    return ""

def fetch_brands_by_category(category_name, sparql_filter):
    """Fetch brands from Wikidata for a category"""
    sparql = f"""
    SELECT DISTINCT ?item ?itemLabel ?itemDescription ?country ?countryLabel ?website ?inception ?foundedBy ?foundedByLabel ?wikipedia WHERE {{
      {sparql_filter}
      ?item wdt:P31 wd:Q4830453.  # instance of business
      OPTIONAL {{ ?item wdt:P17 ?country. }}
      OPTIONAL {{ ?item wdt:P856 ?website. }}
      OPTIONAL {{ ?item wdt:P571 ?inception. }}
      OPTIONAL {{ ?item wdt:P112 ?foundedBy. }}
      OPTIONAL {{
        ?wikipedia schema:about ?item;
                  schema:isPartOf <https://zh.wikipedia.org/>;
                  schema:name ?wpTitle.
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "zh,en". }}
    }}
    ORDER BY DESC(?item)  # prioritize items with more sitelinks
    LIMIT 300
    """
    result = query_wikidata(sparql)
    if not result:
        return []
    
    brands = []
    for binding in result.get("results", {}).get("bindings", []):
        item_id = binding.get("item", {}).get("value", "").split("/")[-1]
        label = binding.get("itemLabel", {}).get("value", "")
        desc = binding.get("itemDescription", {}).get("value", "")
        country_qid = binding.get("country", {}).get("value", "").split("/")[-1] if binding.get("country") else ""
        country_label = binding.get("countryLabel", {}).get("value", "")
        website = binding.get("website", {}).get("value", "")
        inception = binding.get("inception", {}).get("value", "")
        founder = binding.get("foundedByLabel", {}).get("value", "")
        wp_title = binding.get("wpTitle", {}).get("value", "")
        
        if not label or len(label) < 2:
            continue
        
        # Get Chinese name if available
        zh_sparql = f"""
        SELECT ?label WHERE {{
          wd:{item_id} rdfs:label ?label.
          FILTER(LANG(?label) = "zh")
        }}
        """
        zh_result = query_wikidata(zh_sparql)
        zh_name = ""
        if zh_result and zh_result.get("results", {}).get("bindings"):
            zh_name = zh_result["results"]["bindings"][0].get("label", {}).get("value", "")
        
        # Get English name
        en_sparql = f"""
        SELECT ?label WHERE {{
          wd:{item_id} rdfs:label ?label.
          FILTER(LANG(?label) = "en")
        }}
        """
        en_result = query_wikidata(en_sparql)
        en_name = ""
        if en_result and en_result.get("results", {}).get("bindings"):
            en_name = en_result["results"]["bindings"][0].get("label", {}).get("value", "")
        
        display_name = zh_name if zh_name else en_name if en_name else label
        en_display = en_name if en_name else label
        
        brand = {
            "wikidata_id": item_id,
            "brand_name": display_name,
            "brand_name_en": en_display,
            "description": desc,
            "country_qid": country_qid,
            "country": country_label,
            "website": website,
            "founded_year": inception[:4] if inception else "",
            "founder": founder,
            "category": category_name,
            "wikipedia_zh": wp_title,
        }
        brands.append(brand)
        time.sleep(DELAY)
    
    return brands

def main():
    all_brands = []
    seen_qids = set()
    
    categories = [
        ("fashion-luxury", "?item wdt:P452 wd:Q192427. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # luxury fashion brand"),
        ("fashion", "?item wdt:P452 wd:Q28895122. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # fashion brand"),
        ("fashion", "?item wdt:P452 wd:Q131524. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # clothing industry"),
        ("auto", "?item wdt:P452 wd:Q228519. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # automotive industry"),
        ("beauty", "?item wdt:P452 wd:Q270908. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # cosmetics industry"),
        ("tech", "?item wdt:P452 wd:Q11427. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # consumer electronics"),
        ("tech", "?item wdt:P452 wd:Q193179. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # internet industry"),
        ("sport", "?item wdt:P452 wd:Q260937. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # sporting goods"),
        ("food", "?item wdt:P452 wd:Q2095. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # food industry"),
        ("watch", "?item wdt:P452 wd:Q7187. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # watchmaking"),
        ("jewelry", "?item wdt:P452 wd:Q485354. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # jewellery"),
        ("toy", "?item wdt:P452 wd:Q203673. SERVICE wikibase:label { bd:serviceParam wikibase:language 'zh,en'. }  # toy industry"),
    ]
    
    total = len(categories)
    for idx, (cat, sparql_filter) in enumerate(categories, 1):
        print(f"[{idx}/{total}] Fetching {cat}...", flush=True)
        brands = fetch_brands_by_category(cat, sparql_filter)
        
        new_count = 0
        for b in brands:
            qid = b["wikidata_id"]
            if qid not in seen_qids:
                seen_qids.add(qid)
                all_brands.append(b)
                new_count += 1
        
        print(f"  → Got {len(brands)}, new unique: {new_count}, total: {len(all_brands)}", flush=True)
        time.sleep(1)  # rate limiting between categories
    
    # Save raw dataset
    output = {
        "total": len(all_brands),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "brands": all_brands,
    }
    
    with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Total unique brands fetched: {len(all_brands)}")
    print(f"✅ Saved to brand_seed_raw.json")
    
    # Print top brands by category
    from collections import Counter
    cat_counts = Counter(b["category"] for b in all_brands)
    for cat, count in cat_counts.most_common():
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()
