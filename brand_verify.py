#!/usr/bin/env python3
"""
品牌百科线上验证脚本
验证已部署的brand页面：检查10种语言内容独立性和长度
CJK语言（zh-CN, ja, ko）阈值800字符，非CJK语言阈值1500字符
用法: python3 brand_verify.py [slug]
"""
import json, sys, urllib.request
from pathlib import Path

LANGUAGES = ["en", "zh-CN", "fr", "es", "de", "ja", "ko", "pt", "ru", "ar"]
CJK_LANGS = {"zh-CN", "ja", "ko"}
MIN_LEN = {"default": 1500, "cjk": 800}
BASE_URL = "https://pinpai.ai.in"

def verify(slug):
    url = f"{BASE_URL}/{slug}/"
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        html = resp.read().decode("utf-8")
    except Exception as e:
        return {"slug": slug, "status": "FAIL", "error": str(e), "details": {}}
    
    # 提取BRAND_DATA
    import re
    m = re.search(r'const BRAND_DATA\s*=\s*({.*?});', html, re.DOTALL)
    if not m:
        return {"slug": slug, "status": "FAIL", "error": "BRAND_DATA not found", "details": {}}
    
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        return {"slug": slug, "status": "FAIL", "error": f"JSON parse: {e}", "details": {}}
    
    langs = data.get("languages", {})
    en_content = langs.get("en", "")
    results = {}
    all_pass = True
    
    for lang in LANGUAGES:
        content = langs.get(lang, "")
        c = len(content)
        is_cjk = lang in CJK_LANGS
        threshold = MIN_LEN["cjk"] if is_cjk else MIN_LEN["default"]
        
        checks = {
            "len_ok": c >= threshold,
            "not_eq_en": content != en_content,
            "has_content": c > 0
        }
        passed = all(checks.values())
        if not passed:
            all_pass = False
        
        results[lang] = {
            "chars": c,
            "threshold": threshold,
            "eq_en": content == en_content,
            "passed": passed
        }
    
    return {
        "slug": slug,
        "status": "PASS" if all_pass else "FAIL",
        "details": results
    }

if __name__ == "__main__":
    slugs = sys.argv[1:] if len(sys.argv) > 1 else ["escher"]
    for slug in slugs:
        r = verify(slug)
        status_icon = "✅" if r["status"] == "PASS" else "❌"
        print(f"{status_icon} {slug}: {r['status']}")
        if r.get("error"):
            print(f"  错误: {r['error']}")
            continue
        for lang, info in r["details"].items():
            icon = "✅" if info["passed"] else "❌"
            eq = " =EN!" if info["eq_en"] else ""
            print(f"  {icon} {lang}: {info['chars']}chars (threshold={info['threshold']}){eq}")
        print()
