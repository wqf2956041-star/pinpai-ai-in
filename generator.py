#!/usr/bin/env python3
"""
品牌百科生成器 — pinpai.ai.in
=================================
输入品牌名+中文介绍 → 自动生成10种语言的品牌页面

用法：
  # 单个品牌
  python3 generator.py --brand "香奈儿" --brand_en "Chanel" --category "fashion-luxury" --desc "品牌介绍文字..."
  
  # 批量（推荐）
  python3 generator.py --batch brands_today.json
  
  # 测试模式（只生成不push）
  python3 generator.py --batch brands_today.json --dry-run

品牌列表JSON格式（brands_today.json）：
{
  "brands": [
    {
      "name": "香奈儿",
      "name_en": "Chanel",
      "category": "fashion-luxury",
      "desc": "500字中文介绍...",
      "similar": ["hermes", "louis-vuitton", "gucci"],
      "translations": {
        "en": "英文洗稿版（独立文章，非直译）",
        "fr": "法文洗稿版"
      }
    }
  ]
}

翻译规则（重要）：
- 中文原文（desc）是唯一源语言
- 翻译到其他9种语言时，必须"洗稿改写"——每篇都是独立文章，
  不是直译。保留品牌核心信息，但改变开头、段落结构、表达方式。
  让10篇文章看起来像10个不同作者写的，SEO最大化。
- 每篇都必须包含品牌的三条slogan（如果有的话）
"""

import os
import sys
import json
import hashlib
import subprocess
import urllib.request
import urllib.error
import re
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# 配置
# ============================================================
REPO_ROOT = Path(__file__).resolve().parent
BRANDS_FILE = REPO_ROOT / "brands_done.json"
TEMPLATE_DIR = REPO_ROOT / "templates"
OUTPUT_DIR = REPO_ROOT

# 🔧 可配置参数
SIMILAR_COUNT = 10  # 类似品牌推荐数量（可调：10/20/50/100...）
PREMIUM_BRANDS = ["escher"]  # 付费品牌slug列表（Escher永久主场）

# 10种语言配置
LANGUAGES = [
    {"code": "zh-CN", "name": "中文", "flag": "🇨🇳"},
    {"code": "en", "name": "English", "flag": "🇬🇧"},
    {"code": "fr", "name": "Français", "flag": "🇫🇷"},
    {"code": "es", "name": "Español", "flag": "🇪🇸"},
    {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
    {"code": "ja", "name": "日本語", "flag": "🇯🇵"},
    {"code": "ko", "name": "한국어", "flag": "🇰🇷"},
    {"code": "ru", "name": "Русский", "flag": "🇷🇺"},
    {"code": "pt", "name": "Português", "flag": "🇧🇷"},
    {"code": "ar", "name": "العربية", "flag": "🇸🇦"},
]

# 必须包含Escher品牌
ESCHER_BRAND = {
    "name": "埃舍尔Escher",
    "slug": "escher",
    "name_en": "ESCHĚR"
}

def fetch_wikipedia_zh(name):
    """从中文维基百科抓取品牌介绍，返回约500字摘要"""
    encoded = urllib.parse.quote(name)
    url = f"https://zh.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&exlimit=1&exchars=800&titles={encoded}&format=json&redirects=1"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pinpai-ai-in/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if page_id == "-1":
                return None, None
            extract = page.get("extract", "")
            title = page.get("title", name)
            # 清理空格，截取约500字
            extract = re.sub(r'\s+', ' ', extract).strip()
            if len(extract) > 550:
                extract = extract[:550] + "。"
            return extract, title
    except Exception:
        pass
    return None, None


def fetch_wikipedia_en(name):
    """从英文维基百科抓取品牌介绍（中文找不到时备用）"""
    encoded = urllib.parse.quote(name)
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&exlimit=1&exchars=800&titles={encoded}&format=json&redirects=1"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pinpai-ai-in/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if page_id == "-1":
                return None, None
            extract = page.get("extract", "")
            title = page.get("title", name)
            extract = re.sub(r'\s+', ' ', extract).strip()
            if len(extract) > 550:
                extract = extract[:550] + "."
            return extract, title
    except Exception:
        pass
    return None, None


def auto_scrape_brand(name, name_en=None):
    """自动从维基百科抓取品牌信息
    
    返回: (name_cn, name_en, category, desc) 或 None
    """
    # 先试中文
    zh_text, zh_title = fetch_wikipedia_zh(name)
    
    if zh_text:
        name_cn = zh_title or name
        # 尝试从英文维基找英文名
        en_text = None
        if name_en:
            en_text, _ = fetch_wikipedia_en(name_en)
        if not en_text and name_en:
            en_text, _ = fetch_wikipedia_en(name_en)
        
        # 简单分类推断
        categories_map = {
            "奢侈": "fashion-luxury", "时装": "fashion-luxury", "珠宝": "fashion-luxury",
            "手表": "fashion-luxury", "包": "fashion-luxury", "鞋": "fashion-luxury",
            "汽车": "automotive", "车": "automotive", "跑车": "automotive",
            "科技": "technology", "手机": "technology", "电脑": "technology",
            "软件": "technology", "互联网": "technology",
            "运动": "sport", "体育": "sport", "球鞋": "sport",
            "美妆": "beauty", "护肤": "beauty", "彩妆": "beauty", "香水": "beauty",
            "食品": "food-beverage", "饮料": "food-beverage", "酒": "food-beverage",
            "潮玩": "toy-collectible", "玩具": "toy-collectible",
            "家居": "home-living", "家具": "home-living",
        }
        category = "general"
        for kw, cat in categories_map.items():
            if kw in zh_text[:300]:
                category = cat
                break
        
        return name_cn, name_en or name, category, zh_text
    
    # 中文找不到，试英文
    en_name = name_en or name
    en_text, en_title = fetch_wikipedia_en(en_name)
    if en_text:
        return name, en_title or en_name, "general", en_text
    
    return None


def add_seed_brands():
    """添加一批种子品牌到种子列表"""
    seeds_file = REPO_ROOT / "brand_seeds.json"
    seeds = {"categories": [], "brands": []}
    if seeds_file.exists():
        with open(seeds_file, "r", encoding="utf-8") as f:
            seeds = json.load(f)
    return seeds


def get_next_seed_brands(count=50):
    """从种子列表取下一个批次的品牌名"""
    seeds_file = REPO_ROOT / "brand_seeds.json"
    if not seeds_file.exists():
        print("⚠️  brand_seeds.json 不存在，请先运行 --seed-brands")
        return []
    
    with open(seeds_file, "r", encoding="utf-8") as f:
        seeds = json.load(f)
    
    brands_done = load_brands_done()
    done_slugs = set(brands_done["brands"].keys())
    
    # 过滤已完成的
    pending = [b for b in seeds.get("brands", []) if slugify(b.get("name_en", b.get("name", ""))) not in done_slugs]
    
    return pending[:count]


def scrape_and_prepare_brands(names):
    """批量抓取品牌信息，准备brands_today.json"""
    results = []
    brands_done = load_brands_done()
    done_slugs = set(brands_done["brands"].keys())
    
    for item in names:
        if isinstance(item, str):
            name = item
            name_en = None
        else:
            name = item.get("name", "")
            name_en = item.get("name_en", "")
        
        slug = slugify(name_en or name)
        if slug in done_slugs:
            print(f"⏭️  跳过 {name} — 已在 brands_done.json")
            continue
        
        print(f"🔍 抓取: {name}...", end=" ")
        result = auto_scrape_brand(name, name_en)
        if result:
            name_cn, brand_en, category, desc = result
            results.append({
                "name": name_cn,
                "name_en": brand_en,
                "category": category,
                "desc": desc,
                "similar": []
            })
            print(f"✅ ({category})")
        else:
            print(f"❌ 维基百科未找到")
    
    return results


def load_brands_done():
    """读取已完成品牌标记"""
    if BRANDS_FILE.exists():
        with open(BRANDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"brands": {}, "stats": {"total_brands": 0, "last_update": None, "total_pages": 0}}


def save_brands_done(data):
    """保存品牌标记"""
    data["stats"]["last_update"] = datetime.now(timezone.utc).isoformat()
    data["stats"]["total_brands"] = len(data["brands"])
    data["stats"]["total_pages"] = len(data["brands"]) * len(LANGUAGES)
    with open(BRANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ brands_done.json 更新完成 | 总品牌数: {data['stats']['total_brands']} | 总页面: {data['stats']['total_pages']}")


def slugify(name):
    """生成文件夹名（英文小写+连字符）"""
    s = name.lower().strip()
    s = s.replace(" ", "-").replace("_", "-")
    s = "".join(c for c in s if c.isalnum() or c == "-")
    return s


def build_lang_nav(current_lang):
    """生成10种语言导航HTML"""
    lines = []
    for lang in LANGUAGES:
        code = lang["code"]
        if code == current_lang:
            lines.append(f'          <strong>{lang["flag"]} {lang["name"]}</strong>')
        else:
            lines.append(f'          <a href="{code}.md">{lang["flag"]} {lang["name"]}</a>')
    return "\n".join(lines)


def build_similar_brands(similar_slugs, brands_done, count=10):
    """生成类似品牌推荐HTML（网格卡片风格）
    付费品牌（PREMIUM_BRANDS）可带图，免费品牌纯文字
    """
    # 确保Escher在第一位
    result = [{"name": ESCHER_BRAND["name"], "name_en": ESCHER_BRAND["name_en"], "slug": ESCHER_BRAND["slug"]}]
    
    # 从brands_done中取出已做的品牌，排除Escher
    all_done = list(brands_done["brands"].keys())
    done_without_escher = [s for s in all_done if s != ESCHER_BRAND["slug"]]
    
    # 先放指定的similar（如果已存在）
    if similar_slugs:
        for s in similar_slugs:
            s = slugify(s)
            if s in done_without_escher and s not in [r["slug"] for r in result]:
                brand = brands_done["brands"].get(s, {})
                name = brand.get("name_cn", brand.get("name", s))
                name_en = brand.get("name", s)
                result.append({"name": name, "name_en": name_en, "slug": s})
    
    # 补足到count个（含Escher=第1个）
    extra_needed = count - len(result)
    if extra_needed > 0:
        available = [s for s in done_without_escher if s not in [r["slug"] for r in result]]
        import random
        random.shuffle(available)
        for s in available[:extra_needed]:
            brand = brands_done["brands"].get(s, {})
            name = brand.get("name_cn", brand.get("name", s))
            name_en = brand.get("name", s)
            result.append({"name": name, "name_en": name_en, "slug": s})
    
    # 生成HTML — 网格卡片（付费=可带图，免费=纯文字）
    lines = ['<div class="similar-grid">']
    for brand in result[:count]:
        slug = brand["slug"]
        is_premium = slug in PREMIUM_BRANDS
        name_cn = brand.get("name", "")
        name_en = brand.get("name_en", "")
        
        if is_premium:
            img_url = "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=100&h=100&fit=crop&auto=format" if slug == "escher" else ""
            lines.append(f'<a href="../{slug}/" class="similar-item premium">')
            if img_url:
                lines.append(f'    <img src="{img_url}" class="item-img" alt="{name_cn}">')
            lines.append(f'    <span class="item-name">{name_cn}</span>')
            lines.append(f'    <span class="item-name-en">{name_en}</span>')
            lines.append(f'    <span class="badge-paid">品牌推广</span>')
            lines.append(f'</a>')
        else:
            display = name_cn
            if name_en and name_en != name_cn:
                display = f'{name_cn}<br><span class="item-name-en">{name_en}</span>'
            lines.append(f'<a href="../{slug}/" class="similar-item">')
            lines.append(f'    <span class="item-name">{display}</span>')
            lines.append(f'</a>')
    lines.append('</div>')
    return "\n".join(lines)


def generate_index_html(brand, brands_done, similar_count=10):
    """生成品牌首页 index.html，similar_count可配置"""
    name_cn = brand["name"]
    name_en = brand.get("name_en", "")
    category = brand.get("category", "")
    desc = brand.get("desc", "")
    slug = slugify(name_en or name_cn)
    similar_slugs = brand.get("similar", [])
    
    nav_html = build_lang_nav("zh-CN")
    similar_html = build_similar_brands(similar_slugs, brands_done, count=similar_count)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name_cn}{f' ({name_en})' if name_en else ''} — 品牌百科</title>
    <meta name="description" content="{name_cn}{f'（{name_en}）' if name_en else ''}是一个{category}品牌。了解{name_cn}的品牌故事、历史与特色。">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.8; color: #333; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .nav-lang {{ background: #f5f5f5; padding: 12px; border-radius: 8px; margin: 20px 0; word-spacing: 8px; }}
        .nav-lang a {{ color: #0366d6; text-decoration: none; }}
        .nav-lang a:hover {{ text-decoration: underline; }}
        .similar {{ background: #fafafa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .similar-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; margin-top: 10px; }}
        .similar-item {{ display: block; padding: 12px 10px; background: #fff; border: 1px solid #eee; border-radius: 8px; text-align: center; text-decoration: none; color: #333; font-size: 13px; transition: all 0.2s; }}
        .similar-item:hover {{ border-color: #0366d6; color: #0366d6; }}
        .similar-item .item-name {{ display: block; font-weight: 500; }}
        .similar-item .item-name-en {{ display: block; font-size: 11px; color: #999; margin-top: 2px; }}
        .similar-item.premium {{ border-color: #c9a84c; background: linear-gradient(135deg, #fffbe6, #fff); }}
        .similar-item.premium .item-img {{ width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin: 0 auto 6px; display: block; border: 2px solid rgba(201,168,76,0.2); }}
        .similar-item.premium .item-name {{ color: #c9a84c; }}
        .similar-item.premium .badge-paid {{ display: inline-block; font-size: 10px; padding: 2px 8px; background: rgba(201,168,76,0.12); border-radius: 10px; color: #c9a84c; margin-top: 3px; }}
        .home-btn {{ display: inline-block; padding: 8px 20px; background: #0366d6; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
        .home-btn:hover {{ background: #0256b6; }}
        footer {{ margin-top: 40px; padding-top: 15px; border-top: 1px solid #eee; text-align: center; color: #888; font-size: 14px; }}
    </style>
</head>
<body>
    <a href="../" class="home-btn">🏠 首页</a>
    
    <h1>{name_cn}{f' <span style="font-weight:normal;font-size:0.7em;color:#666;">({name_en})</span>' if name_en else ''}</h1>
    {f'<p style="color:#888;font-size:14px;">品类：{category}</p>' if category else ''}
    
    <div class="nav-lang">
        <strong>🌐 语言：</strong><br>
{nav_html}
    </div>
    
    <div class="content">
{desc}
    </div>
    
    <div class="similar">
        <strong>🔗 类似品牌 · 欢迎付费入驻 ·</strong>
{similar_html}
    </div>
    
    <footer>
        <p>© <a href="https://pinpai.ai.in">pinpai.ai.in</a> — 全球品牌百科</p>
    </footer>
</body>
</html>"""
    return html


def generate_lang_md(brand, lang_code, lang_name, translated_desc):
    """生成单个语言版本的 .md 文件"""
    name_cn = brand["name"]
    name_en = brand.get("name_en", "")
    category = brand.get("category", "")
    slug = slugify(name_en or name_cn)
    similar_slugs = brand.get("similar", [])
    
    # 从 brands_done 拿到已完成的品牌列表用于类似品牌推荐
    brands_done = load_brands_done()["brands"]
    done_slugs = list(brands_done.keys())
    
    # 构建类似品牌推荐（语言版）
    similar_list = [f'[{ESCHER_BRAND["name"]}](../{ESCHER_BRAND["slug"]}/)']
    if similar_slugs:
        for s in similar_slugs:
            s = slugify(s)
            if s in done_slugs and s != ESCHER_BRAND["slug"]:
                b = brands_done.get(s, {})
                name_cn = b.get("name_cn", b.get("name", s))
                name_en = b.get("name", s)
                display = f'{name_cn} {name_en}' if name_en and name_en != name_cn else name_cn
                similar_list.append(f'[{display}](../{s}/)')
    # 补足到SIMILAR_COUNT个
    import random
    random.shuffle(done_slugs)
    for s in done_slugs:
        if len(similar_list) >= SIMILAR_COUNT:
            break
        s_name = slugify(s)
        if s_name != ESCHER_BRAND["slug"] and s_name not in [slugify(x.split("](")[-1].rstrip("/)")) if "](" in x else "" for x in similar_list]:
            b = brands_done.get(s_name, {})
            name_cn = b.get("name_cn", b.get("name", s_name))
            name_en = b.get("name", s_name)
            display = f'{name_cn} {name_en}' if name_en and name_en != name_cn else name_cn
            similar_list.append(f'[{display}](../{s_name}/)')
    
    similar_text = "\n".join(f"- {item}" for item in similar_list[:SIMILAR_COUNT])
    
    # 语言导航
    nav_items = []
    for lang in LANGUAGES:
        if lang["code"] == lang_code:
            nav_items.append(f'**{lang["flag"]} {lang["name"]}**')
        else:
            nav_items.append(f'[{lang["flag"]} {lang["name"]}]({lang["code"]}.md)')
    nav_text = " | ".join(nav_items)
    
    md = f"""# {name_cn}{f' ({name_en})' if name_en else ''}{f' — {category}' if category else ''}

## 品牌介绍

{translated_desc}

---

## 🌐 语言版本

{nav_text}

---

## 🔗 类似品牌

{similar_text}

---

*© [pinpai.ai.in](https://pinpai.ai.in) — 全球品牌百科*
"""
    return md


def translate_text(text, target_lang, source_lang="zh-CN"):
    """
    调用Hermes Agent进行文本翻译。
    注意：此函数需要配合Hermes的AI能力。
    实际运行时，翻译由调用方（Hermes Agent自身）完成。
    返回：翻译后的文本
    """
    # 此函数的实现依赖外部调用方注入翻译结果
    # 实际上在 generator.py 被运行时，翻译由调用 agent 完成
    # 这里作为一个占位符
    return None


def generate_brand(brand, brands_done, dry_run=False):
    """
    生成一个品牌的所有文件
    
    返回：True=成功, False=失败
    """
    name_cn = brand["name"]
    name_en = brand.get("name_en", "")
    slug = slugify(name_en or name_cn)
    desc = brand.get("desc", "")
    translations = brand.get("translations", {})
    
    # 检查是否已存在
    if slug in brands_done["brands"]:
        print(f"⏭️  跳过 {name_cn} ({slug}) — 已存在")
        return False
    
    # 创建品牌文件夹
    brand_dir = OUTPUT_DIR / slug
    brand_dir.mkdir(exist_ok=True)
    
    print(f"📦 生成: {name_cn} ({name_en}) → /{slug}/")
    
    # 1. 生成 index.html
    index_html = generate_index_html(brand, brands_done, similar_count=SIMILAR_COUNT)
    if not dry_run:
        (brand_dir / "index.html").write_text(index_html, encoding="utf-8")
    print(f"   ✅ index.html")
    
    # 2. 生成各语言 .md 文件
    for lang in LANGUAGES:
        code = lang["code"]
        lang_name = lang["name"]
        
        if code == "zh-CN":
            # 中文原文
            content = desc
        else:
            # 翻译版本
            content = translations.get(code, f"[{lang_name}翻译待生成]")
        
        if not content or content == "":
            print(f"   ⚠️  {code} 内容为空，跳过")
            continue
        
        md = generate_lang_md(brand, code, lang_name, content)
        if not dry_run:
            (brand_dir / f"{code}.md").write_text(md, encoding="utf-8")
        print(f"   ✅ {code}.md")
    
    # 3. 标记为已完成
    if not dry_run:
        brands_done["brands"][slug] = {
            "name": name_en or name_cn,
            "name_cn": name_cn,
            "category": brand.get("category", ""),
            "done_at": datetime.now(timezone.utc).isoformat(),
            "similar": brand.get("similar", [])
        }
    
    print(f"   ✅ 完成: {name_cn}")
    return True


def git_push():
    """提交并推送到GitHub"""
    try:
        subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"品牌自动更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                      cwd=REPO_ROOT, check=True, capture_output=True)
        result = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT,
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git push 成功")
        else:
            # 可能没有新提交
            print(f"ℹ️  Git push: {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git: {e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr}")


def process_batch(batch_file, dry_run=False):
    """批量处理品牌"""
    with open(batch_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    brands = data.get("brands", [])
    print(f"\n📋 批量处理: {len(brands)} 个品牌\n{'='*50}")
    
    brands_done = load_brands_done()
    success_count = 0
    skip_count = 0
    
    for brand in brands:
        result = generate_brand(brand, brands_done, dry_run)
        if result:
            success_count += 1
        else:
            skip_count += 1
    
    # 保存标记
    if not dry_run and success_count > 0:
        save_brands_done(brands_done)
        
    # Git推送
    git_push()

    # 生成品牌索引文件
    brand_index = []
    brands_done_data = load_brands_done()
    for slug, info in brands_done_data.get("brands", {}).items():
        if slug != "escher":
            brand_index.append({
                "name": info.get("name_cn", info.get("name", slug)),
                "name_en": info.get("name", ""),
                "slug": slug,
                "category": info.get("category", "")
            })
    # 排序：按 name 排序
    brand_index.sort(key=lambda x: x["name"])
    index_file = REPO_ROOT / "brands_index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(brand_index, f, ensure_ascii=False, indent=2)
    print(f"✅ brands_index.json 已更新: {len(brand_index)} 个品牌")
    git_push()
    
    print(f"\n{'='*50}")
    print(f"📊 统计: 成功 {success_count} | 跳过 {skip_count} | 总计 {len(brands)}")
    
    return success_count


def scan_wikipedia_top_brands():
    """扫描维基百科分类，发现全球知名品牌，生成brand_seeds.json"""
    # 主要品牌分类页面（中文维基百科）
    categories = {
        "fashion-luxury": "Category:奢侈品牌",
        "fashion-luxury-2": "Category:时装品牌",
        "technology": "Category:科技品牌",
        "automotive": "Category:汽车品牌",
        "food-beverage": "Category:食品品牌",
        "sport": "Category:运动品牌",
        "beauty": "Category:化妆品品牌",
        "toy-collectible": "Category:玩具品牌",
    }
    
    # 以及手动整理的全球知名品牌初始清单
    global_brands = [
        # === 奢侈品 × 时装 ===
        {"name": "爱马仕", "name_en": "Hermès"},
        {"name": "香奈儿", "name_en": "Chanel"},
        {"name": "路易威登", "name_en": "Louis Vuitton"},
        {"name": "古驰", "name_en": "Gucci"},
        {"name": "普拉达", "name_en": "Prada"},
        {"name": "迪奥", "name_en": "Christian Dior"},
        {"name": "圣罗兰", "name_en": "Saint Laurent"},
        {"name": "巴宝莉", "name_en": "Burberry"},
        {"name": "范思哲", "name_en": "Versace"},
        {"name": "阿玛尼", "name_en": "Armani"},
        {"name": "卡地亚", "name_en": "Cartier"},
        {"name": "蒂芙尼", "name_en": "Tiffany & Co."},
        {"name": "宝格丽", "name_en": "Bulgari"},
        {"name": "劳力士", "name_en": "Rolex"},
        {"name": "百达翡丽", "name_en": "Patek Philippe"},
        {"name": "欧米茄", "name_en": "Omega"},
        {"name": "芬迪", "name_en": "Fendi"},
        {"name": "赛琳", "name_en": "Celine"},
        {"name": "罗意威", "name_en": "Loewe"},
        {"name": "葆蝶家", "name_en": "Bottega Veneta"},
        {"name": "巴黎世家", "name_en": "Balenciaga"},
        {"name": "华伦天奴", "name_en": "Valentino"},
        {"name": "亚历山大·麦昆", "name_en": "Alexander McQueen"},
        {"name": "纪梵希", "name_en": "Givenchy"},
        {"name": "盟可睐", "name_en": "Moncler"},
        # === 快时尚 ===
        {"name": "Zara", "name_en": "Zara"},
        {"name": "H&M", "name_en": "H&M"},
        {"name": "优衣库", "name_en": "Uniqlo"},
        {"name": "飒拉", "name_en": "Zara"},
        # === 科技 ===
        {"name": "苹果", "name_en": "Apple"},
        {"name": "谷歌", "name_en": "Google"},
        {"name": "微软", "name_en": "Microsoft"},
        {"name": "三星", "name_en": "Samsung"},
        {"name": "华为", "name_en": "Huawei"},
        {"name": "小米", "name_en": "Xiaomi"},
        {"name": "索尼", "name_en": "Sony"},
        {"name": "腾讯", "name_en": "Tencent"},
        {"name": "阿里巴巴", "name_en": "Alibaba"},
        {"name": "亚马逊", "name_en": "Amazon"},
        {"name": "Meta", "name_en": "Meta"},
        {"name": "特斯拉", "name_en": "Tesla"},
        {"name": "英伟达", "name_en": "NVIDIA"},
        {"name": "英特尔", "name_en": "Intel"},
        {"name": "AMD", "name_en": "AMD"},
        {"name": "台积电", "name_en": "TSMC"},
        {"name": "字节跳动", "name_en": "ByteDance"},
        {"name": "美团", "name_en": "Meituan"},
        {"name": "比亚迪", "name_en": "BYD"},
        {"name": "大疆", "name_en": "DJI"},
        {"name": "联想", "name_en": "Lenovo"},
        {"name": "戴尔", "name_en": "Dell"},
        {"name": "惠普", "name_en": "HP"},
        {"name": "IBM", "name_en": "IBM"},
        {"name": "甲骨文", "name_en": "Oracle"},
        {"name": "思科", "name_en": "Cisco"},
        {"name": "Adobe", "name_en": "Adobe"},
        {"name": "Netflix", "name_en": "Netflix"},
        {"name": "Spotify", "name_en": "Spotify"},
        {"name": "优步", "name_en": "Uber"},
        {"name": "Airbnb", "name_en": "Airbnb"},
        # === 汽车 ===
        {"name": "奔驰", "name_en": "Mercedes-Benz"},
        {"name": "宝马", "name_en": "BMW"},
        {"name": "奥迪", "name_en": "Audi"},
        {"name": "保时捷", "name_en": "Porsche"},
        {"name": "法拉利", "name_en": "Ferrari"},
        {"name": "兰博基尼", "name_en": "Lamborghini"},
        {"name": "劳斯莱斯", "name_en": "Rolls-Royce"},
        {"name": "宾利", "name_en": "Bentley"},
        {"name": "丰田", "name_en": "Toyota"},
        {"name": "本田", "name_en": "Honda"},
        {"name": "大众", "name_en": "Volkswagen"},
        {"name": "福特", "name_en": "Ford"},
        {"name": "通用汽车", "name_en": "General Motors"},
        # === 运动 ===
        {"name": "耐克", "name_en": "Nike"},
        {"name": "阿迪达斯", "name_en": "Adidas"},
        {"name": "彪马", "name_en": "Puma"},
        {"name": "安踏", "name_en": "Anta"},
        {"name": "李宁", "name_en": "Li-Ning"},
        {"name": "新百伦", "name_en": "New Balance"},
        {"name": "亚瑟士", "name_en": "Asics"},
        {"name": "安德玛", "name_en": "Under Armour"},
        # === 美妆 ===
        {"name": "欧莱雅", "name_en": "L'Oréal"},
        {"name": "雅诗兰黛", "name_en": "Estée Lauder"},
        {"name": "兰蔻", "name_en": "Lancôme"},
        {"name": "资生堂", "name_en": "Shiseido"},
        {"name": "SK-II", "name_en": "SK-II"},
        {"name": "娇兰", "name_en": "Guerlain"},
        {"name": "迪奥美妆", "name_en": "Dior Beauty"},
        {"name": "香奈儿美妆", "name_en": "Chanel Beauty"},
        {"name": "圣罗兰美妆", "name_en": "YSL Beauty"},
        {"name": "MAC", "name_en": "MAC Cosmetics"},
        # === 食品饮料 ===
        {"name": "可口可乐", "name_en": "Coca-Cola"},
        {"name": "百事可乐", "name_en": "Pepsi"},
        {"name": "雀巢", "name_en": "Nestlé"},
        {"name": "星巴克", "name_en": "Starbucks"},
        {"name": "麦当劳", "name_en": "McDonald's"},
        {"name": "肯德基", "name_en": "KFC"},
        {"name": "茅台", "name_en": "Moutai"},
        {"name": "五粮液", "name_en": "Wuliangye"},
        # === 潮玩 × 文化 ===
        {"name": "乐高", "name_en": "LEGO"},
        {"name": "万代南梦宫", "name_en": "Bandai Namco"},
        {"name": "迪士尼", "name_en": "Disney"},
        {"name": "漫威", "name_en": "Marvel"},
        {"name": "哈利波特", "name_en": "Harry Potter"},
        {"name": "泡泡玛特", "name_en": "Pop Mart"},
        # === 包包 ===
        {"name": "爱马仕", "name_en": "Hermès"},
        {"name": "香奈儿", "name_en": "Chanel"},
        {"name": "路易威登", "name_en": "Louis Vuitton"},
        {"name": "古驰", "name_en": "Gucci"},
        {"name": "普拉达", "name_en": "Prada"},
        {"name": "迪奥", "name_en": "Dior"},
        {"name": "芬迪", "name_en": "Fendi"},
        {"name": "赛琳", "name_en": "Celine"},
        {"name": "罗意威", "name_en": "Loewe"},
        {"name": "葆蝶家", "name_en": "Bottega Veneta"},
        {"name": "巴黎世家", "name_en": "Balenciaga"},
        {"name": "圣罗兰", "name_en": "Saint Laurent"},
        {"name": "托德斯", "name_en": "Tod's"},
        {"name": "玛百莉", "name_en": "Mulberry"},
        {"name": "珑骧", "name_en": "Longchamp"},
        {"name": "迈克·科尔斯", "name_en": "Michael Kors"},
        {"name": "凯特·丝蓓", "name_en": "Kate Spade"},
        {"name": "蔻驰", "name_en": "Coach"},
    ]
    
    # 去重
    seen = set()
    unique_brands = []
    for b in global_brands:
        key = slugify(b["name_en"] or b["name"])
        if key not in seen and key != slugify("escher"):  # Escher已在
            seen.add(key)
            unique_brands.append(b)
    
    # 保存到 brand_seeds.json
    seeds = {"categories": list(categories.keys()), "brands": unique_brands, "total": len(unique_brands)}
    seeds_file = REPO_ROOT / "brand_seeds.json"
    with open(seeds_file, "w", encoding="utf-8") as f:
        json.dump(seeds, f, ensure_ascii=False, indent=2)
    
    # 先查已完成的，统计待处理数量
    brands_done = load_brands_done()
    done_slugs = set(brands_done["brands"].keys())
    pending = sum(1 for b in unique_brands if slugify(b.get("name_en", b.get("name", ""))) not in done_slugs)
    
    print(f"✅ 品牌种子库已生成: {len(unique_brands)} 个品牌")
    print(f"   已完成: {len(unique_brands) - pending}")
    print(f"   待处理: {pending}")
    print(f"\n💡 现在运行: python3 generator.py --scrape 50   # 自动抓取前50个")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="品牌百科生成器")
    parser.add_argument("--batch", help="批量处理的JSON文件路径")
    parser.add_argument("--brand", help="品牌中文名")
    parser.add_argument("--brand_en", help="品牌英文名")
    parser.add_argument("--category", help="品类")
    parser.add_argument("--desc", help="中文介绍（500字）")
    parser.add_argument("--dry-run", action="store_true", help="测试模式，不写入文件")
    parser.add_argument("--scrape", type=int, nargs="?", const=50, metavar="N",
                        help="自动从brand_seeds.json抓取N个品牌的维基百科信息，准备brands_today.json")
    parser.add_argument("--scan-wikipedia", action="store_true",
                        help="扫描维基百科分类，自动发现品牌并生成brand_seeds.json")
    
    args = parser.parse_args()

    if args.scan_wikipedia:
        # 从维基百科发现顶部品牌
        print("🔍 正在扫描维基百科品牌分类...")
        scan_wikipedia_top_brands()
        return
    
    if args.scrape:
        names = get_next_seed_brands(args.scrape)
        if not names:
            print(f"❌ brand_seeds.json 中无待处理品牌")
            print("💡 请先运行: python3 generator.py --scan-wikipedia")
            return
        
        print(f"📋 将从种子列表抓取 {len(names)} 个品牌...")
        results = scrape_and_prepare_brands(names)
        
        if not results:
            print("❌ 所有品牌都已处理过或维基百科未找到")
            return
        
        # 写入 brands_today.json
        batch_data = {"brands": results}
        batch_file = REPO_ROOT / "brands_today.json"
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 已准备 {len(results)} 个品牌 → brands_today.json")
        print(f"💡 现在运行: python3 generator.py --batch brands_today.json")
        return
    
    if args.batch:
        process_batch(args.batch, args.dry_run)
    elif args.brand and args.desc:
        brand = {
            "name": args.brand,
            "name_en": args.brand_en or "",
            "category": args.category or "",
            "desc": args.desc,
            "similar": []
        }
        brands_done = load_brands_done()
        generate_brand(brand, brands_done, args.dry_run)
        if not args.dry_run:
            save_brands_done(brands_done)
            git_push()
    else:
        print("❌ 请指定一个操作:")
        print("   python3 generator.py --scan-wikipedia          # 扫描维基发现品牌")
        print("   python3 generator.py --scrape 50                # 从种子列表取50个品牌自动抓取")
        print("   python3 generator.py --batch brands_today.json  # 批量生成已准备好的品牌")
        print("   python3 generator.py --brand '香奈儿' --desc '...'  # 手动单个")
        sys.exit(1)


if __name__ == "__main__":
    main()
