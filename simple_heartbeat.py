#!/usr/bin/env python3
"""
simple_heartbeat.py — Clean, simple brand pipeline for pinpai.cc.cd
每15分钟运行一次，每次处理5个品牌。
流程：取品牌 → Wikipedia查内容 → 生成页面 → 更新索引 → 刷新首页
"""
import json, os, sys, re, time, urllib.request, urllib.parse, shutil

BASE = "/workspace/pinpai-ai-in"
WWW = "/var/www/pinpai"
POOL_FILE = os.path.join(BASE, ".next_batch.json")
LOCK_FILE = os.path.join(BASE, ".heartbeat.lock")
LOG_FILE = "/workspace/pinpai-ai-in/heartbeat.log"

def log(msg):
    t = time.strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

# Lock: 30 min expiry
if os.path.exists(LOCK_FILE):
    mtime = os.path.getmtime(LOCK_FILE)
    if time.time() - mtime < 1800:
        log("LOCKED - another heartbeat running")
        sys.exit(0)
    os.remove(LOCK_FILE)
open(LOCK_FILE, "w").close()

try:
    # 1. Load current state
    www_idx_path = os.path.join(WWW, "brands_index.json")
    with open(www_idx_path) as f:
        index = json.load(f)
    existing_slugs = set(b["slug"] for b in index)
    log(f"Current: {len(index)} brands in index")

    # 2. Load pool
    if not os.path.exists(POOL_FILE):
        log("Pool empty! Sourcing more brands...")
        result = os.system(f"cd {BASE} && python3 auto_source_brands.py 2>&1")
        if not os.path.exists(POOL_FILE):
            log("Still no pool after sourcing. Nothing to do.")
            sys.exit(0)

    with open(POOL_FILE) as f:
        pool = json.load(f)
    log(f"Pool: {len(pool)} brands waiting")

    # 3. Filter out already-deployed
    to_process = [b for b in pool if b["slug"] not in existing_slugs]
    if not to_process:
        log("All pool brands already deployed! Clearing pool.")
        os.remove(POOL_FILE)
        sys.exit(0)

    # 4. Take next batch (5 per run)
    BATCH = 5
    batch = to_process[:BATCH]
    remaining = to_process[BATCH:]
    
    # Save remaining pool
    # Merge remaining with any pool entries not in to_process
    remaining_pool = remaining + [b for b in pool if b["slug"] in existing_slugs]
    json.dump(remaining_pool, open(POOL_FILE, "w"), ensure_ascii=False, indent=2)

    # 5. Process each brand
    added = 0
    for b in batch:
        slug = b["slug"]
        name = b["name"]
        name_en = b.get("name_en", name)
        category = b.get("category", "general")
        
        # Query Wikipedia
        url = ("https://en.wikipedia.org/w/api.php"
               "?action=query&prop=extracts&exintro&explaintext&exchars=500"
               "&titles=" + urllib.parse.quote(name) +
               "&format=json&redirects=1")
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PinpaiBot/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            log(f"  SKIP {slug}: API error - {e}")
            time.sleep(1)
            continue
        
        pages = data.get("query", {}).get("pages", {})
        extract = ""
        matched_title = ""
        for pid, pdata in pages.items():
            if pid == "-1":
                continue
            title = pdata.get("title", "")
            ext = pdata.get("extract", "")
            if ext and len(ext) >= 500:
                extract = ext
                matched_title = title
                break
        
        if not extract:
            log(f"  SKIP {slug}: no Wikipedia content (>{200} chars)")
            time.sleep(0.5)
            continue
        
        # Generate the brand page
        www_dir = os.path.join(WWW, slug)
        os.makedirs(www_dir, exist_ok=True)
        
        # Format content
        paragraphs = extract.strip().split("\n")
        content_html = ""
        for p in paragraphs:
            p = p.strip()
            if p:
                content_html += f"<p>{p}</p>\n"
        
        # Read template from existing brand (avio is a good reference)
        # Or just build it directly with proper structure
        html = generate_brand_page(slug, name, name_en, category, extract, b)
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {name_en} | 全球品牌索引</title>
<meta name="description" content="{name}（{name_en}）知名品牌介绍。">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f8f9fa;color:#222;line-height:1.7}}
.container{{max-width:960px;margin:0 auto;padding:20px}}
.brand-header{{margin-bottom:30px;padding-bottom:20px;border-bottom:2px solid #222}}
.brand-header h1{{font-size:32px;margin-bottom:4px}}
.brand-header .brand-sub{{font-size:16px;color:#777}}
.brand-content{{background:#fff;border:1px solid #eee;border-radius:8px;padding:24px;margin-bottom:30px;font-size:15px;line-height:1.8}}
.brand-content p{{margin-bottom:12px}}
.info-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-bottom:30px}}
.info-card{{background:#fff;border:1px solid #eee;border-radius:8px;padding:14px 18px}}
.info-card .label{{font-size:12px;color:#999;text-transform:uppercase;margin-bottom:4px}}
.info-card .value{{font-size:15px;color:#222;font-weight:500}}
.similar-section{{margin-bottom:30px}}
.similar-section h3{{font-size:16px;margin-bottom:12px;color:#555}}
.similar-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}}
.similar-card{{display:block;background:#fff;border:1px solid #eee;border-radius:8px;padding:12px 16px;text-decoration:none;transition:all 0.2s}}
.similar-card:hover{{border-color:#222;transform:translateY(-2px)}}
.similar-card .zh{{font-size:14px;color:#222}}
.similar-card .en{{font-size:12px;color:#999}}
.similar-card.premium{{background:#222;border-color:#222}}
.similar-card.premium .zh{{color:#fff;font-weight:600}}
.similar-card.premium .en{{color:#aaa}}
.badge-premium{{background:#e53935;color:#fff;font-size:10px;padding:1px 6px;border-radius:3px;margin-left:4px;vertical-align:middle}}
.footer{{margin-top:50px;padding-top:20px;border-top:1px solid #eee;font-size:13px;color:#999;text-align:center}}
.footer a{{color:#666}}
</style>
</head>
<body>
<div class="container">
<div class="brand-header">
<h1>{name} <span style="font-weight:400;color:#999">—</span> {name_en}</h1>
<div class="brand-sub">品牌 · {category}</div>
</div>

<div class="info-grid">
<div class="info-card"><div class="label">📅 创立</div><div class="value">{b.get("founding_year", "信息待补充")}</div></div>
<div class="info-card"><div class="label">🌍 国家</div><div class="value">{b.get("country", "信息待补充")}</div></div>
<div class="info-card"><div class="label">🏭 行业</div><div class="value">{category}</div></div>
</div>

<div class="brand-content" id="brand-content">
{content_html}
</div>

<div class="similar-section">
<h3>类似品牌</h3>
<div class="similar-grid">
<a href="/escher/" class="similar-card premium"><span class="zh">埃舍尔Escher <span class="badge-premium">品牌推广</span></span><span class="en">埃舍尔Escher</span></a>
<div id="dynamic-similars" style="display:contents"></div>
</div>
</div>

<div class="footer">
<p><a href="https://pinpai.cc.cd">全球品牌索引 · pinpai.cc.cd</a></p>
</div>
</div>

<script>
var CURRENT_SLUG = "{slug}";
var CATEGORY = "{category}";
</script>
<script src="/js/similar-brands.js"></script>
</body>
</html>'''
        
        
def generate_brand_page(slug, name, name_en, category, extract, b):
    """Generate brand page with multi-language content switching"""
    LANGUAGES = [
        ("zh-CN", "zh", "中文"),
        ("en", "en", "English"),
        ("fr", "fr", "Fran\xe7ais"),
        ("es", "es", "Espa\xf1ol"),
        ("de", "de", "Deutsch"),
        ("ja", "ja", "\u65e5\u672c\u8a9e"),
        ("ko", "ko", "\ud55c\uad6d\uc5b4"),
        ("pt", "pt", "Portugu\xeas"),
        ("ru", "ru", "\u0420\u0443\u0441\u0441\u043a\u0438\u0439"),
        ("ar", "ar", "\u0627\u0644\u0639\u0631\u0628\u064a\u0629"),
    ]
    
    # Format content for display
    paragraphs = extract.strip().split("\n")
    content_body = ""
    for p in paragraphs:
        p = p.strip()
        if p:
            content_body += f"<p>{p}</p>\n"
    
    # Build language nav and content sections
    lang_nav = ""
    content_sections = ""
    for i, (lang_code, wiki_code, lang_name) in enumerate(LANGUAGES):
        active = ' active' if lang_code == "zh-CN" else ""
        display = "block" if lang_code == "zh-CN" else "none"
        lang_nav += f'<a href="#" lang="{lang_code}" class="lang-tab{active}">{lang_name}</a>\n            '
        content_sections += f'<div class="brand-content lang-{lang_code}" id="content-{lang_code}" style="display:{display}">\n{content_body}\n</div>\n'
    
    first_sentence = extract.split(".")[0] if extract else name
    
    html = f"""<!DOCTYPE html>
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
<h1>{name} <span style="font-weight:400;font-size:22px;color:#777">\u2014</span> {name_en}</h1>
<div class="brand-sub">{category}</div>
</div>

{content_sections}

<div class="similar-section">
<div class="similar-grid">
<a href="/escher/" class="similar-card premium">\u2b50 \u57c3\u820d\u5c14Escher <span class="badge-premium">\u63a8\u5e7f</span></a>
</div>
</div>

<div class="footer">
<p><a href="https://pinpai.cc.cd">\u5168\u7403\u54c1\u724c\u7d22\u5f15</a> | <a href="/">\u2190 \u8fd4\u56de\u9996\u9875</a></p>
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
</html>"""
    return html


www_path = os.path.join(www_dir, "index.html")
        with open(www_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        # Add to index
        index.append({
            "slug": slug,
            "name": name,
            "name_en": name_en,
            "category": category,
            "updated_at": int(time.time())
        })
        added += 1
        log(f"  ADDED {slug}: {name} ({len(extract)} chars)")
        time.sleep(1)  # Rate limit

    # 6. Update brands_index.json in WWW
    json.dump(index, open(www_idx_path, "w"), ensure_ascii=False, indent=2)
    
    # 7. Regenerate homepage
    log(f"Regenerating homepage ({len(index)} brands)...")
    
    # Read current homepage
    hp_path = os.path.join(WWW, "index.html")
    with open(hp_path, encoding="utf-8") as f:
        homepage = f.read()
    
    # Update inline brandsData
    new_data = json.dumps(index, ensure_ascii=False)
    homepage = re.sub(r'var brandsData = \[.*?\];', f'var brandsData = {new_data};', homepage, count=1, flags=re.DOTALL)
    
    # Regenerate server-side brand cards (20 latest)
    cards = ""
    for b in index[-20:]:
        cards += f'\n        <a class="brand-card" href="/{b["slug"]}/"><h2>{b["name"]}</h2><div class="en">{b.get("name_en", b["name"])}</div><span class="cat-tag">{b.get("category","")}</span></a>'
    
    brand_list_pattern = r'<div class="brand-grid" id="brand-list">.*?</div>'
    homepage = re.sub(brand_list_pattern, f'<div class="brand-grid" id="brand-list">{cards}\n    </div>', homepage, count=1, flags=re.DOTALL)
    
    homepage = re.sub(r'共 \d+ 个品牌', f'共 {len(index)} 个品牌', homepage)
    
    with open(hp_path, "w", encoding="utf-8") as f:
        f.write(homepage)
    
    log(f"Heartbeat complete: +{added} brands (total: {len(index)})")

finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
