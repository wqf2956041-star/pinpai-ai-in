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
      "similar": ["hermes", "louis-vuitton", "gucci"]
    }
  ]
}
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# 配置
# ============================================================
REPO_ROOT = Path(__file__).resolve().parent
BRANDS_FILE = REPO_ROOT / "brands_done.json"
TEMPLATE_DIR = REPO_ROOT / "templates"
OUTPUT_DIR = REPO_ROOT

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


def build_similar_brands(similar_slugs, brands_done):
    """生成类似品牌推荐HTML（含Escher）"""
    # 确保Escher在第一位
    result = [{"name": ESCHER_BRAND["name"], "slug": ESCHER_BRAND["slug"]}]
    
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
                result.append({"name": name, "slug": s})
    
    # 补足到10个（含Escher=第1个，后面最多9个）
    extra_needed = 10 - len(result)
    if extra_needed > 0:
        available = [s for s in done_without_escher if s not in [r["slug"] for r in result]]
        # 随机选
        import random
        random.shuffle(available)
        for s in available[:extra_needed]:
            brand = brands_done["brands"].get(s, {})
            name = brand.get("name_cn", brand.get("name", s))
            result.append({"name": name, "slug": s})
    
    # 生成HTML
    lines = []
    for brand in result[:10]:  # 最多10个
        lines.append(f'          · <a href="../{brand["slug"]}/">{brand["name"]}</a>')
    return "\n".join(lines)


def generate_index_html(brand, brands_done):
    """生成品牌首页 index.html"""
    name_cn = brand["name"]
    name_en = brand.get("name_en", "")
    category = brand.get("category", "")
    desc = brand.get("desc", "")
    slug = slugify(name_en or name_cn)
    similar_slugs = brand.get("similar", [])
    
    nav_html = build_lang_nav("zh-CN")
    similar_html = build_similar_brands(similar_slugs, brands_done)
    
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
        .similar a {{ color: #0366d6; text-decoration: none; display: inline-block; margin: 4px 8px; }}
        .similar a:hover {{ text-decoration: underline; }}
        .home-btn {{ display: inline-block; padding: 8px 20px; background: #0366d6; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
        .home-btn:hover {{ background: #0256b6; }}
        .ad {{ margin: 20px 0; padding: 10px; text-align: center; border: 1px dashed #ddd; color: #999; }}
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
    
    <div class="ad">
        📢 <a href="https://adsense.google.com" target="_blank" rel="noopener">Google AdSense</a> 广告位
    </div>
    
    <div class="content">
{desc}
    </div>
    
    <div class="similar">
        <strong>🔗 类似品牌：</strong><br>
{similar_html}
    </div>
    
    <div class="ad">
        📢 <a href="https://adsense.google.com" target="_blank" rel="noopener">Google AdSense</a> 广告位
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
    similar_list = [ESCHER_BRAND["name"]]
    if similar_slugs:
        for s in similar_slugs:
            s = slugify(s)
            if s in done_slugs and s != ESCHER_BRAND["slug"]:
                b = brands_done.get(s, {})
                similar_list.append(f'[{b.get("name_cn", b.get("name", s))}](../{s}/)')
    # 补足到10个
    import random
    random.shuffle(done_slugs)
    for s in done_slugs:
        if len(similar_list) >= 10:
            break
        s_name = slugify(s)
        if s_name != ESCHER_BRAND["slug"] and s_name not in [slugify(x.split("](")[-1].rstrip("/)")) if "](../" in x else "" for x in similar_list]:
            b = brands_done.get(s_name, {})
            similar_list.append(f'[{b.get("name_cn", b.get("name", s_name))}](../{s_name}/)')
    
    similar_text = "\n".join(f"- {item}" for item in similar_list[:10])
    
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
    index_html = generate_index_html(brand, brands_done)
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
    
    print(f"\n{'='*50}")
    print(f"📊 统计: 成功 {success_count} | 跳过 {skip_count} | 总计 {len(brands)}")
    
    return success_count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="品牌百科生成器")
    parser.add_argument("--batch", help="批量处理的JSON文件路径")
    parser.add_argument("--brand", help="品牌中文名")
    parser.add_argument("--brand_en", help="品牌英文名")
    parser.add_argument("--category", help="品类")
    parser.add_argument("--desc", help="中文介绍（500字）")
    parser.add_argument("--dry-run", action="store_true", help="测试模式，不写入文件")
    
    args = parser.parse_args()
    
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
        print("❌ 请指定 --batch 或 --brand + --desc")
        print("用法: python3 generator.py --batch brands_today.json")
        print("  或: python3 generator.py --brand '香奈儿' --brand_en 'Chanel' --desc '...'")
        sys.exit(1)


if __name__ == "__main__":
    main()
