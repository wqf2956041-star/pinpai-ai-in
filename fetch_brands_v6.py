#!/usr/bin/env python3
"""
v6: 补齐 QID + 扩充到1000+品牌 + 选出前50
"""
import json, urllib.request, urllib.parse, time, re, sys, os, csv

USER_AGENT = "GlobalBrandIndex/1.0"

def wikidata_search(query):
    """Search Wikidata by label"""
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "limit": 1,
        "format": "json",
        "origin": "*",
    }
    url = f"https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            for r in data.get("search", []):
                return r.get("id", "")
    except:
        return ""
    return ""

def main():
    # Load current dataset
    with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "r") as f:
        data = json.load(f)
    
    brands = data["brands"]
    with_qid = {b["wikidata_id"]: b for b in brands if b.get("wikidata_id")}
    no_qid = [b for b in brands if not b.get("wikidata_id")]
    
    print(f"Total: {len(brands)}")
    print(f"With QID: {len(with_qid)}")
    print(f"Without QID: {len(no_qid)}")
    
    # Try to resolve missing QIDs
    print("\nResolving missing Wikidata IDs...")
    resolved = 0
    unresolved_names = []
    
    for b in no_qid:
        name = b["brand_name"]
        qid = wikidata_search(name)
        if qid:
            b["wikidata_id"] = qid
            with_qid[qid] = b
            resolved += 1
        else:
            unresolved_names.append(b["brand_name"])
        time.sleep(0.15)
    
    print(f"Resolved: {resolved}, Still missing: {len(unresolved_names)}")
    
    brands_list = list(with_qid.values())
    
    # Now expand categories to broader lists
    # Still have room for ~500 more brands from source lists
    # Use known brand expansions
    
    extra_brands = {
        "fashion-luxury": ["Rimowa", "Moynat", "Goyard", "Delvaux", "Mackintosh",
                          "John Lobb", "Berluti", "A. Lange & Söhne", "Jaquet Droz",
                          "Ulysse Nardin", "Girard-Perregaux", "H. Moser & Cie",
                          "Christophe Claret", "Greubel Forsey", "De Bethune",
                          "Creed", "Xerjoff", "Roja Parfums", "Clive Christian",
                          "Henry Jacques", "The Harmonist", "Memo Paris"],
        "fashion": ["A.P.C.", "COS", "& Other Stories", "Weekday", "Monki",
                   "Arket", "Massimo Dutti", "Pull & Bear", "Bershka",
                   "Stradivarius", "Oysho", "Uterqüe",
                   "GANT", "NA-KD", "Boohoo", "PrettyLittleThing",
                   "ASOS", "Zalando", "About You", "Farfetch",
                   "Ssense", "MatchesFashion", "Net-a-Porter",
                   "Reformation", "Everlane", "Allbirds", "Rothy's",
                   "Madewell", "Frame", "AG Jeans", "Paige",
                   "Rag & Bone", "Theory", "Vince", "Scotch & Soda",
                   "Samsøe Samsøe", "Ganni", "Rotate", "By Malene Birger",
                   "Stine Goya", "Baum und Pferdgarten", "Shaping New Tomorrow"],
        "beauty": ["Huda Beauty", "Fenty Beauty", "Kylie Cosmetics", "Rare Beauty",
                  "Glossier", "Milk Makeup", "Ilia", "Saie", "Kosas",
                  "Tower 28", "Merit", "Westman Atelier", "Jones Road",
                  "Tatcha", "Herbivore", "Youth to the People",
                  "Summer Fridays", "Sol de Janeiro", "Gisou",
                  "Olaplex", "Kérastase", "Redken", "L'Oréal Professionnel",
                  "Davines", "Oribe", "Living Proof", "Aveda",
                  "Bumble and bumble", "Moroccanoil", "Christophe Robin",
                  "Dermalogica", "Murad", "Dr. Barbara Sturm",
                  "Augustinus Bader", "111Skin", "Helena Rubinstein",
                  "Erno Laszlo", "Chantecaille", "By Terry",
                  "Hourglass", "Pat McGrath Labs", "Anastasia Beverly Hills"],
        "tech": ["Canon", "Nikon", "Fujifilm", "Leica", "Hasselblad",
                "Olympus", "Panasonic", "Ricoh", "Pentax",
                "Dyson", "iRobot", "Roomba", "Shark",
                "GoPro", "Ring", "Nest", "Arlo",
                "Seagate", "Western Digital", "Kingston", "Crucial",
                "Corsair", "G.Skill", "Samsung", "SanDisk",
                "Roku", "Chromecast", "Apple TV", "Fire TV",
                "Sonos", "Bose", "JBL", "Harman Kardon",
                "Sennheiser", "Beyerdynamic", "Audio-Technica",
                "Shure", "Marshall", "Bang & Olufsen",
                "Samsung", "LG", "SONY", "Panasonic", "TCL",
                "Hisense", "Vizio", "Sharp", "Toshiba",
                "TikTok", "Telegram", "Signal", "WhatsApp",
                "WeChat", "Line", "KakaoTalk", "Viber",
                "Notion", "Figma", "Canva", "Miro", "Airtable",
                "Monday.com", "Asana", "Trello", "Jira",
                "Wix", "Squarespace", "Webflow", "WordPress"],
        "auto": ["Pirelli", "Michelin", "Continental", "Goodyear", "Bridgestone",
                "Bosch", "Denso", "Valeo", "ZF Friedrichshafen",
                "Magna International", "Aisin", "Faurecia",
                "Shell", "BP", "TotalEnergies", "ExxonMobil",
                "Chevron", "PetroChina", "Sinopec",
                "Hertz", "Avis", "Enterprise", "Turo",
                "Uber", "Lyft", "DiDi", "Grab",
                "Yamaha", "Kawasaki", "Harley-Davidson",
                "Ducati", "BMW Motorrad", "KTM", "Aprilia",
                "Triumph", "Royal Enfield", "Vespa"],
        "food": ["Starbucks Reserve", "Blue Bottle", "Peet's", "Philz",
                "Intelligentsia", "Counter Culture", "Stumptown",
                "Tim Hortons", "Dunkin' Donuts", "Mister Donut",
                "Baskin-Robbins", "Cold Stone", "Haagen-Dazs",
                "Ben & Jerry's", "Magnum", "Mövenpick",
                "Krispy Kreme", "Cinnabon", "Auntie Anne's",
                "Pret a Manger", "Eataly", "Whole Foods",
                "Trader Joe's", "Sprouts", "Aldi", "Lidl",
                "Oatly", "Alpro", "Silk", "Califia Farms",
                "Beyond Meat", "Impossible Foods", "Quorn",
                "MorningStar", "Garden Gourmet",
                "HelloFresh", "Blue Apron", "Gousto", "Marley Spoon",
                "PureGym", "David Lloyd", "Equinox",
                "Peloton", "Mirror", "Tonal", "Hydrow"],
        "sport": ["Decathlon", "Intersport", "Sport Chek", "REI",
                 "Dicks Sporting Goods", "Academy Sports",
                 "Yeti", "Hydro Flask", "Stanley", "Thermos",
                 "Nalgene", "CamelBak", "Gregory", "Osprey",
                 "Deuter", "Vaude", "Mammut", "Millet",
                 "Black Diamond", "Petzl", "Grivel",
                 "Burton", "Lib Tech", "GNU", "Ride",
                 "Salomon", "Rossignol", "Atomic", "Head",
                 "Fischer", "Nordica", "Volkl",
                 "Rip Curl", "Quiksilver", "Billabong",
                 "Roxy", "O'Neill", "Hurley", "Volcom",
                 "Element", "Santa Cruz", "Powell-Peralta",
                 "Baker", "Girl", "Zero Skateboards"],
        "watch": ["Myota", "Fossil", "Michael Kors", "Emporio Armani",
                  "Diesel", "Guess", "Tommy Hilfiger", "Hugo Boss",
                  "Lacoste", "Police", "Nixon", "G-Shock",
                  "Baby-G", "Edifice", "Pro Trek",
                  "Tissot", "Hamilton", "Mido", "Certina",
                  "Mondaine", "Junghans", "Stowa", "Laco",
                  "Steinhart", "Sinn", "Damasko", "Mühle Glashütte",
                  "Kurono Tokyo", "Grand Seiko", "Credor",
                  "Maurice Lacroix", "Raymond Weil", "Frederique Constant",
                  "Oris", "Alpina", "TAG Heuer", "Breitling"],
        "jewelry": ["Pandora", "Alex and Ani", "Kendra Scott", "Gorjana",
                   "Jacquie Aiche", "Jennifer Meyer", "Foundrae",
                   "Catbird", "Mejuri", "Vrai", "Auvere",
                   "Brilliant Earth", "Blue Nile", "James Allen",
                   "Tiffany & Co.", "David Yurman", "John Hardy",
                   "Chopard", "Mikimoto", "Tasaki",
                   "Stauer", "Ross-Simons", "Danbury Mint"],
        "toy": ["Melissa & Doug", "Brio", "Hape", "PlanToys",
                "Green Toys", "Le Toy Van", "Djeco", "Janod",
                "Moulin Roty", "Londji", "SES Creative",
                "Ravensburger", "HABA", "Grimm's", "Grapat",
                "Oribel", "LAMAZE", "Bright Starts",
                "Skip Hop", "Summer Infant", "Fisher-Price",
                "Little Tikes", "Step2", "Radio Flyer",
                "Lego", "Duplo", "Mega Bloks", "Magna-Tiles",
                "PicassoTiles", "100 Wood Toys",
                "Jellycat", "Squishmallows", "Steiff",
                "Gund", "Douglas", "Aurora World"],
    }
    
    seen_names = set(b["brand_name"].lower() for b in brands_list)
    
    for cat, names in extra_brands.items():
        for name in names:
            if name.lower() not in seen_names:
                seen_names.add(name.lower())
                
                # Try to get QID via search
                qid = wikidata_search(name)
                time.sleep(0.1)
                
                if qid and qid not in {b["wikidata_id"] for b in brands_list}:
                    brands_list.append({
                        "wikidata_id": qid,
                        "brand_name": name,
                        "category": cat,
                    })
                elif not qid:
                    brands_list.append({
                        "wikidata_id": "",
                        "brand_name": name,
                        "category": cat,
                    })
    
    # Final save
    output = {
        "total": len(brands_list),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "brands": brands_list,
    }
    with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ FINAL: {len(brands_list)} unique brands")
    print(f"{'='*60}")
    
    from collections import Counter
    cats = Counter(b["category"] for b in brands_list)
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")
    
    with_qid_count = sum(1 for b in brands_list if b.get("wikidata_id"))
    print(f"\nWith Wikidata ID: {with_qid_count}/{len(brands_list)}")
    
    # Generate master.csv top 50
    print(f"\n{'='*60}")
    print("Generating master.csv with top 50 brands...")
    print(f"{'='*60}")
    
    # Sort: fashion-luxury first, then by category alphabetically
    cat_priority = {
        "fashion-luxury": 0, "fashion": 1, "watch": 2, "jewelry": 3,
        "beauty": 4, "auto": 5, "tech": 6, "sport": 7, "food": 8, "toy": 9, "other": 10
    }
    
    brands_list.sort(key=lambda b: (cat_priority.get(b["category"], 10), b["brand_name"]))
    
    # Take top brands - include Escher at position 1
    top_50 = []
    top_50.append({
        "brand": "埃舍尔Escher",
        "slug": "escher",
        "country": "中国",
        "industry": "fashion-luxury",
        "status": "done",
    })
    
    # Add remaining 49 from our dataset (skip duplicates of escher)
    slug_set = {"escher"}
    for b in brands_list:
        slug = re.sub(r'[^a-z0-9]+', '-', b["brand_name"].lower()).strip('-')[:30]
        if slug not in slug_set:
            slug_set.add(slug)
            brand_name = b["brand_name"]
            # Determine country
            country = ""
            cat_display = b["category"]
            top_50.append({
                "brand": brand_name,
                "slug": slug,
                "country": country,
                "industry": cat_display,
                "status": "pending",
            })
        if len(top_50) >= 50:
            break
    
    # Write master.csv
    with open("/workspace/pinpai-ai-in/master.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "brand", "slug", "country", "industry", "status"])
        writer.writeheader()
        for idx, b in enumerate(top_50, 1):
            writer.writerow({
                "id": idx,
                "brand": b["brand"],
                "slug": b["slug"],
                "country": b["country"],
                "industry": b["industry"],
                "status": b["status"],
            })
    
    print(f"\n✅ master.csv written with {len(top_50)} brands")
    print("\n--- Top 10 brands ---")
    for b in top_50[:10]:
        print(f"  {b['brand']} [{b['industry']}] → {b['slug']}.json")

if __name__ == "__main__":
    main()
