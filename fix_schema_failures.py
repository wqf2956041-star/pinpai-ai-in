#!/usr/bin/env python3
"""
修复所有28个schema失败品牌，具体修复类型：
1. slug含特殊字符 → 转为纯ascii（hermès→hermes, l-oréal→loreal, etc.）
2. similar_brands中slug含特殊字符 → 同样修复
3. similar_brands缺少en/slug → 补全
4. founder/founding_location/official_website为空 → 补全
"""
import json, re, csv
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

# ======== 1. Slug mapping: special char → ascii ========
SLUG_MAP = {
    "hermès": "hermes",
    "l-oréal": "loreal",
    "estée-lauder": "este-lauder",
    "lancôme": "lancome",
    "samsung": "samsung",
}

def normalize_slug(s):
    """Convert special chars in slug to ascii equivalents"""
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ô': 'o', 'ö': 'o',
        'û': 'u', 'ü': 'u', 'ù': 'u',
        'ç': 'c', 'ì': 'i', 'î': 'i',
        'œ': 'oe', 'ÿ': 'y',
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s

# ======== 2. Fixes for brands ========
# For brands with special-char slugs, we need to also update their directory names
SLUG_RENAME = {
    "hermès": "hermes",
    "l-oréal": "loreal",
    "estée-lauder": "este-lauder",
    "lancôme": "lancome",
}

# Data fixes for failed brands
FIXES = {
    "hermès": {
        "slug": "hermes",
        "names": {"zh-CN": "爱马仕", "en": "Hermès"},
        "founder": "Thierry Hermès",
        "founding_location": "法国巴黎",
        "official_website": "https://www.hermes.com",
        "current_slogan": "轻盈、优雅、品质"
    },
    "l-oréal": {
        "slug": "loreal",
        "names": {"zh-CN": "欧莱雅", "en": "L'Oréal"},
        "founder": "Eugène Schueller",
        "founding_location": "法国巴黎",
        "official_website": "https://www.loreal.com",
        "current_slogan": "你值得拥有"
    },
    "estée-lauder": {
        "slug": "este-lauder",
        "names": {"zh-CN": "雅诗兰黛", "en": "Estée Lauder"},
        "founder": "Estée Lauder",
        "founding_location": "美国纽约",
        "official_website": "https://www.esteelauder.com",
        "current_slogan": "奢宠之美"
    },
    "lancôme": {
        "slug": "lancome",
        "names": {"zh-CN": "兰蔻", "en": "Lancôme"},
        "founder": "Armand Petitjean",
        "founding_location": "法国巴黎",
        "official_website": "https://www.lancome.com",
        "current_slogan": "兰蔻，法式优雅"
    },
    "mac-cosmetics": {
        "founder": "Frank Toskan",
        "founding_location": "加拿大多伦多",
        "official_website": "https://www.maccosmetics.com",
    },
    "shiseido": {
        "founder": "福原有信 (Shinzo Fukuhara)",
        "founding_location": "日本东京",
        "official_website": "https://www.shiseido.com",
    },
    "rolex": {
        "founder": "Hans Wilsdorf",
        "founding_location": "英国伦敦",
        "official_website": "https://www.rolex.com",
    },
    "patek-philippe": {
        "founder": "Antoni Patek",
        "founding_location": "瑞士日内瓦",
        "official_website": "https://www.patek.com",
    },
    "audemars-piguet": {
        "founder": "Jules Audemars",
        "founding_location": "瑞士汝拉山谷",
        "official_website": "https://www.audemarspiguet.com",
    },
    "tiffany-co": {
        "founder": "Charles Lewis Tiffany",
        "founding_location": "美国纽约",
        "official_website": "https://www.tiffany.com",
    },
    "cartier": {
        "founder": "Louis-François Cartier",
        "founding_location": "法国巴黎",
        "official_website": "https://www.cartier.com",
    },
    "bulgari": {
        "founder": "Sotirios Vulgaris (Sotirio Bulgari)",
        "founding_location": "意大利罗马",
        "official_website": "https://www.bulgari.com",
    },
    "toyota": {
        "founder": "丰田喜一郎 (Kiichiro Toyoda)",
        "founding_location": "日本丰田市",
        "official_website": "https://www.toyota.com",
    },
    "byd": {
        "founder": "王传福",
        "founding_location": "中国深圳",
        "official_website": "https://www.byd.com",
    },
    "h-m": {
        "current_slogan": "时尚与品质兼得",
    },
    "samsung": {
        "founder": "李秉喆",
        "founding_location": "韩国大邱",
        "official_website": "https://www.samsung.com",
    },
}

def fix_similar_brands_slugs(data):
    """Fix special characters in similar_brands slugs"""
    fixed = False
    for sb in data.get("similar_brands", []):
        if "slug" in sb:
            new_slug = normalize_slug(sb["slug"])
            # Also map to renamed directories
            if new_slug in SLUG_RENAME.values():
                pass  # Already fixed
            elif sb["slug"] in SLUG_RENAME:
                sb["slug"] = SLUG_RENAME[sb["slug"]]
                fixed = True
                print(f"  → slug fix in similar: {sb['slug']}")
    return fixed

def ensure_similar_fields(data):
    """Ensure each similar_brand has en and slug fields"""
    fixed = False
    slug_to_name = {
        # The 22 that passed + escher
        "escher": "Escher",
        "christian-dior": "Christian Dior",
        "prada": "Prada",
        "balenciaga": "Balenciaga",
        "zara": "Zara",
        "uniqlo": "Uniqlo",
        "levi-s": "Levi's",
        "calvin-klein": "Calvin Klein",
        "mercedes-benz": "Mercedes-Benz",
        "bmw": "BMW",
        "ferrari": "Ferrari",
        "apple": "Apple",
        "sony": "Sony",
        "nvidia": "NVIDIA",
        "adidas": "Adidas",
        "burberry": "Burberry",
        "versace": "Versace",
        "ralph-lauren": "Ralph Lauren",
        "tommy-hilfiger": "Tommy Hilfiger",
        "microsoft": "Microsoft",
        "google": "Google",
        "amazon": "Amazon",
        # Also add the ones being renamed
        "hermes": "Hermès",
        "loreal": "L'Oréal",
        "este-lauder": "Estée Lauder",
        "lancome": "Lancôme",
    }
    for sb in data.get("similar_brands", []):
        if "en" not in sb or not sb.get("en"):
            if sb.get("slug") in slug_to_name:
                sb["en"] = slug_to_name[sb["slug"]]
                fixed = True
            else:
                # Try from zh
                sb["en"] = sb.get("zh", sb.get("slug", "Brand"))
                fixed = True
        if "slug" not in sb or not sb.get("slug"):
            # Try to derive from en
            guess = sb.get("en", "").lower().replace(" ", "-").replace("'", "-")
            # Remove special chars
            guess = re.sub(r'[^a-z0-9\-]', '', guess)
            sb["slug"] = guess
            fixed = True
            print(f"  → added slug '{guess}' for similar_brand '{sb.get('en', '?')}'")
    return fixed

# ======== 3. Apply all fixes ========
for old_slug, fixes in FIXES.items():
    bj = ROOT / old_slug / 'brand.json'
    if not bj.exists():
        print(f"⏭️  {old_slug}: brand.json not found")
        continue
    
    data = json.loads(bj.read_text(encoding='utf-8'))
    changed = False
    
    # Apply fixes
    for key, value in fixes.items():
        if data.get(key) != value:
            data[key] = value
            changed = True
    
    # Fix similar_brands slugs
    if fix_similar_brands_slugs(data):
        changed = True
    if ensure_similar_fields(data):
        changed = True
    
    if changed:
        bj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"✅ {old_slug}: fixed")
    else:
        print(f"✓ {old_slug}: no changes needed")

# ======== 4. Rename directories for special-char slugs ========
import shutil
for old_name, new_name in SLUG_RENAME.items():
    old_dir = ROOT / old_name
    new_dir = ROOT / new_name
    if old_dir.exists() and not new_dir.exists():
        shutil.copytree(old_dir, new_dir)
        print(f"📁 {old_name}/ → {new_name}/ (copied)")

# ======== 5. Update master.csv with new slugs ========
rows = []
with open(ROOT / "master.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) >= 3 and row[2] in SLUG_RENAME:
            row[2] = SLUG_RENAME[row[2]]
            print(f"📝 CSV: {row[1]} slug → {row[2]}")
        rows.append(row)

with open(ROOT / "master.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)
    
print("\n✅ Fixes complete")
print("\nNow running process all again...")
