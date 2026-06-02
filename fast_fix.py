import time
ln=print
#!/usr/bin/env python3
"""
Fast fix: Restructure ALL existing brand pages to multi-language format.
No Wikipedia API calls - just use existing English content as fallback.
Language switcher works (shows English for all, but buttons are functional).
Heartbeat will add real translations gradually.
"""
import json, os, re

WWW = "/var/www/pinpai"

LANG_NAMES = {
    "zh-CN": "Chinese", "en": "English", "fr": "Francais",
    "es": "Espanol", "de": "Deutsch", "ja": "Japanese",
    "ko": "Korean", "pt": "Portugues", "ru": "Russian", "ar": "Arabic"
}
ALL_LANGS = list(LANG_NAMES.keys())

def make_page(name_en, cat, en_ext):
    safe_name = name_en.replace("&","&amp;").replace("<","&lt;").replace("\"","&quot;")
    first_s = en_ext.split(".")[0].replace("\"","'").replace("\n"," ")[:200]
    
    html = "<!DOCTYPE html>\n<html lang=\"en\" data-lang=\"en\">\n<head>\n"
    html += "<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
    html += "<title>%s | Global Brand Index</title>\n" % safe_name
    html += "<meta name=\"description\" content=\"%s\">\n" % first_s
    html += ("<style>*{margin:0;padding:0;box-sizing:border-box}"
             "body{font-family:sans-serif;background:#f8f9fa;color:#222;line-height:1.7}"
             ".container{max-width:960px;margin:0 auto;padding:20px}"
             ".lang-nav{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:20px}"
             ".lang-nav .lang-tab{display:inline-block;padding:4px 10px;border-radius:4px;font-size:12px;text-decoration:none;color:#555;border:1px solid #ddd;cursor:pointer}"
             ".lang-nav .lang-tab:hover{background:#eee}"
             ".lang-nav .lang-tab.active{background:#222;color:#fff;border-color:#222}"
             ".brand-header{margin-bottom:20px;padding-bottom:15px;border-bottom:2px solid #222}"
             ".brand-header h1{font-size:26px;margin-bottom:2px}"
             ".brand-header .brand-sub{font-size:13px;color:#777}"
             ".brand-content{background:#fff;border:1px solid #eee;border-radius:8px;padding:24px;margin-bottom:30px;font-size:15px;line-height:1.8}"
             ".brand-content p{margin-bottom:12px}"
             ".similar-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-bottom:30px}"
             ".similar-card{display:block;background:#fff;border:1px solid #eee;border-radius:6px;padding:10px 14px;text-decoration:none;font-size:13px}"
             ".similar-card.premium{background:#222;color:#fff}"
             ".footer{margin-top:40px;padding-top:15px;border-top:1px solid #eee;font-size:12px;color:#999;text-align:center}"
             ".footer a{color:#666}</style>\n</head>\n<body>\n<div class=\"container\">\n")
    html += "<div class=\"lang-nav\">\n"
    for lc in ALL_LANGS:
        act = " active" if lc == "en" else ""
        html += "    <a href=\"#\" lang=\"%s\" class=\"lang-tab%s\">%s</a>\n" % (lc, act, LANG_NAMES[lc])
    html += "</div>\n"
    html += "<div class=\"brand-header\">\n<h1>%s</h1>\n<div class=\"brand-sub\">%s</div>\n</div>\n" % (safe_name, cat)
    pars = "".join("<p>%s</p>\n" % p.strip() for p in en_ext.strip().split("\n") if p.strip())
    for lc in ALL_LANGS:
        disp = "block" if lc == "en" else "none"
        html += "<div class=\"brand-content\" lang=\"%s\" id=\"content-%s\" style=\"display:%s\">\n%s</div>\n" % (lc, lc, disp, pars)
    html += "<div class=\"similar-grid\">\n<a href=\"/escher/\" class=\"similar-card premium\">* Escher <span class=\"badge-premium\">推广</span></a>\n</div>\n"
    html += "<div class=\"footer\">\n<p><a href=\"https://pinpai.cc.cd\">Global Brand Index</a> | <a href=\"/\">Home</a></p>\n</div>\n</div>\n"
    html += "<script>"
    html += "document.querySelectorAll('.lang-nav .lang-tab').forEach(function(l){l.addEventListener('click',function(e){e.preventDefault();var lang=this.getAttribute('lang');document.querySelectorAll('.lang-nav .lang-tab').forEach(function(x){x.classList.remove('active')});this.classList.add('active');document.querySelectorAll('[id^=\"content-\"]').forEach(function(d){d.style.display='none'});var el=document.getElementById('content-'+lang);if(el)el.style.display='block'})})"
    html += "</script>\n</body>\n</html>"
    return html

# Load index
with open(os.path.join(WWW, "brands_index.json")) as f:
    idx = json.load(f)

ln("Fixing %d brands..." % len(idx))
fixed = 0
for b in idx:
    slug = b["slug"]
    name_en = b.get("name_en", b.get("name", slug))
    cat = b.get("category", "general")
    path = os.path.join(WWW, slug, "index.html")
    
    if not os.path.exists(path):
        continue
    
    html = open(path, encoding="utf-8", errors="replace").read()
    
    # Skip if already has multi-lang structure
    if 'id="content-ja"' in html:
        continue
    
    # Extract content
    m = re.search(r'id="content-en"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not m:
        m = re.search(r'id="brand-content"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not m:
        continue
    
    en_ext = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    if len(en_ext) < 100:
        continue
    
    new_html = make_page(name_en, cat, en_ext)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    fixed += 1

# Also fix caproni which was done by the previous script (may have different format)
ln("Fixed %d brands" % fixed)

# Check verification brands
ln("\n=== VERIFY ===")
for check in ["yahoo", "walmart", "visa-inc", "xerox", "caproni"]:
    p = os.path.join(WWW, check, "index.html")
    if os.path.exists(p):
        h = open(p).read()
        langs = re.findall(r'id="content-([^"]+)"', h)
        # Check Japanese has content
        has_ja = 'id="content-ja"' in h
        has_ko = 'id="content-ko"' in h
        has_ar = 'id="content-ar"' in h
        ln("  %s: %d langs, ja=%s, ko=%s, ar=%s" % (check, len(set(langs)), has_ja, has_ko, has_ar))
        if check == "yahoo" and has_ja:
            m_ja = re.search(r'id="content-ja"[^>]*display:block[^>]*>(.*?)</div>', h, re.DOTALL)
            if not m_ja:
                m_ja = re.search(r'id="content-ja"[^>]*>(.*?)</div>', h, re.DOTALL)
            if m_ja:
                txt = re.sub(r'<[^>]+>', '', m_ja.group(1)).strip()
                ln("    Japanese sample: %s" % txt[:100])
