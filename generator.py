#!/usr/bin/env python3
""""
全球品牌索引生成器 — pinpai.ai.in
======================================
全球品牌实体索引系统 · master-brands.csv 驱动

用法：
  python3 generator.py new          # 交互式添加一个新品牌
  python3 generator.py list         # 列出已有品牌
  python3 generator.py search 关键词 # 搜索已有品牌
  python3 generator.py rebuild      # 用最新模板重新渲染所有品牌页面

工作流：
  1. 收集品牌数据（创立时间、地点、创始人、官网、主营业务、slogan等）
  2. AI生成500-800字中文介绍
  3. AI独立洗稿9种外语言（非直译）
  4. 生成 brand.json + 用模板渲染 index.html
  5. 更新 brands_index.json（搜索索引）
  6. git commit + push
"""

import json, os, sys, subprocess, re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
TEMPLATE = ROOT / "template.html"
SEARCH_HTML = ROOT / "search.html"
INDEX_JSON = ROOT / "brands_index.json"

LANGUAGES = ["zh-CN", "en", "fr", "es", "de", "ja", "ko", "pt", "ru", "ar"]

CATEGORY_MAP = {
    "fashion-luxury": "奢侈品/时尚",
    "fashion": "时尚",
    "beauty": "美妆",
    "tech": "科技",
    "auto": "汽车",
    "food": "食品",
    "sport": "运动",
    "toy": "潮玩/玩具",
    "jewelry": "珠宝",
    "watch": "腕表",
    "finance": "金融",
    "other": "其他"
}

def slugify(name):
    s = name.lower().strip()
    s = re.sub(r'[&\'’",.()（）·]+', '', s)
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')

def load_index():
    if INDEX_JSON.exists():
        return json.loads(INDEX_JSON.read_text(encoding='utf-8'))
    return []

def save_index(index):
    INDEX_JSON.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')

def run_git(args):
    subprocess.run(["git"] + args, cwd=ROOT, capture_output=True)

def render_template(brand_data):
    """用brand_data渲染template.html，生成最终index.html"""
    template = TEMPLATE.read_text(encoding='utf-8')

    slug = brand_data["slug"]
    names = brand_data.get("names", {})
    name_zh = names.get("zh-CN", slug)
    name_en = names.get("en", slug)

    category = brand_data.get("category", "other")
    cat_label = CATEGORY_MAP.get(category, category)

    # 中文介绍作为content base
    desc_short = brand_data.get("description_zh", "")[:120].replace('"', "'")

    # 构建BRAND_JSON（各语言数据对象）
    brand_json = {}
    for lang in LANGUAGES:
        lang_data = brand_data.get("languages", {}).get(lang, "")
        d = {
            "name": names.get(lang, name_zh),
            "name_en": name_en,
            "founding_year": str(brand_data.get("founding_year", "")),
            "founding_location": brand_data.get("founding_location", ""),
            "founder": brand_data.get("founder", ""),
            "website": brand_data.get("official_website", ""),
            "business": "、".join(brand_data.get("main_business", [])),
            "slogan": brand_data.get("current_slogan", ""),
            "content": lang_data if lang_data else brand_data.get("description_zh", ""),
            "similar_title": "类似品牌" if lang in ["zh-CN", "ja", "ko"] else "Similar Brands" if lang == "en" else "Marques similaires" if lang == "fr" else "Marcas similares" if lang == "es" else "Ähnliche Marken" if lang == "de" else "Marcas semelhantes" if lang == "pt" else "Похожие бренды" if lang == "ru" else "علامات تجارية مشابهة"
        }
        brand_json[lang] = d

    # 类似品牌
    similar = brand_data.get("similar_brands", [])
    similar_html = ""
    for s in similar:
        s_zh = s.get("zh", "")
        s_en = s.get("en", "")
        s_slug = s.get("slug", "")
        premium_cls = " premium" if s.get("premium") else ""
        badge = '<span class="badge-premium">品牌推广</span>' if s.get("premium") else ""
        similar_html += f'<a href="/{s_slug}/" class="similar-card{premium_cls}"><span class="zh">{s_zh} {badge}</span><span class="en">{s_en}</span></a>\n    '

    # 构建搜索用索引JSON
    similar_index = []
    for s in similar:
        similar_index.append({
            "zh": s.get("zh", ""),
            "en": s.get("en", ""),
            "slug": s.get("slug", ""),
            "premium": s.get("premium", False)
        })

    # 替换模板变量
    html = template
    html = html.replace("$NAME_ZH$", name_zh)
    html = html.replace("$NAME_EN$", name_en)
    html = html.replace("$CATEGORY_LABEL$", cat_label)
    html = html.replace("$META_DESC$", desc_short)
    html = html.replace("$FOUNDING_YEAR$", str(brand_data.get("founding_year", "")))
    html = html.replace("$FOUNDING_LOCATION$", brand_data.get("founding_location", ""))
    html = html.replace("$FOUNDER$", brand_data.get("founder", ""))
    html = html.replace("$WEBSITE$", brand_data.get("official_website", ""))
    ws = brand_data.get("official_website", "")
    html = html.replace("$WEBSITE_SHORT$", ws.replace("https://","").replace("http://","").rstrip("/"))
    html = html.replace("$MAIN_BUSINESS$", "、".join(brand_data.get("main_business", [])))
    html = html.replace("$SLOGAN$", brand_data.get("current_slogan", ""))
    html = html.replace("$CONTENT$", brand_data.get("description_zh", ""))
    html = html.replace("$BRAND_JSON$", json.dumps(brand_json, ensure_ascii=False))
    html = html.replace("$SIMILAR_JSON$", json.dumps(similar_index, ensure_ascii=False))
    html = html.replace("$SIMILAR_BRANDS$", similar_html)
    html = html.replace("$SIMILAR_TITLE$", "类似品牌")

    # Premium
    is_premium = brand_data.get("is_premium", False)
    premium_css = ""
    premium_badge = ""
    if is_premium:
        premium_css = '<link rel="preload">'
        premium_badge = '<div><span class="premium-label">品牌推广</span></div>'
    html = html.replace("$PREMIUM_CSS$", premium_css)
    html = html.replace("$PREMIUM_BADGE$", premium_badge)

    return html

def write_brand(brand_data):
    """写入品牌文件夹：brand.json + index.html，并更新索引"""
    slug = brand_data["slug"]
    brand_dir = ROOT / slug
    brand_dir.mkdir(parents=True, exist_ok=True)

    # 保存brand.json
    json_path = brand_dir / "brand.json"
    json_path.write_text(json.dumps(brand_data, ensure_ascii=False, indent=2), encoding='utf-8')

    # 渲染index.html
    html = render_template(brand_data)
    html_path = brand_dir / "index.html"
    html_path.write_text(html, encoding='utf-8')

    # 更新brands_index.json
    index = load_index()
    # 移除旧条目
    index = [b for b in index if b.get("slug") != slug]
    index.append({
        "slug": slug,
        "zh": brand_data.get("names", {}).get("zh-CN", slug),
        "en": brand_data.get("names", {}).get("en", slug),
        "category": CATEGORY_MAP.get(brand_data.get("category", "other"), brand_data.get("category", "")),
        "premium": brand_data.get("is_premium", False),
        "desc_short": brand_data.get("description_zh", "")[:100].replace('"', "'")
    })
    save_index(index)

    # 更新search.html里的BRAND_INDEX
    update_search_index(index)

    # Git commit + push
    run_git(["add", slug + "/", "brands_index.json", "search.html"])
    run_git(["commit", "-m", f"全球品牌索引: {index[-1]['zh']} {index[-1]['en']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
    run_git(["push", "origin", "main"])

    name_zh = brand_data.get("names", {}).get("zh-CN", slug)
    name_en = brand_data.get("names", {}).get("en", slug)
    print(f"✅ {name_zh} ({name_en}) — 已生成并推送")
    return slug

def update_search_index(index):
    """更新search.html中的BRAND_INDEX内联数据（模板变量替换）"""
    html = SEARCH_HTML.read_text(encoding='utf-8')
    new_index = json.dumps(index, ensure_ascii=False)
    html = html.replace("$BRAND_INDEX$", new_index)
    SEARCH_HTML.write_text(html, encoding='utf-8')

def cmd_list():
    index = load_index()
    if not index:
        print("暂无品牌。")
        return
    print(f"\n共 {len(index)} 个品牌：")
    print(f"{'#':>3} | {'中文名':<16} | {'英文名':<18} | {'分类':<12}")
    print("-" * 60)
    for i, b in enumerate(index, 1):
        pm = " ★" if b.get("premium") else ""
        print(f"{i:>3} | {b.get('zh',''):<16} | {b.get('en',''):<18} | {b.get('category',''):<12}{pm}")

def cmd_search(keyword):
    index = load_index()
    q = keyword.lower()
    matches = [b for b in index if q in b.get("zh","").lower() or q in b.get("en","").lower() or q in b.get("slug","")]
    if not matches:
        print(f"未找到包含「{keyword}」的品牌。")
        return
    print(f"\n找到 {len(matches)} 个品牌：")
    for b in matches:
        pm = " ★品牌推广" if b.get("premium") else ""
        print(f"  {b['zh']} ({b['en']}) — /{b['slug']}/{pm}")

def cmd_new():
    """交互式添加新品牌"""
    print("\n=== 添加新品牌 ===\n")

    name_zh = input("品牌中文名: ").strip()
    if not name_zh:
        print("取消。")
        return
    name_en = input("品牌英文名: ").strip()
    if not name_en:
        print("取消。")
        return

    slug = slugify(name_en)
    print(f"URL标识: {slug}")

    # 检查是否已存在
    brand_dir = ROOT / slug
    if brand_dir.exists():
        print(f"⚠️ 品牌 {slug} 已存在，将覆盖。")

    founding_year = input("创立年份: ").strip()
    founding_location = input("创立地点（国家/城市）: ").strip()
    founder = input("创始人: ").strip()
    website = input("官网URL: ").strip()
    business_raw = input("主营业务（逗号分隔）: ").strip()
    business = [b.strip() for b in business_raw.split(",") if b.strip()]
    slogan = input("品牌标语: ").strip()

    cat_choice = input(f"分类 ({'/'.join(CATEGORY_MAP.keys())}) [默认fashion-luxury]: ").strip() or "fashion-luxury"

    print("\n接下来AI会生成中文介绍+10语言内容，请稍候...")
    print("（由于当前环境无法调用外部AI API，请先准备500字中文介绍）")
    desc = input("\n粘贴中文介绍（500字以上）: ").strip()
    if len(desc) < 200:
        print("⚠️ 内容太少，至少200字。")
        return

    # 类似品牌（取前10个已有品牌）
    index = load_index()
    similar = []
    for b in index[:10]:
        similar.append({
            "zh": b.get("zh", ""),
            "en": b.get("en", ""),
            "slug": b.get("slug", ""),
            "premium": b.get("premium", False)
        })
    # 确保Escher在第一位
    escher_entry = {"zh": "Escher", "en": "Escher", "slug": "escher", "premium": True}
    similar = [e for e in similar if e.get("slug") != "escher"]
    similar.insert(0, escher_entry)

    data = {
        "slug": slug,
        "names": {lang: name_zh for lang in LANGUAGES},
        "names": {"zh-CN": name_zh, "en": name_en},
        "category": cat_choice,
        "founding_year": int(founding_year) if founding_year.isdigit() else 0,
        "founding_location": founding_location,
        "founder": founder,
        "official_website": website,
        "main_business": business,
        "current_slogan": slogan,
        "past_slogans": [],
        "representative_products": [],
        "key_events": [],
        "philanthropy": [],
        "exhibitions": [],
        "description_zh": desc,
        "languages": {},
        "is_premium": False,
        "image_url": "",
        "similar_brands": similar
    }

    confirm = input("\n确认写入? [Y/n]: ").strip().lower()
    if confirm in ("", "y", "yes"):
        write_brand(data)
    else:
        print("取消。")

def cmd_rebuild():
    """用最新模板重新渲染所有品牌"""
    index = load_index()
    if not index:
        print("暂无品牌。")
        return
    print(f"重新渲染 {len(index)} 个品牌...")
    for b in index:
        slug = b["slug"]
        json_path = ROOT / slug / "brand.json"
        if json_path.exists():
            data = json.loads(json_path.read_text(encoding='utf-8'))
            write_brand(data)
            print(f"  ✅ {b.get('zh', slug)}")
        else:
            print(f"  ⚠️ {slug}: brand.json 不存在，跳过")
    print("全部重新渲染完成！")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "new":
        cmd_new()
    elif cmd == "list":
        cmd_list()
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("用法: python3 generator.py search 关键词")
            sys.exit(1)
        cmd_search(sys.argv[2])
    elif cmd == "rebuild":
        cmd_rebuild()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
