#!/usr/bin/env python3
"""
批量生成5个品牌页面
对每个品牌：读取已写好的brand.json → 渲染index.html → 生成baike图片
"""
import json, sys, os, textwrap
from pathlib import Path

sys.path.insert(0, str(Path("/workspace/pinpai-ai-in")))
from brand_factory import render_brand

ROOT = Path("/workspace/pinpai-ai-in")
SLUGS = ["hermes", "bmw", "sony", "nike", "chanel"]

# 第1步：读取模板
template_path = ROOT / "template.html"
if not template_path.exists():
    print("❌ 模板文件不存在: template.html")
    sys.exit(1)

template_html = template_path.read_text(encoding="utf-8")
print(f"✅ 已读取模板: {len(template_html)} chars")

# 第2步：读取index.html（渲染用）
index_path = ROOT / "index.html"
if not index_path.exists():
    print("❌ index.html 不存在")
    sys.exit(1)

# 第3步：逐一渲染
results = {}
for slug in SLUGS:
    brand_json_path = ROOT / slug / "brand.json"
    if not brand_json_path.exists():
        print(f"❌ {slug}/brand.json 不存在")
        continue
    
    brand_data = json.loads(brand_json_path.read_text(encoding="utf-8"))
    
    # Render
    html = render_brand(brand_data)
    
    # 写入index.html
    output_dir = ROOT / slug
    output_path = output_dir / "index.html"
    output_path.write_text(html, encoding="utf-8")
    
    # 验证：检查BRAND_DATA是否包含10种语言
    if '"zh-CN"' in html and '"en"' in html and '"ar"' in html:
        # 更精确的验证
        import re
        match = re.search(r'const BRAND_DATA\s*=\s*({.*?});', html, re.DOTALL)
        if match:
            bd = json.loads(match.group(1))
            lang_count = len(bd)
            content_ok = all(bd[l].get("content","") for l in bd)
            print(f"  {slug}: {lang_count} languages in BRAND_DATA, content_ok={content_ok}")
            results[slug] = {"langs": lang_count, "ok": content_ok}
        else:
            print(f"  {slug}: ⚠️ BRAND_DATA not found in HTML")
            results[slug] = {"langs": 0, "ok": False}
    else:
        print(f"  {slug}: ⚠️ Missing language keys")
        results[slug] = {"langs": 0, "ok": False}

print("\n========== 结果汇总 ==========")
all_pass = True
for slug, r in results.items():
    status = "✅" if r["ok"] else "❌"
    print(f"  {status} {slug}: {r['langs']} languages")
    if not r["ok"]:
        all_pass = False
print(f"\n{'✅ 全部通过' if all_pass else '❌ 有失败项'}")
if not all_pass:
    sys.exit(1)
