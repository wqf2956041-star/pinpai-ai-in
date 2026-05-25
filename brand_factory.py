#!/usr/bin/env python3
"""
Brand Factory Engine — 全球品牌实体索引生产系统
=================================================
三段式流水线：生成 → 验证 → 部署

用法：
  python3 brand_factory.py process <slug|all>    # 处理一个或所有pending品牌
  python3 brand_factory.py verify  <slug>         # 仅验证
  python3 brand_factory.py deploy                 # 部署验证通过的
  python3 brand_factory.py status                 # 查看状态
  python3 brand_factory.py list-pending           # 列出待处理品牌

master.csv 字段：
  id, brand, slug, country, industry, status

status: pending → processing → done (或 error)
"""
import csv, json, os, sys, re, subprocess, shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
CSV_PATH = ROOT / "master.csv"
INDEX_JSON = ROOT / "brands_index.json"
LOGS_DIR = ROOT / "logs"
GENERATED_LOG = LOGS_DIR / "generated.csv"
ERROR_LOG = LOGS_DIR / "errors.log"
SITEMAP_PATH = ROOT / "sitemap.xml"
DEPLOY_LOG = LOGS_DIR / "deploy_status.json"

LANGUAGES = ["zh-CN", "en", "fr", "es", "de", "ja", "ko", "pt", "ru", "ar"]

TEMPLATE = (ROOT / "template.html")
SEARCH_HTML = (ROOT / "search.html")
INDEX_HTML = (ROOT / "index.html")

# ============================================================
# 基础工具
# ============================================================

def ensure_logs():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if not GENERATED_LOG.exists():
        with open(GENERATED_LOG, 'w', encoding='utf-8') as f:
            f.write("id,brand,slug,status,timestamp,errors\n")

def log_error(msg, slug=""):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {slug}: {msg}\n" if slug else f"[{ts}] {msg}\n"
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(line)
    print(f"  ⛔ {line.strip()}")

def log_warning(msg, slug=""):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {slug}: [WARN] {msg}\n" if slug else f"[{ts}] [WARN] {msg}\n"
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(line)
    print(f"  ⚠️  {line.strip()}")

def read_csv():
    """读取 master.csv，返回列表"""
    if not CSV_PATH.exists():
        log_error("master.csv 不存在")
        return []
    with open(CSV_PATH, encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(rows):
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=["id","brand","slug","country","industry","status"])
        w.writeheader()
        w.writerows(rows)

def update_status(slug, new_status, errors=None):
    rows = read_csv()
    for r in rows:
        if r["slug"] == slug:
            r["status"] = new_status
            break
    write_csv(rows)
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    brand = next((r["brand"] for r in rows if r["slug"] == slug), slug)
    with open(GENERATED_LOG, 'a', encoding='utf-8') as f:
        err_str = (errors or "")[:100]
        f.write(f"{slug},{brand},{slug},{new_status},{ts},{err_str}\n")

# ============================================================
# 第一步：生成内容
# ============================================================

def render_brand(brand_data):
    """用模板渲染品牌HTML — 兼容格式：description_zh + languages.en + 其他lang fallback到en"""
    template_content = TEMPLATE.read_text(encoding='utf-8')
    slug = brand_data["slug"]
    names = brand_data.get("names", {})
    name_zh = names.get("zh-CN", slug)
    name_en = names.get("en", slug)

    # 中文内容
    desc_zh = brand_data.get("description_zh", "")
    if not desc_zh:
        desc_zh = brand_data.get("description", "")

    # 英文内容
    langs = brand_data.get("languages", {})
    en_content = langs.get("en", desc_zh)

    # 构建10语言brand_json — 中文用desc_zh，英文用en，其他fallback到英文
    lang_names = {
        "zh-CN": "中文", "en": "English", "fr": "Français",
        "es": "Español", "de": "Deutsch", "ja": "日本語",
        "ko": "한국어", "pt": "Português", "ru": "Русский", "ar": "العربية"
    }
    similar_titles = {
        "zh-CN":"类似品牌", "en":"Similar Brands", "fr":"Marques similaires",
        "es":"Marcas similares", "de":"Ähnliche Marken", "pt":"Marcas semelhantes",
        "ru":"Похожие бренды", "ja":"類似ブランド", "ko":"유사 브랜드", "ar":"علامات تجارية مماثلة"
    }

    brand_json = {}
    for lang in LANGUAGES:
        if lang == "zh-CN":
            content = desc_zh
        elif lang == "en":
            content = en_content
        else:
            content = langs.get(lang, en_content)  # fallback to English

        d = {
            "name": names.get(lang, name_zh if lang == "zh-CN" else name_en),
            "name_en": name_en,
            "founding_year": str(brand_data.get("founding_year", "")),
            "founding_location": brand_data.get("founding_location", ""),
            "founder": brand_data.get("founder", ""),
            "website": brand_data.get("official_website", ""),
            "business": "、".join(brand_data.get("main_business", [])),
            "slogan": brand_data.get("current_slogan", ""),
            "content": content,
            "similar_title": similar_titles.get(lang, "Similar Brands")
        }
        brand_json[lang] = d

    cat_map = {
        "fashion-luxury": "奢侈品/时尚", "fashion": "时尚", "beauty": "美妆",
        "tech": "科技", "auto": "汽车", "food": "食品", "sport": "运动",
        "toy": "潮玩/玩具", "jewelry": "珠宝", "watch": "腕表",
        "finance": "金融", "other": "其他"
    }
    cat_label = cat_map.get(brand_data.get("category", ""), brand_data.get("category", ""))

    similar = brand_data.get("similar_brands", [])
    similar_html = ""
    for s in similar:
        s_zh = s.get("zh", "")
        s_en = s.get("en", "")
        s_slug = s.get("slug", "")
        premium_cls = " premium" if s.get("premium") else ""
        badge = '<span class="badge-premium">品牌推广</span>' if s.get("premium") else ""
        similar_html += f'<a href="/{s_slug}/" class="similar-card{premium_cls}"><span class="zh">{s_zh} {badge}</span><span class="en">{s_en}</span></a>\n    '

    similar_index = []
    for s in similar:
        similar_index.append({"zh": s.get("zh",""), "en": s.get("en",""), "slug": s.get("slug",""), "premium": s.get("premium",False)})

    # 替换变量
    html = template_content
    brand_json_str = json.dumps(brand_json, ensure_ascii=False)
    similar_json_str = json.dumps(similar_index, ensure_ascii=False)
    desc_short = desc_zh[:120].replace('"', "'").replace('\n', ' ')

    replacements = {
        "$NAME_ZH$": name_zh,
        "$NAME_EN$": name_en,
        "$CATEGORY_LABEL$": cat_label,
        "$META_DESC$": desc_short,
        "$FOUNDING_YEAR$": str(brand_data.get("founding_year", "")),
        "$FOUNDING_LOCATION$": brand_data.get("founding_location", ""),
        "$FOUNDER$": brand_data.get("founder", ""),
        "$WEBSITE$": brand_data.get("official_website", ""),
        "$WEBSITE_SHORT$": brand_data.get("official_website","").replace("https://","").replace("http://","").rstrip("/"),
        "$MAIN_BUSINESS$": "、".join(brand_data.get("main_business", [])),
        "$SLOGAN$": brand_data.get("current_slogan", ""),
        "$CONTENT$": desc_zh,
        "$BRAND_JSON$": brand_json_str,
        "$SIMILAR_JSON$": similar_json_str,
        "$SIMILAR_BRANDS$": similar_html,
        "$SIMILAR_TITLE$": "类似品牌",
        "$PREMIUM_CSS$": '<link rel="preload" href="data:,"/>' if brand_data.get("is_premium") else "",
        "$PREMIUM_BADGE$": '<div><span class="premium-label">品牌推广</span></div>' if brand_data.get("is_premium") else ""
    }
    for k, v in replacements.items():
        html = html.replace(k, str(v))

    # 替换 hreflang 部分 — 生成正确链接
    lang_codes = {
        "zh-CN": "zh-Hans", "en": "en", "fr": "fr", "es": "es",
        "de": "de", "ja": "ja", "ko": "ko", "pt": "pt", "ru": "ru", "ar": "ar"
    }
    hreflang_html = ""
    for lang, code in lang_codes.items():
        hreflang_html += f'    <link rel="alternate" hreflang="{code}" href="https://pinpai.ai.in/{slug}/"/>\n'

    html = html.replace("$HREFLANG_TAGS$", hreflang_html)

    # 语言切换按钮（所有语言都显示，但fallback到英文的标记为"英"）
    lang_buttons = ""
    lang_order = [
        ("zh-CN", "中文"), ("en", "English"), ("fr", "Français"), ("es", "Español"),
        ("de", "Deutsch"), ("ja", "日本語"), ("ko", "한국어"),
        ("pt", "Português"), ("ru", "Русский"), ("ar", "العربية")
    ]
    for code, label in lang_order:
        is_native = (code == "zh-CN") or (code in langs and len(langs.get(code, "")) > 100)
        note = "" if is_native else " (英)"
        active = ' active' if code == "zh-CN" else ''
        lang_buttons += f'<button class="lang-btn{active}" data-lang="{code}">{label}{note}</button>\n    '
    html = html.replace("$LANG_BUTTONS$", lang_buttons)

    return html

def generate_brand(slug):
    """生成一个品牌：读取brand.json，渲染HTML，写入文件"""
    brand_dir = ROOT / slug
    json_path = brand_dir / "brand.json"
    if not json_path.exists():
        return False, ["brand.json 不存在"]
    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
    except Exception as e:
        return False, [f"读取brand.json失败: {str(e)}"]
    try:
        html = render_brand(data)
    except Exception as e:
        import traceback
        return False, [f"模板渲染失败: {str(e)}\n{traceback.format_exc()}"]
    html_path = brand_dir / "index.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding='utf-8')
    return True, []

# ============================================================
# 第二步：验证系统
# ============================================================

def verify_brand(slug):
    """验证品牌页面质量"""
    errors = []
    brand_dir = ROOT / slug
    json_path = brand_dir / "brand.json"
    html_path = brand_dir / "index.html"

    if not json_path.exists():
        return False, {"errors": ["MISSING_JSON: brand.json 不存在"], "checks": {"file_exists": False}}
    if not html_path.exists():
        return False, {"errors": ["MISSING_HTML: index.html 不存在"], "checks": {"html_exists": False}}

    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
    except:
        return False, {"errors": ["INVALID_JSON: 解析失败"], "checks": {"valid_json": False}}

    # 核心内容检查（description_zh 必须有）
    desc_zh = data.get("description_zh", data.get("description", ""))
    if len(desc_zh) < 200:
        errors.append(f"CONTENT_SHORT: 中文内容仅{len(desc_zh)}字，需≥200")

    # 英文内容检查
    en_content = data.get("languages", {}).get("en", "")
    if len(en_content) < 100:
        errors.append(f"EN_SHORT: 英文内容仅{len(en_content)}字，需≥100")

    # 基本信息
    for f in ["founding_year", "founding_location", "founder", "official_website", "current_slogan"]:
        if not data.get(f):
            errors.append(f"MISSING_{f}: 缺失{f}")

    # 类似品牌
    similar = data.get("similar_brands", [])
    if len(similar) < 3:
        errors.append(f"SIMILAR_FEW: 仅{len(similar)}个类似品牌，建议≥5")

    # HTML检查
    html = html_path.read_text(encoding='utf-8')
    if "<html" not in html.lower():
        errors.append("INVALID_HTML: 缺少<html>")
    if "hreflang" not in html:
        errors.append("MISSING_HREFLANG: 缺少hreflang标签")

    passed = len(errors) == 0
    return passed, {
        "passed": passed,
        "errors": errors,
        "checks": {
            "json_exists": json_path.exists(),
            "html_exists": html_path.exists(),
            "content_length": len(desc_zh),
            "en_length": len(en_content),
            "similar_count": len(similar)
        }
    }

# ============================================================
# 第三步：部署系统
# ============================================================

def write_index_json(rows):
    """更新 brands_index.json，过滤只保留 status=done 的"""
    all_index = []
    for r in rows:
        if r.get("status", "").strip() != "done":
            continue
        slug = r["slug"]
        json_path = ROOT / slug / "brand.json"
        if not json_path.exists():
            continue
        try:
            data = json.loads(json_path.read_text(encoding='utf-8'))
            all_index.append({
                "slug": slug,
                "zh": data.get("names", {}).get("zh-CN", slug),
                "en": data.get("names", {}).get("en", slug),
                "category": data.get("category", ""),
                "premium": data.get("is_premium", False),
                "desc_short": (data.get("description_zh", data.get("description", "")))[:100].replace('"', "'")
            })
        except:
            continue
    INDEX_JSON.write_text(json.dumps(all_index, ensure_ascii=False, indent=2), encoding='utf-8')
    return all_index

def generate_hreflang_xml(slugs):
    """生成sitemap.xml"""
    lang_codes = {
        "zh-CN": "zh-Hans", "en": "en", "fr": "fr", "es": "es",
        "de": "de", "ja": "ja", "ko": "ko", "pt": "pt", "ru": "ru", "ar": "ar"
    }
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
             '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for slug in sorted(slugs):
        lines.append('  <url>')
        lines.append(f'    <loc>https://pinpai.ai.in/{slug}/</loc>')
        lines.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
        lines.append(f'    <changefreq>monthly</changefreq>')
        for lang, code in lang_codes.items():
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{code}" href="https://pinpai.ai.in/{slug}/"/>')
        lines.append('  </url>')
    lines.append('</urlset>')
    SITEMAP_PATH.write_text('\n'.join(lines), encoding='utf-8')

def git_commit_push(message):
    """Git commit + push"""
    try:
        subprocess.run(["git", "add", "-A"], cwd=ROOT, capture_output=True, timeout=30)
        subprocess.run(["git", "commit", "-m", message], cwd=ROOT, capture_output=True, timeout=30)
        r = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, capture_output=True, timeout=120)
        if r.returncode != 0:
            log_error(f"Git push失败: {r.stderr.decode()[:200]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        log_error("Git push超时")
        return False
    except Exception as e:
        log_error(f"Git push异常: {str(e)}")
        return False

# ============================================================
# 主流程：生成 → 验证 → 部署
# ============================================================

def process_brands(slugs=None):
    """处理品牌：生成→验证→部署"""
    ensure_logs()
    rows = read_csv()
    if slugs is None or (len(slugs) == 1 and slugs[0] == "all"):
        slots = [r for r in rows if r.get("status", "").strip() == "pending"]
    else:
        targets = [s for s in slugs if s != "all"]
        slots = [r for r in rows if r["slug"] in targets]
        if not slots:
            print(f"这些slug在master.csv中未找到或状态不匹配: {targets}")
            return

    if not slots:
        print("没有待处理的品牌。")
        return

    print(f"\n{'='*60}")
    print(f"Brand Factory Engine — 处理 {len(slots)} 个品牌")
    print(f"{'='*60}\n")

    passed = []
    failed = []

    for row in slots:
        slug = row["slug"]
        brand = row["brand"]
        print(f"\n[{slug}] {brand}")
        print("-" * 40)
        update_status(slug, "processing")

        # 1. 生成
        print("  [1/3] 生成页面...")
        ok, errs = generate_brand(slug)
        if not ok:
            for e in errs:
                log_error(e[:200], slug)
            update_status(slug, "error", "; ".join(errs)[:100])
            failed.append(slug)
            continue
        print("  ✅ 页面生成完成")

        # 2. 验证
        print("  [2/3] 验证内容...")
        vok, vdetail = verify_brand(slug)
        if not vok:
            for e in vdetail.get("errors", []):
                log_error(e, slug)
            update_status(slug, "error", "; ".join(vdetail.get("errors", []))[:100])
            failed.append(slug)
            print(f"  ❌ 验证失败 ({len(vdetail.get('errors', []))} 项)")
            for e in vdetail.get("errors", []):
                print(f"     - {e}")
            continue
        checks = vdetail.get("checks", {})
        print(f"  ✅ 验证通过 (内容{checks.get('content_length',0)}字, 英文{checks.get('en_length',0)}字)")

        update_status(slug, "done")
        print("  ✅ 状态已更新为 done")
        passed.append(slug)

    # 3. 部署
    if passed:
        print(f"\n[3/3] 部署 {len(passed)} 个品牌...")

        # 更新索引
        all_rows = read_csv()
        write_index_json(all_rows)
        print("  ✅ brands_index.json 已更新")

        # 更新sitemap
        done_slugs = [r["slug"] for r in all_rows if r.get("status","").strip() == "done"]
        generate_hreflang_xml(done_slugs)
        print("  ✅ sitemap.xml 已生成")

        # Git push
        ok = git_commit_push(f"全球品牌索引: {len(passed)}个品牌通过验证")
        if ok:
            print("  ✅ 已部署到 GitHub Pages")
        else:
            log_error("Git push失败，请手动检查")

    # 汇总
    print(f"\n{'='*60}")
    print("📊 处理汇总")
    if passed:
        print(f"   ✅ 通过: {len(passed)} 个 — {', '.join(passed)}")
    if failed:
        print(f"   ❌ 失败: {len(failed)} 个 — {', '.join(failed)}")
    print(f"{'='*60}")

def cmd_status():
    """查看状态"""
    ensure_logs()
    rows = read_csv()
    if not rows:
        print("master.csv 为空")
        return
    print(f"\n全球品牌索引 — 状态 (共 {len(rows)} 个)")
    print(f"{'slug':<20} {'品牌':<20} {'行业':<18} {'状态'}")
    print("-" * 70)
    counts = {"pending": 0, "done": 0, "error": 0, "processing": 0}
    for r in rows:
        s = r.get("status", "").strip()
        print(f"{r['slug']:<20} {r['brand']:<20} {r['industry']:<18} {s}")
        counts[s] = counts.get(s, 0) + 1
    print("-" * 70)
    print(f"待处理: {counts['pending']} | 已完成: {counts['done']} | 失败: {counts['error']} | 处理中: {counts['processing']}")

def cmd_list_pending():
    rows = [r for r in read_csv() if r.get("status", "").strip() == "pending"]
    if not rows:
        print("没有待处理的品牌。")
        return
    print(f"待处理品牌 ({len(rows)}):")
    for r in rows:
        print(f"  {r['slug']:<20} {r['brand']:<20} {r['industry']:<18}")

def cmd_add(slug, brand, country, industry):
    """添加品牌到master.csv"""
    rows = read_csv()
    if any(r["slug"] == slug for r in rows):
        print(f"❌ slug '{slug}' 已存在")
        return
    max_id = max((int(r["id"]) for r in rows if r["id"].isdigit()), default=0)
    rows.append({"id": str(max_id + 1), "brand": brand, "slug": slug, "country": country, "industry": industry, "status": "pending"})
    write_csv(rows)
    print(f"✅ 已添加: {brand} ({slug}) — 状态: pending")

# ============================================================
# CLI 入口
# ============================================================

if __name__ == "__main__":
    ensure_logs()
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "process":
        slugs = sys.argv[2:] if len(sys.argv) > 2 else ["all"]
        process_brands(slugs)
    elif cmd == "verify":
        if len(sys.argv) < 3:
            print("用法: python3 brand_factory.py verify <slug>")
            sys.exit(1)
        slug = sys.argv[2]
        passed, details = verify_brand(slug)
        print(f"验证结果: {'✅ 通过' if passed else '❌ 失败'}")
        print(f"检查项: {json.dumps(details.get('checks',{}), indent=2, ensure_ascii=False)}")
        if details.get("errors"):
            print(f"错误 ({len(details['errors'])}):")
            for e in details["errors"]:
                print(f"  - {e}")
    elif cmd == "status":
        cmd_status()
    elif cmd == "list-pending":
        cmd_list_pending()
    elif cmd == "add":
        if len(sys.argv) < 6:
            print("用法: python3 brand_factory.py add <slug> <brand> <country> <industry>")
            sys.exit(1)
        cmd_add(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "deploy":
        print("部署所有 done 品牌...")
        rows = read_csv()
        done_rows = [r for r in rows if r.get("status","").strip() == "done"]
        if not done_rows:
            print("没有 done 状态的品牌")
            sys.exit(0)
        slugs = [r["slug"] for r in done_rows]
        write_index_json(done_rows)
        generate_hreflang_xml(slugs)
        ok = git_commit_push(f"部署: {len(slugs)}个品牌")
        if ok:
            print(f"✅ 部署完成: {len(slugs)} 个品牌")
    else:
        print(f"未知命令: {cmd}")
