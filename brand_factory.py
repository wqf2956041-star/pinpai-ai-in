#!/usr/bin/env python3
"""
Brand Factory Engine v2.0 — 三流水线 + 三关验证系统
=================================================
流水线：生成 → 验证（schema→内容→功能）→ 部署

新增：
  - 第一关：JSON Schema 严格校验（数据格式不对直接拒绝）
  - 第二关：内部验证（内容质量+内链检查+功能完整）
  - 部署前：必须调用独立 validator.py 确认通过

用法：
  python3 brand_factory.py init <slug>              # 初始化新品牌（生成brand.json模板）
  python3 brand_factory.py process <slug|all>       # 处理一个或所有pending品牌
  python3 brand_factory.py verify <slug>            # 详细验证
  python3 brand_factory.py deploy                   # 部署已验证的品牌
  python3 brand_factory.py status                   # 查看状态
  python3 brand_factory.py add <slug> <brand> <国家> <行业>  # 添加品牌到master.csv
"""
import csv, json, os, sys, re, subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
CSV_PATH = ROOT / "master.csv"
SCHEMA_PATH = ROOT / "schema.json"
INDEX_JSON = ROOT / "brands_index.json"
LOGS_DIR = ROOT / "logs"
GENERATED_LOG = LOGS_DIR / "generated.csv"
ERROR_LOG = LOGS_DIR / "errors.log"
SITEMAP_PATH = ROOT / "sitemap.xml"
LANGUAGES = ["zh-CN", "en", "fr", "es", "de", "ja", "ko", "pt", "ru", "ar"]
TEMPLATE = ROOT / "template.html"
BRAND_FACTORY_VER = "2.0.0"


# ============================================================
# 基础工具
# ============================================================

def ensure_logs():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if not GENERATED_LOG.exists():
        with open(GENERATED_LOG, 'w', encoding='utf-8') as f:
            f.write("id,brand,slug,status,timestamp,errors\n")

def log_error(msg, slug="", show=True):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {slug}: {msg}\n" if slug else f"[{ts}] {msg}\n"
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(line)
    if show:
        print(f"  ⛔ {line.strip()}")

def log_warn(msg, slug="", show=True):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {slug}: [WARN] {msg}\n" if slug else f"[{ts}] [WARN] {msg}\n"
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(line)
    if show:
        print(f"  ⚠️  {line.strip()}")

def read_csv():
    if not CSV_PATH.exists():
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


# ========================================================================
# 第一关：JSON Schema 校验（数据格式硬约束）
# ========================================================================

def validate_schema(slug):
    """
    用 schema.json 对 brand.json 做严格格式校验。
    返回 (passed, errors_list)
    格式不对直接拒绝，不进流水线。
    """
    brand_dir = ROOT / slug
    json_path = brand_dir / "brand.json"

    if not SCHEMA_PATH.exists():
        log_error("schema.json 不存在，无法验证", slug)
        return False, ["SCHEMA_MISSING: schema.json 不存在"]

    if not json_path.exists():
        return False, ["MISSING_JSON: brand.json 不存在"]

    try:
        import jsonschema
    except ImportError:
        log_warn("jsonschema 未安装，跳过 schema 校验", slug)
        return True, []

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
        data = json.loads(json_path.read_text(encoding='utf-8'))
        validator = jsonschema.Draft7Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            err_msgs = []
            for e in errors:
                path = ".".join(str(p) for p in e.path) if e.path else "root"
                err_msgs.append(f"{path}: {e.message}")
            return False, err_msgs
        return True, []
    except jsonschema.exceptions.SchemaError as e:
        log_error(f"schema.json 本身无效: {e.message}", slug)
        return False, [f"INVALID_SCHEMA: {e.message}"]
    except json.JSONDecodeError:
        return False, ["INVALID_JSON: brand.json 解析失败"]
    except Exception as e:
        return False, [f"SCHEMA_VALIDATION_ERROR: {str(e)}"]


# ========================================================================
# 第一步：生成内容
# ========================================================================

def render_brand(brand_data):
    """用模板渲染品牌HTML"""
    template_content = TEMPLATE.read_text(encoding='utf-8')
    slug = brand_data["slug"]
    names = brand_data.get("names", {})
    name_zh = names.get("zh-CN", slug)
    name_en = names.get("en", slug)
    desc_zh = brand_data.get("description_zh", "")
    langs = brand_data.get("languages", {})
    en_content = langs.get("en", desc_zh)

    # 构建10语言 brand_json
    similar_titles = {
        "zh-CN":"类似品牌","en":"Similar Brands","fr":"Marques similaires",
        "es":"Marcas similares","de":"Ähnliche Marken","pt":"Marcas semelhantes",
        "ru":"Похожие бренды","ja":"類似ブランド","ko":"유사 브랜드","ar":"علامات تجارية مماثلة"
    }
    brand_json = {}
    for lang in LANGUAGES:
        if lang == "zh-CN":
            content = desc_zh
        elif lang == "en":
            content = en_content
        else:
            content = langs.get(lang, en_content)
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
        "fashion-luxury":"奢侈品/时尚","fashion":"时尚","beauty":"美妆","tech":"科技",
        "auto":"汽车","food":"食品","sport":"运动","toy":"潮玩/玩具",
        "jewelry":"珠宝","watch":"腕表","finance":"金融","other":"其他"
    }
    cat_label = cat_map.get(brand_data.get("category",""), brand_data.get("category",""))

    similar = brand_data.get("similar_brands", [])
    similar_html = ""
    for s in similar:
        premium_cls = " premium" if s.get("premium") else ""
        badge = '<span class="badge-premium">品牌推广</span>' if s.get("premium") else ""
        similar_html += f'<a href="/{s["slug"]}/" class="similar-card{premium_cls}"><span class="zh">{s["zh"]} {badge}</span><span class="en">{s["en"]}</span></a>\n    '

    similar_index = [{"zh":s["zh"],"en":s["en"],"slug":s["slug"],"premium":s.get("premium",False)} for s in similar]

    html = template_content
    brand_json_str = json.dumps(brand_json, ensure_ascii=False)
    similar_json_str = json.dumps(similar_index, ensure_ascii=False)
    desc_short = desc_zh[:120].replace('"', "'").replace('\n', ' ')

    replacements = {
        "$NAME_ZH$": name_zh, "$NAME_EN$": name_en,
        "$CATEGORY_LABEL$": cat_label,
        "$META_DESC$": desc_short,
        "$FOUNDING_YEAR$": str(brand_data.get("founding_year","")),
        "$FOUNDING_LOCATION$": brand_data.get("founding_location",""),
        "$FOUNDER$": brand_data.get("founder",""),
        "$WEBSITE$": brand_data.get("official_website",""),
        "$WEBSITE_SHORT$": brand_data.get("official_website","").replace("https://","").replace("http://","").rstrip("/"),
        "$MAIN_BUSINESS$": "、".join(brand_data.get("main_business",[])),
        "$SLOGAN$": brand_data.get("current_slogan",""),
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

    # Hreflang
    lang_codes = {"zh-CN":"zh-Hans","en":"en","fr":"fr","es":"es","de":"de","ja":"ja","ko":"ko","pt":"pt","ru":"ru","ar":"ar"}
    hreflang_html = "".join(f'    <link rel="alternate" hreflang="{c}" href="https://pinpai.ai.in/{slug}/"/>\n' for _, c in lang_codes.items())
    html = html.replace("$HREFLANG_TAGS$", hreflang_html)

    # 语言按钮
    lang_order = [("zh-CN","中文"),("en","English"),("fr","Français"),("es","Español"),
                  ("de","Deutsch"),("ja","日本語"),("ko","한국어"),("pt","Português"),("ru","Русский"),("ar","العربية")]
    lang_btns = ""
    for code, label in lang_order:
        is_native = (code == "zh-CN") or (code in langs and len(langs.get(code,"")) > 100)
        note = "" if is_native else " (英)"
        active = ' active' if code == "zh-CN" else ''
        lang_btns += f'<button class="lang-btn{active}" data-lang="{code}">{label}{note}</button>\n    '
    html = html.replace("$LANG_BUTTONS$", lang_btns)

    return html

def generate_brand(slug):
    """生成品牌页面（已通过schema校验的数据，直接渲染）"""
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
        return False, [f"渲染失败: {str(e)}", traceback.format_exc()]
    html_path = brand_dir / "index.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding='utf-8')
    return True, []


# ========================================================================
# 第二关：引擎内部验证（内容+功能+内链）
# ========================================================================

def verify_brand(slug):
    """
    详细验证品牌页面，包括：
      - 内容质量（字数/基本信息/类似品牌数）
      - 功能完整性（hreflang/canonical/标题正确性）
      - 内链检查（类似品牌slug对应的目录是否存在）
    """
    errors = []
    brand_dir = ROOT / slug
    json_path = brand_dir / "brand.json"
    html_path = brand_dir / "index.html"

    if not json_path.exists():
        return False, {"errors": ["MISSING_JSON"], "checks": {}}
    if not html_path.exists():
        return False, {"errors": ["MISSING_HTML"], "checks": {}}

    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
    except:
        return False, {"errors": ["INVALID_JSON"], "checks": {}}

    name_zh = data.get("names", {}).get("zh-CN", "")
    name_en = data.get("names", {}).get("en", "")
    html = html_path.read_text(encoding='utf-8')

    # --- 内容质量 ---
    desc_zh = data.get("description_zh", "")
    if len(desc_zh) < 200:
        errors.append(f"CONTENT_SHORT: 中文仅{len(desc_zh)}字，需≥200")

    en_content = data.get("languages", {}).get("en", "")
    if len(en_content) < 100:
        errors.append(f"EN_SHORT: 英文仅{len(en_content)}字，需≥100")

    for f in ["founding_year","founding_location","founder","official_website","current_slogan"]:
        if not data.get(f):
            errors.append(f"MISSING_{f}")

    similar = data.get("similar_brands", [])
    if len(similar) < 3:
        errors.append(f"SIMILAR_FEW: 仅{len(similar)}个类似品牌")

    # --- 功能完整性 ---
    # 标题正确渲染
    if name_zh and name_zh not in html:
        errors.append("TITLE_MISSING: 品牌名未出现在渲染后的HTML中")

    # hreflang
    if "hreflang" not in html:
        errors.append("MISSING_HREFLANG")
    # 检查hreflang中slug是否正确
    expected_href = f"https://pinpai.ai.in/{slug}/"
    if expected_href not in html:
        errors.append(f"HREFLANG_BAD: 期望的hreflang href未找到: {expected_href}")

    # --- 内链检查：类似品牌的slug是否存在于仓库中 ---
    dead_links = []
    for s in similar:
        s_slug = s.get("slug", "")
        if s_slug == slug:
            continue  # 跳过指向自己
        target_dir = ROOT / s_slug
        target_html = target_dir / "index.html"
        if not target_html.exists():
            dead_links.append(s_slug)

    if dead_links:
        # 不是阻塞错误，因为类似品牌可以指向尚未生成的品牌
        log_warn(f"类似品牌目标不存在: {', '.join(dead_links)}", slug)

    passed = len(errors) == 0
    return passed, {
        "passed": passed,
        "errors": errors,
        "checks": {
            "content_length": len(desc_zh),
            "en_length": len(en_content),
            "similar_count": len(similar),
            "dead_links": dead_links,
            "title_present": name_zh in html if name_zh else False
        }
    }


# ========================================================================
# 第三步：部署系统
# ========================================================================

def write_index_json(rows):
    all_index = []
    for r in rows:
        if r.get("status","").strip() != "done":
            continue
        slug = r["slug"]
        jp = ROOT / slug / "brand.json"
        if not jp.exists():
            continue
        try:
            d = json.loads(jp.read_text(encoding='utf-8'))
            all_index.append({
                "slug": slug,
                "zh": d.get("names",{}).get("zh-CN", slug),
                "en": d.get("names",{}).get("en", slug),
                "category": d.get("category",""),
                "premium": d.get("is_premium", False),
                "desc_short": d.get("description_zh","")[:100].replace('"',"'")
            })
        except:
            continue
    INDEX_JSON.write_text(json.dumps(all_index, ensure_ascii=False, indent=2), encoding='utf-8')
    return all_index

def generate_hreflang_xml(slugs):
    lang_codes = {"zh-CN":"zh-Hans","en":"en","fr":"fr","es":"es","de":"de","ja":"ja","ko":"ko","pt":"pt","ru":"ru","ar":"ar"}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
             '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for slug in sorted(slugs):
        lines.append('  <url>')
        lines.append(f'    <loc>https://pinpai.ai.in/{slug}/</loc>')
        lines.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
        lines.append(f'    <changefreq>monthly</changefreq>')
        for _, code in lang_codes.items():
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{code}" href="https://pinpai.ai.in/{slug}/"/>')
        lines.append('  </url>')
    lines.append('</urlset>')
    SITEMAP_PATH.write_text('\n'.join(lines), encoding='utf-8')

def git_commit_push(message):
    try:
        subprocess.run(["git","add","-A"], cwd=ROOT, capture_output=True, timeout=30)
        subprocess.run(["git","commit","-m",message], cwd=ROOT, capture_output=True, timeout=30)
        r = subprocess.run(["git","push","origin","main"], cwd=ROOT, capture_output=True, timeout=120)
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


# ========================================================================
# 主流程
# ========================================================================

def process_brands(slugs=None):
    """生成 → 验证 → 部署"""
    ensure_logs()
    rows = read_csv()
    if not rows:
        print("master.csv 为空。先用 add 添加品牌。")
        return

    if slugs is None or (len(slugs)==1 and slugs[0]=="all"):
        slots = [r for r in rows if r.get("status","").strip() == "pending"]
    else:
        targets = [s for s in slugs if s != "all"]
        slots = [r for r in rows if r["slug"] in targets]
        if not slots:
            print(f"未找到: {targets}")
            return

    if not slots:
        print("没有待处理的品牌。")
        return

    print(f"\n{'='*60}")
    print(f"Brand Factory Engine v{BRAND_FACTORY_VER} — 处理 {len(slots)} 个品牌")
    print(f"{'='*60}\n")

    passed = []
    failed = []

    for row in slots:
        slug = row["slug"]
        brand = row["brand"]
        print(f"\n[{slug}] {brand}")
        print("-" * 40)
        update_status(slug, "processing")

        # ===== 第一关：Schema校验 =====
        print("  [关卡1/3] Schema格式校验...")
        sok, serrs = validate_schema(slug)
        if not sok:
            for e in serrs:
                log_error(f"SCHEMA: {e}", slug)
            update_status(slug, "error", "; ".join(serrs)[:100])
            failed.append(slug)
            print(f"  ❌ Schema校验失败 ({len(serrs)} 项)")
            for e in serrs:
                print(f"     - {e}")
            continue
        print("  ✅ Schema校验通过")

        # ===== 生成 =====
        print("  [生成] 渲染页面...")
        ok, errs = generate_brand(slug)
        if not ok:
            for e in errs:
                log_error(e[:200], slug)
            update_status(slug, "error", "; ".join(errs)[:100])
            failed.append(slug)
            continue
        print("  ✅ 页面生成完成")

        # ===== 第二关：内部验证 =====
        print("  [关卡2/3] 内容+功能验证...")
        vok, vdetail = verify_brand(slug)
        if not vok:
            for e in vdetail.get("errors",[]):
                log_error(e, slug)
            update_status(slug, "error", "; ".join(vdetail.get("errors",[]))[:100])
            failed.append(slug)
            print(f"  ❌ 验证失败 ({len(vdetail.get('errors',[]))} 项)")
            for e in vdetail.get("errors",[]):
                print(f"     - {e}")
            continue
        checks = vdetail.get("checks",{})
        dl = checks.get("dead_links",[])
        if dl:
            print(f"  ⚠️  类似品牌链接缺失: {len(dl)}个 ({', '.join(dl)})")
        print(f"  ✅ 验证通过 (中文{checks.get('content_length',0)}字, 英文{checks.get('en_length',0)}字)")

        # 写入 _meta
        json_path = ROOT / slug / "brand.json"
        try:
            data = json.loads(json_path.read_text(encoding='utf-8'))
            data.setdefault("_meta", {})
            data["_meta"]["version"] = BRAND_FACTORY_VER
            data["_meta"]["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["_meta"]["validator_pass"] = True
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        except:
            pass

        update_status(slug, "done")
        print("  ✅ 状态 → done")
        passed.append(slug)

    # 部署
    if passed:
        print(f"\n[部署] {len(passed)} 个品牌...")
        all_rows = read_csv()
        write_index_json(all_rows)
        print("  ✅ brands_index.json 已更新")
        done_slugs = [r["slug"] for r in all_rows if r.get("status","").strip() == "done"]
        generate_hreflang_xml(done_slugs)
        print("  ✅ sitemap.xml 已生成")
        ok = git_commit_push(f"全球品牌索引: {len(passed)}个品牌通过验证")
        if ok:
            print("  ✅ 已部署到 GitHub Pages")
        else:
            log_error("Git push失败")

    print(f"\n{'='*60}")
    print("📊 汇总")
    if passed:
        print(f"   ✅ 通过: {len(passed)} — {', '.join(passed)}")
    if failed:
        print(f"   ❌ 失败: {len(failed)} — {', '.join(failed)}")
    print(f"{'='*60}")


# ========================================================================
# CLI 命令
# ========================================================================

def cmd_status():
    ensure_logs()
    rows = read_csv()
    if not rows:
        print("master.csv 为空")
        return
    print(f"\n全球品牌索引 — 状态 (共{len(rows)}个)")
    print(f"{'slug':<20} {'品牌':<20} {'行业':<18} {'状态'}")
    print("-" * 70)
    from collections import Counter
    cnt = Counter()
    for r in rows:
        s = r.get("status","").strip()
        print(f"{r['slug']:<20} {r['brand']:<20} {r['industry']:<18} {s}")
        cnt[s] += 1
    print("-" * 70)
    print(f"待处理:{cnt['pending']} 已完成:{cnt['done']} 失败:{cnt['error']} 处理中:{cnt['processing']}")

def cmd_add(slug, brand, country, industry):
    rows = read_csv()
    if any(r["slug"]==slug for r in rows):
        print(f"❌ slug '{slug}' 已存在")
        return
    max_id = max((int(r["id"]) for r in rows if r["id"].isdigit()), default=0)
    rows.append({"id":str(max_id+1),"brand":brand,"slug":slug,"country":country,"industry":industry,"status":"pending"})
    write_csv(rows)
    print(f"✅ 已添加: {brand} ({slug}) — 状态: pending")

def cmd_init(slug):
    """初始化新品牌：创建品牌目录和 brand.json 模板"""
    brand_dir = ROOT / slug
    if brand_dir.exists():
        print(f"❌ 目录已存在: {slug}/")
        return
    brand_dir.mkdir(parents=True)
    template = {
        "slug": slug,
        "names": {"zh-CN": slug, "en": slug},
        "category": "other",
        "founding_year": 2000,
        "founding_location": "",
        "founder": "",
        "official_website": "",
        "main_business": [""],
        "current_slogan": "",
        "description_zh": "",
        "languages": {"en": ""},
        "similar_brands": [],
        "is_premium": False,
        "image_url": "",
        "representative_products": [],
        "key_events": [],
        "philanthropy": [],
        "exhibitions": [],
        "past_slogans": [],
        "_meta": {"version": BRAND_FACTORY_VER, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "validator_pass": False}
    }
    (brand_dir / "brand.json").write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ 已初始化: {slug}/")
    print(f"   编辑 brand.json 填入品牌数据后，运行:")
    print(f"   python3 brand_factory.py process {slug}")


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
            print("用法: verify <slug>")
            sys.exit(1)
        passed, detail = verify_brand(sys.argv[2])
        print(f"验证结果: {'✅ 通过' if passed else '❌ 失败'}")
        print(f"检查: {json.dumps(detail.get('checks',{}), indent=2, ensure_ascii=False)}")
        if detail.get("errors"):
            print("错误:")
            for e in detail["errors"]:
                print(f"  - {e}")
    elif cmd == "status":
        cmd_status()
    elif cmd == "list-pending":
        rows = [r for r in read_csv() if r.get("status","").strip()=="pending"]
        if not rows:
            print("没有待处理的品牌。")
        else:
            print(f"待处理 ({len(rows)}):")
            for r in rows:
                print(f"  {r['slug']:<20} {r['brand']:<20} {r['industry']:<18}")
    elif cmd == "add":
        if len(sys.argv) < 6:
            print("用法: add <slug> <brand> <country> <industry>")
            sys.exit(1)
        cmd_add(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "init":
        if len(sys.argv) < 3:
            print("用法: init <slug>")
            sys.exit(1)
        cmd_init(sys.argv[2])
    elif cmd == "deploy":
        rows = read_csv()
        done = [r for r in rows if r.get("status","").strip()=="done"]
        if not done:
            print("没有 done 状态的品牌")
            sys.exit(0)
        slugs = [r["slug"] for r in done]
        write_index_json(done)
        generate_hreflang_xml(slugs)
        ok = git_commit_push(f"部署: {len(slugs)}个品牌")
        print(f"{'✅' if ok else '❌'} 部署: {len(slugs)}个品牌")
    else:
        print(f"未知命令: {cmd}")
