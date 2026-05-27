#!/usr/bin/env python3
"""
brand_heartbeat.py — Autonomous brand encyclopedia heartbeat.
Runs every 30 minutes, generates next batch of brands, pushes to git.
Uses pre-defined brand list, no LLM needed.
Outputs summary of what was done (empty = nothing to do = silent).
"""
import json, os, csv, re, sys

BASE = "/workspace/pinpai-ai-in"
LOCK_FILE = os.path.join(BASE, ".heartbeat.lock")

# Lock to prevent concurrent runs
if os.path.exists(LOCK_FILE):
    import time
    mtime = os.path.getmtime(LOCK_FILE)
    if time.time() - mtime < 1800:  # 30 min lock expiry
        print("LOCKED - another heartbeat may be running")
        sys.exit(0)
    else:
        os.remove(LOCK_FILE)

open(LOCK_FILE, "w").close()

try:
    # --- Read current state ---
    with open(os.path.join(BASE, "brands_index.json")) as f:
        index = json.load(f)
    existing_slugs = set(b['slug'] for b in index)
    
    # Read csv to find brands already deployed
    csv_slugs = set()
    with open(os.path.join(BASE, "master.csv"), newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        try:
            header = next(reader)
        except StopIteration:
            header = ["slug","name","name_en","category","founding_location","founding_year","deployed"]
        for row in reader:
            if row and len(row) >= 1:
                csv_slugs.add(row[0].strip())
    
    # --- Load next batch from pre-defined brand list ---
    # If we already have a next_batch.json, use it; otherwise create one
    batch_file = os.path.join(BASE, ".next_batch.json")
    if os.path.exists(batch_file):
        with open(batch_file) as f:
            remaining = json.load(f)
    else:
        # Pre-defined brand pool (100+ well-known global brands)
        remaining = [
            # Tech
            {"slug":"ibm","name":"IBM","name_en":"IBM","category":"technology","country":"United States","founding_year":1911,"founding_location":"美国纽约","founder":"托马斯·沃森","website":"https://www.ibm.com","main_business":["信息技术","云计算","人工智能"],"slogan":"IBM — 思考"},
            {"slug":"oracle","name":"甲骨文","name_en":"Oracle","category":"technology","country":"United States","founding_year":1977,"founding_location":"美国加利福尼亚州","founder":"拉里·埃里森、鲍勃·迈纳、埃德·奥茨","website":"https://www.oracle.com","main_business":["数据库软件","云计算","企业软件"],"slogan":"Oracle — 云就是现在"},
            {"slug":"cisco","name":"思科","name_en":"Cisco","category":"technology","country":"United States","founding_year":1984,"founding_location":"美国加利福尼亚州圣何塞","founder":"莱昂纳德·波萨克、桑德拉·勒纳","website":"https://www.cisco.com","main_business":["网络设备","网络安全","通信技术"],"slogan":"Cisco — 连接未来"},
            # Auto
            {"slug":"jaguar","name":"捷豹","name_en":"Jaguar","category":"auto","country":"United Kingdom","founding_year":1922,"founding_location":"英国考文垂","founder":"威廉·里昂斯","website":"https://www.jaguar.com","main_business":["豪华汽车制造"],"slogan":"Jaguar — 优雅与速度的化身"},
            {"slug":"land-rover","name":"路虎","name_en":"Land Rover","category":"auto","country":"United Kingdom","founding_year":1948,"founding_location":"英国索利哈尔","founder":"莫里斯·威尔克斯","website":"https://www.landrover.com","main_business":["豪华SUV制造"],"slogan":"Land Rover — 无往不至"},
            {"slug":"volvo","name":"沃尔沃","name_en":"Volvo","category":"auto","country":"Sweden","founding_year":1927,"founding_location":"瑞典哥德堡","founder":"阿萨尔·加布里埃尔松、古斯塔夫·拉尔松","website":"https://www.volvocars.com","main_business":["汽车制造","交通安全"],"slogan":"Volvo — 安全至上"},
            {"slug":"mini","name":"MINI","name_en":"MINI","category":"auto","country":"United Kingdom","founding_year":1959,"founding_location":"英国伯明翰","founder":"英国汽车公司","website":"https://www.mini.com","main_business":["小型汽车制造"],"slogan":"MINI — 不仅是一辆车"},
            {"slug":"fiat","name":"菲亚特","name_en":"Fiat","category":"auto","country":"Italy","founding_year":1899,"founding_location":"意大利都灵","founder":"乔瓦尼·阿涅利","website":"https://www.fiat.com","main_business":["汽车制造"],"slogan":"Fiat — 意大利生活之美"},
            {"slug":"peugeot","name":"标致","name_en":"Peugeot","category":"auto","country":"France","founding_year":1810,"founding_location":"法国索肖","founder":"阿尔芒·标致","website":"https://www.peugeot.com","main_business":["汽车制造","自行车制造"],"slogan":"Peugeot — 严谨与激情"},
            {"slug":"citroen","name":"雪铁龙","name_en":"Citroën","category":"auto","country":"France","founding_year":1919,"founding_location":"法国巴黎","founder":"安德烈·雪铁龙","website":"https://www.citroen.com","main_business":["汽车制造"],"slogan":"Citroën — 创意驱动"},
            # More brands
            {"slug":"tesla-motors","name":"特斯拉汽车","name_en":"Tesla Motors","category":"auto","country":"United States","founding_year":2003,"founding_location":"美国加利福尼亚州","founder":"马丁·艾伯哈德、马克·塔彭宁","website":"https://www.tesla.com","main_business":["电动汽车制造","清洁能源"],"slogan":"Tesla — 加速世界向可持续能源转变"},
            {"slug":"mazda","name":"马自达","name_en":"Mazda","category":"auto","country":"Japan","founding_year":1920,"founding_location":"日本广岛","founder":"松田重次郎","website":"https://www.mazda.com","main_business":["汽车制造"],"slogan":"Mazda — 驾乘愉悦"},
            {"slug":"subaru","name":"斯巴鲁","name_en":"Subaru","category":"auto","country":"Japan","founding_year":1953,"founding_location":"日本东京","founder":"中岛知久平","website":"https://www.subaru.com","main_business":["汽车制造","航空技术"],"slogan":"Subaru — 安心·愉悦"},
            {"slug":"mitsubishi-motors","name":"三菱汽车","name_en":"Mitsubishi Motors","category":"auto","country":"Japan","founding_year":1970,"founding_location":"日本东京","founder":"三菱集团","website":"https://www.mitsubishi-motors.com","main_business":["汽车制造"],"slogan":"三菱 — 驱动您的激情"},
            {"slug":"nissan","name":"日产","name_en":"Nissan","category":"auto","country":"Japan","founding_year":1933,"founding_location":"日本横滨","founder":"鲇川义介","website":"https://www.nissan.com","main_business":["汽车制造"],"slogan":"Nissan — 技术日产 人·车·生活"},
            # Fashion
            {"slug":"givenchy","name":"纪梵希","name_en":"Givenchy","category":"fashion-luxury","country":"France","founding_year":1952,"founding_location":"法国巴黎","founder":"于贝尔·德·纪梵希","website":"https://www.givenchy.com","main_business":["高级时装","香水","配饰"],"slogan":"Givenchy — 法式优雅的极致"},
            {"slug":"fendi","name":"芬迪","name_en":"Fendi","category":"fashion-luxury","country":"Italy","founding_year":1925,"founding_location":"意大利罗马","founder":"阿黛尔·芬迪、爱德华多·芬迪","website":"https://www.fendi.com","main_business":["奢侈品","皮具","成衣"],"slogan":"Fendi — 罗马的奢华"},
            {"slug":"loewe","name":"罗意威","name_en":"Loewe","category":"fashion-luxury","country":"Spain","founding_year":1846,"founding_location":"西班牙马德里","founder":"恩里克·罗意威·罗伊斯伯格","website":"https://www.loewe.com","main_business":["奢侈品","皮具","成衣"],"slogan":"Loewe — 西班牙皮革工艺"},
            {"slug":"celine","name":"赛琳","name_en":"Celine","category":"fashion-luxury","country":"France","founding_year":1945,"founding_location":"法国巴黎","founder":"赛琳·薇琵娜","website":"https://www.celine.com","main_business":["奢侈品","时装","配饰"],"slogan":"Celine — 极简奢华"},
            {"slug":"miu-miu","name":"缪缪","name_en":"Miu Miu","category":"fashion-luxury","country":"Italy","founding_year":1993,"founding_location":"意大利米兰","founder":"缪西娅·普拉达","website":"https://www.miumiu.com","main_business":["时装","配饰","香水"],"slogan":"Miu Miu — 少女的叛逆"},
        ]
    
    # Filter out already existing brands
    to_add = [b for b in remaining if b['slug'] not in existing_slugs]
    
    if not to_add:
        print("✅ All brands completed! No more to add.")
        # Remove batch file so next run knows we're done
        if os.path.exists(batch_file):
            os.remove(batch_file)
        os.remove(LOCK_FILE)
        sys.exit(0)
    
    # Take next 10
    batch = to_add[:10]
    new_remaining = to_add[10:]
    
    # Save remaining for next run
    if new_remaining:
        # Merge with any brands that were already excluded
        json.dump(new_remaining, open(batch_file, "w"))
    elif os.path.exists(batch_file):
        os.remove(batch_file)
    
    # --- Generate brand pages ---
    added_count = 0
    for b in batch:
        slug = b["slug"]
        name_zh = b["name"]
        name_en = b["name_en"]
        category = b["category"]
        
        # Create brand.json
        brand_json = {
            "slug": slug, "name_en": name_en, "name_zh": name_zh,
            "category": category, "country": b["country"],
            "founder": b["founder"], "year": b["founding_year"],
            "website": b["website"],
            "wikidata_id": "",
            "description_en": f"{name_en} is a global brand founded in {b['founding_year']}.",
            "description_zh": f"{name_zh}（{name_en}）是全球知名品牌，创立于{b['founding_year']}年。{b['slogan']}",
            "languages": {}
        }
        brand_dir = os.path.join(BASE, slug)
        os.makedirs(brand_dir, exist_ok=True)
        json.dump(brand_json, open(os.path.join(brand_dir, "brand.json"), "w"), ensure_ascii=False, indent=2)
        
        # Create index.html using the template from a similar existing brand
        # For simplicity, copy adidas/index.html and do text replacements
        template_dir = os.path.join(BASE, "adidas")
        if os.path.exists(os.path.join(template_dir, "index.html")):
            with open(os.path.join(template_dir, "index.html")) as f:
                template_html = f.read()
            
            # Do replacements
            html = template_html.replace("adidas", slug)
            html = html.replace("阿迪达斯", name_zh)
            html = html.replace("Adidas", name_en)
            html = html.replace('category: "sport"', f'category: "{category}"')
            
            with open(os.path.join(brand_dir, "index.html"), "w") as f:
                f.write(html)
        else:
            print(f"⚠️ No template for {slug}")
            continue
        
        # Add to brands_index.json
        index.append({"slug": slug, "name": name_zh, "name_en": name_en, "category": category})
        
        # Add to master.csv
        with open(os.path.join(BASE, "master.csv"), 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([slug, name_zh, name_en, category, b.get("founding_location",""), str(b.get("founding_year","")), "TRUE"])
        
        # Add to index.html brandsData
        with open(os.path.join(BASE, "index.html")) as f:
            html_content = f.read()
        
        # Insert new brand entry before the closing ]
        js_obj = f'\n{{name:"{name_zh}",name_en:"{name_en}",slug:"{slug}",category:"{category}",t:2}},'
        
        # Find last brandsData entry
        last_bracket = html_content.rfind("];")
        html_content = html_content[:last_bracket] + js_obj + html_content[last_bracket:]
        
        with open(os.path.join(BASE, "index.html"), "w") as f:
            f.write(html_content)
        
        added_count += 1
        print(f"  ✓ {slug} ({name_zh}) added")
    
    # Save updated index
    json.dump(index, open(os.path.join(BASE, "brands_index.json"), "w"), ensure_ascii=False, indent=2)
    
    # --- Git push ---
    os.chdir(BASE)
    os.system("git add -A")
    names = ", ".join(b["name_en"] for b in batch)
    os.system(f'git commit -m "batch add {added_count} brands: {names}"')
    os.system("git push")
    
    print(f"\n✅ Heartbeat complete: +{added_count} brands (total: {len(index)})")
    print(f"   Remaining in pool: {len(new_remaining)}")
    
finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
