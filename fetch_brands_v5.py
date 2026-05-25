#!/usr/bin/env python3
"""
品牌种子库 v5 — 直接整理全球知名品牌列表
基于已知的全球品牌榜单 + 用 Wikipedia API 单页查询获取 Wikidata QID
"""
import json, urllib.request, urllib.parse, time, re, sys, os

USER_AGENT = "GlobalBrandIndex/1.0"

# ===== 全球知名品牌整理 =====
# 来源：Interbrand Best Global Brands, Forbes Global 2000, 
#       各品类头部品牌

BRANDS_BY_CATEGORY = {
    "fashion-luxury": [
        "Louis Vuitton", "Hermès", "Gucci", "Chanel", "Christian Dior",
        "Cartier", "Prada", "Burberry", "Versace", "Fendi",
        "Givenchy", "Yves Saint Laurent", "Valentino", "Balenciaga",
        "Bottega Veneta", "Giorgio Armani", "Dolce & Gabbana",
        "Ralph Lauren", "Celine", "Chloé", "Loewe", "Miu Miu",
        "Alexander McQueen", "Maison Margiela", "Bally",
        "Salvatore Ferragamo", "Tod's", "Jimmy Choo",
        "Christian Louboutin", "Tiffany & Co.", "Bulgari",
        "Van Cleef & Arpels", "Piaget", "Boucheron", "Chopard",
        "Graff Diamonds", "Harry Winston", "Damiani", "Pomellato",
        "Ermenegildo Zegna", "Brunello Cucinelli", "Loro Piana",
        "Moncler", "Stone Island", "Acne Studios", "Isabel Marant",
        "Marni", "Etro", "Missoni", "Kenzo",
    ],
    "watch": [
        "Rolex", "Patek Philippe", "Audemars Piguet", "Vacheron Constantin",
        "Omega", "Cartier", "IWC Schaffhausen", "Jaeger-LeCoultre",
        "Longines", "Tissot", "Breitling", "Tag Heuer", "Hublot",
        "Richard Mille", "Panerai", "A. Lange & Söhne", "Blancpain",
        "Breguet", "Zenith", "Seiko", "Citizen", "Casio",
        "Swatch", "Rado", "Oris", "Nomos Glashütte", "Baume & Mercier",
        "Movado", "Fossil", "Timex",
    ],
    "fashion": [
        "Zara", "H&M", "Uniqlo", "Mango", "Levi's", "Calvin Klein",
        "Tommy Hilfiger", "Coach", "Michael Kors", "Kate Spade",
        "Longchamp", "Stella McCartney", "Marc Jacobs", "Diesel",
        "Benetton", "Superdry", "Jack & Jones", "Vero Moda",
        "Only", "Sandro", "Maje", "The Kooples", "Comme des Garçons",
        "Yohji Yamamoto", "Issey Miyake", "Rei Kawakubo",
        "Off-White", "Fear of God", "Essentials", "Palm Angels",
        "Ami Paris", "Polo Ralph Lauren", "Tom Ford",
        "Hugo Boss", "Lacoste", "Fred Perry", "Ben Sherman",
        "Carhartt", "Dickies", "Patagonia", "Arc'teryx",
        "The North Face", "Columbia", "Helly Hansen",
        "Birkenstock", "Dr. Martens", "Clarks", "ECCO",
        "Geox", "Skechers", "Crocs", "UGG",
        "Victoria's Secret", "Hanes", "Fruit of the Loom",
        "Lululemon", "Athleta", "Sweaty Betty", "Alo Yoga",
    ],
    "sport": [
        "Nike", "Adidas", "Puma", "Under Armour", "New Balance",
        "Asics", "Reebok", "Converse", "Vans", "Fila",
        "Mizuno", "Lotto", "Kappa", "Umbro", "Diadora",
        "Brooks", "Hoka One One", "Salomon", "Merrell",
        "Wilson", "Spalding", "Rawlings",
        "Speedo", "Arena", "TYR Sport",
        "Callaway", "Titleist", "TaylorMade",
        "Yonex", "Dunlop Sport", "Head",
        "Decathlon", "Intersport", "Sports Direct",
        "Wilson", "Amer Sports", "Anta", "Li-Ning",
        "Peak Sport", "Xtep", "361°", "Erke",
    ],
    "auto": [
        "Toyota", "Volkswagen", "Mercedes-Benz", "BMW", "Honda",
        "Ford", "General Motors", "Hyundai", "Kia", "Tesla",
        "Ferrari", "Lamborghini", "Porsche", "Aston Martin",
        "Bentley", "Rolls-Royce", "Maserati", "McLaren",
        "Bugatti", "Koenigsegg", "Pagani", "Rimac",
        "Jaguar", "Land Rover", "Volvo", "Audi", "Lexus",
        "Cadillac", "Lincoln", "Chrysler", "Dodge", "Jeep",
        "Ram Trucks", "GMC", "Buick", "Chevrolet",
        "Nissan", "Infiniti", "Mitsubishi", "Subaru", "Mazda",
        "Suzuki", "Daihatsu", "Isuzu",
        "BYD", "NIO", "XPeng", "Li Auto", "Zeekr",
        "Great Wall", "Chery", "Geely", "SAIC", "Changan",
        "MG Motor", "Polestar", "Lucid", "Rivian", "Fisker",
        "Skoda", "Seat", "Cupra", "Dacia", "Alfa Romeo",
        "Fiat", "Peugeot", "Citroën", "Renault", "Opel",
        "Vauxhall", "Mini", "Smart",
    ],
    "beauty": [
        "L'Oréal", "Estée Lauder", "Shiseido", "Lancôme", "Clinique",
        "MAC", "Bobbi Brown", "NARS", "Charlotte Tilbury",
        "Tom Ford Beauty", "Gucci Beauty", "Dior Beauty",
        "Yves Saint Laurent Beauté", "Armani Beauty",
        "Kiehl's", "La Mer", "La Prairie", "SK-II",
        "Sulwhasoo", "Amorepacific", "Innisfree", "Etude House",
        "Laneige", "Clio", "Cosrx", "Innisfree",
        "Maybelline", "CoverGirl", "Revlon", "Avon",
        "Mary Kay", "Burt's Bees", "Neutrogena", "Olay",
        "Cetaphil", "CeraVe", "La Roche-Posay", "Vichy",
        "Avene", "Bioderma", "Eucerin", "Nivea",
        "The Body Shop", "Lush", "Aesop", "Grown Alchemist",
        "SkinCeuticals", "Drunk Elephant", "The Ordinary",
        "Paula's Choice", "Caudalie", "Clarins", "Biotherm",
        "Sisley", "Decleor", "Payot",
        "Jo Malone", "Creed", "Byredo", "Diptyque",
        "Acqua di Parma", "Penhaligon's", "Floris",
        "Tom Ford", "Le Labo", "Maison Francis Kurkdjian",
        "Juicy Couture", "Paco Rabanne", "Carolina Herrera",
        "Viktor & Rolf", "Jean Paul Gaultier", "Lalique",
    ],
    "tech": [
        "Apple", "Microsoft", "Google", "Amazon", "Meta",
        "Tencent", "Alibaba", "Samsung", "Sony", "Intel",
        "NVIDIA", "AMD", "Qualcomm", "TSMC", "ASML",
        "IBM", "Oracle", "Cisco", "HPE", "Dell",
        "Siemens", "SAP", "Salesforce", "Adobe", "VMware",
        "Xiaomi", "Huawei", "DJI", "Meituan",
        "ByteDance", "Baidu", "NetEase", "JD.com", "Pinduoduo",
        "Tesla", "SpaceX", "OpenAI", "DeepMind",
        "Spotify", "Netflix", "Uber", "Airbnb",
        "Shopify", "Palantir", "Snowflake", "Datadog",
        "Google Cloud", "AWS", "Azure", "Cloudflare",
        "Zoom", "Slack", "Atlassian", "GitHub",
        "Unity", "Epic Games", "Roblox", "Riot Games",
        "Electronic Arts", "Activision", "Nintendo",
        "Discord", "Reddit", "Twitter", "LinkedIn",
        "PayPal", "Stripe", "Square", "Block",
        "Coinbase", "Binance", "Ripple", "Chainlink",
        "ASUS", "Acer", "LG", "Panasonic", "Toshiba",
        "HP Inc", "Lenovo", "Razer", "Logitech",
    ],
    "food": [
        "Coca-Cola", "Pepsi", "Nestlé", "McDonald's", "Starbucks",
        "KFC", "Burger King", "Subway", "Domino's", "Pizza Hut",
        "Heineken", "Anheuser-Busch", "Budweiser", "Corona",
        "Guinness", "Carlsberg", "Asahi", "Kirin",
        "Coca-Cola", "Sprite", "Fanta", "Dr Pepper",
        "Red Bull", "Monster", "Gatorade", "Powerade",
        "Lipton", "Nescafé", "Folgers", "Starbucks",
        "Lay's", "Doritos", "Cheetos", "Pringles",
        "M&M's", "Snickers", "Kit Kat", "Twix", "Mars",
        "Hershey's", "Cadbury", "Ferrero Rocher",
        "Kraft Heinz", "Unilever", "Danone",
        "Kellogg's", "General Mills", "Nissin",
        "Tyson Foods", "Cargill", "ADM",
        "Walmart", "Costco", "Target", "Carrefour",
        "Tesco", "Aldi", "Lidl", "7-Eleven",
        "Yum! Brands", "Restaurant Brands International",
        "Chipotle", "Wendy's", "Papa John's",
        "Dunkin'", "Panera Bread", "Costa Coffee",
        "Lavazza", "Illy", "Nespresso", "Keurig",
    ],
    "jewelry": [
        "Tiffany & Co.", "Cartier", "Bulgari", "Van Cleef & Arpels",
        "Boucheron", "Chopard", "Graff", "Harry Winston",
        "Piaget", "Damiani", "Pomellato", "Mikimoto",
        "Tasaki", "Swarovski", "Pandora", "Links of London",
        "David Yurman", "John Hardy", "Tous",
        "Mellerio", "Chaumet", "Fred",
        "Poiray", "Mauboussin", "Dinh Van",
        "Roberto Coin", "Pasquale Bruni", "Marco Bicego",
        "Qeelin", "Lukfook", "Chow Tai Fook",
        "Chow Sang Sang", "Lao Feng Xiang", "Zhou Dafu",
    ],
    "toy": [
        "LEGO", "Mattel", "Hasbro", "Bandai Namco", "Takara Tomy",
        "MGA Entertainment", "Spin Master", "JAKKS Pacific",
        "Playmobil", "Ravensburger", "Fisher-Price",
        "Hot Wheels", "Barbie", "G.I. Joe", "Transformers",
        "Monopoly", "Nerf", "Play-Doh", "My Little Pony",
        "Pokémon", "Sanrio", "Disney",
        "Minecraft", "Funko", "Calico Critters",
        "Sylvanian Families", "Brio", "PlanToys",
        "Melissa & Doug", "Hape", "Vtech", "LeapFrog",
        "Moose Toys", "Zuru", "Battat",
    ],
}

def get_wikidata_id(title, lang="en"):
    api = "https://en.wikipedia.org/w/api.php" if lang == "en" else "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "pageprops",
        "ppprop": "wikibase_item",
        "format": "json",
        "origin": "*",
    }
    url = f"{api}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                pages = data.get("query", {}).get("pages", {})
                for pid, info in pages.items():
                    return info.get("pageprops", {}).get("wikibase_item", "")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(2)
                continue
            return ""
        except:
            return ""
    return ""

def main():
    all_brands = []
    seen_qids = set()
    seen_names = set()
    
    # Flatten brand list
    brand_entries = []
    for cat, brands in BRANDS_BY_CATEGORY.items():
        for name in brands:
            if name.lower() not in seen_names:
                seen_names.add(name.lower())
                brand_entries.append((name, cat))
    
    print(f"Total brands to process: {len(brand_entries)}")
    
    # Resolve Wikidata IDs in batch of 50
    all_titles = [b[0] for b in brand_entries]
    
    print("\nResolving Wikidata IDs from English Wikipedia...")
    resolved = 0
    for i in range(0, len(all_titles), 50):
        batch = all_titles[i:i+50]
        params = {
            "action": "query",
            "titles": "|".join(batch),
            "prop": "pageprops",
            "ppprop": "wikibase_item",
            "format": "json",
            "origin": "*",
        }
        url = f"https://en.wikipedia.org/w/api.php?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                pages = data.get("query", {}).get("pages", {})
                for pid, info in pages.items():
                    title = info.get("title", "")
                    qid = info.get("pageprops", {}).get("wikibase_item", "")
                    if qid and qid not in seen_qids:
                        seen_qids.add(qid)
                        cat = "other"
                        for name, c in brand_entries:
                            if name.lower() == title.lower():
                                cat = c
                                break
                        all_brands.append({
                            "wikidata_id": qid,
                            "brand_name": title,
                            "category": cat,
                        })
                        resolved += 1
        except Exception as e:
            print(f"  Batch error: {e}", file=sys.stderr)
        time.sleep(0.5)
        print(f"  Batch {i//50+1}/{(len(all_titles)-1)//50+1}: {resolved} resolved", flush=True)
    
    # For unresolved, do individual API calls with Wikidata search
    resolved_names = {b["brand_name"].lower(): b for b in all_brands}
    unresolved = [(name, cat) for name, cat in brand_entries 
                  if name.lower() not in resolved_names]
    
    if unresolved:
        print(f"\nResolving {len(unresolved)} unresolved brands...")
        for name, cat in unresolved:
            qid = get_wikidata_id(name, "en")
            if not qid:
                qid = get_wikidata_id(name.replace(" ", "_"), "en")
            if qid and qid not in seen_qids:
                seen_qids.add(qid)
                all_brands.append({
                    "wikidata_id": qid,
                    "brand_name": name,
                    "category": cat,
                })
                resolved += 1
            elif not qid:
                # Store without QID
                all_brands.append({
                    "wikidata_id": "",
                    "brand_name": name,
                    "category": cat,
                })
            time.sleep(0.3)
    
    # Save
    output = {
        "total": len(all_brands),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "brands": all_brands,
    }
    with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ FINAL: {len(all_brands)} unique brands")
    print(f"{'='*60}")
    
    from collections import Counter
    cats = Counter(b["category"] for b in all_brands)
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")
    
    with_qid = sum(1 for b in all_brands if b.get("wikidata_id"))
    print(f"\nWith Wikidata ID: {with_qid}/{len(all_brands)}")

if __name__ == "__main__":
    main()
