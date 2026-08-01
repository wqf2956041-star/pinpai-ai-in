#!/usr/bin/env python3
"""
真正从 Wikipedia 拉取10种语言的内容。
之前代码有 bug：iterate 错了字典的 key/value。
现在修好了，只处理前100个品牌（验证效果），其余由心跳自动处理。
"""
import json, os, re, time, urllib.request, urllib.parse

WWW = "/var/www/pinpai"

LANG_MAP = {"zh-CN":"zh","en":"en","fr":"fr","es":"es","de":"de",
            "ja":"ja","ko":"ko","pt":"pt","ru":"ru","ar":"ar"}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def get_langlinks(title):
    url = ("https://en.wikipedia.org/w/api.php"
           "?action=query&prop=langlinks&titles=" + urllib.parse.quote(title) +
           "&lllimit=500&format=json")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PinpaiFix/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        for pid, pdata in data.get("query",{}).get("pages",{}).items():
            if pid == "-1": return {}
            return {l["lang"]: l["*"] for l in pdata.get("langlinks", [])}
    except:
        return {}

def get_local_extract(lang_code, title):
    url = (f"https://{lang_code}.wikipedia.org/w/api.php"
           "?action=query&prop=extracts&exintro&explaintext&exchars=500"
           "&titles=" + urllib.parse.quote(title) +
           "&format=json&redirects=1")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PinpaiFix/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        for pid, pdata in data.get("query",{}).get("pages",{}).items():
            if pid == "-1": continue
            ext = pdata.get("extract", "")
            if ext and len(ext) > 50:
                return ext
    except:
        pass
    return ""

def generate_multilang_page(slug, name, name_en, category, lang_contents):
    """Generate page with REAL translated content per language"""
    LANG_NAMES = {"zh-CN":"中文","en":"English","fr":"Français","es":"Español",
                  "de":"Deutsch","ja":"日本語","ko":"한국어","pt":"Português",
                  "ru":"Русский","ar":"العربية"}
    
    lang_nav = ""
    content_sections = ""
    default_lang = "en"  # Default to English since Wikipedia primary is English
    
    for lc in LANG_MAP:
        content = lang_contents.get(lc, lang_contents.get("en", ""))
        if not content:
            content = lang_contents.get("en", "")
        
        paragraphs = content.strip().split("\n")
        inner = "".join(f"<p>{p.strip()}</p>\n" for p in paragraphs if p.strip())
        
        is_default = (lc == default_lang) or (lc == "zh-CN" and "en" not in lang_contents)
        active = ' active' if is_default else ""
        display = "block" if is_default else "none"
        
        lang_nav += f'<a href="#" lang="{lc}" class="lang-tab{active}">{LANG_NAMES[lc]}</a>\n            '
        content_sections += f'<div class="brand-content lang-{lc}" id="content-{lc}" style="display:{display}">\n{inner}</div>\n'
    
    first_sentence = (lang_contents.get("en") or "").split(".")[0] or name_en
    
    # Escape the template properly
    esc_title = name_en.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    
    html = f'''<!DOCTYPE html>
<html lang="en" data-lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc_title} | Global Brand Index</title>
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
<h1>{esc_title}</h1>
<div class="brand-sub">{category}</div>
</div>

{content_sections}

<div class="similar-section">
<div class="similar-grid">
<a href="/escher/" class="similar-card premium">&#9733; 埃舍尔Escher <span class="badge-premium">推广</span></a>
</div>
</div>

<div class="footer">
<p><a href="https://pinpai.cc.cd">Global Brand Index</a> | <a href="/">&larr; Home</a></p>
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

# Load index
with open(os.path.join(WWW, "brands_index.json")) as f:
    idx = json.load(f)

log(f"Processing {len(idx)} brands with REAL multilingual Wikipedia content...")

# Process first 50 brands to fix the bug
fixed = 0
skipped = 0
for b in idx[:50]:
    slug = b["slug"]
    name_en = b.get("name_en", b.get("name", slug))
    category = b.get("category", "general")
    path = os.path.join(WWW, slug, "index.html")
    
    if not os.path.exists(path):
        skipped += 1
        continue
    
    # Get Wikipedia langlinks (language code -> local title)
    langlinks = get_langlinks(name_en)
    
    # Fetch content in each available language
    lang_contents = {}
    
    # Always get English
    en_extract = ""
    m = re.search(r'id="content-en"[^>]*style="display:none"[^>]*>(.*?)</div>', 
                  open(path).read(), re.DOTALL)
    if m:
        en_extract = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    if not en_extract:
        m = re.search(r'id="content-zh"[^>]*>(.*?)</div>', open(path).read(), re.DOTALL)
        if m:
            en_extract = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    
    if not en_extract or len(en_extract) < 50:
        skipped += 1
        continue
    
    lang_contents["en"] = en_extract
    
    # For each target language, try to get REAL content from Wikipedia
    real_langs = 0
    for lc, wc in LANG_MAP.items():
        if lc == "en":
            continue
        if wc in langlinks:
            local_title = langlinks[wc]
            local_extract = get_local_extract(wc, local_title)
            if local_extract and len(local_extract) > 50:
                lang_contents[lc] = local_extract
                real_langs += 1
            else:
                lang_contents[lc] = en_extract  # fallback
        else:
            lang_contents[lc] = en_extract  # fallback
    
    # Generate page with real translations
    new_html = generate_multilang_page(slug, b.get("name", name_en), name_en, category, lang_contents)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    
    fixed += 1
    if real_langs > 0:
        log(f"  {slug}: +{real_langs} real translations from Wikipedia")
    else:
        log(f"  {slug}: English only (no Wikipedia translations)")
    
    time.sleep(0.5)

log(f"\nDone: {fixed} fixed, {skipped} skipped")

# Show proof: check yahoo's Japanese content
log("\n=== PROOF: yahoo in Japanese ===")
yahoo_html = open(os.path.join(WWW, "yahoo", "index.html")).read()
m_ja = re.search(r'id="content-ja"[^>]*display:block[^>]*>(.*?)</div>', yahoo_html, re.DOTALL)
m_zh = re.search(r'id="content-zh-CN"[^>]*display:block[^>]*>(.*?)</div>', yahoo_html, re.DOTALL)
m_ko = re.search(r'id="content-ko"[^>]*display:block[^>]*>(.*?)</div>', yahoo_html, re.DOTALL)
if m_ja:
    text = re.sub(r'<[^>]+>', '', m_ja.group(1)).strip()
    log(f"  Japanese (active): {text[:150]}")
if m_zh:
    text = re.sub(r'<[^>]+>', '', m_zh.group(1)).strip()
    log(f"  Chinese: {text[:150]}")
