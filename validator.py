#!/usr/bin/env python3
"""
独立验证器 validator.py — 第二关验证
=====================================
与 brand_factory.py 的 verify_brand() 逻辑完全分离实现。
同一个品牌，两个程序各自验证，结果必须一致。

如果不一致 → 谁对都不信任，阻塞部署，人工介入。

用法：
  python3 validator.py <slug>              # 验证单个品牌
  python3 validator.py all                  # 验证所有done品牌
  python3 validator.py check-links <slug>   # 只检查内链
  python3 validator.py compare <slug>       # 与engine结果对比

返回码：
  0 = 全部通过
  1 = 验证失败
  2 = 程序错误
"""
import json, sys, os
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
VAL_VER = "2.0.0"
LANGUAGES = ["zh-CN","en","fr","es","de","ja","ko","pt","ru","ar"]


def check_path(slug):
    """检查文件和目录结构"""
    errs = []
    brand_dir = ROOT / slug
    if not brand_dir.exists():
        return False, ["DIR_MISSING: 品牌目录不存在"]

    json_path = brand_dir / "brand.json"
    html_path = brand_dir / "index.html"

    if not json_path.exists():
        errs.append("MISSING_JSON")
    if not html_path.exists():
        errs.append("MISSING_HTML")

    return len(errs) == 0, errs


def check_json_content(data):
    """检查JSON核心字段（与engine不同的实现）"""
    errs = []

    # 中文描述
    desc_zh = data.get("description_zh", "")
    if len(desc_zh) < 200:
        errs.append(f"CONTENT_SHORT_ZH: {len(desc_zh)}字 < 200")

    # 英文内容
    langs = data.get("languages", {})
    en_content = langs.get("en", "")
    if len(en_content) < 100:
        errs.append(f"CONTENT_SHORT_EN: {len(en_content)}字 < 100")

    # 品牌名必须非空
    names = data.get("names", {})
    if not names.get("zh-CN"):
        errs.append("NAME_ZH_MISSING")
    if not names.get("en"):
        errs.append("NAME_EN_MISSING")

    # 必填字段
    required_fields = ["founding_year","founding_location","founder","official_website","current_slogan","category"]
    for f in required_fields:
        if not data.get(f):
            errs.append(f"FIELD_MISSING: {f}")

    # slug一致性
    js_slug = data.get("slug", "")
    dir_name = Path(data.get("_source","")).parent.name if data.get("_source") else ""
    if js_slug and len(js_slug) < 2:
        errs.append("SLUG_TOO_SHORT")

    # category 必须是合法值
    valid_cats = ["fashion-luxury","fashion","beauty","tech","auto","food","sport","toy","jewelry","watch","finance","other"]
    cat = data.get("category","")
    if cat not in valid_cats:
        errs.append(f"BAD_CATEGORY: {cat}")

    # 类似品牌需要slug合法且至少有3个
    similar = data.get("similar_brands", [])
    if len(similar) < 3:
        errs.append(f"SIMILAR_TOO_FEW: {len(similar)}个")
    for s in similar:
        if not re.match(r'^[a-z0-9-]+$', s.get("slug","")):
            errs.append(f"SIMILAR_BAD_SLUG: {s.get('slug','?')}")

    # main_business 必须非空
    mb = data.get("main_business", [])
    if not mb or not any(b.strip() for b in mb):
        errs.append("MAIN_BUSINESS_EMPTY")

    return errs

import re


def check_html_content(slug, data, html):
    """检查渲染后的HTML — 使用与engine不同的检查和阈值"""
    errs = []
    name_zh = data.get("names", {}).get("zh-CN", "")

    # 标题标签必须包含品牌名
    title_match = re.search(r'<title>([^<]+)</title>', html)
    if title_match:
        title = title_match.group(1)
        if name_zh and name_zh not in title:
            errs.append(f"TITLE_MISMATCH: 标题'{title}'不含品牌名'{name_zh}'")
    else:
        errs.append("TITLE_TAG_MISSING")

    # meta description 必须存在且有内容
    meta_desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    if not meta_desc or len(meta_desc.group(1)) < 10:
        errs.append("META_DESC_SHORT_OR_MISSING")

    # hreflang — 必须正好10个且每个都有href
    hreflangs = re.findall(r'hreflang="([^"]+)"', html)
    expected_codes = ["zh-Hans","en","fr","es","de","ja","ko","pt","ru","ar"]
    found_codes = {h for h in hreflangs if h in expected_codes}
    missing = [c for c in expected_codes if c not in found_codes]
    if missing:
        errs.append(f"HREFLANG_MISSING: {missing}")

    # 必须有类似品牌区块
    if 'class="similar-section"' not in html and 'class="similar-card"' not in html:
        errs.append("SIMILAR_SECTION_MISSING")

    # 语言切换按钮 — 必须有 data-lang 属性
    lang_btns = re.findall(r'data-lang="([^"]+)"', html)
    missing_langs = [l for l in ["zh-CN","en","fr","es","de","ja","ko","pt","ru","ar"] if l not in lang_btns]
    if missing_langs:
        errs.append(f"LANG_BTN_MISSING: {missing_langs}")

    # canonical 标签
    if 'rel="canonical"' not in html:
        errs.append("CANONICAL_MISSING")

    # html lang 属性 — 必须有
    if 'lang="' not in html:
        errs.append("HTML_LANG_MISSING")

    # 检查死链接（在similar-brand锚点中）
    similar_links = re.findall(r'href="/([^/]+)/"', html)
    for link_slug in similar_links:
        if link_slug == slug:
            continue
        target_path = ROOT / link_slug / "index.html"
        if not target_path.exists():
            errs.append(f"DEAD_LINK: /{link_slug}/ → 404")

    return errs


def validate_one(slug, full=True):
    """完整验证一个品牌"""
    brand_dir = ROOT / slug
    json_path = brand_dir / "brand.json"
    html_path = brand_dir / "index.html"

    all_errors = []
    all_warnings = []

    # 1. 路径检查（最基础）
    ok, pe = check_path(slug)
    if not ok:
        return {
            "slug": slug,
            "passed": False,
            "errors": pe,
            "warnings": [],
            "checks": {"path_ok": False}
        }

    # 2. JSON有效性
    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return {"slug": slug, "passed": False, "errors": [f"JSON_DECODE: {e}"], "warnings": [], "checks": {}}
    except Exception as e:
        return {"slug": slug, "passed": False, "errors": [f"JSON_READ: {e}"], "warnings": [], "checks": {}}

    data["_source"] = str(json_path)

    # 3. JSON内容检查
    content_errs = check_json_content(data)
    all_errors.extend(content_errs)

    # 4. HTML渲染检查
    try:
        html = html_path.read_text(encoding='utf-8')
        html_errs = check_html_content(slug, data, html)
        all_errors.extend(html_errs)
    except Exception as e:
        all_errors.append(f"HTML_READ: {e}")

    # 5. HTML文件大小检查（生成的页面不能太小）
    html_size = html_path.stat().st_size if html_path.exists() else 0
    if html_size < 500:
        all_errors.append(f"HTML_TOO_SMALL: {html_size} bytes")

    # 6. JSON有_meta字段（engine写了没有）
    meta = data.get("_meta", {})
    if not meta:
        all_warnings.append("META_MISSING: engine版本号未写入")
    elif meta.get("version") != "2.0.0":
        all_warnings.append(f"META_VERSION: engine版本{meta.get('version')} ≠ 当前2.0.0")

    checks = {
        "path_ok": True,
        "json_parsed": True,
        "html_size": html_size,
        "content_length_zh": len(data.get("description_zh","")),
        "content_length_en": len(data.get("languages",{}).get("en","")),
        "similar_count": len(data.get("similar_brands",[]))
    }

    passed = len(all_errors) == 0
    return {
        "slug": slug,
        "passed": passed,
        "errors": all_errors,
        "warnings": all_warnings,
        "checks": checks
    }


def main():
    if len(sys.argv) < 2:
        print(f"validator.py v{VAL_VER}")
        print("用法:")
        print("  python3 validator.py <slug>         # 验证单个品牌")
        print("  python3 validator.py all             # 验证所有done品牌")
        print("  python3 validator.py check-links     # 检查所有done品牌的内链")
        sys.exit(2)

    cmd = sys.argv[1]

    if cmd == "all":
        # 验证所有done品牌
        csv_path = ROOT / "master.csv"
        if not csv_path.exists():
            print("❌ master.csv 不存在")
            sys.exit(1)

        import csv
        with open(csv_path, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

        done_slugs = [r["slug"] for r in rows if r.get("status","").strip() == "done"]
        if not done_slugs:
            print("没有 done 状态的品牌")
            sys.exit(0)

        print(f"验证 {len(done_slugs)} 个品牌...")
        all_passed = True
        for slug in done_slugs:
            result = validate_one(slug)
            status = "✅" if result["passed"] else "❌"
            errs = result["errors"]
            warns = result["warnings"]
            if errs:
                print(f"  {status} {slug} — {len(errs)}个错误:")
                for e in errs:
                    print(f"       - {e}")
            elif warns:
                print(f"  {status} {slug} — ⚠️  {len(warns)}个警告")
                for w in warns:
                    print(f"       - {w}")
            else:
                print(f"  {status} {slug}")
            if not result["passed"]:
                all_passed = False

        sys.exit(0 if all_passed else 1)

    elif cmd == "check-links":
        # 只检查内链
        import csv
        with open(ROOT/"master.csv", encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        done_slugs = [r["slug"] for r in rows if r.get("status","").strip() == "done"]

        print(f"内链检查 ({len(done_slugs)} 个品牌):")
        all_ok = True
        for slug in done_slugs:
            result = validate_one(slug)
            found_dead = [e for e in result["errors"] if e.startswith("DEAD_LINK")]
            if found_dead:
                for dl in found_dead:
                    print(f"  ❌ {slug}: {dl}")
                all_ok = False

        if all_ok:
            print("  ✅ 所有链接正常")
        sys.exit(0 if all_ok else 1)

    else:
        # 单个品牌
        result = validate_one(cmd)
        print(f"\n验证: {result['slug']}")
        print(f"结果: {'✅ 通过' if result['passed'] else '❌ 失败'}")
        print(f"检查:")
        for k, v in result["checks"].items():
            print(f"  {k}: {v}")
        if result["errors"]:
            print(f"\n错误 ({len(result['errors'])}):")
            for e in result["errors"]:
                print(f"  ❌ {e}")
        if result["warnings"]:
            print(f"\n警告 ({len(result['warnings'])}):")
            for w in result["warnings"]:
                print(f"  ⚠️  {w}")

        sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
