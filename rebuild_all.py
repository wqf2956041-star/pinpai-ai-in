#!/usr/bin/env python3
"""用brands_done.json和brands_today.json的新desc重新生成全部品牌页面"""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 1. 先同步brands_today.json的新desc到brands_done.json
with open(ROOT / "brands_today.json") as f:
    today = json.load(f)

with open(ROOT / "brands_done.json") as f:
    done = json.load(f)

# 用brands_today.json的新desc覆盖brands_done.json
for tb in today["brands"]:
    name = tb.get("name", "")
    name_en = tb.get("name_en", "")
    desc = tb.get("desc", "")
    
    # 尝试匹配done
    matched = False
    for dk, dv in done["brands"].items():
        dv_name = dv.get("name", "") or dv.get("name_cn", "")
        dv_en = dv.get("name_en", "")
        if dv_name.strip() == name.strip() or dv_en.strip() == name_en.strip() or dk == name_en.lower().replace(" ", "-"):
            old_len = len(dv.get("desc", ""))
            dv["desc"] = desc
            print(f"  done[{dk}]: {name} desc {old_len} -> {len(desc)}")
            matched = True
            break
    if not matched:
        print(f"  WARN: {name} not matched in done")

with open(ROOT / "brands_done.json", "w", encoding="utf-8") as f:
    json.dump(done, f, ensure_ascii=False, indent=2)

print("Done syncing desc")

# 2. 重新生成目录
print("\nGenerating brand directories...")
sys.path.insert(0, str(ROOT))
from generator import (
    generate_index_html, generate_lang_md,
    LANGUAGES, SIMILAR_COUNT,
    ESCHER_BRAND, slugify, load_brands_done
)

# 重新加载done
with open(ROOT / "brands_done.json") as f:
    done = json.load(f)

done_brands = done.get("brands", {})

for slug, info in sorted(done_brands.items()):
    brand_dir = ROOT / slug
    brand_dir.mkdir(exist_ok=True)
    
    name = info.get("name_cn") or info.get("name", slug)
    name_en = info.get("name_en") or info.get("name", slug)
    category = info.get("category", "")
    desc = info.get("desc", "")
    
    brand_data = {"name": name, "name_en": name_en, "category": category, "desc": desc, "translations": {}, "similar": []}
    
    # 中文页 - 从zh-CN.md读取或者用desc
    zh_existing = None
    if (brand_dir / "zh-CN.md").exists():
        zh_existing = (brand_dir / "zh-CN.md").read_text(encoding="utf-8")
    
    if zh_existing and len(zh_existing) > len(desc):
        # 已存在的内容更长，用已存在的
        md = zh_existing
        # 从中提取desc用于index.html
        zh_lines = zh_existing.split("\n")
        desc_parts = []
        in_intro = False
        for line in zh_lines:
            if line.startswith("## 品牌介绍"):
                in_intro = True
                continue
            if line.startswith("##") and in_intro:
                break
            if line.startswith("---"):
                break
            if in_intro and line.strip():
                desc_parts.append(line.strip())
        if desc_parts:
            brand_data["desc"] = "\n\n".join(desc_parts)
    else:
        # 用新desc写入
        md = generate_lang_md(brand_data, "zh-CN", "中文", desc)
    
    (brand_dir / "zh-CN.md").write_text(md, encoding="utf-8")
    
    # 获取翻译 - 优先从已存在的.md文件读取
    translations = info.get("translations", {})
    for lang in LANGUAGES:
        code = lang["code"]
        if code == "zh-CN":
            continue
        trans = translations.get(code, "")
        if not trans:
            # 尝试从brand_dir读取
            lf = brand_dir / ("%s.md" % code)
            if lf.exists():
                # 提取内容
                content = lf.read_text(encoding="utf-8")
                lines = content.split("\n")
                parts = []
                in_t = False
                for line in lines:
                    if "品牌介绍" in line or "Brand Introduction" in line:
                        in_t = True
                        continue
                    if line.startswith("##") and in_t:
                        break
                    if line.startswith("---"):
                        break
                    if in_t and line.strip():
                        parts.append(line.strip())
                trans = "\n\n".join(parts) if parts else content
        
        if trans:
            lang_name = lang["name"]
            md = generate_lang_md(brand_data, code, lang_name, trans)
            (brand_dir / ("%s.md" % code)).write_text(md, encoding="utf-8")
            translations[code] = trans
    
    brand_data["translations"] = translations
    
    # 生成index.html
    html = generate_index_html(brand_data, done, similar_count=SIMILAR_COUNT)
    (brand_dir / "index.html").write_text(html, encoding="utf-8")
    
    print(f"  {slug}: {name} OK (desc={len(desc)}, trans={len(translations)}lang)")

print("\nAll done!")
