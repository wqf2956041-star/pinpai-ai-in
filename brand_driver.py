#!/usr/bin/env python3
"""
品牌百科自动驱动脚本 - 由cron每20分钟调用
直接调用 render_all.py 来生成和渲染品牌页面
"""
import csv, json, re, os, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

def get_next_brands(n=3):
    """从master.csv获取下一个待生成的品牌"""
    rows = []
    with open(ROOT / "master.csv", "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    pending = [r for r in rows if r['deployed'] == 'false']
    return pending[:n], rows

def run():
    print("=" * 60)
    from datetime import datetime
    print(f"品牌百科自动推进 - {datetime.now()}")
    print("=" * 60)
    
    pending, all_rows = get_next_brands(3)
    
    if not pending:
        print("✅ 所有品牌已完成！无需再跑")
        return
    
    print(f"\n本轮处理: {len(pending)} 个品牌")
    for b in pending:
        print(f"  📦 {b['name_zh']} ({b['name_en']})")
    
    # 为待处理品牌创建brand.json基础数据
    for brand in pending:
        slug = brand['slug']
        name_en = brand['name_en']
        name_zh = brand['name_zh']
        category = brand['category']
        country = brand['country']
        
        brand_dir = ROOT / slug
        brand_dir.mkdir(exist_ok=True)
        
        data = {
            "slug": slug,
            "names": {"zh-CN": name_zh, "en": name_en},
            "category": category,
            "country": country,
            "founding_year": "",
            "founding_location": "",
            "founder": "",
            "official_website": "",
            "main_business": [category],
            "current_slogan": "",
            "description_zh": f"{name_zh}（{name_en}）是全球知名的{category}品牌。",
            "languages": {
                "zh-CN": "", "en": "", "ja": "", "ko": "",
                "fr": "", "es": "", "de": "", "pt": "", "ru": "", "ar": ""
            },
            "is_premium": False,
            "image_url": "",
            "similar_brands": [
                {"zh": "埃舍尔Escher", "en": "Escher", "slug": "escher", "premium": True}
            ]
        }
        
        bj_path = brand_dir / "brand.json"
        with open(bj_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {slug}/brand.json 创建")
    
    # 调用render_all.py批量渲染
    print("\n🔄 调用 render_all.py 批量渲染...")
    result = subprocess.run(
        [sys.executable, "render_all.py"],
        capture_output=True, text=True, timeout=180, cwd=str(ROOT)
    )
    if result.stdout:
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.stderr:
        print(f"  ⚠️ stderr: {result.stderr[-1000:]}")
    
    print(f"\n  ✅ render_all.py exit_code: {result.returncode}")
    
    # 更新master.csv
    for brand in pending:
        slug = brand['slug']
        for row in all_rows:
            if row['slug'] == slug:
                row['deployed'] = 'true'
    
    with open(ROOT / "master.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)
    
    completed = len(pending)
    remaining = len([r for r in all_rows if r['deployed'] == 'false'])
    print(f"\n{'='*60}")
    print(f"✅ 本轮完成 {completed} 个！剩余 {remaining} 个")
    print(f"{'='*60}")

if __name__ == "__main__":
    run()
