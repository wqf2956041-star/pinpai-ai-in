#!/usr/bin/env python3
"""
重新生成首页 index.html
包含：公告、收录说明、联系方式、完整50品牌列表、免责声明
"""
import json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

with open(ROOT / "brands_index.json", "r") as f:
    brands_data = json.load(f)

# 按行业分组
industry_order = ["fashion-luxury", "fashion", "beauty", "watch", "jewelry", "auto", "tech", "sport", "food", "toy"]
industry_names = {
    "fashion-luxury": "奢侈品/时尚",
    "fashion": "时尚",
    "beauty": "美妆",
    "watch": "腕表",
    "jewelry": "珠宝",
    "auto": "汽车",
    "tech": "科技",
    "sport": "运动",
    "food": "食品",
    "toy": "潮玩/玩具",
}

def make_card_html(b):
    slug = b.get("slug", "")
    zh = b.get("zh", slug)
    en = b.get("en", "")
    cat = b.get("category", "")
    premium = b.get("premium", False)
    badge = '<span class="badge-premium">品牌推广</span>' if premium else ""
    cat_tag = f'<span class="cat-tag">{industry_names.get(cat, cat)}</span>' if cat else ""
    return f'''
        <a href="/{slug}/" class="brand-card">
            <h2>{zh}{badge}</h2>
            <div class="en">{en}</div>
            {cat_tag}
        </a>'''

sections_html = ""
for cat in industry_order:
    cat_brands = [b for b in brands_data if b.get("category") == cat]
    if not cat_brands:
        continue
    title = industry_names.get(cat, cat)
    brands_list = "".join(make_card_html(b) for b in cat_brands)
    sections_html += f'''
    <h2 class="section-title">{title}</h2>
    <div class="brand-grid">{brands_list}</div>'''

brand_count = len(brands_data)

# Build the inline JS brands array
js_brands = []
for b in brands_data:
    js_brands.append({
        "slug": b.get("slug", ""),
        "zh": b.get("zh", b.get("slug", "")),
        "en": b.get("en", ""),
        "category": b.get("category", ""),
        "premium": b.get("premium", False),
    })

html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球品牌索引 — pinpai.ai.in</title>
    <meta name="description" content="全球品牌实体索引系统。全球品牌大全，10种语言呈现。收录全球知名品牌、新兴品牌、中国品牌。欢迎提交品牌收录申请。">
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f8f9fa;color:#222;line-height:1.7}}
        .container{{max-width:960px;margin:0 auto;padding:40px 20px}}
        h1{{font-size:36px;margin-bottom:8px;letter-spacing:-1px}}
        .subtitle{{font-size:16px;color:#777;margin-bottom:30px}}
        
        .announcement{{background:#222;color:#fff;border-radius:10px;padding:20px 24px;margin-bottom:30px}}
        .announcement h2{{font-size:18px;margin-bottom:6px}}
        .announcement p{{font-size:14px;color:#ccc;margin-bottom:4px}}
        .announcement a{{color:#8ab4f8}}
        .announcement .disclaimer{{font-size:13px;color:#999;margin-top:10px;border-top:1px solid #444;padding-top:10px}}
        
        .search-section{{margin-bottom:30px}}
        .search-box{{display:flex;gap:8px;max-width:500px}}
        .search-box input{{flex:1;padding:10px 16px;border:2px solid #ddd;border-radius:8px;font-size:15px;outline:none}}
        .search-box input:focus{{border-color:#222}}
        .search-box button{{padding:10px 20px;background:#222;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:15px}}
        .search-box button:hover{{background:#444}}
        
        .section-title{{font-size:20px;margin:30px 0 12px;padding-bottom:8px;border-bottom:2px solid #222}}
        
        .brand-grid{{display:grid;gap:12px;grid-template-columns:1fr}}
        .brand-card{{display:block;background:#fff;border:1px solid #eee;border-radius:10px;padding:18px 22px;text-decoration:none;transition:all 0.2s}}
        .brand-card:hover{{border-color:#222;transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.08)}}
        .brand-card h2{{font-size:20px;color:#222;margin-bottom:2px}}
        .brand-card .en{{font-size:14px;color:#999;margin-bottom:6px}}
        .brand-card .badge-premium{{display:inline-block;background:#222;color:#fff;font-size:11px;padding:2px 8px;border-radius:3px;margin-left:8px;vertical-align:middle}}
        .brand-card .cat-tag{{display:inline-block;background:#f0f0f0;color:#666;font-size:11px;padding:2px 8px;border-radius:3px;margin-top:6px}}
        .brand-count{{font-size:14px;color:#888;margin-bottom:12px}}
        .footer{{margin-top:50px;padding-top:20px;border-top:1px solid #eee;font-size:13px;color:#999;text-align:center;line-height:2}}
        .footer a{{color:#666}}
        a{{color:#222}}
        a:hover{{color:#555}}
        @media(max-width:600px){{
            h1{{font-size:28px}}
            .search-box{{max-width:100%}}
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>全球品牌索引</h1>
    <p class="subtitle">Global Brand Index · 全球品牌实体索引系统</p>

    <!-- 公告区域 -->
    <div class="announcement">
        <h2>📢 欢迎来到全球品牌索引</h2>
        <p>我们致力于收录全球范围内的品牌信息，不限规模、不限行业、不限国家。</p>
        <p>🔓 任何品牌都可以被收录 — 无论是国际巨头还是新兴品牌。</p>
        <p>📩 提交收录申请或反馈：<a href="mailto:wqf2956041@gmail.com">wqf2956041@gmail.com</a></p>
        <div class="disclaimer">
            ⚠️ 声明：我们只负责收录和展示品牌信息，不参与任何品牌运营、营销或管理。<br>
            品牌内容来源于公开信息，如有异议请联系我们删除或更正。
        </div>
    </div>

    <div class="search-section">
        <div class="search-box">
            <input type="text" id="search-input" placeholder="搜索品牌…" onkeydown="if(event.key==='Enter') searchBrand()">
            <button onclick="searchBrand()">搜索</button>
        </div>
    </div>

    <div class="brand-count">共 {brand_count} 个已收录品牌</div>

    {sections_html}

    <div class="footer">
        <p><a href="https://pinpai.ai.in">全球品牌索引 · pinpai.ai.in</a></p>
        <p>全球品牌大全 · 10种语言呈现 · 品牌信息持续更新</p>
        <p style="color:#aaa;font-size:12px;margin-top:8px">免责声明：本站仅作为品牌信息收录与展示平台，不参与任何品牌运营。品牌信息如有不准确之处，请联系我们更正。</p>
    </div>
</div>

<script>
var brands = {json.dumps(js_brands, ensure_ascii=False)};

function searchBrand(){{
    var q = document.getElementById('search-input').value.toLowerCase().trim();
    var cards = document.querySelectorAll('.brand-card');
    var sections = document.querySelectorAll('.section-title');
    var count = 0;
    cards.forEach(function(card) {{
        var text = card.textContent.toLowerCase();
        if(!q || text.includes(q)){{card.style.display = ''; count++;}}
        else{{card.style.display = 'none';}}
    }});
    sections.forEach(function(s) {{ s.style.display = q ? 'none' : ''; }});
    document.querySelector('.brand-count').textContent = q ? '搜索到 ' + count + ' 个品牌' : '共 {brand_count} 个已收录品牌';
}}
</script>
</body>
</html>"""

(ROOT / "index.html").write_text(html_content, encoding="utf-8")
print(f"✅ 首页已生成，共 {brand_count} 个品牌，按行业分组展示")
