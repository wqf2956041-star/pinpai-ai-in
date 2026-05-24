#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""强制重新生成所有品牌的index.html和语言文件，保留原有内容"""
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generator import (
    generate_index_html, generate_lang_md,
    LANGUAGES, SIMILAR_COUNT,
    ESCHER_BRAND, slugify
)

REPO_ROOT = Path(__file__).resolve().parent
BRANDS_FILE = REPO_ROOT / "brands_done.json"

with open(BRANDS_FILE, 'r') as f:
    brands_done = json.load(f)

# 从已存在的文件读取品牌描述
done_brands = brands_done.get("brands", {})
count = 0

for slug, info in sorted(done_brands.items()):
    brand_dir = REPO_ROOT / slug
    if not brand_dir.exists():
        print("SKIP %s: dir not found" % slug)
        continue
    
    # 读取已存在的zh-CN.md获取描述
    zh_file = brand_dir / "zh-CN.md"
    if not zh_file.exists():
        print("SKIP %s: zh-CN.md not found" % slug)
        continue
    
    zh_content = zh_file.read_text(encoding="utf-8")
    
    # 提取品牌介绍部分（去掉标题）
    lines = zh_content.split("\n")
    desc_parts = []
    in_intro = False
    for line in lines:
        if line.startswith("## 品牌介绍"):
            in_intro = True
            continue
        if line.startswith("##") and in_intro:
            break
        if line.startswith("---"):
            break
        if in_intro and line.strip():
            desc_parts.append(line.strip())
    
    desc = "\n\n".join(desc_parts) if desc_parts else zh_content
    
    name = info.get("name_cn") or info.get("name", slug)
    name_en = info.get("name", slug)
    category = info.get("category", "")
    
    # 读取各语言文件
    translations = {}
    for lang in LANGUAGES:
        code = lang["code"]
        if code == "zh-CN":
            continue
        lang_file = brand_dir / ("%s.md" % code)
        if lang_file.exists():
            content = lang_file.read_text(encoding="utf-8")
            # 提取翻译后的描述
            t_parts = []
            in_t = False
            for line in content.split("\n"):
                if line.startswith("## 品牌介绍") or line.startswith("## Brand Introduction") or "品牌介绍" in line:
                    in_t = True
                    continue
                if line.startswith("##") and in_t:
                    break
                if line.startswith("---"):
                    break
                if in_t and line.strip():
                    t_parts.append(line.strip())
            trans = "\n\n".join(t_parts) if t_parts else content
            if trans:
                translations[code] = trans
    
    brand_data = {
        "name": name,
        "name_en": name_en,
        "category": category,
        "desc": desc,
        "translations": translations,
        "similar": []
    }
    
    print("REGEN: %s (%s) -> /%s/ [desc=%d, trans=%d lang]" % (name, name_en, slug, len(desc), len(translations)))
    
    # 1. 重新生成index.html
    html = generate_index_html(brand_data, brands_done, similar_count=SIMILAR_COUNT)
    (brand_dir / "index.html").write_text(html, encoding="utf-8")
    
    # 2. 重新生成语言文件（用已有翻译内容）
    for lang in LANGUAGES:
        code = lang["code"]
        lang_name = lang["name"]
        content = desc if code == "zh-CN" else translations.get(code, "")
        if content:
            md = generate_lang_md(brand_data, code, lang_name, content)
            (brand_dir / ("%s.md" % code)).write_text(md, encoding="utf-8")
        else:
            print("  WARN: %s missing %s translation" % (slug, code))
    
    count += 1
    print("  OK")

print("\n完成！重新生成了 %d 个品牌，无广告位，类似品牌=%d个，格式=中英文" % (count, SIMILAR_COUNT))
