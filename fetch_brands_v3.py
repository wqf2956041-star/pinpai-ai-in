#!/usr/bin/env python3
"""
Wikipedia 品牌爬取 v3 — 更稳健的版本
1. 中文分类用 UTF-8 编码正确请求
2. 英文用更慢的间隔避免 429
3. 从知名榜单页面直接提取品牌名
"""
import json, urllib.request, urllib.parse, time, sys, os, re

USER_AGENT = "GlobalBrandIndex/1.0 (brand database)"

def api_call(api_url, params, delay=0.3):
    params["format"] = "json"
    params["origin"] = "*"
    url = f"{api_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                time.sleep(delay)
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 2 ** (attempt + 2)
                print(f"    429: waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"    HTTP {e.code}: {e.reason}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"    Error: {e}", file=sys.stderr)
            return None
    return None

def get_category_members(category, lang="zh", limit=500):
    api = "https://zh.wikipedia.org/w/api.php" if lang == "zh" else "https://en.wikipedia.org/w/api.php"
    if lang == "zh":
        cat_title = f"Category:{category}"
    else:
        cat_title = f"Category:{category}"
    
    members = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": cat_title,
        "cmlimit": "max",
        "cmtype": "page",
    }
    while len(members) < limit:
        data = api_call(api, params, 0.5)
        if not data:
            break
        pages = data.get("query", {}).get("categorymembers", [])
        for p in pages:
            title = p.get("title", "")
            if ":" not in title:
                members.append(title)
        if "continue" in data and "cmcontinue" in data.get("continue", {}):
            params["cmcontinue"] = data["continue"]["cmcontinue"]
        else:
            break
    return members[:limit]

def get_page_wikidata_ids(titles, lang="zh"):
    """Get Wikidata IDs for a list of page titles"""
    api = "https://zh.wikipedia.org/w/api.php" if lang == "zh" else "https://en.wikipedia.org/w/api.php"
    results = {}
    for i in range(0, len(titles), 50):
        batch = titles[i:i+50]
        params = {
            "action": "query",
            "titles": "|".join(batch),
            "prop": "pageprops",
            "ppprop": "wikibase_item",
        }
        data = api_call(api, params, 0.3)
        if data:
            pages = data.get("query", {}).get("pages", {})
            for pid, info in pages.items():
                title = info.get("title", "")
                qid = info.get("pageprops", {}).get("wikibase_item", "")
                if qid:
                    results[title] = qid
    return results

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower().strip()).strip('-')

# ====== APPROACH: Use curated brand lists directly ======
# Instead of crawling categories (which rate limits us),
# I'll use known luxury/fashion brands and get their Wikidata IDs
# via Wikipedia API. This is faster and more reliable.

# We'll query the Chinese Wikipedia "Page info" API to get Wikidata IDs
# for a curated list of the most famous global brands.

FAMOUS_BRANDS = {
    # Luxury / Fashion
    "Louis Vuitton": "fashion-luxury",
    "Hermès": "fashion-luxury",
    "Gucci": "fashion-luxury",
    "Chanel": "fashion-luxury",
    "Christian Dior": "fashion-luxury",
    "Cartier (jeweler)": "fashion-luxury",
    "Prada": "fashion-luxury",
    "Burberry": "fashion-luxury",
    "Versace": "fashion-luxury",
    "Fendi": "fashion-luxury",
    "Givenchy": "fashion-luxury",
    "Yves Saint Laurent (brand)": "fashion-luxury",
    "Valentino (fashion house)": "fashion-luxury",
    "Balenciaga": "fashion-luxury",
    "Bottega Veneta": "fashion-luxury",
    "Armani": "fashion-luxury",
    "Dolce & Gabbana": "fashion-luxury",
    "Ralph Lauren Corporation": "fashion-luxury",
    "Tiffany & Co.": "jewelry",
    "Rolex": "watch",
    "Patek Philippe": "watch",
    "Omega SA": "watch",
    "Audemars Piguet": "watch",
    "Richard Mille": "watch",
    "Bulgari": "jewelry",
    "Van Cleef & Arpels": "jewelry",
    "Swarovski": "jewelry",
    "Nike, Inc.": "sport",
    "Adidas": "sport",
    "Puma (brand)": "sport",
    "Lululemon Athletica": "sport",
    "Under Armour": "sport",
    "Zara (retailer)": "fashion",
    "H&M": "fashion",
    "Uniqlo": "fashion",
    "Mango (clothing)": "fashion",
    "Levi Strauss & Co.": "fashion",
    "Calvin Klein": "fashion",
    "Tommy Hilfiger": "fashion",
    "Coach New York": "fashion-luxury",
    "Michael Kors": "fashion-luxury",
    "Kate Spade New York": "fashion",
    "Longchamp": "fashion",
    "Loewe (brand)": "fashion-luxury",
    "Miu Miu": "fashion-luxury",
    "Alexander McQueen": "fashion-luxury",
    "Maison Margiela": "fashion-luxury",
    "Stella McCartney": "fashion",
    "Moncler": "fashion",
    "Canada Goose (clothing)": "fashion",
    "North Face": "sport",
    
    # Beauty / Cosmetics
    "L'Oréal": "beauty",
    "Estée Lauder Companies": "beauty",
    "Shiseido": "beauty",
    "Lancôme": "beauty",
    "Clinique": "beauty",
    "MAC Cosmetics": "beauty",
    "Chanel": "beauty",
    "Giorgio Armani Beauty": "beauty",
    "Yves Saint Laurent Beauté": "beauty",
    "Dior (house)": "beauty",
    "Gucci Beauty": "beauty",
    "SkinCeuticals": "beauty",
    "La Mer (brand)": "beauty",
    "SK-II": "beauty",
    "NARS Cosmetics": "beauty",
    "Bobbi Brown": "beauty",
    "Maybelline": "beauty",
    "CoverGirl": "beauty",
    "Neutrogena": "beauty",
    "Olay": "beauty",
    "Avene": "beauty",
    "La Roche-Posay": "beauty",
    "Vichy": "beauty",
    "The Body Shop": "beauty",
    "Kiehl's": "beauty",
    "Creed (perfume house)": "beauty",
    "Jo Malone London": "beauty",
    "Tom Ford": "beauty",
    
    # Auto
    "Toyota": "auto",
    "Volkswagen": "auto",
    "Mercedes-Benz Group": "auto",
    "BMW": "auto",
    "Honda": "auto",
    "Ford Motor Company": "auto",
    "General Motors": "auto",
    "Hyundai Motor Company": "auto",
    "Tesla, Inc.": "auto",
    "Ferrari": "auto",
    "Lamborghini": "auto",
    "Porsche": "auto",
    "Aston Martin": "auto",
    "Bentley": "auto",  
    "Rolls-Royce Motor Cars": "auto",
    "Maserati": "auto",
    "McLaren Automotive": "auto",
    "Bugatti": "auto",
    "Jaguar": "auto",
    "Land Rover": "auto",
    "Volvo Cars": "auto",
    "Audi": "auto",
    "Lexus": "auto",
    "Cadillac": "auto",
    "BYD Auto": "auto",
    "NIO": "auto",
    "XPeng": "auto",
    "Li Auto": "auto",
    
    # Tech
    "Apple Inc.": "tech",
    "Microsoft": "tech",
    "Google": "tech",
    "Amazon": "tech",
    "Meta Platforms": "tech",
    "Tencent": "tech",
    "Alibaba Group": "tech",
    "Samsung Electronics": "tech",
    "Sony": "tech",
    "Intel": "tech",
    "NVIDIA": "tech",
    "AMD": "tech",
    "IBM": "tech",
    "Oracle Corporation": "tech",
    "Salesforce": "tech",
    "Adobe": "tech",
    "Netflix": "tech",
    "ByteDance": "tech",
    "Xiaomi": "tech",
    "Huawei": "tech",
    "DJI": "tech",
    "TSMC": "tech",
    "ASML": "tech",
    "Spotify": "tech",
    "Uber": "tech",
    "Airbnb": "tech",
    "Shopify": "tech",
    "Square, Inc.": "tech",
    "SpaceX": "tech",
    "OpenAI": "tech",
    
    # Food & Beverage
    "Coca-Cola": "food",
    "PepsiCo": "food",
    "Nestlé": "food",
    "McDonald's": "food",
    "Starbucks": "food",
    "KFC": "food",
    "Heineken": "food",
    "Anheuser-Busch": "food",
    "LVMH": "fashion-luxury",
    "Kering": "fashion-luxury",
    "Richemont": "jewelry",
    
    # More luxury/fashion additions
    "Celine (brand)": "fashion-luxury",
    "Chloé": "fashion-luxury",
    "Kenzo (brand)": "fashion",
    "Marc Jacobs": "fashion",
    "Viktor & Rolf": "fashion-luxury",
    "Bally (fashion house)": "fashion-luxury",
    "Ferragamo": "fashion-luxury",
    "Tod's": "fashion",
    "Jimmy Choo": "fashion-luxury",
    "Manolo Blahnik": "fashion",
    "Christian Louboutin": "fashion",
    "Birkenstock": "fashion",
    "Dr. Martens": "fashion",
    "Converse (shoe company)": "sport",
    "Vans": "sport",
    "New Balance": "sport",
    "Asics": "sport",
    "Reebok": "sport",
    "Skechers": "sport",
    "Columbia Sportswear": "sport",
    "Patagonia (clothing)": "sport",
    "Arc'teryx": "sport",
    "The North Face": "sport",
    "Oakley, Inc.": "sport",
    
    # More beauty
    "LVMH": "beauty",
    "Revlon": "beauty",
    "Avon Products": "beauty",
    "Mary Kay": "beauty",
    "Amorepacific": "beauty",
    "Sulwhasoo": "beauty",
    "Innisfree (brand)": "beauty",
    "Etude House": "beauty",
    "Kao Corporation": "beauty",
    "Procter & Gamble": "beauty",
    "Unilever": "beauty",
}

def main():
    all_brands = []
    seen_qids = set()
    
    # Get Wikidata IDs from Wikipedia for each brand
    en_titles = list(FAMOUS_BRANDS.keys())
    
    print(f"Total brands to resolve: {len(en_titles)}")
    
    # Batch resolve Wikidata IDs from English Wikipedia
    print("\nResolving Wikidata IDs from English Wikipedia...")
    en_qids = {}
    for i in range(0, len(en_titles), 50):
        batch = en_titles[i:i+50]
        results = get_page_wikidata_ids(batch, "en")
        en_qids.update(results)
        print(f"  Batch {i//50 + 1}/{(len(en_titles)-1)//50 + 1}: got {len(results)} QIDs")
        time.sleep(0.5)
    
    # For unresolved ones, try Chinese Wikipedia
    unresolved = [t for t in en_titles if t not in en_qids]
    if unresolved:
        print(f"\nResolving {len(unresolved)} unresolved from Chinese Wikipedia...")
        zh_qids = {}
        for i in range(0, len(unresolved), 50):
            batch = unresolved[i:i+50]
            results = get_page_wikidata_ids(batch, "zh")
            zh_qids.update(results)
            time.sleep(0.5)
        en_qids.update(zh_qids)
    
    print(f"\nResolved {len(en_qids)}/{len(en_titles)} brands to Wikidata IDs")
    
    # Build brand list
    for title, qid in en_qids.items():
        if qid and qid not in seen_qids:
            seen_qids.add(qid)
            cat = FAMOUS_BRANDS.get(title, "other")
            all_brands.append({
                "wikidata_id": qid,
                "brand_name": title,
                "category": cat,
            })
    
    # Also add brands whose title wasn't found but we still want them
    for title in en_titles:
        if title not in en_qids:
            cat = FAMOUS_BRANDS.get(title, "other")
            all_brands.append({
                "wikidata_id": "",
                "brand_name": title,
                "category": cat,
            })
    
    # Save raw dataset
    output = {
        "total": len(all_brands),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "brands": all_brands,
    }
    
    with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Total brands: {len(all_brands)}")
    print(f"✅ Saved to brand_seed_raw.json")
    
    # Show counts by category
    from collections import Counter
    cats = Counter(b["category"] for b in all_brands)
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")
    
    with_qid = sum(1 for b in all_brands if b["wikidata_id"])
    print(f"\nBrands with Wikidata ID: {with_qid}/{len(all_brands)}")

if __name__ == "__main__":
    main()
