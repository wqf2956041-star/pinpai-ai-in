#!/usr/bin/env python3
"""
auto_source_brands.py — Autonomous brand sourcing engine.
Runs every cycle, finds new brands from Wikipedia categories,
refills the pool so heartbeat never runs dry.
No user interaction needed. No LLM calls.
"""
import json, os, csv, sys, re, time, urllib.request, urllib.error, urllib.parse

BASE = "/workspace/pinpai-ai-in"
POOL_FILE = os.path.join(BASE, ".next_batch.json")
LOCK_FILE = os.path.join(BASE, ".sourcing.lock")
DONE_FILE = os.path.join(BASE, ".sourced_slugs.json")

# Lock to prevent concurrent runs
if os.path.exists(LOCK_FILE):
    import time as t
    if t.time() - os.path.getmtime(LOCK_FILE) < 600:
        print("LOCKED")
        sys.exit(0)
    os.remove(LOCK_FILE)
open(LOCK_FILE, "w").close()

try:
    # Load existing brands
    with open(os.path.join(BASE, "brands_index.json")) as f:
        index = json.load(f)
    existing_slugs = set(b['slug'] for b in index)

    # Load previously sourced slugs (to avoid re-sourcing)
    if os.path.exists(DONE_FILE):
        sourced_slugs = set(json.load(open(DONE_FILE)))
    else:
        sourced_slugs = set()

    # Load current pool
    current_pool = []
    if os.path.exists(POOL_FILE):
        current_pool = json.load(open(POOL_FILE))

    pool_slugs = set(b['slug'] for b in current_pool)

    # If pool has at least 5 remaining, skip sourcing
    if len(current_pool) >= 5:
        print(f"Pool ok ({len(current_pool)} remaining)")
        os.remove(LOCK_FILE)
        sys.exit(0)

    print(f"Pool low ({len(current_pool)}). Finding more brands...")

    # Wikipedia categories to source from (diverse industries)
    WIKI_CATEGORIES = [
        # Each entry: (category_url, category_type, name_prefix_filter)
        # Format: https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:...
        ("Category:Multinational_companies_headquartered_in_the_United_States", "general"),
        ("Category:Japanese_brands", "general"),
        ("Category:German_brands", "general"),
        ("Category:French_brands", "general"),
        ("Category:British_brands", "general"),
        ("Category:South_Korean_brands", "general"),
        ("Category:Italian_brands", "general"),
        ("Category:Swiss_brands", "general"),
        ("Category:Chinese_brands", "general"),
        ("Category:Luxury_brands", "fashion-luxury"),
        ("Category:Clothing_brands", "fashion"),
        ("Category:Shoe_brands", "fashion"),
        ("Category:Electronics_companies", "technology"),
        ("Category:Software_companies", "technology"),
        ("Category:Food_and_drink_brands", "food"),
        ("Category:Beer_brands", "beverage"),
        ("Category:Hotel_chains", "hotel"),
        ("Category:Airlines", "airline"),
        ("Category:Automotive_companies", "automotive"),
        ("Category:Retail_companies", "retail"),
        ("Category:Pharmaceutical_companies", "healthcare"),
        ("Category:Medical_device_companies", "healthcare"),
        ("Category:Mass_media_companies", "media"),
        ("Category:Telecommunications_companies", "telecom"),
        ("Category:Financial_services_companies", "finance"),
        ("Category:Insurance_companies", "finance"),
        ("Category:Cosmetics_companies", "cosmetics"),
        ("Category:Sportswear_brands", "sportswear"),
        ("Category:Toy_brands", "toy"),
        ("Category:Video_game_companies", "technology"),
        ("Category:Petroleum_companies", "energy"),
        ("Category:Mining_companies", "energy"),
        ("Category:Restaurant_chains", "food"),
        ("Category:Coffee_brands", "food"),
        ("Category:Confectionery_companies", "food"),
    ]

    # Shuffle categories each run for variety
    random = __import__('random')
    random.shuffle(WIKI_CATEGORIES)

    def slugify(name):
        slug = name.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        return slug

    new_brands = []
    attempted = set()

    for cat_title, cat_type in WIKI_CATEGORIES:
        if len(new_brands) >= 20:
            break

        # Clean category title for API
        params = urllib.parse.urlencode({
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": cat_title,
            "cmlimit": "max",
            "cmtype": "page"
        })
        url = f"https://en.wikipedia.org/w/api.php?{params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BrandBot/1.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())

            pages = data.get("query", {}).get("categorymembers", [])
            for page in pages:
                if len(new_brands) >= 20:
                    break
                title = page.get("title", "")
                ns = page.get("ns", 0)

                # Skip non-article pages, already processed, in pool, or already deployed
                if ns != 0:
                    continue

                slug = slugify(title)
                if not slug or len(slug) < 2:
                    continue
                if slug in existing_slugs or slug in pool_slugs or slug in sourced_slugs or slug in attempted:
                    continue
                attempted.add(slug)

                # Skip common non-brand articles
                skip_patterns = [
                    r'(^List of|^Category:|^Template:|^Wikipedia:|^File:|^Portal:|^Draft:)',
                    r'\(disambiguation\)$', r'^Timeline', r'^History of',
                    r'^Comparison', r'^Outline of', r'^Glossary',
                ]
                if any(re.match(p, title) for p in skip_patterns):
                    continue

                # Skip country/region pages that aren't brands
                if title.endswith((" (company)", " Inc.", " LLC", " Ltd.", " plc", " Corporation", " Group", " & Co.")):
                    pass  # These are likely companies
                elif title.endswith((" (brand)", " (store)", " (restaurant)")):
                    pass  # These are brands
                elif any(kw in title.lower() for kw in ["company", "corporation", "ltd", "inc", "llc", "bancorp", "holdings", "enterprises"]):
                    pass  # Likely a company
                else:
                    # Check if title is short enough to be a brand name
                    if len(title) > 30:
                        continue

                # Build brand entry
                new_entry = {
                    "slug": slug,
                    "name": title,
                    "name_en": title,
                    "category": cat_type,
                    "country": "Unknown",
                    "founding_year": 0,
                    "founding_location": "",
                    "founder": "",
                    "website": "",
                    "main_business": [],
                    "slogan": f"{title} — Global brand"
                }
                new_brands.append(new_entry)
                print(f"  + {slug} ({title}) [{cat_type}]")

        except Exception as e:
            print(f"  ⚠ {cat_title}: {e}")
            time.sleep(1)
            continue

    if not new_brands:
        print("No new brands found this cycle.")
        # Still mark as done so we don't retry same slugs
        all_sourced = sourced_slugs | attempted
        json.dump(list(all_sourced), open(DONE_FILE, "w"))
        os.remove(LOCK_FILE)
        sys.exit(0)

    # Merge with existing pool
    current_pool.extend(new_brands)
    json.dump(current_pool, open(POOL_FILE, "w"), ensure_ascii=False, indent=2)

    # Save sourced slugs
    all_sourced = sourced_slugs | attempted
    json.dump(list(all_sourced), open(DONE_FILE, "w"))

    print(f"\n✅ Sourced {len(new_brands)} new brands (pool: {len(current_pool)})")

finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
