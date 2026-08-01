#!/usr/bin/env python3
"""
修复 master.csv: 清理slug、补充品类多样性、补充国家信息
"""
import csv, re, json, urllib.request, urllib.parse, time, sys, os

USER_AGENT = "GlobalBrandIndex/1.0"

def slugify(name):
    """Convert brand name to clean URL-safe slug (preserve unicode characters)"""
    # Keep Latin chars with diacritics + CJK
    slug = name.strip()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[&,+()/.]', '-', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    # Remove any remaining non-alphanumeric (but keep unicode)
    slug = re.sub(r'[^\w\s\-æøåéèêëàâäùûüôöîïçñß]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.lower().strip('-')
    return slug[:40]

def wikidata_get_label(qid):
    """Get label from Wikidata by QID"""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels",
        "languages": "zh,en",
        "format": "json",
        "origin": "*",
    }
    url = f"https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            entity = data.get("entities", {}).get(qid, {})
            labels = entity.get("labels", {})
            # Prefer Chinese, fallback English
            zh = labels.get("zh", {}).get("value", "")
            en = labels.get("en", {}).get("value", "")
            return zh or en
    except:
        return ""
    return ""

# Load brand seed data
with open("/workspace/pinpai-ai-in/brand_seed_raw.json", "r") as f:
    seed_data = json.load(f)

brand_seed = seed_data["brands"]
seed_by_name = {}
for b in brand_seed:
    seed_by_name[b["brand_name"].lower()] = b
    qid = b.get("wikidata_id", "")
    if qid:
        seed_by_name[qid] = b

# Build a diverse master.csv
# Structure: Escher + top brands by each category
cat_priority = {
    "fashion-luxury": 1, "fashion": 2, "watch": 3, "jewelry": 4,
    "beauty": 5, "auto": 6, "tech": 7, "sport": 8, "food": 9, "toy": 10,
}

# Select top brands per category
from collections import defaultdict
by_cat = defaultdict(list)
for b in brand_seed:
    by_cat[b.get("category", "other")].append(b)

# Manual curated top 50 with proper brand names
# Ensure Chinese brand gets correct slug
def slugify(name):
    """Convert brand name to clean URL-safe slug"""
    # Special case: 埃舍尔Escher → escher
    if name == "埃舍尔Escher":
        return "escher"
    slug = name.strip()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[&,+()/.\'’]', '-', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    # Remove non-ascii (keep only basic latin + numbers)
    slug = re.sub(r'[^a-zA-Z0-9\-\xe0-\xff]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.lower().strip('-')
    return slug[:40]

TOP_50 = [
    # 1. Escher (done)
    ("埃舍尔Escher", "中国", "fashion-luxury", "done"),
    # Fashion Luxury (7 more)
    ("Louis Vuitton", "法国", "fashion-luxury", "pending"),
    ("Hermès", "法国", "fashion-luxury", "pending"),
    ("Gucci", "意大利", "fashion-luxury", "pending"),
    ("Chanel", "法国", "fashion-luxury", "pending"),
    ("Christian Dior", "法国", "fashion-luxury", "pending"),
    ("Prada", "意大利", "fashion-luxury", "pending"),
    ("Balenciaga", "西班牙", "fashion-luxury", "pending"),
    # Fashion (5)
    ("Zara", "西班牙", "fashion", "pending"),
    ("Uniqlo", "日本", "fashion", "pending"),
    ("H&M", "瑞典", "fashion", "pending"),
    ("Levi's", "美国", "fashion", "pending"),
    ("Calvin Klein", "美国", "fashion", "pending"),
    # Beauty (5)
    ("L'Oréal", "法国", "beauty", "pending"),
    ("Estée Lauder", "美国", "beauty", "pending"),
    ("Shiseido", "日本", "beauty", "pending"),
    ("Lancôme", "法国", "beauty", "pending"),
    ("MAC Cosmetics", "美国", "beauty", "pending"),
    # Watch (3)
    ("Rolex", "瑞士", "watch", "pending"),
    ("Patek Philippe", "瑞士", "watch", "pending"),
    ("Audemars Piguet", "瑞士", "watch", "pending"),
    # Jewelry (3)
    ("Tiffany & Co.", "美国", "jewelry", "pending"),
    ("Cartier", "法国", "jewelry", "pending"),
    ("Bulgari", "意大利", "jewelry", "pending"),
    # Auto (5) - include Chinese brands
    ("Toyota", "日本", "auto", "pending"),
    ("Mercedes-Benz", "德国", "auto", "pending"),
    ("BMW", "德国", "auto", "pending"),
    ("Ferrari", "意大利", "auto", "pending"),
    ("BYD", "中国", "auto", "pending"),
    # Tech (5)
    ("Apple", "美国", "tech", "pending"),
    ("Samsung", "韩国", "tech", "pending"),
    ("Huawei", "中国", "tech", "pending"),
    ("Sony", "日本", "tech", "pending"),
    ("NVIDIA", "美国", "tech", "pending"),
    # Sport (3)
    ("Nike", "美国", "sport", "pending"),
    ("Adidas", "德国", "sport", "pending"),
    ("Puma", "德国", "sport", "pending"),
    # Food (3)
    ("Coca-Cola", "美国", "food", "pending"),
    ("McDonald's", "美国", "food", "pending"),
    ("Starbucks", "美国", "food", "pending"),
    # Toy (2)
    ("LEGO", "丹麦", "toy", "pending"),
    ("Mattel", "美国", "toy", "pending"),
    # Fashion (more) (5)
    ("Burberry", "英国", "fashion-luxury", "pending"),
    ("Versace", "意大利", "fashion-luxury", "pending"),
    ("Ralph Lauren", "美国", "fashion", "pending"),
    ("Tommy Hilfiger", "美国", "fashion", "pending"),
    ("Coach", "美国", "fashion", "pending"),
    # Tech (3 more)
    ("Microsoft", "美国", "tech", "pending"),
    ("Google", "美国", "tech", "pending"),
    ("Amazon", "美国", "tech", "pending"),
]

# Write master.csv
with open("/workspace/pinpai-ai-in/master.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "brand", "slug", "country", "industry", "status"])
    for idx, (name, country, industry, status) in enumerate(TOP_50, 1):
        slug = slugify(name)
        writer.writerow([idx, name, slug, country, industry, status])

print("✅ master.csv refreshed with curated top 50")
print(f"\nTotal: {len(TOP_50)} brands")
print()

# Show distribution
from collections import Counter
cat_dist = Counter(x[2] for x in TOP_50)
for cat, count in sorted(cat_dist.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

print(f"\n📄 master.csv preview:")
print("-" * 80)
with open("/workspace/pinpai-ai-in/master.csv", "r") as f:
    for i, line in enumerate(f):
        if i < 5 or i > 46:
            print(line.rstrip())
        elif i == 5:
            print("  ... (45 more rows) ...")
print("-" * 80)
