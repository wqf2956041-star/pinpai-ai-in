#!/usr/bin/env python3
"""
Convert ALL existing brand pages to multi-language structure.
Uses existing English content and wraps it in 10-language template.
No new Wikipedia API calls needed.
"""
import json, os, re

WWW = "/var/www/pinpai"
BASE = "/workspace/pinpai-ai-in"

LANG_NAMES = {
    "zh-CN": "中文", "en": "English", "fr": "Français",
    "es": "Español", "de": "Deutsch", "ja": "日本語",
    "ko": "한국어", "pt": "Português", "ru": "Русский", "ar": "العربية"
}

def log(msg):
    print(f"[{msg}]")

def is_already_multilang(html):
    """Check if page already has the new multi-language structure"""
    return 'id="content-zh-CN"' in html or 'id="content-zh"' in html

def convert_to_multilang(slug, name, name_en, category, en_extract):
    """Convert brand page to multi-language template"""
    paragraphs = en_extract.strip().split("\n")
    content_body = ""
    for p in paragraphs:
        p = p.strip()
        if p:
            content_body += f"<p>{p}</p>\n"
    
    # Build language nav and content sections
    lang_nav = ""
    content_sections = ""
    for i, (lang_code) in enumerate(LANG_NAMES):
        lang_name = LANG_NAMES[lang_code]
        active = ' active' if lang_code == "zh-CN" else ""
        display = "block" if lang_code == "zh-CN" else "none"
        lang_nav += f'<a href="#" lang="{lang_code}" class="lang-tab{active}">{lang_name}</a>\n            '
        content_sections += f'<div class="brand-content lang-{lang_code}" id="content-{lang_code}" style="display:{display}">\n{content_body}\n</div>\n'
    
    first_sentence = en_extract.split(".")[0] if en_extract else name_en
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} | 全球品牌索引</title>
<meta name="description" content="{first_sentence}">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f8f9fa;color:#222;line-height:1.7}}
.container{{max-width:960px;margin:0 auto;padding:20px}}
.lang-nav{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:20px}}
.lang-nav .lang-tab{{display:inline-block;padding:4px 10px;border-radius:4px;font-size:12px;text-decoration:none;color:#555;border:1px solid #ddd;cursor:pointer;transition:all 0.2s}}
.lang-nav .lang-tab:hover{{background:#eee}}
.lang-nav .lang-tab.active{{background:#222;color:#fff;border-color:#222}}
.brand-header{{margin-bottom:20px;padding-bottom:15px;border-bottom:2px solid #222}}
.brand-header h1{{font-size:26px;margin-bottom:2px}}
.brand-header .brand-sub{{font-size:13px;color:#777}}
.brand-content{{background:#fff;border:1px solid #eee;border-radius:8px;padding:24px;margin-bottom:30px;font-size:15px;line-height:1.8}}
.brand-content p{{margin-bottom:12px}}
.similar-section{{margin-bottom:30px}}
.similar-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px}}
.similar-card{{display:block;background:#fff;border:1px solid #eee;border-radius:6px;padding:10px 14px;text-decoration:none;font-size:13px}}
.similar-card.premium{{background:#222;color:#fff}}
.badge-premium{{background:#e53935;color:#fff;font-size:10px;padding:1px 5px;border-radius:3px}}
.footer{{margin-top:40px;padding-top:15px;border-top:1px solid #eee;font-size:12px;color:#999;text-align:center}}
.footer a{{color:#666}}
</style>
</head>
<body>
<div class="container">
<div class="lang-nav">
    {lang_nav}</div>

<div class="brand-header">
<h1>{name} <span style="font-weight:400;font-size:22px;color:#777">—</span> {name_en}</h1>
<div class="brand-sub">{category}</div>
</div>

{content_sections}

<div class="similar-section">
<div class="similar-grid">
<a href="/escher/" class="similar-card premium">⭐ 埃舍尔Escher <span class="badge-premium">推广</span></a>
</div>
</div>

<div class="footer">
<p><a href="https://pinpai.cc.cd">全球品牌索引</a> | <a href="/">← 返回首页</a></p>
</div>
</div>

<script>
document.querySelectorAll('.lang-nav .lang-tab').forEach(function(link) {{
    link.addEventListener('click', function(e) {{
        e.preventDefault();
        var lang = this.getAttribute('lang');
        document.querySelectorAll('.lang-nav .lang-tab').forEach(function(l) {{ l.classList.remove('active'); }});
        this.classList.add('active');
        document.querySelectorAll('[id^="content-"]').forEach(function(d) {{ d.style.display = 'none'; }});
        var el = document.getElementById('content-' + lang);
        if (el) el.style.display = 'block';
    }});
}});
</script>
</body>
</html>'''
    return html

# Load brand index
with open(os.path.join(WWW, "brands_index.json")) as f:
    idx = json.load(f)

log(f"Converting {len(idx)} brand pages to multi-language...")

converted = 0
already = 0
skipped = 0
for b in idx:
    slug = b["slug"]
    name = b.get("name", slug)
    name_en = b.get("name_en", name)
    category = b.get("category", "general")
    path = os.path.join(WWW, slug, "index.html")
    
    if not os.path.exists(path):
        skipped += 1
        continue
    
    html = open(path, encoding="utf-8", errors="replace").read()
    
    if is_already_multilang(html):
        already += 1
        continue
    
    # Extract content from old structure
    m = re.search(r'id="brand-content">(.*?)</div>', html, re.DOTALL)
    if not m:
        skipped += 1
        continue
    
    en_extract = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    if len(en_extract) < 100:
        skipped += 1
        continue
    
    # Convert to multi-language
    new_html = convert_to_multilang(slug, name, name_en, category, en_extract)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    converted += 1
    
    if converted % 20 == 0:
        log(f"  Progress: {converted} converted")

log(f"Done: {converted} converted, {already} already multi-lang, {skipped} skipped")
