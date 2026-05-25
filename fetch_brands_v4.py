#!/usr/bin/env python3
"""
品牌种子库 v4 — 从 Wikipedia "List of" 汇总页面批量爬取品牌
利用 Wikipedia 上的已知品牌列表页面（如 List of fashion brands, List of automobile manufacturers 等）
"""
import json, urllib.request, urllib.parse, re, time, sys, os

USER_AGENT = "GlobalBrandIndex/1.0 (brand crawler)"

def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(3)
                continue
            print(f"  Error fetching {url}: {e}", file=sys.stderr)
            return None
    return None

def extract_wikilinks(html):
    """Extract Wikipedia page titles from wikilink patters in HTML"""
    # Match [[Page Title]] or [[Page Title|display text]]
    links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', html)
    return [l.strip() for l in links if l.strip() and ":" not in l and len(l) > 2]

def extract_brands_from_list_page(page_title, category):
    """Fetch a Wikipedia list page and extract brand names"""
    # Wikipedia API: get page content in wikitext
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "wikitext",
        "format": "json",
        "origin": "*",
    }
    url = f"https://en.wikipedia.org/w/api.php?{urllib.parse.urlencode(params)}"
    data = fetch_text(url)
    if not data:
        return []
    
    try:
        parsed = json.loads(data)
        wikitext = parsed.get("parse", {}).get("wikitext", {}).get("*", "")
    except:
        return []
    
    if not wikitext:
        return []
    
    brands = []
    
    # Extract wikilinks from the page
    links = extract_wikilinks(wikitext)
    
    # For list pages, the table rows often contain the brand links
    # Filter out non-brand links (common words, categories, etc.)
    skip_words = {
        "File:", "Image:", "Category:", "Wikipedia:", "Template:", 
        "Help:", "Portal:", "Special:", "Reference", "Notes", "See also",
        "References", "External links", "Footnotes", "Bibliography",
        "Further reading", "List of", "Lists of",
    }
    
    # Also extract from wiki table markup
    # Tables use |- for rows and ! or | for cells
    # Find all [['s that are likely brand names (capitalized, not common words)
    
    skip_titles = {
        "This article", "The following", "There are", "Brand", "Name", 
        "Company", "Industry", "Sector", "Founded", "Country", "Notes",
        "Year", "Parent", "Revenue", "Headquarters", "Products",
        "Ownership", "Status", "Current", "Former", "Type",
        "Logo", "Image", "Picture", "Photo", "Flagicon", "Flag",
        "A", "An", "The", "In", "On", "At", "For", "By", "To",
        "Is", "Are", "Was", "Were", "Has", "Have", "Had",
        "Main article", "Also known as", "Short description",
        "Brands", "Brands listed", "Examples include",
    }
    
    for link in links:
        if any(link.startswith(s) for s in skip_words):
            continue
        if link in skip_titles or len(link) < 3:
            continue
        # Uppercase first letter = proper noun = likely a brand
        if link[0].isupper() and not link[0].isdigit():
            brands.append(link)
    
    return brands

def get_wikidata_id(page_title, lang="en"):
    """Get Wikidata QID for a Wikipedia page title"""
    api = "https://en.wikipedia.org/w/api.php" if lang == "en" else "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": page_title,
        "prop": "pageprops",
        "ppprop": "wikibase_item",
        "format": "json",
        "origin": "*",
    }
    url = f"{api}?{urllib.parse.urlencode(params)}"
    data = fetch_text(url)
    if not data:
        return ""
    try:
        parsed = json.loads(data)
        pages = parsed.get("query", {}).get("pages", {})
        for pid, info in pages.items():
            return info.get("pageprops", {}).get("wikibase_item", "")
    except:
        return ""
    return ""

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower().strip()).strip('-')

def categorize(title, category_hint):
    """Smart categorization based on the source list"""
    return category_hint

LIST_PAGES = [
    # Luxury/Fashion
    ("List of fashion brands", "fashion"),
    ("List of most valuable brands", "other"),
    ("List of oldest companies", "other"),
    ("List of companies of China", "other"),
    ("List of conglomerates", "other"),
    
    # Luxury
    ("List of luxury brands", "fashion-luxury"),
    
    # Auto
    ("List of automobile manufacturers", "auto"),
    ("List of car brands", "auto"),
    ("List of German cars", "auto"),
    
    # Beauty
    ("List of cosmetics brands", "beauty"),
    ("List of perfumes", "beauty"),
    
    # Tech
    ("List of largest technology companies", "tech"),
    ("List of semiconductor companies", "tech"),
    ("List of smartphone manufacturers", "tech"),
    ("List of e-commerce companies", "tech"),
    
    # Sport
    ("List of sportswear brands", "sport"),
    ("List of shoe brands", "sport"),
    
    # Food
    ("List of food companies", "food"),
    ("List of beverage companies", "food"),
    ("List of coffee companies", "food"),
    ("List of fast food restaurants", "food"),
    ("List of soft drink brands", "food"),
    
    # Jewelry/Watch
    ("List of watch brands", "watch"),
    ("List of jewellery brands", "jewelry"),
    
    # Toy
    ("List of toy brands", "toy"),
    
    # More fashion
    ("List of swimwear brands", "fashion"),
    ("List of denim brands", "fashion"),
    ("List of underwear brands", "fashion"),
    ("List of handbag brands", "fashion-luxury"),
    ("List of sneaker brands", "sport"),
]

# Known common non-brand names that show up in list pages
NON_BRANDS = {
    "This", "That", "There", "These", "Those", "They", "Their", "Them",
    "Also", "Very", "Many", "Some", "Each", "Every", "Both", "Other",
    "First", "Second", "Third", "New", "Old", "Big", "Small", "Large",
    "High", "Low", "Best", "Top", "Most", "Least", "Last", "Next",
    "From", "With", "Without", "Within", "Between", "Under", "Over",
    "Before", "After", "During", "Since", "Until", "Upon", "Into",
    "About", "Above", "Across", "Along", "Among", "Around", "Behind",
    "Below", "Beneath", "Beside", "Beyond", "Down", "Inside", "Near",
    "Off", "Outside", "Through", "Throughout", "Toward", "Towards",
    "Up", "Upon", "Via", "While", "Because", "Though", "Although",
    "Even", "Though", "Than", "Then", "Now", "Here", "There", "Where",
    "Who", "Whom", "Whose", "Which", "What", "When", "Why", "How",
    "All", "Any", "Both", "Each", "Few", "More", "Most", "Much",
    "No", "None", "Not", "Only", "Own", "Same", "Several", "Some",
    "Such", "That", "Those", "Very", "Further", "Furthest",
    # Common words in table headers/layout
    "Main", "Major", "Minor", "Total", "Active", "Passive", "General",
    "Specific", "Individual", "Common", "Popular", "Famous", "Notable",
    "Key", "Primary", "Secondary", "Central", "Local", "Global",
    "International", "National", "Regional", "Corporate", "Private",
    "Public", "Limited", "Incorporated", "Company", "Companies",
    "Corporation", "Group", "Holdings", "Limited", "PLC", "ASA",
    "SpA", "GmbH", "AG", "NV", "SA", "Ltd", "Inc", "Corp",
    "Co", "Brand", "Billion", "Million", "Percent", "Year", "Years",
    "Mark", "Product", "Service", "Category", "Categories",
    "Section", "Part", "Chapter", "Page", "Number", "Numbers",
    "Figure", "Table", "Image", "File", "Media", "Source", "Sources",
    "Notes", "Note", "See", "References", "Reference",
    "External", "Links", "Link", "Further", "Reading",
    "Also", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "1st", "2nd", "3rd", "4th",
    "Former", "Current", "Previous", "Next", "Last",
    "Built", "Founded", "Established", "Created", "Started",
    "Began", "Opened", "Closed", "Ended", "Defunct", "Active",
    "Inactive", "Operating", "Operated",
    "He", "She", "It", "We", "They", "You",
    "US", "UK", "EU", "China", "Japan", "Germany", "France",
    "Italy", "Spain", "UK", "USA", "Canada", "Australia",
    "United States", "United Kingdom", "World", "Global",
    "America", "Americas", "Asia", "Europe", "Africa",
    "Nike", "Inc", "Group",  # specific false positives
}

def main():
    all_brands = {}  # QID -> brand info
    brand_name_to_qid = {}
    
    # First, load existing brands from v3
    if os.path.exists("/workspace/pinpai-ai-in/brand_seed_raw.json"):
        with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "r") as f:
            existing = json.load(f)
        for b in existing.get("brands", []):
            qid = b.get("wikidata_id", "")
            if qid:
                all_brands[qid] = b
                bn = b.get("brand_name", "").lower()
                brand_name_to_qid[bn] = qid
        print(f"Loaded {len(all_brands)} existing brands")
    
    # Fetch list pages
    total_pages = len(LIST_PAGES)
    for idx, (page, category) in enumerate(LIST_PAGES, 1):
        print(f"\n[{idx}/{total_pages}] {page} → {category}")
        brands = extract_brands_from_list_page(page, category)
        
        if not brands:
            print(f"  → Failed to fetch or empty")
            continue
        
        # Filter known non-brands
        brands = [b for b in brands if b not in NON_BRANDS and len(b) > 2]
        
        print(f"  → Found {len(brands)} potential brands")
        
        new_count = 0
        for b in brands[:100]:  # limit per page
            # Check if we already have this brand
            bl = b.lower()
            if bl in brand_name_to_qid:
                continue
            
            # Check if very similar to an existing brand
            # (skip for now, dedup later)
            
            # Get Wikidata QID
            qid = get_wikidata_id(b, "en")
            if not qid:
                # Try Chinese
                qid = get_wikidata_id(b, "zh")
            
            if qid:
                brand_name_to_qid[bl] = qid
                if qid not in all_brands:
                    all_brands[qid] = {
                        "wikidata_id": qid,
                        "brand_name": b,
                        "category": category,
                    }
                    new_count += 1
            else:
                # Store without QID
                all_brands[f"noqid:{b}"] = {
                    "wikidata_id": "",
                    "brand_name": b,
                    "category": category,
                }
                new_count += 1
            
            time.sleep(0.2)  # rate limit
        
        print(f"  → New unique: {new_count}, total: {len(all_brands)}")
        
        # Save incrementally every 3 pages
        if idx % 3 == 0:
            output = {
                "total": len(all_brands),
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "brands": list(all_brands.values()),
            }
            with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"  💾 Saved checkpoint ({len(all_brands)} brands)")
    
    # Final save
    output = {
        "total": len(all_brands),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "brands": list(all_brands.values()),
    }
    with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ FINAL: {len(all_brands)} unique brands")
    print(f"{'='*60}")
    
    # Counts
    from collections import Counter
    cats = Counter(b["category"] for b in output["brands"])
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")
    
    with_qid = sum(1 for b in output["brands"] if b.get("wikidata_id"))
    print(f"\nWith Wikidata ID: {with_qid}/{len(output['brands'])}")

if __name__ == "__main__":
    main()
